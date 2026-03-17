"""通用响应结构定义。"""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
