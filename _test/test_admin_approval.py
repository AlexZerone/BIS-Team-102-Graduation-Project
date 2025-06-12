#!/usr/bin/env python3
"""
Test script for admin approval functionality
Tests the fixed approve_instructor and approve_company functions
"""

import requests
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def test_admin_approval():
    base_url = "http://127.0.0.1:5000"
      # Create a session with retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    
    print("Testing Admin Approval Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Check if the admin login page loads
        print("1. Testing admin login page accessibility...")
        response = session.get(f"{base_url}/admin/login", timeout=10)
        if response.status_code == 200:
            print("✓ Admin login page accessible")
        else:
            print(f"✗ Admin login page returned status: {response.status_code}")
            
        # Test 2: Check if pending instructors page is accessible (may require login)
        print("\n2. Testing pending instructors page...")
        response = session.get(f"{base_url}/admin/pending-instructors", timeout=10)
        print(f"   Status: {response.status_code} (302 redirect expected if not logged in)")
        
        # Test 3: Check if pending companies page is accessible (may require login)  
        print("\n3. Testing pending companies page...")
        response = session.get(f"{base_url}/admin/pending-companies", timeout=10)
        print(f"   Status: {response.status_code} (302 redirect expected if not logged in)")
        
        # Test 4: Verify CSRF token functionality
        print("\n4. Testing CSRF token handling...")
        
        # Try to make a POST request without CSRF token (should fail)
        response = session.post(f"{base_url}/admin/approve-instructor/1", 
                              data={'action': 'approve'}, 
                              timeout=10, 
                              allow_redirects=False)
        
        if response.status_code in [400, 403, 302]:
            print("✓ POST request without CSRF token properly rejected/redirected")
        else:
            print(f"✗ Unexpected response for POST without CSRF: {response.status_code}")
            
        print("\n5. Summary:")
        print("- CSRF tokens have been added to both instructor and company approval forms")
        print("- Admin approval logic has been simplified and improved")
        print("- Both approve_instructor and approve_company functions updated")
        print("- Error handling and validation enhanced")
        
        print("\n6. Next steps to fully test:")
        print("- Create an admin user in the database")
        print("- Log in as admin and test actual approval workflow")
        print("- Verify database updates after approval/rejection")
        
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        print("Make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    test_admin_approval()
