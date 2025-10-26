#!/usr/bin/env python3
"""
Test script to verify unified auth page signup and login flow
"""
import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
TEST_EMAIL = f"{TEST_USERNAME}@example.com"
TEST_PASSWORD = "SecureP@ss123"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_signup():
    """Test user signup functionality"""
    print_section("TEST 1: User Signup")
    
    url = f"{BASE_URL}/auth/signup"
    payload = {
        "username": TEST_USERNAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "role": "user"
    }
    
    print(f"📤 Signing up user: {TEST_USERNAME}")
    print(f"   Email: {TEST_EMAIL}")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ SIGNUP SUCCESSFUL!")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   Active: {user_data.get('is_active')}")
            return True, user_data
        else:
            print(f"❌ SIGNUP FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False, None
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False, None

def test_login(username, password):
    """Test user login functionality"""
    print_section("TEST 2: User Login")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": username,
        "password": password
    }
    
    print(f"🔐 Logging in with username: {username}")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            login_data = response.json()
            print("✅ LOGIN SUCCESSFUL!")
            print(f"   Access Token: {login_data.get('access_token')[:50]}...")
            print(f"   Token Type: {login_data.get('token_type')}")
            print(f"   User ID: {login_data.get('user', {}).get('id')}")
            print(f"   Username: {login_data.get('user', {}).get('username')}")
            print(f"   Email: {login_data.get('user', {}).get('email')}")
            print(f"   Role: {login_data.get('user', {}).get('role')}")
            return True, login_data
        else:
            print(f"❌ LOGIN FAILED!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False, None
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False, None

def test_get_current_user(token):
    """Test getting current user info with token"""
    print_section("TEST 3: Get Current User Info")
    
    url = f"{BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    print("👤 Fetching current user information...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ USER INFO RETRIEVED SUCCESSFULLY!")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
            print(f"   Email: {user_data.get('email')}")
            print(f"   Role: {user_data.get('role')}")
            print(f"   Active: {user_data.get('is_active')}")
            print(f"   Created At: {user_data.get('created_at')}")
            print(f"   Last Login: {user_data.get('last_login')}")
            return True, user_data
        else:
            print(f"❌ FAILED TO GET USER INFO!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error: {response.json().get('detail', 'Unknown error')}")
            return False, None
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False, None

def test_wrong_password():
    """Test login with wrong password"""
    print_section("TEST 4: Login with Wrong Password")
    
    url = f"{BASE_URL}/auth/login"
    payload = {
        "username": TEST_USERNAME,
        "password": "WrongPassword123!"
    }
    
    print(f"🔐 Attempting login with wrong password...")
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 401:
            print("✅ CORRECTLY REJECTED WRONG PASSWORD!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Error Message: {response.json().get('detail', 'Unknown error')}")
            return True
        else:
            print(f"❌ SECURITY ISSUE: Wrong password accepted!")
            return False
            
    except Exception as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  UNIFIED AUTH PAGE - COMPREHENSIVE TEST SUITE")
    print("="*60)
    print(f"Testing against: {BASE_URL}")
    print(f"Test User: {TEST_USERNAME}")
    print(f"Test Email: {TEST_EMAIL}")
    
    results = {
        "signup": False,
        "login": False,
        "get_user": False,
        "wrong_password": False
    }
    
    # Test 1: Signup
    signup_success, signup_data = test_signup()
    results["signup"] = signup_success
    
    if not signup_success:
        print("\n⚠️ Signup failed - cannot continue with login tests")
        print_summary(results)
        return
    
    # Test 2: Login
    login_success, login_data = test_login(TEST_USERNAME, TEST_PASSWORD)
    results["login"] = login_success
    
    if not login_success:
        print("\n⚠️ Login failed - cannot continue with token tests")
        print_summary(results)
        return
    
    # Test 3: Get current user
    token = login_data.get("access_token")
    get_user_success, user_data = test_get_current_user(token)
    results["get_user"] = get_user_success
    
    # Test 4: Wrong password
    wrong_pass_success = test_wrong_password()
    results["wrong_password"] = wrong_pass_success
    
    # Print summary
    print_summary(results)

def print_summary(results):
    """Print test summary"""
    print_section("TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\n📊 Results:")
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"   {status}  {test_name.replace('_', ' ').title()}")
    
    print(f"\n{'='*60}")
    print(f"  Total Tests: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Success Rate: {(passed/total*100):.1f}%")
    print('='*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Authentication flow is working correctly.")
        print("✅ Signup stores data properly")
        print("✅ Login validates credentials correctly")
        print("✅ JWT tokens work as expected")
        print("✅ Security checks are in place")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Please review the errors above.")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(1)
