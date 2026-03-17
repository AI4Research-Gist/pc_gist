"""项目相关接口。"""

from fastapi import APIRouter

from app.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)
from app.services.project_service import ProjectService

router = APIRouter()


@router.get("", response_model=ProjectListResponse, summary="List projects")
def list_projects() -> ProjectListResponse:
    return ProjectService().list_projects()


@router.post("", response_model=ProjectResponse, summary="Create project")
def create_project(payload: ProjectCreateRequest) -> ProjectResponse:
    return ProjectService().create_project(payload)


@router.get("/{project_id}", response_model=ProjectResponse, summary="Get project detail")
def get_project(project_id: int) -> ProjectResponse:
    return ProjectService().get_project(project_id)


@router.patch("/{project_id}", response_model=ProjectResponse, summary="Update project")
def update_project(project_id: int, payload: ProjectUpdateRequest) -> ProjectResponse:
    return ProjectService().update_project(project_id, payload)


@router.delete("/{project_id}", summary="Delete project")
def delete_project(project_id: int) -> dict[str, str]:
    ProjectService().delete_project(project_id)
    return {"message": f"Project {project_id} delete placeholder"}
