#!/usr/bin/env python3
"""
Authentication Setup Script
- Creates database tables for User and AuditLog
- Seeds initial admin user
- Verifies setup
"""

import sys
from pathlib import Path
import os

# Add UI backend to path
ui_root = Path(__file__).parent.parent
sys.path.insert(0, str(ui_root))

# Change to UI directory
os.chdir(str(ui_root))

from sqlalchemy import create_engine, inspect
from backend.database import Base, get_db, engine
from backend.auth_models import User, UserRole, AuditLog
from backend.auth_service import get_password_hash


def create_tables():
    """Create authentication tables in the database"""
    print("=" * 60)
    print("Creating authentication tables...")
    print("=" * 60)

    try:
        # Create tables
        Base.metadata.create_all(bind=engine)

        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'users' in tables and 'audit_logs' in tables:
            print("✓ Tables created successfully:")
            print("  - users")
            print("  - audit_logs")
        else:
            print("⚠ Warning: Some tables may not have been created")

        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def seed_admin_user():
    """Create initial admin user"""
    print("\n" + "=" * 60)
    print("Seeding initial admin user...")
    print("=" * 60)

    try:
        # Get database session
        db = next(get_db())

        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()

        if existing_admin:
            print("⚠ Admin user already exists")
            print(f"  Username: {existing_admin.username}")
            print(f"  Email: {existing_admin.email}")
            print(f"  Role: {existing_admin.role.value}")
            return True

        # Create admin user
        admin_password = "admin123"  # Default password
        hashed_password = get_password_hash(admin_password)

        admin_user = User(
            username="admin",
            email="admin@cfrapp.com",
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("✓ Admin user created successfully:")
        print(f"  Username: admin")
        print(f"  Email: admin@cfrapp.com")
        print(f"  Password: {admin_password}")
        print(f"  Role: admin")
        print("\n⚠ IMPORTANT: Change the admin password after first login!")

        db.close()
        return True
    except Exception as e:
        print(f"✗ Error seeding admin user: {e}")
        return False


def verify_setup():
    """Verify the authentication setup"""
    print("\n" + "=" * 60)
    print("Verifying setup...")
    print("=" * 60)

    try:
        # Check tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'users' not in tables:
            print("✗ Users table not found")
            return False

        if 'audit_logs' not in tables:
            print("✗ Audit logs table not found")
            return False

        print("✓ Database tables verified")

        # Check admin user
        db = next(get_db())
        admin = db.query(User).filter(User.username == "admin").first()

        if not admin:
            print("✗ Admin user not found")
            db.close()
            return False

        print("✓ Admin user verified")

        # Get user count
        user_count = db.query(User).count()
        print(f"✓ Total users in database: {user_count}")

        db.close()
        return True
    except Exception as e:
        print(f"✗ Verification error: {e}")
        return False


def main():
    """Main setup function"""
    print("\n")
    print("╔═════════════════════════════════════════════════════════════╗")
    print("║                                                             ║")
    print("║           CFR Agentic AI - Authentication Setup            ║")
    print("║                                                             ║")
    print("╚═════════════════════════════════════════════════════════════╝")
    print("\n")

    # Step 1: Create tables
    if not create_tables():
        print("\n✗ Setup failed at table creation step")
        sys.exit(1)

    # Step 2: Seed admin user
    if not seed_admin_user():
        print("\n✗ Setup failed at admin user creation step")
        sys.exit(1)

    # Step 3: Verify setup
    if not verify_setup():
        print("\n✗ Setup verification failed")
        sys.exit(1)

    # Success message
    print("\n" + "=" * 60)
    print("✓ SETUP COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the application: python run.py")
    print("2. Open your browser to: http://localhost:8000/ui")
    print("3. Login with:")
    print("   Username: admin")
    print("   Password: admin123")
    print("4. Change the admin password immediately")
    print("\n")


if __name__ == "__main__":
    main()
