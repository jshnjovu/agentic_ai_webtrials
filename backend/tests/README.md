# Testing Strategy for Lighthouse API Integration

This project uses a **dual testing approach** to ensure both fast development and real-world validation.

## 🚀 Fast Unit Tests (Recommended for Development)

**Location**: `tests/unit/`
**Purpose**: Fast, reliable tests for development and CI/CD
**API Calls**: Mocked (no external dependencies)
**Speed**: ~2-3 seconds for all tests
**Cost**: Free (no API quota consumption)

### Running Unit Tests
```bash
# Run all unit tests
python -m pytest tests/unit/ -v

# Run specific test categories
python -m pytest tests/unit/test_services/test_lighthouse_service.py -v
python -m pytest tests/unit/test_api/test_website_scoring_api.py -v
python -m pytest tests/unit/test_utils/test_score_calculation.py -v

# Run specific test methods
python -m pytest tests/unit/test_services/test_lighthouse_service.py::TestLighthouseService::test_run_lighthouse_audit_success -v
```

## 🌐 Real API Integration Tests (For Production Validation)

**Location**: `tests/integration/`
**Purpose**: Validate real-world API integration
**API Calls**: Real Google PageSpeed Insights API
**Speed**: ~30-60 seconds (due to API response times)
**Cost**: Consumes API quota (25,000 requests/day limit)

### Prerequisites for Integration Tests
1. **Real API Key**: Set `LIGHTHOUSE_API_KEY` in your `.env` file
2. **Rate Limit Awareness**: Tests include delays to respect API limits
3. **Network Access**: Requires internet connection

### Running Integration Tests
```bash
# Run all integration tests
python -m pytest tests/integration/ -v

# Run specific integration test
python -m pytest tests/integration/test_lighthouse_real_api.py -v

# Run with verbose output
python -m pytest tests/integration/test_lighthouse_real_api.py -v --tb=short
```

## 🔧 Test Configuration

### Environment Variables
```bash
# Required for real API tests
LIGHTHOUSE_API_KEY=your_real_api_key_here

# Optional timeout configurations
LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS=30
LIGHTHOUSE_CONNECT_TIMEOUT_SECONDS=10
LIGHTHOUSE_READ_TIMEOUT_SECONDS=25
LIGHTHOUSE_FALLBACK_TIMEOUT_SECONDS=15
```

### Rate Limiting
- **Unit Tests**: No rate limiting (mocked)
- **Integration Tests**: 2-second delay between tests to respect API limits
- **Production**: 240 requests/minute, 25,000 requests/day

## 📊 Test Coverage

### Unit Tests (57 tests)
- ✅ Lighthouse Service: 16 tests
- ✅ Website Scoring API: 15 tests  
- ✅ Score Calculation Utils: 26 tests

### Integration Tests (7 tests)
- ✅ Real Desktop Audit
- ✅ Real Mobile Audit
- ✅ Timeout Handling
- ✅ Invalid URL Handling
- ✅ Rate Limiting
- ✅ Fallback Mechanism
- ✅ Data Consistency

## 🎯 When to Use Each Approach

### Use Unit Tests When:
- 🚀 **Developing new features**
- 🔄 **Running CI/CD pipelines**
- 🧪 **Quick validation during development**
- 💰 **Want to avoid API quota consumption**
- ⚡ **Need fast test execution**

### Use Integration Tests When:
- 🌐 **Validating real API integration**
- 🚀 **Before production deployment**
- 🔍 **Debugging API-related issues**
- 📊 **Performance testing with real data**
- ✅ **Final validation of implementation**

## 🚨 Important Notes

### For Integration Tests:
1. **API Quota**: Each test consumes 1 API request
2. **Network Dependency**: Tests will fail without internet
3. **Rate Limits**: Tests include delays to respect API limits
4. **Real Data**: Results may vary based on website performance

### For Unit Tests:
1. **Fast Execution**: All tests complete in seconds
2. **Consistent Results**: Mocked responses ensure reliability
3. **No External Dependencies**: Works offline
4. **Development Friendly**: Perfect for iterative development

## 🔍 Example Test Output

### Unit Test (Fast)
```bash
$ python -m pytest tests/unit/test_services/test_lighthouse_service.py -v
collected 16 items
tests/unit/test_services/test_lighthouse_service.py::TestLighthouseService::test_validate_input_valid PASSED [  6%]
tests/unit/test_services/test_lighthouse_service.py::TestLighthouseService::test_validate_input_invalid PASSED [ 12%]
# ... more tests ...
========================== 16 passed in 1.23s ==========================
```

### Integration Test (Real API)
```bash
$ python -m pytest tests/integration/test_lighthouse_real_api.py::TestLighthouseRealAPI::test_real_lighthouse_audit_desktop -v
test_real_lighthouse_audit_desktop PASSED [100%]
========================== 1 passed in 12.45s ==========================
```

## 🛠️ Troubleshooting

### Integration Tests Failing?
1. **Check API Key**: Ensure `LIGHTHOUSE_API_KEY` is set correctly
2. **Network Access**: Verify internet connection
3. **Rate Limits**: Wait a few minutes if you hit rate limits
4. **API Status**: Check if Google PageSpeed Insights API is available

### Unit Tests Failing?
1. **Dependencies**: Run `pip install -r requirements.txt`
2. **Python Version**: Ensure Python 3.11+
3. **Test Files**: Verify test files are in correct locations

## 📈 Performance Comparison

| Test Type | Execution Time | API Calls | Reliability | Cost |
|-----------|----------------|-----------|-------------|------|
| Unit Tests | ~2-3 seconds | 0 (mocked) | High | Free |
| Integration Tests | ~30-60 seconds | 7 real calls | Medium | API quota |

## 🎉 Best Practices

1. **Development**: Use unit tests for fast iteration
2. **Pre-deployment**: Run integration tests to validate real API
3. **CI/CD**: Use unit tests for automated testing
4. **Manual Validation**: Use integration tests for final verification

This dual approach gives you the best of both worlds: fast development with unit tests and real-world validation with integration tests!
