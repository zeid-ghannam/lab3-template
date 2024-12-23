from datetime import datetime
from http import HTTPStatus
from requests.exceptions import ConnectionError, RequestException
from flask import jsonify
from src.services.base import BaseServiceClient
from src.schemas.reservation import ReservationResponseSchema
from src.services.payment import PaymentService
from src.services.loyalty import LoyaltyService
from src.config import Config


class ReservationService(BaseServiceClient):
    def __init__(self):
        super().__init__()
        self.base_url = Config.RESERVATION_SERVICE_URL
        self.schema = ReservationResponseSchema()
        self.payment_service = PaymentService()
        self.loyalty_service = LoyaltyService()

    def get_user_reservations(self, username):
        reservations = self.circuit_breaker_request(
            "reservation", "GET", f"{self.base_url}/reservations", headers={"X-User-Name": username}, schema=ReservationResponseSchema(many=True)
        )

        if reservations:
            return [self._enrich_reservation(username, reservation) for reservation in reservations]
        return []

    def get_reservation(self, username, reservation_uid):
        reservation = self.circuit_breaker_request(
            "reservation", "GET", f"{self.base_url}/reservations/{reservation_uid}", headers={"X-User-Name": username}, schema=self.schema
        )

        if reservation:
            return self._enrich_reservation(username, reservation)
        return None

    def create_reservation(self, username, request_data):
        try:
            loyalty = self.circuit_breaker_request("loyalty", "GET", f"{Config.LOYALTY_SERVICE_URL}/loyalty", headers={"X-User-Name": username})

            if not loyalty:
                return {"message": "Loyalty Service unavailable", "status_code": HTTPStatus.SERVICE_UNAVAILABLE}
            reservation = self.circuit_breaker_request(
                "reservation", "POST", f"{self.base_url}/reservations", headers={"X-User-Name": username}, json=request_data
            )

            if not reservation:
                raise Exception("Failed to create reservation")
            if reservation:
                # Calculate payment
                start_date = datetime.fromisoformat(reservation["startDate"])
                end_date = datetime.fromisoformat(reservation["endDate"])
                nights = (end_date - start_date).days
                total_price = reservation["price"] * nights

                # Get loyalty discount
                discounted_price = total_price * (1 - loyalty["discount"] / 100)
                reservation["discount"] = loyalty["discount"]

                # Create payment
                payment_data = {"price": discounted_price, "reservationUid": reservation["reservationUid"], "status": "PAID"}
                payment = self.payment_service.create_payment(username, payment_data)

                if not payment:
                    # Rollback reservation if payment fails
                    self.delete_reservation(username, reservation["reservationUid"])

                    # Queue for retry
                    retry_data = {"reservation": request_data, "payment": payment_data}
                    self.queue_for_retry("create_reservation", retry_data, username)

                    # Return success to user
                    return {"message": "Reservation queued for processing", "status": "PENDING", "reservationUid": reservation["reservationUid"]}
                if payment:
                    reservation["payment"] = payment
                    reservation["status"] = payment["status"]
                    self.loyalty_service.update_loyalty(username)

                del reservation["price"]
                return reservation

        except (ConnectionError, RequestException) as e:
            return jsonify({"message": "Service unavailable"}), HTTPStatus.SERVICE_UNAVAILABLE

        except Exception as e:
            # Queue for retry
            retry_data = {"reservation": request_data}
            self.queue_for_retry("create_reservation", retry_data, username)

            # Return temporary response
            return jsonify({"message": "Reservation queued for processing", "status": "PENDING"}), HTTPStatus.SERVICE_UNAVAILABLE

        return jsonify({"message": "Failed to create reservation"}), HTTPStatus.BAD_REQUEST

    def delete_reservation(self, username, reservation_uid):
        reservation = self.circuit_breaker_request(
            "reservation", "DELETE", f"{self.base_url}/reservations/{reservation_uid}", headers={"X-User-Name": username}
        )

        if reservation is None:
            payment = self.payment_service.get_payment(username, reservation_uid)
            if payment:

                self.payment_service.delete_payment(username, payment["paymentUid"])

                x = self.circuit_breaker_request("loyalty", "POST", f"{Config.LOYALTY_SERVICE_URL}/loyalty/decrease", headers={"X-User-Name": username})
                if x == {}:
                    retry_data = {"operation_type": "decrease_loyalty", "username": username}
                    self.queue_for_retry("decrease_loyalty", retry_data, username)
                return True
        return False

    def _enrich_reservation(self, username, reservation):
        payment = self.payment_service.get_payment(username, reservation["reservationUid"])
        if not payment:
            reservation["payment"] = {}
            reservation["status"] = "RESERVED"
        else:
            del payment["paymentUid"]
            reservation["payment"] = payment
            reservation["status"] = payment["status"]
        return reservation
