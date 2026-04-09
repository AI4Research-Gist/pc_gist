"""项目模块数据库访问层。"""

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.project import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_projects(
        self,
        *,
        owner_id: int,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[tuple[Project, int]], int]:
        filters = [Project.ownerId == owner_id]
        if keyword:
            pattern = f"%{keyword.strip()}%"
            filters.append(
                or_(
                    Project.name.ilike(pattern),
                    Project.Title.ilike(pattern),
                    Project.description.ilike(pattern),
                )
            )

        statement = (
            select(Project, func.count(Item.Id).label("item_count"))
            .outerjoin(Item, Item.project_id == Project.Id)
            .group_by(Project.Id)
            .order_by(Project.Id.desc())
        )
        count_statement = select(func.count()).select_from(Project)

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        statement = statement.offset((page - 1) * page_size).limit(page_size)
        projects = [(project, item_count) for project, item_count in self.db.execute(statement).all()]
        total = self.db.execute(count_statement).scalar_one()
        return list(projects), total

    def count_items(self, project_id: int, *, owner_id: int) -> int:
        statement = select(func.count()).select_from(Item).where(
            Item.project_id == project_id,
            Item.ownerId == owner_id,
        )
        return self.db.execute(statement).scalar_one()

    def get_by_id(self, project_id: int, *, owner_id: int) -> Project | None:
        statement = select(Project).where(
            Project.Id == project_id,
            Project.ownerId == owner_id,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_project(
        self,
        *,
        name: str,
        title: str | None = None,
        description: str | None = None,
        owner_id: int | None = None,
    ) -> Project:
        project = Project(
            name=name,
            Title=title,
            description=description,
            ownerId=owner_id,
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update_project(
        self,
        project: Project,
        *,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> Project:
        if name is not None:
            project.name = name
        if title is not None:
            project.Title = title
        if description is not None:
            project.description = description

        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete_project(self, project: Project) -> None:
        # 删除项目之前先把条目转移到“未分组”状态，避免外键和业务归属混乱。
        self.db.execute(
            update(Item)
            .where(
                Item.project_id == project.Id,
                Item.ownerId == project.ownerId,
            )
            .values(project_id=None)
        )
        self.db.delete(project)
        self.db.commit()
