from marshmallow import ValidationError

from main.commons import exceptions


def validate(request, schema):
    try:
        data = schema().load(request.json)
    except ValidationError as err:
        raise exceptions.ValidationError(error_data=err.messages)
    return data
