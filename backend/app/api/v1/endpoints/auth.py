from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=LoginResponse, summary="Register a user")
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> LoginResponse:
    return AuthService(db).register(payload)


@router.post("/login", response_model=LoginResponse, summary="Login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    return AuthService(db).login(payload)


@router.post("/logout", summary="Logout")
def logout() -> dict[str, str]:
    return {"message": "Logout placeholder"}


@router.get("/me", summary="Current user")
def me() -> dict[str, str]:
    return {"message": "Current user placeholder"}
