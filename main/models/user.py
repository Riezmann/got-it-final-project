from main import db


class UserModel(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    hashed_password = db.Column(db.String(256), nullable=False)
    items = db.relationship("ItemModel", back_populates="user", lazy="dynamic")
    categories = db.relationship("CategoryModel", back_populates="user", lazy="dynamic")
