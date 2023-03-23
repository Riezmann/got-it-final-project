import logging

from main.commons.exceptions import Forbidden, ValidationError

normal_item = {"name": "Fan", "description": "A fan", "category_id": 1}
name_not_str_item = {"name": 1, "description": "A fan", "category_id": 1}
category_not_exist_item = {
    "name": "Fan",
    "description": "A fan",
    "category_id": 9999999999,
}
empty_item = {}

user_name = "bao.thcs20@gmail.com"
password = "Aa@123"

new_user_name = "bao-test1@gmail.com"
new_password = "Aa@123"


def test_create_item(items, client, categories):
    normal_item["category_id"] = categories[0].id
    name_not_str_item["category_id"] = categories[0].id
    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    logging.warning(response.json)
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    response = client.post("/items", json=normal_item, headers=headers)
    logging.warning(response.json)
    assert response.status_code == 200

    response = client.post("/items", json=name_not_str_item, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == ValidationError.error_message

    response = client.post("/items", json=empty_item, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == ValidationError.error_message

    response = client.post("/items", json=normal_item, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Item already exists"

    response = client.post("/items", json=category_not_exist_item, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Category does not exist"


def test_paging_get_items(items, client):
    """Test paging for get items"""

    def check_item(item_object, item_idx):
        assert item_object["name"] == "Item {}".format(item_idx)

    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # case when getting the first 20 items
    response = client.get("/items", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 20
    assert page == 1
    for index, item in enumerate(response.json["items"]):
        item_index = (page - 1) * items_per_page + index
        check_item(item, item_index)

    # case when getting the next last 10 items
    response = client.get("/items?page=2", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 10
    assert page == 2
    for index, item in enumerate(response.json["items"]):
        item_index = (page - 1) * items_per_page + index
        check_item(item, item_index)

    # case when getting the page that out of range
    response = client.get("/items?page=3", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == 30
    assert len(response.json["items"]) == 0
    assert response.json["page"] == 3

    # case when items_per_page varies
    for items_per_page in range(1, 20):
        response = client.get(
            f"/items?items-per-page={items_per_page}", headers=headers
        )
        page = response.json["page"]
        total_items = response.json["total_items"]
        items = response.json["items"]
        assert response.status_code == 200
        assert total_items == 30
        assert len(items) == items_per_page
        assert page == 1
        for index, item in enumerate(response.json["items"]):
            item_index = (page - 1) * items_per_page + index
            check_item(item, item_index)

    # case when items_per_page is invalid
    response = client.get("/items?items-per-page=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"
    assert response.json["error_data"] == {
        "page": "Page must be an integer",
        "items_per_page": "Items per page must be an integer",
    }

    # case when page is invalid
    response = client.get("/items?page=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"
    assert response.json["error_data"] == {
        "page": "Page must be an integer",
        "items_per_page": "Items per page must be an integer",
    }


def test_get_items_with_category_id(items, client, categories):
    """Test paging for get items"""

    def check_item(item_object, item_idx):
        assert item_object["name"] == "Item {}".format(item_idx)

    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # case when getting the first 20 items in the first categories
    response = client.get(f"/items?category-id={categories[0].id}", headers=headers)
    logging.warning(response.json)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 1
    assert page == 1
    for index, item in enumerate(response.json["items"]):
        item_index = (page - 1) * items_per_page + index
        check_item(item, item_index)

    # case when trying to get items with invalid category id
    response = client.get("/items?category-id=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"
    assert response.json["error_data"] == {
        "category_id": "Category id must be an integer",
    }

    # case when trying to get items with out-of-range category id
    response = client.get("/items?category-id=-1", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Category does not exist"


def test_not_owner_get_items(items, client):
    """Test case when user is not owner of item"""

    def check_item(item_object, item_idx):
        assert item_object["is_owner"] is False
        assert item_object["name"] == "Item {}".format(item_idx)

    response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    # case when getting the first 20 items
    response = client.get("/items", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 20
    assert page == 1
    for index, item in enumerate(response.json["items"]):
        item_index = (page - 1) * items_per_page + index
        check_item(item, item_index)

    # case when getting the next last 10 items
    response = client.get("/items?page=2", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    total_items = response.json["total_items"]
    items = response.json["items"]
    assert response.status_code == 200
    assert total_items == 30
    assert len(items) == 10
    assert page == 2
    for index, item in enumerate(response.json["items"]):
        item_index = (page - 1) * items_per_page + index
        check_item(item, item_index)

    # case when getting the page that out of range
    response = client.get("/items?page=3", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == 30
    assert len(response.json["items"]) == 0
    assert response.json["page"] == 3


def test_get_one_item(items, client):
    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for item in items:
        response = client.get(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json["name"] == item["name"]
        assert response.json["is_owner"] is True

    # case when item does not exist
    response = client.get("/items/9999999999", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Item not found"


def test_not_owner_get_one_item(items, client):
    response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for item in items:
        response = client.get(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json["name"] == item["name"]
        assert response.json["is_owner"] is False


def test_update_item(items, client, categories):
    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for item in items:
        response = client.put(
            f"/items/{item['id']}",
            json={
                "name": f"New name Item {item['id']}",
                "description": "New description",
                "category_id": item["category_id"],
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json["name"] == f"New name Item {item['id']}"

    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for item in items:
        assert item["name"] == f"New name Item {item['id']}"

    # case when item does not exist
    response = client.put(
        "/items/99999",
        json={
            "name": "New name Item",
            "description": "New description",
            "category_id": categories[0].id,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["name"] == "New name Item"


def test_unauthorized_update_item(items, client):
    response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}

    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for item in items:
        response = client.put(
            f"/items/{item['id']}",
            json={
                "name": f"New name Item {item['id']}",
                "description": "New description",
                "category_id": item["category_id"],
            },
            headers=headers,
        )
        assert response.status_code == 403
        assert response.json["error_message"] == Forbidden.error_message


def test_delete_item(items, client):
    """Test delete item in case the user is the creator"""

    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = client.get("/items", headers=headers)
    original_total_items = response.json["total_items"]
    logging.warning(response.json)
    items = response.json["items"]
    for item in items:
        response = client.delete(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 200
    response = client.get("/items", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == original_total_items - len(items)


def test_unauthorized_delete_item(items, client):
    """Test delete item in case the user is not the creator"""

    response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = client.get("/items", headers=headers)
    original_total_items = response.json["total_items"]
    logging.warning(response.json)
    items = response.json["items"]
    for item in items:
        response = client.delete(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 403
        assert response.json["error_message"] == Forbidden.error_message
    response = client.get("/items", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == original_total_items

    # case when the item_id is not exist
    response = client.delete("/items/9999999999", headers=headers)
    assert response.status_code == 200
