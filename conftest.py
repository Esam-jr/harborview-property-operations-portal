from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.enums import UserRole
from app.models.property_listing import PropertyListing
from app.models.property_listing_media import PropertyListingMedia
from app.models.service_order import ServiceOrder
from app.models.service_order_status_history import ServiceOrderStatusHistory
from app.models.user import User
from app.services.user_service import UserService

TEST_TABLES = [
    User.__table__,
    PropertyListing.__table__,
    PropertyListingMedia.__table__,
    ServiceOrder.__table__,
    ServiceOrderStatusHistory.__table__,
]


@pytest.fixture()
def test_engine(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(bind=engine, tables=TEST_TABLES)
    yield engine
    Base.metadata.drop_all(bind=engine, tables=TEST_TABLES)
    engine.dispose()


@pytest.fixture()
def session_factory(test_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def db_session(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    api_client = TestClient(app)
    try:
        yield api_client
    finally:
        app.dependency_overrides.clear()
        api_client.close()


@pytest.fixture()
def create_user(db_session):
    def _create_user(username: str, password: str, role: UserRole):
        return UserService.create_user(db_session, username=username, password=password, role=role)

    return _create_user


@pytest.fixture()
def register_user(client):
    def _register_user(username: str, password: str, role: str):
        return client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": password, "role": role},
        )

    return _register_user


@pytest.fixture()
def login_user(client):
    def _login_user(username: str, password: str):
        return client.post("/api/v1/auth/login", json={"username": username, "password": password})

    return _login_user


@pytest.fixture()
def auth_headers(register_user, login_user):
    def _auth_headers(username: str, password: str, role: str):
        register_response = register_user(username, password, role)
        assert register_response.status_code == 201

        login_response = login_user(username, password)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers
