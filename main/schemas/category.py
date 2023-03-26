from marshmallow import fields, post_load, validate

from main.schemas.base import BaseSchema, PaginationSchema


class RequestCategorySchema(BaseSchema):
    name = fields.String(
        required=True,
        validate=[
            validate.Length(
                max=100, error="Category name must not " "exceed 100 characters"
            ),
            validate.Length(min=1, error="Category name must not be empty"),
        ],
    )

    @post_load
    def remove_whitespace(self, data, **_):
        data["name"] = data["name"].strip()
        return data


class ResponseCategorySchema(RequestCategorySchema):
    id = fields.Integer(required=True, dump_only=True, strict=True)
    is_owner = fields.Boolean(required=True, dump_only=True)


class PagingCategorySchema(PaginationSchema):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            setattr(self, key, value)

    items = fields.List(
        fields.Nested(ResponseCategorySchema()), required=True, dump_only=True
    )
