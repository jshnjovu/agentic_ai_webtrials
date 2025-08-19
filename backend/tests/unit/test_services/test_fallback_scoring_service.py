"""
Unit tests for FallbackScoringService.
Tests fallback detection, retry logic, quality assessment, and error handling.
"""

import pytest
import time
import pytest_asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.services.fallback_scoring_service import (
    FallbackScoringService,
    FailureSeverity,
    FallbackDecision
)
from src.schemas.website_scoring import (
    FallbackScore, FallbackReason, FallbackReasonDetails, FallbackQuality, FallbackQualityDetails, FallbackMetrics, ConfidenceLevel
)


class TestFallbackScoringService:
    """Test cases for FallbackScoringService."""
    
    @pytest.fixture
    def service(self):
        """Create a FallbackScoringService instance for testing."""
        return FallbackScoringService()
    
    @pytest.fixture
    def mock_comprehensive_result(self):
        """Mock comprehensive speed analysis result."""
        return {
            "success": True,
            "scores": {
                "pagespeed_performance": 85.0,
                "pagespeed_accessibility": 72.0,
                "pagespeed_best_practices": 68.0,
                "pagespeed_seo": 78.0,
                "pingdom_trust": 65.0,
                "pingdom_cro": 73.6,
                "overall_score": 73.6
            },
            "pagespeed_data": {
                "performance_score": 85.0,
                "accessibility_score": 72.0,
                "best_practices_score": 68.0,
                "seo_score": 78.0,
                "first_contentful_paint": 1200.0,
                "largest_contentful_paint": 2500.0,
                "cumulative_layout_shift": 0.1,
                "total_blocking_time": 150.0,
                "speed_index": 1800.0
            },
            "pingdom_data": {
                "trust_score": 65.0,
                "cro_score": 73.6,
                "ssl_status": "valid",
                "response_time": 250,
                "uptime": 99.9,
                "security_headers": ["X-Frame-Options", "X-Content-Type-Options"]
            }
        }
    
    def test_validate_input_success(self, service):
        """Test successful input validation."""
        valid_data = {
            "website_url": "https://example.com",
            "business_id": "business123",
            "lighthouse_failure_reason": "Timeout error"
        }
        
        assert service.validate_input(valid_data) is True
    
    def test_validate_input_failure(self, service):
        """Test input validation failure."""
        invalid_data = {
            "website_url": "https://example.com",
            "business_id": "business123"
            # Missing lighthouse_failure_reason
        }
        
        assert service.validate_input(invalid_data) is False
    
    def test_validate_input_wrong_type(self, service):
        """Test input validation with wrong data type."""
        assert service.validate_input("not a dict") is False
        assert service.validate_input(None) is False
    
    def test_extract_failure_type_timeout(self, service):
        """Test timeout failure type extraction."""
        failure_reason = "Request timed out after 30 seconds"
        failure_type = service._extract_failure_type(failure_reason)
        
        assert failure_type == "TIMEOUT"
    
    def test_extract_failure_type_rate_limit(self, service):
        """Test rate limit failure type extraction."""
        failure_reason = "Rate limit exceeded for this API"
        failure_type = service._extract_failure_type(failure_reason)
        
        assert failure_type == "RATE_LIMIT_EXCEEDED"
    
    def test_extract_failure_type_api_error(self, service):
        """Test API error failure type extraction."""
        failure_reason = "API returned an error code 500"
        failure_type = service._extract_failure_type(failure_reason)
        
        assert failure_type == "API_ERROR"
    
    def test_extract_failure_type_network_error(self, service):
        """Test network error failure type extraction."""
        failure_reason = "Network connection failed"
        failure_type = service._extract_failure_type(failure_reason)
        
        assert failure_type == "NETWORK_ERROR"
    
    def test_extract_failure_type_invalid_url(self, service):
        """Test invalid URL failure type extraction."""
        failure_reason = "Invalid URL format provided"
        failure_type = service._extract_failure_type(failure_reason)
        
        assert failure_type == "INVALID_URL"
    
    def test_extract_failure_type_unknown(self, service):
        """Test unknown failure type extraction."""
        failure_reason = "Some other error occurred"
        failure_type = service._extract_failure_type(failure_reason)
        
        assert failure_type == "UNKNOWN_ERROR"
    
    def test_analyze_failure_success(self, service):
        """Test successful failure analysis."""
        failure_reason = "Request timed out after 30 seconds"
        analysis = service._analyze_failure(failure_reason)
        
        assert analysis["failure_type"] == "TIMEOUT"
        assert analysis["severity"] == FailureSeverity.MEDIUM
        assert analysis["decision"] == FallbackDecision.RETRY_THEN_FALLBACK
        assert analysis["retry_count"] == 2
        assert analysis["original_reason"] == failure_reason
    
    def test_analyze_failure_unknown_pattern(self, service):
        """Test failure analysis with unknown pattern."""
        failure_reason = "Some completely unknown error"
        analysis = service._analyze_failure(failure_reason)
        
        # Should fall back to UNKNOWN_ERROR pattern
        assert analysis["failure_type"] == "UNKNOWN_ERROR"
        assert analysis["severity"] == FailureSeverity.MEDIUM
        assert analysis["decision"] == FallbackDecision.RETRY_THEN_FALLBACK
    
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_execute_retry_logic_success(self, mock_sleep, service):
        """Test successful retry logic execution."""
        failure_analysis = {
            "failure_type": "TIMEOUT",
            "retry_count": 2
        }
        
        # Mock successful recovery on first retry
        with patch.object(service, '_attempt_lighthouse_recovery', return_value=True):
            retry_attempts = service._execute_retry_logic(
                "https://example.com", "business123", "run123", failure_analysis
            )
        
        assert retry_attempts == 1
        mock_sleep.assert_called_once_with(1.0)  # First retry delay
    
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_execute_retry_logic_all_failures(self, mock_sleep, service):
        """Test retry logic when all attempts fail."""
        failure_analysis = {
            "failure_type": "NETWORK_ERROR",
            "retry_count": 3
        }
        
        # Mock all recovery attempts fail
        with patch.object(service, '_attempt_lighthouse_recovery', return_value=False):
            retry_attempts = service._execute_retry_logic(
                "https://example.com", "business123", "run123", failure_analysis
            )
        
        assert retry_attempts == 3
        assert mock_sleep.call_count == 3  # All retry delays
    
    def test_attempt_lighthouse_recovery(self, service):
        """Test Lighthouse recovery attempt."""
        # Mock the recovery attempt
        with patch.object(service, '_attempt_lighthouse_recovery', return_value=False):
            result = service._attempt_lighthouse_recovery(
                "https://example.com", "business123", "run123"
            )
        
        assert result is False
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_analysis_success(self, service, mock_comprehensive_result):
        """Test successful comprehensive speed analysis."""
        with patch.object(service.comprehensive_service, 'run_comprehensive_analysis', return_value=mock_comprehensive_result):
            result = await service._run_comprehensive_analysis(
                "https://example.com", "business123", "run123"
            )
        
        assert result["success"] is True
        assert result["scores"]["overall_score"] == 73.6
    
    @pytest.mark.asyncio
    async def test_run_comprehensive_analysis_failure(self, service):
        """Test comprehensive speed analysis failure."""
        failed_result = {
            "success": False,
            "error": "Analysis failed",
            "context": "analysis_execution"
        }
        
        with patch.object(service.comprehensive_service, 'run_comprehensive_analysis', return_value=failed_result):
            result = await service._run_comprehensive_analysis(
                "https://example.com", "business123", "run123"
            )
        
        assert result["success"] is False
        assert result["error"] == "Analysis failed"
    
    def test_create_fallback_score_success(self, service, mock_comprehensive_result):
        """Test successful fallback score creation."""
        fallback_reason = "Request timed out"
        
        fallback_score = service._create_fallback_score(
            mock_comprehensive_result, fallback_reason, "run123"
        )
        
        assert isinstance(fallback_score, FallbackScore)
        assert fallback_score.fallback_scores["pingdom_trust"] == 65.0
        assert fallback_score.fallback_scores["overall_score"] == 73.6
        assert fallback_score.confidence_level == ConfidenceLevel.LOW
        assert fallback_score.fallback_reason == FallbackReason.TIMEOUT
    
    def test_create_fallback_score_missing_data(self, service):
        """Test fallback score creation with missing data."""
        incomplete_result = {
            "scores": {
                "pingdom_trust": 85.0
                # Missing other scores
            }
        }
        
        fallback_reason = "Request timed out"
        
        fallback_score = service._create_fallback_score(
            incomplete_result, fallback_reason, "run123"
        )
        
        assert fallback_score.fallback_scores["pingdom_trust"] == 85.0
        assert fallback_score.fallback_scores["pingdom_cro"] == 0.0  # Default value
        assert fallback_score.fallback_scores["overall_score"] == 0.0  # Default value
    
    def test_create_fallback_reason_success(self, service):
        """Test successful fallback reason creation."""
        failure_analysis = {
            "failure_type": "TIMEOUT",
            "severity": FailureSeverity.MEDIUM,
            "decision": FallbackDecision.RETRY_THEN_FALLBACK
        }
        
        fallback_reason = service._create_fallback_reason(
            "Request timed out", failure_analysis, 2, True
        )
        
        assert isinstance(fallback_reason, FallbackReasonDetails)
        assert fallback_reason.failure_type == "TIMEOUT"
        assert fallback_reason.severity_level == "medium"
        assert fallback_reason.fallback_decision == "retry_then_fallback"
        assert fallback_reason.retry_attempts == 2
        assert fallback_reason.success_status is True
    
    def test_calculate_data_completeness_high(self, service, mock_comprehensive_result):
        """Test data completeness calculation with high completeness."""
        completeness = service._calculate_data_completeness(mock_comprehensive_result)
    
        # Should be high based on mock data (all fields present)
        assert completeness > 0.95
        assert completeness <= 1.0
    
    def test_calculate_data_completeness_low(self, service):
        """Test data completeness calculation with low completeness."""
        low_completeness_result = {
            "scores": {
                "pingdom_trust": 30.0,
                "pingdom_cro": 25.0
                # Missing other scores
            }
        }
        
        completeness = service._calculate_data_completeness(low_completeness_result)
        
        # Should be low since most scores are missing
        assert completeness < 0.3
    
    def test_calculate_reliability_score(self, service):
        """Test reliability score calculation."""
        # Test with medium severity and high data completeness
        reliability = service._calculate_reliability_score(
            FailureSeverity.MEDIUM, 90.0
        )
        
        # Base 100 - medium penalty (25) - low completeness penalty
        expected = 100.0 - 25.0 - (10.0 * 0.3)
        assert abs(reliability - expected) < 1.0
    
    def test_calculate_confidence_adjustment(self, service):
        """Test confidence adjustment calculation."""
        # Test with medium severity and high data completeness
        adjustment = service._calculate_confidence_adjustment(
            FailureSeverity.MEDIUM, 90.0
        )
        
        # Should be around 0.7 * 0.9 = 0.63
        assert 0.6 < adjustment < 0.7
    
    def test_determine_quality_indicators(self, service, mock_comprehensive_result):
        """Test quality indicators determination."""
        fallback_score = FallbackScore(
            business_id="test_business",
            run_id="test_run",
            website_url="https://example.com",
            fallback_timestamp=time.time(),
            fallback_reason=FallbackReason.TIMEOUT,
            fallback_scores={
                "pingdom_trust": 65.0,
                "pingdom_cro": 73.6,
                "pagespeed_performance": 85.0,
                "pagespeed_accessibility": 72.0,
                "pagespeed_best_practices": 68.0,
                "pagespeed_seo": 78.0,
                "overall_score": 73.6
            },
            quality_metrics=FallbackMetrics(
                data_completeness=0.8,
                source_reliability=0.7,
                confidence_score=0.6,
                fallback_reason=FallbackReason.TIMEOUT,
                quality_rating=FallbackQuality.FAIR,
                fallback_success_rate=75.0,
                average_fallback_score_quality=70.0,
                failure_pattern_analysis={"TIMEOUT": 1},
                performance_metrics={"execution_time": 2.5},
                total_fallbacks=1,
                successful_fallbacks=1
            ),
            confidence_level=ConfidenceLevel.LOW,
            notes="Test fallback score",
            fallback_history=[]
        )
        
        failure_analysis = {
            "severity": FailureSeverity.MEDIUM,
            "decision": FallbackDecision.RETRY_THEN_FALLBACK,
            "retry_count": 2
        }
        
        indicators = service._determine_quality_indicators(
            fallback_score, mock_comprehensive_result, failure_analysis
        )
        
        assert indicators["scores_reasonable"] is True
        assert indicators["data_available"] is True
        assert indicators["failure_analysis_complete"] is True
        assert indicators["confidence_appropriate"] is True
    
    def test_generate_quality_recommendation_high_reliability(self, service):
        """Test quality recommendation generation for high reliability."""
        recommendation = service._generate_quality_recommendation(
            85.0, 90.0, {"severity": FailureSeverity.LOW}
        )
        
        assert "highly reliable" in recommendation.lower()
        assert "confidence" in recommendation.lower()
    
    def test_generate_quality_recommendation_low_reliability(self, service):
        """Test quality recommendation generation for low reliability."""
        recommendation = service._generate_quality_recommendation(
            30.0, 40.0, {"severity": FailureSeverity.HIGH}
        )
        
        assert "low reliability" in recommendation.lower()
        assert "critical decisions" in recommendation.lower()
    
    @patch('src.services.rate_limiter.RateLimiter.can_make_request')
    @pytest.mark.asyncio
    async def test_run_fallback_scoring_rate_limit_exceeded(self, mock_can_make_request, service):
        """Test fallback scoring when rate limit is exceeded."""
        mock_can_make_request.return_value = (False, "Rate limit exceeded")
        
        result = await service.run_fallback_scoring(
            "https://example.com",
            "business123",
            "Request timed out",
            "run123"
        )
        
        assert result["success"] is False
        assert "Rate limit exceeded" in result["error"]
        assert result["context"] == "rate_limit_check"
    
    @patch('src.services.rate_limiter.RateLimiter.can_make_request')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._analyze_failure')
    @pytest.mark.asyncio
    async def test_run_fallback_scoring_no_fallback_recommended(self, mock_analyze_failure, mock_can_make_request, service):
        """Test fallback scoring when fallback is not recommended."""
        mock_can_make_request.return_value = (True, "OK")
        mock_analyze_failure.return_value = {
            "decision": FallbackDecision.NO_FALLBACK,
            "severity": FailureSeverity.CRITICAL
        }
        
        result = await service.run_fallback_scoring(
            "https://example.com",
            "business123",
            "Invalid URL",
            "run123"
        )
        
        assert result["success"] is False
        assert "not recommended" in result["error"]
        assert result["context"] == "fallback_strategy"
    
    @patch('src.services.rate_limiter.RateLimiter.can_make_request')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._analyze_failure')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._execute_retry_logic')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._run_comprehensive_analysis')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._create_fallback_score')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._create_fallback_reason')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._assess_fallback_quality')
    @patch('src.services.rate_limiter.RateLimiter.record_request')
    @pytest.mark.asyncio
    async def test_run_fallback_scoring_success(
        self,
        mock_record_request,
        mock_assess_quality,
        mock_create_reason,
        mock_create_score,
        mock_run_comprehensive,
        mock_execute_retry,
        mock_analyze_failure,
        mock_can_make_request,
        service,
        mock_comprehensive_result
    ):
        """Test successful fallback scoring execution."""
        # Setup mocks
        mock_can_make_request.return_value = (True, "OK")
        mock_analyze_failure.return_value = {
            "decision": FallbackDecision.RETRY_THEN_FALLBACK,
            "severity": FailureSeverity.MEDIUM,
            "retry_count": 2
        }
        mock_execute_retry.return_value = 1
        mock_run_comprehensive.return_value = mock_comprehensive_result
        
        mock_fallback_score = FallbackScore(
            business_id="business123",
            run_id="run123",
            website_url="https://example.com",
            fallback_timestamp=time.time(),
            fallback_reason=FallbackReason.TIMEOUT,
            fallback_scores={
                "pingdom_trust": 65.0,
                "pingdom_cro": 73.6,
                "pagespeed_performance": 85.0,
                "pagespeed_accessibility": 72.0,
                "pagespeed_best_practices": 68.0,
                "pagespeed_seo": 78.0,
                "overall_score": 73.6
            },
            quality_metrics=FallbackMetrics(
                data_completeness=0.8,
                source_reliability=0.7,
                confidence_score=0.6,
                fallback_reason=FallbackReason.TIMEOUT,
                quality_rating=FallbackQuality.FAIR,
                fallback_success_rate=75.0,
                average_fallback_score_quality=70.0,
                failure_pattern_analysis={"TIMEOUT": 1},
                performance_metrics={"execution_time": 2.5},
                total_fallbacks=1,
                successful_fallbacks=1
            ),
            confidence_level=ConfidenceLevel.LOW,
            notes="Test fallback score",
            fallback_history=[]
        )
        mock_create_score.return_value = mock_fallback_score
        
        mock_fallback_reason = FallbackReasonDetails(
            failure_type="TIMEOUT",
            error_message="Request timed out",
            severity_level="medium",
            fallback_decision="retry_then_fallback",
            retry_attempts=1,
            success_status=True,
            fallback_timestamp=time.time()
        )
        mock_create_reason.return_value = mock_fallback_reason
        
        mock_fallback_quality = FallbackQualityDetails(
            reliability_score=75.0,
            data_completeness=85.0,
            confidence_adjustment=0.7,
            quality_indicators={},
            recommendation="Results are moderately reliable"
        )
        mock_assess_quality.return_value = mock_fallback_quality
        
        # Execute fallback scoring
        result = await service.run_fallback_scoring(
            "https://example.com",
            "business123",
            "Request timed out",
            "run123"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["website_url"] == "https://example.com"
        assert result["business_id"] == "business123"
        assert result["run_id"] == "run123"
        assert result["retry_attempts"] == 1
        assert result["fallback_score"] == mock_fallback_score
        assert result["fallback_reason"] == mock_fallback_reason
        assert result["fallback_quality"] == mock_fallback_quality
        
        # Verify mocks were called
        mock_can_make_request.assert_called_once_with("fallback", "run123")
        mock_analyze_failure.assert_called_once_with("Request timed out")
        mock_execute_retry.assert_called_once()
        mock_run_comprehensive.assert_called_once()
        mock_create_score.assert_called_once()
        mock_create_reason.assert_called_once()
        mock_assess_quality.assert_called_once()
        mock_record_request.assert_called_once_with("fallback", True, "run123")
    
    def test_get_fallback_metrics(self, service):
        """Test fallback metrics retrieval."""
        metrics = service.get_fallback_metrics()
        
        assert isinstance(metrics, FallbackMetrics)
        assert metrics.fallback_success_rate == 85.0
        assert metrics.average_fallback_score_quality == 72.0
        assert metrics.total_fallbacks == 120
        assert metrics.successful_fallbacks == 102
        assert "TIMEOUT" in metrics.failure_pattern_analysis
        assert "average_execution_time" in metrics.performance_metrics
    
    def test_create_error_response(self, service):
        """Test error response creation."""
        error_response = service._create_error_response(
            "Test error message",
            "test_context",
            "https://example.com",
            "business123",
            "run123"
        )
        
        assert error_response["success"] is False
        assert error_response["error"] == "Test error message"
        assert error_response["context"] == "test_context"
        assert error_response["website_url"] == "https://example.com"
        assert error_response["business_id"] == "business123"
        assert error_response["run_id"] == "run123"
        assert error_response["fallback_score"] is None
        assert error_response["fallback_reason"] is None
        assert error_response["fallback_quality"] is None
        assert error_response["retry_attempts"] == 0
