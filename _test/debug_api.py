"""
Debug Admin API Endpoints
"""
import requests
import json

def test_api_endpoint(url):
    try:
        response = requests.get(url)
        print(f"URL: {url}")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Content: {response.text[:500]}...")
        print("-" * 50)
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Valid JSON response")
                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Array'}")
            except:
                print("❌ Invalid JSON response")
        
        return response
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    base_url = "http://127.0.0.1:5000"
    
    endpoints = [
        "/admin/api/stats",
        "/admin/api/notifications", 
        "/admin/api/activity"
    ]
    
    print("🔍 Testing Admin API Endpoints...")
    for endpoint in endpoints:
        print(f"\n📡 Testing {endpoint}")
        test_api_endpoint(f"{base_url}{endpoint}")
