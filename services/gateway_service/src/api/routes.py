from http import HTTPStatus
from flask import jsonify, request
from src.api.decorators import handle_service_error
from src.services.hotel import HotelService
from src.services.reservation import ReservationService
from src.services.loyalty import LoyaltyService
from src.services.base import BaseServiceClient


def register_routes(app):
    hotel_service = HotelService()
    reservation_service = ReservationService()
    loyalty_service = LoyaltyService()

    @app.route("/manage/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "OK"}), 200

    @app.route("/api/v1/hotels", methods=["GET"])
    @handle_service_error
    def get_hotels():
        page = request.args.get("page", 1, type=int)
        size = request.args.get("size", 10, type=int)
        hotels_data = hotel_service.get_hotels(page, size)
        return jsonify(hotels_data), HTTPStatus.OK

    @app.route("/api/v1/reservations", methods=["GET"])
    @handle_service_error
    def get_reservations():
        username = BaseServiceClient.check_user_header(request.headers)
        user_reservations = reservation_service.get_user_reservations(username)
        return jsonify(user_reservations), HTTPStatus.OK

    @app.route("/api/v1/reservations", methods=["POST"])
    @handle_service_error
    def create_reservation():
        username = BaseServiceClient.check_user_header(request.headers)
        data = request.json
        reservation = reservation_service.create_reservation(username, data)
        if reservation:
            response = jsonify(reservation)
            status_code = response.get_json().get("status_code", 200)
            if status_code != 200:
                return jsonify(reservation), status_code
            return response, HTTPStatus.OK
        return jsonify({}), HTTPStatus.INTERNAL_SERVER_ERROR

    @app.route("/api/v1/reservations/<string:reservation_uid>", methods=["GET"])
    @handle_service_error
    def get_reservation(reservation_uid):
        username = BaseServiceClient.check_user_header(request.headers)
        reservation = reservation_service.get_reservation(username, reservation_uid)
        return jsonify(reservation), HTTPStatus.OK

    @app.route("/api/v1/reservations/<string:reservation_uid>", methods=["DELETE"])
    @handle_service_error
    def cancel_reservation(reservation_uid):
        username = BaseServiceClient.check_user_header(request.headers)
        success = reservation_service.delete_reservation(username, reservation_uid)
        if success:
            return jsonify({"message": "Reservation canceled"}), HTTPStatus.NO_CONTENT
        return jsonify({"message": "Failed to cancel reservation"}), HTTPStatus.BAD_REQUEST

    @app.route("/api/v1/me", methods=["GET"])
    @handle_service_error
    def get_user_info():
        username = BaseServiceClient.check_user_header(request.headers)
        user_reservations = reservation_service.get_user_reservations(username)
        loyalty, status_code = loyalty_service.get_loyalty(username)
        user_info = {"reservations": user_reservations, "loyalty": loyalty}
        if status_code != 200:
            jsonify(user_info), status_code

        return jsonify(user_info), HTTPStatus.OK

    @app.route("/api/v1/loyalty", methods=["GET"])
    @handle_service_error
    def get_loyalty():
        username = BaseServiceClient.check_user_header(request.headers)
        loyalty_info, status_code = loyalty_service.get_loyalty(username)

        return jsonify(loyalty_info), status_code
