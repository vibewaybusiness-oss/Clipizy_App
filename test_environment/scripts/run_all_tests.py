#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all tests in the test environment
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

class TestRunner:
    def __init__(self):
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.start_time = time.time()

    def log_result(self, test_name: str, success: bool, error: str = None):
        """Log test result"""
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")

    def run_backend_tests(self):
        """Run backend tests"""
        print("\n🔧 Running Backend Tests...")
        print("=" * 50)
        
        # Test API endpoints
        try:
            result = subprocess.run([
                sys.executable, 
                "test_environment/backend/test_api_endpoints.py"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Backend API Endpoints", True)
            else:
                self.log_result("Backend API Endpoints", False, result.stderr)
        except Exception as e:
            self.log_result("Backend API Endpoints", False, str(e))
        
        # Test services
        try:
            result = subprocess.run([
                sys.executable,
                "test_environment/backend/test_services.py"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Backend Services", True)
            else:
                self.log_result("Backend Services", False, result.stderr)
        except Exception as e:
            self.log_result("Backend Services", False, str(e))

    def run_frontend_tests(self):
        """Run frontend tests"""
        print("\n🎨 Running Frontend Tests...")
        print("=" * 50)
        
        # Run hook structure tests
        try:
            result = subprocess.run([
                "node",
                "test_environment/frontend/test_hooks.js"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Frontend Hooks Structure", True)
            else:
                self.log_result("Frontend Hooks Structure", False, result.stderr)
        except Exception as e:
            self.log_result("Frontend Hooks Structure", False, str(e))
        
        # Run hook import tests
        try:
            result = subprocess.run([
                "node",
                "test_environment/frontend/test_hook_imports.js"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Frontend Hook Imports", True)
            else:
                self.log_result("Frontend Hook Imports", False, result.stderr)
        except Exception as e:
            self.log_result("Frontend Hook Imports", False, str(e))
        
        # Run hook runtime simulation tests
        try:
            result = subprocess.run([
                "node",
                "test_environment/frontend/test_hook_runtime_simulation.js"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Frontend Hook Runtime", True)
            else:
                self.log_result("Frontend Hook Runtime", False, result.stderr)
        except Exception as e:
            self.log_result("Frontend Hook Runtime", False, str(e))

    def run_integration_tests(self):
        """Run integration tests"""
        print("\n🔗 Running Integration Tests...")
        print("=" * 50)
        
        try:
            result = subprocess.run([
                sys.executable,
                "test_environment/integration/test_end_to_end.py"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("End-to-End Integration", True)
            else:
                self.log_result("End-to-End Integration", False, result.stderr)
        except Exception as e:
            self.log_result("End-to-End Integration", False, str(e))

    def run_quick_tests(self):
        """Run quick tests"""
        print("\n⚡ Running Quick Tests...")
        print("=" * 50)
        
        try:
            result = subprocess.run([
                sys.executable,
                "quick_test.py"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Quick Tests", True)
            else:
                self.log_result("Quick Tests", False, result.stderr)
        except Exception as e:
            self.log_result("Quick Tests", False, str(e))

    def run_comprehensive_tests(self):
        """Run comprehensive tests"""
        print("\n🧪 Running Comprehensive Tests...")
        print("=" * 50)
        
        try:
            result = subprocess.run([
                sys.executable,
                "test_all_apis.py"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Comprehensive API Tests", True)
            else:
                self.log_result("Comprehensive API Tests", False, result.stderr)
        except Exception as e:
            self.log_result("Comprehensive API Tests", False, str(e))

    def generate_test_files(self):
        """Generate test files"""
        print("\n📁 Generating Test Files...")
        print("=" * 50)
        
        try:
            result = subprocess.run([
                sys.executable,
                "test_environment/fixtures/test_files.py"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent.parent)
            
            if result.returncode == 0:
                self.log_result("Test File Generation", True)
            else:
                self.log_result("Test File Generation", False, result.stderr)
        except Exception as e:
            self.log_result("Test File Generation", False, str(e))

    def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 60)
        
        # Generate test files first
        self.generate_test_files()
        
        # Run all test suites
        self.run_quick_tests()
        self.run_backend_tests()
        self.run_frontend_tests()
        self.run_integration_tests()
        self.run_comprehensive_tests()
        
        # Print summary
        end_time = time.time()
        total_time = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⏱️  Total time: {total_time:.2f}s")
        
        if self.test_results['errors']:
            print("\n❌ ERRORS:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        success_rate = (self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed'])) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n🎉 System is healthy!")
        elif success_rate >= 60:
            print("\n⚠️  System has some issues but is functional")
        else:
            print("\n💥 System has significant issues!")
        
        return self.test_results['failed'] == 0

def main():
    """Main function"""
    print("🧪 Clipizy Comprehensive Test Suite")
    print("=" * 60)
    
    runner = TestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
