#!/bin/bash

# Authentication and Project Creation Test Script

echo "🔍 Testing Authentication and Project Creation..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test 1: Check if backend is running
echo -e "${BLUE}1. Testing backend health...${NC}"
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ Backend is running${NC}"
else
    echo -e "${RED}❌ Backend is not running${NC}"
    exit 1
fi

# Test 2: Check database connection
echo -e "${BLUE}2. Testing database connection...${NC}"
if docker exec clipizi-postgres psql -U postgres -d clipizy -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Database is accessible${NC}"
else
    echo -e "${RED}❌ Database is not accessible${NC}"
    exit 1
fi

# Test 3: Check existing users
echo -e "${BLUE}3. Checking existing users...${NC}"
USER_COUNT=$(docker exec clipizi-postgres psql -U postgres -d clipizy -t -c "SELECT COUNT(*) FROM users;" | tr -d ' ')
echo -e "${GREEN}✅ Found $USER_COUNT users in database${NC}"

# Test 4: Check existing projects
echo -e "${BLUE}4. Checking existing projects...${NC}"
PROJECT_COUNT=$(docker exec clipizi-postgres psql -U postgres -d clipizy -t -c "SELECT COUNT(*) FROM projects;" | tr -d ' ')
echo -e "${GREEN}✅ Found $PROJECT_COUNT projects in database${NC}"

# Test 5: Check existing tracks
echo -e "${BLUE}5. Checking existing tracks...${NC}"
TRACK_COUNT=$(docker exec clipizi-postgres psql -U postgres -d clipizy -t -c "SELECT COUNT(*) FROM tracks;" | tr -d ' ')
echo -e "${GREEN}✅ Found $TRACK_COUNT tracks in database${NC}"

# Test 6: Show recent projects
echo -e "${BLUE}6. Recent projects:${NC}"
docker exec clipizi-postgres psql -U postgres -d clipizy -c "SELECT id, name, type, status, created_at FROM projects ORDER BY created_at DESC LIMIT 3;"

# Test 7: Show recent tracks
echo -e "${BLUE}7. Recent tracks:${NC}"
docker exec clipizi-postgres psql -U postgres -d clipizy -c "SELECT id, project_id, title, status, created_at FROM tracks ORDER BY created_at DESC LIMIT 3;"

echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo -e "${YELLOW}   1. Make sure you're logged in at http://localhost:3000${NC}"
echo -e "${YELLOW}   2. Check browser console for authentication errors${NC}"
echo -e "${YELLOW}   3. Try uploading a file again${NC}"
echo -e "${YELLOW}   4. Check the database-access-guide.md for more database queries${NC}"
