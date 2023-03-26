from .base import BaseConfig


class Config(BaseConfig):
    DEBUG = True
    TESTING = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    JWT_EXPIRATION_MINUTES = 30
    JWT_EXPIRATION_SECONDS = 0
