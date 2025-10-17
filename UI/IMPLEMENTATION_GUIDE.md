# UI Module - Complete Implementation Guide

## Table of Contents
1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Phase 1: Backend - Database Models](#phase-1-backend---database-models)
4. [Phase 2: Backend - Authentication Service](#phase-2-backend---authentication-service)
5. [Phase 3: Backend - API Router](#phase-3-backend---api-router)
6. [Phase 4: Frontend - Login Page](#phase-4-frontend---login-page)
7. [Phase 5: Frontend - User Dashboard](#phase-5-frontend---user-dashboard)
8. [Phase 6: Frontend - Admin Panel](#phase-6-frontend---admin-panel)
9. [Phase 7: JavaScript - Authentication](#phase-7-javascript---authentication)
10. [Phase 8: JavaScript - API Wrapper](#phase-8-javascript---api-wrapper)
11. [Phase 9: CSS Styling](#phase-9-css-styling)
12. [Phase 10: Setup Script](#phase-10-setup-script)
13. [Phase 11: Integration with Main App](#phase-11-integration-with-main-app)
14. [Testing & Verification](#testing--verification)

---

## Overview

This guide provides a complete step-by-step implementation of the User/Admin authentication system for the CFR Agentic AI Application. All code is self-contained in the UI folder.

**Key Features:**
- JWT-based authentication
- Role-based access control (User vs Admin)
- Audit logging
- Secure password hashing
- Clean separation from existing codebase

**Tech Stack:**
- Backend: FastAPI, SQLAlchemy, JWT, bcrypt
- Frontend: HTML5, JavaScript (Vanilla), CSS3
- Database: SQLite (same as main app)

---

## Folder Structure

```
UI/
├── IMPLEMENTATION_GUIDE.md (this file)
├── README.md
│
├── backend/                    # Backend authentication logic
│   ├── __init__.py
│   ├── auth_models.py         # Database models
│   ├── auth_service.py        # JWT & password utilities
│   ├── auth_schemas.py        # Pydantic schemas
│   └── auth_router.py         # API endpoints
│
├── frontend/                   # Frontend UI
│   ├── login.html
│   ├── dashboard.html         # User view
│   ├── admin.html             # Admin view
│   │
│   ├── js/
│   │   ├── auth.js            # Authentication logic
│   │   ├── api.js             # API wrapper
│   │   ├── dashboard.js       # User dashboard
│   │   └── admin.js           # Admin panel
│   │
│   └── css/
│       └── styles.css         # Styling
│
└── scripts/
    └── setup_auth.py          # Database setup
```

---

## Phase 1: Backend - Database Models

### File: `UI/backend/__init__.py`

```python
"""
UI Backend Module - Authentication and Authorization
"""
```

---

### File: `UI/backend/auth_models.py`

```python
"""
Database Models for Authentication
- User: Stores user accounts with roles
- AuditLog: Tracks user actions for security
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import Base
import enum


class UserRole(str, enum.Enum):
    """User role enumeration"""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """
    User model for authentication

    Attributes:
        id: Primary key
        username: Unique username for login
        email: User email address
        hashed_password: Bcrypt hashed password
        role: User role (admin or user)
        is_active: Account status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role}')>"


class AuditLog(Base):
    """
    Audit log for tracking user actions

    Attributes:
        id: Primary key
        user_id: ID of user who performed action
        username: Username (for reference)
        action: Action performed
        endpoint: API endpoint accessed
        timestamp: When action occurred
        details: Additional JSON details
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)
    endpoint = Column(String(255))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(String(1000))  # JSON string

    def __repr__(self):
        return f"<AuditLog(user='{self.username}', action='{self.action}')>"
```

**Purpose:**
- Defines database schema for users and audit logs
- Uses SQLAlchemy ORM for database operations
- Integrates with existing app.database module

---

## Phase 2: Backend - Authentication Service

### File: `UI/backend/auth_service.py`

```python
"""
Authentication Service
- Password hashing and verification (bcrypt)
- JWT token generation and validation
- User authentication logic
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from UI.backend.auth_models import User, UserRole

# ============================================
# CONFIGURATION
# ============================================

SECRET_KEY = "cfr-agentic-ai-secret-key-change-in-production-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Token expires after 1 hour

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================
# PASSWORD FUNCTIONS
# ============================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash

    Args:
        plain_password: Password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


# ============================================
# JWT TOKEN FUNCTIONS
# ============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token

    Args:
        data: Dictionary with user data (username, role, etc.)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Encode token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload dictionary, or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        print(f"Token decode error: {e}")
        return None


# ============================================
# USER AUTHENTICATION
# ============================================

def authenticate_user(db, username: str, password: str) -> Optional[User]:
    """
    Authenticate user with username and password

    Args:
        db: Database session
        username: Username to authenticate
        password: Plain text password

    Returns:
        User object if authentication successful, None otherwise
    """
    # Find user
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        return None

    # Check if active
    if not user.is_active:
        return None

    return user


def validate_token(token: str) -> Optional[dict]:
    """
    Validate JWT token and return payload

    Args:
        token: JWT token string

    Returns:
        Token payload if valid, None otherwise
    """
    payload = decode_access_token(token)
    if not payload:
        return None

    # Check expiration
    exp = payload.get("exp")
    if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
        return None

    return payload
```

**Purpose:**
- Handles password hashing with bcrypt
- Creates and validates JWT tokens
- Authenticates users against database

---

## Phase 3: Backend - API Router

### File: `UI/backend/auth_schemas.py`

```python
"""
Pydantic Schemas for Authentication API
- Request/response models
- Data validation
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserCreate(BaseModel):
    """User creation schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="user", pattern="^(user|admin)$")


class UserResponse(BaseModel):
    """User response schema (no password)"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload schema"""
    username: Optional[str] = None
    role: Optional[str] = None


class AuditLogResponse(BaseModel):
    """Audit log response schema"""
    id: int
    username: str
    action: str
    endpoint: Optional[str]
    timestamp: datetime
    details: Optional[str]

    class Config:
        from_attributes = True
```

---

### File: `UI/backend/auth_router.py`

```python
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
import sys
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.database import get_db
from UI.backend.auth_models import User, UserRole, AuditLog
from UI.backend.auth_schemas import (
    Token, UserCreate, UserResponse, AuditLogResponse
)
from UI.backend.auth_service import (
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
```

**Purpose:**
- Provides REST API endpoints for authentication
- Implements JWT token-based auth
- Protects endpoints with role-based access control
- Logs all authentication events

---

## Phase 4: Frontend - Login Page

### File: `UI/frontend/login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - CFR Agentic AI</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body class="login-page">
    <div class="login-container">
        <div class="login-box">
            <!-- Logo/Header -->
            <div class="login-header">
                <h1>CFR Agentic AI</h1>
                <p class="subtitle">Code of Federal Regulations Analysis Platform</p>
            </div>

            <!-- Login Form -->
            <form id="loginForm" class="login-form">
                <h2>Login</h2>

                <div class="form-group">
                    <label for="username">Username</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        required
                        autocomplete="username"
                        placeholder="Enter your username"
                    >
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        required
                        autocomplete="current-password"
                        placeholder="Enter your password"
                    >
                </div>

                <!-- Error Message -->
                <div id="errorMessage" class="error-message" style="display: none;"></div>

                <!-- Submit Button -->
                <button type="submit" class="btn-primary" id="loginBtn">
                    Login
                </button>

                <!-- Loading Spinner -->
                <div id="loadingSpinner" class="loading-spinner" style="display: none;">
                    <div class="spinner"></div>
                    <span>Authenticating...</span>
                </div>
            </form>

            <!-- Help Text -->
            <div class="help-section">
                <p class="help-text">
                    <strong>Default Admin Credentials:</strong><br>
                    Username: <code>admin</code><br>
                    Password: <code>admin123</code>
                </p>
                <p class="help-note">
                    ⚠️ Change the admin password after first login
                </p>
            </div>
        </div>

        <!-- Footer -->
        <div class="login-footer">
            <p>&copy; 2025 CFR Agentic AI Platform</p>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="js/auth.js"></script>
</body>
</html>
```

**Purpose:**
- Provides login interface
- Captures username/password
- Displays errors and loading states
- Shows default credentials for testing

---

## Phase 5: Frontend - User Dashboard

### File: `UI/frontend/dashboard.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - CFR Agentic AI</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body class="dashboard-page">
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div class="nav-brand">
            <h1>CFR Agentic AI</h1>
            <span class="user-badge">User</span>
        </div>
        <div class="nav-menu">
            <span id="userDisplayName" class="user-name"></span>
            <button onclick="logout()" class="btn-logout">Logout</button>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Sidebar -->
        <aside class="sidebar">
            <ul class="nav-links">
                <li><a href="#overview" class="active" onclick="showSection('overview')">Overview</a></li>
                <li><a href="#search" onclick="showSection('search')">RAG Search</a></li>
                <li><a href="#results" onclick="showSection('results')">View Results</a></li>
                <li><a href="#stats" onclick="showSection('stats')">Statistics</a></li>
            </ul>
        </aside>

        <!-- Content Area -->
        <main class="content-area">
            <!-- Overview Section -->
            <section id="overview-section" class="content-section active">
                <h2>Welcome to CFR Analysis Platform</h2>
                <p>You have <strong>User</strong> access level.</p>

                <div class="info-cards">
                    <div class="info-card">
                        <h3>What You Can Do</h3>
                        <ul>
                            <li>✓ Search regulations using RAG queries</li>
                            <li>✓ View clustering results</li>
                            <li>✓ Browse analysis reports</li>
                            <li>✓ View visualizations</li>
                            <li>✓ Download results</li>
                        </ul>
                    </div>

                    <div class="info-card">
                        <h3>Restrictions</h3>
                        <ul>
                            <li>✗ Cannot run data pipeline</li>
                            <li>✗ Cannot perform clustering</li>
                            <li>✗ Cannot run analysis</li>
                            <li>✗ Cannot manage users</li>
                        </ul>
                        <p class="note">Contact admin for elevated access</p>
                    </div>
                </div>

                <!-- Quick Stats -->
                <div class="quick-stats" id="quickStats">
                    <h3>Quick Statistics</h3>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <span class="stat-value" id="statChapters">-</span>
                            <span class="stat-label">Chapters</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-value" id="statSubchapters">-</span>
                            <span class="stat-label">Subchapters</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-value" id="statSections">-</span>
                            <span class="stat-label">Sections</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Search Section -->
            <section id="search-section" class="content-section">
                <h2>RAG Search</h2>
                <p>Search regulations using natural language queries</p>

                <div class="search-box">
                    <input
                        type="text"
                        id="ragQuery"
                        placeholder="e.g., privacy protection requirements"
                        class="search-input"
                    >
                    <button onclick="performSearch()" class="btn-primary">Search</button>
                </div>

                <div id="searchResults" class="search-results">
                    <!-- Results will be populated here -->
                </div>
            </section>

            <!-- Results Section -->
            <section id="results-section" class="content-section">
                <h2>Analysis Results</h2>
                <p>Browse existing clustering and similarity results</p>

                <div class="results-tabs">
                    <button class="tab-btn active" onclick="showResults('clustering')">Clustering</button>
                    <button class="tab-btn" onclick="showResults('similarity')">Similarity</button>
                </div>

                <div id="resultsContent" class="results-content">
                    <p class="placeholder">Select a result type to view</p>
                </div>
            </section>

            <!-- Stats Section -->
            <section id="stats-section" class="content-section">
                <h2>Detailed Statistics</h2>
                <div id="detailedStats" class="detailed-stats">
                    <p>Loading statistics...</p>
                </div>
            </section>
        </main>
    </div>

    <!-- Scripts -->
    <script src="js/auth.js"></script>
    <script src="js/api.js"></script>
    <script src="js/dashboard.js"></script>
</body>
</html>
```

**Purpose:**
- Read-only dashboard for regular users
- Search interface for RAG queries
- View existing results and statistics
- Clean, intuitive navigation

---

## Phase 6: Frontend - Admin Panel

### File: `UI/frontend/admin.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Panel - CFR Agentic AI</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body class="admin-page">
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div class="nav-brand">
            <h1>CFR Agentic AI</h1>
            <span class="admin-badge">Admin</span>
        </div>
        <div class="nav-menu">
            <span id="userDisplayName" class="user-name"></span>
            <button onclick="logout()" class="btn-logout">Logout</button>
        </div>
    </nav>

    <!-- Main Content -->
    <div class="main-content">
        <!-- Sidebar -->
        <aside class="sidebar">
            <ul class="nav-links">
                <li><a href="#dashboard" class="active" onclick="showSection('dashboard')">Dashboard</a></li>
                <li><a href="#pipeline" onclick="showSection('pipeline')">Pipeline</a></li>
                <li><a href="#clustering" onclick="showSection('clustering')">Clustering</a></li>
                <li><a href="#analysis" onclick="showSection('analysis')">Analysis</a></li>
                <li><a href="#search" onclick="showSection('search')">RAG Search</a></li>
                <li><a href="#users" onclick="showSection('users')">User Management</a></li>
                <li><a href="#logs" onclick="showSection('logs')">Audit Logs</a></li>
            </ul>
        </aside>

        <!-- Content Area -->
        <main class="content-area">
            <!-- Dashboard Section -->
            <section id="dashboard-section" class="content-section active">
                <h2>Admin Dashboard</h2>
                <p>Full administrative access to all system operations</p>

                <div class="quick-stats" id="adminStats">
                    <h3>System Overview</h3>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <span class="stat-value" id="statChapters">-</span>
                            <span class="stat-label">Chapters</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-value" id="statSubchapters">-</span>
                            <span class="stat-label">Subchapters</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-value" id="statSections">-</span>
                            <span class="stat-label">Sections</span>
                        </div>
                        <div class="stat-box">
                            <span class="stat-value" id="statUsers">-</span>
                            <span class="stat-label">Users</span>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Pipeline Section -->
            <section id="pipeline-section" class="content-section">
                <h2>Data Pipeline</h2>
                <p>Run complete data processing pipeline</p>

                <div class="action-box">
                    <div class="form-group">
                        <label for="pipelineUrl">CFR Data URL</label>
                        <input
                            type="url"
                            id="pipelineUrl"
                            placeholder="https://example.com/cfr-data.xml"
                            class="input-full"
                        >
                    </div>
                    <button onclick="runPipeline()" class="btn-primary">Run Pipeline</button>
                </div>

                <div id="pipelineStatus" class="status-box">
                    <h3>Pipeline Status</h3>
                    <p id="pipelineMessage">Ready</p>
                    <div id="pipelineProgress" class="progress-bar" style="display: none;">
                        <div class="progress-fill"></div>
                    </div>
                </div>
            </section>

            <!-- Clustering Section -->
            <section id="clustering-section" class="content-section">
                <h2>Clustering Operations</h2>
                <p>Perform K-Means clustering with LLM summaries</p>

                <div class="action-box">
                    <div class="form-group">
                        <label for="clusterLevel">Level</label>
                        <select id="clusterLevel" class="input-full">
                            <option value="chapter">Chapter</option>
                            <option value="subchapter">Subchapter</option>
                            <option value="section">Section</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="clusterCount">Number of Clusters</label>
                        <input
                            type="number"
                            id="clusterCount"
                            value="5"
                            min="2"
                            max="20"
                            class="input-full"
                        >
                    </div>
                    <button onclick="performClustering()" class="btn-primary">Perform Clustering</button>
                </div>

                <div id="clusteringResults" class="results-box">
                    <!-- Results will be populated here -->
                </div>
            </section>

            <!-- Analysis Section -->
            <section id="analysis-section" class="content-section">
                <h2>Semantic Analysis</h2>
                <p>Run similarity, overlap, and redundancy analysis</p>

                <div class="action-box">
                    <div class="form-group">
                        <label for="analysisLevel">Analysis Level</label>
                        <select id="analysisLevel" class="input-full">
                            <option value="chapter">Chapter</option>
                            <option value="subchapter">Subchapter</option>
                            <option value="section">Section</option>
                        </select>
                    </div>
                    <button onclick="runSimilarityAnalysis()" class="btn-primary">Run Similarity Analysis</button>
                    <button onclick="checkOverlaps()" class="btn-secondary">Check Overlaps</button>
                    <button onclick="checkRedundancy()" class="btn-secondary">Check Redundancy</button>
                </div>

                <div id="analysisResults" class="results-box">
                    <!-- Results will be populated here -->
                </div>
            </section>

            <!-- Search Section -->
            <section id="search-section" class="content-section">
                <h2>RAG Search</h2>
                <p>Search regulations using natural language queries</p>

                <div class="search-box">
                    <input
                        type="text"
                        id="ragQuery"
                        placeholder="e.g., privacy protection requirements"
                        class="search-input"
                    >
                    <button onclick="performSearch()" class="btn-primary">Search</button>
                </div>

                <div id="searchResults" class="search-results">
                    <!-- Results will be populated here -->
                </div>
            </section>

            <!-- User Management Section -->
            <section id="users-section" class="content-section">
                <h2>User Management</h2>
                <p>Create and manage user accounts</p>

                <!-- Create User Form -->
                <div class="action-box">
                    <h3>Create New User</h3>
                    <form id="createUserForm">
                        <div class="form-row">
                            <div class="form-group">
                                <label for="newUsername">Username</label>
                                <input type="text" id="newUsername" required>
                            </div>
                            <div class="form-group">
                                <label for="newEmail">Email</label>
                                <input type="email" id="newEmail" required>
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group">
                                <label for="newPassword">Password</label>
                                <input type="password" id="newPassword" required minlength="6">
                            </div>
                            <div class="form-group">
                                <label for="newRole">Role</label>
                                <select id="newRole">
                                    <option value="user">User</option>
                                    <option value="admin">Admin</option>
                                </select>
                            </div>
                        </div>
                        <button type="submit" class="btn-primary">Create User</button>
                    </form>
                </div>

                <!-- Users List -->
                <div class="users-list">
                    <h3>Existing Users</h3>
                    <table id="usersTable" class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Username</th>
                                <th>Email</th>
                                <th>Role</th>
                                <th>Status</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Users will be populated here -->
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- Audit Logs Section -->
            <section id="logs-section" class="content-section">
                <h2>Audit Logs</h2>
                <p>View system audit trail</p>

                <div class="logs-container">
                    <table id="logsTable" class="data-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>User</th>
                                <th>Action</th>
                                <th>Endpoint</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            <!-- Logs will be populated here -->
                        </tbody>
                    </table>
                </div>
            </section>
        </main>
    </div>

    <!-- Scripts -->
    <script src="js/auth.js"></script>
    <script src="js/api.js"></script>
    <script src="js/admin.js"></script>
</body>
</html>
```

**Purpose:**
- Full admin control panel
- Pipeline, clustering, analysis operations
- User management interface
- Audit log viewer

---

**[Continue to next comment for remaining phases...]**
