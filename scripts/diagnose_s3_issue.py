#!/usr/bin/env python3
"""
Complete diagnostic for S3 upload and track analysis issues
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded .env file from: {env_path}")
    else:
        print(f"⚠️  No .env file found at: {env_path}")
except ImportError:
    print("⚠️  python-dotenv not installed, trying to load .env manually...")
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Manually loaded .env file from: {env_path}")

print()
print("🔍 CLIPIZY S3 DIAGNOSTIC TOOL")
print("=" * 70)
print()

print("STEP 1: CHECKING ENVIRONMENT VARIABLES")
print("-" * 70)

env_vars = {
    'S3_BUCKET': os.getenv('S3_BUCKET'),
    'S3_REGION': os.getenv('S3_REGION'),
    'S3_ENDPOINT_URL': os.getenv('S3_ENDPOINT_URL'),
    'S3_ACCESS_KEY': os.getenv('S3_ACCESS_KEY'),
    'S3_SECRET_KEY': os.getenv('S3_SECRET_KEY'),
}

all_set = True
for key, value in env_vars.items():
    if value:
        if 'KEY' in key:
            display = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
        else:
            display = value
        print(f"✅ {key}: {display}")
    else:
        print(f"❌ {key}: NOT SET")
        all_set = False

print()

if not all_set:
    print("❌ CRITICAL: Some S3 environment variables are missing!")
    print()
    print("To fix this:")
    print("1. Create a .env file in the project root:")
    print("   cp env.template .env")
    print()
    print("2. Edit .env and add your S3 credentials:")
    print("   S3_BUCKET=your-bucket-name")
    print("   S3_REGION=us-east-1")
    print("   S3_ENDPOINT_URL=https://s3.amazonaws.com")
    print("   S3_ACCESS_KEY=your-access-key")
    print("   S3_SECRET_KEY=your-secret-key")
    print()
    print("3. Restart the backend:")
    print("   pkill -f uvicorn")
    print("   # Then restart with ./app.sh or your startup command")
    print()
    sys.exit(1)

print("\nSTEP 2: CHECKING SETTINGS MODULE")
print("-" * 70)

try:
    from api.config.settings import settings
    print(f"✅ Settings loaded successfully")
    print(f"   Bucket: {settings.s3_bucket}")
    print(f"   Region: {settings.s3_region}")
    print(f"   Endpoint: {settings.s3_endpoint_url}")
    print(f"   Access Key Set: {'Yes' if settings.s3_access_key else 'No'}")
    print(f"   Secret Key Set: {'Yes' if settings.s3_secret_key else 'No'}")
except Exception as e:
    print(f"❌ Failed to load settings: {e}")
    sys.exit(1)

print()

print("STEP 3: CHECKING BACKEND STORAGE SERVICE")
print("-" * 70)

try:
    from api.services.storage.backend_storage import backend_storage_service
    
    if backend_storage_service.s3_client:
        print("✅ Backend storage service initialized with S3 client")
        print(f"   Bucket: {backend_storage_service.bucket_name}")
    else:
        print("❌ Backend storage service initialized WITHOUT S3 client")
        print("   This means S3 initialization failed during service startup")
        print()
        print("Common causes:")
        print("   1. Invalid S3 credentials")
        print("   2. Bucket doesn't exist")
        print("   3. No network access to S3")
        print("   4. IAM permissions insufficient")
        sys.exit(1)
except Exception as e:
    print(f"❌ Failed to initialize backend storage service: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

print("STEP 4: TESTING S3 BUCKET ACCESS")
print("-" * 70)

try:
    backend_storage_service.s3_client.head_bucket(Bucket=settings.s3_bucket)
    print(f"✅ Successfully connected to bucket: {settings.s3_bucket}")
except Exception as e:
    print(f"❌ Cannot access bucket '{settings.s3_bucket}': {e}")
    print()
    print("Possible issues:")
    print("   1. Bucket doesn't exist - create it in AWS console")
    print("   2. Wrong bucket name - check S3_BUCKET environment variable")
    print("   3. No permissions - check IAM user permissions")
    print("   4. Wrong region - check S3_REGION matches bucket region")
    sys.exit(1)

print()

print("STEP 5: TESTING FILE UPLOAD")
print("-" * 70)

try:
    import io
    from fastapi import UploadFile
    
    test_content = b"Test audio file for diagnostic purposes"
    test_file = io.BytesIO(test_content)
    
    upload_file = UploadFile(
        filename="diagnostic-test.mp3",
        file=test_file
    )
    upload_file.content_type = "audio/mpeg"
    upload_file.size = len(test_content)
    
    test_key = "diagnostic-tests/test-upload.mp3"
    
    print(f"Uploading test file to: {test_key}")
    
    import asyncio
    asyncio.run(backend_storage_service._upload_to_s3(upload_file, test_key))
    
    print("✅ Upload successful!")
    
    print("Verifying file exists...")
    exists = backend_storage_service.file_exists(test_key)
    if exists:
        print("✅ File verified in S3")
    else:
        print("❌ File upload succeeded but file not found in S3")
        sys.exit(1)
    
    print("Testing download...")
    content = backend_storage_service.get_file_content(test_key)
    if content == test_content:
        print("✅ Download successful and content verified")
    else:
        print("❌ Downloaded content doesn't match uploaded content")
        sys.exit(1)
    
    print("Cleaning up...")
    backend_storage_service.s3_client.delete_object(
        Bucket=settings.s3_bucket,
        Key=test_key
    )
    print("✅ Cleanup complete")
    
except Exception as e:
    print(f"❌ File upload test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

print("STEP 6: CHECKING DATABASE CONNECTION")
print("-" * 70)

try:
    from api.services.database import SessionLocal
    
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
        print("✅ Database connection successful")
    finally:
        db.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("   This may cause issues with track storage")

print()

print("=" * 70)
print("🎉 ALL DIAGNOSTIC TESTS PASSED!")
print("=" * 70)
print()
print("Your S3 configuration is working correctly.")
print()
print("If you're still experiencing issues with track uploads:")
print()
print("1. CHECK BACKEND LOGS for specific error messages")
print("   Look for lines containing 'S3' or 'storage' or 'track'")
print()
print("2. RESTART THE BACKEND to ensure new environment variables are loaded:")
print("   pkill -f uvicorn")
print("   ./app.sh")
print()
print("3. TEST TRACK UPLOAD with the frontend")
print("   - Upload a track in the music clip creator")
print("   - Check browser console for errors")
print("   - Check Network tab for the exact error response")
print()
print("4. RUN THE SPECIFIC TRACK UPLOAD TEST:")
print("   python scripts/test_track_upload.py")
print()
print("=" * 70)

