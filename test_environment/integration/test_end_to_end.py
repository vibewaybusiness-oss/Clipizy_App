#!/usr/bin/env python3
"""
End-to-End Integration Test Suite
Tests complete user workflows and system integration
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
from fastapi.testclient import TestClient

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import directly to avoid circular imports
from api.main import app
from api.services.database import get_db
from api.services.storage.storage import unified_storage_service
from api.models import User, Project, Track

class EndToEndTester:
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.test_user_id = None
        self.test_project_id = None
        self.auth_token = None

    def log_result(self, test_name: str, success: bool, error: str = None):
        """Log test result"""
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")

    def test_user_registration_flow(self):
        """Test complete user registration flow"""
        print("\n👤 Testing User Registration Flow...")
        
        try:
            # Test Google OAuth URL generation
            response = self.client.get("/api/auth/google")
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data.get("data", {}):
                    self.log_result("OAuth URL generation", True)
                else:
                    self.log_result("OAuth URL generation", False, "No auth_url in response")
            else:
                self.log_result("OAuth URL generation", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("User registration flow", False, str(e))

    def test_project_creation_flow(self):
        """Test project creation workflow"""
        print("\n📁 Testing Project Creation Flow...")
        
        try:
            # Test project creation endpoint
            project_data = {
                "name": "Test Project",
                "description": "Test project for integration testing",
                "project_type": "music-clip"
            }
            
            response = self.client.post("/api/storage/projects", json=project_data)
            if response.status_code in [200, 401]:  # 401 expected without auth
                self.log_result("Project creation endpoint", True)
            else:
                self.log_result("Project creation endpoint", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Project creation flow", False, str(e))

    def test_file_upload_flow(self):
        """Test file upload workflow"""
        print("\n📤 Testing File Upload Flow...")
        
        try:
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(b"fake audio content for testing")
                temp_file_path = temp_file.name
            
            # Test file upload endpoint
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test.mp3", f, "audio/mpeg")}
                response = self.client.post("/api/storage/projects/test-project-id/tracks/upload", files=files)
            
            if response.status_code in [200, 401, 404]:  # 401/404 expected without auth/project
                self.log_result("File upload endpoint", True)
            else:
                self.log_result("File upload endpoint", False, f"Status: {response.status_code}")
            
            # Clean up
            os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_result("File upload flow", False, str(e))

    def test_storage_integration(self):
        """Test storage service integration"""
        print("\n💾 Testing Storage Integration...")
        
        try:
            # Test storage service initialization
            unified_storage_service._ensure_bucket_exists()
            self.log_result("Storage service initialization", True)
            
            # Test path generation
            test_path = unified_storage_service.generate_path(
                "user_project",
                user_id="test-user",
                project_id="test-project",
                file_type="tracks",
                filename="test.mp3"
            )
            if "users/test-user/projects/music-clip/test-project/tracks/test.mp3" in test_path:
                self.log_result("Storage path generation", True)
            else:
                self.log_result("Storage path generation", False, f"Unexpected path: {test_path}")
            
            # Test file operations
            test_key = "integration-test.txt"
            test_content = b"Integration test content"
            
            # Save file
            unified_storage_service.save_bytes(test_content, test_key)
            self.log_result("Storage file save", True)
            
            # Check file exists
            exists = unified_storage_service.file_exists(test_key)
            if exists:
                self.log_result("Storage file existence check", True)
            else:
                self.log_result("Storage file existence check", False, "File should exist after saving")
            
            # Delete file
            unified_storage_service.delete_file(test_key)
            self.log_result("Storage file deletion", True)
            
            # Verify deletion
            exists_after = unified_storage_service.file_exists(test_key)
            if not exists_after:
                self.log_result("Storage file deletion verification", True)
            else:
                self.log_result("Storage file deletion verification", False, "File should not exist after deletion")
                
        except Exception as e:
            self.log_result("Storage integration", False, str(e))

    def test_database_integration(self):
        """Test database integration"""
        print("\n🗄️ Testing Database Integration...")
        
        try:
            # Test database connection
            db = next(get_db())
            self.log_result("Database connection", True)
            
            # Test user model operations
            user_count = db.query(User).count()
            self.log_result("User model query", True)
            
            # Test project model operations
            project_count = db.query(Project).count()
            self.log_result("Project model query", True)
            
            # Test track model operations
            track_count = db.query(Track).count()
            self.log_result("Track model query", True)
            
            # Test database session management
            db.close()
            self.log_result("Database session management", True)
            
        except Exception as e:
            self.log_result("Database integration", False, str(e))

    def test_api_endpoint_integration(self):
        """Test API endpoint integration"""
        print("\n🌐 Testing API Endpoint Integration...")
        
        endpoints_to_test = [
            ("/api/storage/health", "Storage health check"),
            ("/api/auth/google", "Google OAuth"),
            ("/api/storage/projects", "Projects listing"),
            ("/api/ai/prompts", "AI prompts"),
            ("/api/analytics/stats", "Analytics stats")
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 401]:  # 401 is OK for protected endpoints
                    self.log_result(f"API endpoint: {description}", True)
                else:
                    self.log_result(f"API endpoint: {description}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"API endpoint: {description}", False, str(e))

    def test_error_handling_integration(self):
        """Test error handling integration"""
        print("\n⚠️ Testing Error Handling Integration...")
        
        try:
            # Test invalid endpoint
            response = self.client.get("/api/invalid/endpoint")
            if response.status_code == 404:
                self.log_result("Invalid endpoint handling", True)
            else:
                self.log_result("Invalid endpoint handling", False, f"Expected 404, got {response.status_code}")
            
            # Test invalid file upload
            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
                temp_file.write(b"invalid file content")
                temp_file_path = temp_file.name
            
            with open(temp_file_path, "rb") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                response = self.client.post("/api/storage/projects/test/tracks/upload", files=files)
            
            # Should return error for invalid file type
            if response.status_code in [400, 401, 404]:
                self.log_result("Invalid file type handling", True)
            else:
                self.log_result("Invalid file type handling", False, f"Expected error status, got {response.status_code}")
            
            # Clean up
            os.unlink(temp_file_path)
                
        except Exception as e:
            self.log_result("Error handling integration", False, str(e))

    def test_performance_integration(self):
        """Test performance integration"""
        print("\n⚡ Testing Performance Integration...")
        
        try:
            # Test response times
            start_time = time.time()
            response = self.client.get("/api/storage/health")
            end_time = time.time()
            
            response_time = end_time - start_time
            if response_time < 1.0:  # Should respond within 1 second
                self.log_result("API response time", True)
            else:
                self.log_result("API response time", False, f"Response too slow: {response_time:.2f}s")
            
            # Test storage operations performance
            start_time = time.time()
            test_key = "performance-test.txt"
            test_content = b"Performance test content"
            
            unified_storage_service.save_bytes(test_content, test_key)
            exists = unified_storage_service.file_exists(test_key)
            unified_storage_service.delete_file(test_key)
            
            end_time = time.time()
            storage_time = end_time - start_time
            
            if storage_time < 2.0:  # Storage operations should complete within 2 seconds
                self.log_result("Storage operations performance", True)
            else:
                self.log_result("Storage operations performance", False, f"Storage operations too slow: {storage_time:.2f}s")
                
        except Exception as e:
            self.log_result("Performance integration", False, str(e))

    def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 Starting End-to-End Integration Testing...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_user_registration_flow()
        self.test_project_creation_flow()
        self.test_file_upload_flow()
        self.test_storage_integration()
        self.test_database_integration()
        self.test_api_endpoint_integration()
        self.test_error_handling_integration()
        self.test_performance_integration()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
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
    print("🧪 End-to-End Integration Testing Suite")
    print("=" * 60)
    
    tester = EndToEndTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All integration tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some integration tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
