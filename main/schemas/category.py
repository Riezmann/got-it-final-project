from marshmallow import Schema, fields, validate

from main.schemas.base import PaginationSchema


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(min=1, max=300)])
    is_owner = fields.Boolean(dump_only=True)


class PagingCategorySchema(PaginationSchema):
    items = fields.List(fields.Nested(CategorySchema()), dump_only=True)
