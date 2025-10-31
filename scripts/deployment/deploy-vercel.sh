#!/bin/bash

# Vercel Deployment Script for clipizy API
echo "🚀 Deploying clipizy API to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo "🔐 Please log in to Vercel..."
    vercel login
fi

# Backup original requirements
echo "📦 Backing up original requirements..."
cp requirements.txt requirements-original.txt

# Use Vercel-compatible requirements
echo "🔄 Switching to Vercel-compatible requirements..."
cp requirements-vercel.txt requirements.txt

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

# Restore original requirements for local development
echo "🔄 Restoring original requirements for local development..."
cp requirements-original.txt requirements.txt

echo "✅ Deployment complete!"
echo "📖 Check VERCEL_DEPLOYMENT.md for more information"
