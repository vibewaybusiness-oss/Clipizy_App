@echo off
REM Vercel Deployment Script for clipizy API
echo 🚀 Deploying clipizy API to Vercel...

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Vercel CLI not found. Installing...
    npm install -g vercel
)

REM Check if user is logged in
vercel whoami >nul 2>nul
if %errorlevel% neq 0 (
    echo 🔐 Please log in to Vercel...
    vercel login
)

REM Backup original requirements
echo 📦 Backing up original requirements...
copy requirements.txt requirements-original.txt

REM Use Vercel-compatible requirements
echo 🔄 Switching to Vercel-compatible requirements...
copy requirements-vercel.txt requirements.txt

REM Deploy to Vercel
echo 🚀 Deploying to Vercel...
vercel --prod

REM Restore original requirements for local development
echo 🔄 Restoring original requirements for local development...
copy requirements-original.txt requirements.txt

echo ✅ Deployment complete!
echo 📖 Check VERCEL_DEPLOYMENT.md for more information
pause
