#!/usr/bin/env python3
"""
Check S3 bucket existence and permissions
"""

import os
import sys
from pathlib import Path
import boto3
from botocore.exceptions import ClientError

# Load .env
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / '.env')
except:
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

bucket_name = os.getenv("S3_BUCKET", "clipizy-dev")
region = os.getenv("S3_REGION", "us-east-1")
access_key = os.getenv("S3_ACCESS_KEY")
secret_key = os.getenv("S3_SECRET_KEY")

print("🔍 S3 BUCKET CHECK")
print("=" * 60)
print(f"Bucket Name: {bucket_name}")
print(f"Region: {region}")
print()

# Create S3 client
s3 = boto3.client(
    's3',
    region_name=region,
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)

# List all buckets
print("📋 Listing all accessible buckets:")
print("-" * 60)
try:
    response = s3.list_buckets()
    buckets = response.get('Buckets', [])
    
    if not buckets:
        print("❌ No buckets found! This IAM user can't see any buckets.")
        print()
        print("Possible issues:")
        print("  1. IAM user has no S3 permissions")
        print("  2. Wrong credentials")
        print("  3. No buckets exist in this AWS account")
    else:
        print(f"✅ Found {len(buckets)} bucket(s):")
        print()
        found_target = False
        for bucket in buckets:
            name = bucket['Name']
            creation_date = bucket['CreationDate']
            is_target = " ← TARGET BUCKET" if name == bucket_name else ""
            print(f"  • {name} (created: {creation_date}){is_target}")
            if name == bucket_name:
                found_target = True
        
        print()
        if found_target:
            print(f"✅ Target bucket '{bucket_name}' EXISTS")
        else:
            print(f"❌ Target bucket '{bucket_name}' NOT FOUND")
            print(f"   You need to create it or update S3_BUCKET in .env")
            
except ClientError as e:
    error_code = e.response['Error']['Code']
    print(f"❌ Error: {error_code} - {e.response['Error']['Message']}")
    if error_code == 'AccessDenied':
        print()
        print("IAM user lacks permission to list buckets.")
        print("Trying to access the specific bucket directly...")

print()
print("🔍 Checking specific bucket access:")
print("-" * 60)

try:
    # Try to get bucket location
    response = s3.get_bucket_location(Bucket=bucket_name)
    location = response.get('LocationConstraint')
    if location is None:
        location = 'us-east-1'  # None means us-east-1
    
    print(f"✅ Bucket exists: {bucket_name}")
    print(f"✅ Bucket region: {location}")
    
    if location != region:
        print(f"⚠️  WARNING: Bucket region ({location}) doesn't match S3_REGION ({region})")
        print(f"   Update S3_REGION to '{location}' in .env")
    
    # Try to list objects
    print()
    print("Testing ListObjects permission...")
    response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
    print("✅ Can list objects")
    
    # Try to put object
    print("Testing PutObject permission...")
    s3.put_object(
        Bucket=bucket_name,
        Key='test-permissions.txt',
        Body=b'test'
    )
    print("✅ Can upload objects")
    
    # Try to get object
    print("Testing GetObject permission...")
    s3.get_object(Bucket=bucket_name, Key='test-permissions.txt')
    print("✅ Can download objects")
    
    # Clean up
    print("Testing DeleteObject permission...")
    s3.delete_object(Bucket=bucket_name, Key='test-permissions.txt')
    print("✅ Can delete objects")
    
    print()
    print("🎉 ALL PERMISSIONS OK!")
    
except ClientError as e:
    error_code = e.response['Error']['Code']
    error_msg = e.response['Error']['Message']
    
    print(f"❌ Error: {error_code} - {error_msg}")
    print()
    
    if error_code == 'NoSuchBucket':
        print(f"The bucket '{bucket_name}' does not exist.")
        print()
        print("To create it:")
        print(f"  1. Go to https://s3.console.aws.amazon.com/s3/")
        print(f"  2. Click 'Create bucket'")
        print(f"  3. Name: {bucket_name}")
        print(f"  4. Region: {region}")
        print(f"  5. Click 'Create bucket'")
        
    elif error_code in ['AccessDenied', 'Forbidden', '403']:
        print("IAM user lacks permissions for this bucket.")
        print()
        print("Required IAM permissions:")
        print("""
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::""" + bucket_name + """"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::""" + bucket_name + """/*"
    }
  ]
}
        """)
    
    sys.exit(1)

print()
print("=" * 60)
print("✅ S3 configuration is correct!")
print("   You can now restart your backend and upload tracks.")
print("=" * 60)









