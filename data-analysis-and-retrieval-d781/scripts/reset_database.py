#!/usr/bin/env python3
"""
Reset database and clean all data directories
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import reset_db
from app.config import DATA_DIR, OUTPUT_DIR, VISUALIZATIONS_DIR
import shutil

def reset_all():
    """Reset database and remove all data directories"""
    print("⚠️  WARNING: This will delete ALL data!")
    print(f"   - Database: cfr_data.db")
    print(f"   - Data directory: {DATA_DIR}")
    print(f"   - Output directory: {OUTPUT_DIR}")
    print(f"   - Visualizations: {VISUALIZATIONS_DIR}")
    print()
    
    confirm = input("Type 'yes' to continue: ")
    
    if confirm.lower() != 'yes':
        print("❌ Reset cancelled")
        return
    
    print("\n🗑️  Resetting database...")
    try:
        reset_db()
        print("✅ Database reset complete")
    except Exception as e:
        print(f"⚠️  Database reset error: {e}")
    
    # Remove data directories
    for directory in [DATA_DIR, OUTPUT_DIR, VISUALIZATIONS_DIR]:
        if os.path.exists(directory):
            print(f"🗑️  Removing {directory}...")
            try:
                shutil.rmtree(directory)
                print(f"✅ Removed {directory}")
            except Exception as e:
                print(f"⚠️  Error removing {directory}: {e}")
    
    print("\n✅ Reset complete!")
    print("   You can now restart the server with: python run.py")

if __name__ == "__main__":
    reset_all()
