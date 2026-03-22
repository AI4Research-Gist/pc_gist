"""条目相关接口。"""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.item import ItemCreateRequest, ItemListResponse, ItemResponse, ItemUpdateRequest
from app.services.item_service import ItemService

router = APIRouter()


@router.get("", response_model=ItemListResponse, summary="List items")
def list_items(
    db: Annotated[Session, Depends(get_db)],
    item_type: str | None = Query(default=None, alias="type"),
    project_id: int | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    read_status: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort_by: Literal["created_at", "updated_at", "title", "status"] = Query(default="created_at"),
    sort_order: Literal["asc", "desc"] = Query(default="desc"),
) -> ItemListResponse:
    """查询条目列表。

    这是 `items` 模块最核心的列表接口，支持按类型、项目、状态、阅读状态、
    关键字进行筛选，并支持分页和排序。接口层只负责接收查询参数，
    复杂的过滤和结果组装统一下沉到 `ItemService`。

    Args:
        db: 当前请求注入的数据库会话。
        item_type: 条目类型过滤条件，对应查询参数 `type`。
        project_id: 项目 ID 过滤条件。
        status_filter: 条目处理状态过滤条件，对应查询参数 `status`。
        read_status: 阅读状态过滤条件。
        keyword: 关键字搜索条件，可匹配标题、摘要、正文和标签。
        page: 当前页码，从 1 开始。
        page_size: 每页返回数量。
        sort_by: 排序字段。
        sort_order: 排序方向，支持升序和降序。

    Returns:
        ItemListResponse: 包含条目列表和分页信息的响应对象。
    """
    return ItemService(db).list_items(
        item_type=item_type,
        project_id=project_id,
        status=status_filter,
        read_status=read_status,
        keyword=keyword,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.post(
    "",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create item",
)
def create_item(
    payload: ItemCreateRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ItemResponse:
    """创建一个新条目。

    接口会接收条目的基础字段和 `meta_json` 结构化数据，并交由服务层完成：
    项目存在性校验、`meta_json` 规范化处理、数据库写入和响应转换。

    Args:
        payload: 条目创建请求体。
        db: 当前请求注入的数据库会话。

    Returns:
        ItemResponse: 新建条目的完整详情。
    """
    return ItemService(db).create_item(payload)


@router.get("/{item_id}", response_model=ItemResponse, summary="Get item detail")
def get_item(
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> ItemResponse:
    """获取单个条目的详情。

    该接口通常用于详情页加载。若条目不存在，服务层会统一抛出 404。

    Args:
        item_id: 条目主键 ID。
        db: 当前请求注入的数据库会话。

    Returns:
        ItemResponse: 对应条目的完整详情。
    """
    return ItemService(db).get_item(item_id)


@router.patch("/{item_id}", response_model=ItemResponse, summary="Update item")
def update_item(
    item_id: int,
    payload: ItemUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ItemResponse:
    """更新指定条目。

    支持部分字段更新，也兼容前端近全量 PATCH 的调用方式。服务层会负责校验
    新的 `project_id` 是否存在，并把 `meta_json` 统一解析为对象后再入库。

    Args:
        item_id: 需要更新的条目 ID。
        payload: 条目更新请求体。
        db: 当前请求注入的数据库会话。

    Returns:
        ItemResponse: 更新后的条目详情。
    """
    return ItemService(db).update_item(item_id, payload)


@router.delete("/{item_id}", summary="Delete item")
def delete_item(
    item_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, str]:
    """删除指定条目。

    该接口负责触发条目的删除逻辑。当前实现为直接删除数据库记录，
    后续如果项目切换为软删除，也可以继续保留相同的接口形态。

    Args:
        item_id: 需要删除的条目 ID。
        db: 当前请求注入的数据库会话。

    Returns:
        dict[str, str]: 删除成功后的确认消息。
    """
    ItemService(db).delete_item(item_id)
    return {"message": f"Item {item_id} deleted successfully"}
