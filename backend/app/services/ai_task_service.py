"""AI 任务业务逻辑层。"""

from __future__ import annotations

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from app.models.ai_task import AITask
from app.models.user import User
from app.repositories.ai_task_repository import AITaskRepository
from app.schemas.ai_task import AITaskCreateRequest, AITaskResponse, AITaskStatusResponse
from app.services.ai_task_processor import AITaskProcessor

SUPPORTED_TASKS = {
    "parse-link": "url",
    "structure-text": "text",
    "parse-image": "image",
    "transcribe-audio": "audio",
}

TASK_ALIASES = {
    "parse_link": "parse-link",
    "link-parse": "parse-link",
    "text-structure": "structure-text",
    "parse-text": "structure-text",
    "parse_image": "parse-image",
    "ocr": "parse-image",
    "transcribe_audio": "transcribe-audio",
}


def process_ai_task_in_background(task_id: int, session_factory: sessionmaker) -> None:
    db = session_factory()
    repository = AITaskRepository(db)
    try:
        task = repository.get_by_id(task_id)
        if task is None:
            return

        repository.mark_processing(task)
        output_payload = AITaskProcessor().process(task)
        repository.mark_done(task, output_payload)
    except Exception as exc:
        task = repository.get_by_id(task_id)
        if task is not None:
            repository.mark_failed(task, str(exc))
    finally:
        db.close()


class AITaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AITaskRepository(db)

    def create_task(
        self,
        payload: AITaskCreateRequest,
        current_user: User,
        background_tasks: BackgroundTasks,
    ) -> AITaskResponse:
        normalized_task_type, normalized_input_type = self._validate_create_payload(payload)

        task = self.repository.create_task(
            item_id=payload.item_id,
            owner_id=current_user.Id,
            task_type=normalized_task_type,
            input_type=normalized_input_type,
            input_payload=payload.input_payload,
        )
        session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.db.get_bind(),
        )
        background_tasks.add_task(process_ai_task_in_background, task.id, session_factory)
        return self._to_task_response(task)

    def get_task(self, task_id: int, current_user: User) -> AITaskStatusResponse:
        task = self.repository.get_by_id(task_id, owner_id=current_user.Id)
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI task {task_id} not found",
            )
        return self._to_task_status_response(task)

    def _validate_create_payload(self, payload: AITaskCreateRequest) -> tuple[str, str]:
        normalized_task_type = TASK_ALIASES.get(payload.task_type, payload.task_type)
        expected_input_type = SUPPORTED_TASKS.get(normalized_task_type)
        if expected_input_type is None:
            supported = ", ".join(SUPPORTED_TASKS)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported task_type. Supported values: {supported}",
            )
        if payload.input_type != expected_input_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"task_type `{normalized_task_type}` requires input_type `{expected_input_type}`.",
            )
        if not payload.input_payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="input_payload cannot be empty.",
            )
        return normalized_task_type, expected_input_type

    @staticmethod
    def _to_task_response(task: AITask) -> AITaskResponse:
        return AITaskResponse(
            id=task.id,
            task_type=task.task_type,
            input_type=task.input_type,
            status=task.status,
            input_payload=task.input_payload,
        )

    @staticmethod
    def _to_task_status_response(task: AITask) -> AITaskStatusResponse:
        return AITaskStatusResponse(
            id=task.id,
            item_id=task.item_id,
            owner_id=task.owner_id,
            task_type=task.task_type,
            input_type=task.input_type,
            input_payload=task.input_payload,
            output_payload=task.output_payload,
            status=task.status,
            error_message=task.error_message,
            started_at=task.started_at,
            finished_at=task.finished_at,
            created_at=task.CreatedAt,
            updated_at=task.UpdatedAt,
        )

