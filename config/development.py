import secrets

from .base import BaseConfig


class Config(BaseConfig):
    DEBUG = True
    API_TITLE = "Catalog API"
    API_VERSION = "1.0.0"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/"
    OPENAPI_SWAGGER_UI_PATH = "/docs"
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    JWT_SECRET_KEY = str(secrets.SystemRandom().getrandbits(128))
