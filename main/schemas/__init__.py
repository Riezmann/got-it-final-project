from marshmallow import validate

LENGTH_ERROR_TEMPLATE = "%s must be between %d and %d characters long."
POSITIVE_STRING_TEMPLATE = "%s must be a positive number."


def validate_length(target, min_len=None, max_len=None):
    return [
        validate.Length(
            min=min_len,
            max=max_len,
            error=LENGTH_ERROR_TEMPLATE % (target, min_len, max_len),
        ),
    ]
