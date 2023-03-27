from marshmallow import RAISE, fields, post_load, validate

from .base import BaseSchema, PaginationSchema


class RequestItemSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    name = fields.String(
        required=True,
        validate=[
            validate.Length(
                min=1, max=100, error="Category name must not " "exceed 100 characters."
            )
        ],
    )
    description = fields.String(
        required=True,
        validate=[
            validate.Length(
                max=100, error="Category name must not" "exceed 100 characters."
            ),
            validate.Length(min=1, error="Category name must not be empty."),
        ],
    )
    category_id = fields.Integer(required=True, strict=True)

    @post_load
    def remove_whitespace(self, data, **_):
        data["name"] = data["name"].strip()
        data["description"] = data["description"].strip()
        return data


class PutItemSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    name = fields.String(
        validate=[
            validate.Length(
                min=1, max=100, error="Category name must not " "exceed 100 characters."
            )
        ],
    )
    description = fields.String(
        validate=[
            validate.Length(
                max=100, error="Category name must not" "exceed 100 characters."
            ),
            validate.Length(min=1, error="Category name must not be empty."),
        ],
    )
    category_id = fields.Integer(strict=True)


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
