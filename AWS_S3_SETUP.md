# AWS S3 Setup Guide for Clipizy

This guide will help you set up AWS S3 storage for your Clipizy application instead of using the local MinIO S3-compatible service.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured (optional but recommended)
- Access to AWS Console

## Step 1: Create S3 Buckets

### Production Bucket
1. Log into AWS Console
2. Navigate to S3 service
3. Click "Create bucket"
4. Configure the bucket:
   - **Bucket name**: `clipizy-prod` (or your preferred name)
   - **Region**: `us-east-1` (or your preferred region)
   - **Block Public Access**: Keep all settings enabled for security
   - **Bucket Versioning**: Enable (recommended)
   - **Default encryption**: Enable with AES-256 or AWS KMS

### Development Bucket
1. Create another bucket for development:
   - **Bucket name**: `clipizy-dev`
   - **Region**: Same as production bucket
   - **Block Public Access**: Keep all settings enabled
   - **Bucket Versioning**: Enable
   - **Default encryption**: Enable

### Testing Bucket (Optional)
1. Create a bucket for testing:
   - **Bucket name**: `clipizy-test`
   - **Region**: Same as other buckets
   - **Block Public Access**: Keep all settings enabled
   - **Bucket Versioning**: Enable
   - **Default encryption**: Enable

## Step 2: Create IAM User and Policy

### Create IAM User
1. Navigate to IAM service in AWS Console
2. Click "Users" → "Create user"
3. **User name**: `clipizy-s3-user`
4. **Access type**: Programmatic access
5. Click "Next"

### Create Custom Policy
1. Click "Attach policies directly"
2. Click "Create policy"
3. Use JSON editor and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket",
                "s3:GetObjectVersion",
                "s3:PutObjectAcl",
                "s3:GetObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::clipizy-prod",
                "arn:aws:s3:::clipizy-prod/*",
                "arn:aws:s3:::clipizy-dev",
                "arn:aws:s3:::clipizy-dev/*",
                "arn:aws:s3:::clipizy-test",
                "arn:aws:s3:::clipizy-test/*"
            ]
        }
    ]
}
```

4. **Policy name**: `ClipizyS3Policy`
5. Click "Create policy"

### Attach Policy to User
1. Go back to user creation
2. Search for and select `ClipizyS3Policy`
3. Click "Next" → "Create user"
4. **IMPORTANT**: Save the Access Key ID and Secret Access Key

## Step 3: Configure Environment Variables

### Option 1: Using .env file (Recommended for Development)
Create a `.env` file in your project root:

```bash
# AWS S3 Configuration
S3_BUCKET=clipizy-dev
S3_REGION=us-east-1
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your_access_key_here
S3_SECRET_KEY=your_secret_key_here

# Other configurations...
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clipizy
FRONTEND_URL=http://localhost:3000
```

### Option 2: Using AWS CLI (Recommended for Production)
Configure AWS CLI with your credentials:

```bash
aws configure
```

Then set these environment variables:
```bash
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1
```

### Option 3: Using AWS IAM Roles (Recommended for EC2/ECS)
If running on AWS infrastructure, use IAM roles instead of access keys for better security.

## Step 4: Update Application Configuration

The application configuration files have been updated to use AWS S3:

- `api/config/json/production.json` - Uses `clipizy-prod` bucket
- `api/config/json/development.json` - Uses `clipizy-dev` bucket  
- `api/config/json/testing.json` - Uses `clipizy-test` bucket

## Step 5: Test the Connection

### Test S3 Connection
You can test the S3 connection using the AWS CLI:

```bash
# Test bucket access
aws s3 ls s3://clipizy-dev

# Test file upload
echo "test" > test.txt
aws s3 cp test.txt s3://clipizy-dev/
aws s3 rm s3://clipizy-dev/test.txt
rm test.txt
```

### Test Application Connection
Start your application and check the logs for S3 connection status:

```bash
# Start the backend
cd api
uvicorn main:app --reload

# Look for this log message:
# "S3 client initialized successfully with bucket: clipizy-dev"
```

## Step 6: Migrate Existing Data (If Applicable)

If you have existing data in your local MinIO setup, you'll need to migrate it:

### Using AWS CLI
```bash
# Sync local MinIO data to AWS S3
aws s3 sync s3://clipizy s3://clipizy-dev --source-region us-east-1 --endpoint-url http://localhost:9000
```

### Using MinIO Client
```bash
# If you have mc (MinIO client) installed
mc mirror local/clipizy aws/clipizy-dev
```

## Security Best Practices

1. **Never commit AWS credentials to version control**
2. **Use IAM roles when possible instead of access keys**
3. **Rotate access keys regularly**
4. **Enable S3 bucket versioning**
5. **Enable S3 bucket encryption**
6. **Use least privilege principle for IAM policies**
7. **Enable CloudTrail for S3 API logging**
8. **Set up S3 bucket policies for additional security**

## Troubleshooting

### Common Issues

1. **Access Denied Error**
   - Check IAM policy permissions
   - Verify bucket names match configuration
   - Ensure access keys are correct

2. **Bucket Not Found Error**
   - Verify bucket exists in the correct region
   - Check bucket name spelling
   - Ensure you have access to the bucket

3. **Connection Timeout**
   - Check network connectivity
   - Verify endpoint URL is correct
   - Check AWS region configuration

### Debug Mode
Enable debug logging to troubleshoot S3 issues:

```bash
export LOG_LEVEL=DEBUG
```

## Cost Optimization

1. **Use S3 Intelligent Tiering** for automatic cost optimization
2. **Set up lifecycle policies** to transition old files to cheaper storage classes
3. **Monitor usage** with AWS Cost Explorer
4. **Use appropriate storage classes** (Standard, IA, Glacier) based on access patterns

## Next Steps

1. Update your deployment scripts to use AWS S3
2. Remove MinIO Docker containers from your local setup
3. Update CI/CD pipelines to use AWS S3
4. Consider setting up CloudFront CDN for better performance
5. Implement S3 backup strategies

For more information, refer to the [AWS S3 Documentation](https://docs.aws.amazon.com/s3/).
