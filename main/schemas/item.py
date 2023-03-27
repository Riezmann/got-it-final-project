from marshmallow import RAISE, fields, post_load, pre_load

from ..commons.exceptions import MethodNotAllowed
from . import validate_length
from .base import BaseSchema, PaginationSchema


class RequestItemSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    name = fields.String(
        required=True,
        validate=validate_length(target="Item name", min_len=1, max_len=100),
    )
    description = fields.String(
        required=True,
        validate=validate_length(target="Item description", min_len=1, max_len=300),
    )
    category_id = fields.Integer(required=True, strict=True)

    @post_load
    def remove_whitespace(self, data, **_):
        data["name"] = data["name"].strip()
        data["description"] = data["description"].strip()
        return data


class UpdateItemSchema(BaseSchema):
    class Meta:
        unknown = RAISE

    name = fields.String(
        validate=validate_length(target="Item name", min_len=1, max_len=100),
    )
    description = fields.String(
        validate=validate_length(target="Item description", min_len=1, max_len=300),
    )
    category_id = fields.Integer(strict=True)

    @pre_load
    def check_empty_request(self, data, **_):
        if not data:
            raise MethodNotAllowed(error_message="Empty update request is not allowed")
        return data

    @post_load
    def remove_whitespace(self, data, **_):
        if data.get("name"):
            data["name"] = data["name"].strip()
        if data.get("description"):
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
