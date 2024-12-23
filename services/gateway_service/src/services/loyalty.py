from http import HTTPStatus
from requests.exceptions import ConnectionError, RequestException
from src.services.base import BaseServiceClient
from src.schemas.loyalty import LoyaltySchema
from src.config import Config


class LoyaltyService(BaseServiceClient):
    def __init__(self):
        super().__init__()
        self.base_url = Config.LOYALTY_SERVICE_URL
        self.schema = LoyaltySchema()

    def get_loyalty(self, username):
        try:
            response = self.circuit_breaker_request("loyalty", "GET", f"{self.base_url}/loyalty", headers={"X-User-Name": username}, schema=self.schema)
            if not response:
                raise ConnectionError("Loyalty Service unavailable")
            return response, HTTPStatus.OK
        except (ConnectionError, RequestException):
            # For direct loyalty requests, raise service unavailable
            if self.is_direct_loyalty_request():
                return {"message": "Loyalty Service unavailable"}, HTTPStatus.SERVICE_UNAVAILABLE
            # For indirect requests (like /me endpoint), return empty dict
            return {}, HTTPStatus.OK

    def update_loyalty(self, username):
        try:
            response = self.circuit_breaker_request("loyalty", "POST", f"{self.base_url}/loyalty", headers={"X-User-Name": username})
            if response is None:
                raise ConnectionError("Loyalty Service unavailable")
            return response
        except (ConnectionError, RequestException):
            return None

    @staticmethod
    def is_direct_loyalty_request():
        """Check if the current request is directly to the loyalty endpoint"""
        from flask import request

        return request.endpoint == "get_loyalty"
