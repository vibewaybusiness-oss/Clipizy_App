#!/usr/bin/env python3
"""
Test script to verify Amazon S3 connection and configuration
"""

import os
import sys
from pathlib import Path
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, NoCredentialsError

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

def test_s3_connection():
    """Test S3 connection with current configuration"""
    
    # Get configuration from environment
    bucket_name = os.getenv("S3_BUCKET", "clipizy-dev")
    region = os.getenv("S3_REGION", "us-east-1")
    endpoint_url = os.getenv("S3_ENDPOINT_URL", "https://s3.amazonaws.com")
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    
    # Fix endpoint URL for region-specific access
    if endpoint_url == "https://s3.amazonaws.com" and region != "us-east-1":
        endpoint_url = f"https://s3.{region}.amazonaws.com"
    elif endpoint_url == "https://s3.amazonaws.com" and region == "us-east-1":
        # For us-east-1, we can use None to let boto3 handle it
        endpoint_url = None
    
    print("🔍 Testing Amazon S3 Connection")
    print("=" * 50)
    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    print(f"Endpoint: {endpoint_url}")
    print(f"Access Key: {'✅ Set' if access_key else '❌ Missing'}")
    print(f"Secret Key: {'✅ Set' if secret_key else '❌ Missing'}")
    print()
    
    if not access_key or not secret_key:
        print("❌ S3 credentials are missing!")
        print("Please set S3_ACCESS_KEY and S3_SECRET_KEY environment variables")
        return False
    
    try:
        # Initialize S3 client
        config = Config(
            region_name=region,
            signature_version='s3v4',
            retries={'max_attempts': 3, 'mode': 'adaptive'},
            read_timeout=30,
            connect_timeout=10
        )
        
        s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=config
        )
        
        # Test bucket access
        print("🔍 Testing bucket access...")
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Successfully connected to bucket: {bucket_name}")
        
        # Test list objects
        print("🔍 Testing list objects...")
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=5)
        object_count = response.get('KeyCount', 0)
        print(f"✅ Bucket contains {object_count} objects")
        
        # Test upload a small test file
        print("🔍 Testing file upload...")
        test_content = b"Test file for S3 connection verification"
        test_key = "test-connection.txt"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print(f"✅ Successfully uploaded test file: {test_key}")
        
        # Test download
        print("🔍 Testing file download...")
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read()
        if downloaded_content == test_content:
            print("✅ Successfully downloaded and verified test file")
        else:
            print("❌ Downloaded content doesn't match uploaded content")
            return False
        
        # Clean up test file
        print("🔍 Cleaning up test file...")
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Test file cleaned up")
        
        print()
        print("🎉 All S3 tests passed! Your Amazon S3 configuration is working correctly.")
        return True
        
    except NoCredentialsError:
        print("❌ AWS credentials not found or invalid")
        return False
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            print(f"❌ Bucket '{bucket_name}' does not exist")
            print("Please create the bucket or check the S3_BUCKET environment variable")
        elif error_code == 'AccessDenied':
            print("❌ Access denied to S3 bucket")
            print("Please check your S3_ACCESS_KEY and S3_SECRET_KEY permissions")
        else:
            print(f"❌ S3 error: {error_code} - {e.response['Error']['Message']}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_s3_connection()
    sys.exit(0 if success else 1)
