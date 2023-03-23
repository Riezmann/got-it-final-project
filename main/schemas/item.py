from marshmallow import Schema, fields

from main.schemas.base import PaginationSchema


class ItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    category_id = fields.Integer(required=True)
    is_owner = fields.Boolean(dump_only=True)


class PagingItemSchema(PaginationSchema):
    items = fields.List(fields.Nested(ItemSchema()), dump_only=True)
