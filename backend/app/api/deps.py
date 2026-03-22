"""FastAPI 依赖项定义。"""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import JWTError, decode_access_token
from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db() -> Generator:
    """提供数据库会话依赖。

    这个函数会在每次请求进入接口层时创建一个独立的 SQLAlchemy Session，
    供 Repository / Service 在本次请求内复用。请求处理完成后，无论成功还是异常，
    都会在 finally 中关闭会话，避免连接泄漏。

    Returns:
        Generator: 产出一个数据库会话对象，供 FastAPI 依赖注入使用。
    """
    # 每次请求分配一个独立的数据库会话，请求结束后自动释放。
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """解析 Bearer Token 并返回当前登录用户。

    该依赖主要给需要鉴权的接口使用，例如 `auth/me`、`users/me`、
    修改密码、登出等。处理流程为：
    1. 从请求头中读取 Bearer Token。
    2. 解码 JWT，获取其中的 `sub` 用户主键。
    3. 根据用户主键到数据库查询真实用户。
    4. 如果 token 非法、过期、格式错误，或用户不存在，则统一返回 401。

    Args:
        db: 当前请求注入的数据库会话。
        token: 由 `OAuth2PasswordBearer` 自动提取的访问令牌。

    Returns:
        User: 当前 token 对应的用户 ORM 对象。

    Raises:
        HTTPException: 当 token 无效或用户不存在时抛出 401。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if subject is None:
            raise credentials_exception
        user_id = int(subject)
    except (JWTError, ValueError):
        raise credentials_exception

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user
