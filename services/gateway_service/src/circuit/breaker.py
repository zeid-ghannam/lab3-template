import pybreaker
import logging
from src.config import Config

logging.basicConfig(
    level=logging.INFO,  # Set the desired log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("/var/log/flask_app.log"), logging.StreamHandler()],  # Log to a file  # Also log to stdout (for Docker logs)
)

logger = logging.getLogger(__name__)


class CircuitBreakerFactory:
    _breakers = {}

    @classmethod
    def get_breaker(cls, service_name):
        if service_name not in cls._breakers:
            cls._breakers[service_name] = pybreaker.CircuitBreaker(
                fail_max=Config.CIRCUIT_BREAKER_FAIL_MAX, reset_timeout=Config.CIRCUIT_BREAKER_RESET_TIMEOUT, exclude=[ConnectionError], name=service_name
            )
        return cls._breakers[service_name]
