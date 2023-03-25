from marshmallow import ValidationError

from main.commons import exceptions


def parse_request_body(request, schema):
    try:
        data = schema().load(request.json)
    except ValidationError as err:
        raise exceptions.ValidationError(error_data=err.messages)
    return data


def parse_request_queries(request, schema):
    try:
        raw_queries = request.args.to_dict()
        data = schema().load(raw_queries)
    except ValueError:
        raise ValidationError(error_message="Query params are not integers")
    return data
