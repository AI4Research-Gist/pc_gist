"""用户接口测试。"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base_class import Base
from app.main import app
from app.models.user import User

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def override_get_db() -> Generator:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(
        User(
            username="demo_user",
            email="demo@example.com",
            password="secret123",
            Phonenumber="13800000000",
        )
    )
    db.add(
        User(
            username="another_user",
            email="another@example.com",
            password="secret456",
            Phonenumber="13900000000",
        )
    )
    db.commit()
    db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=engine)


def _login_headers(client: TestClient) -> dict[str, str]:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "demo_user", "password": "secret123"},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_and_update_current_user_profile(client: TestClient) -> None:
    headers = _login_headers(client)

    me_response = client.get("/api/v1/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "demo_user"

    update_response = client.patch(
        "/api/v1/users/me",
        json={
            "username": "demo_user_updated",
            "email": "updated@example.com",
            "phone": "13700000000",
            "avatar_url": "https://example.com/avatar.png",
            "biometric_enabled": True,
        },
        headers=headers,
    )
    assert update_response.status_code == 200

    updated_user = update_response.json()
    assert updated_user["username"] == "demo_user_updated"
    assert updated_user["email"] == "updated@example.com"
    assert updated_user["phone"] == "13700000000"
    assert updated_user["avatar_url"] == "https://example.com/avatar.png"
    assert updated_user["biometric_enabled"] is True


def test_check_username_availability(client: TestClient) -> None:
    available_response = client.get("/api/v1/users/check-username", params={"username": "brand_new"})
    assert available_response.status_code == 200
    assert available_response.json()["available"] is True

    taken_response = client.get("/api/v1/users/check-username", params={"username": "demo_user"})
    assert taken_response.status_code == 200
    assert taken_response.json()["available"] is False


def test_update_current_user_rejects_duplicate_username(client: TestClient) -> None:
    headers = _login_headers(client)

    response = client.patch(
        "/api/v1/users/me",
        json={"username": "another_user"},
        headers=headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists."
