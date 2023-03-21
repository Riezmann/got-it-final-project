from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(
        required=True,
        validate=[
            validate.Length(min=6, error="Password must be at least 8 characters long"),
            validate.Regexp(
                regex=r"^[a-zA-Z0-9!@#$%^&*()_+{}\[\]:;\"\'<>,.?/\\|-]+$",
                error="Password must contain only letters, numbers, "
                "and special characters",
            ),
        ],
    )
    password = fields.String(required=True, load_only=True)
