import pika
import json
import logging
from datetime import datetime, timezone
import time
from src.config import Config

logger = logging.getLogger(__name__)


class RabbitMQClient:
    def __init__(self):
        self._connect()

    def _connect(self):
        retries = 0
        max_retries = 5
        while retries < max_retries:
            try:
                self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=Config.RABBITMQ_HOST, connection_attempts=3, retry_delay=5))
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue="retry_queue", durable=True)
                logger.info("Successfully connected to RabbitMQ")
                return
            except pika.exceptions.AMQPConnectionError:
                retries += 1
                logger.warning(f"Failed to connect to RabbitMQ. Retry {retries}/{max_retries}")
                time.sleep(5)

        raise Exception("Failed to connect to RabbitMQ after multiple attempts")

    def publish_retry_operation(self, operation_type, payload, username):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if self.connection is None or self.connection.is_closed:
                    self._connect()

                message = {"operation_type": operation_type, "payload": payload, "username": username, "timestamp": datetime.now(tz=timezone.utc).isoformat()}

                self.channel.basic_publish(exchange="", routing_key="retry_queue", body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=2))
                logger.info(f"Published retry operation: {operation_type}")
                return True

            except (pika.exceptions.AMQPConnectionError, ConnectionResetError) as e:
                logger.warning(f"Connection error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                try:
                    self.close()
                except:
                    pass
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)  # Exponential backoff
                    continue
                logger.error(f"Failed to publish retry operation after {max_retries} attempts")
                return False
            except Exception as e:
                logger.error(f"Unexpected error publishing message: {str(e)}")
                return False

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
