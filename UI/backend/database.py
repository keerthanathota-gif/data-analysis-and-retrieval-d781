"""
Database models and schema for UI Authentication System
Copied and simplified from main CFR application
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cfr_data.db")

Base = declarative_base()

# Core CFR models (simplified - only what's needed for auth system)
class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    subchapters = relationship("Subchapter", back_populates="chapter", cascade="all, delete-orphan")

class Subchapter(Base):
    __tablename__ = 'subchapters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    name = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    chapter = relationship("Chapter", back_populates="subchapters")
    parts = relationship("Part", back_populates="subchapter", cascade="all, delete-orphan")

class Part(Base):
    __tablename__ = 'parts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subchapter_id = Column(Integer, ForeignKey('subchapters.id'), nullable=False)
    heading = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    subchapter = relationship("Subchapter", back_populates="parts")
    sections = relationship("Section", back_populates="part", cascade="all, delete-orphan")

class Section(Base):
    __tablename__ = 'sections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    part_id = Column(Integer, ForeignKey('parts.id'), nullable=False)
    section_number = Column(String(100))
    subject = Column(String(1000))
    text = Column(Text)
    citation = Column(String(500))
    section_label = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

    part = relationship("Part", back_populates="sections")

class SimilarityResult(Base):
    __tablename__ = 'similarity_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item1_type = Column(String(50), nullable=False)
    item1_id = Column(Integer, nullable=False)
    item2_type = Column(String(50), nullable=False)
    item2_id = Column(Integer, nullable=False)
    similarity_score = Column(Float, nullable=False)
    is_overlap = Column(Boolean, default=False)
    is_redundant = Column(Boolean, default=False)
    overlap_data = Column(Text)
    llm_justification = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ParityCheck(Base):
    __tablename__ = 'parity_checks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String(50), nullable=False)
    item_id = Column(Integer, nullable=False)
    check_type = Column(String(100), nullable=False)
    result = Column(Boolean, nullable=False)
    details = Column(Text)
    llm_justification = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database initialization
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database and create all tables"""
    Base.metadata.create_all(bind=engine)

def reset_db():
    """Reset database - drop all tables and recreate"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Database reset completed")

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
