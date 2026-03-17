"""条目相关接口。"""

from fastapi import APIRouter

from app.schemas.item import ItemCreateRequest, ItemListResponse, ItemResponse, ItemUpdateRequest
from app.services.item_service import ItemService

router = APIRouter()


@router.get("", response_model=ItemListResponse, summary="List items")
def list_items() -> ItemListResponse:
    return ItemService().list_items()


@router.post("", response_model=ItemResponse, summary="Create item")
def create_item(payload: ItemCreateRequest) -> ItemResponse:
    return ItemService().create_item(payload)


@router.get("/{item_id}", response_model=ItemResponse, summary="Get item detail")
def get_item(item_id: int) -> ItemResponse:
    return ItemService().get_item(item_id)


@router.patch("/{item_id}", response_model=ItemResponse, summary="Update item")
def update_item(item_id: int, payload: ItemUpdateRequest) -> ItemResponse:
    return ItemService().update_item(item_id, payload)


@router.delete("/{item_id}", summary="Delete item")
def delete_item(item_id: int) -> dict[str, str]:
    ItemService().delete_item(item_id)
    return {"message": f"Item {item_id} delete placeholder"}
