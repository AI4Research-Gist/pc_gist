"""条目接口测试。"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base_class import Base
from app.main import app
from app.models.project import Project
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
    db.add(User(username="demo_user", email="demo@example.com", password="secret"))
    db.commit()
    db.add(Project(name="默认项目", Title="默认项目", ownerId=1))
    db.commit()
    db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

    Base.metadata.drop_all(bind=engine)


def _login_headers(client: TestClient, *, identifier: str = "demo_user", password: str = "secret") -> dict[str, str]:
    login_response = client.post(
        "/api/v1/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_item_crud_flow(client: TestClient) -> None:
    headers = _login_headers(client)
    create_response = client.post(
        "/api/v1/items",
        json={
            "type": "paper",
            "title": "Transformer",
            "summary": "attention is all you need",
            "content_md": "# Transformer",
            "origin_url": "https://arxiv.org/abs/1706.03762",
            "status": "processing",
            "read_status": "unread",
            "tags": "llm,nlp",
            "project_id": 1,
            "meta_json": {"identifier": "1706.03762", "year": "2017"},
        },
        headers=headers,
    )
    assert create_response.status_code == 201

    created_item = create_response.json()
    item_id = created_item["id"]
    assert created_item["title"] == "Transformer"
    assert created_item["owner_id"] == 1
    assert created_item["meta_json"]["identifier"] == "1706.03762"

    list_response = client.get(
        "/api/v1/items",
        params={
            "type": "paper",
            "project_id": 1,
            "read_status": "unread",
            "keyword": "Transformer",
            "page": 1,
            "page_size": 10,
            "sort_by": "title",
            "sort_order": "asc",
        },
        headers=headers,
    )
    assert list_response.status_code == 200

    listed_items = list_response.json()
    assert listed_items["total"] == 1
    assert listed_items["page"] == 1
    assert listed_items["page_size"] == 10
    assert listed_items["list"][0]["id"] == item_id

    detail_response = client.get(f"/api/v1/items/{item_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["content_md"] == "# Transformer"

    update_response = client.patch(
        f"/api/v1/items/{item_id}",
        json={
            "status": "done",
            "read_status": "read",
            "meta_json": "{\"identifier\": \"1706.03762\", \"year\": \"2017\", \"conference\": \"NeurIPS\"}",
        },
        headers=headers,
    )
    assert update_response.status_code == 200

    updated_item = update_response.json()
    assert updated_item["status"] == "done"
    assert updated_item["read_status"] == "read"
    assert updated_item["meta_json"]["conference"] == "NeurIPS"

    delete_response = client.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Item {item_id} deleted successfully"

    deleted_detail_response = client.get(f"/api/v1/items/{item_id}", headers=headers)
    assert deleted_detail_response.status_code == 404
    assert deleted_detail_response.json()["detail"] == f"Item {item_id} not found"


def test_create_item_with_invalid_project_returns_404(client: TestClient) -> None:
    headers = _login_headers(client)
    response = client.post(
        "/api/v1/items",
        json={
            "type": "paper",
            "title": "Bad Project",
            "status": "processing",
            "read_status": "unread",
            "project_id": 999,
        },
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project 999 not found"


def test_update_item_with_invalid_meta_json_returns_422(client: TestClient) -> None:
    headers = _login_headers(client)
    create_response = client.post(
        "/api/v1/items",
        json={
            "type": "paper",
            "title": "Meta Test",
            "status": "processing",
            "read_status": "unread",
        },
        headers=headers,
    )
    item_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/items/{item_id}",
        json={"meta_json": "{invalid json}"},
        headers=headers,
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "meta_json must be a valid JSON object or JSON string"


def test_items_are_isolated_by_current_user(client: TestClient) -> None:
    db = TestingSessionLocal()
    db.add(User(username="other_user", email="other@example.com", password="secret"))
    db.commit()
    db.close()

    demo_headers = _login_headers(client, identifier="demo_user", password="secret")
    other_headers = _login_headers(client, identifier="other_user", password="secret")

    create_response = client.post(
        "/api/v1/items",
        json={
            "type": "paper",
            "title": "Private Item",
            "status": "processing",
            "read_status": "unread",
            "project_id": 1,
        },
        headers=demo_headers,
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    other_list = client.get("/api/v1/items", headers=other_headers)
    assert other_list.status_code == 200
    assert other_list.json()["total"] == 0

    other_detail = client.get(f"/api/v1/items/{item_id}", headers=other_headers)
    assert other_detail.status_code == 404
