import logging
from http import HTTPStatus

import requests
from marshmallow import ValidationError
import pybreaker
from src.api.exceptions import SchemaValidationError, ServiceUnavailableError
from src.circuit.breaker import CircuitBreakerFactory
from src.queue.rabbitmq import RabbitMQClient

logging.basicConfig(
    level=logging.INFO,  # Set the desired log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/var/log/flask_app.log"), logging.StreamHandler()],  # Log to a file  # Also log to stdout (for Docker logs)
)


logger = logging.getLogger(__name__)


def fallback_response(service_name):
    """Fallback responses for different services"""
    fallbacks = {"loyalty": {}, "payment": {}, "hotels": {"items": [], "page": 1, "pageSize": 10, "totalElements": 0}, "reservation": []}
    return fallbacks.get(service_name, {})


class BaseServiceClient:
    def __init__(self):
        self.rabbitmq_client = RabbitMQClient()

    @staticmethod
    def check_user_header(headers):
        if "X-User-Name" not in headers:
            raise SchemaValidationError("X-User-Name header is required")
        return headers.get("X-User-Name")

    def circuit_breaker_request(self, service_name, method, url, schema=None, **kwargs):

        breaker = CircuitBreakerFactory.get_breaker(service_name)

        @breaker
        def make_request():
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()

                if schema and response.content:
                    try:
                        return schema.load(response.json())
                    except ValidationError as e:

                        raise SchemaValidationError("Invalid response format", e.messages)

                return response.json() if response.content else None

            except requests.exceptions.HTTPError as e:

                if response.status_code == HTTPStatus.NOT_FOUND:
                    raise SchemaValidationError("Resource not found")
                if response.status_code == HTTPStatus.SERVICE_UNAVAILABLE:
                    raise ServiceUnavailableError(f"{service_name} is unavailable")
                raise e

        try:

            return make_request()
        except pybreaker.CircuitBreakerError:
            return fallback_response(service_name)
        except ServiceUnavailableError:
            raise
        except Exception as e:
            logger.error(f"Error making request to {service_name}: {str(e)}")
            return fallback_response(service_name)

    def queue_for_retry(self, operation_type, payload, username):
        try:
            logger.info(f"queue for retry {operation_type}, {payload}")

            self.rabbitmq_client.publish_retry_operation(operation_type, payload, username)
            return True
        except Exception as e:
            logger.error(f"Failed to queue retry operation: {str(e)}")
            return False
