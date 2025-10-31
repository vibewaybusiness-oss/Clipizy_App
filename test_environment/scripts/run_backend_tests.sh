#!/bin/bash
# Backend Tests Runner
# Runs all backend tests in the test environment

echo "🔧 Backend Tests Runner"
echo "======================"

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

# Test 1: API Endpoints
run_test "Backend API Endpoints" "cd /root/clipizy && source .venv/bin/activate && python3 test_environment/backend/test_api_endpoints.py"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 2: Services
run_test "Backend Services" "cd /root/clipizy && source .venv/bin/activate && python3 test_environment/backend/test_services.py"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 3: Quick Backend Test
run_test "Quick Backend Test" "cd /root/clipizy && source .venv/bin/activate && python3 quick_test.py"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Test 4: Comprehensive API Test
run_test "Comprehensive API Test" "cd /root/clipizy && source .venv/bin/activate && python3 test_all_apis.py"
if [ $? -eq 0 ]; then
    ((passed_tests++))
fi
((total_tests++))

# Print final results
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}📊 BACKEND TEST RESULTS${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Total Tests: $total_tests"
echo -e "Passed: ${GREEN}$passed_tests${NC}"
echo -e "Failed: ${RED}$((total_tests - passed_tests))${NC}"

success_rate=$((passed_tests * 100 / total_tests))
echo -e "Success Rate: ${YELLOW}$success_rate%${NC}"

if [ $passed_tests -eq $total_tests ]; then
    echo -e "\n${GREEN}🎉 ALL BACKEND TESTS PASSED!${NC}"
    exit 0
else
    echo -e "\n${RED}💥 SOME BACKEND TESTS FAILED!${NC}"
    exit 1
fi
