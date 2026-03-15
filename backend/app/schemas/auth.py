from pydantic import BaseModel, EmailStr

from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    phone: str | None = None
    password: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
