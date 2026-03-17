"""NocoDB 风格时间字段混入类。"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class NocoCreatedAtMixin:
    # 保持字段名为 CreatedAt，便于和原数据库结构完全对齐。
    CreatedAt: Mapped[datetime] = mapped_column(
        "CreatedAt",
        DateTime,
        server_default=func.now(),
        nullable=False,
    )


class NocoTimestampMixin(NocoCreatedAtMixin):
    # 同时保留 UpdatedAt 字段，适用于 users 和 items 表。
    UpdatedAt: Mapped[datetime] = mapped_column(
        "UpdatedAt",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
