"""仓储层基础类。"""

from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session | None = None) -> None:
        self.db = db
