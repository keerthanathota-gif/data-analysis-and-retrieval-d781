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
