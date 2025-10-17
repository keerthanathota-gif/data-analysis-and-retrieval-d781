"""
Configuration file for UI Authentication System
Simplified from main CFR application
"""
import os

# Base directory (UI folder)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database configuration
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'cfr_data.db')}"

# FastAPI settings for UI
API_HOST = "0.0.0.0"
API_PORT = 8001  # Different from main app (8000)

# Authentication settings
SECRET_KEY = "cfr-agentic-ai-secret-key-change-in-production-2025"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
