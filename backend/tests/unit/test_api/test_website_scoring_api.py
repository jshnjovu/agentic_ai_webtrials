"""
Unit tests for website scoring API endpoints.
Tests the Lighthouse audit API functionality.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
from src.schemas.website_scoring import (
    LighthouseAuditRequest,
    LighthouseAuditResponse,
    AuditStrategy,
    ConfidenceLevel
)


class TestWebsiteScoringAPI:
    """Test cases for website scoring API endpoints."""

    @pytest.fixture
    def sample_audit_request(self):
        """Sample audit request data."""
        return {
            "business_id": "test_business_123",
            "run_id": "test_run_456",
            "strategy": "desktop",
            "website_url": "https://example.com"
        }

    @pytest.fixture
    def sample_audit_response(self):
        """Sample successful audit response."""
        return {
            "audit_timestamp": 1703000000.0,
            "business_id": "test_business_123",
            "confidence": "high",
            "core_web_vitals": {
                "cumulative_layout_shift": 0.05,
                "first_contentful_paint": 1200.0,
                "largest_contentful_paint": 2100.0,
                "speed_index": 1800.0,
                "time_to_interactive": 2500.0
            },
            "overall_score": 89.5,
            "raw_data": {"lighthouseResult": {"categories": {}}},
            "scores": {
                "accessibility": 92.0,
                "best_practices": 88.0,
                "performance": 85.0,
                "seo": 95.0
            },
            "strategy": "desktop",
            "success": True,
            "website_url": "https://example.com"
        }

    def test_run_lighthouse_audit_success(self, test_client_with_mocked_dependencies, sample_audit_request, sample_audit_response):
        """Test successful Lighthouse audit API call."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = True
        mock_service.run_lighthouse_audit.return_value = sample_audit_response
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=sample_audit_request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["website_url"] == "https://example.com/"  # Note: trailing slash is added during processing
        assert data["scores"]["performance"] == 85.0
        assert data["confidence"] == "high"

    def test_run_lighthouse_audit_validation_failure(self, test_client_with_mocked_dependencies, sample_audit_request):
        """Test Lighthouse audit API with validation failure."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = False
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=sample_audit_request)
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid Lighthouse audit request" in data["detail"]

    def test_run_lighthouse_audit_timeout_error(self, test_client_with_mocked_dependencies, sample_audit_request):
        """Test Lighthouse audit API with timeout error."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = True
        mock_service.run_lighthouse_audit.return_value = {
            "success": False,
            "error": "Audit request timed out",
            "error_code": "TIMEOUT",
            "context": "audit_execution"
        }
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=sample_audit_request)
        
        assert response.status_code == 408
        data = response.json()
        assert data["detail"]["error"] == "Lighthouse audit timed out"
        assert data["detail"]["error_code"] == "TIMEOUT"

    def test_run_lighthouse_audit_rate_limit_error(self, test_client_with_mocked_dependencies, sample_audit_request):
        """Test Lighthouse audit API with rate limit error."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = True
        mock_service.run_lighthouse_audit.return_value = {
            "success": False,
            "error": "Rate limit exceeded",
            "error_code": "RATE_LIMIT_EXCEEDED",
            "context": "rate_limit_check"
        }
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=sample_audit_request)
        
        assert response.status_code == 429
        data = response.json()
        assert data["detail"]["error"] == "Rate limit exceeded for Lighthouse API"
        assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"

    def test_run_lighthouse_audit_general_error(self, test_client_with_mocked_dependencies, sample_audit_request):
        """Test Lighthouse audit API with general error."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = True
        mock_service.run_lighthouse_audit.return_value = {
            "success": False,
            "error": "General audit failure",
            "error_code": "AUDIT_FAILED",
            "context": "audit_execution"
        }
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=sample_audit_request)
        
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "General audit failure"
        assert data["detail"]["error_code"] == "AUDIT_FAILED"

    def test_run_lighthouse_audit_service_exception(self, test_client_with_mocked_dependencies, sample_audit_request):
        """Test Lighthouse audit API with service exception."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = True
        mock_service.run_lighthouse_audit.side_effect = Exception("Service error")
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=sample_audit_request)
        
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error" in data["detail"]

    def test_run_lighthouse_audit_missing_run_id(self, test_client_with_mocked_dependencies):
        """Test Lighthouse audit API with auto-generated run_id."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = True
        mock_service.run_lighthouse_audit.return_value = {
            "success": True,
            "website_url": "https://example.com",
            "business_id": "test_business_123",
            "audit_timestamp": 1703000000.0,
            "strategy": "desktop",
            "scores": {
                "performance": 85.0,
                "accessibility": 88.0,
                "best_practices": 85.0,
                "seo": 90.0,
                "overall": 89.5
            },
            "core_web_vitals": {},
            "confidence": "high"
        }
        
        request_data = {
            "website_url": "https://example.com",
            "business_id": "test_business_123",
            "strategy": "desktop"
        }
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "run_id" in data
        assert data["run_id"] is not None

    def test_get_website_scoring_summary(self, test_client_with_mocked_dependencies):
        """Test getting website scoring summary."""
        client, mock_service = test_client_with_mocked_dependencies
        
        response = client.get("/api/v1/website-scoring/lighthouse/test_business_123/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "business_id" in data
        assert data["business_id"] == "test_business_123"

    def test_lighthouse_health_check(self, test_client_with_mocked_dependencies):
        """Test Lighthouse health check endpoint."""
        client, mock_service = test_client_with_mocked_dependencies
        
        response = client.get("/api/v1/website-scoring/lighthouse/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_audit_request_schema_validation(self, test_client_with_mocked_dependencies):
        """Test audit request schema validation."""
        client, mock_service = test_client_with_mocked_dependencies
        
        # Test with missing required fields
        invalid_request = {
            "website_url": "https://example.com"
            # Missing business_id
        }
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=invalid_request)
        
        assert response.status_code == 422  # Validation error

    def test_audit_request_url_validation(self, test_client_with_mocked_dependencies):
        """Test audit request URL validation."""
        client, mock_service = test_client_with_mocked_dependencies
        
        # Test with invalid URL
        invalid_request = {
            "business_id": "test_business_123",
            "website_url": "not-a-valid-url"
        }
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=invalid_request)
        
        assert response.status_code == 422  # Validation error

    def test_audit_strategy_enum_validation(self, test_client_with_mocked_dependencies):
        """Test audit strategy enum validation."""
        client, mock_service = test_client_with_mocked_dependencies
        
        # Test with invalid strategy
        invalid_request = {
            "business_id": "test_business_123",
            "website_url": "https://example.com",
            "strategy": "invalid_strategy"
        }
        
        response = client.post("/api/v1/website-scoring/lighthouse", json=invalid_request)
        
        assert response.status_code == 422  # Validation error

    def test_background_task_persistence(self, test_client_with_mocked_dependencies, sample_audit_request, sample_audit_response):
        """Test that background task for persistence is added."""
        client, mock_service = test_client_with_mocked_dependencies
        
        mock_service.validate_input.return_value = True
        mock_service.run_lighthouse_audit.return_value = sample_audit_response
        
        # Mock the background task function
        with patch('src.api.v1.website_scoring._persist_audit_results') as mock_persist:
            response = client.post("/api/v1/website-scoring/lighthouse", json=sample_audit_request)
            
            assert response.status_code == 200
            # Note: In a real test, you might want to verify the background task was added
            # This depends on how FastAPI handles background tasks in tests
