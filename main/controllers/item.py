from flask import Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError

from main import db
from main.commons.exceptions import (
    BadRequest,
    InternalServerError,
    NotFound,
    Unauthorized,
    ValidationError,
)
from main.engines.validator import validate
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.schemas.item import ItemSchema

blp = Blueprint("Items", __name__)


class ItemsOperations(MethodView):
    @jwt_required()
    def post(self):
        item_data = validate(request, ItemSchema)
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
            return ItemSchema().dump(item), 200
        except SQLAlchemyError:
            return InternalServerError().to_response()

    @jwt_required()
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

        if category_id:
            category = CategoryModel.query.get(category_id)
            if not category:
                return BadRequest(error_message="Category does not exist").to_response()
            items = ItemModel.query.filter(
                ItemModel.category_id == category_id
            ).paginate(page=page, per_page=items_per_page, error_out=False)
        else:
            items = ItemModel.query.paginate(
                page=page, per_page=items_per_page, error_out=False
            )
        for item in items:
            item.is_owner = item.user_id == user_id

        items = ItemSchema(many=True).dump(items)
        return {
            "page": page,
            "items_per_page": items_per_page,
            "items": items,
            "total_items": len(items),
        }


class ItemOperations(MethodView):
    @jwt_required()
    def get(self, item_id):
        item = ItemModel.query.get(item_id)
        if not item:
            return NotFound(error_message="Item not found").to_response()
        return ItemSchema().dump(item), 200

    @jwt_required()
    def put(self, item_id):
        item_data = validate(request, ItemSchema)
        user_id = get_jwt_identity()
        item = ItemModel.query.get(item_id)
        if item:
            if item.user_id != user_id:
                return Unauthorized().to_response()
            item.name = item_data["name"]
            item.description = item_data["description"]
            item.category_id = item_data["category_id"]
            item.user_id = user_id
        else:
            item = ItemModel(id=item_id, **item_data, user_id=user_id)
            db.session.add(item)
        db.session.commit()
        return ItemSchema().dump(item), 200

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


itemsOperations_view = ItemsOperations.as_view("itemsOperations")
itemOperations_view = ItemOperations.as_view("categoryOperations")
blp.add_url_rule("/items", view_func=itemsOperations_view)
blp.add_url_rule("/items/<int:item_id>", view_func=itemOperations_view)
