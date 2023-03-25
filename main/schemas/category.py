from marshmallow import fields, validate

from main.schemas.base import BaseSchema


class CategorySchema(BaseSchema):
    id = fields.Integer(dump_only=True, strict=True)
    name = fields.String(
        required=True,
        validate=[
            validate.Length(
                min=1, max=100, error="Category name must not " "exceed 100 characters"
            )
        ],
    )
    is_owner = fields.Boolean(dump_only=True)
