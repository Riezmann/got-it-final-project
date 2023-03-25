from flask import request
from marshmallow import ValidationError

from main.commons import exceptions


def request_data(schema):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                if request.method in ["POST", "PUT"]:
                    data = schema().load(request.json)
                else:
                    data = schema().load(request.args.to_dict())
            except ValidationError as err:
                raise exceptions.ValidationError(error_data=err.messages)
            return func(*args, data, **kwargs)

        return wrapper

    return decorator
