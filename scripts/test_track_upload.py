#!/usr/bin/env python3
"""
Test script to diagnose track upload issues to S3
"""

import os
import sys
import io
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

from api.config.settings import settings
from api.services.storage.backend_storage import backend_storage_service
from fastapi import UploadFile

def test_s3_credentials():
    """Test if S3 credentials are properly configured"""
    print("🔍 CHECKING S3 CONFIGURATION")
    print("=" * 60)
    print(f"Bucket: {settings.s3_bucket}")
    print(f"Region: {settings.s3_region}")
    print(f"Endpoint: {settings.s3_endpoint_url}")
    print(f"Access Key: {'✅ Set' if settings.s3_access_key else '❌ Missing'}")
    print(f"Secret Key: {'✅ Set' if settings.s3_secret_key else '❌ Missing'}")
    print(f"S3 Client Initialized: {'✅ Yes' if backend_storage_service.s3_client else '❌ No'}")
    print()
    
    if not settings.s3_access_key or not settings.s3_secret_key:
        print("❌ S3 credentials are missing in environment variables!")
        return False
    
    if not backend_storage_service.s3_client:
        print("❌ S3 client failed to initialize!")
        return False
    
    return True

def test_bucket_access():
    """Test if we can access the S3 bucket"""
    print("🔍 TESTING BUCKET ACCESS")
    print("=" * 60)
    
    if not backend_storage_service.s3_client:
        print("❌ S3 client not available")
        return False
    
    try:
        backend_storage_service.s3_client.head_bucket(Bucket=settings.s3_bucket)
        print(f"✅ Successfully accessed bucket: {settings.s3_bucket}")
        return True
    except Exception as e:
        print(f"❌ Failed to access bucket: {e}")
        return False

def test_direct_upload():
    """Test direct upload to S3"""
    print("\n🔍 TESTING DIRECT UPLOAD TO S3")
    print("=" * 60)
    
    if not backend_storage_service.s3_client:
        print("❌ S3 client not available")
        return False
    
    try:
        test_content = b"Test audio file content for track upload"
        test_key = "test-uploads/test-track.mp3"
        
        print(f"Uploading test file to: {test_key}")
        backend_storage_service.s3_client.put_object(
            Bucket=settings.s3_bucket,
            Key=test_key,
            Body=test_content,
            ContentType='audio/mpeg'
        )
        print("✅ Direct upload successful!")
        
        print("Verifying file exists...")
        backend_storage_service.s3_client.head_object(
            Bucket=settings.s3_bucket,
            Key=test_key
        )
        print("✅ File verified in S3!")
        
        print("Cleaning up test file...")
        backend_storage_service.s3_client.delete_object(
            Bucket=settings.s3_bucket,
            Key=test_key
        )
        print("✅ Cleanup successful!")
        
        return True
    except Exception as e:
        print(f"❌ Direct upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_upload_via_service():
    """Test upload via BackendStorageService"""
    print("\n🔍 TESTING UPLOAD VIA BACKEND STORAGE SERVICE")
    print("=" * 60)
    
    if not backend_storage_service.s3_client:
        print("❌ S3 client not available")
        return False
    
    try:
        test_content = b"Test audio file content for service upload"
        test_file = io.BytesIO(test_content)
        
        upload_file = UploadFile(
            filename="test-track.mp3",
            file=test_file
        )
        upload_file.content_type = "audio/mpeg"
        upload_file.size = len(test_content)
        
        test_key = "test-uploads/service-test-track.mp3"
        
        print(f"Uploading via service to: {test_key}")
        
        import asyncio
        asyncio.run(backend_storage_service._upload_to_s3(upload_file, test_key))
        
        print("✅ Service upload successful!")
        
        print("Verifying file exists...")
        exists = backend_storage_service.file_exists(test_key)
        if exists:
            print("✅ File verified in S3!")
        else:
            print("❌ File not found in S3!")
            return False
        
        print("Cleaning up test file...")
        backend_storage_service.s3_client.delete_object(
            Bucket=settings.s3_bucket,
            Key=test_key
        )
        print("✅ Cleanup successful!")
        
        return True
    except Exception as e:
        print(f"❌ Service upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_music_analysis_endpoint():
    """Check what might be wrong with the music analysis endpoint"""
    print("\n🔍 CHECKING MUSIC ANALYSIS ENDPOINT ISSUE")
    print("=" * 60)
    print("Error: POST http://localhost:8000/api/music-analysis/music/... 500")
    print("\nPossible causes:")
    print("1. S3 credentials not loaded when backend starts")
    print("2. S3 bucket doesn't exist or incorrect name")
    print("3. IAM permissions insufficient")
    print("4. Network connectivity issues to AWS S3")
    print("5. Endpoint URL incorrect (should be https://s3.amazonaws.com or region-specific)")
    print("\nTo fix:")
    print("1. Ensure .env file exists with S3 credentials")
    print("2. Restart the backend after setting credentials")
    print("3. Check backend logs for S3 initialization errors")
    print()

def main():
    """Run all tests"""
    print("🚀 TRACK UPLOAD TO S3 DIAGNOSTIC TEST")
    print("=" * 60)
    print()
    
    success = True
    
    if not test_s3_credentials():
        success = False
        print("\n⚠️  Cannot proceed without S3 credentials")
        check_music_analysis_endpoint()
        return 1
    
    if not test_bucket_access():
        success = False
        print("\n⚠️  Cannot access S3 bucket")
        check_music_analysis_endpoint()
        return 1
    
    if not test_direct_upload():
        success = False
    
    if not test_upload_via_service():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("\nS3 upload is working correctly.")
        print("If you're still getting 500 errors, check:")
        print("1. Backend logs for specific error messages")
        print("2. Database connection (track metadata)")
        print("3. The music-analysis endpoint implementation")
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease fix the issues above and:")
        print("1. Set your S3 credentials in .env file")
        print("2. Restart the backend service")
        print("3. Run this test again")
        check_music_analysis_endpoint()
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
