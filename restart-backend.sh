#!/bin/bash

# clipizy Backend Restart Script
# This script restarts the FastAPI backend with auto-reload enabled

echo "🔄 Restarting FastAPI Backend with Auto-Reload..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Kill existing FastAPI processes
echo -e "${YELLOW}🛑 Stopping existing FastAPI processes...${NC}"
pkill -f 'uvicorn.*api.main:app' 2>/dev/null || true

# Wait a moment for processes to stop
sleep 2

# Check if port is still in use
if lsof -i :8000 >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 8000 is still in use. Please manually stop the process using port 8000.${NC}"
    echo -e "${YELLOW}💡 Try: sudo lsof -i :8000 && sudo kill -9 <PID>${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}📦 Activating Python virtual environment...${NC}"
source .venv/bin/activate

# Set database URL
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/clipizy"

# Start FastAPI with reload
echo -e "${YELLOW}🚀 Starting FastAPI server with auto-reload...${NC}"
echo -e "${BLUE}🔄 Auto-reload is ENABLED - changes will be automatically detected${NC}"
python scripts/backend/start.py

echo -e "${GREEN}✅ FastAPI backend restarted with auto-reload at http://localhost:8000${NC}"
