"""
Authentication routes for CPSC Regulation System
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.models.auth_database import get_auth_db as get_db, UserRole, User
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse, UserUpdate
from app.auth.auth_service import AuthService
from app.auth.dependencies import get_current_active_user, get_admin_user
from datetime import datetime, timedelta
import os
import base64
import httpx
import urllib.parse

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

@router.post("/admin-login", response_model=Token)
async def admin_login(
    user_credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Admin-only login and return access token"""
    try:
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")

        token_data = auth_service.login_admin(
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
            detail=f"Error during admin login: {str(e)}"
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

# OAuth endpoints
@router.get("/oauth/start")
async def oauth_start(provider: str = Query(..., pattern="^(google|microsoft|apple)$")):
    """Return CSRF state and client ID for starting OAuth on the frontend."""
    from app.config import GOOGLE_CLIENT_ID, MICROSOFT_CLIENT_ID, APPLE_CLIENT_ID
    
    state = base64.urlsafe_b64encode(os.urandom(24)).decode().rstrip("=")
    
    # Get the appropriate client ID based on provider
    client_id = None
    if provider == "google":
        client_id = GOOGLE_CLIENT_ID
    elif provider == "microsoft":
        client_id = MICROSOFT_CLIENT_ID
    elif provider == "apple":
        client_id = APPLE_CLIENT_ID
    
    return {
        "provider": provider,
        "state": state,
        "client_id": client_id  # Will be None if not configured
    }

@router.post("/oauth/callback", response_model=Token)
async def oauth_callback(
    provider: str,
    provider_account_id: str,
    email: str = None,
    name: str = None,
    access_token: str = None,
    refresh_token: str = None,
    expires_in: int = None,
    db: Session = Depends(get_db)
):
    """Finalize OAuth: upsert user and return our JWT"""
    try:
        expires_at = None
        if expires_in:
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        token_data = auth_service.login_or_register_oauth(
            db=db,
            provider=provider,
            provider_account_id=provider_account_id,
            email=email,
            name=name,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        return token_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during OAuth callback: {str(e)}"
        )

@router.post("/oauth/token-login", response_model=Token)
async def oauth_token_login(
    provider: str,
    id_token: str,
    db: Session = Depends(get_db)
):
    """Verify provider ID token and login via OAuth."""
    try:
        return auth_service.token_login_oauth(db, provider, id_token)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during OAuth token login: {str(e)}"
        )

# Provider-specific OAuth callback handlers
@router.get("/oauth/{provider}/callback")
async def oauth_provider_callback(
    provider: str,
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    error_description: str = Query(None),
    db: Session = Depends(get_db)
):
    """Handle OAuth provider callback with authorization code."""
    from app.config import (
        GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI,
        MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET, MICROSOFT_REDIRECT_URI,
        APPLE_CLIENT_ID, APPLE_CLIENT_SECRET, APPLE_REDIRECT_URI,
        FRONTEND_URL
    )
    
    # Handle OAuth errors
    if error:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error={error}&description={urllib.parse.quote(error_description or '')}"
        )
    
    if not code or not state:
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=missing_parameters"
        )
    
    try:
        # Get provider configuration
        if provider == "google":
            token_url = "https://oauth2.googleapis.com/token"
            userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            client_id = GOOGLE_CLIENT_ID
            client_secret = GOOGLE_CLIENT_SECRET
            redirect_uri = GOOGLE_REDIRECT_URI
        elif provider == "microsoft":
            token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            userinfo_url = "https://graph.microsoft.com/v1.0/me"
            client_id = MICROSOFT_CLIENT_ID
            client_secret = MICROSOFT_CLIENT_SECRET
            redirect_uri = MICROSOFT_REDIRECT_URI
        elif provider == "apple":
            # Apple Sign In requires special handling
            token_url = "https://appleid.apple.com/auth/token"
            userinfo_url = None  # Apple doesn't have a userinfo endpoint
            client_id = APPLE_CLIENT_ID
            client_secret = APPLE_CLIENT_SECRET
            redirect_uri = APPLE_REDIRECT_URI
        else:
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=invalid_provider"
            )
        
        if not client_id or not client_secret:
            return RedirectResponse(
                url=f"{FRONTEND_URL}/login?error=provider_not_configured"
            )
        
        # Exchange authorization code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect_uri,
                    "client_id": client_id,
                    "client_secret": client_secret,
                }
            )
            
            if token_response.status_code != 200:
                return RedirectResponse(
                    url=f"{FRONTEND_URL}/login?error=token_exchange_failed"
                )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            id_token = token_data.get("id_token")
            expires_in = token_data.get("expires_in")
            
            # Get user information
            user_info = {}
            if provider == "apple" and id_token:
                # For Apple, decode the id_token to get user info
                import jwt
                user_info = jwt.decode(id_token, options={"verify_signature": False})
            elif userinfo_url and access_token:
                # For Google and Microsoft, fetch user info from API
                headers = {"Authorization": f"Bearer {access_token}"}
                userinfo_response = await client.get(userinfo_url, headers=headers)
                if userinfo_response.status_code == 200:
                    user_info = userinfo_response.json()
            
            # Extract user details
            email = user_info.get("email")
            name = user_info.get("name") or user_info.get("displayName")
            provider_account_id = user_info.get("sub") or user_info.get("id")
            
            # Login or register the user
            token_result = auth_service.login_or_register_oauth(
                db=db,
                provider=provider,
                provider_account_id=provider_account_id,
                email=email,
                name=name,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
            )
            
            # Redirect to frontend with JWT token
            jwt_token = token_result["access_token"]
            return RedirectResponse(
                url=f"{FRONTEND_URL}/oauth-callback?token={jwt_token}&provider={provider}"
            )
            
    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=authentication_failed&details={urllib.parse.quote(str(e))}"
        )