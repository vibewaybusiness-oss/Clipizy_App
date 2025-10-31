#!/usr/bin/env python3
"""
Test Configuration
Configuration settings for all tests
"""

import os
from pathlib import Path

class TestConfig:
    """Test configuration settings"""
    
    # Base paths
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    TEST_ENVIRONMENT = Path(__file__).parent.parent
    FIXTURES_DIR = TEST_ENVIRONMENT / "fixtures"
    SCRIPTS_DIR = TEST_ENVIRONMENT / "scripts"
    
    # Test data
    TEST_DATA_FILE = FIXTURES_DIR / "test_data.json"
    
    # API settings
    API_BASE_URL = "http://localhost:8000"
    API_TIMEOUT = 30
    
    # Database settings
    TEST_DATABASE_URL = "sqlite:///./test_clipizy.db"
    
    # Storage settings
    TEST_S3_BUCKET = "clipizy-test"
    TEST_S3_ENDPOINT_URL = "http://localhost:9000"
    TEST_S3_ACCESS_KEY = "admin"
    TEST_S3_SECRET_KEY = "admin123"
    
    # Test user credentials
    TEST_USER_EMAIL = "test@example.com"
    TEST_USER_PASSWORD = "testpassword123"
    TEST_USER_NAME = "Test User"
    
    # Test project settings
    TEST_PROJECT_NAME = "Test Project"
    TEST_PROJECT_DESCRIPTION = "Test project for testing"
    TEST_PROJECT_TYPE = "music-clip"
    
    # File settings
    TEST_AUDIO_FILE_SIZE = 1024 * 1024  # 1MB
    TEST_IMAGE_FILE_SIZE = 512 * 1024   # 512KB
    TEST_VIDEO_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Performance thresholds
    API_RESPONSE_TIME_THRESHOLD = 1.0  # seconds
    STORAGE_OPERATION_THRESHOLD = 2.0  # seconds
    DATABASE_QUERY_THRESHOLD = 0.5     # seconds
    
    # Test flags
    RUN_SLOW_TESTS = os.getenv("RUN_SLOW_TESTS", "false").lower() == "true"
    RUN_INTEGRATION_TESTS = os.getenv("RUN_INTEGRATION_TESTS", "true").lower() == "true"
    RUN_PERFORMANCE_TESTS = os.getenv("RUN_PERFORMANCE_TESTS", "false").lower() == "true"
    
    # Logging
    LOG_LEVEL = os.getenv("TEST_LOG_LEVEL", "INFO")
    VERBOSE_OUTPUT = os.getenv("VERBOSE_TESTS", "false").lower() == "true"
    
    # Cleanup
    CLEANUP_AFTER_TESTS = os.getenv("CLEANUP_AFTER_TESTS", "true").lower() == "true"
    KEEP_TEST_FILES = os.getenv("KEEP_TEST_FILES", "false").lower() == "true"
    
    @classmethod
    def get_test_database_url(cls):
        """Get test database URL"""
        return cls.TEST_DATABASE_URL
    
    @classmethod
    def get_test_storage_config(cls):
        """Get test storage configuration"""
        return {
            "bucket": cls.TEST_S3_BUCKET,
            "endpoint_url": cls.TEST_S3_ENDPOINT_URL,
            "access_key": cls.TEST_S3_ACCESS_KEY,
            "secret_key": cls.TEST_S3_SECRET_KEY
        }
    
    @classmethod
    def get_test_user_data(cls):
        """Get test user data"""
        return {
            "email": cls.TEST_USER_EMAIL,
            "password": cls.TEST_USER_PASSWORD,
            "name": cls.TEST_USER_NAME
        }
    
    @classmethod
    def get_test_project_data(cls):
        """Get test project data"""
        return {
            "name": cls.TEST_PROJECT_NAME,
            "description": cls.TEST_PROJECT_DESCRIPTION,
            "type": cls.TEST_PROJECT_TYPE
        }
    
    @classmethod
    def is_slow_test_enabled(cls):
        """Check if slow tests are enabled"""
        return cls.RUN_SLOW_TESTS
    
    @classmethod
    def is_integration_test_enabled(cls):
        """Check if integration tests are enabled"""
        return cls.RUN_INTEGRATION_TESTS
    
    @classmethod
    def is_performance_test_enabled(cls):
        """Check if performance tests are enabled"""
        return cls.RUN_PERFORMANCE_TESTS

# Environment-specific configurations
class DevelopmentTestConfig(TestConfig):
    """Development test configuration"""
    API_BASE_URL = "http://localhost:8000"
    TEST_S3_ENDPOINT_URL = "http://localhost:9000"
    VERBOSE_OUTPUT = True

class ProductionTestConfig(TestConfig):
    """Production test configuration"""
    API_BASE_URL = "https://api.clipizy.com"
    TEST_S3_ENDPOINT_URL = "https://s3.clipizy.com"
    VERBOSE_OUTPUT = False

class StagingTestConfig(TestConfig):
    """Staging test configuration"""
    API_BASE_URL = "https://staging-api.clipizy.com"
    TEST_S3_ENDPOINT_URL = "https://staging-s3.clipizy.com"
    VERBOSE_OUTPUT = True

def get_test_config():
    """Get test configuration based on environment"""
    env = os.getenv("TEST_ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionTestConfig()
    elif env == "staging":
        return StagingTestConfig()
    else:
        return DevelopmentTestConfig()

# Global test configuration instance
test_config = get_test_config()
