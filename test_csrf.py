#!/usr/bin/env python3
"""
Simple test script to verify CSRF token functionality
"""
import requests
from bs4 import BeautifulSoup
import sys

def test_csrf_protection():
    """Test that CSRF tokens are properly generated and accepted"""
    base_url = "http://127.0.0.1:5000"
    
    print("Testing CSRF token functionality...")
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    try:
        # Test 1: Check if home page loads
        print("1. Testing home page...")
        response = session.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Home page loads successfully")
        else:
            print(f"✗ Home page failed with status {response.status_code}")
            return False
            
        # Test 2: Check if login page loads and has CSRF token
        print("2. Testing login page...")
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            print("✓ Login page loads successfully")
            
            # Parse the HTML to check for CSRF token
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                print("✓ CSRF token found in login form")
            else:
                print("✗ CSRF token missing from login form")
                return False
        else:
            print(f"✗ Login page failed with status {response.status_code}")
            return False
            
        # Test 3: Test form submission without authentication (should work for login)
        print("3. Testing form submission...")
        
        # Try to submit login form with invalid credentials but valid CSRF
        csrf_token = csrf_input.get('value')
        login_data = {
            'csrf_token': csrf_token,
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = session.post(f"{base_url}/login", data=login_data)
        
        # We expect this to fail with authentication error, not CSRF error
        if response.status_code in [200, 302]:  # 200 = form errors shown, 302 = redirect
            print("✓ Form submission accepted (CSRF token working)")
            
            # Check if we got a proper error message instead of CSRF error
            if response.status_code == 200:
                if "Invalid email or password" in response.text or "csrf" not in response.text.lower():
                    print("✓ Got expected authentication error (not CSRF error)")
                else:
                    print("? Unexpected response content")
            else:
                print("✓ Form redirected (likely successful or authentication required)")
                
        else:
            print(f"✗ Form submission failed with status {response.status_code}")
            if "csrf" in response.text.lower():
                print("✗ CSRF error detected")
                return False
                
        print("\n✓ All CSRF tests passed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to Flask application")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_csrf_protection()
    sys.exit(0 if success else 1)
