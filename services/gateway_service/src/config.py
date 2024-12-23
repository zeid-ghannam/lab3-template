import os


class Config:
    RESERVATION_SERVICE_URL = os.environ.get("RESERVATION_SERVICE_URL", "http://localhost:8070")
    PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:8060")
    LOYALTY_SERVICE_URL = os.environ.get("LOYALTY_SERVICE_URL", "http://localhost:8050")

    # Circuit breaker configuration
    CIRCUIT_BREAKER_FAIL_MAX = int(os.environ.get("CIRCUIT_BREAKER_FAIL_MAX", "5"))
    CIRCUIT_BREAKER_RESET_TIMEOUT = int(os.environ.get("CIRCUIT_BREAKER_RESET_TIMEOUT", "60"))

    # RabbitMQ configuration
    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
