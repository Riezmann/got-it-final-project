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

existing_user_name = "bao.thcs20@gmail.com"
password = "Aa@123"

new_user_name = "bao-test1@gmail.com"
new_password = "Aa@123"


def get_login_auth_header(client):
    auth_response = client.post(
        "/access-tokens", json={"email": existing_user_name, "password": password}
    )
    access_token = auth_response.json["access_token"]
    return {"Authorization": "Bearer {}".format(access_token)}


def get_regis_auth_header(client):
    auth_response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = auth_response.json["access_token"]
    return {"Authorization": "Bearer {}".format(access_token)}


def test_create_item(items, client, categories):
    normal_item["category_id"] = categories[0].id
    name_not_str_item["category_id"] = categories[0].id
    response = client.post(
        "/access-tokens", json={"email": existing_user_name, "password": password}
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


def validate_items(
    current_response, current_page, current_items_per_page, expect_is_owner
):
    for idx, curr_item in enumerate(current_response.json["items"]):
        item_idx = (current_page - 1) * current_items_per_page + idx
        assert curr_item["is_owner"] is expect_is_owner
        assert curr_item["name"] == "Item {}".format(item_idx)


def assert_response(
    running_response, expect_stt_code, expect_total_items, expect_len_items, expect_page
):
    assert running_response.status_code == expect_stt_code
    assert running_response.json["total_items"] == expect_total_items
    assert len(running_response.json["items"]) == expect_len_items
    assert running_response.json["page"] == expect_page


def validate_all_items(current_response, current_page, current_items_per_page):
    for idx, current_item in enumerate(current_response.json["items"]):
        item_idx = (current_page - 1) * current_items_per_page + idx
        assert current_item["is_owner"] is (idx % 2 == 0)
        assert current_item["name"] == "Item {}".format(item_idx)


def test_get_items_no_category_id(items, client):
    headers = get_login_auth_header(client)
    # test getting the first 20 items
    response = client.get("/items", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert_response(response, 200, 60, 20, 1)
    validate_all_items(response, page, items_per_page)

    # test getting the next page items
    response = client.get("/items?page=2", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert_response(response, 200, 60, 20, 2)
    validate_all_items(response, page, items_per_page)

    # case when getting the page that out of range
    response = client.get("/items?page=4", headers=headers)
    assert_response(response, 200, 60, 0, 4)

    # case when items_per_page varies
    for items_per_page in range(1, 30):
        response = client.get(
            f"/items?items-per-page={items_per_page}", headers=headers
        )
        page = response.json["page"]
        assert_response(response, 200, 60, items_per_page, 1)
        validate_all_items(response, page, items_per_page)

    # case when items_per_page is invalid
    response = client.get("/items?items-per-page=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"

    # case when page is invalid
    response = client.get("/items?page=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"


def test_get_items_with_category_id(items, client, categories):
    headers = get_login_auth_header(client)

    # case when getting the first 20 items in the first categories
    response = client.get(f"/items?category-id={categories[0].id}", headers=headers)
    logging.warning(response.json)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert_response(response, 200, 2, 2, 1)
    validate_all_items(response, page, items_per_page)
    for curr_item in response.json["items"]:
        assert curr_item["category_id"] == categories[0].id

    # case when trying to get items with invalid category id
    response = client.get("/items?category-id=abc", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Query params are not integers"

    # case when trying to get items with out-of-range category id
    response = client.get("/items?category-id=-1", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Category does not exist"


def test_not_owner_get_items(items, client):
    headers = get_regis_auth_header(client)

    # case when getting the first 20 items
    response = client.get("/items", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert_response(response, 200, 60, 20, 1)
    validate_items(response, page, items_per_page, False)

    # case when getting the next last 10 items
    response = client.get("/items?page=2", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert_response(response, 200, 60, 20, 2)
    validate_items(response, page, items_per_page, False)

    # case when getting the page that out of range
    response = client.get("/items?page=4", headers=headers)
    assert_response(response, 200, 60, 0, 4)


def test_get_one_item(items, client):
    headers = get_login_auth_header(client)

    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for index, item in enumerate(items):
        response = client.get(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json["name"] == item["name"]
        assert response.json["is_owner"] == (index % 2 == 0)

    # case when item does not exist
    response = client.get("/items/9999999999", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Item not found"


def test_not_owner_get_one_item(items, client):
    headers = get_regis_auth_header(client)
    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for item in items:
        response = client.get(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json["name"] == item["name"]
        assert response.json["is_owner"] is False


def test_update_item(items, client, categories):
    headers = get_login_auth_header(client)
    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for index, item in enumerate(items):
        if index % 2 != 0:  # only update the items that belong to the owner
            continue
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
    for index, item in enumerate(items):
        if index % 2 != 0:  # only update the items that belong to the owner
            continue
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
    headers = get_regis_auth_header(client)
    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for index, item in enumerate(items):
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
    headers = get_login_auth_header(client)
    response = client.get("/items", headers=headers)
    original_total_items = response.json["total_items"]
    logging.warning(response.json)
    items = response.json["items"]
    for index, item in enumerate(items):
        if index % 2 != 0:
            continue
        response = client.delete(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 200
    response = client.get("/items", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == original_total_items - len(items) / 2


def test_unauthorized_delete_item(items, client):
    headers = get_regis_auth_header(client)
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
    response = client.delete("/items/9999", headers=headers)
    assert response.status_code == 200
