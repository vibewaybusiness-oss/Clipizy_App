"""
Settings module for Clipizy application
Provides configuration settings from environment variables
"""

import os
from typing import Optional

class Settings:
    """Application settings"""
    
    def __init__(self):
        # Database settings
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clipizy")
        
        # Frontend settings
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        
        # S3 settings
        self.s3_bucket = os.getenv("S3_BUCKET", "clipizy-dev")
        self.s3_region = os.getenv("S3_REGION", "us-east-1")
        self.s3_endpoint_url = os.getenv("S3_ENDPOINT_URL", "https://s3.amazonaws.com")
        self.s3_access_key = os.getenv("S3_ACCESS_KEY")
        self.s3_secret_key = os.getenv("S3_SECRET_KEY")
        
        # OAuth settings
        self.oauth_github_client_id = os.getenv("OAUTH_GITHUB_CLIENT_ID")
        self.github_client_secret = os.getenv("GITHUB_CLIENT_SECRET")
        self.oauth_redirect_uri = os.getenv("OAUTH_REDIRECT_URI", f"{self.frontend_url}/auth/callback")
        
        # JWT settings
        self.jwt_secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.jwt_access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # API settings
        self.api_host = os.getenv("API_HOST", "localhost")
        self.api_port = int(os.getenv("API_PORT", "8000"))
        
        # CORS settings
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

# Create global settings instance
settings = Settings()
