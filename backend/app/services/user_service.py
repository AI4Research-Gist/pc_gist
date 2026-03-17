"""用户业务逻辑层占位实现。"""

from app.schemas.user import UserResponse, UserUpdateRequest


class UserService:
    def get_current_user(self) -> UserResponse:
        # 当前仍是占位数据，后续会替换成真实鉴权用户。
        return UserResponse(
            id=1,
            username="demo_user",
            email="demo@example.com",
            phone="13800000000",
            avatar_url=None,
            biometric_enabled=False,
            status="active",
        )

    def update_current_user(self, payload: UserUpdateRequest) -> UserResponse:
        # 先基于当前用户生成数据，再用请求中的非空字段覆盖。
        current = self.get_current_user()
        data = current.model_dump()
        updates = payload.model_dump(exclude_none=True)
        data.update(updates)
        return UserResponse(**data)

    def is_username_available(self, username: str) -> bool:
        # 这里先用演示逻辑占位，后续应走数据库查询。
        return username != "demo_user"
