"""
Sec Era Platform - Admin Interface Test Script
Test all admin functionality and routes
"""
import requests
import json
from datetime import datetime

class AdminTester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_admin_routes(self):
        """Test all admin routes for accessibility"""
        routes_to_test = [
            '/admin',
            '/admin/dashboard',
            '/admin/users',
            '/admin/pending-instructors',
            '/admin/pending-companies', 
            '/admin/pending-courses',
            '/admin/subscriptions',
            '/admin/settings',
            '/admin/reports',
            '/admin/contact-requests',
        ]
        
        print("🔍 Testing Admin Routes...")
        results = {}
        
        for route in routes_to_test:
            try:
                response = self.session.get(f"{self.base_url}{route}")
                status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
                results[route] = {
                    'status_code': response.status_code,
                    'accessible': response.status_code == 200,
                    'content_length': len(response.content)
                }
                print(f"  {route}: {status}")
                
            except Exception as e:
                results[route] = {
                    'status_code': None,
                    'accessible': False,
                    'error': str(e)
                }
                print(f"  {route}: ❌ ERROR - {str(e)}")
        
        return results
    
    def test_admin_api_endpoints(self):
        """Test admin API endpoints"""
        api_endpoints = [
            '/admin/api/stats',
            '/admin/api/notifications', 
            '/admin/api/activity',
        ]
        
        print("\n🔍 Testing Admin API Endpoints...")
        results = {}
        
        for endpoint in api_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  {endpoint}: ✅ PASS (JSON Response)")
                        results[endpoint] = {
                            'status_code': 200,
                            'valid_json': True,
                            'data_keys': list(data.keys()) if isinstance(data, dict) else 'array'
                        }
                    except:
                        print(f"  {endpoint}: ⚠️  PASS (Non-JSON Response)")
                        results[endpoint] = {
                            'status_code': 200,
                            'valid_json': False
                        }
                else:
                    print(f"  {endpoint}: ❌ FAIL ({response.status_code})")
                    results[endpoint] = {
                        'status_code': response.status_code,
                        'valid_json': False
                    }
                    
            except Exception as e:
                results[endpoint] = {
                    'error': str(e)
                }
                print(f"  {endpoint}: ❌ ERROR - {str(e)}")
        
        return results
    
    def test_upload_endpoints(self):
        """Test upload endpoints"""
        upload_endpoints = [
            '/uploads/list/profiles',
            '/uploads/list/courses',
            '/uploads/list/admin',
        ]
        
        print("\n🔍 Testing Upload Endpoints...")
        results = {}
        
        for endpoint in upload_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"  {endpoint}: ✅ PASS")
                        results[endpoint] = {
                            'status_code': 200,
                            'valid_json': True,
                            'file_count': len(data.get('files', []))
                        }
                    except:
                        print(f"  {endpoint}: ⚠️  Non-JSON Response")
                        results[endpoint] = {
                            'status_code': 200,
                            'valid_json': False
                        }
                else:
                    print(f"  {endpoint}: ❌ FAIL ({response.status_code})")
                    results[endpoint] = {
                        'status_code': response.status_code
                    }
                    
            except Exception as e:
                results[endpoint] = {
                    'error': str(e)
                }
                print(f"  {endpoint}: ❌ ERROR - {str(e)}")
        
        return results
    
    def generate_report(self, results):
        """Generate a comprehensive test report"""
        print("\n" + "="*60)
        print("📋 ADMIN INTERFACE TEST REPORT")
        print("="*60)
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base URL: {self.base_url}")
        
        # Count results
        total_tests = 0
        passed_tests = 0
        
        for category, tests in results.items():
            print(f"\n📁 {category.upper()}:")
            for test_name, result in tests.items():
                total_tests += 1
                if result.get('accessible') or result.get('status_code') == 200:
                    passed_tests += 1
                    status = "✅ PASS"
                else:
                    status = "❌ FAIL"
                
                print(f"  {test_name}: {status}")
                if 'error' in result:
                    print(f"    Error: {result['error']}")
                elif 'status_code' in result:
                    print(f"    Status: {result['status_code']}")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {passed_tests}")
        print(f"  Failed: {total_tests - passed_tests}")
        print(f"  Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests/total_tests)*100
        }
    
    def run_full_test(self):
        """Run complete admin interface test suite"""
        print("🚀 Starting Admin Interface Test Suite...")
        print("="*60)
        
        results = {
            'admin_routes': self.test_admin_routes(),
            'api_endpoints': self.test_admin_api_endpoints(),
            'upload_endpoints': self.test_upload_endpoints()
        }
        
        summary = self.generate_report(results)
        
        return results, summary

if __name__ == "__main__":
    tester = AdminTester()
    results, summary = tester.run_full_test()
    
    # Save results to file
    with open('admin_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: admin_test_results.json")
    
    if summary['success_rate'] >= 80:
        print("🎉 ADMIN INTERFACE IS READY FOR USE!")
    else:
        print("⚠️  ADMIN INTERFACE NEEDS ATTENTION")
