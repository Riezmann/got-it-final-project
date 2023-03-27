from main import db
from main.commons.exceptions import BadRequest


def check_exist(model, error_out=False, **kwargs):
    obj = db.session.query(model).filter_by(**kwargs).first()
    if obj:
        return obj
    if error_out:
        raise BadRequest(
            error_message=f"{model.__tablename__.capitalize()} does not exist."
        )
    return False
