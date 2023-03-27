from main import db
from main.commons.exceptions import Forbidden, ValidationError
from main.models.category import CategoryModel
from main.models.item import ItemModel
from tests import get_login_auth_header, get_regis_auth_header

normal_category = {"name": "Category 1"}
name_not_str_category = {"name": 1}
empty_category = {}


def test_create_category_success(client, users):
    headers = get_login_auth_header(client)
    response = client.post("/categories", json=normal_category, headers=headers)
    assert response.status_code == 200


def test_create_category_empty_string_name_fail(client, users):
    headers = get_login_auth_header(client)
    response = client.post("/categories", json=empty_category, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == ValidationError.error_message


def test_create_category_not_string_name_fail(client, users):
    headers = get_login_auth_header(client)
    response = client.post("/categories", json=name_not_str_category, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == ValidationError.error_message


def test_create_duplicated_category_fail(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.post("/categories", json=normal_category, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Category already exists."


def test_get_categories_no_queries_success(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.get("/categories", headers=headers)
    assert response.status_code == 200
    assert len(response.json["items"]) == 20
    assert response.json["total_items"] == 60
    for index, category in enumerate(response.json["items"]):
        assert category["name"] == "Category {}".format(index)


def test_get_categories_only_page_query_success(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.get("/categories?page=2", headers=headers)
    assert response.status_code == 200
    assert len(response.json["items"]) == 20
    assert response.json["total_items"] == 60
    for index, category in enumerate(response.json["items"]):
        assert category["name"] == "Category {}".format(index + 20)


def test_get_categories_only_per_page_query_success(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.get("/categories?items_per_page=10", headers=headers)
    assert response.status_code == 200
    assert len(response.json["items"]) == 10
    assert response.json["total_items"] == 60
    for index, category in enumerate(response.json["items"]):
        assert category["name"] == "Category {}".format(index)


def test_get_categories_full_queries_success(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.get("/categories?page=2&items_per_page=10", headers=headers)
    assert response.status_code == 200
    assert len(response.json["items"]) == 10
    assert response.json["total_items"] == 60
    for index, category in enumerate(response.json["items"]):
        assert category["name"] == "Category {}".format(index + 10)


def test_get_categories_with_redundant_queries_fail(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.get(
        "/categories?page=2&items_per_page=10&redundant=1", headers=headers
    )
    assert response.status_code == 400


def test_get_categories_with_negative_queries_fail(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.get("/categories?page=-1&items_per_page=10", headers=headers)
    assert response.status_code == 400


def test_get_categories_with_string_queries_fail(client, users, categories):
    headers = get_login_auth_header(client)
    response = client.get("/categories?page='abc'&items_per_page=10", headers=headers)
    assert response.status_code == 400


def test_not_owner_get_categories(categories, client):
    headers = get_regis_auth_header(client)
    response = client.get("/categories", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 60
    assert len(items) == 20
    assert page == 1
    for index, category in enumerate(response.json["items"]):
        category_index = (page - 1) * items_per_page + index
        assert category["is_owner"] is False
        assert category["name"] == "Category {}".format(category_index)


def test_owner_get_category_success(client, users, categories, items):
    headers = get_login_auth_header(client)
    response = client.get(f"/categories/{categories[0].id}", headers=headers)
    assert response.status_code == 200
    assert response.json["is_owner"] is True
    assert response.json["name"] == "Category 0"


def test_not_owner_get_category_success(client, users, categories, items):
    headers = get_regis_auth_header(client)
    response = client.get(f"/categories/{categories[0].id}", headers=headers)
    assert response.status_code == 200
    assert response.json["is_owner"] is False
    assert response.json["name"] == "Category 0"


def test_get_not_exist_category(client, users, categories, items):
    headers = get_login_auth_header(client)
    response = client.get("/categories/99999", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Category not found."


def test_delete_category(categories, items, client):
    headers = get_login_auth_header(client)
    original_total_items = db.session.query(CategoryModel).count()
    categories = db.session.query(CategoryModel).limit(30).all()
    for category in categories:
        response = client.delete(f"/categories/{category.id}", headers=headers)
        assert response.status_code == 200
    assert db.session.query(CategoryModel).count() == original_total_items - 30
    # test delete cascade items
    items = db.session.query(ItemModel).all()
    for index, item in enumerate(items):
        assert item.name == "Item {}".format(60 + index)


def test_unauthorized_delete_category(categories, users, items, client):
    headers = get_regis_auth_header(client)
    original_total_items = db.session.query(CategoryModel).count()
    categories = db.session.query(CategoryModel).all()
    for category in categories:
        response = client.delete(f"/categories/{category.id}", headers=headers)
        assert response.status_code == 403
        assert response.json["error_message"] == Forbidden.error_message
    assert original_total_items == db.session.query(CategoryModel).count()


def test_delete_not_exist_category(categories, items, client):
    headers = get_login_auth_header(client)
    response = client.delete("/categories/9999999999", headers=headers)
    assert response.status_code == 404
