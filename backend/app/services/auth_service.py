from app.core.security import create_access_token
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.schemas.user import UserResponse


class AuthService:
    def register(self, payload: RegisterRequest) -> LoginResponse:
        user = UserResponse(
            id=1,
            username=payload.username,
            email=payload.email,
            phone=payload.phone,
            avatar_url=None,
            biometric_enabled=False,
            status="active",
        )
        token = create_access_token(str(user.id))
        return LoginResponse(user=user, access_token=token)

    def login(self, payload: LoginRequest) -> LoginResponse:
        user = UserResponse(
            id=1,
            username=payload.identifier,
            email=None,
            phone=None,
            avatar_url=None,
            biometric_enabled=False,
            status="active",
        )
        token = create_access_token(str(user.id))
        return LoginResponse(user=user, access_token=token)
