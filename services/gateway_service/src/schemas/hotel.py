from marshmallow import Schema, fields, post_load, validate, EXCLUDE
from typing import Any, Dict


class HotelResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    hotelUid = fields.UUID(required=True, data_key="hotelUid")
    name = fields.Str(required=True)
    country = fields.Str(required=True)
    city = fields.Str(required=True)
    address = fields.Str(required=True)
    stars = fields.Int(required=True, validate=validate.Range(min=1, max=5))
    price = fields.Float(required=True)


class HotelInfoSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    hotelUid = fields.UUID(required=True, data_key="hotelUid")
    name = fields.Str(required=True)
    country = fields.Str()
    city = fields.Str()
    address = fields.Str()
    fullAddress = fields.Str()
    stars = fields.Int(required=True, validate=validate.Range(min=1, max=5))

    @post_load
    def create_full_address(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        if all(k in data for k in ["country", "city", "address"]):
            data["fullAddress"] = f"{data['country']}, {data['city']}, {data['address']}"
            del data["country"]
            del data["city"]
            del data["address"]
        return data


class HotelPaginationSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    page = fields.Int(required=True)
    pageSize = fields.Int(required=True)
    totalElements = fields.Int(required=True)
    items = fields.List(fields.Nested(HotelResponseSchema), required=True)
