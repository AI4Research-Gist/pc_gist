"""AI 任务接口测试。"""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.main import app
from app.models.user import User
from app.services.ai_task_processor import AITaskProcessor

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
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(User(username="demo_user", email="demo@example.com", password="secret123"))
    db.commit()
    db.close()

    monkeypatch.setattr(AITaskProcessor, "__init__", lambda self: None)
    monkeypatch.setattr(
        AITaskProcessor,
        "process",
        lambda self, task: {
            "item_type": "article",
            "title": "Mocked AI output",
            "summary": "这是模拟的 AI 摘要",
            "tags": ["mock", "ai"],
            "meta_json": {"summary_short": "模拟短摘要"},
            "content_md": "",
        },
    )

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


def test_create_and_get_ai_task(client: TestClient) -> None:
    headers = _login_headers(client)

    create_response = client.post(
        "/api/v1/ai-tasks",
        json={
            "task_type": "structure-text",
            "input_type": "text",
            "input_payload": {
                "text": "这是一个关于科研工具的文章摘要。",
                "target_type": "article",
            },
        },
        headers=headers,
    )
    assert create_response.status_code == 200
    assert create_response.json()["status"] == "pending"

    task_id = create_response.json()["id"]
    detail_response = client.get(f"/api/v1/ai-tasks/{task_id}", headers=headers)
    assert detail_response.status_code == 200
    payload = detail_response.json()
    assert payload["status"] == "done"
    assert payload["owner_id"] == 1
    assert payload["output_payload"]["title"] == "Mocked AI output"
    assert payload["output_payload"]["meta_json"]["summary_short"] == "模拟短摘要"


def test_create_ai_task_rejects_invalid_task_type(client: TestClient) -> None:
    headers = _login_headers(client)

    response = client.post(
        "/api/v1/ai-tasks",
        json={
            "task_type": "unknown-task",
            "input_type": "text",
            "input_payload": {"text": "hello"},
        },
        headers=headers,
    )
    assert response.status_code == 400
    assert "Unsupported task_type" in response.json()["detail"]
