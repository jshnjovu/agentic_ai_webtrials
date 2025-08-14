"""
Unit tests for authentication API endpoints.
Tests the FastAPI authentication routes.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from src.main import app


class TestAuthenticationAPI:
    """Test cases for authentication API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.base_url = "/api/v1/auth"
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        assert "LeadGen Makeover Agent API" in response.json()["message"]
    
    def test_root_health_endpoint(self):
        """Test the root health endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch('src.api.v1.authentication.validate_environment')
    @patch('src.api.v1.authentication.google_places_service.authenticate')
    def test_authenticate_google_places_success(self, mock_authenticate, mock_validate):
        """Test successful Google Places authentication."""
        # Mock environment validation
        mock_validate.return_value = True
        
        # Mock successful authentication
        mock_authenticate.return_value = {
            "success": True,
            "api_name": "google_places",
            "message": "Successfully authenticated with Google Places API",
            "run_id": "test-run-12345",
            "details": {"status": "OK"}
        }
        
        # Make request
        response = self.client.post(
            f"{self.base_url}/google-places",
            json={"run_id": "test-run-12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["api_name"] == "google_places"
        assert "Successfully authenticated" in data["message"]
    
    @patch('src.api.v1.authentication.validate_environment')
    def test_authenticate_google_places_environment_failure(self, mock_validate):
        """Test Google Places authentication with environment validation failure."""
        # Mock environment validation failure
        mock_validate.return_value = False
        
        # Make request
        response = self.client.post(
            f"{self.base_url}/google-places",
            json={"run_id": "test-run-12345"}
        )
        
        assert response.status_code == 500
        assert "Environment configuration validation failed" in response.json()["detail"]
    
    @patch('src.api.v1.authentication.validate_environment')
    @patch('src.api.v1.authentication.google_places_service.authenticate')
    def test_authenticate_google_places_authentication_failure(self, mock_authenticate, mock_validate):
        """Test Google Places authentication with authentication failure."""
        # Mock environment validation
        mock_validate.return_value = True
        
        # Mock authentication failure
        mock_authenticate.return_value = {
            "success": False,
            "error": "Invalid API key"
        }
        
        # Make request
        response = self.client.post(
            f"{self.base_url}/google-places",
            json={"run_id": "test-run-12345"}
        )
        
        assert response.status_code == 400
        assert "Invalid API key" in response.json()["detail"]
    
    @patch('src.api.v1.authentication.validate_environment')
    @patch('src.api.v1.authentication.yelp_fusion_service.authenticate')
    def test_authenticate_yelp_fusion_success(self, mock_authenticate, mock_validate):
        """Test successful Yelp Fusion authentication."""
        # Mock environment validation
        mock_validate.return_value = True
        
        # Mock successful authentication
        mock_authenticate.return_value = {
            "success": True,
            "api_name": "yelp_fusion",
            "message": "Successfully authenticated with Yelp Fusion API",
            "run_id": "test-run-12345",
            "details": {"total_businesses": 0}
        }
        
        # Make request
        response = self.client.post(
            f"{self.base_url}/yelp-fusion",
            json={"run_id": "test-run-12345"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["api_name"] == "yelp_fusion"
        assert "Successfully authenticated" in data["message"]
    
    @patch('src.api.v1.authentication.validate_environment')
    @patch('src.api.v1.authentication.yelp_fusion_service.authenticate')
    def test_authenticate_yelp_fusion_authentication_failure(self, mock_authenticate, mock_validate):
        """Test Yelp Fusion authentication with authentication failure."""
        # Mock environment validation
        mock_validate.return_value = True
        
        # Mock authentication failure
        mock_authenticate.return_value = {
            "success": False,
            "error": "Invalid Bearer token"
        }
        
        # Make request
        response = self.client.post(
            f"{self.base_url}/yelp-fusion",
            json={"run_id": "test-run-12345"}
        )
        
        assert response.status_code == 400
        assert "Invalid Bearer token" in response.json()["detail"]
    
    @patch('src.api.v1.authentication.google_places_service.get_health_status')
    @patch('src.api.v1.authentication.yelp_fusion_service.get_health_status')
    def test_health_check_success(self, mock_yelp_health, mock_google_health):
        """Test successful health check."""
        # Mock Google Places health
        mock_google_health.return_value = {
            "success": True,
            "api_name": "google_places",
            "message": "API is healthy"
        }
        
        # Mock Yelp Fusion health
        mock_yelp_health.return_value = {
            "success": True,
            "api_name": "yelp_fusion",
            "message": "API is healthy"
        }
        
        # Make request
        response = self.client.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "google_places" in data["apis"]
        assert "yelp_fusion" in data["apis"]
    
    @patch('src.api.v1.authentication.google_places_service.get_health_status')
    @patch('src.api.v1.authentication.yelp_fusion_service.get_health_status')
    def test_health_check_partial_failure(self, mock_yelp_health, mock_google_health):
        """Test health check with partial failure."""
        # Mock Google Places health
        mock_google_health.return_value = {
            "success": True,
            "api_name": "google_places",
            "message": "API is healthy"
        }
        
        # Mock Yelp Fusion health failure
        mock_yelp_health.return_value = {
            "success": False,
            "error": "Connection timeout"
        }
        
        # Make request
        response = self.client.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["apis"]["google_places"]["success"] is True
        assert data["apis"]["yelp_fusion"]["success"] is False
    
    @patch('src.api.v1.authentication.google_places_service.get_health_status')
    def test_google_places_health_only(self, mock_health):
        """Test Google Places health check endpoint."""
        # Mock health status
        mock_health.return_value = {
            "success": True,
            "api_name": "google_places",
            "message": "API is healthy"
        }
        
        # Make request
        response = self.client.get(f"{self.base_url}/google-places/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["api_name"] == "google_places"
    
    @patch('src.api.v1.authentication.yelp_fusion_service.get_health_status')
    def test_yelp_fusion_health_only(self, mock_health):
        """Test Yelp Fusion health check endpoint."""
        # Mock health status
        mock_health.return_value = {
            "success": True,
            "api_name": "yelp_fusion",
            "message": "API is healthy"
        }
        
        # Make request
        response = self.client.get(f"{self.base_url}/yelp-fusion/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["api_name"] == "yelp_fusion"
    
    def test_authenticate_google_places_invalid_json(self):
        """Test Google Places authentication with invalid JSON."""
        # Make request with invalid JSON
        response = self.client.post(
            f"{self.base_url}/google-places",
            json={"invalid_field": "value"}
        )
        
        # Should work as run_id is optional in the schema
        # The response will depend on the actual API call result
        assert response.status_code in [200, 400]  # 200 if API call succeeds, 400 if it fails
    
    def test_authenticate_yelp_fusion_invalid_json(self):
        """Test Yelp Fusion authentication with invalid JSON."""
        # Make request with invalid JSON
        response = self.client.post(
            f"{self.base_url}/yelp-fusion",
            json={"invalid_field": "value"}
        )
        
        # Should work as run_id is optional in the schema
        # The response will depend on the actual API call result
        assert response.status_code in [200, 400]  # 200 if API call succeeds, 400 if it fails
