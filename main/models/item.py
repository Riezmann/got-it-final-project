from main import db


class ItemModel(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    created_time = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    updated_time = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    user = db.relationship("UserModel", back_populates="items")
    category = db.relationship("CategoryModel", back_populates="items")
