existing_user_name = "bao.thcs20@gmail.com"
existing_password = "Aa@123"

new_user_name = "bao-test1@gmail.com"
new_password = "Aa@123"


def get_login_auth_header(client):
    auth_response = client.post(
        "/access-tokens",
        json={"email": existing_user_name, "password": existing_password},
    )
    access_token = auth_response.json["access_token"]
    return {"Authorization": "Bearer {}".format(access_token)}


def get_regis_auth_header(client):
    auth_response = client.post(
        "/users", json={"email": new_user_name, "password": new_password}
    )
    access_token = auth_response.json["access_token"]
    return {"Authorization": "Bearer {}".format(access_token)}
