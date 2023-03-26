from marshmallow import fields, validate

from .base import BaseSchema


class UserSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(
        required=True,
        validate=[
            validate.Email(),
            validate.Length(
                min=6, max=255, error="Email must be between 6 and 255 characters long"
            ),
        ],
    )
    password = fields.String(
        required=True,
        validate=[
            validate.Length(
                min=6,
                max=255,
                error="Password must be between 6 and 255 characters long",
            ),
            validate.Regexp(
                regex=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]",
                error="Password must contain at least 1 letter, 1 number, "
                "and 1 special characters",
            ),
        ],
        load_only=True,
    )
