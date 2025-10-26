"""
Models package for CPSC Regulation System
Contains database models and schemas
"""

from app.models.auth_database import (
    get_auth_db,
    UserRole,
    User,
    ActivityLog,
    OAuthAccount,
    init_auth_db,
    reset_auth_db,
    create_default_admin
)

from app.models.cfr_database import (
    get_cfr_db,
    Chapter,
    Subchapter,
    Part,
    Section,
    ChapterEmbedding,
    SubchapterEmbedding,
    SectionEmbedding,
    Cluster,
    SimilarityResult,
    ParityCheck,
    init_cfr_db,
    reset_cfr_db
)

__all__ = [
    # Auth database
    'get_auth_db',
    'UserRole',
    'User',
    'ActivityLog',
    'OAuthAccount',
    'init_auth_db',
    'reset_auth_db',
    'create_default_admin',
    # CFR database
    'get_cfr_db',
    'Chapter',
    'Subchapter',
    'Part',
    'Section',
    'ChapterEmbedding',
    'SubchapterEmbedding',
    'SectionEmbedding',
    'Cluster',
    'SimilarityResult',
    'ParityCheck',
    'init_cfr_db',
    'reset_cfr_db',
]
