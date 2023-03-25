from datetime import timedelta

from flask import Blueprint, jsonify, request
from flask.views import MethodView
from flask_jwt_extended import create_access_token
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.exc import SQLAlchemyError

from main import db
from main.commons.exceptions import BadRequest, InternalServerError, Unauthorized
from main.libs.parser import parse_request_body
from main.libs.salt_generator import generate_salt
from main.schemas.user import UserSchema

from ..models.user import UserModel

blp = Blueprint("Users", __name__, url_prefix="/")


class UserRegister(MethodView):
    def post(self):
        user_data = parse_request_body(request, UserSchema)
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            return BadRequest(error_message="User already exists").to_response()
        user = UserModel(
            email=user_data["email"],
            hashed_password=sha256.using(salt=generate_salt()).hash(
                user_data["password"]
            ),
        )
        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            return InternalServerError().to_response()
        access_token = create_access_token(
            identity=user.id, fresh=True, expires_delta=timedelta(minutes=120)
        )
        return jsonify({"access_token": access_token}), 200


class UserLogin(MethodView):
    def post(self):
        user_data = parse_request_body(request, UserSchema)
        user = UserModel.query.filter(UserModel.email == user_data["email"]).first()
        if user and sha256.verify(user_data["password"], user.hashed_password):
            access_token = create_access_token(
                identity=user.id, fresh=True, expires_delta=timedelta(minutes=120)
            )
            return jsonify({"access_token": access_token}), 200
        else:
            return Unauthorized().to_response()


userRegister_view = UserRegister.as_view("userRegister")
userLogin_view = UserLogin.as_view("userLogin")
blp.add_url_rule("/users", view_func=userRegister_view)
blp.add_url_rule("/access-tokens", view_func=userLogin_view)
