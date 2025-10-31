#!/bin/bash

# clipizy Development Environment Startup Script
# This script starts all required services for local development

echo "🚀 Starting clipizy Development Environment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Skip stop script to avoid sudo requirement
# bash scripts/startup/stop.sh

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Try to stop existing containers without sudo
docker stop clipizy-minio clipizy-postgres 2>/dev/null || true
docker rm clipizy-minio clipizy-postgres 2>/dev/null || true

# Function to check if a port is in use
port_in_use() {
    local port=$1
    # Check multiple times with small delay to avoid race conditions
    for i in {1..3}; do
        if lsof -i :$port >/dev/null 2>&1; then
            return 0
        fi
        sleep 0.5
    done
    return 1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10+ first.${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"

# Check Amazon S3 Configuration
echo -e "${BLUE}☁️  Checking Amazon S3 configuration...${NC}"
if [ -z "$S3_ACCESS_KEY" ] || [ -z "$S3_SECRET_KEY" ] || [ -z "$S3_BUCKET" ]; then
    echo -e "${YELLOW}⚠️  Amazon S3 credentials not found in environment variables${NC}"
    echo -e "${YELLOW}   Please set the following environment variables:${NC}"
    echo -e "${YELLOW}   - S3_ACCESS_KEY${NC}"
    echo -e "${YELLOW}   - S3_SECRET_KEY${NC}"
    echo -e "${YELLOW}   - S3_BUCKET${NC}"
    echo -e "${YELLOW}   - S3_REGION (optional, defaults to us-east-1)${NC}"
    echo -e "${YELLOW}   - S3_ENDPOINT_URL (optional, defaults to https://s3.amazonaws.com)${NC}"
    echo -e "${YELLOW}   Continuing startup, but S3 operations may fail...${NC}"
else
    echo -e "${GREEN}✅ Amazon S3 credentials found${NC}"
    echo -e "${GREEN}   Bucket: $S3_BUCKET${NC}"
    echo -e "${GREEN}   Region: ${S3_REGION:-us-east-1}${NC}"
fi

# Start PostgreSQL
echo -e "${BLUE}🗄️  Starting PostgreSQL...${NC}"
# Kill any existing PostgreSQL processes
pkill -f postgres 2>/dev/null || true
docker stop clipizy-postgres 2>/dev/null || true
docker rm clipizy-postgres 2>/dev/null || true

if port_in_use 5432; then
    echo -e "${YELLOW}⚠️  Port 5432 is still in use. Using port 5433 instead.${NC}"
    POSTGRES_PORT=5433
else
    POSTGRES_PORT=5432
fi

docker run -d --name clipizy-postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=clipizy \
    -p 0.0.0.0:$POSTGRES_PORT:5432 \
    postgres:15
echo -e "${GREEN}✅ PostgreSQL started at localhost:$POSTGRES_PORT${NC}"

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Set database URL based on PostgreSQL port
# Use psycopg3 driver for WSL compatibility
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:$POSTGRES_PORT/clipizy"

# Initialize database
echo -e "${BLUE}🗄️  Initializing database...${NC}"
if [ -f "scripts/backend/init_database.py" ]; then
    echo -e "${YELLOW}📋 Setting up database tables and schema...${NC}"
    DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:$POSTGRES_PORT/clipizy" python scripts/backend/init_database.py
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Database initialized successfully${NC}"
    else
        echo -e "${RED}❌ Database initialization failed${NC}"
        echo -e "${YELLOW}⚠️  Continuing with startup, but database may not be ready${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  init_database.py not found. Skipping database initialization.${NC}"
fi

# Start FastAPI Backend
echo -e "${BLUE}🐍 Starting FastAPI Backend...${NC}"
if port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use. FastAPI might already be running.${NC}"
    echo -e "${YELLOW}💡 To restart with reload, run: pkill -f 'uvicorn.*api.main:app' && sleep 2${NC}"
else
    # Check if virtual environment exists in root directory
    if [ ! -d ".venv" ]; then
        echo -e "${YELLOW}📦 Creating Python virtual environment...${NC}"
        python3 -m venv .venv
    fi

    echo -e "${YELLOW}📦 Activating Python virtual environment...${NC}"
    source .venv/bin/activate

    echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"

    echo -e "${YELLOW}🚀 Starting FastAPI server with auto-reload...${NC}"
    echo -e "${BLUE}🔄 Auto-reload is ENABLED - changes will be automatically detected${NC}"
    DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:$POSTGRES_PORT/clipizy" python scripts/backend/start.py &
    echo -e "${GREEN}✅ FastAPI started at http://localhost:8000 with auto-reload${NC}"
fi

# Start ComfyUI (GPU processing)
echo -e "${BLUE}🎨 Starting ComfyUI (GPU processing)...${NC}"
if port_in_use 8188; then
    echo -e "${YELLOW}⚠️  Port 8188 is already in use. ComfyUI might already be running.${NC}"
else
    # Check if ComfyUI directory exists
    if [ -d "ComfyUI" ]; then
        cd ComfyUI
        echo -e "${YELLOW}🚀 Starting ComfyUI server...${NC}"
        python3 main.py --listen 0.0.0.0 --port 8188 &
        echo -e "${GREEN}✅ ComfyUI started at http://localhost:8188${NC}"
        cd ..
    else
        echo -e "${YELLOW}⚠️  ComfyUI directory not found. Skipping ComfyUI startup.${NC}"
        echo -e "${YELLOW}   To install ComfyUI, run: git clone https://github.com/comfyanonymous/ComfyUI.git${NC}"
    fi
fi

# Start Next.js Frontend
echo -e "${BLUE}⚛️  Starting Next.js Frontend...${NC}"
# Small delay to ensure all cleanup is complete
sleep 2
if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use. Next.js might already be running.${NC}"
else
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
        npm install
    fi

    echo -e "${YELLOW}🚀 Starting Next.js development server...${NC}"
    bash start-nextjs.sh &
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Next.js started at http://localhost:3000${NC}"
    else
        echo -e "${RED}❌ Failed to start Next.js${NC}"
        echo -e "${YELLOW}💡 To fix this issue, run the following commands in WSL:${NC}"
        echo -e "${YELLOW}   cd /home/unix/code/clipizy${NC}"
        echo -e "${YELLOW}   rm -rf node_modules package-lock.json .next${NC}"
        echo -e "${YELLOW}   npm install${NC}"
        echo -e "${YELLOW}   npm run dev${NC}"
        echo -e "${YELLOW}   See FIX_NEXTJS_ISSUE.md for more details${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 clipizy Development Environment Started!${NC}"
echo "================================================"
echo -e "${BLUE}📱 Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}🔧 API Docs:${NC} http://localhost:8000/docs"
echo -e "${BLUE}🗄️  MinIO Console:${NC} http://localhost:9001 (admin/admin123)"
echo -e "${BLUE}🎨 ComfyUI:${NC} http://localhost:8188"
echo -e "${BLUE}🗄️  PostgreSQL:${NC} localhost:$POSTGRES_PORT (postgres/postgres)"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo -e "${YELLOW}   1. Register a user at http://localhost:3000/auth/register${NC}"
echo -e "${YELLOW}   2. To create an admin user, run:${NC}"
echo -e "${YELLOW}      cd api && python create_admin_user.py${NC}"
echo -e "${YELLOW}   3. Access admin panel at http://localhost:3000/admin${NC}"
echo ""
echo -e "${BLUE}🔄 Development Features:${NC}"
echo -e "${BLUE}   • FastAPI auto-reload: Changes to Python files will automatically restart the server${NC}"
echo -e "${BLUE}   • Next.js hot reload: Changes to React components will automatically update${NC}"
echo -e "${BLUE}   • Database persistence: All data is stored in PostgreSQL${NC}"
echo -e "${BLUE}   • File storage: Files are stored in MinIO (S3-compatible)${NC}"
echo ""
echo -e "${YELLOW}💡 To stop all services, run: ./stop.sh${NC}"
echo -e "${YELLOW}💡 To restart FastAPI with reload, run: ./restart-backend.sh${NC}"
echo -e "${YELLOW}💡 To view logs, run: docker logs -f clipizy-minio${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"