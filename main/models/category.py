from main import db

from .base import BaseModel


class CategoryModel(BaseModel):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    items = db.relationship(
        "ItemModel", back_populates="category", cascade="all, delete", lazy="dynamic"
    )
    user = db.relationship("UserModel", back_populates="categories")
