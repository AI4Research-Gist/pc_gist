"""AI 任务相关接口。"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.ai_task import (
    AITaskCreateRequest,
    AITaskResponse,
    AITaskStatusResponse,
)
from app.services.ai_task_service import AITaskService

router = APIRouter()


@router.post("", response_model=AITaskResponse, summary="Create AI task")
def create_ai_task(
    payload: AITaskCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> AITaskResponse:
    """创建一个 AI 异步任务。

    当前这个接口主要用于为后续的链接解析、OCR、摘要生成、转写等异步能力
    预留统一入口。接口层只接收请求体，并把任务创建交给 `AITaskService`。

    Args:
        payload: AI 任务创建请求体。

    Returns:
        AITaskResponse: 新建任务的基础信息。
    """
    return AITaskService(db).create_task(payload, current_user, background_tasks)


@router.get("/{task_id}", response_model=AITaskStatusResponse, summary="Get AI task status")
def get_ai_task(
    task_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> AITaskStatusResponse:
    """查询指定 AI 任务的状态。

    前端可以通过这个接口轮询任务处理进度，例如等待解析完成、读取失败原因
    或获取输出结果。当前具体状态管理由 `AITaskService` 统一返回。

    Args:
        task_id: AI 任务主键 ID。

    Returns:
        AITaskStatusResponse: 任务当前状态及相关结果信息。
    """
    return AITaskService(db).get_task(task_id, current_user)
