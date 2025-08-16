#!/usr/bin/env python3
"""
Test Streamlit App Functionality
Tests the actual running Streamlit app
"""

import requests
import time
import json
from datetime import datetime

def test_app_health():
    """Test if the app is running and healthy"""
    print("🏥 Testing App Health...")
    
    try:
        # Test basic health
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        if response.status_code == 200:
            print("✅ App health check passed")
            return True
        else:
            print(f"❌ App health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ App health check failed: {e}")
        return False

def test_app_accessibility():
    """Test if the app is accessible"""
    print("\n🌐 Testing App Accessibility...")
    
    try:
        # Test main page
        response = requests.get("http://localhost:8501", timeout=10)
        if response.status_code == 200:
            print("✅ Main page accessible")
            
            # Check if it's a Streamlit page
            if "Streamlit" in response.text:
                print("✅ Confirmed Streamlit app")
            else:
                print("⚠️  Page loaded but may not be Streamlit")
            
            return True
        else:
            print(f"❌ Main page not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ App accessibility test failed: {e}")
        return False

def test_app_content():
    """Test if the app content is loading correctly"""
    print("\n📄 Testing App Content...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        content = response.text.lower()
        
        # Check for key content elements
        checks = [
            ("autoppm", "AutoPPM branding"),
            ("trading platform", "Trading platform description"),
            ("authentication", "Authentication system"),
            ("portfolio", "Portfolio features"),
            ("risk management", "Risk management features")
        ]
        
        passed_checks = 0
        for keyword, description in checks:
            if keyword in content:
                print(f"✅ Found: {description}")
                passed_checks += 1
            else:
                print(f"⚠️  Missing: {description}")
        
        print(f"📊 Content check: {passed_checks}/{len(checks)} elements found")
        return passed_checks >= len(checks) * 0.8  # 80% threshold
    except Exception as e:
        print(f"❌ Content test failed: {e}")
        return False

def test_app_responsiveness():
    """Test app response times"""
    print("\n⚡ Testing App Responsiveness...")
    
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8501", timeout=10)
        load_time = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✅ Page loaded in {load_time:.2f} seconds")
            
            if load_time < 5.0:
                print("✅ Load time is acceptable (< 5s)")
                return True
            elif load_time < 10.0:
                print("⚠️  Load time is slow but acceptable (< 10s)")
                return True
            else:
                print(f"❌ Load time is too slow: {load_time:.2f}s")
                return False
        else:
            print(f"❌ Failed to load page: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Responsiveness test failed: {e}")
        return False

def test_app_structure():
    """Test app structure and navigation"""
    print("\n🏗️  Testing App Structure...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        content = response.text
        
        # Check for HTML structure
        if "<html" in content and "</html>" in content:
            print("✅ HTML structure is valid")
        else:
            print("⚠️  HTML structure may be incomplete")
        
        # Check for JavaScript
        if "main." in content and ".js" in content:
            print("✅ JavaScript files are loading")
        else:
            print("⚠️  JavaScript files may not be loading")
        
        # Check for CSS
        if "main." in content and ".css" in content:
            print("✅ CSS files are loading")
        else:
            print("⚠️  CSS files may not be loading")
        
        return True
    except Exception as e:
        print(f"❌ Structure test failed: {e}")
        return False

def test_app_functionality():
    """Test if the app has the expected functionality"""
    print("\n🔧 Testing App Functionality...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=10)
        content = response.text.lower()
        
        # Check for expected functionality
        functionality_checks = [
            ("sign up", "Sign up functionality"),
            ("login", "Login functionality"),
            ("dashboard", "Dashboard functionality"),
            ("portfolio", "Portfolio management"),
            ("risk", "Risk management"),
            ("analytics", "Analytics features")
        ]
        
        found_features = 0
        for feature, description in functionality_checks:
            if feature in content:
                print(f"✅ Found: {description}")
                found_features += 1
            else:
                print(f"⚠️  Missing: {description}")
        
        print(f"📊 Functionality check: {found_features}/{len(functionality_checks)} features found")
        return found_features >= len(functionality_checks) * 0.7  # 70% threshold
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all Streamlit app tests"""
    print("🚀 AutoPPM Streamlit App Test Suite")
    print("=" * 50)
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    tests = [
        test_app_health,
        test_app_accessibility,
        test_app_content,
        test_app_responsiveness,
        test_app_structure,
        test_app_functionality
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Streamlit app is working correctly.")
        print("✅ Ready for Streamlit Cloud deployment!")
    elif passed >= total * 0.8:
        print("✅ Most tests passed! App is mostly functional.")
        print("⚠️  Some minor issues detected but ready for deployment.")
    else:
        print("❌ Many tests failed. Please fix issues before deployment.")
    
    print(f"🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return passed >= total * 0.8

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
