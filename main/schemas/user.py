from marshmallow import Schema, fields


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
