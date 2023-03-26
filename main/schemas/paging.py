from marshmallow import RAISE, fields, validate

from .base import BaseSchema


class PagingSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    page = fields.Integer(
        validate=[validate.Range(min=1, error="page must be a positive number")],
        load_default=1,
    )
    items_per_page = fields.Integer(
        validate=[
            validate.Range(min=1, error="items per page must be a positive number")
        ],
        load_default=20,
    )
    category_id = fields.Integer(
        validate=[validate.Range(min=1, error="page must be a positive number")]
    )
