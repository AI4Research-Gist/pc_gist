"""items 表 ORM 模型。"""

from typing import Any

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import NocoTimestampMixin


class Item(NocoTimestampMixin, Base):
    __tablename__ = "items"

    Id: Mapped[int] = mapped_column("Id", Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    content_md: Mapped[str | None] = mapped_column(Text)
    origin_url: Mapped[str | None] = mapped_column(String(500))
    audio_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(32), default="processing", nullable=False)
    read_status: Mapped[str] = mapped_column(String(32), default="unread", nullable=False)
    tags: Mapped[str | None] = mapped_column(String(500))
    project_id: Mapped[int | None] = mapped_column("project_id", Integer, ForeignKey("projects.Id"), index=True)
    meta_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    ownerId: Mapped[int | None] = mapped_column("ownerId", Integer, ForeignKey("users.Id"), index=True)

    # 条目既可以直接归属于用户，也可以再进一步绑定到某个项目。
    owner = relationship("User", back_populates="items")
    project = relationship("Project", back_populates="items")
