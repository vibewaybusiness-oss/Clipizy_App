# S3 TROUBLESHOOTING GUIDE

## Problem: Tracks Not Uploading to S3

### Error Message
```
POST http://localhost:8000/api/music-analysis/music/<track_id> 500 (Internal Server Error)
```

### Root Cause
The S3 environment variables are not loaded into the backend process. The backend needs these credentials to upload files to Amazon S3.

---

## 🔧 SOLUTION: Set Up S3 Credentials

### Option 1: Interactive Setup (Recommended)
Run the interactive setup script:
```bash
./scripts/setup_s3_env.sh
```

This will:
1. Create/update your `.env` file
2. Add your S3 credentials
3. Test the connection
4. Guide you through restarting the backend

### Option 2: Manual Setup

1. **Copy the environment template:**
```bash
cp env.template .env
```

2. **Edit `.env` and add your S3 credentials:**
```bash
nano .env
# or
vim .env
```

Add these lines:
```bash
S3_BUCKET=your-bucket-name
S3_REGION=us-east-1
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your-aws-access-key
S3_SECRET_KEY=your-aws-secret-key
```

3. **Test the connection:**
```bash
python3 scripts/test_s3_connection.py
```

4. **Restart the backend:**
```bash
pkill -f uvicorn
./app.sh
```

---

## 🧪 DIAGNOSTIC TOOLS

### 1. Complete S3 Diagnostic
Tests all aspects of S3 configuration:
```bash
python3 scripts/diagnose_s3_issue.py
```

**What it checks:**
- ✅ Environment variables are set
- ✅ Settings module loads correctly
- ✅ Backend storage service initializes
- ✅ S3 bucket is accessible
- ✅ File upload/download works
- ✅ Database connection works

### 2. Simple S3 Connection Test
Quick test of S3 connectivity:
```bash
python3 scripts/test_s3_connection.py
```

**What it tests:**
- Bucket access
- File upload
- File download
- File deletion

### 3. Track Upload Test
Specific test for track upload functionality:
```bash
python3 scripts/test_track_upload.py
```

**What it tests:**
- S3 credentials loaded
- Backend storage service initialized
- Direct S3 upload works
- Service-based upload works

---

## 🐛 COMMON ISSUES

### Issue 1: "S3 credentials not found"
**Cause:** Environment variables not set

**Solution:**
1. Run `./scripts/setup_s3_env.sh`
2. OR manually create `.env` file with credentials
3. Restart backend

---

### Issue 2: "Bucket does not exist"
**Cause:** S3 bucket hasn't been created in AWS

**Solution:**
1. Log into AWS Console
2. Go to S3 service
3. Create bucket with name matching `S3_BUCKET` variable
4. Ensure bucket is in the correct region

---

### Issue 3: "Access Denied"
**Cause:** IAM user lacks permissions

**Solution:**
Add these permissions to your IAM user:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:HeadBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

---

### Issue 4: Backend not loading .env file
**Cause:** Backend was started before .env was created

**Solution:**
1. Stop the backend: `pkill -f uvicorn`
2. Ensure `.env` exists with correct values
3. Start backend: `./app.sh`

**Alternative:** Export variables before starting:
```bash
export S3_BUCKET=your-bucket
export S3_REGION=us-east-1
export S3_ENDPOINT_URL=https://s3.amazonaws.com
export S3_ACCESS_KEY=your-key
export S3_SECRET_KEY=your-secret
./app.sh
```

---

### Issue 5: "S3 client initialization failed"
**Cause:** Invalid credentials or network issues

**Solution:**
1. Verify credentials are correct in AWS Console
2. Check network connectivity to AWS
3. Try different endpoint URL based on region:
   - `https://s3.us-east-1.amazonaws.com` (US East)
   - `https://s3.us-west-2.amazonaws.com` (US West)
   - `https://s3.eu-west-1.amazonaws.com` (EU)

---

## 📋 VERIFICATION CHECKLIST

After setting up S3, verify everything works:

- [ ] `.env` file exists with S3 credentials
- [ ] `python3 scripts/diagnose_s3_issue.py` passes all tests
- [ ] Backend logs show "S3 client initialized successfully"
- [ ] Can upload tracks through frontend without 500 errors
- [ ] Tracks appear in S3 bucket
- [ ] Can analyze uploaded tracks

---

## 🔍 DEBUGGING TIPS

### Check Backend Logs
Look for S3-related messages:
```bash
# If using app.sh logs
tail -f logs/backend.log | grep -i s3

# Or check console output
# Look for lines containing:
# - "S3 client initialized"
# - "Failed to initialize S3"
# - "S3 upload failed"
```

### Verify Environment Variables Loaded
```bash
python3 -c "from api.config.settings import settings; print(f'Bucket: {settings.s3_bucket}'); print(f'Has creds: {bool(settings.s3_access_key)}')"
```

### Test S3 from Python Console
```python
import boto3
from api.config.settings import settings

s3 = boto3.client(
    's3',
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key
)

# Test bucket access
s3.head_bucket(Bucket=settings.s3_bucket)
print("Success!")
```

---

## 📞 STILL HAVING ISSUES?

1. Run full diagnostic: `python3 scripts/diagnose_s3_issue.py`
2. Check the error output carefully
3. Ensure your S3 bucket exists in AWS
4. Verify IAM permissions
5. Confirm backend was restarted after setting credentials
6. Check browser console for specific error messages
7. Check backend logs for detailed error traces

---

## 🎯 QUICK FIX SUMMARY

**Most common solution:**
```bash
# 1. Set up credentials
./scripts/setup_s3_env.sh

# 2. Restart backend
pkill -f uvicorn
./app.sh

# 3. Verify
python3 scripts/test_s3_connection.py
```




