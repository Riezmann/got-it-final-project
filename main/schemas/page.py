from item import ItemSchema
from marshmallow import Schema, fields


class PageSchema(Schema):
    page_number = fields.Integer(missing=1)
    item_per_page = fields.Integer(missing=20)
    total_items = fields.Integer(missing=0)
    items = fields.List(fields.Nested(ItemSchema()), many=True, dump_only=True)
