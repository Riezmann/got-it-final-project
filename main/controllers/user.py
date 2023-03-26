from datetime import timedelta

from flask import Blueprint, jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256 as sha256

from main import app, db
from main.commons.exceptions import BadRequest, Unauthorized
from main.schemas.user import UserSchema

from ..commons.decorators import request_data
from ..models.user import UserModel

blp = Blueprint("Users", __name__, url_prefix="/")


class UserRegister(MethodView):
    @request_data(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            return BadRequest(error_message="User already exists").to_response()
        user = UserModel(
            email=user_data["email"],
            hashed_password=sha256.hash(user_data["password"]),
        )
        user.save_to_db()
        access_token = create_access_token(
            identity=user.id,
            fresh=True,
            expires_delta=timedelta(
                minutes=app.config["JWT_EXPIRATION_MINUTES"],
                seconds=app.config["JWT_EXPIRATION_SECONDS"],
            ),
        )
        return jsonify({"access_token": access_token}), 200


class UserLogin(MethodView):
    @request_data(UserSchema)
    def post(self, user_data):
        user = db.session.query(UserModel).filter_by(email=user_data["email"]).first()
        if user and sha256.verify(user_data["password"], user.hashed_password):
            access_token = create_access_token(
                identity=user.id,
                fresh=True,
                expires_delta=timedelta(
                    minutes=app.config["JWT_EXPIRATION_MINUTES"],
                    seconds=app.config["JWT_EXPIRATION_SECONDS"],
                ),
            )
            return {"access_token": access_token}, 200
        else:
            return Unauthorized().to_response()


user_register_view = UserRegister.as_view("user_register")
user_login_view = UserLogin.as_view("user_login")
blp.add_url_rule("/users", view_func=user_register_view)
blp.add_url_rule("/access-tokens", view_func=user_login_view)
