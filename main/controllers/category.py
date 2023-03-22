from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from sqlalchemy.exc import SQLAlchemyError

from main import db
from main.commons.exceptions import (
    BadRequest,
    InternalServerError,
    Unauthorized,
    ValidationError,
)
from main.models.category import CategoryModel
from main.schemas.category import CategorySchema, PagingCategorySchema

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
    @blp.response(200, PagingCategorySchema)
    def get(self):
        user_id = get_jwt_identity()
        args = request.args

        page = args.get("page")
        items_per_page = args.get("items-per-page")

        if not page or not items_per_page:
            page = 1
            items_per_page = 20

        try:
            page = int(page)
            items_per_page = int(items_per_page)
        except ValueError:
            return ValidationError(
                error_message="Query params are not integers",
                error_data={
                    "page": "Page must be an integer",
                    "items_per_page": "Items per page must be an integer",
                },
            ).to_response()

        categories = CategoryModel.query.paginate(
            page=page, per_page=items_per_page, error_out=False
        )
        for category in categories:
            if category.user_id == user_id:
                category.is_owner = True
            else:
                category.is_owner = False
        page_response = PagingCategorySchema()
        page_response.page = page
        page_response.items_per_page = items_per_page
        page_response.items = categories
        page_response.total_items = categories.total
        return page_response


@blp.route("/categories/<int:category_id>")
class CategoryDelete(MethodView):
    @jwt_required()
    def delete(self, category_id):
        user_id = get_jwt_identity()
        category = CategoryModel.query.get(category_id)
        if not category:
            return {"message": "Category deleted successfully"}, 200
        if user_id != category.user_id:
            return Unauthorized().to_response()
        db.session.delete(category)
        db.session.commit()
        return {"message": "Category deleted successfully"}, 200
