def test_register_login_and_access_protected_me(client):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"username": "api_resident", "password": "resident-pass-123", "role": "resident"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["username"] == "api_resident"

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "api_resident", "password": "resident-pass-123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get(
        "/api/v1/protected/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["message"] == "Access granted"
    assert payload["user"]["username"] == "api_resident"
    assert payload["user"]["role"] == "resident"


def test_login_with_invalid_password_returns_401(client, register_user):
    register_response = register_user("api_manager", "manager-pass-123", "manager")
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "api_manager", "password": "wrong-pass-123"},
    )
    assert login_response.status_code == 401
