def test_create_user_normal(session, client):
    response = client.post(
        "/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"}
    )
    assert response.status_code == 200


def test_create_user_with_wrong_email_form(session, client):
    response = client.post("/users", json={"email": "giabao", "password": "Aa@123"})
    assert response.status_code == 400


def test_create_user_with_wrong_password_form(session, client):
    response = client.post(
        "/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@23"}
    )
    assert response.status_code == 400


def test_create_user_with_missing_password(session, client):
    response = client.post("/users", json={"email": "bao.thcs20@gmail.com"})
    assert response.status_code == 400


def test_create_user_with_missing_email(session, client):
    response = client.post("/users", json={"password": "Aa@123"})
    assert response.status_code == 400


def test_create_user_with_existing_email(session, client):
    client.post("/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"})
    response = client.post(
        "/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"}
    )
    assert response.json["error_message"] == "User already exists"


def test_login_user_normal(client):
    client.post("/users", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"})
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20@gmail.com", "password": "Aa@123"}
    )
    assert response.status_code == 200


def test_login_user_wrong_password(client):
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20@gmail.com", "password": "Aa@13"}
    )
    assert response.status_code == 400


def test_login_user_with_wrong_email_form(client):
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20", "password": "Aa@123"}
    )

    assert response.status_code == 400


def test_login_user_with_wrong_password_form(client):
    response = client.post(
        "/access-tokens", json={"email": "bao.thcs20@gmail.com", "password": "Aa@3"}
    )

    assert response.status_code == 400


def test_login_user_with_missing_password(client):
    response = client.post("/access-tokens", json={"email": "bao.thcs20@gmail.com"})
    assert response.status_code == 400


def test_login_user_with_missing_email(client):
    response = client.post("/access-tokens", json={"password": "Aa@3"})
    assert response.status_code == 400
