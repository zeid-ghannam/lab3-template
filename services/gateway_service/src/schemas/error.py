from marshmallow import Schema, fields


class ErrorSchema(Schema):
    message = fields.Str(required=True, description="Error message")


class ErrorDescriptionSchema(Schema):
    field = fields.Str(required=True)
    error = fields.Str(required=True)


class ValidationErrorSchema(Schema):
    message = fields.Str(required=True)
    errors = fields.List(fields.Nested(ErrorDescriptionSchema), required=True)
