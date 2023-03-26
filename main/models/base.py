from main import db


class BaseModel(db.Model):

    __abstract__ = True

    created_time = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )
    updated_time = db.Column(
        db.DateTime, nullable=False, default=db.func.current_timestamp()
    )

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
