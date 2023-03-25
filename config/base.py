import logging
import secrets


class BaseConfig:
    LOGGING_LEVEL = logging.INFO

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:giabao0120@127.0.0.1/catalog"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    API_TITLE = "Catalog API"
    API_VERSION = "1.0.0"
    JWT_SECRET_KEY = str(secrets.SystemRandom().getrandbits(128))
