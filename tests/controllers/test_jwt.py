from time import sleep

from main import app
from tests import get_login_auth_header


def test_jwt_fail_expired(client, users, categories, items):
    app.config["JWT_EXPIRATION_MINUTES"] = 0
    app.config["JWT_EXPIRATION_SECONDS"] = 1
    headers = get_login_auth_header(client)
    sleep(1)
    response = client.get("/categories", headers=headers)
    assert response.status_code == 401
    assert response.json["error_message"] == "Token has expired"


def test_jwt_fail_invalid(client, users, items):
    app.config["JWT_EXPIRATION_MINUTES"] = 1
    app.config["JWT_EXPIRATION_SECONDS"] = 0
    headers = {"Authorization": "Bearer This is an invalid token"}
    response = client.get("/categories", headers=headers)
    assert response.status_code == 401
    assert response.json["error_message"] == "Invalid token"


def test_jwt_fail_missing(client, users, items):
    app.config["JWT_EXPIRATION_MINUTES"] = 1
    app.config["JWT_EXPIRATION_SECONDS"] = 0
    headers = {"Authorization": ""}
    response = client.get("/categories", headers=headers)
    assert response.status_code == 401
    assert response.json["error_message"] == "Missing Authorization Header"


def test_jwt_fail_random_authorization_header(client, users, items):
    app.config["JWT_EXPIRATION_MINUTES"] = 1
    app.config["JWT_EXPIRATION_SECONDS"] = 0
    headers = {"Authorization": "This is a very random JWT"}
    response = client.get("/categories", headers=headers)
    assert response.status_code == 401
