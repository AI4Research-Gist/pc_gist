"""用户业务逻辑层。"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdateRequest


class UserService:
    def __init__(self, db: Session) -> None:
        """初始化用户服务并挂载用户仓储。"""
        self.user_repository = UserRepository(db)

    def get_current_user(self, current_user: User) -> UserResponse:
        """返回当前登录用户的标准资料响应。"""
        return self._to_user_response(current_user)

    def update_current_user(self, current_user: User, payload: UserUpdateRequest) -> UserResponse:
        """更新当前登录用户资料并返回最新结果。"""
        self._validate_update_payload(current_user, payload)

        updated_user = self.user_repository.update_user(
            current_user,
            username=payload.username.strip() if payload.username is not None else None,
            email=str(payload.email) if payload.email is not None else None,
            phone=payload.phone,
            avatar_url=payload.avatar_url,
            biometric_enabled=payload.biometric_enabled,
        )
        return self._to_user_response(updated_user)

    def is_username_available(self, username: str) -> bool:
        """判断指定用户名在当前系统中是否可用。"""
        candidate = username.strip()
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username cannot be empty.",
            )
        return self.user_repository.get_by_username(candidate) is None

    def _validate_update_payload(self, current_user: User, payload: UserUpdateRequest) -> None:
        """校验用户资料更新请求的长度和唯一性约束。"""
        if payload.username is not None:
            username = payload.username.strip()
            if len(username) < 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username must be at least 3 characters long.",
                )
            existing_user = self.user_repository.get_by_username(username)
            if existing_user and existing_user.Id != current_user.Id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username already exists.",
                )

        if payload.email is not None:
            existing_user = self.user_repository.get_by_email(str(payload.email))
            if existing_user and existing_user.Id != current_user.Id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already exists.",
                )

        if payload.phone is not None:
            existing_user = self.user_repository.get_by_phone(payload.phone)
            if existing_user and existing_user.Id != current_user.Id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Phone number already exists.",
                )

    @staticmethod
    def _to_user_response(user: User) -> UserResponse:
        """把用户 ORM 对象转换成用户资料响应模型。"""
        return UserResponse(
            id=user.Id,
            username=user.username,
            email=user.email,
            phone=user.Phonenumber,
            avatar_url=user.avatar_url,
            biometric_enabled=bool(user.biometric_enabled) if user.biometric_enabled is not None else False,
            status="active",
            created_at=user.CreatedAt,
            updated_at=user.UpdatedAt,
        )
