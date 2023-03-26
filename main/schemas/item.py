from marshmallow import fields, post_load, validate

from .base import BaseSchema, PaginationSchema


class RequestItemSchema(BaseSchema):
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

    @post_load
    def remove_whitespace(self, data, **_):
        data["name"] = data["name"].strip()
        data["description"] = data["description"].strip()
        return data


class ResponseItemSchema(RequestItemSchema):
    id = fields.Integer(required=True, dump_only=True, strict=True)
    is_owner = fields.Boolean(required=True, dump_only=True)


class PagingItemSchema(PaginationSchema):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    items = fields.List(
        fields.Nested(ResponseItemSchema()), required=True, dump_only=True
    )
