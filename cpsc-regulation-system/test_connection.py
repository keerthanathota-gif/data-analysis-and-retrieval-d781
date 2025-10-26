#!/usr/bin/env python3
"""
Test script to verify backend API and frontend connection
"""
import requests
import sys
import time

def test_backend_health():
    """Test if backend is running and healthy"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is running and healthy")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible at http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        return False

def test_cors_headers():
    """Test if CORS is properly configured"""
    try:
        response = requests.options('http://localhost:8000/search/stats', 
                                     headers={'Origin': 'http://localhost:3000'},
                                     timeout=5)
        cors_header = response.headers.get('Access-Control-Allow-Origin')
        if cors_header:
            print(f"✅ CORS is configured: {cors_header}")
            return True
        else:
            print("⚠️  CORS headers not found (may cause frontend issues)")
            return False
    except Exception as e:
        print(f"⚠️  Could not test CORS: {e}")
        return False

def test_database_stats():
    """Test if database endpoints are working"""
    try:
        response = requests.get('http://localhost:8000/search/stats', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Database stats endpoint working")
            print(f"   - Chapters: {data.get('total_chapters', 0)}")
            print(f"   - Sections: {data.get('total_sections', 0)}")
            print(f"   - Embeddings: {data.get('total_embeddings', 0)}")
            return True
        else:
            print(f"❌ Database stats endpoint returned: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing database: {e}")
        return False

def main():
    print("🔍 Testing CFR Pipeline System Backend Connection\n")
    print("=" * 60)
    
    # Test backend
    print("\n📡 Testing Backend API...")
    backend_ok = test_backend_health()
    
    if not backend_ok:
        print("\n⚠️  Backend is not running!")
        print("   Start it with: cd backend && python run.py")
        sys.exit(1)
    
    # Test CORS
    print("\n🌐 Testing CORS Configuration...")
    test_cors_headers()
    
    # Test database
    print("\n💾 Testing Database Endpoints...")
    test_database_stats()
    
    print("\n" + "=" * 60)
    print("✅ Connection tests completed!")
    print("\n📝 Frontend Configuration:")
    print("   - API URL: http://localhost:8000")
    print("   - Frontend URL: http://localhost:3000")
    print("\n🚀 To start frontend: cd frontend && npm start")

if __name__ == "__main__":
    main()
