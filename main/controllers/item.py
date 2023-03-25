from flask import Blueprint
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from main import db
from main.commons.decorators import request_data
from main.commons.exceptions import BadRequest, Forbidden, NotFound
from main.libs.exist_checker import check_exist
from main.libs.log import ServiceLogger
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.schemas.item import ItemSchema
from main.schemas.paging import PagingSchema

blp = Blueprint("Items", __name__)


class ItemsOperations(MethodView):
    @jwt_required()
    @request_data(ItemSchema)
    def post(self, item_data):
        check_exist(CategoryModel, item_data["category_id"])
        item = ItemModel.query.filter(ItemModel.name == item_data["name"]).first()
        if item:
            return BadRequest(error_message="Item already exists").to_response()
        user_id = get_jwt_identity()
        item = ItemModel(
            name=item_data["name"],
            description=item_data["description"],
            category_id=item_data["category_id"],
            user_id=user_id,
        )
        db.session.add(item)
        db.session.commit()
        item.is_owner = True
        return ItemSchema().dump(item)

    @jwt_required()
    @request_data(PagingSchema)
    def get(self, queries_data):
        user_id = get_jwt_identity()
        page = queries_data.get("page")
        items_per_page = queries_data.get("items_per_page")
        category_id = queries_data.get("category_id")
        item_query = ItemModel.query

        if category_id:
            if not db.session.get(CategoryModel, category_id):
                return BadRequest(error_message="Category does not exist").to_response()
            item_query = item_query.filter(ItemModel.category_id == category_id)

        items = item_query.paginate(page=page, per_page=items_per_page, error_out=False)
        for item in items:
            item.is_owner = item.user_id == user_id

        items = ItemSchema(many=True).dump(items)
        return {
            "page": page,
            "items_per_page": items_per_page,
            "items": items,
            "total_items": item_query.count(),
        }


class ItemOperations(MethodView):
    @jwt_required()
    def get(self, item_id):
        item = db.session.get(ItemModel, item_id)
        if not item:
            return NotFound(error_message="Item not found").to_response()
        user_id = get_jwt_identity()
        item.is_owner = item.user_id == user_id
        return ItemSchema().dump(item)

    @jwt_required()
    @request_data(ItemSchema)
    def put(self, item_data, item_id):
        ServiceLogger(name="ItemOperations").info(message=f"item id: {item_id}")
        user_id = get_jwt_identity()
        check_exist(CategoryModel, item_data["category_id"])
        item = db.session.get(ItemModel, item_id)
        if item:
            if item.user_id != user_id:
                return Forbidden().to_response()
            item.name = item_data["name"]
            item.description = item_data["description"]
            item.category_id = item_data["category_id"]
            item.user_id = user_id
        else:
            return NotFound(error_message="Item not found").to_response()
        db.session.commit()
        return ItemSchema().dump(item)

    @jwt_required()
    def delete(self, item_id):
        user_id = get_jwt_identity()
        item = db.session.get(ItemModel, item_id)
        if not item:
            return NotFound(error_message="Item not found").to_response()
        if user_id != item.user_id:
            return Forbidden().to_response()
        db.session.delete(item)
        db.session.commit()
        return {}


itemsOperations_view = ItemsOperations.as_view("itemsOperations")
itemOperations_view = ItemOperations.as_view("categoryOperations")
blp.add_url_rule("/items", view_func=itemsOperations_view)
blp.add_url_rule("/items/<int:item_id>", view_func=itemOperations_view)
