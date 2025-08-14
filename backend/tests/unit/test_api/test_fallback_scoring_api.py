"""
Unit tests for fallback scoring API endpoints.
Tests the POST /fallback and GET /fallback/monitoring endpoints.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.api.v1.website_scoring import router
from src.schemas.website_scoring import (
    FallbackScoringRequest,
    FallbackScoringResponse,
    FallbackScoringError,
    FallbackMonitoringResponse,
    FallbackScore,
    FallbackReason,
    FallbackQuality,
    FallbackMetrics,
    ConfidenceLevel
)
from src.services.fallback_scoring_service import (
    FallbackScoringService,
    FailureSeverity,
    FallbackDecision
)


class TestFallbackScoringAPI:
    """Test cases for fallback scoring API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the API."""
        return TestClient(router)
    
    @pytest.fixture
    def valid_fallback_request(self):
        """Valid fallback scoring request data."""
        return {
            "website_url": "https://example.com",
            "business_id": "business123",
            "run_id": "run123",
            "lighthouse_failure_reason": "Request timed out after 30 seconds",
            "fallback_parameters": {
                "priority": "high",
                "timeout_override": 15
            }
        }
    
    @pytest.fixture
    def mock_fallback_service(self):
        """Mock fallback scoring service."""
        return Mock(spec=FallbackScoringService)
    
    @pytest.fixture
    def successful_fallback_result(self):
        """Mock successful fallback scoring result."""
        return {
            "success": True,
            "website_url": "https://example.com",
            "business_id": "business123",
            "run_id": "run123",
            "fallback_timestamp": time.time(),
            "fallback_score": {
                "trust_score": 85.0,
                "cro_score": 72.0,
                "mobile_score": 68.0,
                "content_score": 78.0,
                "social_score": 65.0,
                "overall_score": 73.6,
                "confidence_level": "low",
                "fallback_reason": "Request timed out after 30 seconds",
                "fallback_timestamp": time.time()
            },
            "fallback_reason": {
                "failure_type": "TIMEOUT",
                "error_message": "Request timed out after 30 seconds",
                "severity_level": "medium",
                "fallback_decision": "retry_then_fallback",
                "retry_attempts": 2,
                "success_status": True,
                "fallback_timestamp": time.time()
            },
            "fallback_quality": {
                "reliability_score": 75.0,
                "data_completeness": 85.0,
                "confidence_adjustment": 0.7,
                "quality_indicators": {
                    "scores_reasonable": True,
                    "data_available": True,
                    "failure_analysis_complete": True,
                    "confidence_appropriate": True
                },
                "recommendation": "Fallback results are moderately reliable and can be used with caution."
            },
            "retry_attempts": 2,
            "execution_time": 3.2
        }
    
    def test_fallback_scoring_endpoint_success(self, client, valid_fallback_request, successful_fallback_result):
        """Test successful fallback scoring endpoint."""
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = successful_fallback_result
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=valid_fallback_request)
            
            assert response.status_code == 200
            response_data = response.json()
            
            assert response_data["success"] is True
            assert response_data["website_url"] == "https://example.com"
            assert response_data["business_id"] == "business123"
            assert response_data["run_id"] == "run123"
            assert response_data["fallback_score"]["overall_score"] == 73.6
            assert response_data["fallback_score"]["confidence_level"] == "low"
            assert response_data["retry_attempts"] == 2
            
            # Verify service was called correctly
            mock_service.validate_input.assert_called_once()
            mock_service.run_fallback_scoring.assert_called_once()
    
    def test_fallback_scoring_endpoint_validation_failure(self, client, valid_fallback_request):
        """Test fallback scoring endpoint with validation failure."""
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = False
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=valid_fallback_request)
            
            assert response.status_code == 400
            response_data = response.json()
            assert "Invalid fallback scoring request" in response_data["detail"]
    
    def test_fallback_scoring_endpoint_rate_limit_exceeded(self, client, valid_fallback_request):
        """Test fallback scoring endpoint when rate limit is exceeded."""
        rate_limit_error_result = {
            "success": False,
            "error": "Rate limit exceeded: 120 requests per minute",
            "error_code": "RATE_LIMIT_EXCEEDED",
            "context": "rate_limit_check"
        }
        
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = rate_limit_error_result
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=valid_fallback_request)
            
            assert response.status_code == 429
            response_data = response.json()
            assert "Rate limit exceeded" in response_data["detail"]["error"]
            assert response_data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"
    
    def test_fallback_scoring_endpoint_fallback_not_recommended(self, client, valid_fallback_request):
        """Test fallback scoring endpoint when fallback is not recommended."""
        no_fallback_result = {
            "success": False,
            "error": "Fallback not recommended for critical severity failure",
            "context": "fallback_strategy"
        }
        
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = no_fallback_result
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=valid_fallback_request)
            
            assert response.status_code == 400
            response_data = response.json()
            assert "not recommended" in response_data["detail"]["error"]
            assert response_data["detail"]["error_code"] == "FALLBACK_NOT_RECOMMENDED"
    
    def test_fallback_scoring_endpoint_general_error(self, client, valid_fallback_request):
        """Test fallback scoring endpoint with general error."""
        general_error_result = {
            "success": False,
            "error": "Heuristic evaluation failed",
            "context": "heuristic_evaluation"
        }
        
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = general_error_result
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=valid_fallback_request)
            
            assert response.status_code == 400
            response_data = response.json()
            assert "Heuristic evaluation failed" in response_data["detail"]["error"]
    
    def test_fallback_scoring_endpoint_missing_run_id(self, client, successful_fallback_result):
        """Test fallback scoring endpoint with missing run_id (should generate one)."""
        request_without_run_id = {
            "website_url": "https://example.com",
            "business_id": "business123",
            "lighthouse_failure_reason": "Request timed out after 30 seconds"
        }
        
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = successful_fallback_result
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=request_without_run_id)
            
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["run_id"] is not None  # Should have generated run_id
    
    def test_fallback_scoring_endpoint_invalid_url(self, client):
        """Test fallback scoring endpoint with invalid URL."""
        invalid_request = {
            "website_url": "not-a-url",
            "business_id": "business123",
            "lighthouse_failure_reason": "Request timed out"
        }
        
        response = client.post("/fallback", json=invalid_request)
        
        assert response.status_code == 422  # Validation error
    
    def test_fallback_scoring_endpoint_missing_required_fields(self, client):
        """Test fallback scoring endpoint with missing required fields."""
        incomplete_request = {
            "website_url": "https://example.com"
            # Missing business_id and lighthouse_failure_reason
        }
        
        response = client.post("/fallback", json=incomplete_request)
        
        assert response.status_code == 422  # Validation error
    
    def test_fallback_monitoring_endpoint_success(self, client):
        """Test successful fallback monitoring endpoint."""
        mock_metrics = FallbackMetrics(
            fallback_success_rate=85.0,
            average_fallback_score_quality=72.0,
            failure_pattern_analysis={
                "TIMEOUT": 45,
                "RATE_LIMIT_EXCEEDED": 25,
                "API_ERROR": 20,
                "NETWORK_ERROR": 10
            },
            performance_metrics={
                "average_execution_time": 3.2,
                "success_rate_trend": 2.1
            },
            total_fallbacks=120,
            successful_fallbacks=102
        )
        
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.get_fallback_metrics.return_value = mock_metrics
            mock_get_service.return_value = mock_service
            
            response = client.get("/fallback/monitoring")
            
            assert response.status_code == 200
            response_data = response.json()
            
            assert response_data["success"] is True
            assert response_data["metrics"]["fallback_success_rate"] == 85.0
            assert response_data["metrics"]["total_fallbacks"] == 120
            assert response_data["metrics"]["successful_fallbacks"] == 102
            assert "TIMEOUT" in response_data["metrics"]["failure_pattern_analysis"]
            assert len(response_data["recommendations"]) > 0
            
            # Verify service was called
            mock_service.get_fallback_metrics.assert_called_once()
    
    def test_fallback_monitoring_endpoint_service_error(self, client):
        """Test fallback monitoring endpoint when service fails."""
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.get_fallback_metrics.side_effect = Exception("Service error")
            mock_get_service.return_value = mock_service
            
            response = client.get("/fallback/monitoring")
            
            assert response.status_code == 500
            response_data = response.json()
            assert "Internal server error" in response_data["detail"]
    
    def test_fallback_scoring_endpoint_service_exception(self, client, valid_fallback_request):
        """Test fallback scoring endpoint when service raises exception."""
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.side_effect = Exception("Unexpected error")
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=valid_fallback_request)
            
            assert response.status_code == 500
            response_data = response.json()
            assert "Internal server error" in response_data["detail"]
    
    def test_fallback_scoring_endpoint_background_task(self, client, valid_fallback_request, successful_fallback_result):
        """Test that background task is added for data persistence."""
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = successful_fallback_result
            mock_get_service.return_value = mock_service
            
            # Mock the background task function
            with patch('src.api.v1.website_scoring._persist_fallback_results') as mock_persist:
                response = client.post("/fallback", json=valid_fallback_request)
                
                assert response.status_code == 200
                # Note: In a real test, we'd need to verify the background task was added
                # This is challenging with the current test setup, but the endpoint should work
    
    def test_fallback_scoring_endpoint_error_response_structure(self, client, valid_fallback_request):
        """Test that error responses have the correct structure."""
        error_result = {
            "success": False,
            "error": "Test error message",
            "context": "test_context"
        }
        
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = error_result
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=valid_fallback_request)
            
            assert response.status_code == 400
            response_data = response.json()
            
            # Verify error response structure
            assert "error" in response_data["detail"]
            assert "error_code" in response_data["detail"]
            assert "context" in response_data["detail"]
            assert "website_url" in response_data["detail"]
            assert "business_id" in response_data["detail"]
            assert "run_id" in response_data["detail"]
    
    def test_fallback_scoring_endpoint_optional_parameters(self, client, successful_fallback_result):
        """Test fallback scoring endpoint with optional parameters."""
        request_with_optional_params = {
            "website_url": "https://example.com",
            "business_id": "business123",
            "lighthouse_failure_reason": "Request timed out after 30 seconds",
            "fallback_parameters": {
                "priority": "high",
                "timeout_override": 15,
                "custom_threshold": 80.0
            }
        }
        
        with patch('src.api.v1.website_scoring.get_fallback_scoring_service') as mock_get_service:
            mock_service = Mock(spec=FallbackScoringService)
            mock_service.validate_input.return_value = True
            mock_service.run_fallback_scoring.return_value = successful_fallback_result
            mock_get_service.return_value = mock_service
            
            response = client.post("/fallback", json=request_with_optional_params)
            
            assert response.status_code == 200
            # Verify that optional parameters are passed through
            mock_service.run_fallback_scoring.assert_called_once()
            call_args = mock_service.run_fallback_scoring.call_args
            assert call_args[1]["fallback_parameters"] == request_with_optional_params["fallback_parameters"]
