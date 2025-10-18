"""
Authentication service for CPSC Regulation System
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.database import User, UserRole, ActivityLog
from app.auth.password_utils import verify_password, get_password_hash, check_password_strength
from app.auth.jwt_utils import create_access_token
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    def __init__(self):
        pass

    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_user(self, db: Session, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> User:
        """Create a new user"""
        # Check if user already exists
        if db.query(User).filter(User.username == username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        if db.query(User).filter(User.email == email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check password strength
        password_check = check_password_strength(password)
        if not password_check["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password does not meet requirements: {', '.join(password_check['issues'])}"
            )
        
        # Create user
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user

    def login_user(self, db: Session, username: str, password: str, ip_address: str = None, user_agent: str = None) -> dict:
        """Login user and return access token"""
        user = self.authenticate_user(db, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Log activity
        self.log_activity(db, user.id, "login", f"User {username} logged in", ip_address, user_agent)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active
            }
        }

    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def get_all_users(self, db: Session, skip: int = 0, limit: int = 100) -> list:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()

    def update_user_role(self, db: Session, user_id: int, new_role: UserRole) -> User:
        """Update user role (admin only)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user

    def deactivate_user(self, db: Session, user_id: int) -> User:
        """Deactivate user (admin only)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user

    def activate_user(self, db: Session, user_id: int) -> User:
        """Activate user (admin only)"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user

    def log_activity(self, db: Session, user_id: int, action: str, details: str = None, ip_address: str = None, user_agent: str = None):
        """Log user activity"""
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(activity)
        db.commit()

    def get_activity_logs(self, db: Session, user_id: int = None, skip: int = 0, limit: int = 100) -> list:
        """Get activity logs with optional user filter"""
        query = db.query(ActivityLog)
        if user_id:
            query = query.filter(ActivityLog.user_id == user_id)
        
        return query.order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit).all()

    def get_user_stats(self, db: Session) -> dict:
        """Get user statistics"""
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "admin_users": admin_users,
            "regular_users": total_users - admin_users
        }