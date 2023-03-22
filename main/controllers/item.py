from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_smorest import Blueprint
from sqlalchemy.exc import SQLAlchemyError

from main import db
from main.commons.exceptions import (
    BadRequest,
    InternalServerError,
    NotFound,
    Unauthorized,
    ValidationError,
)
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.schemas.item import ItemSchema, PagingItemSchema

blp = Blueprint("Items", __name__, description="Operations on items")


@blp.route("/items")
class ItemsOperation(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    @blp.arguments(ItemSchema)
    def post(self, item_data):
        category = CategoryModel.query.filter(
            CategoryModel.id == item_data["category_id"]
        ).first()
        if not category:
            return BadRequest(error_message="Category does not exist").to_response()
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
        item.is_owner = True
        try:
            db.session.add(item)
            db.session.commit()
            return item, 201
        except SQLAlchemyError:
            return InternalServerError().to_response()

    @jwt_required()
    @blp.response(200, PagingItemSchema)
    def get(self):

        user_id = get_jwt_identity()
        args = request.args

        page = args.get("page")
        items_per_page = args.get("items-per-page")
        category_id = args.get("category-id")

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

        page_response = PagingItemSchema()
        page_response.page = page
        page_response.items_per_page = items_per_page

        if category_id:
            category = CategoryModel.query.filter(
                CategoryModel.id == category_id
            ).first()
            if not category:
                return BadRequest(error_message="Category does not exist").to_response()
            items = ItemModel.query.filter(
                ItemModel.category_id == category_id
            ).paginate(page=page, per_page=items_per_page, error_out=False)
            page_response.items = items
            page_response.total_items = items.total
            for item in items:
                if item.user_id == user_id:
                    item.is_owner = True
                else:
                    item.is_owner = False
        else:
            items = ItemModel.query.paginate(
                page=page, per_page=items_per_page, error_out=False
            )
            page_response.items = items
            page_response.total_items = items.total
            for item in items:
                if item.user_id == user_id:
                    item.is_owner = True
                else:
                    item.is_owner = False
        return page_response


@blp.route("/items/<int:item_id>")
class ItemOperation(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        item = ItemModel.query.get(item_id)
        if not item:
            return NotFound(error_message="Hello").to_response()
        return item

    @jwt_required()
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        user_id = get_jwt_identity()
        item = ItemModel.query.get(item_id)
        if not item:
            item.name = item_data["name"]
            item.description = item_data["description"]
            item.category_id = item_data["category_id"]
            item.user_id = user_id
        if item.user_id != user_id:
            return Unauthorized().to_response()
        item = ItemModel(id=item_id, **item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            return InternalServerError().to_response()
        return item

    @jwt_required()
    def delete(self, item_id):
        user_id = get_jwt_identity()
        item = ItemModel.query.get(item_id)
        if not item:
            return {"message": "Item deleted successfully"}, 200
        if user_id != item.user_id:
            return Unauthorized().to_response()
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted successfully"}, 200
