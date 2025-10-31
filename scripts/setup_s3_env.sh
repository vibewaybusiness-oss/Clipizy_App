#!/bin/bash

# S3 ENVIRONMENT SETUP SCRIPT

set -e

echo "🚀 CLIPIZY S3 ENVIRONMENT SETUP"
echo "================================"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "✅ .env file already exists"
    echo ""
    read -p "Do you want to update it with S3 credentials? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
else
    echo "📝 Creating new .env file from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        echo "✅ .env file created from template"
    else
        echo "⚠️  env.template not found, creating basic .env file"
        touch .env
    fi
fi

echo ""
echo "Please enter your AWS S3 credentials:"
echo "-------------------------------------"
echo ""

# Read S3 credentials
read -p "S3 Bucket Name (e.g., clipizy-dev): " S3_BUCKET
read -p "S3 Region (e.g., us-east-1): " S3_REGION
read -p "S3 Endpoint URL (default: https://s3.amazonaws.com): " S3_ENDPOINT_URL
S3_ENDPOINT_URL=${S3_ENDPOINT_URL:-https://s3.amazonaws.com}
read -p "S3 Access Key: " S3_ACCESS_KEY
read -sp "S3 Secret Key: " S3_SECRET_KEY
echo ""

echo ""
echo "📝 Updating .env file..."

# Remove old S3 settings if they exist
sed -i '/^S3_BUCKET=/d' .env 2>/dev/null || true
sed -i '/^S3_REGION=/d' .env 2>/dev/null || true
sed -i '/^S3_ENDPOINT_URL=/d' .env 2>/dev/null || true
sed -i '/^S3_ACCESS_KEY=/d' .env 2>/dev/null || true
sed -i '/^S3_SECRET_KEY=/d' .env 2>/dev/null || true

# Add new S3 settings
cat >> .env << EOF

# Amazon S3 Storage Configuration
S3_BUCKET=$S3_BUCKET
S3_REGION=$S3_REGION
S3_ENDPOINT_URL=$S3_ENDPOINT_URL
S3_ACCESS_KEY=$S3_ACCESS_KEY
S3_SECRET_KEY=$S3_SECRET_KEY
EOF

echo "✅ .env file updated with S3 credentials"
echo ""

# Export for current session
export S3_BUCKET="$S3_BUCKET"
export S3_REGION="$S3_REGION"
export S3_ENDPOINT_URL="$S3_ENDPOINT_URL"
export S3_ACCESS_KEY="$S3_ACCESS_KEY"
export S3_SECRET_KEY="$S3_SECRET_KEY"

echo "🧪 Testing S3 connection..."
echo ""

if python3 scripts/test_s3_connection.py; then
    echo ""
    echo "🎉 SUCCESS! S3 is configured correctly."
    echo ""
    echo "Next steps:"
    echo "1. Restart your backend server to load the new credentials:"
    echo "   pkill -f uvicorn"
    echo "   ./app.sh"
    echo ""
    echo "2. Test track upload through the frontend"
else
    echo ""
    echo "❌ S3 connection test failed."
    echo "Please check your credentials and try again."
    echo ""
    echo "You can manually edit .env file and run:"
    echo "   python3 scripts/test_s3_connection.py"
    exit 1
fi
