from marshmallow import fields, validate

from .base import BaseSchema


class ItemSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=[
            validate.Length(
                min=1, max=100, error="Category name must not " "exceed 100 characters"
            )
        ],
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(
                min=1, max=300, error="Category name must not" "exceed 300 characters"
            )
        ],
    )
    category_id = fields.Integer(required=True, strict=True)
    is_owner = fields.Boolean(dump_only=True)
