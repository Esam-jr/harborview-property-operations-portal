from app.models.enums import UserRole
from app.services.user_service import UserService


def test_create_user_hashes_password_and_persists_role(db_session):
    user = UserService.create_user(
        db_session,
        username="unit_manager",
        password="manager-pass-123",
        role=UserRole.manager,
    )

    assert user.id is not None
    assert user.username == "unit_manager"
    assert user.role == UserRole.manager
    assert user.password != "manager-pass-123"


def test_authenticate_returns_user_for_valid_credentials(db_session):
    UserService.create_user(
        db_session,
        username="resident_one",
        password="resident-pass-123",
        role=UserRole.resident,
    )

    authenticated = UserService.authenticate(db_session, "resident_one", "resident-pass-123")
    assert authenticated is not None
    assert authenticated.username == "resident_one"


def test_authenticate_returns_none_for_invalid_password(db_session):
    UserService.create_user(
        db_session,
        username="resident_two",
        password="resident-pass-123",
        role=UserRole.resident,
    )

    authenticated = UserService.authenticate(db_session, "resident_two", "wrong-pass-123")
    assert authenticated is None
