#!/usr/bin/env python3
"""
Test script for CPSC Regulation System
"""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8000"

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check: PASSED")
            return True
        else:
            print(f"❌ API Health Check: FAILED (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API Health Check: FAILED (Error: {e})")
        return False

def test_auth():
    """Test authentication endpoints"""
    print("\n🔐 Testing Authentication...")
    
    # Test signup
    try:
        signup_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "TestPass123!",
            "role": "user"
        }
        response = requests.post(f"{API_BASE}/auth/signup", json=signup_data)
        if response.status_code == 200:
            print("✅ User Signup: PASSED")
        else:
            print(f"❌ User Signup: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ User Signup: FAILED (Error: {e})")
    
    # Test login
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            print("✅ Admin Login: PASSED")
            token = response.json()["access_token"]
            return token
        else:
            print(f"❌ Admin Login: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Admin Login: FAILED (Error: {e})")
        return None

def test_admin_endpoints(token):
    """Test admin endpoints"""
    if not token:
        print("❌ Skipping admin tests - no token")
        return
    
    print("\n👑 Testing Admin Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test stats
    try:
        response = requests.get(f"{API_BASE}/admin/stats", headers=headers)
        if response.status_code == 200:
            print("✅ Admin Stats: PASSED")
            stats = response.json()
            print(f"   Users: {stats.get('total_users', 0)}")
            print(f"   Sections: {stats.get('total_sections', 0)}")
        else:
            print(f"❌ Admin Stats: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Admin Stats: FAILED (Error: {e})")
    
    # Test users list
    try:
        response = requests.get(f"{API_BASE}/admin/users", headers=headers)
        if response.status_code == 200:
            print("✅ Admin Users List: PASSED")
        else:
            print(f"❌ Admin Users List: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Admin Users List: FAILED (Error: {e})")

def test_search_endpoints(token):
    """Test search endpoints"""
    if not token:
        print("❌ Skipping search tests - no token")
        return
    
    print("\n🔍 Testing Search Endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test search
    try:
        search_data = {
            "query": "safety requirements",
            "level": "all",
            "top_k": 5
        }
        response = requests.post(f"{API_BASE}/search/query", json=search_data, headers=headers)
        if response.status_code == 200:
            print("✅ Search Query: PASSED")
            results = response.json()
            print(f"   Found {len(results.get('results', []))} results")
        else:
            print(f"❌ Search Query: FAILED (Status: {response.status_code})")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Search Query: FAILED (Error: {e})")

def main():
    """Run all tests"""
    print("🧪 CPSC Regulation System Test Suite")
    print("=" * 40)
    
    # Test API health
    if not test_health():
        print("\n❌ API is not running. Please start the backend server first.")
        print("   Run: cd backend && python run.py")
        sys.exit(1)
    
    # Test authentication
    token = test_auth()
    
    # Test admin endpoints
    test_admin_endpoints(token)
    
    # Test search endpoints
    test_search_endpoints(token)
    
    print("\n" + "=" * 40)
    print("🎉 Test suite completed!")
    print("\nTo start the full system:")
    print("   ./start.sh")
    print("\nOr manually:")
    print("   Backend: cd backend && python run.py")
    print("   Frontend: cd frontend && npm start")

if __name__ == "__main__":
    main()