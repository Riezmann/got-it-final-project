from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from main import db
from main.commons.exceptions import BadRequest, Forbidden
from main.libs.parser import parse_request_body, parse_request_queries
from main.models.category import CategoryModel
from main.schemas.category import CategorySchema
from main.schemas.paging import PagingSchema

blp = Blueprint("Categories", __name__)


class CategoriesOperations(MethodView):
    @jwt_required()
    def post(self):
        category_data = parse_request_body(request, CategorySchema)
        if CategoryModel.query.filter(
            CategoryModel.name == category_data["name"]
        ).first():
            raise BadRequest(error_message="Category already exists")
        user_id = get_jwt_identity()
        category = CategoryModel(name=category_data["name"])
        category.user_id = user_id
        db.session.add(category)
        db.session.commit()
        category.is_owner = True
        return CategorySchema().dump(category)

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        page, items_per_page = parse_request_queries(request, PagingSchema)

        categories = CategoryModel.query.paginate(
            page=page, per_page=items_per_page, error_out=False
        )

        for category in categories:
            category.is_owner = category.user_id == user_id

        categories = CategorySchema(many=True).dump(categories)
        return {
            "page": page,
            "items_per_page": items_per_page,
            "items": categories,
            "total_items": CategoryModel.query.count(),
        }


class CategoryOperations(MethodView):
    @jwt_required()
    def delete(self, category_id):
        user_id = get_jwt_identity()
        category = db.session.get(CategoryModel, category_id)
        if not category:
            return {}
        if user_id != category.user_id:
            return Forbidden().to_response()
        db.session.delete(category)
        db.session.commit()
        return {}


categoriesOperations_view = CategoriesOperations.as_view("categoriesOperations")
categoryOperations_view = CategoryOperations.as_view("categoryOperations")
blp.add_url_rule("/categories", view_func=categoriesOperations_view)
blp.add_url_rule("/categories/<int:category_id>", view_func=categoryOperations_view)
