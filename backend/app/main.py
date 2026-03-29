"""FastAPI 应用入口文件。"""

import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 兼容从 backend/app 目录直接执行 python main.py 的场景。
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 统一把业务接口挂载到版本化前缀下，例如 /api/v1。
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_debug,
    )
