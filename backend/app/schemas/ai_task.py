"""AI 任务模块请求与响应模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AITaskCreateRequest(BaseModel):
    """创建 AI 任务时的请求体。"""

    task_type: str
    input_type: str
    input_payload: dict[str, Any]
    item_id: int | None = None


class AITaskResponse(BaseModel):
    """创建 AI 任务后的简要响应。"""

    id: int
    task_type: str
    input_type: str
    status: str
    input_payload: dict[str, Any]


class AITaskStatusResponse(BaseModel):
    """AI 任务状态查询响应。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int | None = None
    owner_id: int = 0
    task_type: str
    input_type: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any] | None = None
    status: str
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
