from marshmallow import Schema, fields, validate, EXCLUDE


class LoyaltySchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.Str(required=True, validate=validate.OneOf(["BRONZE", "SILVER", "GOLD"]))
    discount = fields.Float(required=True)
    reservationCount = fields.Int(required=True)
