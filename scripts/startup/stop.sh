#!/bin/bash

# clipizy Development Environment Stop Script
# This script stops all running services

echo "🛑 Stopping clipizy Development Environment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Stop Docker containers
echo -e "${BLUE}🐳 Stopping Docker containers...${NC}"

# Stop MinIO
if sudo docker ps -q -f name=clipizy-minio | grep -q .; then
    sudo docker stop clipizy-minio
    sudo docker rm clipizy-minio
    echo -e "${GREEN}✅ MinIO stopped and removed${NC}"
else
    echo -e "${YELLOW}⚠️  MinIO container not found${NC}"
fi

# Stop PostgreSQL
if sudo docker ps -q -f name=clipizy-postgres | grep -q .; then
    sudo docker stop clipizy-postgres
    sudo docker rm clipizy-postgres
    echo -e "${GREEN}✅ PostgreSQL stopped and removed${NC}"
else
    echo -e "${YELLOW}⚠️  PostgreSQL container not found${NC}"
fi

# Stop FastAPI (kill processes on port 8000)
echo -e "${BLUE}🐍 Stopping FastAPI...${NC}"
if lsof -ti:8000 >/dev/null 2>&1; then
    kill $(lsof -ti:8000)
    echo -e "${GREEN}✅ FastAPI stopped${NC}"
else
    echo -e "${YELLOW}⚠️  FastAPI not running on port 8000${NC}"
fi

# Stop ComfyUI (kill processes on port 8188)
echo -e "${BLUE}🎨 Stopping ComfyUI...${NC}"
if lsof -ti:8188 >/dev/null 2>&1; then
    kill $(lsof -ti:8188)
    echo -e "${GREEN}✅ ComfyUI stopped${NC}"
else
    echo -e "${YELLOW}⚠️  port 8188 not running on port 8188${NC}"
fi

# Stop Next.js (kill processes on port 3000)
echo -e "${BLUE}⚛️  Stopping Next.js...${NC}"
if lsof -ti:3000 >/dev/null 2>&1; then
    kill $(lsof -ti:3000)
    echo -e "${GREEN}✅ Next.js stopped${NC}"
else
    echo -e "${YELLOW}⚠️  Next.js not running on port 3000${NC}"
fi

echo ""
echo -e "${GREEN}🎉 All services stopped!${NC}"
echo "================================================"
echo -e "${YELLOW}💡 To start services again, run: ./app.sh${NC}"
echo ""
