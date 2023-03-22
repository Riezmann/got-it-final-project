import logging


class BaseConfig:
    LOGGING_LEVEL = logging.INFO

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:giabao0120@127.0.0.1/catalog"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
