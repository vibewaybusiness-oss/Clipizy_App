# 🧪 Clipizy Test Environment

Comprehensive testing suite for the Clipizy application covering backend APIs, frontend hooks, and end-to-end integration.

## 📁 Directory Structure

```
test_environment/
├── backend/                 # Backend API and service tests
│   ├── test_api_endpoints.py
│   └── test_services.py
├── frontend/                # Frontend hook and component tests
│   └── test_hooks.js
├── integration/             # End-to-end integration tests
│   └── test_end_to_end.py
├── fixtures/                # Test data and file generators
│   ├── test_data.json
│   └── test_files.py
├── scripts/                 # Test runners and utilities
│   ├── run_all_tests.py
│   ├── run_backend_tests.sh
│   └── run_frontend_tests.sh
├── config/                  # Test configuration
│   └── test_config.py
└── README.md               # This file
```

## 🚀 Quick Start

### 1. **Run All Tests**
```bash
cd /root/clipizy
python3 test_environment/scripts/run_all_tests.py
```

### 2. **Run Backend Tests Only**
```bash
cd /root/clipizy
./test_environment/scripts/run_backend_tests.sh
```

### 3. **Run Frontend Tests Only**
```bash
cd /root/clipizy
./test_environment/scripts/run_frontend_tests.sh
```

### 4. **Run Individual Test Suites**
```bash
# Backend API endpoints
python3 test_environment/backend/test_api_endpoints.py

# Backend services
python3 test_environment/backend/test_services.py

# Frontend hooks
node test_environment/frontend/test_hooks.js

# End-to-end integration
python3 test_environment/integration/test_end_to_end.py
```

## 📊 Test Coverage

### Backend Tests
- ✅ **API Endpoints**: All HTTP endpoints and responses
- ✅ **Services**: Storage, auth, database, and AI services
- ✅ **Database**: Model operations and queries
- ✅ **Storage**: S3/MinIO operations and file handling
- ✅ **Authentication**: User management and OAuth flows
- ✅ **Error Handling**: Exception handling and error responses

### Frontend Tests
- ✅ **React Hooks**: Hook structure and patterns
- ✅ **API Integration**: Frontend-backend communication
- ✅ **Component Structure**: React component patterns
- ✅ **TypeScript**: Type safety and interfaces
- ✅ **Package Dependencies**: Required packages and scripts

### Integration Tests
- ✅ **End-to-End Workflows**: Complete user journeys
- ✅ **File Upload**: Audio, image, and video processing
- ✅ **Project Management**: Creation, updates, and deletion
- ✅ **User Authentication**: Registration and login flows
- ✅ **Performance**: Response times and operation speeds

## 🔧 Configuration

### Environment Variables
```bash
# Test environment
export TEST_ENVIRONMENT=development  # development, staging, production

# Test flags
export RUN_SLOW_TESTS=false
export RUN_INTEGRATION_TESTS=true
export RUN_PERFORMANCE_TESTS=false

# Logging
export TEST_LOG_LEVEL=INFO
export VERBOSE_TESTS=false

# Cleanup
export CLEANUP_AFTER_TESTS=true
export KEEP_TEST_FILES=false
```

### Test Configuration
Edit `test_environment/config/test_config.py` to customize:
- API endpoints and timeouts
- Database connections
- Storage settings
- Performance thresholds
- Test data and fixtures

## 📈 Performance Benchmarks

| Test Type | Expected Time | Success Criteria |
|-----------|---------------|------------------|
| Quick Tests | 2-3 seconds | 100% pass rate |
| Backend Tests | 5-10 seconds | 90%+ pass rate |
| Frontend Tests | 1-2 seconds | 80%+ pass rate |
| Integration Tests | 10-15 seconds | 85%+ pass rate |
| Full Suite | 20-30 seconds | 80%+ pass rate |

## 🎯 Success Criteria

### Healthy System Indicators
- ✅ All critical imports working
- ✅ Database connectivity established
- ✅ Storage service operational
- ✅ API endpoints responding
- ✅ Frontend structure valid
- ✅ Integration workflows functional

### Target Success Rates
- **Backend**: 90%+ for core functionality
- **Frontend**: 80%+ for structure validation
- **Integration**: 85%+ for end-to-end workflows
- **Overall**: 80%+ for system health

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Check Python path
   export PYTHONPATH=/root/clipizy:$PYTHONPATH
   ```

2. **Database Connection Issues**
   ```bash
   # Check database file exists
   ls -la /root/clipizy/clipizy.db
   ```

3. **MinIO Connection Issues**
   ```bash
   # Check MinIO is running
   curl http://localhost:9000/minio/health/live
   ```

4. **API Server Issues**
   ```bash
   # Check if server is running
   curl http://localhost:8000/api/storage/health
   ```

5. **Frontend Build Issues**
   ```bash
   # Check Node.js and npm
   node --version
   npm --version
   
   # Install dependencies
   npm install
   ```

### Test File Generation
```bash
# Generate test files
python3 test_environment/fixtures/test_files.py

# Test files will be created in temporary directory
# Use these for file upload testing
```

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: 18
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm install
      - name: Run tests
        run: python3 test_environment/scripts/run_all_tests.py
```

## 📝 Adding New Tests

### Backend Tests
1. Add test methods to existing test files
2. Follow naming convention: `test_<functionality>`
3. Use `self.log_result()` for consistent output
4. Handle exceptions gracefully

### Frontend Tests
1. Add test methods to `test_hooks.js`
2. Check for React patterns and TypeScript types
3. Validate API integration and error handling
4. Use `this.logResult()` for consistent output

### Integration Tests
1. Add workflow tests to `test_end_to_end.py`
2. Test complete user journeys
3. Validate cross-service communication
4. Include performance benchmarks

## 🎉 Best Practices

1. **Test Isolation**: Each test should be independent
2. **Cleanup**: Always clean up test data and files
3. **Error Handling**: Graceful handling of test failures
4. **Performance**: Monitor test execution times
5. **Documentation**: Keep test documentation updated
6. **Maintenance**: Regular review and updates of test cases

## 📞 Support

For test-related issues:
1. Check the troubleshooting section above
2. Review test logs and error messages
3. Verify system dependencies and configuration
4. Run individual test suites to isolate issues

---

**Happy Testing! 🧪✨**
