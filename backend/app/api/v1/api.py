from fastapi import APIRouter

from app.api.v1.endpoints import ai_tasks, auth, health, items, projects, users

api_v1_router = APIRouter()
api_v1_router.include_router(health.router, tags=["health"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(users.router, prefix="/users", tags=["users"])
api_v1_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_v1_router.include_router(items.router, prefix="/items", tags=["items"])
api_v1_router.include_router(ai_tasks.router, prefix="/ai-tasks", tags=["ai-tasks"])
