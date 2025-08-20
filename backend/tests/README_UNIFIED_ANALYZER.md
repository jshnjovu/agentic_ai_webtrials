# UnifiedAnalyzer Test Suite

This directory contains comprehensive tests for the `UnifiedAnalyzer` service, which provides enterprise-grade website analysis capabilities with built-in reliability features.

## 🧪 Test Structure

### Unit Tests (`tests/unit/test_services/test_unified_analyzer.py`)
- **Core Functionality**: Tests individual methods and components
- **Mocked Dependencies**: Uses mocked services for isolated testing
- **Fast Execution**: Quick feedback during development
- **Comprehensive Coverage**: Tests all public methods and edge cases

### Integration Tests (`tests/integration/test_unified_analyzer_integration.py`)
- **Real API Integration**: Tests actual external API calls
- **End-to-End Workflows**: Tests complete analysis pipelines
- **Performance Testing**: Measures real-world performance characteristics
- **Error Handling**: Tests graceful degradation and error recovery

## 🚀 Quick Start

### 1. Run All Tests
```bash
# From the backend directory
python run_unified_analyzer_tests.py

# Or using pytest directly
python -m pytest tests/ -v -s
```

### 2. Run Specific Test Types
```bash
# Unit tests only
python run_unified_analyzer_tests.py --type unit

# Integration tests only
python run_unified_analyzer_tests.py --type integration

# All tests with captured output
python run_unified_analyzer_tests.py --type all --capture
```

### 3. Analyze Test Setup
```bash
python run_unified_analyzer_tests.py --analyze
```

## 📊 Test Coverage

### Unit Tests Cover:
- ✅ **Initialization**: Service setup and configuration
- ✅ **Metric Extraction**: PageSpeed audit data processing
- ✅ **Opportunity Analysis**: Performance improvement detection
- ✅ **Mobile Usability**: Mobile-friendly assessment
- ✅ **Domain Age Estimation**: Domain credibility analysis
- ✅ **Score Calculations**: UX, interactivity, and visual stability
- ✅ **Cache Management**: TTL and cleanup functionality
- ✅ **Health Monitoring**: Service status tracking
- ✅ **Rate Limiting**: Request throttling and circuit breakers
- ✅ **Error Handling**: Graceful failure management

### Integration Tests Cover:
- ✅ **Real PageSpeed API**: Actual Google PageSpeed integration
- ✅ **Comprehensive Analysis**: End-to-end website analysis
- ✅ **Caching Performance**: Real cache hit/miss behavior
- ✅ **Health Monitoring**: Live service status
- ✅ **API Reliability**: Real-world error handling

## 🔧 Test Configuration

### Environment Variables
```bash
# Required for integration tests
export GOOGLE_GENERAL_API_KEY="your_api_key_here"
export WHOIS_API_KEY="your_whois_api_key_here"

# Optional for enhanced testing
export LOG_LEVEL="DEBUG"
export UNIFIED_ANALYZER_TEST_MODE="true"
```

### Pytest Configuration
The tests use a custom pytest configuration file (`pytest_unified_analyzer.ini`) that provides:
- Verbose output with print statements
- Coverage reporting
- Custom markers for test categorization
- Timeout handling
- Logging configuration

## 📈 Key Test Data Analysis

### Performance Metrics
Tests log detailed performance data including:
- **Analysis Time**: How long each analysis takes
- **Cache Hit Rate**: Effectiveness of caching system
- **API Response Times**: External service performance
- **Memory Usage**: Resource consumption patterns

### Quality Metrics
Tests validate:
- **Score Accuracy**: Performance score calculations
- **Data Consistency**: Result structure validation
- **Error Recovery**: Graceful failure handling
- **Rate Limiting**: API quota management

### Business Impact Metrics
Tests measure:
- **Overall Score Calculation**: Business-weighted scoring
- **Confidence Levels**: Data quality assessment
- **Recommendation Generation**: Actionable insights
- **Risk Assessment**: Website health evaluation

## 🎯 Test Scenarios

### 1. **Happy Path Testing**
- Valid URLs with good performance
- Successful API responses
- Cache hits and misses
- Normal rate limiting

### 2. **Error Handling Testing**
- Invalid URLs
- API failures
- Network timeouts
- Rate limit exceeded
- Service unavailability

### 3. **Edge Case Testing**
- Empty or malformed data
- Boundary conditions
- Concurrent requests
- Memory pressure
- Long-running operations

