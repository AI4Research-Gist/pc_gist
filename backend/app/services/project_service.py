"""项目业务逻辑层。"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.models.user import User
from app.repositories.project_repository import ProjectRepository
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)


class ProjectService:
    def __init__(self, db: Session) -> None:
        """初始化项目服务并挂载项目仓储。"""
        self.db = db
        self.project_repository = ProjectRepository(db)

    def list_projects(
        self,
        *,
        current_user: User,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ProjectListResponse:
        """按分页和关键字条件返回当前用户的项目列表。"""
        projects, total = self.project_repository.list_projects(
            owner_id=current_user.Id,
            keyword=keyword,
            page=page,
            page_size=page_size,
        )
        return ProjectListResponse(
            list=[self._to_response(project, item_count=item_count) for project, item_count in projects],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_project(self, payload: ProjectCreateRequest, *, current_user: User) -> ProjectResponse:
        """创建新项目并返回标准项目响应。"""
        project = self.project_repository.create_project(
            name=payload.name,
            title=payload.title or payload.name,
            description=payload.description,
            owner_id=current_user.Id,
        )
        return self._to_response(project, item_count=0)

    def get_project(self, project_id: int, *, current_user: User) -> ProjectResponse:
        """获取指定项目详情及其条目统计。"""
        project = self._get_project_or_404(project_id, current_user=current_user)
        return self._to_response(
            project,
            item_count=self.project_repository.count_items(project_id, owner_id=current_user.Id),
        )

    def update_project(self, project_id: int, payload: ProjectUpdateRequest, *, current_user: User) -> ProjectResponse:
        """更新指定项目并返回包含条目数量的最新结果。"""
        project = self._get_project_or_404(project_id, current_user=current_user)
        updated_project = self.project_repository.update_project(
            project,
            name=payload.name,
            title=payload.title,
            description=payload.description,
        )
        return self._to_response(
            updated_project,
            item_count=self.project_repository.count_items(project_id, owner_id=current_user.Id),
        )

    def delete_project(self, project_id: int, *, current_user: User) -> None:
        """删除指定项目。"""
        project = self._get_project_or_404(project_id, current_user=current_user)
        self.project_repository.delete_project(project)

    def _get_project_or_404(self, project_id: int, *, current_user: User) -> Project:
        """查询项目，不存在时抛出 404。"""
        project = self.project_repository.get_by_id(project_id, owner_id=current_user.Id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )
        return project

    @staticmethod
    def _to_response(project: Project, *, item_count: int = 0) -> ProjectResponse:
        """把项目 ORM 对象转换成接口返回的响应模型。"""
        return ProjectResponse(
            id=project.Id,
            owner_id=project.ownerId or 0,
            item_count=item_count,
            name=project.name or project.Title or "",
            title=project.Title or project.name,
            description=project.description,
            is_deleted=False,
            created_at=project.CreatedAt,
            updated_at=getattr(project, "UpdatedAt", None),
        )
