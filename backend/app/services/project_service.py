"""项目业务逻辑层。"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)


class ProjectService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.user_repository = UserRepository(db)

    def list_projects(
        self,
        *,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ProjectListResponse:
        projects, total = self.project_repository.list_projects(
            keyword=keyword,
            page=page,
            page_size=page_size,
        )
        return ProjectListResponse(
            list=[self._to_response(project) for project in projects],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_project(self, payload: ProjectCreateRequest) -> ProjectResponse:
        owner_id = 1 if self.user_repository.get_by_id(1) else None
        project = self.project_repository.create_project(
            name=payload.name,
            title=payload.title or payload.name,
            description=payload.description,
            owner_id=owner_id,
        )
        return self._to_response(project)

    def get_project(self, project_id: int) -> ProjectResponse:
        project = self._get_project_or_404(project_id)
        return self._to_response(project)

    def update_project(self, project_id: int, payload: ProjectUpdateRequest) -> ProjectResponse:
        project = self._get_project_or_404(project_id)
        updated_project = self.project_repository.update_project(
            project,
            name=payload.name,
            title=payload.title,
            description=payload.description,
        )
        return self._to_response(updated_project)

    def delete_project(self, project_id: int) -> None:
        project = self._get_project_or_404(project_id)
        self.project_repository.delete_project(project)

    def _get_project_or_404(self, project_id: int) -> Project:
        project = self.project_repository.get_by_id(project_id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )
        return project

    @staticmethod
    def _to_response(project: Project) -> ProjectResponse:
        return ProjectResponse(
            id=project.Id,
            owner_id=project.ownerId or 0,
            name=project.name or project.Title or "",
            title=project.Title or project.name,
            description=project.description,
            is_deleted=False,
            created_at=project.CreatedAt,
            updated_at=getattr(project, "UpdatedAt", None),
        )
