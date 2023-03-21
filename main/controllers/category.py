from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from sqlalchemy.exc import SQLAlchemyError

from main import db
from main.commons.exceptions import BadRequest, InternalServerError
from main.models import CategoryModel
from main.schemas.base import PaginationSchema
from main.schemas.category import CategorySchema

blp = Blueprint("Categories", __name__, description="Operations on categories")


@blp.route("/categories")
class CategoryCreate(MethodView):
    @jwt_required()
    @blp.arguments(CategorySchema)
    def post(self, category_data):
        if CategoryModel.query.filter(
            CategoryModel.name == category_data["name"]
        ).first():
            raise BadRequest()
        user_id = get_jwt_identity()
        category = CategoryModel(name=category_data["name"])
        category.user_id = user_id
        try:
            db.session.add(category)
            db.session.commit()
        except SQLAlchemyError:
            raise InternalServerError()
        return {"message": "Category created successfully"}, 201

    @jwt_required()
    @blp.arguments(PaginationSchema)
    @blp.response(200, CategorySchema(many=True))
    def get(self, page_data):
        user_id = get_jwt_identity()
        categories = CategoryModel.query.filter(
            CategoryModel.user_id == user_id
        ).paginate(
            page=page_data["page"], per_page=page_data["per_page"], error_out=False
        )
        return categories.items
