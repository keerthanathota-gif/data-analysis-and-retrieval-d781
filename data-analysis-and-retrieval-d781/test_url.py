#!/usr/bin/env python3
"""
Test URL parsing and validation for CFR data
Tests with: https://www.govinfo.gov/bulkdata/CFR/2024/title-4
"""

import re

def test_url_parsing(target_url_base):
    """Test if URL can be parsed correctly"""
    print("\n" + "="*60)
    print(f"Testing URL: {target_url_base}")
    print("="*60)
    
    # Parse URL parts
    url_parts = [part for part in target_url_base.split('/') if part]
    
    print(f"\nURL parts: {url_parts}")
    
    if len(url_parts) < 2:
        print("❌ URL too short - need at least year and title")
        return False
    
    # Extract year and title
    year = url_parts[-2] if len(url_parts) >= 2 else None
    title_part = url_parts[-1] if len(url_parts) >= 1 else None
    
    print(f"Year: {year}")
    print(f"Title part: {title_part}")
    
    # Validate year
    if year and re.match(r'^\d{4}$', year):
        print(f"✅ Year '{year}' is valid")
    else:
        print(f"❌ Year '{year}' is invalid")
        return False
    
    # Validate title format
    if title_part and re.match(r'^title-\d+$', title_part):
        print(f"✅ Title '{title_part}' is valid format")
    else:
        print(f"❌ Title '{title_part}' should be format: title-NUMBER")
        return False
    
    # Construct expected ZIP filename
    zip_filename = f"CFR-{year}-{title_part}.zip"
    full_zip_url = f"https://www.govinfo.gov/bulkdata/CFR/{year}/{title_part}/{zip_filename}"
    
    print(f"\n📦 Expected ZIP filename: {zip_filename}")
    print(f"🔗 Full ZIP URL: {full_zip_url}")
    
    return True, full_zip_url

def test_url_accessibility(url):
    """Test if URL is accessible (requires requests library)"""
    try:
        import requests
        print(f"\n🔍 Testing URL accessibility...")
        
        # HEAD request to check if file exists
        response = requests.head(url, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            print(f"✅ URL is accessible!")
            if 'content-length' in response.headers:
                size_mb = int(response.headers['content-length']) / (1024 * 1024)
                print(f"📊 File size: {size_mb:.2f} MB")
            return True
        else:
            print(f"⚠️  URL returned status code: {response.status_code}")
            return False
            
    except ImportError:
        print("⚠️  'requests' library not installed - skipping accessibility test")
        print("   Install with: pip install requests")
        return None
    except Exception as e:
        print(f"❌ Error checking URL: {e}")
        return False

def main():
    """Test the provided URL"""
    print("\n╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + " "*10 + "CFR URL Validation Test" + " "*25 + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Test URL
    test_url = "https://www.govinfo.gov/bulkdata/CFR/2024/title-4"
    
    # Parse and validate
    result = test_url_parsing(test_url)
    
    if isinstance(result, tuple):
        valid, zip_url = result
        
        if valid:
            print("\n" + "="*60)
            print("✅ URL VALIDATION: PASSED")
            print("="*60)
            
            # Try to check accessibility
            accessible = test_url_accessibility(zip_url)
            
            print("\n" + "="*60)
            print("📋 SUMMARY")
            print("="*60)
            print(f"Input URL: {test_url}")
            print(f"ZIP URL: {zip_url}")
            print(f"URL Format: ✅ Valid")
            
            if accessible is True:
                print(f"Accessibility: ✅ File exists and is downloadable")
            elif accessible is False:
                print(f"Accessibility: ❌ File not found or not accessible")
            else:
                print(f"Accessibility: ⚠️  Could not verify (install requests)")
            
            print("\n" + "="*60)
            print("🚀 NEXT STEPS")
            print("="*60)
            print("1. Start the application:")
            print("   python run.py")
            print("")
            print("2. Open browser:")
            print("   http://localhost:8000/ui")
            print("")
            print("3. In Pipeline tab, enter URL:")
            print(f"   {test_url}")
            print("")
            print("4. Click 'Run Complete Pipeline'")
            print("")
            print("5. Watch progress bar update!")
            print("="*60)
        else:
            print("\n❌ URL VALIDATION: FAILED")
            print("Please check the URL format")
    else:
        print("\n❌ URL VALIDATION: FAILED")

if __name__ == "__main__":
    main()
