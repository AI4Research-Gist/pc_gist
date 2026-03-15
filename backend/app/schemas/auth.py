from pydantic import AliasChoices, BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    phone: str | None = Field(default=None, validation_alias=AliasChoices("phone", "Phonenumber"))
    password: str


class LoginRequest(BaseModel):
    identifier: str
    password: str


class LoginResponse(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
