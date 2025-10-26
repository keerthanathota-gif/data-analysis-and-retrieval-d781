"""
Configuration file for CFR Agentic AI Application
"""
import os
from pathlib import Path

# Try to load dotenv if available (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, continue without it

# Base directory (project root) - using Path for better cross-platform support
BASE_DIR = str(Path(__file__).parent.parent.absolute())

# Default URLs to crawl for CFR data (can be overridden by user input)
DEFAULT_CRAWL_URLS = [
    "https://www.govinfo.gov/bulkdata/CFR/2025/title-16/"
]

# URLs will be set dynamically by user input
CRAWL_URLS = DEFAULT_CRAWL_URLS.copy()

# Database configuration helper for cross-platform compatibility
def get_sqlite_url(db_name):
    """Generate proper SQLite URL that works on all platforms"""
    db_path = Path(BASE_DIR) / db_name
    db_path_str = str(db_path.absolute())
    # Convert backslashes to forward slashes for SQLite
    db_path_str = db_path_str.replace('\\', '/')
    return f"sqlite:///{db_path_str}"

# Database configuration - Dual databases for clean separation
AUTH_DATABASE_URL = get_sqlite_url('auth.db')
CFR_DATABASE_URL = get_sqlite_url('cfr_data.db')

# Legacy support - some old imports might still use DATABASE_URL
DATABASE_URL = CFR_DATABASE_URL  # Deprecated - use CFR_DATABASE_URL or AUTH_DATABASE_URL

# Embedding model configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# Clustering configuration
CLUSTERING_ALGORITHM = "kmeans"  # Only K-Means is supported
MIN_CLUSTER_SIZE = 2
MIN_SAMPLES = 1
DEFAULT_N_CLUSTERS = 5  # Default number of clusters for K-Means

# Similarity thresholds
SIMILARITY_THRESHOLD = 0.75
OVERLAP_THRESHOLD = 0.80
REDUNDANCY_THRESHOLD = 0.85

# RAG configuration
TOP_K_RESULTS = 10
LLM_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # For embeddings
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50

# Application settings
DATA_DIR = os.path.join(BASE_DIR, "cfr_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
VISUALIZATIONS_DIR = os.path.join(BASE_DIR, "visualizations")

# FastAPI settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Model Context Protocol settings
MCP_ENABLED = True
MCP_SERVER_NAME = "cfr-agentic-server"
MCP_VERSION = "1.0.0"

# Authentication settings
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Frontend base URL (used for OAuth callback redirects)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# OAuth (OIDC) provider configuration - set env vars in deployment
# Google
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/oauth/google/callback"
)

# Microsoft (v2.0 endpoint)
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_REDIRECT_URI = os.getenv(
    "MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/oauth/microsoft/callback"
)

# Apple (requires private key based client secret; placeholder support)
APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
APPLE_CLIENT_SECRET = os.getenv("APPLE_CLIENT_SECRET")  # Pre-signed JWT
APPLE_REDIRECT_URI = os.getenv(
    "APPLE_REDIRECT_URI", "http://localhost:8000/auth/oauth/apple/callback"
)

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:8000",  # FastAPI dev server
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]
