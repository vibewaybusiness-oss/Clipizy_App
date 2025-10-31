#!/usr/bin/env python3
"""
Simple API Endpoint Testing Script
Uses built-in libraries to test endpoints
"""

import urllib.request
import urllib.parse
import urllib.error
import json
import sys
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

class SimpleEndpointTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.auth_token = None
        self.test_results = {}
        
    def make_request(self, method: str, endpoint: str, data=None, headers=None):
        """Make HTTP request and return response data"""
        url = f"{self.base_url}{endpoint}"
        
        if headers is None:
            headers = {}
            
        # Add auth token if available
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
            
        # Add content type for JSON data
        if data and isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif data and isinstance(data, str):
            data = data.encode('utf-8')
            
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=10) as response:
                response_data = response.read().decode('utf-8')
                try:
                    json_data = json.loads(response_data)
                except:
                    json_data = {"text": response_data}
                    
                return {
                    "status": response.status,
                    "data": json_data,
                    "headers": dict(response.headers),
                    "url": url
                }
        except urllib.error.HTTPError as e:
            try:
                error_data = e.read().decode('utf-8')
                json_data = json.loads(error_data)
            except:
                json_data = {"text": error_data}
            return {
                "status": e.code,
                "data": json_data,
                "url": url,
                "error": str(e)
            }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "url": url
            }
    
    def test_endpoint(self, name: str, method: str, endpoint: str, expected_status: int = 200, data=None, headers=None):
        """Test a single endpoint"""
        print(f"Testing {name}: {method} {endpoint}")
        
        start_time = time.time()
        result = self.make_request(method, endpoint, data, headers)
        end_time = time.time()
        
        result["test_name"] = name
        result["method"] = method
        result["endpoint"] = endpoint
        result["expected_status"] = expected_status
        result["response_time"] = end_time - start_time
        result["timestamp"] = datetime.now().isoformat()
        
        # Check if test passed
        if result["status"] == expected_status:
            result["passed"] = True
            print(f"✅ {name}: PASSED ({result['status']}) - {result['response_time']:.2f}s")
        else:
            result["passed"] = False
            print(f"❌ {name}: FAILED ({result['status']} != {expected_status}) - {result['response_time']:.2f}s")
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        return result
    
    def authenticate(self):
        """Authenticate and get token"""
        print("🔐 Authenticating...")
        
        # Try to register first
        register_result = self.test_endpoint(
            "User Registration",
            "POST",
            "/api/auth/register",
            201,
            data={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "name": "Test User"
            }
        )
        
        # Try to login
        login_result = self.test_endpoint(
            "User Login",
            "POST",
            "/api/auth/login",
            200,
            data={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
        
        if login_result["passed"] and "data" in login_result and "access_token" in login_result["data"]:
            self.auth_token = login_result["data"]["access_token"]
            print(f"✅ Authentication successful")
            return True
        else:
            print(f"❌ Authentication failed")
            return False
    
    def test_health_endpoints(self):
        """Test health and basic endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        endpoints = [
            ("Root Endpoint", "GET", "/", 200),
            ("Health Check", "GET", "/health", 200),
            ("API Docs", "GET", "/docs", 200),
            ("OpenAPI Schema", "GET", "/openapi.json", 200),
        ]
        
        for name, method, endpoint, expected_status in endpoints:
            result = self.test_endpoint(name, method, endpoint, expected_status)
            self.test_results[f"health_{name.lower().replace(' ', '_')}"] = result
    
    def test_storage_endpoints(self):
        """Test storage router endpoints"""
        print("\n📁 Testing Storage Endpoints...")
        
        endpoints = [
            ("Storage Health", "GET", "/api/storage/health", 200),
            ("List Projects", "GET", "/api/storage/projects", 200),
            ("Create Project", "POST", "/api/storage/projects", 201, {
                "project_type": "music-clip",
                "name": "Test Project",
                "description": "Test project for endpoint testing"
            }),
        ]
        
        for endpoint_data in endpoints:
            name = endpoint_data[0]
            method = endpoint_data[1]
            endpoint = endpoint_data[2]
            expected_status = endpoint_data[3]
            data = endpoint_data[4] if len(endpoint_data) > 4 else None
            
            result = self.test_endpoint(name, method, endpoint, expected_status, data)
            self.test_results[f"storage_{name.lower().replace(' ', '_')}"] = result
    
    def test_analysis_endpoints(self):
        """Test analysis endpoints"""
        print("\n🔍 Testing Analysis Endpoints...")
        
        endpoints = [
            ("Analysis Comprehensive", "POST", "/api/analysis/analyze/comprehensive", 200, {
                "file_path": "test.mp3",
                "analysis_type": "music"
            }),
            ("Analysis Simple", "POST", "/api/analysis/analyze/simple", 200, {
                "file_path": "test.mp3"
            }),
        ]
        
        for endpoint_data in endpoints:
            name = endpoint_data[0]
            method = endpoint_data[1]
            endpoint = endpoint_data[2]
            expected_status = endpoint_data[3]
            data = endpoint_data[4] if len(endpoint_data) > 4 else None
            
            result = self.test_endpoint(name, method, endpoint, expected_status, data)
            self.test_results[f"analysis_{name.lower().replace(' ', '_')}"] = result
    
    def test_credits_endpoints(self):
        """Test credits endpoints"""
        print("\n💰 Testing Credits Endpoints...")
        
        endpoints = [
            ("Credits Balance", "GET", "/api/credits/balance", 200),
            ("Credits Transactions", "GET", "/api/credits/transactions", 200),
            ("Credits Pricing Music", "GET", "/api/credits/pricing/music", 200),
        ]
        
        for name, method, endpoint, expected_status in endpoints:
            result = self.test_endpoint(name, method, endpoint, expected_status)
            self.test_results[f"credits_{name.lower().replace(' ', '_')}"] = result
    
    def test_ai_endpoints(self):
        """Test AI service endpoints"""
        print("\n🤖 Testing AI Endpoints...")
        
        endpoints = [
            ("Prompts Random", "GET", "/api/prompts/random", 200),
            ("ComfyUI Status", "GET", "/api/comfyui/status", 200),
            ("ComfyUI Workflows", "GET", "/api/comfyui/workflows", 200),
        ]
        
        for name, method, endpoint, expected_status in endpoints:
            result = self.test_endpoint(name, method, endpoint, expected_status)
            self.test_results[f"ai_{name.lower().replace(' ', '_')}"] = result
    
    def run_all_tests(self):
        """Run all endpoint tests"""
        print("🚀 Starting Simple API Endpoint Testing")
        print(f"Base URL: {self.base_url}")
        print("=" * 60)
        
        # Test health endpoints first (no auth required)
        self.test_health_endpoints()
        
        # Authenticate
        auth_success = self.authenticate()
        if not auth_success:
            print("❌ Authentication failed, skipping authenticated endpoints")
            return
        
        # Test authenticated endpoints
        self.test_storage_endpoints()
        self.test_analysis_endpoints()
        self.test_credits_endpoints()
        self.test_ai_endpoints()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("📊 TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get("passed", False))
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for name, result in self.test_results.items():
                if not result.get("passed", False):
                    print(f"  - {result.get('test_name', name)}: {result.get('status', 'ERROR')}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")
        
        # Save detailed report
        report_file = f"simple_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    tester = SimpleEndpointTester(base_url)
    tester.run_all_tests()

if __name__ == "__main__":
    main()
