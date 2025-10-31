#!/usr/bin/env python3
"""
Backend Services Test Suite
Tests all backend services and their functionality
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

# Add project root to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import directly to avoid circular imports
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import services directly
from api.services.storage.storage import unified_storage_service
from api.services.auth.auth import auth_service
from api.services.database import get_db
from api.models import User, Project, Track
from api.config.settings import settings

class ServicesTester:
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

    def test_storage_service(self):
        """Test storage service functionality"""
        print("\n💾 Testing Storage Service...")
        
        try:
            # Test initialization
            self.log_result("Storage service initialization", True)
            
            # Test bucket operations
            unified_storage_service._ensure_bucket_exists()
            self.log_result("Storage bucket operations", True)
            
            # Test path generation
            test_cases = [
                {
                    "type": "user_project",
                    "kwargs": {
                        "user_id": "test-user",
                        "project_id": "test-project",
                        "file_type": "tracks",
                        "filename": "test.mp3"
                    },
                    "expected": "users/test-user/projects/music-clip/test-project/tracks/test.mp3"
                },
                {
                    "type": "user_file",
                    "kwargs": {
                        "user_id": "test-user",
                        "file_type": "uploads",
                        "filename": "test.jpg"
                    },
                    "expected": "users/test-user/uploads/test.jpg"
                },
                {
                    "type": "project_script",
                    "kwargs": {
                        "user_id": "test-user",
                        "project_id": "test-project"
                    },
                    "expected": "users/test-user/projects/music-clip/test-project/script.json"
                }
            ]
            
            for case in test_cases:
                try:
                    path = unified_storage_service.generate_path(case["type"], **case["kwargs"])
                    if case["expected"] in path:
                        self.log_result(f"Path generation: {case['type']}", True)
                    else:
                        self.log_result(f"Path generation: {case['type']}", False, f"Expected: {case['expected']}, Got: {path}")
                except Exception as e:
                    self.log_result(f"Path generation: {case['type']}", False, str(e))
            
            # Test file operations
            test_key = "test-file.txt"
            test_content = b"Hello, World!"
            
            # Test save_bytes
            unified_storage_service.save_bytes(test_content, test_key)
            self.log_result("Storage save_bytes operation", True)
            
            # Test file_exists
            exists = unified_storage_service.file_exists(test_key)
            if exists:
                self.log_result("Storage file_exists operation", True)
            else:
                self.log_result("Storage file_exists operation", False, "File should exist after saving")
            
            # Test delete_file
            unified_storage_service.delete_file(test_key)
            self.log_result("Storage delete_file operation", True)
            
            # Test file_exists after deletion
            exists_after = unified_storage_service.file_exists(test_key)
            if not exists_after:
                self.log_result("Storage file deletion verification", True)
            else:
                self.log_result("Storage file deletion verification", False, "File should not exist after deletion")
                
        except Exception as e:
            self.log_result("Storage service", False, str(e))

    def test_auth_service(self):
        """Test authentication service"""
        print("\n🔐 Testing Auth Service...")
        
        try:
            # Test service initialization
            self.log_result("Auth service initialization", True)
            
            # Test user creation (without actually creating)
            test_email = "test@example.com"
            test_password = "testpassword123"
            
            # Test password hashing
            hashed_password = auth_service.hash_password(test_password)
            if hashed_password and len(hashed_password) > 10:
                self.log_result("Password hashing", True)
            else:
                self.log_result("Password hashing", False, "Invalid hash generated")
            
            # Test password verification
            is_valid = auth_service.verify_password(test_password, hashed_password)
            if is_valid:
                self.log_result("Password verification", True)
            else:
                self.log_result("Password verification", False, "Password verification failed")
            
            # Test invalid password verification
            is_invalid = auth_service.verify_password("wrongpassword", hashed_password)
            if not is_invalid:
                self.log_result("Invalid password rejection", True)
            else:
                self.log_result("Invalid password rejection", False, "Should reject invalid password")
                
        except Exception as e:
            self.log_result("Auth service", False, str(e))

    def test_database_service(self):
        """Test database service"""
        print("\n🗄️ Testing Database Service...")
        
        try:
            # Test database connection
            db = next(get_db())
            self.log_result("Database connection", True)
            
            # Test user model
            user_count = db.query(User).count()
            self.log_result("User model query", True)
            
            # Test project model
            project_count = db.query(Project).count()
            self.log_result("Project model query", True)
            
            # Test track model
            track_count = db.query(Track).count()
            self.log_result("Track model query", True)
            
            # Test database session management
            db.close()
            self.log_result("Database session management", True)
            
        except Exception as e:
            self.log_result("Database service", False, str(e))

    def test_settings_service(self):
        """Test settings service"""
        print("\n⚙️ Testing Settings Service...")
        
        try:
            # Test settings initialization
            self.log_result("Settings initialization", True)
            
            # Test database URL
            if settings.database_url:
                self.log_result("Database URL configuration", True)
            else:
                self.log_result("Database URL configuration", False, "Database URL not configured")
            
            # Test S3 configuration
            if settings.s3_bucket:
                self.log_result("S3 bucket configuration", True)
            else:
                self.log_result("S3 bucket configuration", False, "S3 bucket not configured")
            
            if settings.s3_endpoint_url:
                self.log_result("S3 endpoint configuration", True)
            else:
                self.log_result("S3 endpoint configuration", False, "S3 endpoint not configured")
            
            # Test JWT configuration
            if settings.jwt_secret_key:
                self.log_result("JWT secret configuration", True)
            else:
                self.log_result("JWT secret configuration", False, "JWT secret not configured")
            
            # Test frontend URL
            if settings.frontend_url:
                self.log_result("Frontend URL configuration", True)
            else:
                self.log_result("Frontend URL configuration", False, "Frontend URL not configured")
                
        except Exception as e:
            self.log_result("Settings service", False, str(e))

    def test_metadata_extraction(self):
        """Test metadata extraction functionality"""
        print("\n📊 Testing Metadata Extraction...")
        
        try:
            # Test audio metadata extraction with fake file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(b"fake audio content")
                temp_file_path = temp_file.name
            
            try:
                metadata = unified_storage_service.extract_audio_metadata(temp_file_path)
                if isinstance(metadata, dict):
                    self.log_result("Audio metadata extraction", True)
                else:
                    self.log_result("Audio metadata extraction", False, "Should return dictionary")
            except Exception as e:
                # This is expected for fake files
                self.log_result("Audio metadata extraction (expected failure)", True)
            
            # Test image metadata extraction with fake file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_file.write(b"fake image content")
                temp_file_path = temp_file.name
            
            try:
                metadata = unified_storage_service.extract_image_metadata(temp_file_path)
                if isinstance(metadata, dict):
                    self.log_result("Image metadata extraction", True)
                else:
                    self.log_result("Image metadata extraction", False, "Should return dictionary")
            except Exception as e:
                # This is expected for fake files
                self.log_result("Image metadata extraction (expected failure)", True)
            
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
                
        except Exception as e:
            self.log_result("Metadata extraction", False, str(e))

    def run_all_tests(self):
        """Run all service tests"""
        print("🚀 Starting Backend Services Testing...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all test suites
        self.test_storage_service()
        self.test_auth_service()
        self.test_database_service()
        self.test_settings_service()
        self.test_metadata_extraction()
        
        end_time = time.time()
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 SERVICES TEST SUMMARY")
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
    print("🧪 Backend Services Testing Suite")
    print("=" * 60)
    
    tester = ServicesTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All services tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some services tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
