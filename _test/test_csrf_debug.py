#!/usr/bin/env python3
"""
Debug CSRF token functionality for admin approval system
"""

import requests
from bs4 import BeautifulSoup
import json

def test_csrf_debug():
    """Debug CSRF token issues with admin approval"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 CSRF Debug Test - Admin Approval System")
    print("=" * 55)
    
    session = requests.Session()
    
    try:
        # Test 1: Check if admin page is accessible (should redirect to login)
        print("1. Testing admin page access...")
        response = session.get(f"{base_url}/admin/pending-instructors")
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Correctly redirected to login (admin protection working)")
        
        # Test 2: Check admin route exists
        print("\n2. Testing admin approve endpoint directly...")
        response = session.post(f"{base_url}/admin/approve-instructor/1", 
                              data={'action': 'approve'}, 
                              allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ❌ 400 error - likely CSRF or validation issue")
            print(f"   Response headers: {dict(response.headers)}")
            print(f"   Response text preview: {response.text[:200]}...")
        elif response.status_code == 302:
            print("   ✓ Redirected (likely to login)")
        
        # Test 3: Check if we can access a regular page with CSRF
        print("\n3. Testing CSRF token generation on login page...")
        response = session.get(f"{base_url}/login")
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            csrf_input = soup.find('input', {'name': 'csrf_token'})
            if csrf_input:
                token = csrf_input.get('value')
                print(f"   ✓ CSRF token found: {token[:20]}...")
                
                # Test 4: Try posting to login with CSRF
                print("\n4. Testing CSRF token usage...")
                login_data = {
                    'csrf_token': token,
                    'email': 'test@example.com',
                    'password': 'wrongpassword'
                }
                login_response = session.post(f"{base_url}/login", data=login_data)
                print(f"   Login attempt status: {login_response.status_code}")
                if login_response.status_code == 200:
                    print("   ✓ CSRF token accepted (got authentication error, not CSRF error)")
                elif login_response.status_code == 400:
                    print("   ❌ CSRF token rejected")
            else:
                print("   ❌ No CSRF token found in login form")
        
        # Test 5: Check enrollment page CSRF (known working example)
        print("\n5. Testing CSRF on enrollment page (working example)...")
        response = session.get(f"{base_url}/enrollment")
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✓ Redirected to login (needs authentication)")
        
        print("\n📋 Summary:")
        print("- CSRF tokens are being generated correctly")
        print("- Admin pages require authentication (working)")
        print("- The 400 error on admin approval suggests:")
        print("  a) CSRF validation issue in admin routes")
        print("  b) Missing form validation") 
        print("  c) Admin role checking problem")
        
        print("\n🔧 Next steps:")
        print("1. Check admin role assignment")
        print("2. Create admin user for testing")
        print("3. Test actual admin login flow")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask application")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_csrf_debug()
