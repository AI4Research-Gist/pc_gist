"""AI 任务模块数据库访问层。"""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_task import AITask
from app.repositories.base import BaseRepository


class AITaskRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        """使用指定数据库会话初始化 AI 任务仓储。"""
        super().__init__(db)

    def create_task(
        self,
        *,
        item_id: int | None,
        owner_id: int,
        task_type: str,
        input_type: str,
        input_payload: dict,
    ) -> AITask:
        """创建一条新的 AI 任务记录并返回持久化结果。"""
        task = AITask(
            item_id=item_id,
            owner_id=owner_id,
            task_type=task_type,
            input_type=input_type,
            input_payload=input_payload,
            status="pending",
            output_payload=None,
            error_message=None,
            started_at=None,
            finished_at=None,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int, owner_id: int | None = None) -> AITask | None:
        """按任务 ID 查询任务，可选附带 owner_id 约束。"""
        statement = select(AITask).where(AITask.id == task_id)
        if owner_id is not None:
            statement = statement.where(AITask.owner_id == owner_id)
        return self.db.execute(statement).scalar_one_or_none()

    def mark_processing(self, task: AITask) -> AITask:
        """把任务状态更新为处理中并记录开始时间。"""
        task.status = "processing"
        task.error_message = None
        task.started_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_done(self, task: AITask, output_payload: dict) -> AITask:
        """把任务标记为完成并写入输出结果。"""
        task.status = "done"
        task.output_payload = output_payload
        task.error_message = None
        task.finished_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def mark_failed(self, task: AITask, error_message: str) -> AITask:
        """把任务标记为失败并记录错误原因。"""
        task.status = "failed"
        task.error_message = error_message
        task.finished_at = datetime.utcnow()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
