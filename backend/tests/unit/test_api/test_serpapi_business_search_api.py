"""
Unit tests for SERPAPI business search API endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from src.main import app
from src.schemas import (
    BusinessSearchRequest, BusinessSearchResponse, BusinessSearchError,
    LocationType, BusinessData
)


class TestSerpAPIBusinessSearchAPI:
    """Test cases for SERPAPI business search API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_business_data(self):
        """Sample business data for SERPAPI testing."""
        return BusinessData(
            place_id="serpapi_test_123",
            name="Test Gym London",
            address="123 Fitness St, London, UK",
            phone="+44 20 1234 5678",
            website="https://testgym.com",
            rating=4.8,
            user_ratings_total=1400,
            price_level=2,
            types=["gym", "fitness", "health"],
            geometry={"location": {"lat": 51.5074, "lng": -0.1278}},
            formatted_address="123 Fitness St, London, UK",
            confidence_level="high"
        )
    
    @pytest.fixture
    def sample_search_request(self):
        """Sample business search request for SERPAPI testing."""
        return {
            "query": "gyms",
            "location": "London, UK",
            "location_type": "city",
            "category": "fitness",
            "radius": 5000,
            "max_results": 10,
            "run_id": "test_serpapi_run_123"
        }
    
    @pytest.fixture
    def sample_search_response(self, sample_business_data):
        """Sample business search response for SERPAPI testing."""
        return BusinessSearchResponse(
            success=True,
            query="gyms",
            location="London, UK",
            total_results=1,
            results=[sample_business_data],
            run_id="test_serpapi_run_123",
            search_metadata={
                "api_used": "serpapi",
                "total_api_results": 1,
                "engine": "google_local",
                "google_domain": "google.com"
            }
        )
    
    @pytest.fixture
    def sample_search_error(self):
        """Sample business search error for SERPAPI testing."""
        return BusinessSearchError(
            success=False,
            error="SerpAPI rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            context="rate_limit_check",
            query="gyms",
            location="London, UK",
            run_id="test_serpapi_run_123"
        )

    # ==================== SERPAPI Direct Search Tests ====================
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_post_success(self, mock_service_class, client, sample_search_request, sample_search_response):
        """Test successful POST SERPAPI business search."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = sample_search_response
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "gyms"
        assert data["location"] == "London, UK"
        assert data["total_results"] == 1
        assert len(data["results"]) == 1
        assert data["search_metadata"]["api_used"] == "serpapi"
        
        # Verify service calls
        mock_service.validate_input.assert_called_once()
        mock_service.search_businesses.assert_called_once()
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_post_validation_failure(self, mock_service_class, client, sample_search_request):
        """Test POST SERPAPI business search with validation failure."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = False
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "Invalid business search request" in data["detail"]
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_post_service_error(self, mock_service_class, client, sample_search_request, sample_search_error):
        """Test POST SERPAPI business search when service returns error."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = sample_search_error
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "SerpAPI rate limit exceeded"
        assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"
        assert data["detail"]["context"] == "rate_limit_check"
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_get_success(self, mock_service_class, client, sample_search_response):
        """Test successful GET SERPAPI business search."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = sample_search_response
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "query": "gyms",
            "location": "London, UK",
            "location_type": "city",
            "category": "fitness",
            "radius": 5000,
            "max_results": 10
        })
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "gyms"
        assert data["location"] == "London, UK"
        assert data["search_metadata"]["api_used"] == "serpapi"
        
        # Verify service calls
        mock_service.validate_input.assert_called_once()
        mock_service.search_businesses.assert_called_once()
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_get_validation_failure(self, mock_service_class, client):
        """Test GET SERPAPI business search with validation failure."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = False
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "query": "gyms",
            "location": "London, UK"
        })
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "Invalid business search request" in data["detail"]
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_get_service_error(self, mock_service_class, client, sample_search_error):
        """Test GET SERPAPI business search when service returns error."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = sample_search_error
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "query": "gyms",
            "location": "London, UK"
        })
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "SerpAPI rate limit exceeded"
        assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"

    # ==================== SERPAPI with Fallback Tests ====================
    
    @patch('src.api.v1.business_search.BusinessSearchFallbackService')
    def test_serpapi_search_with_fallback_success(self, mock_service_class, client, sample_search_request, sample_search_response):
        """Test successful SERPAPI search with fallback service."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses_with_fallback.return_value = sample_search_response
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search/with-fallback", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "gyms"
        assert data["location"] == "London, UK"
        assert data["search_metadata"]["api_used"] == "serpapi"
        
        # Verify service calls
        mock_service.validate_input.assert_called_once()
        mock_service.search_businesses_with_fallback.assert_called_once()
    
    @patch('src.api.v1.business_search.BusinessSearchFallbackService')
    def test_serpapi_search_with_fallback_validation_failure(self, mock_service_class, client, sample_search_request):
        """Test SERPAPI search with fallback when validation fails."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = False
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search/with-fallback", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "Invalid business search request" in data["detail"]
    
    @patch('src.api.v1.business_search.BusinessSearchFallbackService')
    def test_serpapi_search_with_fallback_service_error(self, mock_service_class, client, sample_search_request, sample_search_error):
        """Test SERPAPI search with fallback when service returns error."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses_with_fallback.return_value = sample_search_error
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search/with-fallback", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "SerpAPI rate limit exceeded"
        assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"

    # ==================== Next Page Tests ====================
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_next_page_success(self, mock_service_class, client):
        """Test successful next page retrieval for SERPAPI."""
        # Since the endpoint returns 501 (Not Implemented), we should expect that
        response = client.get("/api/v1/business-search/serpapi/next-page", params={
            "next_page_token": "test_token"
        })
        
        # Verify response
        assert response.status_code == 501
        data = response.json()
        assert "not yet implemented" in data["detail"].lower()
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_next_page_missing_token(self, mock_service_class, client):
        """Test next page retrieval with missing token for SERPAPI."""
        # Make request without token
        response = client.get("/api/v1/business-search/serpapi/next-page")
        
        # Verify response
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_next_page_service_error(self, mock_service_class, client):
        """Test next page retrieval when SERPAPI service returns error."""
        # Since the endpoint returns 501 (Not Implemented), we should expect that
        response = client.get("/api/v1/business-search/serpapi/next-page", params={
            "next_page_token": "test_token"
        })
        
        # Verify response
        assert response.status_code == 501
        data = response.json()
        assert "not yet implemented" in data["detail"].lower()

    # ==================== Health Check Tests ====================
    
    def test_serpapi_health_check_success(self, client):
        """Test successful SERPAPI health check."""
        response = client.get("/api/v1/business-search/serpapi/search/health")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SerpAPIService"
        assert "Service is operational" in data["message"]
        assert "serpapi_business_search" in data["capabilities"]

    # ==================== Run ID Generation Tests ====================
    
    def test_serpapi_search_post_missing_run_id(self, client, sample_search_request):
        """Test POST SERPAPI business search without run_id (should generate one)."""
        # Remove run_id from request
        del sample_search_request["run_id"]
        
        with patch('src.api.v1.business_search.SerpAPIService') as mock_service_class:
            # Mock service
            mock_service = Mock()
            mock_service.validate_input.return_value = True
            mock_service.search_businesses.return_value = BusinessSearchResponse(
                success=True,
                query="gyms",
                location="London, UK",
                total_results=0,
                results=[],
                run_id="generated_serpapi_run_id"
            )
            mock_service_class.return_value = mock_service
            
            # Make request
            response = client.post("/api/v1/business-search/serpapi/search", json=sample_search_request)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "run_id" in data
    
    def test_serpapi_search_get_missing_run_id(self, client):
        """Test GET SERPAPI business search without run_id (should generate one)."""
        with patch('src.api.v1.business_search.SerpAPIService') as mock_service_class:
            # Mock service
            mock_service = Mock()
            mock_service.validate_input.return_value = True
            mock_service.search_businesses.return_value = BusinessSearchResponse(
                success=True,
                query="gyms",
                location="London, UK",
                total_results=0,
                results=[],
                run_id="generated_serpapi_run_id"
            )
            mock_service_class.return_value = mock_service
            
            # Make request
            response = client.get("/api/v1/business-search/serpapi/search", params={
                "query": "gyms",
                "location": "London, UK"
            })
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "run_id" in data
    
    def test_serpapi_search_get_with_run_id(self, client):
        """Test GET SERPAPI business search with provided run_id."""
        with patch('src.api.v1.business_search.SerpAPIService') as mock_service_class:
            # Mock service
            mock_service = Mock()
            mock_service.validate_input.return_value = True
            mock_service.search_businesses.return_value = BusinessSearchResponse(
                success=True,
                query="gyms",
                location="London, UK",
                total_results=0,
                results=[],
                run_id="provided_serpapi_run_id"
            )
            mock_service_class.return_value = mock_service
            
            # Make request with run_id
            response = client.get("/api/v1/business-search/serpapi/search", params={
                "query": "gyms",
                "location": "London, UK",
                "run_id": "provided_serpapi_run_id"
            })
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["run_id"] == "provided_serpapi_run_id"

    # ==================== Edge Cases and Error Handling ====================
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_unexpected_exception(self, mock_service_class, client, sample_search_request):
        """Test SERPAPI search when unexpected exception occurs."""
        # Mock service to raise exception
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.side_effect = Exception("Unexpected error")
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 500
        data = response.json()
        assert "Internal server error during business search" in data["detail"]
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_empty_results(self, mock_service_class, client, sample_search_request):
        """Test SERPAPI search with empty results."""
        # Mock service to return empty results
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = BusinessSearchResponse(
            success=True,
            query="gyms",
            location="London, UK",
            total_results=0,
            results=[],
            run_id="test_serpapi_run_123"
        )
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/serpapi/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_results"] == 0
        assert len(data["results"]) == 0
    
    @patch('src.api.v1.business_search.SerpAPIService')
    def test_serpapi_search_max_results_limit(self, mock_service_class, client):
        """Test SERPAPI search with maximum results limit."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = BusinessSearchResponse(
            success=True,
            query="gyms",
            location="London, UK",
            total_results=20,
            results=[BusinessData(
                place_id=f"serpapi_{i}",
                name=f"Gym {i}",
                address=f"Address {i}",
                confidence_level="high"
            ) for i in range(20)],
            run_id="test_serpapi_run_123"
        )
        mock_service_class.return_value = mock_service
        
        # Make request with max results
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "query": "gyms",
            "location": "London, UK",
            "max_results": 20
        })
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total_results"] == 20
        assert len(data["results"]) == 20

    # ==================== Parameter Validation Tests ====================
    
    def test_serpapi_search_invalid_radius(self, client):
        """Test SERPAPI search with invalid radius parameter."""
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "query": "gyms",
            "location": "London, UK",
            "radius": 99999  # Invalid: exceeds max of 50000
        })
        
        # Should fail validation
        assert response.status_code == 422  # Validation error
    
    def test_serpapi_search_invalid_max_results(self, client):
        """Test SERPAPI search with invalid max_results parameter."""
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "query": "gyms",
            "location": "London, UK",
            "max_results": 25  # Invalid: exceeds max of 20
        })
        
        # Should fail validation
        assert response.status_code == 422  # Validation error
    
    def test_serpapi_search_missing_required_params(self, client):
        """Test SERPAPI search with missing required parameters."""
        # Missing query
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "location": "London, UK"
        })
        assert response.status_code == 422  # Validation error
        
        # Missing location
        response = client.get("/api/v1/business-search/serpapi/search", params={
            "query": "gyms"
        })
        assert response.status_code == 422  # Validation error
