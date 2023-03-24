from marshmallow import Schema, fields


class ItemSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    category_id = fields.Integer(required=True)
    is_owner = fields.Boolean(dump_only=True)
