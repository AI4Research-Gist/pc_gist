"""认证模块请求与响应模型。"""

from pydantic import AliasChoices, BaseModel, EmailStr, Field

from app.schemas.user import UserResponse


class RegisterRequest(BaseModel):
    """注册请求体。"""

    username: str
    email: EmailStr
    phone: str | None = Field(default=None, validation_alias=AliasChoices("phone", "Phonenumber"))
    password: str


class LoginRequest(BaseModel):
    """登录请求体。"""

    identifier: str
    password: str


class LoginResponse(BaseModel):
    """登录/注册成功后的统一返回结构。"""

    user: UserResponse
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    """修改密码请求体。"""

    current_password: str
    new_password: str


class MessageResponse(BaseModel):
    """简单消息响应。"""

    message: str
