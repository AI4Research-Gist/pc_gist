from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    type: str
    title: str
    summary: str | None = None
    content_md: str | None = None
    origin_url: str | None = None
    audio_url: str | None = None
    status: str = "processing"
    read_status: str = "unread"
    is_starred: bool = False
    tags: str | None = None
    project_id: int | None = None
    meta_json: dict[str, Any] | None = None


class ItemCreateRequest(ItemBase):
    pass


class ItemUpdateRequest(BaseModel):
    type: str | None = None
    title: str | None = None
    summary: str | None = None
    content_md: str | None = None
    origin_url: str | None = None
    audio_url: str | None = None
    status: str | None = None
    read_status: str | None = None
    is_starred: bool | None = None
    tags: str | None = None
    project_id: int | None = None
    meta_json: dict[str, Any] | None = None


class ItemResponse(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ItemListResponse(BaseModel):
    list: list[ItemResponse]
    total: int
    page: int = 1
    page_size: int = 20
