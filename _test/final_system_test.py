"""
Final System Test Suite for Sec Era Platform
This script performs comprehensive testing of all major system components
"""
import requests
import json
from datetime import datetime

def test_application_health():
    """Test basic application health and functionality"""
    base_url = "http://127.0.0.1:5000"
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": {},
        "summary": {}
    }
    
    print("🚀 Sec Era Platform - Final System Test Suite")
    print("=" * 60)
    
    # Test public pages
    public_pages = [
        "/",
        "/register", 
        "/login",
        "/help",
        "/help/getting-started",
        "/pages/about",
        "/pages/contact"
    ]
    
    print("🔍 Testing Public Pages...")
    public_passed = 0
    for page in public_pages:
        try:
            response = requests.get(f"{base_url}{page}", timeout=10)
            if response.status_code == 200:
                print(f"  {page}: ✅ PASS")
                results["tests"][page] = {"status": "PASS", "code": 200}
                public_passed += 1
            else:
                print(f"  {page}: ❌ FAIL ({response.status_code})")
                results["tests"][page] = {"status": "FAIL", "code": response.status_code}
        except Exception as e:
            print(f"  {page}: ❌ ERROR ({str(e)})")
            results["tests"][page] = {"status": "ERROR", "error": str(e)}
    
    # Test authentication pages (should redirect to login)
    auth_required_pages = [
        "/dashboard",
        "/courses",
        "/assignments", 
        "/jobs",
        "/profile",
        "/enrollment"
    ]
    
    print("🔍 Testing Authentication-Required Pages...")
    auth_passed = 0
    for page in auth_required_pages:
        try:
            response = requests.get(f"{base_url}{page}", allow_redirects=False, timeout=10)
            if response.status_code in [302, 401]:  # Redirect to login or unauthorized
                print(f"  {page}: ✅ PASS (Auth Required)")
                results["tests"][page] = {"status": "PASS", "code": response.status_code, "note": "Auth Required"}
                auth_passed += 1
            else:
                print(f"  {page}: ❌ FAIL ({response.status_code})")
                results["tests"][page] = {"status": "FAIL", "code": response.status_code}
        except Exception as e:
            print(f"  {page}: ❌ ERROR ({str(e)})")
            results["tests"][page] = {"status": "ERROR", "error": str(e)}
    
    # Test admin pages (should redirect or require auth)
    admin_pages = [
        "/admin",
        "/admin/dashboard",
        "/admin/users",
        "/admin/settings"
    ]
    
    print("🔍 Testing Admin Pages...")
    admin_passed = 0
    for page in admin_pages:
        try:
            response = requests.get(f"{base_url}{page}", allow_redirects=False, timeout=10)
            if response.status_code in [302, 401]:  # Should require authentication
                print(f"  {page}: ✅ PASS (Admin Auth Required)")
                results["tests"][page] = {"status": "PASS", "code": response.status_code, "note": "Admin Auth Required"}
                admin_passed += 1
            else:
                print(f"  {page}: ❌ FAIL ({response.status_code})")
                results["tests"][page] = {"status": "FAIL", "code": response.status_code}
        except Exception as e:
            print(f"  {page}: ❌ ERROR ({str(e)})")
            results["tests"][page] = {"status": "ERROR", "error": str(e)}
    
    # Calculate summary
    total_tests = len(public_pages) + len(auth_required_pages) + len(admin_pages)
    total_passed = public_passed + auth_passed + admin_passed
    success_rate = (total_passed / total_tests) * 100
    
    results["summary"] = {
        "total_tests": total_tests,
        "passed": total_passed,
        "failed": total_tests - total_passed,
        "success_rate": success_rate,
        "public_pages": {"total": len(public_pages), "passed": public_passed},
        "auth_pages": {"total": len(auth_required_pages), "passed": auth_passed},
        "admin_pages": {"total": len(admin_pages), "passed": admin_passed}
    }
    
    print("=" * 60)
    print("📊 FINAL SYSTEM TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    print(f"Public Pages: {public_passed}/{len(public_pages)} ({'✅' if public_passed == len(public_pages) else '⚠️'})")
    print(f"Auth-Required Pages: {auth_passed}/{len(auth_required_pages)} ({'✅' if auth_passed == len(auth_required_pages) else '⚠️'})")
    print(f"Admin Pages: {admin_passed}/{len(admin_pages)} ({'✅' if admin_passed == len(admin_pages) else '⚠️'})")
    
    if success_rate >= 90:
        print("🎉 SYSTEM STATUS: EXCELLENT - All major components working!")
    elif success_rate >= 75:
        print("✅ SYSTEM STATUS: GOOD - Minor issues detected")
    else:
        print("⚠️  SYSTEM STATUS: NEEDS ATTENTION - Multiple issues detected")
    
    # Save results
    with open("final_system_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"💾 Results saved to: final_system_test_results.json")
    
    return results

if __name__ == "__main__":
    test_application_health()
