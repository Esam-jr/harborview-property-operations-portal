import pytest
from datetime import date
from decimal import Decimal

from app.models.billing_record import BillingRecord
from app.models.enums import BillingStatus, UserRole
from app.services.user_service import UserService


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
    return user_id, {"Authorization": f"Bearer {token}"}


@pytest.mark.parametrize("staff_role", ["admin", "manager"])
def test_staff_can_create_billing_record_happy_path(client, staff_role):
    resident_id, _ = _register_and_login(
        client,
        username=f"billing_resident_{staff_role}",
        password="resident-pass-123",
        role="resident",
    )
    _, staff_headers = _register_and_login(
        client,
        username=f"billing_staff_{staff_role}",
        password="staff-pass-123",
        role=staff_role,
    )

    create_response = client.post(
        "/api/v1/billing",
        json={
            "resident_user_id": resident_id,
            "amount_due": "245.75",
            "due_date": "2026-04-15",
            "notes": "Monthly HOA charges",
        },
        headers=staff_headers,
    )

    assert create_response.status_code == 201
    payload = create_response.json()
    assert payload["resident_user_id"] == resident_id
    assert payload["amount_due"] == "245.75"
    assert payload["status"] == "pending"
    assert payload["reference_code"].startswith("BILL-")


def test_resident_can_upload_payment_proof_for_own_billing_record(client):
    resident_id, resident_headers = _register_and_login(
        client,
        username="billing_resident_proof",
        password="resident-pass-123",
        role="resident",
    )
    _, admin_headers = _register_and_login(
        client,
        username="billing_admin_proof",
        password="admin-pass-123",
        role="admin",
    )

    create_response = client.post(
        "/api/v1/billing",
        json={
            "resident_user_id": resident_id,
            "amount_due": "100.00",
            "due_date": "2026-04-20",
            "notes": "Testing payment proof flow",
        },
        headers=admin_headers,
    )
    assert create_response.status_code == 201
    billing_id = create_response.json()["id"]

    upload_response = client.post(
        f"/api/v1/billing/{billing_id}/upload-proof",
        data={
            "payment_method": "check",
            "amount": "100.00",
            "payment_date": "2026-03-28",
            "reference_number": "CHK-100",
        },
        files={"proof_file": ("proof.png", b"\x89PNG\r\n\x1a\nfake-image-content", "image/png")},
        headers=resident_headers,
    )

    assert upload_response.status_code == 200
    upload_payload = upload_response.json()
    assert upload_payload["billing_id"] == billing_id
    assert upload_payload["payment_method"] == "check"
    assert upload_payload["file_name"] == "proof.png"
    assert upload_payload["file_size_bytes"] > 0

    resident_records = client.get("/api/v1/billing", headers=resident_headers)
    assert resident_records.status_code == 200
    records = resident_records.json()
    assert len(records) == 1
    assert records[0]["id"] == billing_id
    assert records[0]["status"] == "paid"


def test_resident_cannot_download_statement_for_other_resident_record(client):
    resident_a_id, resident_a_headers = _register_and_login(
        client,
        username="billing_resident_a",
        password="resident-pass-123",
        role="resident",
    )
    resident_b_id, _ = _register_and_login(
        client,
        username="billing_resident_b",
        password="resident-pass-123",
        role="resident",
    )
    _, manager_headers = _register_and_login(
        client,
        username="billing_manager_access",
        password="manager-pass-123",
        role="manager",
    )

    create_response = client.post(
        "/api/v1/billing",
        json={
            "resident_user_id": resident_b_id,
            "amount_due": "80.00",
            "due_date": "2026-05-01",
            "notes": "Access control test",
        },
        headers=manager_headers,
    )
    assert create_response.status_code == 201
    billing_id = create_response.json()["id"]

    statement_response = client.get(
        f"/api/v1/billing/{billing_id}/statement",
        headers=resident_a_headers,
    )

    assert resident_a_id != resident_b_id
    assert statement_response.status_code == 403
    assert "another resident" in statement_response.json()["detail"].lower()


def test_upload_payment_proof_rejects_unsupported_file_type(client, db_session):
    resident = UserService.create_user(
        db_session,
        username="billing_invalid_file_resident",
        password="resident-pass-123",
        role=UserRole.resident,
    )
    billing_record = BillingRecord(
        resident_user_id=resident.id,
        reference_code="BILL-INVALID-FILE-001",
        amount_due=Decimal("50.00"),
        due_date=date(2026, 5, 1),
        status=BillingStatus.pending,
        notes="Unsupported file test",
    )
    db_session.add(billing_record)
    db_session.commit()
    db_session.refresh(billing_record)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": resident.username, "password": "resident-pass-123"},
    )
    assert login_response.status_code == 200
    resident_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    upload_response = client.post(
        f"/api/v1/billing/{billing_record.id}/upload-proof",
        data={
            "payment_method": "check",
            "amount": "50.00",
            "payment_date": "2026-03-28",
            "reference_number": "TXT-REF-01",
        },
        files={"proof_file": ("proof.txt", b"not-an-image", "text/plain")},
        headers=resident_headers,
    )

    assert upload_response.status_code in (400, 422)


def test_resident_cannot_fetch_another_residents_billing_statement(client, db_session):
    resident_a = UserService.create_user(
        db_session,
        username="billing_statement_resident_a",
        password="resident-pass-123",
        role=UserRole.resident,
    )
    resident_b = UserService.create_user(
        db_session,
        username="billing_statement_resident_b",
        password="resident-pass-123",
        role=UserRole.resident,
    )

    billing_record = BillingRecord(
        resident_user_id=resident_b.id,
        reference_code="BILL-CROSS-RESIDENT-001",
        amount_due=Decimal("75.00"),
        due_date=date(2026, 5, 2),
        status=BillingStatus.pending,
        notes="Cross resident access test",
    )
    db_session.add(billing_record)
    db_session.commit()
    db_session.refresh(billing_record)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": resident_a.username, "password": "resident-pass-123"},
    )
    assert login_response.status_code == 200
    resident_a_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    statement_response = client.get(
        f"/api/v1/billing/{billing_record.id}/statement",
        headers=resident_a_headers,
    )

    assert resident_a.id != resident_b.id
    assert statement_response.status_code == 403
