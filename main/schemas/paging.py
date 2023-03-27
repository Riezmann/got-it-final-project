from marshmallow import RAISE, fields, validate

from .base import BaseSchema

DEFAULT_ITEMS_PER_PAGE = 20
DEFAULT_PAGE = 1


class PagingSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    page = fields.Integer(
        validate=[validate.Range(min=1, error="Page must be a positive number.")],
        load_default=DEFAULT_PAGE,
    )
    items_per_page = fields.Integer(
        validate=[
            validate.Range(min=1, error="Items per page must be a positive number.")
        ],
        load_default=DEFAULT_ITEMS_PER_PAGE,
    )
    category_id = fields.Integer(
        validate=[validate.Range(min=1, error="Page must be a positive number.")]
    )