### 4. **Performance Testing**
- Batch analysis
- Cache effectiveness
- Memory usage
- Response time consistency

## 🔍 Debugging Tests

### Enable Verbose Logging
```bash
# Set environment variable
export LOG_LEVEL="DEBUG"

# Run with verbose output
python -m pytest tests/ -v -s --log-cli-level=DEBUG
```

### Analyze Test Output
```bash
# Capture output for analysis
python run_unified_analyzer_tests.py --capture

# Run specific test with detailed output
python -m pytest tests/unit/test_services/test_unified_analyzer.py::TestUnifiedAnalyzer::test_initialization -v -s
```

### Check Test Dependencies
```bash
# Analyze test setup
python run_unified_analyzer_tests.py --analyze

# Check pytest configuration
python -m pytest --collect-only
```

## 📋 Test Data Examples

### Sample Test Output
```
🔧 Created UnifiedAnalyzer instance: <UnifiedAnalyzer object>
📊 Initial service health: {'pagespeed': 'healthy', 'domain_analysis': 'healthy', 'overall': 'healthy'}
📈 Initial analysis stats: {'total_analyses': 0, 'successful_analyses': 0, 'failed_analyses': 0, 'cache_hits': 0, 'cache_misses': 0}

✅ Testing UnifiedAnalyzer initialization
📋 Cache TTL: 3600s
🔄 Retry config: {'max_attempts': 3, 'base_delay': 2, 'max_delay': 30, 'exponential_backoff': True}
🏥 Service health: {'pagespeed': 'healthy', 'domain_analysis': 'healthy', 'overall': 'healthy'}
📊 Analysis stats: {'total_analyses': 0, 'successful_analyses': 0, 'failed_analyses': 0, 'cache_hits': 0, 'cache_misses': 0}
```

### Key Data Points to Monitor
1. **Service Health Status**: Overall system health
2. **Cache Performance**: Hit rates and effectiveness
3. **Analysis Times**: Performance characteristics
4. **Error Rates**: Failure patterns and recovery
5. **Score Distributions**: Quality assessment patterns

## 🚨 Common Issues

### 1. **Import Errors**
```bash
# Ensure you're in the backend directory
cd backend

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 2. **API Key Issues**
```bash
# Check environment variables
echo $GOOGLE_GENERAL_API_KEY
echo $WHOIS_API_KEY

# Set if missing
export GOOGLE_GENERAL_API_KEY="your_key_here"
```

### 3. **Test Timeouts**
```bash
# Increase timeout for slow tests
export PYTEST_TIMEOUT=600

# Or modify pytest configuration
# timeout = 600
```

### 4. **Coverage Issues**
```bash
# Install coverage
pip install coverage

# Run with coverage
python -m pytest --cov=src.services.unified --cov-report=html
```

## 📊 Test Results Analysis

### Success Indicators
- ✅ All tests pass
- ✅ High test coverage (>90%)
- ✅ Consistent performance metrics
- ✅ Low error rates
- ✅ Fast execution times

### Warning Signs
- ⚠️ Flaky tests (intermittent failures)
- ⚠️ Slow test execution
- ⚠️ Low cache hit rates
- ⚠️ High API error rates
- ⚠️ Memory leaks or resource issues

### Performance Benchmarks
- **Unit Tests**: < 10 seconds
- **Integration Tests**: < 60 seconds
- **Cache Hit Rate**: > 60%
- **API Response Time**: < 5 seconds
- **Memory Usage**: < 100MB

## 🔄 Continuous Integration

### GitHub Actions Example
```yaml
name: UnifiedAnalyzer Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_unified_analyzer_tests.py --type all
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📚 Additional Resources

- **Test Architecture**: See `conftest.py` for shared fixtures
- **Mocking Patterns**: See existing test files for examples
- **Performance Testing**: See integration tests for benchmarks
- **Error Handling**: See edge case tests for failure scenarios

## 🤝 Contributing

When adding new tests:
1. Follow existing naming conventions
2. Add appropriate markers
3. Include detailed logging
4. Test both success and failure cases
5. Update this documentation
6. Ensure good test coverage

---

**Note**: These tests are designed to provide comprehensive validation of the UnifiedAnalyzer service while maintaining fast feedback loops for development. The detailed logging helps developers understand system behavior and diagnose issues quickly.
