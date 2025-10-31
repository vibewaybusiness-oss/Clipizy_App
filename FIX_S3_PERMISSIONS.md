# 🔐 FIX S3 PERMISSIONS

## Issue Found

Your IAM user `Runpod` (arn:aws:iam::188594592347:user/Runpod) **does not have S3 permissions**.

This is why you're getting **403 Forbidden** errors when trying to upload tracks.

---

## ✅ SOLUTION: Add S3 Permissions to IAM User

### Option 1: AWS Console (Easiest)

1. **Go to IAM Console:**
   https://console.aws.amazon.com/iam/

2. **Navigate to Users:**
   - Click "Users" in the left sidebar
   - Find and click on user: `Runpod`

3. **Add Permissions:**
   - Click "Add permissions" → "Attach policies directly"
   
4. **Option A - Full S3 Access (Quick but less secure):**
   - Search for: `AmazonS3FullAccess`
   - Check the box
   - Click "Next" → "Add permissions"

5. **Option B - Specific Bucket Access (Recommended):**
   - Click "Create policy"
   - Click "JSON" tab
   - Paste this policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ListBuckets",
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation"
      ],
      "Resource": "*"
    },
    {
      "Sid": "BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::clipizy-dev"
    },
    {
      "Sid": "ObjectAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::clipizy-dev/*"
    }
  ]
}
```

   - Click "Next: Tags" → "Next: Review"
   - Name: `Clipizy-S3-Access`
   - Click "Create policy"
   - Go back to user `Runpod` → "Add permissions"
   - Search for: `Clipizy-S3-Access`
   - Check the box → Click "Add permissions"

---

### Option 2: AWS CLI

If you have AWS CLI installed:

```bash
# Save the policy to a file
cat > clipizy-s3-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListAllMyBuckets",
        "s3:GetBucketLocation"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ],
      "Resource": "arn:aws:s3:::clipizy-dev"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::clipizy-dev/*"
    }
  ]
}
EOF

# Create the policy
aws iam create-policy \
    --policy-name Clipizy-S3-Access \
    --policy-document file://clipizy-s3-policy.json

# Attach to user (replace ACCOUNT_ID with your AWS account ID: 188594592347)
aws iam attach-user-policy \
    --user-name Runpod \
    --policy-arn arn:aws:iam::188594592347:policy/Clipizy-S3-Access
```

---

## 🧪 Verify Permissions

After adding permissions, test again:

```bash
python3 scripts/check_s3_bucket.py
```

Expected output:
```
✅ Bucket exists: clipizy-dev
✅ Can list objects
✅ Can upload objects
✅ Can download objects
✅ Can delete objects
🎉 ALL PERMISSIONS OK!
```

---

## 🚀 After Fixing Permissions

1. **Restart your backend:**
```bash
pkill -f uvicorn
./app.sh
```

2. **Check backend logs:**
Look for: `"S3 client initialized successfully with bucket: clipizy-dev"`

3. **Test track upload:**
- Go to frontend
- Create a music clip project
- Upload a track
- Should work without 500 errors!

---

## 📋 Checklist

- [ ] Logged into AWS Console
- [ ] Navigated to IAM → Users → Runpod
- [ ] Added S3 permissions (Full Access or Custom Policy)
- [ ] Ran `python3 scripts/check_s3_bucket.py` - all tests pass
- [ ] Restarted backend
- [ ] Tested track upload in frontend - works!

---

## 🎯 Quick Summary

**Problem:** IAM user `Runpod` has no S3 permissions  
**Solution:** Add S3 permissions in AWS IAM Console  
**Test:** Run `python3 scripts/check_s3_bucket.py`  
**Deploy:** Restart backend and test uploads

---

## ⚠️ Important Notes

- **Security:** The custom policy (Option B) is more secure as it only grants access to the specific bucket
- **Propagation:** IAM changes take effect immediately, but may take a few seconds
- **Multiple Buckets:** If you need access to `clipizy-prod` and `clipizy-test`, add them to the policy too

---

## 🆘 Still Having Issues?

If permissions are added but still getting errors:

1. **Wait 30 seconds** - IAM changes can take a moment to propagate
2. **Check bucket exists:**
   - Go to https://s3.console.aws.amazon.com/s3/
   - Look for `clipizy-dev`
   - If missing, create it
3. **Check region matches:**
   - Bucket region should match `S3_REGION` in `.env`
4. **Verify credentials:**
   - Make sure `S3_ACCESS_KEY` and `S3_SECRET_KEY` are for the `Runpod` user

