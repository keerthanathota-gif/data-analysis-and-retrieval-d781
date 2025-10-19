from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.auth.models import get_auth_db, User
from app.auth.schemas import UserCreate, UserLogin, Token, UserResponse
from app.auth.service import AuthService
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/signup", response_model=UserResponse)
def signup(payload: UserCreate, db: Session = Depends(get_auth_db)):
    user = service.signup(db, payload.username, payload.email, payload.password, payload.role)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_auth_db)):
    return service.login(db, payload.username, payload.password)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Logged out"}
