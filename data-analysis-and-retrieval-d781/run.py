#!/usr/bin/env python3
"""
Main entry point for CFR Agentic AI Application
Run this file to start the application
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.config import API_HOST, API_PORT
    
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                                                               ║")
    print("║         CFR Agentic AI Application Starting...               ║")
    print("║                                                               ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()
    print(f"🚀 Server will start on http://{API_HOST}:{API_PORT}")
    print(f"📊 UI available at http://localhost:{API_PORT}/ui")
    print()
    print("Press CTRL+C to stop the server")
    print("═" * 65)
    print()
    
    uvicorn.run(
        "app.main:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
        log_level="info"
    )
