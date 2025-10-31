#!/usr/bin/env python3
"""
clipizy Backend Startup Script
"""
import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path so we can import the api module
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load .env file BEFORE any other imports that might need environment variables
from dotenv import load_dotenv
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"✅ Loaded environment variables from {env_path}")
    # Verify critical environment variables are loaded
    s3_key = os.getenv("S3_ACCESS_KEY")
    s3_secret = os.getenv("S3_SECRET_KEY")
    s3_bucket = os.getenv("S3_BUCKET")
    runpod_key = os.getenv("RUNPOD_API_KEY")
    if s3_key and s3_secret and s3_bucket:
        print(f"✅ S3 credentials found (bucket: {s3_bucket})")
    else:
        print(f"⚠️  S3 credentials missing - S3_ACCESS_KEY={'set' if s3_key else 'NOT SET'}, S3_SECRET_KEY={'set' if s3_secret else 'NOT SET'}, S3_BUCKET={'set' if s3_bucket else 'NOT SET'}")
    if runpod_key:
        print(f"✅ RunPod API key found")
    else:
        print(f"⚠️  RunPod API key not found")
else:
    print(f"⚠️  .env file not found at {env_path}, using environment variables only")

import uvicorn

def check_database_health():
    """
    Check if database is ready before starting FastAPI
    """
    try:
        from sqlalchemy import create_engine, text
        import time
        
        database_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clipizy")
        
        # PostgreSQL health check required
            
        # For PostgreSQL, check connection
        for attempt in range(15):
            try:
                engine = create_engine(database_url)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                print(f"✅ Database connection successful (attempt {attempt + 1})")
                return True
            except Exception as e:
                print(f"⚠️ Database connection attempt {attempt + 1} failed: {e}")
                if attempt < 14:
                    time.sleep(2)
                else:
                    print(f"❌ Database connection failed after 15 attempts")
                    return False
        return False
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False

def create_database_tables():
    """
    Create database tables if they don't exist
    """
    try:
        from api.db import create_tables
        create_tables()
        print("✅ Database tables created/verified")
        return True
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False


if __name__ == "__main__":
    # Set environment variables
    # Only set default if not already set by the calling script
    if "DATABASE_URL" not in os.environ:
        os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/clipizy")
    os.environ.setdefault("BACKEND_URL", "http://localhost:8000")
    # Set uvicorn configuration for large request bodies
    os.environ.setdefault("UVICORN_LIMIT_MAX_REQUESTS", "1000")
    os.environ.setdefault("UVICORN_LIMIT_CONCURRENCY", "1000")
    os.environ.setdefault("UVICORN_TIMEOUT_KEEP_ALIVE", "30")

    print("🔍 Checking database health before starting FastAPI...")
    print(f"🗄️  Using database URL: {os.environ.get('DATABASE_URL', 'Not set')}")

    # Check database health
    db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/clipizy')
    
    if not check_database_health():
        print("❌ Database connection failed. Please check your database connection.")
        sys.exit(1)
    else:
        print("✅ Database is ready.")

    # Create database tables
    print("🔧 Creating/verifying database tables...")
    if not create_database_tables():
        print("❌ Failed to create database tables. Exiting.")
        sys.exit(1)

    print("🚀 Starting FastAPI server...")

    # Start the FastAPI server with reload enabled for development
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        limit_max_requests=1000,
        limit_concurrency=1000,
        timeout_keep_alive=300,  # 5 minutes for large file uploads
        timeout_graceful_shutdown=30
    )
