from marshmallow import Schema, fields, validate, EXCLUDE
from src.schemas.enums import PaymentStatus


class PaymentInfoSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    status = fields.Str(validate=validate.OneOf([s.value for s in PaymentStatus]))
    price = fields.Integer()


class PaymentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    paymentUid = fields.UUID(required=True)
    status = fields.Str(required=True, validate=validate.OneOf([s.value for s in PaymentStatus]))
    price = fields.Float(required=True)
