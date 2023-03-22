import secrets
import string
from datetime import datetime, timedelta

from flask.views import MethodView
from flask_jwt_extended import create_access_token
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256 as sha256

from main import db
from main.commons.exceptions import Unauthorized
from main.schemas.user import UserSchema

from ..models.user import UserModel

blp = Blueprint("Users", __name__, description="Operations on users")


@blp.route("/users")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        if UserModel.query.filter(UserModel.email == user_data["email"]).first():
            abort(409, message="User already exists")
        # Define the character set
        charset = string.ascii_letters + string.digits + "./"
        # Generate a random 16-byte salt
        salt = "".join(secrets.choice(charset) for _ in range(16)).encode("utf-8")
        user = UserModel(
            email=user_data["email"],
            hashed_password=sha256.using(salt=salt).hash(user_data["password"]),
            created_time=datetime.isoformat(datetime.utcnow()),
            updated_time=datetime.isoformat(datetime.utcnow()),
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully"}, 201


@blp.route("/access-tokens")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(UserModel.email == user_data["email"]).first()
        if user and sha256.verify(user_data["password"], user.hashed_password):
            access_token = create_access_token(
                identity=user.id, fresh=True, expires_delta=timedelta(minutes=120)
            )
            return {"access_token": access_token}, 200
        else:
            return Unauthorized().to_response()
