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
    """创建一个 AI 异步任务。

    当前这个接口主要用于为后续的链接解析、OCR、摘要生成、转写等异步能力
    预留统一入口。接口层只接收请求体，并把任务创建交给 `AITaskService`。

    Args:
        payload: AI 任务创建请求体。

    Returns:
        AITaskResponse: 新建任务的基础信息。
    """
    return AITaskService().create_task(payload)


@router.get("/{task_id}", response_model=AITaskStatusResponse, summary="Get AI task status")
def get_ai_task(task_id: int) -> AITaskStatusResponse:
    """查询指定 AI 任务的状态。

    前端可以通过这个接口轮询任务处理进度，例如等待解析完成、读取失败原因
    或获取输出结果。当前具体状态管理由 `AITaskService` 统一返回。

    Args:
        task_id: AI 任务主键 ID。

    Returns:
        AITaskStatusResponse: 任务当前状态及相关结果信息。
    """
    return AITaskService().get_task(task_id)
