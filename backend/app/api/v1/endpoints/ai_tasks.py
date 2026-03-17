"""AI 任务相关接口。"""

from fastapi import APIRouter

from app.schemas.ai_task import (
    AITaskCreateRequest,
    AITaskResponse,
    AITaskStatusResponse,
)
from app.services.ai_task_service import AITaskService

router = APIRouter()


@router.post("", response_model=AITaskResponse, summary="Create AI task")
def create_ai_task(payload: AITaskCreateRequest) -> AITaskResponse:
    return AITaskService().create_task(payload)


@router.get("/{task_id}", response_model=AITaskStatusResponse, summary="Get AI task status")
def get_ai_task(task_id: int) -> AITaskStatusResponse:
    return AITaskService().get_task(task_id)
