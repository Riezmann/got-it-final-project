from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    email = fields.Email(required=True, validate=validate.Email())

    password = fields.String(
        required=True,
        validate=[
            validate.Length(min=6, error="Password must be at least 6 characters long"),
            validate.Regexp(
                regex=r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]",
                error="Password must contain only letters, numbers, "
                "and special characters",
            ),
        ],
        load_only=True,
    )
