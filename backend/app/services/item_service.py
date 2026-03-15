from app.schemas.item import ItemCreateRequest, ItemListResponse, ItemResponse, ItemUpdateRequest


class ItemService:
    def list_items(self) -> ItemListResponse:
        items = [
            ItemResponse(
                id=1,
                owner_id=1,
                type="paper",
                title="示例条目",
                summary="条目模块骨架占位数据",
                content_md="# 示例条目",
                origin_url="https://example.com",
                audio_url=None,
                status="processing",
                read_status="unread",
                is_starred=False,
                tags="demo",
                project_id=1,
                meta_json={"source": "scaffold"},
            )
        ]
        return ItemListResponse(list=items, total=len(items))

    def create_item(self, payload: ItemCreateRequest) -> ItemResponse:
        return ItemResponse(id=1, owner_id=1, **payload.model_dump())

    def get_item(self, item_id: int) -> ItemResponse:
        return ItemResponse(
            id=item_id,
            owner_id=1,
            type="paper",
            title="示例条目",
            summary="条目详情占位数据",
            content_md="# 示例条目",
            origin_url="https://example.com",
            audio_url=None,
            status="processing",
            read_status="unread",
            is_starred=False,
            tags="demo",
            project_id=1,
            meta_json={"source": "scaffold"},
        )

    def update_item(self, item_id: int, payload: ItemUpdateRequest) -> ItemResponse:
        base = self.get_item(item_id).model_dump()
        base.update(payload.model_dump(exclude_none=True))
        return ItemResponse(**base)

    def delete_item(self, item_id: int) -> None:
        return None
