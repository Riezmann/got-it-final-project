import os
import sys
from pathlib import Path

import pytest
from alembic.command import upgrade
from alembic.config import Config
from passlib.hash import pbkdf2_sha256 as sha256

from main import app as _app
from main import db
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
def users():
    email1 = "bao.thcs20@gmail.com"
    password1 = "Aa@123"
    email2 = "bao.test1@gmail.com"
    password2 = "Aa@123"
    hashed_password1 = sha256.hash(password1)
    hashed_password2 = sha256.hash(password2)
    user1 = UserModel(email=email1, hashed_password=hashed_password1)
    user2 = UserModel(email=email2, hashed_password=hashed_password2)
    db.session.add(user1)
    db.session.add(user2)
    db.session.commit()
    return db.session.query(UserModel).all()


@pytest.fixture(scope="function")
def categories(users):
    for i in range(30):
        category = CategoryModel(name=f"Category {i}", user_id=users[0].id)
        db.session.add(category)
    for i in range(30, 60):
        category = CategoryModel(name=f"Category {i}", user_id=users[1].id)
        db.session.add(category)
    db.session.commit()
    return db.session.query(CategoryModel).all()


@pytest.fixture(scope="function")
def items(categories, users):
    for i in range(0, 60):
        item1 = ItemModel(
            name=f"Item {2*i}",
            description=f"Test item {i}",
            category_id=categories[i].id,
            user_id=users[0].id,
        )
        item2 = ItemModel(
            name=f"Item {2*i + 1}",
            description=f"Test item {i + 1}",
            category_id=categories[i].id,
            user_id=users[1].id,
        )
        db.session.add(item1)
        db.session.add(item2)
    db.session.commit()
    return db.session.query(ItemModel).all()
