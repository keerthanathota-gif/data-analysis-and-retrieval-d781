"""
Configuration file for CFR Agentic AI Application
"""
import os

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Default URLs to crawl for CFR data (can be overridden by user input)
DEFAULT_CRAWL_URLS = [
    "https://www.govinfo.gov/bulkdata/CFR/2025/title-16/"
]

# URLs will be set dynamically by user input
CRAWL_URLS = DEFAULT_CRAWL_URLS.copy()

# Database configuration
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'cfr_data.db')}"

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
