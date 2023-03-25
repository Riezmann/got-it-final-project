from marshmallow import ValidationError

from main.commons import exceptions
from main.libs.log import ServiceLogger


def parse_request_body(request, schema):
    try:
        data = schema().load(request.json)
    except ValidationError as err:
        raise exceptions.ValidationError(error_data=err.messages)
    return data


def parse_request_queries(request, schema):
    try:
        ServiceLogger(name="parse_request_queries").info(message=request.args.to_dict())
        data = schema().load(request.args.to_dict())
    except ValidationError as err:
        raise exceptions.ValidationError(error_data=err.messages)
    return data
