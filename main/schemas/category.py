from marshmallow import Schema, fields


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    user_id = fields.Integer(required=True, load_only=True)
    is_owner = fields.Boolean(dump_only=True)
