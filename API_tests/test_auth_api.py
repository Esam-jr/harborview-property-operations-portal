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


def test_auth_me_returns_only_authenticated_user_data(client):
    register_alice = client.post(
        "/api/v1/auth/register",
        json={
            "username": "me_alice",
            "password": "alice-pass-123",
            "role": "resident",
            "shipping_address": "Alice Shipping",
            "mailing_address": "Alice Mailing",
        },
    )
    assert register_alice.status_code == 201

    register_bob = client.post(
        "/api/v1/auth/register",
        json={
            "username": "me_bob",
            "password": "bob-pass-123",
            "role": "resident",
            "shipping_address": "Bob Shipping",
            "mailing_address": "Bob Mailing",
        },
    )
    assert register_bob.status_code == 201

    login_alice = client.post(
        "/api/v1/auth/login",
        json={"username": "me_alice", "password": "alice-pass-123"},
    )
    assert login_alice.status_code == 200
    alice_token = login_alice.json()["access_token"]

    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert me_response.status_code == 200
    payload = me_response.json()
    assert payload["username"] == "me_alice"
    assert payload["shipping_address"] == "Alice Shipping"
    assert payload["mailing_address"] == "Alice Mailing"
    assert payload["username"] != "me_bob"
    assert payload["shipping_address"] != "Bob Shipping"
