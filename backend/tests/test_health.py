"""最小健康检查测试。"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check() -> None:
    # 用最基础的接口确认应用能正常启动并返回预期响应。
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
