from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AITaskCreateRequest(BaseModel):
    task_type: str
    input_type: str
    input_payload: dict[str, Any]
    item_id: int | None = None


class AITaskResponse(BaseModel):
    id: int
    task_type: str
    input_type: str
    status: str
    input_payload: dict[str, Any]


class AITaskStatusResponse(BaseModel):
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
    created_at: datetime | None = None
    updated_at: datetime | None = None
