#!/usr/bin/env python3
"""
Simple Backend Test
Tests basic functionality without complex imports
"""

import os
import sys
import time
from pathlib import Path

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

class SimpleTester:
    def __init__(self):
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }

    def log_result(self, test_name: str, success: bool, error: str = None):
        """Log test result"""
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")

    def test_imports(self):
        """Test basic imports"""
        print("\n📦 Testing Basic Imports...")
        
        try:
            # Test settings import
            from api.config.settings import settings
            self.log_result("Settings import", True)
            
            # Test models import
            from api.models import User, Project, Track
            self.log_result("Models import", True)
            
            # Test storage service import (direct)
            from api.services.storage.storage import UnifiedStorageService
            self.log_result("Storage service import", True)
            
        except Exception as e:
            self.log_result("Basic imports", False, str(e))

    def test_storage_service(self):
        """Test storage service"""
        print("\n💾 Testing Storage Service...")
        
        try:
            from api.services.storage.storage import UnifiedStorageService
            
            # Create storage service instance
            storage = UnifiedStorageService()
            self.log_result("Storage service initialization", True)
            
            # Test path generation
            test_path = storage.generate_path(
                "user_project",
                user_id="test-user",
                project_id="test-project",
                file_type="tracks",
                filename="test.mp3"
            )
            
            if "users/test-user/projects/music-clip/test-project/tracks/test.mp3" in test_path:
                self.log_result("Path generation", True)
            else:
                self.log_result("Path generation", False, f"Unexpected path: {test_path}")
                
        except Exception as e:
            self.log_result("Storage service", False, str(e))

    def test_auth_service(self):
        """Test auth service"""
        print("\n🔐 Testing Auth Service...")
        
        try:
            from api.services.auth.auth import auth_service
            
            # Check if auth service has expected methods
            if hasattr(auth_service, 'hash_password'):
                # Test password hashing
                test_password = "testpassword123"
                hashed = auth_service.hash_password(test_password)
                
                if hashed and len(hashed) > 10:
                    self.log_result("Password hashing", True)
                else:
                    self.log_result("Password hashing", False, "Invalid hash")
                
                # Test password verification
                if hasattr(auth_service, 'verify_password'):
                    is_valid = auth_service.verify_password(test_password, hashed)
                    if is_valid:
                        self.log_result("Password verification", True)
                    else:
                        self.log_result("Password verification", False, "Verification failed")
                else:
                    self.log_result("Password verification", False, "verify_password method not found")
            else:
                # Just test that auth service exists
                self.log_result("Auth service exists", True)
                self.log_result("Auth service methods", False, "hash_password method not found")
                
        except Exception as e:
            self.log_result("Auth service", False, str(e))

    def test_file_operations(self):
        """Test file operations"""
        print("\n📁 Testing File Operations...")
        
        try:
            import tempfile
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"test content")
                temp_file_path = temp_file.name
            
            # Check file exists
            if os.path.exists(temp_file_path):
                self.log_result("File creation", True)
            else:
                self.log_result("File creation", False, "File not created")
            
            # Check file size
            file_size = os.path.getsize(temp_file_path)
            if file_size > 0:
                self.log_result("File size check", True)
            else:
                self.log_result("File size check", False, "File is empty")
            
            # Clean up
            os.unlink(temp_file_path)
            self.log_result("File cleanup", True)
            
        except Exception as e:
            self.log_result("File operations", False, str(e))

    def test_environment(self):
        """Test environment setup"""
        print("\n🌍 Testing Environment...")
        
        try:
            # Check Python version
            python_version = sys.version_info
            if python_version.major == 3 and python_version.minor >= 8:
                self.log_result("Python version", True)
            else:
                self.log_result("Python version", False, f"Python {python_version.major}.{python_version.minor} not supported")
            
            # Check working directory
            cwd = os.getcwd()
            if "clipizy" in cwd:
                self.log_result("Working directory", True)
            else:
                self.log_result("Working directory", False, f"Not in clipizy directory: {cwd}")
            
            # Check if virtual environment is activated
            if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
                self.log_result("Virtual environment", True)
            else:
                self.log_result("Virtual environment", False, "Virtual environment not activated")
                
        except Exception as e:
            self.log_result("Environment", False, str(e))

    def run_all_tests(self):
        """Run all simple tests"""
        print("🚀 Starting Simple Backend Tests...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_environment()
        self.test_imports()
        self.test_storage_service()
        self.test_auth_service()
        self.test_file_operations()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SIMPLE TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"⏱️  Total time: {end_time - start_time:.2f}s")
        
        if self.test_results['errors']:
            print("\n❌ ERRORS:")
            for error in self.test_results['errors']:
                print(f"  - {error}")
        
        success_rate = (self.test_results['passed'] / (self.test_results['passed'] + self.test_results['failed'])) * 100
        print(f"\n🎯 Success Rate: {success_rate:.1f}%")
        
        return self.test_results['failed'] == 0

def main():
    """Main function"""
    print("🧪 Simple Backend Testing Suite")
    print("=" * 60)
    
    tester = SimpleTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All simple tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some simple tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
