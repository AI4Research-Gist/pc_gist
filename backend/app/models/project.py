from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import NocoCreatedAtMixin


class Project(NocoCreatedAtMixin, Base):
    __tablename__ = "projects"

    Id: Mapped[int] = mapped_column("Id", Integer, primary_key=True, autoincrement=True)
    Title: Mapped[str | None] = mapped_column("Title", String(128))
    name: Mapped[str | None] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(Text)
    ownerId: Mapped[int | None] = mapped_column("ownerId", Integer, ForeignKey("users.Id"), index=True)

    owner = relationship("User", back_populates="projects")
    items = relationship("Item", back_populates="project")
