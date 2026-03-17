"""健康检查接口。"""

from fastapi import APIRouter

from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
