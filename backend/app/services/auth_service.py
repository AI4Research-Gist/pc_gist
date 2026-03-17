"""认证业务逻辑层。"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.user import UserResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.user_repository = UserRepository(db)

    def register(self, payload: RegisterRequest) -> LoginResponse:
        # 先做参数校验，再做唯一性校验，最后才写数据库。
        self._validate_register_payload(payload)
        self._ensure_user_not_exists(payload)

        user = self.user_repository.create_user(
            username=payload.username,
            email=str(payload.email),
            password=payload.password,
            phone=payload.phone,
            avatar_url=None,
            biometric_enabled=False,
        )
        token = create_access_token(str(user.Id))
        return LoginResponse(user=self._to_user_response(user), access_token=token)

    def login(self, payload: LoginRequest) -> LoginResponse:
        # 登录沿用原项目约定，支持用户名/邮箱/手机号三种标识。
        self._validate_login_payload(payload)

        user = self.user_repository.get_by_identifier(payload.identifier.strip())
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username, email, or phone number.",
            )

        # 当前仍按原数据库方式使用明文密码，后续如升级安全策略可切到哈希校验。
        if user.password != payload.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password.",
            )

        token = create_access_token(str(user.Id))
        return LoginResponse(user=self._to_user_response(user), access_token=token)

    def _ensure_user_not_exists(self, payload: RegisterRequest) -> None:
        # 显式做唯一性判断，可以给前端返回更明确的冲突信息。
        if self.user_repository.get_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists.",
            )

        if self.user_repository.get_by_email(str(payload.email)):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists.",
            )

        if payload.phone and self.user_repository.get_by_phone(payload.phone):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already exists.",
            )

    def _validate_register_payload(self, payload: RegisterRequest) -> None:
        if len(payload.username.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters long.",
            )

        if len(payload.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long.",
            )

    def _validate_login_payload(self, payload: LoginRequest) -> None:
        if not payload.identifier.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Identifier cannot be empty.",
            )

        if not payload.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password cannot be empty.",
            )

    @staticmethod
    def _to_user_response(user: User) -> UserResponse:
        # 把 ORM 字段转换成接口层约定的响应结构。
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
