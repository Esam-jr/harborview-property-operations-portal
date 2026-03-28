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


def test_resident_to_manager_chained_order_flow(client):
    resident_id, resident_headers = _register_and_login(
        client,
        username="chain_resident",
        password="resident-pass-123",
        role="resident",
    )
    _, manager_headers = _register_and_login(
        client,
        username="chain_manager",
        password="manager-pass-123",
        role="manager",
    )
    dispatcher_id, _ = _register_and_login(
        client,
        username="chain_dispatcher",
        password="dispatcher-pass-123",
        role="dispatcher",
    )

    created = client.post(
        "/api/v1/orders",
        json={"title": "Water leak", "description": "There is a leak under the kitchen sink."},
        headers=resident_headers,
    )
    assert created.status_code == 201
    created_order = created.json()
    order_id = created_order["id"]
    assert created_order["resident_user_id"] == resident_id
    assert created_order["status"] == "pending"
    assert len(created_order["status_history"]) == 1

    updated = client.put(
        f"/api/v1/orders/{order_id}/status",
        json={
            "status": "in_progress",
            "assigned_to_user_id": dispatcher_id,
            "note": "Assigned and work started",
        },
        headers=manager_headers,
    )
    assert updated.status_code == 200
    updated_order = updated.json()
    assert updated_order["status"] == "in_progress"
    assert updated_order["assigned_to_user_id"] == dispatcher_id
    assert len(updated_order["status_history"]) == 2
    assert updated_order["status_history"][-1]["status"] == "in_progress"
    assert updated_order["status_history"][-1]["note"] == "Assigned and work started"

    resident_fetch = client.get(f"/api/v1/orders/{order_id}", headers=resident_headers)
    assert resident_fetch.status_code == 200
    assert resident_fetch.json()["resident_user_id"] == resident_id


def test_resident_cannot_fetch_another_residents_order(client):
    _, resident_a_headers = _register_and_login(
        client,
        username="orders_resident_a",
        password="resident-pass-123",
        role="resident",
    )
    _, resident_b_headers = _register_and_login(
        client,
        username="orders_resident_b",
        password="resident-pass-123",
        role="resident",
    )

    create_response = client.post(
        "/api/v1/orders",
        json={"title": "B order", "description": "Owned by resident B."},
        headers=resident_b_headers,
    )
    assert create_response.status_code == 201
    order_id = create_response.json()["id"]

    fetch_response = client.get(f"/api/v1/orders/{order_id}", headers=resident_a_headers)
    assert fetch_response.status_code == 403
    assert "not allowed" in fetch_response.json()["detail"].lower()


def test_get_nonexistent_service_order_returns_404(client):
    _, resident_headers = _register_and_login(
        client,
        username="orders_resident_404",
        password="resident-pass-123",
        role="resident",
    )

    response = client.get("/api/v1/orders/999999", headers=resident_headers)
    assert response.status_code == 404
