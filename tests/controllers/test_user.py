def test_create_user_normal_success(session, client):
    response = client.post(
        "/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"}
    )
    assert response.status_code == 200


def test_create_user_with_wrong_email_form_fail(session, client):
    response = client.post("/users", json={"email": "giabao", "password": "Aa@123"})
    assert response.status_code == 400


def test_create_user_with_wrong_password_form_fail(session, client):
    response = client.post(
        "/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@23"}
    )
    assert response.status_code == 400


def test_create_user_with_missing_password_fail(session, client):
    response = client.post("/users", json={"email": "bao.thcs20@gmail.com"})
    assert response.status_code == 400


def test_create_user_with_missing_email_fail(session, client):
    response = client.post("/users", json={"password": "Aa@123"})
    assert response.status_code == 400


def test_create_user_with_existing_email_fail(session, client):
    client.post("/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"})
    response = client.post(
        "/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"}
    )
    assert response.status_code == 400
    assert response.json["error_message"] == "User already exists"


def test_login_user_normal_success(client):
    client.post("/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"})
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"}
    )
    assert response.status_code == 200


def test_login_user_wrong_password_fail(client):
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20@gmail.com", "password": "Aa@153"}
    )
    assert response.status_code == 401


def test_login_user_with_wrong_email_form_fail(client):
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20", "password": "Aa@123"}
    )
    assert response.status_code == 400


def test_login_user_with_wrong_password_form_fail(client):
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20@gmail.com", "password": "Aa@3"}
    )

    assert response.status_code == 400


def test_login_user_with_missing_password_fail(client):
    response = client.post("/access-tokens", json={"email": "bao.thcs20@gmail.com"})
    assert response.status_code == 400


def test_login_user_with_missing_email_fail(client):
    response = client.post("/access-tokens", json={"password": "Aa@3"})
    assert response.status_code == 400
