from marshmallow import fields, validate

from .base import BaseSchema


class PagingSchema(BaseSchema):
    page = fields.Integer(validate=[validate.Range(min=1)], load_default=1, strict=True)
    items_per_page = fields.Integer(
        validate=[validate.Range(min=1)], load_default=20, strict=True
    )
    category_id = fields.Integer(validate=[validate.Range(min=1)], strict=True)
