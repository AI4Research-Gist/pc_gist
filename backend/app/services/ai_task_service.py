"""AI 任务业务逻辑层占位实现。"""

from app.schemas.ai_task import AITaskCreateRequest, AITaskResponse, AITaskStatusResponse


class AITaskService:
    def create_task(self, payload: AITaskCreateRequest) -> AITaskResponse:
        return AITaskResponse(
            id=1,
            task_type=payload.task_type,
            input_type=payload.input_type,
            status="pending",
            input_payload=payload.input_payload,
        )

    def get_task(self, task_id: int) -> AITaskStatusResponse:
        return AITaskStatusResponse(
            id=task_id,
            item_id=None,
            owner_id=1,
            task_type="parse-link",
            input_type="url",
            input_payload={"url": "https://example.com"},
            output_payload=None,
            status="pending",
            error_message=None,
        )
