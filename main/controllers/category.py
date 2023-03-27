from flask import Blueprint
from flask.views import MethodView

from main import db
from main.commons.decorators import request_data, required_jwt
from main.commons.exceptions import BadRequest, Forbidden, NotFound
from main.libs.exist_checker import check_exist
from main.models.category import CategoryModel
from main.schemas.category import (
    PagingCategorySchema,
    RequestCategorySchema,
    ResponseCategorySchema,
)
from main.schemas.paging import PagingSchema

blp = Blueprint("Categories", __name__)


class CategoriesOperations(MethodView):
    @required_jwt
    @request_data(RequestCategorySchema)
    def post(self, category_data, user_id):
        if check_exist(CategoryModel, name=category_data["name"]):
            raise BadRequest(error_message="Category already exists.")
        category = CategoryModel(name=category_data["name"])
        category.user_id = user_id
        category.save_to_db()
        category.is_owner = True
        return ResponseCategorySchema().jsonify(category)

    @required_jwt
    @request_data(PagingSchema)
    def get(self, queries_data, user_id):
        page = queries_data["page"]
        items_per_page = queries_data["items_per_page"]

        categories = CategoryModel.query.paginate(
            page=page, per_page=items_per_page, error_out=False
        )
        for category in categories:
            category.is_owner = category.user_id == user_id
        paging = PagingCategorySchema(
            page=page,
            items_per_page=items_per_page,
            items=categories,
            total_items=CategoryModel.query.count(),
        )
        return PagingCategorySchema().jsonify(paging)


class CategoryOperations(MethodView):
    @required_jwt
    def get(self, category_id, user_id):
        category = db.session.get(CategoryModel, category_id)
        if not category:
            raise NotFound(error_message="Category not found.")
        category.is_owner = category.user_id == user_id
        return ResponseCategorySchema().jsonify(category)

    @required_jwt
    def delete(self, category_id, user_id):
        category = db.session.get(CategoryModel, category_id)
        if not category:
            raise NotFound(error_message="Category not found.")
        if user_id != category.user_id:
            raise Forbidden()
        category.delete_from_db()
        return {}


categoriesOperations_view = CategoriesOperations.as_view("categoriesOperations")
categoryOperations_view = CategoryOperations.as_view("categoryOperations")
blp.add_url_rule("/categories", view_func=categoriesOperations_view)
blp.add_url_rule("/categories/<int:category_id>", view_func=categoryOperations_view)
