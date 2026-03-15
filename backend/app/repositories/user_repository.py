from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(User.Id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_phone(self, phone: str) -> User | None:
        statement = select(User).where(User.Phonenumber == phone)
        return self.db.execute(statement).scalar_one_or_none()

    def get_by_identifier(self, identifier: str) -> User | None:
        statement = select(User).where(
            or_(
                User.username == identifier,
                User.email == identifier,
                User.Phonenumber == identifier,
            )
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_user(
        self,
        *,
        username: str,
        email: str,
        password: str,
        phone: str | None = None,
        avatar_url: str | None = None,
        biometric_enabled: bool | None = False,
    ) -> User:
        user = User(
            username=username,
            email=email,
            password=password,
            Phonenumber=phone,
            avatar_url=avatar_url,
            biometric_enabled=biometric_enabled,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
