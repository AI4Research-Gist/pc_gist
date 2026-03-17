"""项目总路由入口。"""

from fastapi import APIRouter

from app.api.v1.api import api_v1_router

api_router = APIRouter()
# 当前只接入 v1 版本接口，后续扩展 v2 时可以平行增加。
api_router.include_router(api_v1_router)
