from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr | None = None
    phone: str | None = None
    avatar_url: str | None = None
    biometric_enabled: bool = False


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str = "active"
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserUpdateRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    avatar_url: str | None = None
    biometric_enabled: bool | None = None
