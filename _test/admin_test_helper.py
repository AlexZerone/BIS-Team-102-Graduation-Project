"""
Admin Test Helper - Quick Admin Login for Testing
=================================================

This script helps create an admin session for testing API endpoints
and other authenticated admin functionality.
"""
import requests
from getpass import getpass

class AdminTestHelper:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def login_as_admin(self, username=None, password=None):
        """Login as admin user"""
        print("🔐 Admin Login Helper")
        print("="*40)
        
        if not username:
            username = input("Admin Username/Email: ")
        if not password:
            password = getpass("Admin Password: ")
        
        # Get login page to get CSRF token
        login_page = self.session.get(f"{self.base_url}/login")
        if login_page.status_code != 200:
            print("❌ Could not access login page")
            return False
        
        # Extract CSRF token (simplified - in real implementation you'd parse HTML)
        print("📝 Attempting login...")
        
        # Attempt login
        login_data = {
            'username': username,
            'password': password
        }
        
        response = self.session.post(f"{self.base_url}/login", data=login_data)
        
        if response.status_code == 200 and "dashboard" in response.url.lower():
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed")
            return False
    
    def test_authenticated_endpoints(self):
        """Test admin endpoints with authentication"""
        print("\n🧪 Testing Authenticated Admin Endpoints...")
        print("="*50)
        
        endpoints = [
            "/admin/api/stats",
            "/admin/api/notifications",
            "/admin/api/activity"
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✅ {endpoint}: Success (JSON)")
                        if isinstance(data, dict) and 'success' in data:
                            print(f"   Status: {data.get('success')}")
                        print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
                    except:
                        print(f"⚠️  {endpoint}: Success (Non-JSON)")
                else:
                    print(f"❌ {endpoint}: Failed ({response.status_code})")
            except Exception as e:
                print(f"❌ {endpoint}: Error - {e}")
        
    def create_test_admin(self):
        """Create a test admin account (for development only)"""
        print("\n🔧 Create Test Admin Account")
        print("="*40)
        print("⚠️  This should only be used in development!")
        
        confirm = input("Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            return
        
        # This would typically interact with your user creation system
        print("📝 Test admin creation would be implemented here")
        print("   For now, create an admin user manually in the database")
        print("   with UserType = 'admin'")

def main():
    helper = AdminTestHelper()
    
    print("🚀 Sec Era Admin Test Helper")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Login as Admin")
        print("2. Test Authenticated Endpoints")
        print("3. Create Test Admin (Dev Only)")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ")
        
        if choice == "1":
            if helper.login_as_admin():
                print("🎉 Ready to test admin functionality!")
        elif choice == "2":
            helper.test_authenticated_endpoints()
        elif choice == "3":
            helper.create_test_admin()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
