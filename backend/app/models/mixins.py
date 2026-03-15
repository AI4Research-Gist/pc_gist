from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


class NocoCreatedAtMixin:
    CreatedAt: Mapped[datetime] = mapped_column(
        "CreatedAt",
        DateTime,
        server_default=func.now(),
        nullable=False,
    )


class NocoTimestampMixin(NocoCreatedAtMixin):
    UpdatedAt: Mapped[datetime] = mapped_column(
        "UpdatedAt",
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
