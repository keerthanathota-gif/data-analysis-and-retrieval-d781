"""
Authentication Database models for CPSC Regulation System
Separate database for user authentication and authorization
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Enum, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from app.config import AUTH_DATABASE_URL

Base = declarative_base()

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    activity_logs = relationship("ActivityLog", back_populates="user", cascade="all, delete-orphan")
    oauth_accounts = relationship("OAuthAccount", back_populates="user", cascade="all, delete-orphan")

class OAuthAccount(Base):
    __tablename__ = 'oauth_accounts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # google, microsoft, apple
    provider_account_id = Column(String(255), nullable=False)  # sub/oidc subject
    access_token = Column(Text)
    refresh_token = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('provider', 'provider_account_id', name='uq_provider_account'),
    )

    # Relationships
    user = relationship("User", back_populates="oauth_accounts")

class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String(100), nullable=False)  # 'login', 'search', 'crawl', 'parse', etc.
    details = Column(Text)  # Additional details about the action
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="activity_logs")

# Database initialization
engine = create_engine(AUTH_DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_auth_db():
    """Initialize authentication database and create all tables"""
    Base.metadata.create_all(bind=engine)
    print("Authentication database initialized")

def reset_auth_db():
    """Reset authentication database - drop all tables and recreate"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Authentication database reset completed")

def get_auth_db():
    """Get authentication database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create default admin user
def create_default_admin():
    """Create default admin user if none exists"""
    from app.auth.password_utils import get_password_hash

    db = SessionLocal()
    try:
        # Check if any admin exists
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            admin_user = User(
                username="admin",
                email="admin@cpsc.gov",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("Default admin user created: username=admin, password=admin123")
    except Exception as e:
        print(f"Error creating default admin: {e}")
        db.rollback()
    finally:
        db.close()
