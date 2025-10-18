"""
Authentication routes for CPSC Regulation System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.models.database import get_db, UserRole
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse, UserUpdate
from app.auth.auth_service import AuthService
from app.auth.dependencies import get_current_active_user, get_admin_user

router = APIRouter(prefix="/auth", tags=["authentication"])
auth_service = AuthService()

@router.post("/signup", response_model=UserResponse)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        user = auth_service.create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user and return access token"""
    try:
        # Get client IP and user agent
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")
        
        token_data = auth_service.login_user(
            db=db,
            username=user_credentials.username,
            password=user_credentials.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return token_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        # Only allow updating username and email for regular users
        if current_user.role == UserRole.USER:
            if user_update.role is not None or user_update.is_active is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions to change role or active status"
                )
        
        # Update user
        user = db.query(User).filter(User.id == current_user.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user_update.username is not None:
            user.username = user_update.username
        if user_update.email is not None:
            user.email = user_update.email
        if user_update.role is not None and current_user.role == UserRole.ADMIN:
            user.role = user_update.role
        if user_update.is_active is not None and current_user.role == UserRole.ADMIN:
            user.is_active = user_update.is_active
        
        db.commit()
        db.refresh(user)
        
        # Log activity
        auth_service.log_activity(
            db=db,
            user_id=user.id,
            action="profile_update",
            details=f"User {user.username} updated profile"
        )
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}"
        )

@router.post("/logout")
async def logout(
    current_user: UserResponse = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Logout user (log activity)"""
    try:
        auth_service.log_activity(
            db=db,
            user_id=current_user.id,
            action="logout",
            details=f"User {current_user.username} logged out"
        )
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during logout: {str(e)}"
        )