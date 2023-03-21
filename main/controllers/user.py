import os
from datetime import timedelta

from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.exc import SQLAlchemyError

from main import db
from main.commons.exceptions import InternalServerError, Unauthorized
from main.models import UserModel
from main.schemas.user import UserSchema

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route("/users")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="User already exists")
        salt = os.urandom(32)
        mixed_password = salt + user_data["password"].encode("utf-8")
        user = UserModel(
            email=user_data["email"], hashed_password=sha256.hash(mixed_password)
        )
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            raise InternalServerError()
        return {"message": "User created successfully"}, 201


@blp.route("/access-tokens")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.email == user_data["email"]).first()
        mixed_password = user.salt + user_data["password"].encode("utf-8")
        if user and sha256.verify(mixed_password, user.hashed_password):
            access_token = create_access_token(
                identity=user.id, fresh=True, expires_delta=timedelta(hours=2)
            )
            return {"access_token": access_token}, 200
        else:
            raise Unauthorized()
