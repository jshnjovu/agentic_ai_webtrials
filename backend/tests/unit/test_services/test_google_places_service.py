"""
Unit tests for Google Places business search service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from src.services import GooglePlacesService
from src.schemas import (
    BusinessSearchRequest, BusinessData, BusinessSearchResponse, 
    BusinessSearchError, LocationType
)


class TestGooglePlacesService:
    """Test cases for GooglePlacesService."""
    
    @pytest.fixture
    def service(self):
        """Create a GooglePlacesService instance for testing."""
        with patch('src.services.google_places_service.get_api_config') as mock_config:
            mock_config.return_value = Mock(
                GOOGLE_PLACES_API_KEY="test_api_key",
                API_TIMEOUT_SECONDS=30
            )
            return GooglePlacesService()
    
    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock rate limiter that allows all requests."""
        mock_limiter = Mock()
        mock_limiter.can_make_request.return_value = (True, None)
        mock_limiter.record_request.return_value = None
        return mock_limiter
    
    @pytest.fixture
    def sample_business_data(self):
        """Sample business data for testing."""
        return {
            "place_id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
            "name": "Test Restaurant",
            "formatted_address": "123 Test St, Test City, TS 12345",
            "formatted_phone_number": "+1-555-123-4567",
            "website": "https://testrestaurant.com",
            "rating": 4.5,
            "user_ratings_total": 150,
            "price_level": 2,
            "types": ["restaurant", "food", "establishment"],
            "geometry": {
                "location": {"lat": 37.7749, "lng": -122.4194}
            },
            "international_phone_number": "+1-555-123-4567",
            "opening_hours": {"open_now": True},
            "photos": [{"photo_reference": "test_ref"}],
            "reviews": [{"rating": 5, "text": "Great food!"}]
        }
    
    @pytest.fixture
    def sample_search_request(self):
        """Sample business search request for testing."""
        return BusinessSearchRequest(
            query="restaurant",
            location="San Francisco",
            location_type=LocationType.CITY,
            category="restaurant",
            radius=5000,
            max_results=10,
            run_id="test_run_123"
        )
    
    def test_validate_input_valid(self, service, sample_search_request):
        """Test input validation with valid request."""
        assert service.validate_input(sample_search_request) is True
    
    def test_validate_input_invalid(self, service):
        """Test input validation with invalid request."""
        assert service.validate_input("invalid_input") is False
        assert service.validate_input(None) is False
        assert service.validate_input({}) is False
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_search_businesses_success(self, mock_client, service, sample_search_request, sample_business_data):
        """Test successful business search."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        service.rate_limiter.record_request.return_value = None
        
        # Mock HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [sample_business_data],
            "next_page_token": "next_page_token_123"
        }
        
        # Mock the context manager properly
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client.return_value.__exit__.return_value = None
        
        # Execute search
        result = service.search_businesses(sample_search_request)
        
        # Verify result
        assert isinstance(result, BusinessSearchResponse)
        assert result.success is True
        assert result.query == "restaurant"
        assert result.location == "San Francisco"
        assert result.total_results == 1
        assert len(result.results) == 1
        assert result.next_page_token == "next_page_token_123"
        
        # Verify business data
        business = result.results[0]
        assert business.place_id == "ChIJN1t_tDeuEmsRUsoyG83frY4"
        assert business.name == "Test Restaurant"
        assert business.address == "123 Test St, Test City, TS 12345"
        assert business.phone == "+1-555-123-4567"
        assert business.website == "https://testrestaurant.com"
        assert business.rating == 4.5
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_search_businesses_rate_limit_exceeded(self, mock_client, service, sample_search_request):
        """Test business search when rate limit is exceeded."""
        # Mock rate limiter to deny request
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (False, "Rate limit exceeded")
        
        # Execute search
        result = service.search_businesses(sample_search_request)
        
        # Verify error result
        assert isinstance(result, BusinessSearchError)
        assert result.success is False
        assert "Rate limit exceeded" in result.error
        assert result.context == "rate_limit_check"
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_search_businesses_invalid_location(self, mock_client, service, sample_search_request):
        """Test business search with invalid location."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        
        # Set invalid location
        sample_search_request.location = ""
        sample_search_request.location_type = LocationType.CITY
        
        # Execute search
        result = service.search_businesses(sample_search_request)
        
        # Verify error result
        assert isinstance(result, BusinessSearchError)
        assert result.success is False
        assert "Invalid location" in result.error
        assert result.context == "location_validation"
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_search_businesses_api_error(self, mock_client, service, sample_search_request):
        """Test business search when API returns error."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        service.rate_limiter.record_request.return_value = None
        
        # Mock HTTP client response with API error
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "INVALID_REQUEST",
            "error_message": "Invalid API key"
        }
        
        # Mock the context manager properly
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client.return_value.__exit__.return_value = None
        
        # Execute search
        result = service.search_businesses(sample_search_request)
        
        # Verify error result
        assert isinstance(result, BusinessSearchError)
        assert result.success is False
        assert "INVALID_REQUEST" in result.error
        assert result.error_code == "INVALID_REQUEST"
        assert result.context == "api_search_execution"
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_search_businesses_http_error(self, mock_client, service, sample_search_request):
        """Test business search when HTTP request fails."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        service.rate_limiter.record_request.return_value = None
        
        # Mock HTTP client response with HTTP error
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        # Mock the context manager properly
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client.return_value.__exit__.return_value = None
        
        # Execute search
        result = service.search_businesses(sample_search_request)
        
        # Verify error result
        assert isinstance(result, BusinessSearchError)
        assert result.success is False
        assert "HTTP 500" in result.error
        assert result.error_code == "HTTP_500"
        assert result.context == "api_search_execution"
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_search_businesses_timeout(self, mock_client, service, sample_search_request):
        """Test business search when request times out."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        
        # Mock HTTP client to raise timeout exception
        mock_client_instance = Mock()
        mock_client_instance.get.side_effect = Exception("timeout")
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client.return_value.__exit__.return_value = None
        
        # Execute search
        result = service.search_businesses(sample_search_request)
        
        # Verify error result
        assert isinstance(result, BusinessSearchError)
        assert result.success is False
        assert "Unexpected error" in result.error
        assert result.context == "api_search_execution"
    
    def test_process_location_coordinates_valid(self, service):
        """Test location processing with valid coordinates."""
        result = service._process_location("37.7749,-122.4194", LocationType.COORDINATES)
        assert result["valid"] is True
        assert result["type"] == "coordinates"
        assert result["coordinates"] == "37.7749,-122.4194"
    
    def test_process_location_coordinates_invalid(self, service):
        """Test location processing with invalid coordinates."""
        result = service._process_location("invalid_coords", LocationType.COORDINATES)
        assert result["valid"] is False
        assert "Invalid coordinate format" in result["error"]
    
    def test_process_location_zip_code_valid(self, service):
        """Test location processing with valid ZIP code."""
        result = service._process_location("12345", LocationType.ZIP_CODE)
        assert result["valid"] is True
        assert result["type"] == "zip_code"
        assert result["zip_code"] == "12345"
        
        result = service._process_location("12345-6789", LocationType.ZIP_CODE)
        assert result["valid"] is True
        assert result["zip_code"] == "12345-6789"
    
    def test_process_location_zip_code_invalid(self, service):
        """Test location processing with invalid ZIP code."""
        result = service._process_location("123", LocationType.ZIP_CODE)
        assert result["valid"] is False
        assert "Invalid ZIP code format" in result["error"]
    
    def test_process_location_city_valid(self, service):
        """Test location processing with valid city."""
        result = service._process_location("San Francisco", LocationType.CITY)
        assert result["valid"] is True
        assert result["type"] == "city"
        assert result["text"] == "San Francisco"
    
    def test_process_location_city_invalid(self, service):
        """Test location processing with invalid city."""
        result = service._process_location("A", LocationType.CITY)
        assert result["valid"] is False
        assert "at least 2 characters" in result["error"]
    
    def test_build_search_params_coordinates(self, service, sample_search_request):
        """Test building search parameters for coordinate-based search."""
        location_info = {"valid": True, "coordinates": "37.7749,-122.4194", "type": "coordinates"}
        params = service._build_search_params(sample_search_request, location_info)
        
        assert params["query"] == "restaurant"
        assert params["location"] == "37.7749,-122.4194"
        assert params["radius"] == 5000
        assert params["type"] == "restaurant"
        assert params["maxresults"] == 10
    
    def test_build_search_params_city(self, service, sample_search_request):
        """Test building search parameters for city-based search."""
        location_info = {"valid": True, "text": "San Francisco", "type": "city"}
        params = service._build_search_params(sample_search_request, location_info)
        
        assert params["query"] == "restaurant in San Francisco"
        assert "location" not in params
        assert "radius" not in params
        assert params["type"] == "restaurant"
    
    def test_build_search_params_zip_code(self, service, sample_search_request):
        """Test building search parameters for ZIP code-based search."""
        location_info = {"valid": True, "zip_code": "12345", "type": "zip_code"}
        params = service._build_search_params(sample_search_request, location_info)
        
        assert params["query"] == "restaurant in 12345"
        assert "location" not in params
        assert "radius" not in params
        assert params["type"] == "restaurant"
    
    def test_process_business_results_success(self, service, sample_business_data):
        """Test processing business results successfully."""
        raw_results = [sample_business_data]
        businesses = service._process_business_results(raw_results, 10, "test_run_123")
        
        assert len(businesses) == 1
        business = businesses[0]
        assert business.place_id == "ChIJN1t_tDeuEmsRUsoyG83frY4"
        assert business.name == "Test Restaurant"
        assert business.rating == 4.5
    
    def test_process_business_results_limit(self, service, sample_business_data):
        """Test processing business results with limit."""
        raw_results = [sample_business_data] * 25  # More than max_results
        businesses = service._process_business_results(raw_results, 10, "test_run_123")
        
        assert len(businesses) == 10  # Limited to max_results
    
    def test_process_business_results_empty(self, service):
        """Test processing empty business results."""
        businesses = service._process_business_results([], 10, "test_run_123")
        assert len(businesses) == 0
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_get_next_page_success(self, mock_client, service):
        """Test successful next page retrieval."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        service.rate_limiter.record_request.return_value = None
        
        # Mock HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "OK",
            "results": [{"place_id": "next_page_123", "name": "Next Page Business"}],
            "next_page_token": "next_next_page_token"
        }
        
        # Mock the context manager properly
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        mock_client.return_value.__exit__.return_value = None
        
        # Execute next page request
        result = service.get_next_page("test_token", "test_run_123")
        
        # Verify result
        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["next_page_token"] == "next_next_page_token"
        assert result["api_status"] == "OK"
    
    @patch('src.services.google_places_service.httpx.Client')
    def test_get_next_page_rate_limit_exceeded(self, mock_client, service):
        """Test next page retrieval when rate limit is exceeded."""
        # Mock rate limiter to deny request
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (False, "Rate limit exceeded")
        
        # Execute next page request
        result = service.get_next_page("test_token", "test_run_123")
        
        # Verify error result
        assert result["success"] is False
        assert "Rate limit exceeded" in result["error"]
        assert result["error_code"] == "RATE_LIMIT_EXCEEDED"
