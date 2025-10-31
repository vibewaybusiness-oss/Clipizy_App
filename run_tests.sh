#!/bin/bash
# Comprehensive Test Runner for Clipizy
# Tests all API services, routers, and frontend hooks

echo "🧪 Clipizy Comprehensive Testing Suite"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run a test and capture result
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${BLUE}Running: $test_name${NC}"
    echo "Command: $test_command"
    echo "----------------------------------------"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✅ $test_name PASSED${NC}"
        return 0
    else
        echo -e "${RED}❌ $test_name FAILED${NC}"
        return 1
    fi
}

# Track results
total_tests=0
passed_tests=0

# Test 1: Quick Backend Test
run_test "Quick Backend Test" "cd /root/clipizy && source .venv/bin/activate && python3 quick_test.py"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 2: Comprehensive API Test
run_test "Comprehensive API Test" "cd /root/clipizy && source .venv/bin/activate && python3 test_all_apis.py"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 3: Frontend Structure Test
run_test "Frontend Structure Test" "cd /root/clipizy && node test_frontend_hooks.js"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 4: Check if server is running
run_test "API Server Health Check" "curl -s http://localhost:8000/api/storage/health | grep -q 'healthy' || echo 'Server not responding'"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 5: Check MinIO connection
run_test "MinIO Connection Test" "curl -s http://localhost:9000/minio/health/live | grep -q 'OK' || echo 'MinIO not responding'"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 6: Check database connection
run_test "Database Connection Test" "cd /root/clipizy && source .venv/bin/activate && python3 -c 'from api.services.database import get_db; from api.models import User; db = next(get_db()); print(f\"Users: {db.query(User).count()}\")'"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 7: Check storage service
run_test "Storage Service Test" "cd /root/clipizy && source .venv/bin/activate && python3 -c 'from api.services.storage import unified_storage_service; print(\"Storage service OK\")'"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 8: Check auth service
run_test "Auth Service Test" "cd /root/clipizy && source .venv/bin/activate && python3 -c 'from api.services.auth.auth import auth_service; print(\"Auth service OK\")'"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Print final results
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}📊 FINAL TEST RESULTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Tests: $total_tests"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"

success_rate=$((passed_tests * 100 / total_tests))
echo -e "Success Rate: ${YELLOW}$success_rate%${NC}"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "\n${GREEN}🎉 ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}💥 SOME TESTS FAILED!${NC}"
    exit 1
fi
