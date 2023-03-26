from importlib import import_module

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from ._config import config
from .commons.error_handlers import register_error_handlers
from .commons.exceptions import Unauthorized

app = Flask(__name__)

app.config.from_object(config)

db = SQLAlchemy(app)
jwt = JWTManager(app)


@jwt.expired_token_loader
def expired_token_callback(_header, _payload):
    return Unauthorized(error_message="Token has expired").to_response()


@jwt.invalid_token_loader
def invalid_token_callback(_):
    return Unauthorized(error_message="Invalid token").to_response()


@jwt.unauthorized_loader
def unauthorized_callback(error):
    return Unauthorized(error_message=error).to_response()


migrate = Migrate(app, db)

CORS(app)


def register_subpackages():
    from main import models

    for m in models.__all__:
        import_module("main.models." + m)

    from main.controllers.category import blp as category_blueprint
    from main.controllers.item import blp as item_blueprint
    from main.controllers.user import blp as user_blueprint

    app.register_blueprint(category_blueprint)
    app.register_blueprint(item_blueprint)
    app.register_blueprint(user_blueprint)


register_subpackages()
register_error_handlers(app)
