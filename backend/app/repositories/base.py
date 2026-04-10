"""仓储层基础类。"""

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session | None = None) -> None:
        """保存当前仓储实例使用的数据库会话。"""
        self.db = db
