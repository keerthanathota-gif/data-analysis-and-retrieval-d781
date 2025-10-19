from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.auth.models import User, UserRole
from app.auth.jwt_utils import get_password_hash, verify_password, create_access_token


class AuthService:
    def signup(self, db: Session, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        if db.query(User).filter((User.username == username) | (User.email == email)).first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            role=role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def login(self, db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        user.last_login = datetime.utcnow()
        db.commit()
        token = create_access_token({"sub": user.username, "user_id": user.id, "role": user.role.value})
        return {
            "access_token": token,
            "user": {"id": user.id, "username": user.username, "email": user.email, "role": user.role.value}
        }
