# 🚀 QUICK START: Fix S3 Upload Issues

## The Problem
❌ Tracks won't upload to S3  
❌ Getting 500 errors when analyzing music  
❌ Backend can't connect to Amazon S3

## The Solution (2 Minutes)

### Step 1: Set Up Credentials
```bash
./scripts/setup_s3_env.sh
```

**You'll be asked for:**
- S3 Bucket Name (the bucket you created in AWS)
- S3 Region (e.g., `us-east-1`)
- S3 Endpoint URL (default: `https://s3.amazonaws.com`)
- S3 Access Key (from AWS IAM user)
- S3 Secret Key (from AWS IAM user)

### Step 2: Restart Backend
```bash
pkill -f uvicorn
./app.sh
```

### Step 3: Verify
```bash
python3 scripts/diagnose_s3_issue.py
```

✅ If all tests pass, you're done!

---

## Don't Have S3 Credentials Yet?

### Create AWS S3 Bucket
1. Go to [AWS S3 Console](https://console.aws.amazon.com/s3)
2. Click "Create bucket"
3. Name it `clipizy-dev`
4. Choose your region (e.g., `us-east-1`)
5. Keep default settings
6. Click "Create bucket"

### Create IAM User
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam)
2. Click "Users" → "Add users"
3. Username: `clipizy-s3`
4. Access type: "Programmatic access"
5. Permissions: "Attach existing policies directly"
6. Search and attach: "AmazonS3FullAccess" (or create custom policy)
7. Click through and "Create user"
8. **Save the Access Key ID and Secret Access Key**

### Set Permissions (Custom Policy)
If you want minimal permissions, use this policy:
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
        "arn:aws:s3:::clipizy-dev",
        "arn:aws:s3:::clipizy-dev/*"
      ]
    }
  ]
}
```

---

## Already Have Credentials?

### Manual Setup
```bash
# Create .env file
cp env.template .env

# Edit it
nano .env
```

Add these lines:
```bash
S3_BUCKET=clipizy-dev
S3_REGION=us-east-1
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY=your-access-key-here
S3_SECRET_KEY=your-secret-key-here
```

Save and restart backend:
```bash
pkill -f uvicorn
./app.sh
```

---

## Verification Checklist

- [ ] Created S3 bucket in AWS
- [ ] Created IAM user with S3 permissions
- [ ] Ran `./scripts/setup_s3_env.sh` or created `.env` manually
- [ ] `.env` file contains all S3 credentials
- [ ] Restarted backend server
- [ ] Ran `python3 scripts/diagnose_s3_issue.py` - all tests pass
- [ ] Can upload tracks through frontend
- [ ] No 500 errors when analyzing music

---

## Still Not Working?

### Check Backend Logs
```bash
tail -f logs/backend.log | grep -i s3
```

Look for:
- ✅ "S3 client initialized successfully"
- ❌ "S3 client initialization failed"

### Run Diagnostics
```bash
# Complete diagnostic
python3 scripts/diagnose_s3_issue.py

# Just test connection
python3 scripts/test_s3_connection.py

# Test track upload
python3 scripts/test_track_upload.py
```

### Common Issues

**"S3 credentials not found"**
→ `.env` file missing or not loaded  
→ Restart backend after creating `.env`

**"Bucket does not exist"**
→ Create bucket in AWS Console  
→ Check bucket name matches `.env`

**"Access Denied"**
→ IAM user needs S3 permissions  
→ Add policy shown above

**Backend won't start**
→ Check DATABASE_URL is also set in `.env`  
→ Make sure PostgreSQL is running

---

## Need More Help?

📖 **Full Documentation:**
- [S3_MIGRATION_SUMMARY.md](./S3_MIGRATION_SUMMARY.md) - Complete migration details
- [S3_TROUBLESHOOTING.md](./scripts/S3_TROUBLESHOOTING.md) - Detailed troubleshooting
- [AWS_S3_SETUP.md](./AWS_S3_SETUP.md) - AWS configuration guide

🧪 **Diagnostic Tools:**
- `scripts/diagnose_s3_issue.py` - Complete diagnostic
- `scripts/test_s3_connection.py` - Connection test
- `scripts/test_track_upload.py` - Track upload test

---

## TL;DR

```bash
# 1. Set up S3 credentials (creates .env file)
./scripts/setup_s3_env.sh

# 2. Restart backend
pkill -f uvicorn && ./app.sh

# 3. Done! Test by uploading a track
```

**That's it!** 🎉







