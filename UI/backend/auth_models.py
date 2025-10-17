"""
Database Models for Authentication
- User: Stores user accounts with roles
- AuditLog: Tracks user actions for security
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
import enum

# Import from local database module
from backend.database import Base


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
