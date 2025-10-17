"""
Database models and schema for CFR Agentic AI Application
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
from app.config import DATABASE_URL

Base = declarative_base()

class Chapter(Base):
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subchapters = relationship("Subchapter", back_populates="chapter", cascade="all, delete-orphan")
    embeddings = relationship("ChapterEmbedding", back_populates="chapter", cascade="all, delete-orphan")

class Subchapter(Base):
    __tablename__ = 'subchapters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    name = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="subchapters")
    parts = relationship("Part", back_populates="subchapter", cascade="all, delete-orphan")
    embeddings = relationship("SubchapterEmbedding", back_populates="subchapter", cascade="all, delete-orphan")

class Part(Base):
    __tablename__ = 'parts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subchapter_id = Column(Integer, ForeignKey('subchapters.id'), nullable=False)
    heading = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
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
    
    # Relationships
    part = relationship("Part", back_populates="sections")
    embeddings = relationship("SectionEmbedding", back_populates="section", cascade="all, delete-orphan")

class ChapterEmbedding(Base):
    __tablename__ = 'chapter_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    embedding = Column(Text, nullable=False)  # Stored as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="embeddings")

class SubchapterEmbedding(Base):
    __tablename__ = 'subchapter_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    subchapter_id = Column(Integer, ForeignKey('subchapters.id'), nullable=False)
    embedding = Column(Text, nullable=False)  # Stored as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    subchapter = relationship("Subchapter", back_populates="embeddings")

class SectionEmbedding(Base):
    __tablename__ = 'section_embeddings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    section_id = Column(Integer, ForeignKey('sections.id'), nullable=False)
    embedding = Column(Text, nullable=False)  # Stored as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    section = relationship("Section", back_populates="embeddings")

class Cluster(Base):
    __tablename__ = 'clusters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_type = Column(String(50), nullable=False)  # 'chapter', 'subchapter', 'section'
    cluster_label = Column(Integer, nullable=False)
    item_ids = Column(Text, nullable=False)  # Stored as JSON array
    centroid = Column(Text)  # Stored as JSON array
    size = Column(Integer)
    summary = Column(Text)  # LLM-generated summary
    name = Column(String(200))  # LLM-suggested name
    created_at = Column(DateTime, default=datetime.utcnow)

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
    overlap_data = Column(Text)  # Overlapping content details
    llm_justification = Column(Text)  # LLM explanation
    created_at = Column(DateTime, default=datetime.utcnow)

class ParityCheck(Base):
    __tablename__ = 'parity_checks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    item_type = Column(String(50), nullable=False)
    item_id = Column(Integer, nullable=False)
    check_type = Column(String(100), nullable=False)
    result = Column(Boolean, nullable=False)
    details = Column(Text)
    llm_justification = Column(Text)  # LLM explanation
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
