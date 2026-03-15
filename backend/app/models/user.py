from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.mixins import NocoTimestampMixin


class User(NocoTimestampMixin, Base):
    __tablename__ = "users"

    Id: Mapped[int] = mapped_column("Id", Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    Phonenumber: Mapped[str | None] = mapped_column("Phonenumber", String(32), unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(255))
    biometric_enabled: Mapped[bool | None] = mapped_column(Boolean)

    projects = relationship("Project", back_populates="owner")
    items = relationship("Item", back_populates="owner")
