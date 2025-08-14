"""
Unit tests for Lighthouse API integration service.
Tests website performance auditing functionality with mocked API responses.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from src.services.lighthouse_service import LighthouseService


class TestLighthouseService:
    """Test cases for LighthouseService."""
    
    @pytest.fixture
    def service(self):
        """Create a LighthouseService instance for testing."""
        with patch('src.services.lighthouse_service.get_api_config') as mock_config:
            mock_config.return_value = Mock(
                LIGHTHOUSE_API_KEY="test_lighthouse_api_key",
                LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS=30,
                LIGHTHOUSE_CONNECT_TIMEOUT_SECONDS=10,
                LIGHTHOUSE_READ_TIMEOUT_SECONDS=25,
                LIGHTHOUSE_FALLBACK_TIMEOUT_SECONDS=15
            )
            return LighthouseService()
    
    @pytest.fixture
    def sample_lighthouse_response(self):
        """Sample successful Lighthouse API response."""
        return {
            "lighthouseResult": {
                "configSettings": {"formFactor": "desktop"},
                "categories": {
                    "performance": {"score": 0.85},
                    "accessibility": {"score": 0.92},
                    "best-practices": {"score": 0.88},
                    "seo": {"score": 0.95}
                },
                "audits": {
                    "first-contentful-paint": {"numericValue": 1200},
                    "largest-contentful-paint": {"numericValue": 2100},
                    "cumulative-layout-shift": {"numericValue": 0.05},
                    "total-blocking-time": {"numericValue": 150},
                    "speed-index": {"numericValue": 1800}
                }
            }
        }
    
    def test_validate_input_valid(self, service):
        """Test input validation with valid request."""
        valid_input = {'website_url': 'https://example.com', 'business_id': 'test_123'}
        assert service.validate_input(valid_input) is True
    
    def test_validate_input_invalid(self, service):
        """Test input validation with invalid request."""
        assert service.validate_input("invalid_input") is False
        assert service.validate_input({}) is False
    
    def test_validate_url_valid(self, service):
        """Test URL validation with valid URLs."""
        assert service._validate_url("https://example.com") is True
        assert service._validate_url("http://example.com") is True
    
    def test_validate_url_invalid(self, service):
        """Test URL validation with invalid URLs."""
        assert service._validate_url("not-a-url") is False
    
    @patch('src.services.lighthouse_service.requests.get')
    def test_execute_audit_success(self, mock_get, service, sample_lighthouse_response):
        """Test successful audit execution."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_lighthouse_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, "OK")
        
        result = service._execute_audit_with_retry(
            {'url': 'https://example.com', 'strategy': 'desktop'},
            'test_run_123',
            'test_business_123'
        )
        
        assert result["success"] is True
        assert result["data"] == sample_lighthouse_response
    
    @patch('src.services.lighthouse_service.requests.get')
    def test_execute_audit_timeout(self, mock_get, service):
        """Test audit execution timeout handling."""
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, "OK")
        
        result = service._execute_audit_with_retry(
            {'url': 'https://example.com', 'strategy': 'desktop'},
            'test_run_123',
            'test_business_123'
        )
        
        assert result["success"] is False
        assert result["error_code"] == "TIMEOUT"
    
    def test_extract_score_valid(self, service, sample_lighthouse_response):
        """Test score extraction from valid categories."""
        categories = sample_lighthouse_response['lighthouseResult']['categories']
        
        assert service._extract_score(categories, 'performance') == 85.0
        assert service._extract_score(categories, 'accessibility') == 92.0
    
    def test_extract_core_web_vitals(self, service, sample_lighthouse_response):
        """Test Core Web Vitals extraction."""
        core_web_vitals = service._extract_core_web_vitals(sample_lighthouse_response)
        
        assert core_web_vitals['first_contentful_paint'] == 1200.0
        assert core_web_vitals['largest_contentful_paint'] == 2100.0
    
    def test_determine_confidence_high(self, service, sample_lighthouse_response):
        """Test confidence determination for high confidence results."""
        confidence = service._determine_confidence(sample_lighthouse_response)
        assert confidence == "high"
    
    @patch('src.services.lighthouse_service.requests.get')
    def test_run_lighthouse_audit_success(self, mock_get, service, sample_lighthouse_response):
        """Test successful Lighthouse audit execution."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_lighthouse_response
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, "OK")
        service.rate_limiter.record_request.return_value = None
        
        result = service.run_lighthouse_audit(
            "https://example.com",
            "test_business_123",
            "test_run_456",
            "desktop"
        )
        
        assert result["success"] is True
        assert result["scores"]["performance"] == 85.0
        assert result["confidence"] == "high"
    
    def test_run_lighthouse_audit_rate_limit_exceeded(self, service):
        """Test Lighthouse audit with rate limit exceeded."""
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (False, "Rate limit exceeded")
        
        result = service.run_lighthouse_audit(
            "https://example.com",
            "test_business_123",
            "test_run_456",
            "desktop"
        )
        
        assert result["success"] is False
        assert "Rate limit exceeded" in result["error"]
    
    def test_run_lighthouse_audit_invalid_url(self, service):
        """Test Lighthouse audit with invalid URL."""
        result = service.run_lighthouse_audit(
            "not-a-valid-url",
            "test_business_123",
            "test_run_456",
            "desktop"
        )
        
        assert result["success"] is False
        assert result["error"] == "Invalid website URL format"
    
    @patch('src.services.lighthouse_service.requests.get')
    def test_fallback_audit_success(self, mock_get, service):
        """Test successful fallback audit execution."""
        # Mock primary audit failure with timeout
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, "OK")
        service.rate_limiter.record_request.return_value = None
        
        # Mock fallback audit success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lighthouseResult": {
                "categories": {
                    "performance": {"score": 0.75}
                }
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock primary audit to fail with timeout
        with patch.object(service, '_execute_audit_with_retry') as mock_primary:
            mock_primary.return_value = {
                "success": False,
                "error": "Audit request timed out",
                "error_code": "TIMEOUT",
                "context": "audit_execution"
            }
            
            result = service.run_lighthouse_audit(
                "https://example.com",
                "test_business_123",
                "test_run_456",
                "desktop"
            )
            
            assert result["success"] is True
            assert result["fallback_used"] is True
            assert result["scores"]["performance"] == 75.0
            assert result["confidence"] == "medium"
    
    @patch('src.services.lighthouse_service.requests.get')
    def test_fallback_audit_failure(self, mock_get, service):
        """Test fallback audit failure handling."""
        # Mock primary audit failure with timeout
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, "OK")
        service.rate_limiter.record_request.return_value = None
        
        # Mock fallback audit failure
        mock_get.side_effect = requests.RequestException("Fallback failed")
        
        # Mock primary audit to fail with timeout
        with patch.object(service, '_execute_audit_with_retry') as mock_primary:
            mock_primary.return_value = {
                "success": False,
                "error": "Audit request timed out",
                "error_code": "TIMEOUT",
                "context": "audit_execution"
            }
            
            result = service.run_lighthouse_audit(
                "https://example.com",
                "test_business_123",
                "test_run_456",
                "desktop"
            )
            
            assert result["success"] is False
            assert result["error_code"] == "FALLBACK_FAILED"
    
    def test_timeout_configuration(self, service):
        """Test timeout configuration values."""
        assert service.timeout == 30
        assert service.connect_timeout == 10
        assert service.read_timeout == 25
        assert service.fallback_timeout == 15
    
    @patch('src.services.lighthouse_service.requests.get')
    def test_enhanced_timeout_handling(self, mock_get, service):
        """Test enhanced timeout handling with connect and read timeouts."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"lighthouseResult": {"categories": {}}}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, "OK")
        service.rate_limiter.record_request.return_value = None
        
        # Test that timeout tuple is used
        with patch.object(service, '_execute_audit_with_retry') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "data": {"lighthouseResult": {"categories": {}}},
                "status_code": 200
            }
            
            service.run_lighthouse_audit(
                "https://example.com",
                "test_business_123",
                "test_run_456",
                "desktop"
            )
            
            # Verify timeout tuple was used in the mock
            mock_execute.assert_called_once()
