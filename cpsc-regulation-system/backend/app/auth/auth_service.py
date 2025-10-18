"""
Authentication service for CPSC Regulation System
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
from datetime import datetime as dt
from jose import jwt
import requests
from app.config import (
    GOOGLE_CLIENT_ID,
    MICROSOFT_CLIENT_ID,
    APPLE_CLIENT_ID,
)
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.database import User, UserRole, ActivityLog, OAuthAccount
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
                detail="Sign in failed. Please check your username and password.",
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

    def login_admin(self, db: Session, username: str, password: str, ip_address: str = None, user_agent: str = None) -> dict:
        """Admin-only login that prevents non-admin users from authenticating"""
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

        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )

        user.last_login = datetime.utcnow()
        db.commit()

        self.log_activity(db, user.id, "admin_login", f"Admin {username} logged in", ip_address, user_agent)

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

    def _generate_unique_username(self, db: Session, base: str) -> str:
        """Generate a unique username based on a base string"""
        sanitized = ''.join(c for c in base.lower() if c.isalnum() or c in ('_', '-')) or 'user'
        candidate = sanitized
        suffix = 1
        while db.query(User).filter(User.username == candidate).first():
            suffix += 1
            candidate = f"{sanitized}{suffix}"
        return candidate

    def _default_provider_account_id(self, provider: str, provider_account_id: Optional[str], email: Optional[str]) -> str:
        if provider_account_id:
            return provider_account_id
        if email:
            return email.lower()
        return f"{provider}-{secrets.token_hex(8)}"

    def login_or_register_oauth(
        self,
        db: Session,
        provider: str,
        provider_account_id: Optional[str],
        email: Optional[str],
        name: Optional[str],
        access_token: Optional[str],
        refresh_token: Optional[str],
        expires_at: Optional[datetime]
    ) -> dict:
        """Login or register a user via OAuth provider and return JWT token data"""
        provider_account_id = self._default_provider_account_id(provider, provider_account_id, email)
        # Find linked account first
        account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_account_id == provider_account_id,
            )
            .first()
        )

        if account:
            user = account.user
        else:
            # If not linked, try existing user by email
            user = None
            if email:
                user = db.query(User).filter(User.email == email).first()

            if not user:
                # Create new user
                base_username = (email.split('@')[0] if email else f"{provider}_user")
                username = self._generate_unique_username(db, base_username)
                random_password = secrets.token_urlsafe(16)
                user = User(
                    username=username,
                    email=email or f"{provider}_{provider_account_id}@example.local",
                    hashed_password=get_password_hash(random_password),
                    role=UserRole.USER,
                    is_active=True,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Link OAuth account
            account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_account_id=provider_account_id,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_at=expires_at,
            )
            db.add(account)
            db.commit()

        # Update last login and log activity
        user.last_login = datetime.utcnow()
        db.commit()

        self.log_activity(
            db,
            user.id,
            "oauth_login",
            f"User {user.username} logged in via {provider}",
        )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            data={"sub": user.username, "user_id": user.id, "role": user.role.value},
            expires_delta=access_token_expires,
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value,
                "is_active": user.is_active,
            },
        }

    # --- ID token verification for real OAuth logins ---
    def verify_id_token(self, provider: str, id_token: str) -> dict:
        provider = provider.lower()
        if provider == "google":
            jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
            audience = GOOGLE_CLIENT_ID
            issuers = {"https://accounts.google.com", "accounts.google.com"}
        elif provider == "microsoft":
            jwks_uri = "https://login.microsoftonline.com/common/discovery/v2.0/keys"
            audience = MICROSOFT_CLIENT_ID
            issuers = None  # Azure AD varies by tenant
        elif provider == "apple":
            jwks_uri = "https://appleid.apple.com/auth/keys"
            audience = APPLE_CLIENT_ID
            issuers = {"https://appleid.apple.com"}
        else:
            raise HTTPException(status_code=400, detail="Unsupported provider")

        if not audience:
            raise HTTPException(status_code=500, detail="OAuth provider not configured on server")

        jwks = requests.get(jwks_uri, timeout=10).json()
        unverified_header = jwt.get_unverified_header(id_token)
        kid = unverified_header.get("kid")
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            # Some providers rotate keys; try verify without kid match using all keys
            last_error = None
            for candidate in jwks.get("keys", []):
                try:
                    claims = jwt.decode(id_token, candidate, algorithms=[candidate.get("alg", "RS256")], audience=audience)
                    if issuers and claims.get("iss") not in issuers:
                        continue
                    return claims
                except Exception as e:  # noqa: BLE001
                    last_error = e
            raise HTTPException(status_code=401, detail=f"Invalid ID token: {last_error}")

        # Verify with selected key
        claims = jwt.decode(id_token, key, algorithms=[key.get("alg", "RS256")], audience=audience)
        if issuers and claims.get("iss") not in issuers:
            raise HTTPException(status_code=401, detail="Invalid token issuer")
        return claims

    def token_login_oauth(self, db: Session, provider: str, id_token: str) -> dict:
        """Verify provider ID token and login/register user accordingly."""
        claims = self.verify_id_token(provider, id_token)
        subject = claims.get("sub") or claims.get("oid")
        email = claims.get("email")
        name = claims.get("name") or claims.get("preferred_username")
        return self.login_or_register_oauth(
            db=db,
            provider=provider,
            provider_account_id=subject,
            email=email,
            name=name,
            access_token=None,
            refresh_token=None,
            expires_at=None,
        )

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