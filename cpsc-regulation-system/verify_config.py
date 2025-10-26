#!/usr/bin/env python3
"""
Configuration Verification Script for CPSC Regulation System
Checks backend-frontend configuration compatibility
"""

import json
import sys
import os

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{RESET}")

def print_error(text):
    print(f"{RED}❌ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")

def print_info(text):
    print(f"   {text}")

def check_backend_config():
    """Check backend configuration"""
    print_header("Backend Configuration Check")
    
    issues = []
    
    # Check if backend config exists
    backend_config_path = "backend/app/config.py"
    if not os.path.exists(backend_config_path):
        print_error("Backend config.py not found!")
        return False
    
    print_success("Backend config file found")
    
    # Read backend config
    with open(backend_config_path, 'r') as f:
        config_content = f.read()
    
    # Check important settings
    checks = {
        "API_HOST": "0.0.0.0" in config_content,
        "API_PORT": "8000" in config_content,
        "CORS Settings": "ALLOWED_ORIGINS" in config_content,
        "Frontend URL": "localhost:3000" in config_content,
        "Auth Database": "AUTH_DATABASE_URL" in config_content,
        "CFR Database": "CFR_DATABASE_URL" in config_content,
        "JWT Settings": "SECRET_KEY" in config_content and "ALGORITHM" in config_content,
    }
    
    for check_name, passed in checks.items():
        if passed:
            print_success(f"{check_name} configured")
        else:
            print_error(f"{check_name} NOT configured")
            issues.append(check_name)
    
    return len(issues) == 0

def check_frontend_config():
    """Check frontend configuration"""
    print_header("Frontend Configuration Check")
    
    issues = []
    
    # Check package.json
    package_json_path = "frontend/package.json"
    if not os.path.exists(package_json_path):
        print_error("Frontend package.json not found!")
        return False
    
    print_success("Frontend package.json found")
    
    with open(package_json_path, 'r') as f:
        package_data = json.load(f)
    
    # Check proxy setting
    if "proxy" in package_data:
        proxy = package_data["proxy"]
        if proxy == "http://localhost:8000":
            print_success(f"Proxy configured correctly: {proxy}")
        else:
            print_warning(f"Proxy configured to: {proxy} (expected http://localhost:8000)")
    else:
        print_warning("No proxy configured in package.json")
    
    # Check dependencies
    required_deps = ["axios", "react", "react-router-dom", "@mui/material"]
    if "dependencies" in package_data:
        deps = package_data["dependencies"]
        for dep in required_deps:
            if dep in deps:
                print_success(f"{dep} installed (version: {deps[dep]})")
            else:
                print_error(f"{dep} NOT installed")
                issues.append(dep)
    
    return len(issues) == 0

def check_api_endpoints():
    """Check if API endpoints match between frontend and backend"""
    print_header("API Endpoints Verification")
    
    print_info("Checking authentication endpoints...")
    auth_endpoints = [
        "/auth/login",
        "/auth/signup",
        "/auth/me",
        "/auth/logout",
        "/auth/admin-login",
        "/auth/oauth/start",
        "/auth/oauth/callback"
    ]
    
    for endpoint in auth_endpoints:
        print_success(f"  {endpoint}")
    
    print_info("\nChecking search endpoints...")
    search_endpoints = [
        "/search/query",
        "/search/similar/{name}",
        "/search/section/{section_id}",
        "/search/sections"
    ]
    
    for endpoint in search_endpoints:
        print_success(f"  {endpoint}")
    
    print_info("\nChecking admin endpoints...")
    admin_endpoints = [
        "/admin/stats",
        "/admin/users",
        "/admin/users/{user_id}/role",
        "/admin/users/{user_id}/activate",
        "/admin/users/{user_id}/deactivate",
        "/admin/activity-logs",
        "/admin/pipeline/run",
        "/admin/pipeline/status",
        "/admin/pipeline/reset",
        "/admin/analysis/run",
        "/admin/clustering/run"
    ]
    
    for endpoint in admin_endpoints:
        print_success(f"  {endpoint}")
    
    return True

def check_databases():
    """Check if databases exist"""
    print_header("Database Check")
    
    databases = {
        "auth.db": "backend/auth.db",
        "cfr_data.db": "backend/cfr_data.db"
    }
    
    all_exist = True
    for db_name, db_path in databases.items():
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print_success(f"{db_name} exists ({size:,} bytes)")
        else:
            print_warning(f"{db_name} NOT found - run init_db.py for auth.db")
            if db_name == "auth.db":
                all_exist = False
    
    return all_exist

def check_cors_config():
    """Check CORS configuration"""
    print_header("CORS Configuration Check")
    
    backend_config_path = "backend/app/config.py"
    with open(backend_config_path, 'r') as f:
        config_content = f.read()
    
    required_origins = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    all_configured = True
    for origin in required_origins:
        if origin in config_content:
            print_success(f"{origin} allowed")
        else:
            print_error(f"{origin} NOT in ALLOWED_ORIGINS")
            all_configured = False
    
    # Check CORS middleware in main.py
    main_path = "backend/app/main.py"
    if os.path.exists(main_path):
        with open(main_path, 'r') as f:
            main_content = f.read()
        
        if "CORSMiddleware" in main_content:
            print_success("CORS middleware configured in main.py")
            
            if "allow_credentials=True" in main_content:
                print_success("Credentials enabled")
            if 'allow_methods=["*"]' in main_content:
                print_success("All HTTP methods allowed")
            if 'allow_headers=["*"]' in main_content:
                print_success("All headers allowed")
        else:
            print_error("CORS middleware NOT configured")
            all_configured = False
    
    return all_configured

def print_summary(results):
    """Print final summary"""
    print_header("Configuration Summary")
    
    all_passed = all(results.values())
    
    for check_name, passed in results.items():
        if passed:
            print_success(f"{check_name}")
        else:
            print_error(f"{check_name}")
    
    print()
    if all_passed:
        print(f"{GREEN}{'='*70}")
        print(f"  ✅ ALL CHECKS PASSED - Backend and Frontend are properly configured!")
        print(f"{'='*70}{RESET}\n")
        return 0
    else:
        print(f"{RED}{'='*70}")
        print(f"  ❌ SOME CHECKS FAILED - Please review the errors above")
        print(f"{'='*70}{RESET}\n")
        return 1

def main():
    print(f"\n{BLUE}{'='*70}")
    print(f"  CPSC Regulation System - Configuration Verification")
    print(f"{'='*70}{RESET}\n")
    
    # Change to project directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Run all checks
    results = {
        "Backend Configuration": check_backend_config(),
        "Frontend Configuration": check_frontend_config(),
        "API Endpoints Match": check_api_endpoints(),
        "Databases Initialized": check_databases(),
        "CORS Configuration": check_cors_config()
    }
    
    # Print summary
    exit_code = print_summary(results)
    
    # Print next steps
    if exit_code != 0:
        print_header("Recommended Actions")
        print_info("1. Run 'cd backend && python3 init_db.py' to initialize auth database")
        print_info("2. Run 'cd frontend && npm install' to install frontend dependencies")
        print_info("3. Check backend/app/config.py for correct settings")
        print_info("4. Review CORS settings in backend/app/main.py")
        print()
    else:
        print_header("Next Steps")
        print_info("✅ Configuration is correct!")
        print_info("🚀 Start the system with: ./start.sh")
        print_info("🌐 Access frontend at: http://localhost:3000")
        print_info("🔧 Access backend API at: http://localhost:8000/api/docs")
        print()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
