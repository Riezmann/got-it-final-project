from flask import Blueprint
from flask.views import MethodView

from main import db
from main.commons.decorators import request_data, required_jwt
from main.commons.exceptions import BadRequest, Forbidden
from main.models.category import CategoryModel
from main.schemas.category import CategorySchema
from main.schemas.paging import PagingSchema

blp = Blueprint("Categories", __name__)


class CategoriesOperations(MethodView):
    @required_jwt()
    @request_data(CategorySchema)
    def post(self, user_id, category_data):
        if CategoryModel.query.filter(
            CategoryModel.name == category_data["name"]
        ).first():
            raise BadRequest(error_message="Category already exists")
        category = CategoryModel(name=category_data["name"])
        category.user_id = user_id
        db.session.add(category)
        db.session.commit()
        category.is_owner = True
        return CategorySchema().dump(category)

    @required_jwt()
    @request_data(PagingSchema)
    def get(self, user_id, queries_data):
        page = queries_data["page"]
        items_per_page = queries_data["items_per_page"]

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
    @required_jwt()
    def delete(self, user_id, category_id):
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
