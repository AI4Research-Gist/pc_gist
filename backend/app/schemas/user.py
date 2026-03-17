"""用户模块请求与响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """用户接口通用字段。"""

    username: str
    email: EmailStr | None = None
    phone: str | None = None
    avatar_url: str | None = None
    biometric_enabled: bool = False


class UserResponse(UserBase):
    """用户信息响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserUpdateRequest(BaseModel):
    """更新用户资料时允许修改的字段。"""

    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    avatar_url: str | None = None
    biometric_enabled: bool | None = None
