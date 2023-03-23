import logging

normal_category = {"name": "PC accessories"}
name_not_str_category = {"name": 1}
empty_category = {}

user_name = "bao.thcs20@gmail.com"
password = "Aa@123"


def test_create_category(client):
    response = client.post("/users", json={"email": user_name, "password": password})
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = client.post("/categories", json=normal_category, headers=headers)
    assert response.status_code == 200

    response = client.post("/categories", json=name_not_str_category, headers=headers)
    assert response.status_code == 400

    response = client.post("/categories", json=empty_category, headers=headers)
    assert response.status_code == 400


def test_get_category(categories, client):
    response = client.post(
        "/access-tokens", json={"email": user_name, "password": password}
    )
    access_token = response.json["access_token"]
    headers = {"Authorization": "Bearer {}".format(access_token)}
    response = client.get("/categories", headers=headers)
    logging.warning(response.json)

    assert response.status_code == 400
