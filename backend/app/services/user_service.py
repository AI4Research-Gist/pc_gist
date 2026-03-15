from app.schemas.user import UserResponse, UserUpdateRequest


class UserService:
    def get_current_user(self) -> UserResponse:
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
        current = self.get_current_user()
        data = current.model_dump()
        updates = payload.model_dump(exclude_none=True)
        data.update(updates)
        return UserResponse(**data)

    def is_username_available(self, username: str) -> bool:
        return username != "demo_user"
