from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
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


def required_jwt():
    def decorator(func):
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            return current_app.ensure_sync(func)(*args, user_id, **kwargs)

        return wrapper

    return decorator
