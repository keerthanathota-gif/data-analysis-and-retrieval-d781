#!/usr/bin/env python3
"""
Initialize the authentication database for CPSC Regulation System
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.auth_database import init_auth_db, create_default_admin

if __name__ == "__main__":
    print("🔧 Initializing Authentication Database...")
    print("=" * 50)
    
    try:
        # Initialize database and create tables
        init_auth_db()
        
        # Create default admin user
        create_default_admin()
        
        print("\n✅ Database initialization completed successfully!")
        print("\n📝 Default Admin Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  Please change the admin password after first login!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
