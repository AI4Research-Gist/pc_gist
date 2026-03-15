from app.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
)


class ProjectService:
    def list_projects(self) -> ProjectListResponse:
        projects = [
            ProjectResponse(
                id=1,
                owner_id=1,
                name="默认项目",
                title="默认项目",
                description="项目模块骨架占位数据",
                is_deleted=False,
            )
        ]
        return ProjectListResponse(list=projects, total=len(projects))

    def create_project(self, payload: ProjectCreateRequest) -> ProjectResponse:
        return ProjectResponse(id=1, owner_id=1, is_deleted=False, **payload.model_dump())

    def get_project(self, project_id: int) -> ProjectResponse:
        return ProjectResponse(
            id=project_id,
            owner_id=1,
            name="默认项目",
            title="默认项目",
            description="项目详情占位数据",
            is_deleted=False,
        )

    def update_project(self, project_id: int, payload: ProjectUpdateRequest) -> ProjectResponse:
        base = self.get_project(project_id).model_dump()
        base.update(payload.model_dump(exclude_none=True))
        return ProjectResponse(**base)

    def delete_project(self, project_id: int) -> None:
        return None
