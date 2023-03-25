from main import db
from main.commons.exceptions import BadRequest


def check_exist(model, unique_prop):
    obj = db.session.get(model, unique_prop)
    if obj:
        return obj
    raise BadRequest(error_message=f"{model.__tablename__} does not exist")
