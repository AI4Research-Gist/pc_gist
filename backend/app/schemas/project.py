"""项目模块请求与响应模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
    """项目通用字段。"""

    name: str
    title: str | None = None
    description: str | None = None


class ProjectCreateRequest(ProjectBase):
    pass


class ProjectUpdateRequest(BaseModel):
    name: str | None = None
    title: str | None = None
    description: str | None = None


class ProjectResponse(ProjectBase):
    """项目详情响应模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int = 0
    item_count: int = 0
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProjectListResponse(BaseModel):
    """项目列表响应模型。"""

    list: list[ProjectResponse]
    total: int
    page: int = 1
    page_size: int = 20
