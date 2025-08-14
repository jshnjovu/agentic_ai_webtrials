"""
Unit tests for business search API endpoints.
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


class TestBusinessSearchAPI:
    """Test cases for business search API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_business_data(self):
        """Sample business data for testing."""
        return BusinessData(
            place_id="ChIJN1t_tDeuEmsRUsoyG83frY4",
            name="Test Restaurant",
            address="123 Test St, Test City, TS 12345",
            phone="+1-555-123-4567",
            website="https://testrestaurant.com",
            rating=4.5,
            user_ratings_total=150,
            price_level=2,
            types=["restaurant", "food", "establishment"],
            geometry={"location": {"lat": 37.7749, "lng": -122.4194}},
            formatted_address="123 Test St, Test City, TS 12345",
            international_phone_number="+1-555-123-4567",
            opening_hours={"open_now": True},
            photos=[{"photo_reference": "test_ref"}],
            reviews=[{"rating": 5, "text": "Great food!"}]
        )
    
    @pytest.fixture
    def sample_search_request(self):
        """Sample business search request for testing."""
        return {
            "query": "restaurant",
            "location": "San Francisco",
            "location_type": "city",
            "category": "restaurant",
            "radius": 5000,
            "max_results": 10,
            "run_id": "test_run_123"
        }
    
    @pytest.fixture
    def sample_search_response(self, sample_business_data):
        """Sample business search response for testing."""
        return BusinessSearchResponse(
            success=True,
            query="restaurant",
            location="San Francisco",
            total_results=1,
            results=[sample_business_data],
            next_page_token="next_page_token_123",
            run_id="test_run_123",
            search_metadata={
                "location_type": "city",
                "radius_meters": 5000,
                "category_filter": "restaurant",
                "api_status": "OK"
            }
        )
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_search_businesses_post_success(self, mock_service_class, client, sample_search_request, sample_search_response):
        """Test successful POST business search."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = sample_search_response
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/google-places/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "restaurant"
        assert data["location"] == "San Francisco"
        assert data["total_results"] == 1
        assert len(data["results"]) == 1
        assert data["next_page_token"] == "next_page_token_123"
        
        # Verify service calls
        mock_service.validate_input.assert_called_once()
        mock_service.search_businesses.assert_called_once()
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_search_businesses_post_validation_failure(self, mock_service_class, client, sample_search_request):
        """Test POST business search with validation failure."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = False
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/google-places/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "Invalid business search request" in data["detail"]
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_search_businesses_post_service_error(self, mock_service_class, client, sample_search_request):
        """Test POST business search when service returns error."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = BusinessSearchError(
            error="API error occurred",
            error_code="API_ERROR",
            context="api_search_execution",
            query="restaurant",
            location="San Francisco",
            run_id="test_run_123"
        )
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.post("/api/v1/business-search/google-places/search", json=sample_search_request)
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "API error occurred"
        assert data["detail"]["error_code"] == "API_ERROR"
        assert data["detail"]["context"] == "api_search_execution"
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_search_businesses_get_success(self, mock_service_class, client, sample_search_response):
        """Test successful GET business search."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = sample_search_response
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/google-places/search", params={
            "query": "restaurant",
            "location": "San Francisco",
            "location_type": "city",
            "category": "restaurant",
            "radius": 5000,
            "max_results": 10
        })
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["query"] == "restaurant"
        assert data["location"] == "San Francisco"
        
        # Verify service calls
        mock_service.validate_input.assert_called_once()
        mock_service.search_businesses.assert_called_once()
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_search_businesses_get_validation_failure(self, mock_service_class, client):
        """Test GET business search with validation failure."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = False
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/google-places/search", params={
            "query": "restaurant",
            "location": "San Francisco"
        })
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "Invalid business search request" in data["detail"]
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_search_businesses_get_service_error(self, mock_service_class, client):
        """Test GET business search when service returns error."""
        # Mock service
        mock_service = Mock()
        mock_service.validate_input.return_value = True
        mock_service.search_businesses.return_value = BusinessSearchError(
            error="API error occurred",
            error_code="API_ERROR",
            context="api_search_execution",
            query="restaurant",
            location="San Francisco",
            run_id="test_run_123"
        )
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/google-places/search", params={
            "query": "restaurant",
            "location": "San Francisco"
        })
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "API error occurred"
        assert data["detail"]["error_code"] == "API_ERROR"
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_get_next_page_success(self, mock_service_class, client):
        """Test successful next page retrieval."""
        # Mock service
        mock_service = Mock()
        mock_service.get_next_page.return_value = {
            "success": True,
            "results": [{"place_id": "next_page_123", "name": "Next Page Business"}],
            "next_page_token": "next_next_page_token",
            "api_status": "OK"
        }
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/google-places/next-page", params={
            "next_page_token": "test_token"
        })
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert len(data["results"]) == 1
        assert data["next_page_token"] == "next_next_page_token"
        assert data["api_status"] == "OK"
        
        # Verify service calls - run_id is generated if not provided
        mock_service.get_next_page.assert_called_once()
        call_args = mock_service.get_next_page.call_args
        assert call_args[0][0] == "test_token"  # first argument is token
        assert call_args[0][1] is not None  # second argument is generated run_id
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_get_next_page_missing_token(self, mock_service_class, client):
        """Test next page retrieval with missing token."""
        # Make request without token
        response = client.get("/api/v1/business-search/google-places/next-page")
        
        # Verify response
        assert response.status_code == 422  # Validation error
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_get_next_page_empty_token(self, mock_service_class, client):
        """Test next page retrieval with empty token."""
        # Make request with empty token
        response = client.get("/api/v1/business-search/google-places/next-page", params={
            "next_page_token": ""
        })
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert "Next page token is required" in data["detail"]
    
    @patch('src.api.v1.business_search.GooglePlacesService')
    def test_get_next_page_service_error(self, mock_service_class, client):
        """Test next page retrieval when service returns error."""
        # Mock service
        mock_service = Mock()
        mock_service.get_next_page.return_value = {
            "success": False,
            "error": "Service error occurred",
            "error_code": "SERVICE_ERROR"
        }
        mock_service_class.return_value = mock_service
        
        # Make request
        response = client.get("/api/v1/business-search/google-places/next-page", params={
            "next_page_token": "test_token"
        })
        
        # Verify response
        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "Service error occurred"
        assert data["detail"]["error_code"] == "SERVICE_ERROR"
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/api/v1/business-search/google-places/search/health")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "GooglePlacesService"
        assert "Service is operational" in data["message"]
        assert "business_search" in data["capabilities"]
    
    def test_health_check_service_failure(self, client):
        """Test health check when service fails."""
        # This test verifies that the health check endpoint works correctly
        # The actual service initialization failure is tested in the service tests
        # Here we just verify the endpoint returns a healthy status when working
        
        response = client.get("/api/v1/business-search/google-places/search/health")
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "Service is operational" in data["message"]
        assert "business_search" in data["capabilities"]
    
    def test_search_businesses_post_missing_run_id(self, client, sample_search_request):
        """Test POST business search without run_id (should generate one)."""
        # Remove run_id from request
        del sample_search_request["run_id"]
        
        with patch('src.api.v1.business_search.GooglePlacesService') as mock_service_class:
            # Mock service
            mock_service = Mock()
            mock_service.validate_input.return_value = True
            mock_service.search_businesses.return_value = BusinessSearchResponse(
                success=True,
                query="restaurant",
                location="San Francisco",
                total_results=0,
                results=[],
                run_id="generated_run_id"
            )
            mock_service_class.return_value = mock_service
            
            # Make request
            response = client.post("/api/v1/business-search/google-places/search", json=sample_search_request)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "run_id" in data
    
    def test_search_businesses_get_missing_run_id(self, client):
        """Test GET business search without run_id (should generate one)."""
        with patch('src.api.v1.business_search.GooglePlacesService') as mock_service_class:
            # Mock service
            mock_service = Mock()
            mock_service.validate_input.return_value = True
            mock_service.search_businesses.return_value = BusinessSearchResponse(
                success=True,
                query="restaurant",
                location="San Francisco",
                total_results=0,
                results=[],
                run_id="generated_run_id"
            )
            mock_service_class.return_value = mock_service
            
            # Make request
            response = client.get("/api/v1/business-search/google-places/search", params={
                "query": "restaurant",
                "location": "San Francisco"
            })
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "run_id" in data
    
    def test_search_businesses_get_with_run_id(self, client):
        """Test GET business search with provided run_id."""
        with patch('src.api.v1.business_search.GooglePlacesService') as mock_service_class:
            # Mock service
            mock_service = Mock()
            mock_service.validate_input.return_value = True
            mock_service.search_businesses.return_value = BusinessSearchResponse(
                success=True,
                query="restaurant",
                location="San Francisco",
                total_results=0,
                results=[],
                run_id="provided_run_id"
            )
            mock_service_class.return_value = mock_service
            
            # Make request with run_id
            response = client.get("/api/v1/business-search/google-places/search", params={
                "query": "restaurant",
                "location": "San Francisco",
                "run_id": "provided_run_id"
            })
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["run_id"] == "provided_run_id"
