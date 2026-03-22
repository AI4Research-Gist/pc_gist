"""认证相关接口。"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, LoginRequest, LoginResponse, MessageResponse, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=LoginResponse, summary="Register a user")
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """注册新用户并直接返回登录态。

    接口层负责接收注册请求体和数据库会话，然后把具体的参数校验、
    唯一性检查、用户创建和 token 签发交给 `AuthService` 处理。
    注册成功后会直接返回用户信息和访问令牌，前端无需额外再次调用登录接口。

    Args:
        payload: 注册请求体，包含用户名、邮箱、手机号和密码。
        db: 当前请求注入的数据库会话。

    Returns:
        LoginResponse: 注册成功后的用户信息与访问令牌。
    """
    # 注册逻辑统一放到 Service 层，接口层只负责接收请求和返回结果。
    return AuthService(db).register(payload)


@router.post("/login", response_model=LoginResponse, summary="Login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    """执行用户登录并返回访问令牌。

    当前支持使用用户名、邮箱或手机号作为登录标识。接口层不做业务判断，
    只负责把请求转发到 `AuthService`，由服务层完成身份校验和 token 生成。

    Args:
        payload: 登录请求体，包含登录标识和密码。
        db: 当前请求注入的数据库会话。

    Returns:
        LoginResponse: 登录成功后的用户信息与访问令牌。
    """
    # 登录支持用户名、邮箱、手机号三种标识。
    return AuthService(db).login(payload)


@router.post("/change-password", response_model=MessageResponse, summary="Change password")
def change_password(
    payload: ChangePasswordRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> MessageResponse:
    """修改当前登录用户的密码。

    该接口要求请求头携带 Bearer Token。接口层会先通过 `get_current_user`
    解析出当前登录用户，再把旧密码校验、新密码合法性校验和数据库更新
    交给 `AuthService` 处理。

    Args:
        payload: 修改密码请求体，包含旧密码与新密码。
        current_user: 由 token 解析得到的当前登录用户。
        db: 当前请求注入的数据库会话。

    Returns:
        MessageResponse: 修改成功后的消息提示。
    """
    result = AuthService(db).change_password(current_user, payload)
    return MessageResponse(**result)


@router.post("/logout", response_model=MessageResponse, summary="Logout")
def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> MessageResponse:
    """执行当前用户的登出动作。

    当前项目采用无状态 JWT，服务端不维护 token 会话表，因此这里的登出
    语义是“确认当前 token 合法并返回成功消息”，前端收到成功响应后应主动
    清理本地保存的 access_token。后续如果引入黑名单或刷新令牌机制，
    可以在 Service 层继续扩展。

    Args:
        current_user: 由 token 解析得到的当前登录用户。
        db: 当前请求注入的数据库会话。

    Returns:
        MessageResponse: 登出成功后的消息提示。
    """
    result = AuthService(db).logout(current_user)
    return MessageResponse(**result)


@router.get("/me", response_model=UserResponse, summary="Current user")
def me(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> UserResponse:
    """返回当前登录用户的信息。

    该接口通常用于前端启动后恢复登录态，或刷新页面时重新获取当前用户资料。
    接口层仅负责确保用户已经通过 token 鉴权，再调用服务层把 ORM 用户对象
    转换成统一的响应结构。

    Args:
        current_user: 由 token 解析得到的当前登录用户。
        db: 当前请求注入的数据库会话。

    Returns:
        UserResponse: 当前登录用户的资料信息。
    """
    return AuthService(db).get_current_user(current_user)
