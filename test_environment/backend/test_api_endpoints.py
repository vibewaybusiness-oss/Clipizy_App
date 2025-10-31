#!/usr/bin/env python3
"""
Backend API Endpoints Test Suite
Comprehensive testing of all API endpoints
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import pytest
import requests
from fastapi.testclient import TestClient

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import directly to avoid circular imports
from api.main import app
from api.services.database import get_db
from api.services.storage.storage import unified_storage_service
from api.models import User, Project, Track

class APIEndpointTester:
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

    def test_health_endpoints(self):
        """Test all health check endpoints"""
        print("\n🏥 Testing Health Endpoints...")
        
        health_endpoints = [
            "/api/storage/health",
            "/api/auth/health", 
            "/api/ai/health",
            "/api/analytics/health"
        ]
        
        for endpoint in health_endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code in [200, 401]:  # 401 is OK for health checks
                    self.log_result(f"Health check {endpoint}", True)
                else:
                    self.log_result(f"Health check {endpoint}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Health check {endpoint}", False, str(e))

    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Auth Endpoints...")
        
        # Test Google OAuth URL generation
        try:
            response = self.client.get("/api/auth/google")
            if response.status_code == 200:
                data = response.json()
                if "auth_url" in data.get("data", {}):
                    self.log_result("Google OAuth URL generation", True)
                else:
                    self.log_result("Google OAuth URL generation", False, "No auth_url in response")
            else:
                self.log_result("Google OAuth URL generation", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Google OAuth URL generation", False, str(e))

    def test_storage_endpoints(self):
        """Test storage endpoints"""
        print("\n📁 Testing Storage Endpoints...")
        
        # Test projects listing
        try:
            response = self.client.get("/api/storage/projects")
            if response.status_code in [200, 401]:  # 401 expected without auth
                self.log_result("Projects listing endpoint", True)
            else:
                self.log_result("Projects listing endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Projects listing endpoint", False, str(e))

    def test_ai_endpoints(self):
        """Test AI endpoints"""
        print("\n🤖 Testing AI Endpoints...")
        
        # Test prompts endpoint
        try:
            response = self.client.get("/api/ai/prompts")
            if response.status_code in [200, 401]:
                self.log_result("AI prompts endpoint", True)
            else:
                self.log_result("AI prompts endpoint", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("AI prompts endpoint", False, str(e))

    def test_file_upload_simulation(self):
        """Test file upload simulation"""
        print("\n📤 Testing File Upload Simulation...")
        
        try:
            # Create a temporary test file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(b"fake audio content")
                temp_file_path = temp_file.name
            
            # Test file validation
            from fastapi import UploadFile
            with open(temp_file_path, "rb") as f:
                file_content = f.read()
            
            # Simulate file upload validation
            unified_storage_service.validate_audio_file(
                UploadFile(filename="test.mp3", file=temp_file)
            )
            
            self.log_result("File upload validation", True)
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            self.log_result("File upload validation", False, str(e))

    def test_database_operations(self):
        """Test database operations"""
        print("\n🗄️ Testing Database Operations...")
        
        try:
            # Test database connection
            db = next(get_db())
            
            # Test user query
            user_count = db.query(User).count()
            self.log_result("Database user query", True)
            
            # Test project query
            project_count = db.query(Project).count()
            self.log_result("Database project query", True)
            
            # Test track query
            track_count = db.query(Track).count()
            self.log_result("Database track query", True)
            
        except Exception as e:
            self.log_result("Database operations", False, str(e))

    def test_storage_service_operations(self):
        """Test storage service operations"""
        print("\n💾 Testing Storage Service Operations...")
        
        try:
            # Test bucket existence
            unified_storage_service._ensure_bucket_exists()
            self.log_result("Storage bucket check", True)
            
            # Test path generation
            test_path = unified_storage_service.generate_path(
                "user_project",
                user_id="test-user",
                project_id="test-project",
                file_type="tracks",
                filename="test.mp3"
            )
            expected_path = "users/test-user/projects/music-clip/test-project/tracks/test.mp3"
            if expected_path in test_path:
                self.log_result("Storage path generation", True)
            else:
                self.log_result("Storage path generation", False, f"Expected: {expected_path}, Got: {test_path}")
            
            # Test file existence check
            exists = unified_storage_service.file_exists("non-existent-file")
            if exists == False:  # Should return False for non-existent file
                self.log_result("Storage file existence check", True)
            else:
                self.log_result("Storage file existence check", False, "Should return False for non-existent file")
                
        except Exception as e:
            self.log_result("Storage service operations", False, str(e))

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Backend API Testing...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_auth_endpoints()
        self.test_storage_endpoints()
        self.test_ai_endpoints()
        self.test_file_upload_simulation()
        self.test_database_operations()
        self.test_storage_service_operations()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 BACKEND TEST SUMMARY")
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
    print("🧪 Backend API Testing Suite")
    print("=" * 60)
    
    tester = APIEndpointTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All backend tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some backend tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
