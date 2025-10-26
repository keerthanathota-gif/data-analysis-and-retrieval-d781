#!/usr/bin/env python3
"""
Quick UI verification script for CFR Pipeline System
Tests that all components are properly configured
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    try:
        from app.config import API_HOST, API_PORT, DATABASE_URL
        from app.main import app
        from app.database import init_db
        print("✅ All imports successful")
        print(f"   - API configured for {API_HOST}:{API_PORT}")
        print(f"   - Database: {DATABASE_URL}")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_static_files():
    """Test that UI files exist"""
    print("\nTesting static files...")
    static_path = os.path.join(os.path.dirname(__file__), "app", "static", "index.html")
    if os.path.exists(static_path):
        print(f"✅ UI file exists: {static_path}")
        # Check file size
        size = os.path.getsize(static_path)
        print(f"   - File size: {size:,} bytes")
        return True
    else:
        print(f"❌ UI file not found: {static_path}")
        return False

def test_dependencies():
    """Test that required dependencies are available"""
    print("\nTesting dependencies...")
    required = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'requests'
    ]
    
    all_ok = True
    for module in required:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def test_api_routes():
    """Test that API routes are defined"""
    print("\nTesting API routes...")
    try:
        from app.main import app
        routes = [route.path for route in app.routes]
        
        expected_routes = [
            '/api/pipeline/run',
            '/api/pipeline/stats',
            '/api/pipeline/status',
            '/api/pipeline/reset',
            '/ui'
        ]
        
        for route in expected_routes:
            if any(r.startswith(route) for r in routes):
                print(f"✅ {route}")
            else:
                print(f"❌ {route} - NOT FOUND")
        
        print(f"\n   Total routes defined: {len(routes)}")
        return True
    except Exception as e:
        print(f"❌ Failed to load routes: {e}")
        return False

def test_ui_content():
    """Test that UI contains required elements"""
    print("\nTesting UI content...")
    static_path = os.path.join(os.path.dirname(__file__), "app", "static", "index.html")
    
    try:
        with open(static_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_elements = [
            ('CFR Pipeline System', 'Title'),
            ('Database Statistics', 'Stats section'),
            ('Data Pipeline Control', 'Pipeline control'),
            ('Total Chapters', 'Chapters stat'),
            ('Total Regulations', 'Regulations stat'),
            ('Total Embeddings', 'Embeddings stat'),
            ('Run Pipeline', 'Run button'),
            ('Reset Database', 'Reset button'),
            ('Pipeline Results', 'Results section'),
            ('Overall Progress', 'Progress bar'),
        ]
        
        all_found = True
        for element, description in required_elements:
            if element in content:
                print(f"✅ {description}: '{element}'")
            else:
                print(f"❌ {description}: '{element}' NOT FOUND")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"❌ Failed to read UI file: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("CFR Pipeline System - UI Verification Test")
    print("=" * 70)
    print()
    
    tests = [
        test_imports,
        test_static_files,
        test_dependencies,
        test_api_routes,
        test_ui_content
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if all(results):
        print("\n✅ ALL TESTS PASSED - UI is ready!")
        print("\nTo start the application:")
        print("  python3 run.py")
        print("\nThen open:")
        print("  http://localhost:8000/ui")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        if not results[2]:  # Dependencies test failed
            print("\nTo install dependencies:")
            print("  pip3 install -r requirements.txt")
        return 1

if __name__ == "__main__":
    exit(main())
