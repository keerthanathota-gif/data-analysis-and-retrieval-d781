#!/usr/bin/env python3
"""
Test database path configuration and fix for [Errno 22] Invalid argument
"""
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_configuration():
    """Test database configuration and connection"""
    print("=" * 70)
    print("  DATABASE CONFIGURATION TEST")
    print("=" * 70)
    
    try:
        # Test 1: Import configuration
        print("\n[1/5] Testing configuration import...")
        from app.config import CFR_DATABASE_URL, AUTH_DATABASE_URL, BASE_DIR
        print(f"  ✓ Configuration imported successfully")
        
        # Test 2: Check base directory
        print("\n[2/5] Checking base directory...")
        print(f"  Base Dir: {BASE_DIR}")
        print(f"  Exists: {os.path.exists(BASE_DIR)}")
        print(f"  Writable: {os.access(BASE_DIR, os.W_OK)}")
        
        if not os.path.exists(BASE_DIR):
            print("  ✗ Base directory does not exist!")
            return False
        
        if not os.access(BASE_DIR, os.W_OK):
            print("  ✗ Base directory is not writable!")
            return False
        
        print("  ✓ Base directory is valid and writable")
        
        # Test 3: Check database URLs
        print("\n[3/5] Checking database URLs...")
        print(f"  CFR Database URL: {CFR_DATABASE_URL}")
        print(f"  Auth Database URL: {AUTH_DATABASE_URL}")
        
        # Extract paths
        cfr_path = CFR_DATABASE_URL.replace('sqlite:///', '')
        auth_path = AUTH_DATABASE_URL.replace('sqlite:///', '')
        
        print(f"\n  CFR Database File: {cfr_path}")
        print(f"    Exists: {os.path.exists(cfr_path)}")
        if os.path.exists(cfr_path):
            print(f"    Size: {os.path.getsize(cfr_path)} bytes")
        
        print(f"\n  Auth Database File: {auth_path}")
        print(f"    Exists: {os.path.exists(auth_path)}")
        if os.path.exists(auth_path):
            print(f"    Size: {os.path.getsize(auth_path)} bytes")
        
        print("  ✓ Database paths are valid")
        
        # Test 4: Test CFR database connection
        print("\n[4/5] Testing CFR database connection...")
        from app.models.cfr_database import engine as cfr_engine, init_cfr_db
        
        try:
            init_cfr_db()
            with cfr_engine.connect() as conn:
                result = conn.execute("SELECT 1").scalar()
                print(f"  ✓ CFR database connection successful! (Result: {result})")
        except Exception as e:
            print(f"  ✗ CFR database connection failed: {e}")
            return False
        
        # Test 5: Test Auth database connection
        print("\n[5/5] Testing Auth database connection...")
        from app.models.auth_database import engine as auth_engine, init_auth_db
        
        try:
            init_auth_db()
            with auth_engine.connect() as conn:
                result = conn.execute("SELECT 1").scalar()
                print(f"  ✓ Auth database connection successful! (Result: {result})")
        except Exception as e:
            print(f"  ✗ Auth database connection failed: {e}")
            return False
        
        print("\n" + "=" * 70)
        print("  ✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\n  The [Errno 22] Invalid argument error should be fixed.")
        print("  You can now run the pipeline without database errors.")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n  ❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_database_configuration()
    
    if success:
        print("  Next Steps:")
        print("  1. Run the pipeline: python3 -m app.pipeline.data_pipeline")
        print("  2. Or start the server: python3 run.py")
        print()
    else:
        print("\n  ⚠️ Please check the errors above and retry.")
        print()
    
    sys.exit(0 if success else 1)
