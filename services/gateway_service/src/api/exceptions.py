from http import HTTPStatus


class SchemaValidationError(Exception):
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors


class ServiceUnavailableError(Exception):
    """Exception raised when a service is unavailable"""

    def __init__(self, message):
        super().__init__(message)
        self.status_code = HTTPStatus.SERVICE_UNAVAILABLE  # 503
        self.error = "Service Unavailable"
