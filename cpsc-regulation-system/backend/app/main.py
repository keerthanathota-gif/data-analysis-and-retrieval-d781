"""
Main FastAPI Application for CPSC Regulation System
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.models.database import init_db, create_default_admin
from app.auth.routes import router as auth_router
from app.admin.routes import router as admin_router
from app.search.routes import router as search_router
from app.config import API_HOST, API_PORT, ALLOWED_ORIGINS, VISUALIZATIONS_DIR, DATA_DIR, OUTPUT_DIR

# Initialize FastAPI app
app = FastAPI(
    title="CPSC Regulation System",
    description="Intelligent analysis and retrieval system for CPSC regulations with authentication",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount static files for visualizations
app.mount("/visualizations", StaticFiles(directory=VISUALIZATIONS_DIR), name="visualizations")

# Include routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(search_router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create default admin user"""
    init_db()
    create_default_admin()
    print("Database initialized and default admin user created")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "CPSC Regulation System API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Serve the React frontend
@app.get("/ui")
async def serve_ui():
    """Serve the React UI"""
    ui_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "build", "index.html")
    if os.path.exists(ui_path):
        return FileResponse(ui_path)
    else:
        return {"message": "Frontend not built. Run 'npm run build' in the frontend directory."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT)