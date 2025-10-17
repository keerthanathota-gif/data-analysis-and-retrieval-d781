"""
Standalone UI Application - Authentication System
Run this separately from the main CFR application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
import os
import sys
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Initialize FastAPI app
app = FastAPI(
    title="CFR UI - Authentication System",
    description="User authentication and management interface",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import authentication router (after path setup)
try:
    from backend import auth_router
    app.include_router(auth_router.router)
    print("✓ Authentication system enabled")
except ImportError as e:
    print(f"Error: Could not import authentication router: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)

# Mount frontend static files
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(FRONTEND_PATH):
    try:
        app.mount("/ui/css", StaticFiles(directory=os.path.join(FRONTEND_PATH, "css")), name="ui_css")
        app.mount("/ui/js", StaticFiles(directory=os.path.join(FRONTEND_PATH, "js")), name="ui_js")
        print(f"✓ UI frontend files mounted from {FRONTEND_PATH}")
    except Exception as e:
        print(f"Warning: Could not mount UI frontend files: {e}")

# Root endpoint - redirect to UI
@app.get("/")
async def root():
    return RedirectResponse(url="/ui")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CFR UI Authentication"}

# Serve the login page
@app.get("/ui")
async def serve_ui():
    """Serve the login page"""
    login_path = os.path.join(FRONTEND_PATH, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"error": "UI not found. Please check folder structure."}

# Serve dashboard
@app.get("/ui/dashboard")
async def serve_dashboard():
    """Serve the user dashboard"""
    dashboard_path = os.path.join(FRONTEND_PATH, "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path)
    return RedirectResponse(url="/ui")

# Serve admin panel
@app.get("/ui/admin")
async def serve_admin():
    """Serve the admin panel"""
    admin_path = os.path.join(FRONTEND_PATH, "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path)
    return RedirectResponse(url="/ui")


if __name__ == "__main__":
    import uvicorn

    print("\n")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║         CFR UI - Authentication System Starting...           ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print("🚀 Server starting on http://localhost:8001")
    print("📊 UI available at http://localhost:8001/ui")
    print()
    print("Default Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print()
    print("Press CTRL+C to stop the server")
    print("═" * 65)
    print()

    uvicorn.run(
        "app:app",  # Changed from app to "app:app" string for reload to work
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
