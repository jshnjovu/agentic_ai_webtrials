"""
Unit tests for SERPAPI service.
"""

import pytest
from unittest.mock import Mock, patch
from src.services.serpapi_service import SerpAPIService
from src.schemas.business_search import (
    BusinessSearchRequest, BusinessSearchResponse, BusinessSearchError,
    LocationType, BusinessData
)


class TestSerpAPIService:
    """Test cases for SERPAPI service."""
    
    @pytest.fixture
    def serpapi_service(self):
        """Create a SERPAPI service instance for testing."""
        with patch('src.services.serpapi_service.get_api_config') as mock_config:
            mock_config.return_value.SERPAPI_API_KEY = "test_api_key"
            return SerpAPIService()
    
    @pytest.fixture
    def sample_search_request(self):
        """Sample business search request for testing."""
        return BusinessSearchRequest(
            query="gyms",
            location="London",
            max_results=10,
            run_id="test_run_123"
        )
    
    @pytest.fixture
    def sample_serpapi_response(self):
        """Sample SERPAPI API response for testing."""
        return {
            "local_results": [
                {
                    "title": "Test Gym London",
                    "address": "123 Fitness St, London, UK",
                    "phone": "+44 20 1234 5678",
                    "rating": 4.8,
                    "reviews": 1400,
                    "type": "gym",
                    "gps_coordinates": {"latitude": 51.5074, "longitude": -0.1278},
                    "links": {"website": "https://testgym.com"}
                }
            ]
        }

    def test_service_initialization(self, serpapi_service):
        """Test that SERPAPI service initializes correctly."""
        assert serpapi_service.name == "SerpAPIService"
        assert serpapi_service.base_url == "https://serpapi.com/search.json"
        assert serpapi_service.api_key == "test_api_key"
        assert serpapi_service.max_results_per_request == 20

    def test_validate_input(self, serpapi_service, sample_search_request):
        """Test input validation."""
        assert serpapi_service.validate_input(sample_search_request) is True
        assert serpapi_service.validate_input("invalid") is False
        assert serpapi_service.validate_input(None) is False

    @patch('src.services.serpapi_service.RateLimiter')
    @pytest.mark.asyncio
    async def test_search_businesses_success(self, mock_rate_limiter_class, serpapi_service, sample_search_request, sample_serpapi_response):
        """Test successful business search."""
        # Mock rate limiter
        mock_rate_limiter = Mock()
        mock_rate_limiter.can_make_request.return_value = (True, "OK")
        mock_rate_limiter_class.return_value = mock_rate_limiter
        
        # Mock GeoapifyService
        with patch.object(serpapi_service.geoapify_service, 'extract_country_code') as mock_geoapify:
            mock_geoapify.return_value = "us"
            
            # Mock HTTP request
            with patch('httpx.Client') as mock_client_class:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = sample_serpapi_response
                mock_client.get.return_value = mock_response
                mock_client_class.return_value.__enter__.return_value = mock_client
                
                result = await serpapi_service.search_businesses(sample_search_request)
                
                assert isinstance(result, BusinessSearchResponse)
                assert result.success is True
                assert result.query == "gyms"
                assert result.total_results == 1
                assert result.search_metadata["api_used"] == "serpapi"

    @patch('src.services.serpapi_service.RateLimiter')
    @pytest.mark.asyncio
    async def test_search_businesses_rate_limit_exceeded(self, mock_rate_limiter_class, serpapi_service, sample_search_request):
        """Test business search when rate limit is exceeded."""
        # Create a new service instance with the mocked rate limiter
        with patch('src.services.serpapi_service.RateLimiter') as mock_rate_limiter_class:
            mock_rate_limiter = Mock()
            mock_rate_limiter.can_make_request.return_value = (False, "Rate limit exceeded")
            mock_rate_limiter_class.return_value = mock_rate_limiter
            
            # Create a new service instance to use the mocked rate limiter
            service = SerpAPIService()
            service.rate_limiter = mock_rate_limiter
            
            result = await service.search_businesses(sample_search_request)
            
            assert isinstance(result, BusinessSearchError)
            assert result.success is False
            assert "Rate limit exceeded" in result.error
            assert result.context == "rate_limit_check"

    @pytest.mark.asyncio
    async def test_build_search_params(self, serpapi_service, sample_search_request):
        """Test building search parameters - exactly matching SERPAPI.md pattern."""
        # Mock GeoapifyService
        with patch.object(serpapi_service.geoapify_service, 'extract_country_code') as mock_geoapify:
            mock_geoapify.return_value = "us"
            
            params = await serpapi_service._build_search_params(sample_search_request)
            
            # Query should be combined like SERPAPI.md: "Gym London UK" format
            assert params["q"] == "gyms London"
            assert params["engine"] == "google_local"
            assert params["google_domain"] == "google.com"
            assert "num" not in params  # No num parameter in SERPAPI.md
            assert "location" not in params  # No separate location parameter

    def test_execute_search_success(self, serpapi_service, sample_serpapi_response):
        """Test successful search execution."""
        search_params = {"q": "gyms", "api_key": "test_key"}
        
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_serpapi_response
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__enter__.return_value = mock_client
            
            result = serpapi_service._execute_search(search_params, "test_run")
            
            assert result["success"] is True
            assert result["results"] == sample_serpapi_response["local_results"]

    def test_execute_search_serpapi_error(self, serpapi_service):
        """Test search execution when SERPAPI returns error."""
        search_params = {"q": "test", "api_key": "test_key"}
        
        with patch('httpx.Client') as mock_client_class:
            mock_client = Mock()
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"error": "Invalid API key"}
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__enter__.return_value = mock_client
            
            result = serpapi_service._execute_search(search_params, "test_run")
            
            assert result["success"] is False
            assert "SerpAPI error: Invalid API key" in result["error"]
            assert result["error_code"] == "SERPAPI_ERROR"

    def test_process_business_results(self, serpapi_service, sample_serpapi_response):
        """Test processing of business results."""
        raw_results = sample_serpapi_response["local_results"]
        
        processed_results = serpapi_service._process_business_results(raw_results, 5, "test_run")
        
        assert len(processed_results) == 1
        assert all(isinstance(business, BusinessData) for business in processed_results)
        
        business = processed_results[0]
        assert business.place_id == "serpapi_0"
        assert business.name == "Test Gym London"
        assert business.website == "https://testgym.com"
        assert business.rating == 4.8
        assert business.confidence_level == "high"

    def test_process_business_results_max_limit(self, serpapi_service):
        """Test that processing respects max_results limit."""
        raw_results = [
            {"title": f"Business {i}", "address": f"Address {i}"}
            for i in range(10)
        ]
        
        processed_results = serpapi_service._process_business_results(raw_results, 3, "test_run")
        
        assert len(processed_results) == 3
        assert processed_results[0].name == "Business 0"
        assert processed_results[1].name == "Business 1"
        assert processed_results[2].name == "Business 2"
