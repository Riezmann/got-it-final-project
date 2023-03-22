from marshmallow import Schema, fields

from main.schemas.base import PaginationSchema


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    user_id = fields.Integer(load_only=True)
    is_owner = fields.Boolean(dump_only=True)


class PagingCategorySchema(PaginationSchema):
    items = fields.List(fields.Nested(CategorySchema()), dump_only=True)
