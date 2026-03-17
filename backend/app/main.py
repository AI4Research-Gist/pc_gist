"""FastAPI 应用入口文件。"""

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging


def create_application() -> FastAPI:
    # 应用启动前先初始化日志配置，便于后续排查问题。
    configure_logging()

    application = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    # 统一把业务接口挂载到版本化前缀下，例如 /api/v1。
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()
