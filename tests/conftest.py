import os
import sys
from pathlib import Path

import pytest
from alembic.command import upgrade
from alembic.config import Config
from passlib.hash import pbkdf2_sha256 as sha256

from main import app as _app
from main import db
from main.engines.salt_generator import generate_salt
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.models.user import UserModel

if os.getenv("ENVIRONMENT") != "test":
    print('Tests should be run with "ENVIRONMENT=test"')
    sys.exit(1)

ALEMBIC_CONFIG = (
    (Path(__file__) / ".." / ".." / "migrations" / "alembic.ini").resolve().as_posix()
)


@pytest.fixture(scope="session", autouse=True)
def app():
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope="session", autouse=True)
def recreate_database(app):
    db.reflect()
    db.drop_all()
    _config = Config(ALEMBIC_CONFIG)
    upgrade(_config, "heads")


@pytest.fixture(scope="function", autouse=True)
def session(recreate_database):
    from sqlalchemy.orm import sessionmaker

    connection = db.engine.connect()
    transaction = connection.begin()

    session_factory = sessionmaker(bind=connection)
    session = db.scoped_session(session_factory)

    db.session = session

    yield

    transaction.rollback()
    connection.close()
    session.close()


@pytest.fixture(scope="function", autouse=True)
def client(app, session):
    app.testing = True
    return app.test_client()


@pytest.fixture(scope="function")
def user():
    email = "bao.thcs20@gmail.com"
    password = "Aa@123"
    hashed_password = sha256.using(salt=generate_salt()).hash(password)
    user = UserModel(email=email, hashed_password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return db.session.query(UserModel).filter_by(email=email).first()


@pytest.fixture(scope="function")
def categories(user):
    for i in range(30):
        category = CategoryModel(name=f"Category {i}", user_id=user.id)
        db.session.add(category)
    db.session.commit()
    return db.session.query(CategoryModel).all()


@pytest.fixture(scope="function")
def items(categories, user):
    for i in range(30):
        item = ItemModel(
            name=f"Item {i}",
            description=f"Test item {i}",
            category_id=categories[i].id,
            user_id=user.id,
        )
        db.session.add(item)
    db.session.commit()
