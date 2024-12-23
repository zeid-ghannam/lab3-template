from marshmallow import Schema, fields, post_load, validate, EXCLUDE
from typing import Any, Dict
from src.schemas.hotel import HotelInfoSchema
from src.schemas.payment import PaymentInfoSchema
from src.schemas.enums import ReservationStatus


class ReservationResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reservationUid = fields.UUID()
    hotel = fields.Nested(HotelInfoSchema, required=True)
    startDate = fields.Date(format="%Y-%m-%d")
    endDate = fields.Date(format="%Y-%m-%d")

    @post_load
    def change_dates_to_str(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        data["startDate"] = data["startDate"].strftime("%Y-%m-%d")
        data["endDate"] = data["endDate"].strftime("%Y-%m-%d")
        return data


class ReservationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    reservationUid = fields.UUID(required=True)
    hotel = fields.Nested(HotelInfoSchema, required=True)
    startDate = fields.Date(required=True, format="%Y-%m-%d")
    endDate = fields.Date(required=True, format="%Y-%m-%d")
    status = fields.Str(required=True, validate=validate.OneOf([s.value for s in ReservationStatus]))
    payment = fields.Nested(PaymentInfoSchema, required=True)
