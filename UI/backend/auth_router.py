"""
Authentication API Router
- Login/logout endpoints
- User management endpoints
- Protected route dependencies
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import json

# Import from local modules
from backend.database import get_db
from backend.auth_models import User, UserRole, AuditLog
from backend.auth_schemas import (
    Token, UserCreate, UserResponse, AuditLogResponse
)
from backend.auth_service import (
    authenticate_user,
    create_access_token,
    decode_access_token,
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create router
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============================================
# DEPENDENCIES
# ============================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from token

    Raises:
        HTTPException: If token invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Get user from database
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin role

    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint - authenticate and return JWT token

    Args:
        form_data: Username and password from form
        db: Database session

    Returns:
        JWT access token
    """
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)

    if not user:
        # Log failed attempt
        log = AuditLog(
            user_id=0,
            username=form_data.username,
            action="login_failed",
            endpoint="/api/auth/login",
            details=json.dumps({"reason": "invalid_credentials"})
        )
        db.add(log)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )

    # Log successful login
    log = AuditLog(
        user_id=user.id,
        username=user.username,
        action="login_success",
        endpoint="/api/auth/login",
        details=json.dumps({"role": user.role.value})
    )
    db.add(log)
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information

    Returns:
        Current user details (no password)
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint - log the logout action
    Note: Client must delete token from storage
    """
    # Log logout
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="logout",
        endpoint="/api/auth/logout"
    )
    db.add(log)
    db.commit()

    return {"message": "Logged out successfully"}


# ============================================
# USER MANAGEMENT ENDPOINTS (ADMIN ONLY)
# ============================================

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Register new user (admin only)

    Args:
        user_data: User creation data
        db: Database session
        current_user: Current admin user

    Returns:
        Created user details
    """
    # Check if username exists
    existing_user = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = db.query(User).filter(
        User.email == user_data.email
    ).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        role=UserRole(user_data.role),
        is_active=True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Log user creation
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="create_user",
        endpoint="/api/auth/register",
        details=json.dumps({
            "new_username": user_data.username,
            "role": user_data.role
        })
    )
    db.add(log)
    db.commit()

    return new_user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    List all users (admin only)

    Returns:
        List of all users
    """
    users = db.query(User).all()
    return users


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Get audit logs (admin only)

    Args:
        limit: Maximum number of logs to return

    Returns:
        List of audit logs
    """
    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).limit(limit).all()
    return logs
