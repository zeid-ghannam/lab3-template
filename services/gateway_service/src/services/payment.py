from src.services.base import BaseServiceClient
from src.schemas.payment import PaymentSchema
from src.config import Config


class PaymentService(BaseServiceClient):
    def __init__(self):
        super().__init__()
        self.base_url = Config.PAYMENT_SERVICE_URL
        self.schema = PaymentSchema()

    def get_payment(self, username, reservation_uid):
        return self.circuit_breaker_request("payment", "GET", f"{self.base_url}/payment/{reservation_uid}", headers={"X-User-Name": username})

    def create_payment(self, username, payment_data):
        return self.circuit_breaker_request("payment", "POST", f"{self.base_url}/payment", headers={"X-User-Name": username}, json=payment_data)

    def delete_payment(self, username, payment_uid):
        return self.circuit_breaker_request("payment", "DELETE", f"{self.base_url}/payment/{payment_uid}", headers={"X-User-Name": username})
