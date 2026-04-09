"""项目相关接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("", response_model=ProjectListResponse, summary="List projects")
def list_projects(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ProjectListResponse:
    """查询项目列表。

    支持关键字搜索和基础分页，适合给项目管理页、下拉选择器或侧边栏项目列表使用。
    搜索、分页和数据组装都由 `ProjectService` 负责，接口层只负责把查询参数传入。

    Args:
        db: 当前请求注入的数据库会话。
        keyword: 项目搜索关键字，可匹配名称、标题或描述。
        page: 当前页码，从 1 开始。
        page_size: 每页返回数量。

    Returns:
        ProjectListResponse: 包含项目列表和分页信息的响应对象。
    """
    return ProjectService(db).list_projects(
        current_user=current_user,
        keyword=keyword,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
)
def create_project(
    payload: ProjectCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectResponse:
    """创建一个新项目。

    该接口接收项目的基础信息，并通过服务层完成数据落库和响应转换。
    当前实现会自动关联默认用户，后续如果接入完整鉴权，可以直接切换到
    当前登录用户作为项目归属人。

    Args:
        payload: 项目创建请求体。
        db: 当前请求注入的数据库会话。

    Returns:
        ProjectResponse: 新创建项目的完整信息。
    """
    return ProjectService(db).create_project(payload, current_user=current_user)


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project detail")
def get_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectResponse:
    """获取单个项目的详情。

    该接口根据项目主键查询数据库中的项目记录。如果项目不存在，
    由服务层统一抛出 404，接口层只负责接收路径参数并返回结果。

    Args:
        project_id: 项目主键 ID。
        db: 当前请求注入的数据库会话。

    Returns:
        ProjectResponse: 对应项目的详情信息。
    """
    return ProjectService(db).get_project(project_id, current_user=current_user)


@router.patch("/{project_id}", response_model=ProjectResponse, summary="Update project")
def update_project(
    project_id: int,
    payload: ProjectUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectResponse:
    """更新指定项目。

    支持对项目名称、标题和描述进行部分更新。接口层负责收集路径参数和请求体，
    实际的存在性校验、更新逻辑和响应组装交给服务层处理。

    Args:
        project_id: 需要更新的项目 ID。
        payload: 项目更新请求体，允许部分字段为空。
        db: 当前请求注入的数据库会话。

    Returns:
        ProjectResponse: 更新后的项目信息。
    """
    return ProjectService(db).update_project(project_id, payload, current_user=current_user)


@router.delete("/{project_id}", summary="Delete project")
def delete_project(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """删除指定项目。

    当前删除逻辑会先在服务层中校验项目是否存在，再由仓储层处理项目删除和
    关联条目的项目解绑，避免项目被删除后 `items.project_id` 悬空。

    Args:
        project_id: 需要删除的项目 ID。
        db: 当前请求注入的数据库会话。

    Returns:
        dict[str, str]: 删除成功后的确认消息。
    """
    ProjectService(db).delete_project(project_id, current_user=current_user)
    return {"message": f"Project {project_id} deleted successfully"}
