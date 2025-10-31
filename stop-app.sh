#!/bin/bash

# clipizy Development Environment Stop Script
# This script stops all running services and processes related to the project

echo "🛑 Stopping clipizy Development Environment..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    local service_name=$2
    
    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${BLUE}🔪 Killing processes on port $port ($service_name)...${NC}"
        # Try graceful kill first
        kill $(lsof -ti:$port) 2>/dev/null || true
        sleep 2
        # Force kill if still running
        if lsof -ti:$port >/dev/null 2>&1; then
            kill -9 $(lsof -ti:$port) 2>/dev/null || true
        fi
        echo -e "${GREEN}✅ Port $port ($service_name) cleared${NC}"
    else
        echo -e "${YELLOW}⚠️  No processes found on port $port ($service_name)${NC}"
    fi
}

# Function to stop Docker containers
stop_docker_container() {
    local container_name=$1
    local service_name=$2
    
    if docker ps -q -f name=$container_name | grep -q .; then
        echo -e "${BLUE}🐳 Stopping $service_name container...${NC}"
        docker stop $container_name 2>/dev/null || true
        docker rm $container_name 2>/dev/null || true
        echo -e "${GREEN}✅ $service_name container stopped and removed${NC}"
    else
        echo -e "${YELLOW}⚠️  $service_name container not found${NC}"
    fi
}

# Stop Docker containers
echo -e "${BLUE}🐳 Stopping Docker containers...${NC}"
stop_docker_container "clipizy-minio" "MinIO"
stop_docker_container "clipizy-postgres" "PostgreSQL"

# Stop all possible frontend ports
echo -e "${BLUE}⚛️  Stopping Frontend services...${NC}"
kill_port 3000 "Next.js (default)"
kill_port 3001 "Next.js (alternative)"
kill_port 3002 "Next.js (alternative 2)"
kill_port 3003 "Next.js (alternative 3)"

# Stop backend services
echo -e "${BLUE}🐍 Stopping Backend services...${NC}"
kill_port 8000 "FastAPI"
kill_port 8001 "FastAPI (alternative)"
kill_port 8002 "FastAPI (alternative 2)"

# Stop ComfyUI
echo -e "${BLUE}🎨 Stopping ComfyUI...${NC}"
kill_port 8188 "ComfyUI"
kill_port 8189 "ComfyUI (alternative)"

# Stop MinIO ports
echo -e "${BLUE}🗄️  Stopping MinIO services...${NC}"
kill_port 9000 "MinIO"
kill_port 9001 "MinIO Console"

# Stop PostgreSQL ports
echo -e "${BLUE}🗄️  Stopping PostgreSQL services...${NC}"
kill_port 5432 "PostgreSQL (default)"
kill_port 5433 "PostgreSQL (alternative)"

# Kill any remaining Python processes related to the project
echo -e "${BLUE}🐍 Killing remaining Python processes...${NC}"
pkill -f "python.*start.py" 2>/dev/null || true
pkill -f "python.*main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "fastapi" 2>/dev/null || true

# Kill any remaining Node.js processes related to the project
echo -e "${BLUE}⚛️  Killing remaining Node.js processes...${NC}"
pkill -f "next dev" 2>/dev/null || true
pkill -f "next start" 2>/dev/null || true
pkill -f "npm run dev" 2>/dev/null || true
pkill -f "npx next" 2>/dev/null || true

# Kill any processes with clipizy in the command line
echo -e "${BLUE}🔍 Killing any remaining clipizy processes...${NC}"
pkill -f "clipizy" 2>/dev/null || true

# Clear caches to prevent webpack cache corruption
echo -e "${BLUE}🧹 Clearing application caches...${NC}"
if [ -d ".next" ]; then
    echo -e "${BLUE}🗑️  Removing Next.js build cache (.next)...${NC}"
    rm -rf .next
    echo -e "${GREEN}✅ Next.js build cache cleared${NC}"
else
    echo -e "${YELLOW}⚠️  No .next directory found${NC}"
fi

if [ -d "node_modules/.cache" ]; then
    echo -e "${BLUE}🗑️  Removing Node.js cache (node_modules/.cache)...${NC}"
    rm -rf node_modules/.cache
    echo -e "${GREEN}✅ Node.js cache cleared${NC}"
else
    echo -e "${YELLOW}⚠️  No node_modules/.cache directory found${NC}"
fi

# Clear Python cache files
echo -e "${BLUE}🗑️  Removing Python cache files (__pycache__)...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Python cache files cleared${NC}"

# Clear npm cache
echo -e "${BLUE}🗑️  Clearing npm cache...${NC}"
npm cache clean --force 2>/dev/null || true
echo -e "${GREEN}✅ npm cache cleared${NC}"

# Clean up any remaining processes on common development ports
echo -e "${BLUE}🧹 Cleaning up common development ports...${NC}"
for port in 3000 3001 3002 3003 8000 8001 8002 8188 8189 9000 9001 5432 5433; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Found remaining process on port $port, force killing...${NC}"
        kill -9 $(lsof -ti:$port) 2>/dev/null || true
    fi
done

# Show final status
echo ""
echo -e "${GREEN}🎉 All clipizy services stopped!${NC}"
echo "================================================"

# Check if any ports are still in use
echo -e "${BLUE}📊 Final port status check:${NC}"
ports_to_check=(3000 3001 3002 3003 8000 8001 8002 8188 8189 9000 9001 5432 5433)
any_ports_in_use=false

for port in "${ports_to_check[@]}"; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is still in use${NC}"
        any_ports_in_use=true
    else
        echo -e "${GREEN}✅ Port $port is free${NC}"
    fi
done

if [ "$any_ports_in_use" = true ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Some ports are still in use. You may need to manually kill those processes.${NC}"
    echo -e "${YELLOW}💡 To see what's using a port, run: lsof -i :PORT_NUMBER${NC}"
    echo -e "${YELLOW}💡 To force kill a process, run: kill -9 PID${NC}"
else
    echo ""
    echo -e "${GREEN}✅ All ports are now free!${NC}"
fi

echo ""
echo -e "${YELLOW}💡 To start services again, run: ./app.sh${NC}"
echo -e "${YELLOW}💡 To check running processes, run: ps aux | grep -E '(python|node|next)'${NC}"
echo ""
echo -e "${GREEN}Happy coding! 🚀${NC}"
