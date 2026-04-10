"""条目模块数据库访问层。"""

from typing import Any

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.models.item import Item
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository):
    def __init__(self, db: Session) -> None:
        """使用指定数据库会话初始化条目仓储。"""
        super().__init__(db)

    def list_items(
        self,
        *,
        owner_id: int,
        item_type: str | None = None,
        project_id: int | None = None,
        status: str | None = None,
        read_status: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Item], int]:
        """按过滤条件、分页和排序规则查询条目列表。"""
        filters = [Item.ownerId == owner_id]
        if item_type:
            filters.append(Item.type == item_type)
        if project_id is not None:
            filters.append(Item.project_id == project_id)
        if status:
            filters.append(Item.status == status)
        if read_status:
            filters.append(Item.read_status == read_status)
        if keyword:
            pattern = f"%{keyword.strip()}%"
            filters.append(
                or_(
                    Item.title.ilike(pattern),
                    Item.summary.ilike(pattern),
                    Item.content_md.ilike(pattern),
                    Item.tags.ilike(pattern),
                )
            )

        statement = select(Item)
        count_statement = select(func.count()).select_from(Item)

        if filters:
            statement = statement.where(*filters)
            count_statement = count_statement.where(*filters)

        statement = statement.order_by(self._get_sort_clause(sort_by, sort_order))
        statement = statement.offset((page - 1) * page_size).limit(page_size)

        items = self.db.execute(statement).scalars().all()
        total = self.db.execute(count_statement).scalar_one()
        return list(items), total

    def get_by_id(self, item_id: int, *, owner_id: int) -> Item | None:
        """按条目主键和所属用户查询单条记录。"""
        statement = select(Item).where(
            Item.Id == item_id,
            Item.ownerId == owner_id,
        )
        return self.db.execute(statement).scalar_one_or_none()

    def create_item(
        self,
        *,
        item_type: str,
        title: str,
        summary: str | None = None,
        content_md: str | None = None,
        origin_url: str | None = None,
        audio_url: str | None = None,
        status: str = "processing",
        read_status: str = "unread",
        tags: str | None = None,
        project_id: int | None = None,
        meta_json: dict[str, Any] | None = None,
        owner_id: int | None = None,
    ) -> Item:
        """创建条目并返回数据库刷新后的对象。"""
        item = Item(
            type=item_type,
            title=title,
            summary=summary,
            content_md=content_md,
            origin_url=origin_url,
            audio_url=audio_url,
            status=status,
            read_status=read_status,
            tags=tags,
            project_id=project_id,
            meta_json=meta_json,
            ownerId=owner_id,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_item(self, item: Item, **updates: Any) -> Item:
        """按允许更新的字段集合批量修改条目。"""
        field_mapping = {
            "type": "type",
            "title": "title",
            "summary": "summary",
            "content_md": "content_md",
            "origin_url": "origin_url",
            "audio_url": "audio_url",
            "status": "status",
            "read_status": "read_status",
            "tags": "tags",
            "project_id": "project_id",
            "meta_json": "meta_json",
        }

        for field_name, value in updates.items():
            if field_name in field_mapping:
                setattr(item, field_mapping[field_name], value)

        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_item(self, item: Item) -> None:
        """删除指定条目记录。"""
        self.db.delete(item)
        self.db.commit()

    @staticmethod
    def _get_sort_clause(sort_by: str, sort_order: str):
        """把排序字段和方向转换成 SQLAlchemy 排序表达式。"""
        sort_mapping = {
            "created_at": Item.CreatedAt,
            "updated_at": Item.UpdatedAt,
            "title": Item.title,
            "status": Item.status,
        }
        column = sort_mapping.get(sort_by, Item.CreatedAt)
        return asc(column) if sort_order == "asc" else desc(column)
