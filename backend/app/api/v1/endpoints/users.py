"""用户相关接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
def get_current_user_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> UserResponse:
    """获取当前登录用户的资料页信息。

    与 `auth/me` 相比，这个接口更偏向“用户中心”语义，后续适合继续扩展
    成资料管理入口，例如头像、手机号、偏好设置等。当前实现会基于 token
    识别当前用户，并从数据库返回标准化后的用户资料。

    Args:
        current_user: 由 token 解析得到的当前登录用户。
        db: 当前请求注入的数据库会话。

    Returns:
        UserResponse: 当前用户的资料信息。
    """
    return UserService(db).get_current_user(current_user)


@router.patch("/me", response_model=UserResponse, summary="Update current user profile")
def update_current_user_profile(
    payload: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> UserResponse:
    """更新当前登录用户的资料信息。

    支持局部更新用户名、邮箱、手机号、头像地址和生物识别开关等字段。
    具体的唯一性校验和数据库更新逻辑放在 `UserService` 中统一处理，
    接口层只负责接收请求、注入当前用户和返回最终结果。

    Args:
        payload: 用户资料更新请求体。
        current_user: 由 token 解析得到的当前登录用户。
        db: 当前请求注入的数据库会话。

    Returns:
        UserResponse: 更新后的用户资料。
    """
    return UserService(db).update_current_user(current_user, payload)


@router.get("/check-username", summary="Check username availability")
def check_username(
    username: str,
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    """检查某个用户名是否可用。

    该接口通常用于注册页或资料编辑页做实时校验。接口会对传入的用户名做
    基础非空检查，然后查询数据库中是否已存在相同用户名，最后返回布尔结果。

    Args:
        username: 需要校验的目标用户名。
        db: 当前请求注入的数据库会话。

    Returns:
        dict[str, bool]: 形如 `{"available": true}` 的可用性结果。
    """
    return {"available": UserService(db).is_username_available(username)}
