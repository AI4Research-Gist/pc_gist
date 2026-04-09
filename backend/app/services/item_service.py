"""条目业务逻辑层。"""

import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.user import User
from app.repositories.item_repository import ItemRepository
from app.repositories.project_repository import ProjectRepository
from app.schemas.item import ItemCreateRequest, ItemListResponse, ItemResponse, ItemUpdateRequest


class ItemService:
    def __init__(self, db: Session) -> None:
        self.item_repository = ItemRepository(db)
        self.project_repository = ProjectRepository(db)

    def list_items(
        self,
        *,
        current_user: User,
        item_type: str | None = None,
        project_id: int | None = None,
        status: str | None = None,
        read_status: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> ItemListResponse:
        items, total = self.item_repository.list_items(
            owner_id=current_user.Id,
            item_type=item_type,
            project_id=project_id,
            status=status,
            read_status=read_status,
            keyword=keyword,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return ItemListResponse(
            list=[self._to_response(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def create_item(self, payload: ItemCreateRequest, *, current_user: User) -> ItemResponse:
        self._ensure_project_exists(payload.project_id, current_user=current_user)
        item = self.item_repository.create_item(
            item_type=payload.type,
            title=payload.title,
            summary=payload.summary,
            content_md=payload.content_md,
            origin_url=payload.origin_url,
            audio_url=payload.audio_url,
            status=payload.status,
            read_status=payload.read_status,
            tags=payload.tags,
            project_id=payload.project_id,
            meta_json=self._normalize_meta_json(payload.meta_json),
            owner_id=current_user.Id,
        )
        return self._to_response(item)

    def get_item(self, item_id: int, *, current_user: User) -> ItemResponse:
        item = self._get_item_or_404(item_id, current_user=current_user)
        return self._to_response(item)

    def update_item(self, item_id: int, payload: ItemUpdateRequest, *, current_user: User) -> ItemResponse:
        item = self._get_item_or_404(item_id, current_user=current_user)
        updates = payload.model_dump(exclude_unset=True)
        if "project_id" in updates:
            self._ensure_project_exists(updates["project_id"], current_user=current_user)
        if "meta_json" in updates:
            updates["meta_json"] = self._normalize_meta_json(updates["meta_json"])

        updated_item = self.item_repository.update_item(item, **updates)
        return self._to_response(updated_item)

    def delete_item(self, item_id: int, *, current_user: User) -> None:
        item = self._get_item_or_404(item_id, current_user=current_user)
        self.item_repository.delete_item(item)

    def _get_item_or_404(self, item_id: int, *, current_user: User) -> Item:
        item = self.item_repository.get_by_id(item_id, owner_id=current_user.Id)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {item_id} not found",
            )
        return item

    def _ensure_project_exists(self, project_id: int | None, *, current_user: User) -> None:
        if project_id is None:
            return
        project = self.project_repository.get_by_id(project_id, owner_id=current_user.Id)
        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )

    def _normalize_meta_json(self, value: dict[str, Any] | str | None) -> dict[str, Any] | None:
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="meta_json must be a valid JSON object or JSON string",
            ) from exc
        if not isinstance(parsed, dict):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="meta_json must be a JSON object",
            )
        return parsed

    @staticmethod
    def _to_response(item: Item) -> ItemResponse:
        return ItemResponse(
            id=item.Id,
            owner_id=item.ownerId or 0,
            type=item.type,
            title=item.title,
            summary=item.summary,
            content_md=item.content_md,
            origin_url=item.origin_url,
            audio_url=item.audio_url,
            status=item.status,
            read_status=item.read_status,
            tags=item.tags,
            project_id=item.project_id,
            meta_json=item.meta_json,
            created_at=item.CreatedAt,
            updated_at=item.UpdatedAt,
        )
