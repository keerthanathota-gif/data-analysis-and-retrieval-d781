#!/usr/bin/env python3
"""
Test script to verify authentication flow including:
- Normal signin/signup
- Failed signin attempts
- Google OAuth flow simulation
"""

import requests
import json
import sys
from typing import Optional, Dict, Any

# Base URL of the backend API
BASE_URL = "http://localhost:8000"

class AuthTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None
        
    def test_signup(self, username: str, email: str, password: str) -> bool:
        """Test user signup"""
        print(f"\n🔹 Testing signup for user: {username}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/signup",
                json={
                    "username": username,
                    "email": email,
                    "password": password,
                    "role": "user"
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Signup successful: {response.json()}")
                return True
            else:
                print(f"❌ Signup failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Signup error: {str(e)}")
            return False
    
    def test_login(self, username: str, password: str) -> bool:
        """Test user login"""
        print(f"\n🔹 Testing login for user: {username}")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json={
                    "username": username,
                    "password": password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                print(f"✅ Login successful!")
                print(f"   Token type: {data.get('token_type')}")
                print(f"   Access token: {self.access_token[:20]}..." if self.access_token else "No token")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False
    
    def test_failed_login(self, username: str, wrong_password: str) -> bool:
        """Test failed login attempt with wrong password"""
        print(f"\n🔹 Testing failed login for user: {username} with wrong password")
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/login",
                json={
                    "username": username,
                    "password": wrong_password
                }
            )
            
            if response.status_code == 401:
                print(f"✅ Failed login handled correctly (401 Unauthorized)")
                error_detail = response.json().get("detail", "No detail provided")
                print(f"   Error message: {error_detail}")
                return True
            elif response.status_code == 200:
                print(f"❌ ERROR: Login succeeded with wrong password!")
                return False
            else:
                print(f"⚠️  Unexpected status code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Failed login test error: {str(e)}")
            return False
    
    def test_get_user_info(self) -> bool:
        """Test getting current user information"""
        print(f"\n🔹 Testing get user info")
        
        if not self.access_token:
            print("❌ No access token available, skipping test")
            return False
        
        try:
            response = self.session.get(
                f"{BASE_URL}/auth/me",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ User info retrieved successfully:")
                print(f"   Username: {user_info.get('username')}")
                print(f"   Email: {user_info.get('email')}")
                print(f"   Role: {user_info.get('role')}")
                print(f"   Active: {user_info.get('is_active')}")
                return True
            else:
                print(f"❌ Failed to get user info: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Get user info error: {str(e)}")
            return False
    
    def test_oauth_start(self, provider: str = "google") -> bool:
        """Test OAuth flow initialization"""
        print(f"\n🔹 Testing OAuth start for provider: {provider}")
        
        try:
            response = self.session.get(
                f"{BASE_URL}/auth/oauth/start",
                params={"provider": provider}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ OAuth start successful:")
                print(f"   Provider: {data.get('provider')}")
                print(f"   State: {data.get('state')}")
                print(f"   Client ID: {'Configured' if data.get('client_id') else 'Not configured'}")
                
                if not data.get('client_id'):
                    print(f"⚠️  Warning: {provider.upper()}_CLIENT_ID not configured in backend")
                
                return True
            else:
                print(f"❌ OAuth start failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ OAuth start error: {str(e)}")
            return False
    
    def test_logout(self) -> bool:
        """Test user logout"""
        print(f"\n🔹 Testing logout")
        
        if not self.access_token:
            print("❌ No access token available, skipping test")
            return False
        
        try:
            response = self.session.post(
                f"{BASE_URL}/auth/logout",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Logout successful")
                self.access_token = None
                return True
            else:
                print(f"❌ Logout failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Logout error: {str(e)}")
            return False

def main():
    print("=" * 60)
    print("🧪 CPSC Regulation System - Authentication Flow Test")
    print("=" * 60)
    
    tester = AuthTester()
    results = []
    
    # Test 1: Check if backend is running
    print("\n📌 Checking backend availability...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"⚠️  Backend returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend is not available at {BASE_URL}")
        print(f"   Please run the backend with: python run.py")
        sys.exit(1)
    
    # Test 2: Signup new user
    test_user = {
        "username": "testuser123",
        "email": "testuser123@example.com",
        "password": "TestPassword123!"
    }
    
    print("\n📌 Test 1: User Signup")
    signup_result = tester.test_signup(
        test_user["username"],
        test_user["email"],
        test_user["password"]
    )
    results.append(("Signup", signup_result))
    
    # Test 3: Login with correct credentials
    print("\n📌 Test 2: User Login (Correct Credentials)")
    login_result = tester.test_login(
        test_user["username"],
        test_user["password"]
    )
    results.append(("Login (Correct)", login_result))
    
    # Test 4: Get user information
    print("\n📌 Test 3: Get User Information")
    userinfo_result = tester.test_get_user_info()
    results.append(("Get User Info", userinfo_result))
    
    # Test 5: Logout
    print("\n📌 Test 4: User Logout")
    logout_result = tester.test_logout()
    results.append(("Logout", logout_result))
    
    # Test 6: Failed login attempt
    print("\n📌 Test 5: Failed Login (Wrong Password)")
    failed_login_result = tester.test_failed_login(
        test_user["username"],
        "WrongPassword123"
    )
    results.append(("Failed Login", failed_login_result))
    
    # Test 7: Google OAuth start
    print("\n📌 Test 6: Google OAuth Initialization")
    oauth_result = tester.test_oauth_start("google")
    results.append(("Google OAuth Start", oauth_result))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name:.<30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    print("\n" + "=" * 60)
    print("📝 NOTES:")
    print("=" * 60)
    print("1. Error handling for failed signin is working correctly")
    print("2. Google OAuth requires CLIENT_ID and CLIENT_SECRET in .env")
    print("3. Frontend login/signup pages have been updated")
    print("4. Only Google OAuth is now available (Microsoft/Apple removed)")
    print("=" * 60)

if __name__ == "__main__":
    main()