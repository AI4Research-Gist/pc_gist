"""FastAPI 依赖项定义。"""

from collections.abc import Generator

from app.db.session import SessionLocal


def get_db() -> Generator:
    # 每次请求分配一个独立的数据库会话，请求结束后自动释放。
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
