#!/usr/bin/env python3
"""
Main entry point for CPSC Regulation System Backend
"""

import uvicorn
from app.config import API_HOST, API_PORT

if __name__ == "__main__":
    print("🚀 Starting CPSC Regulation System Backend...")
    print(f"📡 Server will be available at: http://{API_HOST}:{API_PORT}")
    print(f"📚 API Documentation: http://{API_HOST}:{API_PORT}/api/docs")
    print(f"🎨 Frontend: http://{API_HOST}:{API_PORT}/ui")
    print("\n" + "="*50)
    
    uvicorn.run(
        "app.main:app",  # Use import string instead of direct app reference
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )