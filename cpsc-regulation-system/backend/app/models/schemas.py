"""
Pydantic models for CPSC Regulation System
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.models.database import UserRole

# Authentication schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

# Activity log schemas
class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Search schemas
class SearchRequest(BaseModel):
    query: str
    level: str = "all"  # 'chapter', 'subchapter', 'section', 'all'
    top_k: Optional[int] = 20

class SearchResponse(BaseModel):
    query: str
    level: str
    top_k: int
    results: List[dict]
    total_results: int

# Pipeline schemas
class PipelineRequest(BaseModel):
    urls: List[str]

class PipelineResponse(BaseModel):
    message: str
    status: str
    urls: List[str]
    num_urls: int

class PipelineStatus(BaseModel):
    state: str
    current_step: Optional[str] = None
    progress: int
    total_steps: int
    steps_completed: List[str]
    error_message: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    stats: dict

# Analysis schemas
class AnalysisRequest(BaseModel):
    level: str  # 'chapter', 'subchapter', 'section'
    check_similarity: bool = True
    check_overlap: bool = True
    check_redundancy: bool = True
    check_parity: bool = True

class AnalysisResponse(BaseModel):
    level: str
    total_pairs: int
    results: List[dict]

# Clustering schemas
class ClusteringRequest(BaseModel):
    level: str
    n_clusters: Optional[int] = None

class ClusteringResponse(BaseModel):
    level: str
    algorithm: str
    num_clusters: int
    clusters: List[dict]

# Admin schemas
class AdminStats(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    admin_users: int
    regular_users: int
    total_sections: int
    total_chapters: int
    total_subchapters: int

class UserManagementRequest(BaseModel):
    user_id: int
    action: str  # 'activate', 'deactivate', 'change_role'
    new_role: Optional[UserRole] = None