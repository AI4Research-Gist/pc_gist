"""认证接口测试。"""

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
    db.add(User(username="demo_user", email="demo@example.com", password="secret123"))
    db.commit()
    db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=engine)


def test_login_me_change_password_logout_flow(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "demo_user", "password": "secret123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "demo_user"

    change_password_response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "secret123", "new_password": "newpass123"},
        headers=headers,
    )
    assert change_password_response.status_code == 200
    assert change_password_response.json()["message"] == "Password updated successfully"

    logout_response = client.post("/api/v1/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "User 1 logged out successfully"

    old_password_login = client.post(
        "/api/v1/auth/login",
        json={"identifier": "demo_user", "password": "secret123"},
    )
    assert old_password_login.status_code == 401

    new_password_login = client.post(
        "/api/v1/auth/login",
        json={"identifier": "demo_user", "password": "newpass123"},
    )
    assert new_password_login.status_code == 200


def test_change_password_rejects_wrong_current_password(client: TestClient) -> None:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "demo_user", "password": "secret123"},
    )
    token = login_response.json()["access_token"]

    response = client.post(
        "/api/v1/auth/change-password",
        json={"current_password": "wrong", "new_password": "newpass123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect."
