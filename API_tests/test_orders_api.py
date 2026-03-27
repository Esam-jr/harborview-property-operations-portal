def _register_and_login(client, username: str, password: str, role: str):
    register_response = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": password, "role": role},
    )
    assert register_response.status_code == 201
    user_id = register_response.json()["id"]

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_id, headers


def test_resident_can_create_order_and_manager_can_update_status(client):
    _, resident_headers = _register_and_login(
        client,
        username="api_orders_resident",
        password="resident-pass-123",
        role="resident",
    )
    _, manager_headers = _register_and_login(
        client,
        username="api_orders_manager",
        password="manager-pass-123",
        role="manager",
    )
    dispatcher_id, _ = _register_and_login(
        client,
        username="api_orders_dispatcher",
        password="dispatcher-pass-123",
        role="dispatcher",
    )

    create_response = client.post(
        "/api/v1/orders",
        json={"title": "HVAC not cooling", "description": "Apartment HVAC runs but does not cool."},
        headers=resident_headers,
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    update_response = client.patch(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "in_progress", "assigned_to_user_id": dispatcher_id},
        headers=manager_headers,
    )
    assert update_response.status_code == 200
    updated_order = update_response.json()
    assert updated_order["status"] == "in_progress"
    assert updated_order["assigned_to_user_id"] == dispatcher_id


def test_non_resident_cannot_create_order(client):
    _, manager_headers = _register_and_login(
        client,
        username="api_orders_manager_blocked",
        password="manager-pass-123",
        role="manager",
    )

    create_response = client.post(
        "/api/v1/orders",
        json={"title": "Should fail", "description": "Managers cannot create resident service orders."},
        headers=manager_headers,
    )
    assert create_response.status_code == 403
    assert create_response.json()["detail"] == "Only residents can create service orders"
