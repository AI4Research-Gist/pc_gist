"""条目模块请求与响应模型。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """条目通用字段。"""

    type: str
    title: str
    summary: str | None = None
    content_md: str | None = None
    origin_url: str | None = None
    audio_url: str | None = None
    status: str = "processing"
    read_status: str = "unread"
    tags: str | None = None
    project_id: int | None = None
    meta_json: dict[str, Any] | str | None = None


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
    tags: str | None = None
    project_id: int | None = None
    meta_json: dict[str, Any] | str | None = None


class ItemResponse(ItemBase):
    """条目详情响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int = 0
    meta_json: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ItemListResponse(BaseModel):
    """条目列表响应模型。"""

    list: list[ItemResponse]
    total: int
    page: int = 1
    page_size: int = 20
