from flask import current_app, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from marshmallow import ValidationError

from main.commons import exceptions


def request_data(schema):
    """Decorator to validate the request data using the given schema"""

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


def required_jwt(func):
    """Decorator to ensure that the user is logged in before accessing the endpoint"""

    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        # ensure sync is used to ensure the synchronous execution of the function
        return current_app.ensure_sync(func)(*args, **kwargs, user_id=user_id)

    return wrapper
