"""项目接口测试。"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base_class import Base
from app.main import app
from app.models.item import Item
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


def test_project_crud_flow(client: TestClient) -> None:
    headers = _login_headers(client)
    create_response = client.post(
        "/api/v1/projects",
        json={"name": "AI 研究", "description": "项目描述"},
        headers=headers,
    )
    assert create_response.status_code == 201

    created_project = create_response.json()
    project_id = created_project["id"]
    assert created_project["name"] == "AI 研究"
    assert created_project["title"] == "AI 研究"
    assert created_project["owner_id"] == 1
    assert created_project["item_count"] == 0

    list_response = client.get(
        "/api/v1/projects",
        params={"keyword": "研究", "page": 1, "page_size": 10},
        headers=headers,
    )
    assert list_response.status_code == 200

    listed_projects = list_response.json()
    assert listed_projects["total"] == 1
    assert listed_projects["page"] == 1
    assert listed_projects["page_size"] == 10
    assert listed_projects["list"][0]["id"] == project_id
    assert listed_projects["list"][0]["item_count"] == 0

    detail_response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert detail_response.status_code == 200
    assert detail_response.json()["description"] == "项目描述"
    assert detail_response.json()["item_count"] == 0

    update_response = client.patch(
        f"/api/v1/projects/{project_id}",
        json={"title": "AI Weekly", "description": "更新后的描述"},
        headers=headers,
    )
    assert update_response.status_code == 200

    updated_project = update_response.json()
    assert updated_project["title"] == "AI Weekly"
    assert updated_project["description"] == "更新后的描述"

    db = TestingSessionLocal()
    db.add(
        Item(
            type="paper",
            title="测试条目",
            status="processing",
            read_status="unread",
            ownerId=1,
            project_id=project_id,
        )
    )
    db.commit()
    db.close()

    recount_response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert recount_response.status_code == 200
    assert recount_response.json()["item_count"] == 1

    delete_response = client.delete(f"/api/v1/projects/{project_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Project {project_id} deleted successfully"

    deleted_detail_response = client.get(f"/api/v1/projects/{project_id}", headers=headers)
    assert deleted_detail_response.status_code == 404
    assert deleted_detail_response.json()["detail"] == f"Project {project_id} not found"

    db = TestingSessionLocal()
    orphan_item = db.query(Item).filter(Item.title == "测试条目").one()
    assert orphan_item.project_id is None
    db.close()


def test_projects_are_isolated_by_current_user(client: TestClient) -> None:
    db = TestingSessionLocal()
    db.add(User(username="other_user", email="other@example.com", password="secret"))
    db.commit()
    db.close()

    demo_headers = _login_headers(client, identifier="demo_user", password="secret")
    other_headers = _login_headers(client, identifier="other_user", password="secret")

    demo_project = client.post(
        "/api/v1/projects",
        json={"name": "Demo 私有项目", "description": "demo owner"},
        headers=demo_headers,
    )
    assert demo_project.status_code == 201
    project_id = demo_project.json()["id"]

    other_list = client.get("/api/v1/projects", headers=other_headers)
    assert other_list.status_code == 200
    assert other_list.json()["total"] == 0

    other_detail = client.get(f"/api/v1/projects/{project_id}", headers=other_headers)
    assert other_detail.status_code == 404
