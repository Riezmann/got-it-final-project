from flask import Blueprint
from flask.views import MethodView

from main import db
from main.commons.decorators import request_data, required_jwt
from main.commons.exceptions import BadRequest, Forbidden, NotFound
from main.libs.exist_checker import check_exist
from main.libs.log import ServiceLogger
from main.models.category import CategoryModel
from main.models.item import ItemModel
from main.schemas.item import PagingItemSchema, RequestItemSchema, ResponseItemSchema
from main.schemas.paging import PagingSchema

blp = Blueprint("Items", __name__)


class ItemsOperations(MethodView):
    @required_jwt()
    @request_data(RequestItemSchema)
    def post(self, user_id, item_data):
        check_exist(CategoryModel, error_out=True, id=item_data["category_id"])
        if check_exist(ItemModel, name=item_data["name"]):
            raise BadRequest(error_message="Item already exists")
        item = ItemModel(
            name=item_data["name"],
            description=item_data["description"],
            category_id=item_data["category_id"],
            user_id=user_id,
        )
        db.session.add(item)
        db.session.commit()
        item.is_owner = True
        return ResponseItemSchema().dump(item)

    @required_jwt()
    @request_data(PagingSchema)
    def get(self, user_id, queries_data):
        page = queries_data.get("page")
        items_per_page = queries_data.get("items_per_page")
        category_id = queries_data.get("category_id")
        item_query = ItemModel.query

        if category_id:
            check_exist(CategoryModel, error_out=True, id=category_id)
            item_query = item_query.filter(ItemModel.category_id == category_id)

        items = item_query.paginate(page=page, per_page=items_per_page, error_out=False)
        for item in items:
            item.is_owner = item.user_id == user_id

        paging = PagingItemSchema(
            page=page,
            items_per_page=items_per_page,
            items=items,
            total_items=CategoryModel.query.count(),
        )
        return PagingItemSchema().jsonify(paging)


class ItemOperations(MethodView):
    @required_jwt()
    def get(self, user_id, item_id):
        item = db.session.get(ItemModel, item_id)
        if not item:
            raise NotFound(error_message="Item not found")
        item.is_owner = item.user_id == user_id
        return ResponseItemSchema().dump(item)

    @required_jwt()
    @request_data(RequestItemSchema)
    def put(self, user_id, item_data, item_id):
        ServiceLogger(name="ItemOperations").info(message=f"item id: {item_id}")
        check_exist(CategoryModel, item_data["category_id"])
        item = db.session.get(ItemModel, item_id)
        if item:
            if item.user_id != user_id:
                raise Forbidden()
            item.name = item_data["name"]
            item.description = item_data["description"]
            item.category_id = item_data["category_id"]
            item.user_id = user_id
        else:
            raise NotFound(error_message="Item not found")
        db.session.commit()
        item.is_owner = True
        return ResponseItemSchema().dump(item)

    @required_jwt()
    def delete(self, user_id, item_id):
        item = db.session.get(ItemModel, item_id)
        if not item:
            raise NotFound(error_message="Item not found")
        if user_id != item.user_id:
            raise Forbidden()
        db.session.delete(item)
        db.session.commit()
        return {}


itemsOperations_view = ItemsOperations.as_view("itemsOperations")
itemOperations_view = ItemOperations.as_view("categoryOperations")
blp.add_url_rule("/items", view_func=itemsOperations_view)
blp.add_url_rule("/items/<int:item_id>", view_func=itemOperations_view)
