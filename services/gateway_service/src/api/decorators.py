from functools import wraps
from http import HTTPStatus
from flask import request, jsonify
from marshmallow import ValidationError
import requests
from src.api.exceptions import SchemaValidationError
from src.schemas.error import ErrorSchema, ValidationErrorSchema


def validate_request_schema(schema_cls):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            schema = schema_cls()
            try:
                if request.is_json:
                    data = schema.load(request.json)
                    request.validated_data = data
                return f(*args, **kwargs)
            except ValidationError as err:
                raise SchemaValidationError("Validation error", err.messages)

        return wrapper

    return decorator


def handle_service_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SchemaValidationError as e:
            error_schema = ValidationErrorSchema()
            return jsonify(error_schema.dump({"message": str(e), "errors": e.errors})), HTTPStatus.BAD_REQUEST
        except requests.exceptions.ConnectionError:
            error_schema = ErrorSchema()
            return jsonify(error_schema.dump({"message": "Service temporarily unavailable"})), HTTPStatus.SERVICE_UNAVAILABLE
        except requests.exceptions.RequestException as e:
            error_schema = ErrorSchema()
            return jsonify(error_schema.dump({"message": "Internal service error"})), HTTPStatus.INTERNAL_SERVER_ERROR

    return wrapper
