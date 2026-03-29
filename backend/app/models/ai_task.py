"""AI 异步任务表模型。"""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import NocoTimestampMixin


class AITask(NocoTimestampMixin, Base):
    __tablename__ = "item_ai_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[int | None] = mapped_column(Integer, index=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(32), nullable=False)
    input_type: Mapped[str] = mapped_column(String(32), nullable=False)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    output_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
