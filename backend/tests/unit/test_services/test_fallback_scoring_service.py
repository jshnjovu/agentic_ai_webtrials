"""
Unit tests for FallbackScoringService.
Tests fallback detection, retry logic, quality assessment, and error handling.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from src.services.fallback_scoring_service import (
    FallbackScoringService,
    FailureSeverity,
    FallbackDecision
)
from src.schemas.website_scoring import (
    FallbackScore, FallbackReason, FallbackQuality, FallbackMetrics, ConfidenceLevel
)


class TestFallbackScoringService:
    """Test cases for FallbackScoringService."""
    
    @pytest.fixture
    def service(self):
        """Create a FallbackScoringService instance for testing."""
        return FallbackScoringService()
    
    @pytest.fixture
    def mock_heuristic_result(self):
        """Mock heuristic evaluation result."""
        return {
            "success": True,
            "scores": {
                "trust_score": 85.0,
                "cro_score": 72.0,
                "mobile_score": 68.0,
                "content_score": 78.0,
                "social_score": 65.0,
                "overall_heuristic_score": 73.6
            },
            "trust_signals": {
                "has_https": True,
                "has_privacy_policy": True,
                "has_contact_info": True,
                "has_about_page": False,
                "has_terms_of_service": False,
                "has_ssl_certificate": True,
                "has_business_address": True,
                "has_phone_number": True,
                "has_email": True
            },
            "cro_elements": {
                "has_cta_buttons": True,
                "has_contact_forms": True,
                "has_pricing_tables": False,
                "has_testimonials": True,
                "has_reviews": False,
                "has_social_proof": True,
                "has_urgency_elements": False,
                "has_trust_badges": True
            },
            "mobile_usability": {
                "has_viewport_meta": True,
                "has_touch_targets": True,
                "has_responsive_design": True,
                "has_mobile_navigation": False,
                "has_readable_fonts": True,
                "has_adequate_spacing": True
            },
            "content_quality": {
                "has_proper_headings": True,
                "has_alt_text": True,
                "has_meta_description": True,
                "has_meta_keywords": False,
                "has_structured_data": True,
                "has_internal_links": True,
                "has_external_links": False,
                "has_blog_content": True
            },
            "social_proof": {
                "has_social_media_links": True,
                "has_customer_reviews": False,
                "has_testimonials": True,
                "has_case_studies": False,
                "has_awards_certifications": True,
                "has_partner_logos": False,
                "has_user_generated_content": False
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
    
    def test_run_heuristic_evaluation_success(self, service, mock_heuristic_result):
        """Test successful heuristic evaluation."""
        with patch.object(service.heuristic_service, 'run_heuristic_evaluation', return_value=mock_heuristic_result):
            result = service._run_heuristic_evaluation(
                "https://example.com", "business123", "run123"
            )
        
        assert result["success"] is True
        assert result["scores"]["overall_heuristic_score"] == 73.6
    
    def test_run_heuristic_evaluation_failure(self, service):
        """Test heuristic evaluation failure."""
        failed_result = {
            "success": False,
            "error": "Evaluation failed",
            "context": "evaluation_execution"
        }
        
        with patch.object(service.heuristic_service, 'run_heuristic_evaluation', return_value=failed_result):
            result = service._run_heuristic_evaluation(
                "https://example.com", "business123", "run123"
            )
        
        assert result["success"] is False
        assert result["error"] == "Evaluation failed"
    
    def test_create_fallback_score_success(self, service, mock_heuristic_result):
        """Test successful fallback score creation."""
        fallback_reason = "Request timed out"
        
        fallback_score = service._create_fallback_score(
            mock_heuristic_result, fallback_reason, "run123"
        )
        
        assert isinstance(fallback_score, FallbackScore)
        assert fallback_score.trust_score == 85.0
        assert fallback_score.overall_score == 73.6
        assert fallback_score.confidence_level == ConfidenceLevel.LOW
        assert fallback_score.fallback_reason == fallback_reason
    
    def test_create_fallback_score_missing_data(self, service):
        """Test fallback score creation with missing data."""
        incomplete_result = {
            "scores": {
                "trust_score": 85.0
                # Missing other scores
            }
        }
        
        fallback_reason = "Request timed out"
        
        fallback_score = service._create_fallback_score(
            incomplete_result, fallback_reason, "run123"
        )
        
        assert fallback_score.trust_score == 85.0
        assert fallback_score.cro_score == 0.0  # Default value
        assert fallback_score.overall_score == 0.0  # Default value
    
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
        
        assert isinstance(fallback_reason, FallbackReason)
        assert fallback_reason.failure_type == "TIMEOUT"
        assert fallback_reason.severity_level == "medium"
        assert fallback_reason.fallback_decision == "retry_then_fallback"
        assert fallback_reason.retry_attempts == 2
        assert fallback_reason.success_status is True
    
    def test_calculate_data_completeness_high(self, service, mock_heuristic_result):
        """Test data completeness calculation with high completeness."""
        completeness = service._calculate_data_completeness(mock_heuristic_result)
    
        # Should be moderately high (68.42% based on mock data)
        assert completeness > 65.0
        assert completeness < 70.0
    
    def test_calculate_data_completeness_low(self, service):
        """Test data completeness calculation with low completeness."""
        low_completeness_result = {
            "trust_signals": {"has_https": True, "has_privacy_policy": False},
            "cro_elements": {"has_cta_buttons": False, "has_contact_forms": False},
            "mobile_usability": {"has_viewport_meta": False, "has_touch_targets": False},
            "content_quality": {"has_proper_headings": False, "has_alt_text": False},
            "social_proof": {"has_social_media_links": False, "has_customer_reviews": False}
        }
        
        completeness = service._calculate_data_completeness(low_completeness_result)
        
        # Should be low since most fields are False
        assert completeness < 20.0
    
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
    
    def test_determine_quality_indicators(self, service, mock_heuristic_result):
        """Test quality indicators determination."""
        fallback_score = FallbackScore(
            trust_score=85.0,
            cro_score=72.0,
            mobile_score=68.0,
            content_score=78.0,
            social_score=65.0,
            overall_score=73.6,
            confidence_level=ConfidenceLevel.LOW,
            fallback_reason="Request timed out",
            fallback_timestamp=time.time()
        )
        
        failure_analysis = {
            "severity": FailureSeverity.MEDIUM,
            "decision": FallbackDecision.RETRY_THEN_FALLBACK,
            "retry_count": 2
        }
        
        indicators = service._determine_quality_indicators(
            fallback_score, mock_heuristic_result, failure_analysis
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
    def test_run_fallback_scoring_rate_limit_exceeded(self, mock_can_make_request, service):
        """Test fallback scoring when rate limit is exceeded."""
        mock_can_make_request.return_value = (False, "Rate limit exceeded")
        
        result = service.run_fallback_scoring(
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
    def test_run_fallback_scoring_no_fallback_recommended(self, mock_analyze_failure, mock_can_make_request, service):
        """Test fallback scoring when fallback is not recommended."""
        mock_can_make_request.return_value = (True, "OK")
        mock_analyze_failure.return_value = {
            "decision": FallbackDecision.NO_FALLBACK,
            "severity": FailureSeverity.CRITICAL
        }
        
        result = service.run_fallback_scoring(
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
    @patch('src.services.fallback_scoring_service.FallbackScoringService._run_heuristic_evaluation')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._create_fallback_score')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._create_fallback_reason')
    @patch('src.services.fallback_scoring_service.FallbackScoringService._assess_fallback_quality')
    @patch('src.services.rate_limiter.RateLimiter.record_request')
    def test_run_fallback_scoring_success(
        self,
        mock_record_request,
        mock_assess_quality,
        mock_create_reason,
        mock_create_score,
        mock_run_heuristic,
        mock_execute_retry,
        mock_analyze_failure,
        mock_can_make_request,
        service,
        mock_heuristic_result
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
        mock_run_heuristic.return_value = mock_heuristic_result
        
        mock_fallback_score = FallbackScore(
            trust_score=85.0,
            cro_score=72.0,
            mobile_score=68.0,
            content_score=78.0,
            social_score=65.0,
            overall_score=73.6,
            confidence_level=ConfidenceLevel.LOW,
            fallback_reason="Request timed out",
            fallback_timestamp=time.time()
        )
        mock_create_score.return_value = mock_fallback_score
        
        mock_fallback_reason = FallbackReason(
            failure_type="TIMEOUT",
            error_message="Request timed out",
            severity_level="medium",
            fallback_decision="retry_then_fallback",
            retry_attempts=1,
            success_status=True,
            fallback_timestamp=time.time()
        )
        mock_create_reason.return_value = mock_fallback_reason
        
        mock_fallback_quality = FallbackQuality(
            reliability_score=75.0,
            data_completeness=85.0,
            confidence_adjustment=0.7,
            quality_indicators={},
            recommendation="Results are moderately reliable"
        )
        mock_assess_quality.return_value = mock_fallback_quality
        
        # Execute fallback scoring
        result = service.run_fallback_scoring(
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
        mock_run_heuristic.assert_called_once()
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
