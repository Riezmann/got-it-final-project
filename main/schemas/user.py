from marshmallow import RAISE, fields, validate

from . import validate_length
from .base import BaseSchema


class UserSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    id = fields.Integer(dump_only=True)
    email = fields.Email(
        required=True,
        validate=[
            validate.Email(),
            *validate_length(target="Password", min_len=6, max_len=32),
        ],
    )
    password = fields.String(
        required=True,
        validate=[
            *validate_length(target="Password", min_len=6, max_len=32),
            validate.Regexp(
                regex=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]",
                error="Password must contain at least 1 letter, 1 number, "
                "and 1 special characters.",
            ),
        ],
        load_only=True,
    )
