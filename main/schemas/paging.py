from marshmallow import RAISE, fields, validate

from . import POSITIVE_STRING_TEMPLATE
from .base import BaseSchema

DEFAULT_ITEMS_PER_PAGE = 20
DEFAULT_PAGE = 1


class PagingSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    page = fields.Integer(
        validate=[validate.Range(min=1, error=POSITIVE_STRING_TEMPLATE % "Page")],
        load_default=DEFAULT_PAGE,
    )
    items_per_page = fields.Integer(
        validate=[
            validate.Range(min=1, error=POSITIVE_STRING_TEMPLATE % "Items per page")
        ],
        load_default=DEFAULT_ITEMS_PER_PAGE,
    )
    category_id = fields.Integer(
        validate=[validate.Range(min=1, error=POSITIVE_STRING_TEMPLATE % "Category ID")]
    )
