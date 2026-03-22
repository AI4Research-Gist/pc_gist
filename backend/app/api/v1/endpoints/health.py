"""健康检查接口。"""

from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    """提供最小健康检查接口。

    该接口不依赖数据库、不依赖鉴权，主要用于确认服务进程是否正常启动、
    路由是否已挂载成功，以及网关或部署平台是否能正确访问应用。

    Returns:
        HealthResponse: 固定返回 `status="ok"` 的健康状态对象。
    """
    return HealthResponse(status="ok")
