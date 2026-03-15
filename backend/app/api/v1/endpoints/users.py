from fastapi import APIRouter

from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserResponse, summary="Get current user profile")
def get_current_user_profile() -> UserResponse:
    return UserService().get_current_user()


@router.patch("/me", response_model=UserResponse, summary="Update current user profile")
def update_current_user_profile(payload: UserUpdateRequest) -> UserResponse:
    return UserService().update_current_user(payload)


@router.get("/check-username", summary="Check username availability")
def check_username(username: str) -> dict[str, bool]:
    return {"available": UserService().is_username_available(username)}
