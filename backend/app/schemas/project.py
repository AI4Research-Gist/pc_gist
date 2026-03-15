from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProjectBase(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int = 0
    is_deleted: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ProjectListResponse(BaseModel):
    list: list[ProjectResponse]
    total: int
    page: int = 1
    page_size: int = 20
