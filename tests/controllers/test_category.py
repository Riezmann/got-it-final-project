import logging

from main.commons.exceptions import Forbidden, ValidationError

normal_category = {"name": "PC accessories"}
name_not_str_category = {"name": 1}
empty_category = {}

user_name = "bao.thcs20@gmail.com"
password = "Aa@123"

new_user_name = "bao-test1@gmail.com"
new_password = "Aa@123"


def test_create_category(client):
    response = client.post("/users", json={"email": user_name, "password": password})
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    response = client.post("/categories", json=normal_category, headers=headers)
    assert response.status_code == 200

    response = client.post("/categories", json=name_not_str_category, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == ValidationError.error_message

    response = client.post("/categories", json=empty_category, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == ValidationError.error_message

    response = client.post("/categories", json=normal_category, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Category already exists"


def test_paging_get_category(categories, client):
    """Test paging for get categories"""

    def check_category(category_object, category_idx):
        assert category_object["name"] == "Category {}".format(category_idx)

    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # case when getting the first 20 categories
    response = client.get("/categories", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 20
    assert page == 1
    for index, category in enumerate(response.json["items"]):
        category_index = (page - 1) * items_per_page + index
        check_category(category, category_index)

    # case when getting the next last 10 categories
    response = client.get("/categories?page=2", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 10
    assert page == 2
    for index, category in enumerate(response.json["items"]):
        category_index = (page - 1) * items_per_page + index
        check_category(category, category_index)

    # case when getting the page that out of range
    response = client.get("/categories?page=3", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == 30
    assert len(response.json["items"]) == 0
    assert response.json["page"] == 3

    # case when items_per_page varies
    for items_per_page in range(1, 20):
        response = client.get(
            f"/categories?items-per-page={items_per_page}", headers=headers
        )
        page = response.json["page"]
        total_items = response.json["total_items"]
        items = response.json["items"]
        assert response.status_code == 200
        assert total_items == 30
        assert len(items) == items_per_page
        assert page == 1
        for index, category in enumerate(response.json["items"]):
            category_index = (page - 1) * items_per_page + index
            check_category(category, category_index)

    # case when page is  invalid
    response = client.get("/categories?page=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"

    # case when items_per_page is invalid
    response = client.get("/categories?items-per-page=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"


def test_not_owner_get_category(categories, client):
    """Test case when user is not owner of category"""

    def check_category(category_object, category_idx):
        assert category_object["is_owner"] is False
        assert category_object["name"] == "Category {}".format(category_idx)

    response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # case when getting the first 20 categories
    response = client.get("/categories", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 20
    assert page == 1
    for index, category in enumerate(response.json["items"]):
        category_index = (page - 1) * items_per_page + index
        check_category(category, category_index)

    # case when getting the next last 10 categories
    response = client.get("/categories?page=2", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 10
    assert page == 2
    for index, category in enumerate(response.json["items"]):
        category_index = (page - 1) * items_per_page + index
        check_category(category, category_index)

    # case when getting the page that out of range
    response = client.get("/categories?page=3", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == 30
    assert len(response.json["items"]) == 0
    assert response.json["page"] == 3


def test_delete_category(categories, client):
    """Test delete category in case the user is the creator"""

    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = client.get("/categories", headers=headers)
    original_total_items = response.json["total_items"]
    logging.warning(response.json)
    items = response.json["items"]
    for category in items:
        response = client.delete(f"/categories/{category['id']}", headers=headers)
        assert response.status_code == 200
    response = client.get("/categories", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == original_total_items - len(items)


def test_unauthorized_delete_category(categories, client):
    """Test delete category in case the user is not the creator"""

    response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = client.get("/categories", headers=headers)
    original_total_items = response.json["total_items"]
    logging.warning(response.json)
    items = response.json["items"]
    for category in items:
        response = client.delete(f"/categories/{category['id']}", headers=headers)
        assert response.status_code == 403
        assert response.json["error_message"] == Forbidden.error_message
    response = client.get("/categories", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == original_total_items

    # case when the category_id is not exist
    response = client.delete("/categories/9999999999", headers=headers)
    assert response.status_code == 200
