import pika
import json
import logging
import time
from src.services.base import BaseServiceClient
from src.services.reservation import ReservationService
from src.config import Config

logger = logging.getLogger(__name__)


class RetryWorker:
    def __init__(self):
        self.reservation_service = ReservationService()
        self.base_service = BaseServiceClient()
        self._connect()

    def _connect(self):
        retries = 0
        max_retries = 5
        while retries < max_retries:
            try:
                parameters = pika.ConnectionParameters(
                    host=Config.RABBITMQ_HOST,
                    connection_attempts=3,
                    retry_delay=5,
                    heartbeat=60,  # Add heartbeat
                    blocked_connection_timeout=300,  # Add timeout
                    socket_timeout=10,  # Add socket timeout
                )
                self.connection = pika.BlockingConnection(parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue="retry_queue", durable=True)
                logger.info("Successfully connected to RabbitMQ")
                return
            except pika.exceptions.AMQPConnectionError:
                retries += 1
                logger.warning(f"Failed to connect to RabbitMQ. Retry {retries}/{max_retries}")
                time.sleep(5)

        raise Exception("Failed to connect to RabbitMQ after multiple attempts")

    def process_message(self, ch, method, properties, body):
        try:
            message = json.loads(body)
            operation_type = message["operation_type"]
            payload = message["payload"]
            username = message["username"]

            if operation_type == "create_reservation":
                result = self.reservation_service.create_reservation(username, payload["reservation"])
                if result and "status" not in result:
                    logger.info("Successfully processed retry for reservation")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logger.warning("Failed to process retry, will retry later")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            elif operation_type == "delete_reservation":
                result = self.reservation_service.delete_reservation(username, payload["reservation_uid"])
                if result:
                    logger.info("Successfully processed retry for reservation deletion")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    logger.warning("Failed to process retry, will retry later")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            elif operation_type == "decrease_loyalty":
                try:
                    result = self.base_service.circuit_breaker_request(
                        "loyalty", "POST", f"{Config.LOYALTY_SERVICE_URL}/loyalty/decrease", headers={"X-User-Name": username}
                    )
                    if result:
                        logger.info("Successfully processed retry for loyalty decrease")
                        ch.basic_ack(delivery_tag=method.delivery_tag)
                    else:
                        logger.warning("Failed to process retry, will retry later")
                        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
                except Exception as e:
                    logger.error(f"Error decreasing loyalty: {str(e)}")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

            else:
                logger.warning(f"Unknown operation type: {operation_type}")
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        while True:
            try:
                self.channel.basic_qos(prefetch_count=1)
                self.channel.basic_consume(queue="retry_queue", on_message_callback=self.process_message)
                logger.info("Started consuming messages from retry queue")
                self.channel.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                logger.error("Lost connection to RabbitMQ. Attempting to reconnect...")
                time.sleep(5)
                self._connect()
            except Exception as e:
                logger.error(f"Unexpected error in worker: {str(e)}")
                time.sleep(5)
