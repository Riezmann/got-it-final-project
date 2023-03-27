from main import db
from main.commons.exceptions import Forbidden
from main.models.item import ItemModel
from tests import get_login_auth_header, get_regis_auth_header

normal_item = {"name": "Item 1", "description": "A fan", "category_id": 1}
name_not_str_item = {"name": 1, "description": "A fan", "category_id": 1}
category_not_exist_item = {
    "name": "Item 1",
    "description": "A fan",
    "category_id": 9999999999,
}
empty_item = {}


def test_create_item_success(client, categories, users):
    headers = get_login_auth_header(client)
    normal_item["category_id"] = categories[0].id
    response = client.post("/items", json=normal_item, headers=headers)
    assert response.status_code == 200


def test_create_item_empty_string_name_fail(client, categories, users):
    headers = get_login_auth_header(client)
    response = client.post("/items", json=empty_item, headers=headers)
    assert response.status_code == 400


def test_create_item_not_string_name_fail(client, categories, users):
    headers = get_login_auth_header(client)
    response = client.post("/items", json=name_not_str_item, headers=headers)
    assert response.status_code == 400


def test_create_duplicated_item_fail(client, users, categories, items):
    headers = get_login_auth_header(client)
    normal_item["category_id"] = categories[0].id
    response = client.post("/items", json=normal_item, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Item already exists."


def test_create_item_with_category_not_exist_fail(client, users, categories, items):
    headers = get_login_auth_header(client)
    response = client.post("/items", json=category_not_exist_item, headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Category does not exist."


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


def test_get_items_no_queries_success(users, items, categories, client):
    headers = get_login_auth_header(client)
    response = client.get("/items", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert response.status_code == 200
    assert response.json["total_items"] == 120
    assert len(response.json["items"]) == 20
    assert response.json["page"] == 1
    for idx, current_item in enumerate(response.json["items"]):
        item_idx = (page - 1) * items_per_page + idx
        assert current_item["is_owner"] is (idx % 2 == 0)
        assert current_item["name"] == "Item {}".format(item_idx)


def test_get_items_only_page_query_success(users, items, categories, client):
    headers = get_login_auth_header(client)
    response = client.get("/items?page=2", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert response.status_code == 200
    assert response.json["total_items"] == 120
    assert len(response.json["items"]) == 20
    assert response.json["page"] == 2
    for idx, current_item in enumerate(response.json["items"]):
        item_idx = (page - 1) * items_per_page + idx
        assert current_item["is_owner"] is (idx % 2 == 0)
        assert current_item["name"] == "Item {}".format(item_idx)


def test_get_items_only_per_page_query_success(users, items, categories, client):
    headers = get_login_auth_header(client)
    response = client.get("/items?items_per_page=5", headers=headers)
    items_per_page = response.json["items_per_page"]
    page = response.json["page"]
    assert response.status_code == 200
    assert response.json["total_items"] == 120
    assert len(response.json["items"]) == 5
    assert response.json["page"] == 1
    for idx, current_item in enumerate(response.json["items"]):
        item_idx = (page - 1) * items_per_page + idx
        assert current_item["is_owner"] is (idx % 2 == 0)
        assert current_item["name"] == "Item {}".format(item_idx)


def test_get_items_only_category_id_query_success(users, items, categories, client):
    headers = get_login_auth_header(client)
    response = client.get(f"/items?category_id={categories[0].id}", headers=headers)
    assert response.status_code == 200
    assert response.json["total_items"] == 2
    assert len(response.json["items"]) == 2
    assert response.json["page"] == 1
    assert response.json["items"][0]["is_owner"] is True
    assert response.json["items"][1]["is_owner"] is False
    assert response.json["items"][0]["name"] == "Item 0"
    assert response.json["items"][1]["name"] == "Item 1"


def test_get_items_only_non_exist_category_id_query_fail(
    users, items, categories, client
):
    headers = get_login_auth_header(client)
    response = client.get("/items?category_id=999", headers=headers)
    assert response.status_code == 400
    assert response.json["error_message"] == "Category does not exist."


def test_get_items_full_queries_success(users, items, categories, client):
    headers = get_login_auth_header(client)
    response = client.get(
        f"/items?page=2&items_per_page=1&category_id={categories[0].id}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json["total_items"] == 2
    assert len(response.json["items"]) == 1
    assert response.json["page"] == 2
    assert response.json["items_per_page"] == 1
    assert response.json["items"][0]["is_owner"] is False
    assert response.json["items"][0]["name"] == "Item 1"


def test_get_items_string_page_fail(users, items, categories, client):
    headers = get_login_auth_header(client)
    response = client.get("/items?page=abc", headers=headers)
    assert response.status_code == 400


def test_get_item_by_id_success(users, items, categories, client):
    headers = get_login_auth_header(client)
    first_item = items[0]
    response = client.get(f"/items/{first_item.id}", headers=headers)
    assert response.status_code == 200
    assert response.json["is_owner"] is True
    assert response.json["name"] == "Item 0"


def test_get_item_by_id_not_exist_fail(users, items, categories, client):
    headers = get_login_auth_header(client)
    response = client.get("/items/999", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Item not found."


def test_unauthorized_get_items_success(items, client):
    headers = get_regis_auth_header(client)

    # case when getting the first 20 items
    response = client.get("/items", headers=headers)
    page = response.json["page"]
    items_per_page = response.json["items_per_page"]
    assert response.status_code == 200
    assert response.json["total_items"] == 120
    assert len(response.json["items"]) == 20
    assert response.json["page"] == 1
    for idx, current_item in enumerate(response.json["items"]):
        item_idx = (page - 1) * items_per_page + idx
        assert current_item["is_owner"] is False
        assert current_item["name"] == "Item {}".format(item_idx)


def test_unauthorized_get_item_by_id_success(items, client):
    headers = get_regis_auth_header(client)
    response = client.get("/items", headers=headers)
    items = response.json["items"]
    for item in items:
        response = client.get(f"/items/{item['id']}", headers=headers)
        assert response.status_code == 200
        assert response.json["name"] == item["name"]
        assert response.json["is_owner"] is False


def test_unauthorized_get_item_by_id_fail(items, client):
    headers = get_regis_auth_header(client)
    response = client.get("/items/999", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Item not found."


def test_authorized_update_item_success(items, client, categories):
    headers = get_login_auth_header(client)
    for index, item in enumerate(items):
        if index % 2 != 0:  # only update the items that belong to the owner
            continue
        response = client.put(
            f"/items/{item.id}",
            json={
                "name": f"New name Item {item.id}",
                "description": "New description",
                "category_id": item.category_id,
            },
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json["name"] == f"New name Item {item.id}"

    items = db.session.query(ItemModel).all()
    for index, item in enumerate(items):
        if index % 2 != 0:  # only update the items that belong to the owner
            continue
        assert item.name == f"New name Item {item.id}"


def test_update_item_causes_duplicating_name_fail(items, client, categories):
    headers = get_login_auth_header(client)
    response = client.put(
        f"/items/{items[0].id}",
        json={
            "name": "Item 1",
            "description": "New description",
            "category_id": categories[0].id,
        },
        headers=headers,
    )
    assert response.status_code == 500


def test_update_not_exist_item_fail(items, client, categories):
    headers = get_login_auth_header(client)
    response = client.put(
        "/items/99999",
        json={
            "name": "New name Item",
            "description": "New description",
            "category_id": categories[0].id,
        },
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json["error_message"] == "Item not found."


def test_unauthorized_update_item_fail(items, client):
    headers = get_regis_auth_header(client)
    for index, item in enumerate(items):
        response = client.put(
            f"/items/{item.id}",
            json={
                "name": f"New name Item {item.id}",
                "description": "New description",
                "category_id": item.category_id,
            },
            headers=headers,
        )
        assert response.status_code == 403
        assert response.json["error_message"] == Forbidden.error_message


def test_authorized_delete_item_success(items, client):
    headers = get_login_auth_header(client)
    original_total_items = len(items)
    for index, item in enumerate(items):
        if index % 2 != 0:
            continue
        response = client.delete(f"/items/{item.id}", headers=headers)
        assert response.status_code == 200
    assert db.session.query(ItemModel).count() == original_total_items - 60


def test_delete_not_exist_item_fail(items, client):
    headers = get_login_auth_header(client)
    response = client.delete("/items/99999", headers=headers)
    assert response.status_code == 404
    assert response.json["error_message"] == "Item not found."


def test_unauthorized_delete_item_fail(items, client):
    headers = get_regis_auth_header(client)
    original_total_items = len(items)
    for item in items:
        response = client.delete(f"/items/{item.id}", headers=headers)
        assert response.status_code == 403
        assert response.json["error_message"] == Forbidden.error_message
    assert db.session.query(ItemModel).count() == original_total_items
