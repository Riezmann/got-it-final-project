from main import db


class CategoryModel(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_time = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    updated_time = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    items = db.relationship(
        "ItemModel", back_populates="category", cascade="all, delete", lazy="dynamic"
    )
    user = db.relationship("UserModel", back_populates="categories")
