"""
Unit tests for Yelp Fusion business search service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from src.services import YelpFusionService
from src.schemas.yelp_fusion import (
    YelpBusinessSearchRequest, YelpBusinessData, YelpBusinessSearchResponse, 
    YelpBusinessSearchError, YelpLocationType, YelpBusinessHours, YelpBusinessCategory,
    YelpBusinessCoordinates, YelpBusinessLocation
)


class TestYelpFusionService:
    """Test cases for YelpFusionService."""
    
    @pytest.fixture
    def service(self):
        """Create a YelpFusionService instance for testing."""
        with patch('src.services.yelp_fusion_service.get_api_config') as mock_config:
            mock_config.return_value = Mock(
                YELP_FUSION_API_KEY="test_api_key",
                API_TIMEOUT_SECONDS=30
            )
            return YelpFusionService()
    
    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock rate limiter that allows all requests."""
        mock_limiter = Mock()
        mock_limiter.can_make_request.return_value = (True, None)
        mock_limiter.record_request.return_value = None
        mock_limiter.get_rate_limit_info.return_value = {"requests_today": 0, "limit": 5000}
        return mock_limiter
    
    @pytest.fixture
    def sample_yelp_business_data(self):
        """Sample Yelp business data for testing."""
        return {
            "id": "test_business_123",
            "alias": "test-restaurant",
            "name": "Test Restaurant",
            "image_url": "https://example.com/image.jpg",
            "is_closed": False,
            "url": "https://www.yelp.com/biz/test-restaurant",
            "review_count": 150,
            "categories": [
                {"alias": "restaurants", "title": "Restaurants"},
                {"alias": "food", "title": "Food"}
            ],
            "rating": 4.5,
            "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
            "transactions": ["delivery", "pickup"],
            "price": "$$",
            "location": {
                "address1": "123 Test St",
                "address2": "Suite 100",
                "city": "San Francisco",
                "state": "CA",
                "zip_code": "94102",
                "country": "US",
                "display_address": ["123 Test St", "San Francisco, CA 94102"],
                "cross_streets": "Test Ave & Test Blvd"
            },
            "phone": "+15551234567",
            "display_phone": "(555) 123-4567",
            "distance": 1500.5,
            "hours": [
                {"day": 0, "start": "0900", "end": "2200", "is_overnight": False},
                {"day": 1, "start": "0900", "end": "2200", "is_overnight": False}
            ],
            "photos": ["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"]
        }
    
    @pytest.fixture
    def sample_search_request(self):
        """Sample Yelp business search request for testing."""
        return YelpBusinessSearchRequest(
            term="restaurant",
            location="San Francisco",
            location_type=YelpLocationType.CITY,
            categories=["restaurants", "food"],
            radius=40000,
            limit=20,
            offset=0,
            sort_by="best_match",
            price="$$",
            open_now=True,
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
    
    def test_process_location_city(self, service):
        """Test location processing for city input."""
        result = service._process_location("San Francisco", YelpLocationType.CITY)
        assert result["valid"] is True
        assert result["processed_location"] == "San Francisco"
        assert result["type"] == "text"
    
    def test_process_location_coordinates_valid(self, service):
        """Test location processing for valid coordinates."""
        result = service._process_location("37.7749,-122.4194", YelpLocationType.COORDINATES)
        assert result["valid"] is True
        assert result["processed_location"] == "37.7749,-122.4194"
        assert result["type"] == "coordinates"
    
    def test_process_location_coordinates_invalid(self, service):
        """Test location processing for invalid coordinates."""
        result = service._process_location("invalid_coords", YelpLocationType.COORDINATES)
        assert result["valid"] is False
        assert "Invalid coordinate format" in result["error"]
    
    def test_process_location_zip_code_valid(self, service):
        """Test location processing for valid ZIP code."""
        result = service._process_location("94102", YelpLocationType.ZIP_CODE)
        assert result["valid"] is True
        assert result["processed_location"] == "94102"
        assert result["type"] == "zip_code"
    
    def test_process_location_zip_code_invalid(self, service):
        """Test location processing for invalid ZIP code."""
        result = service._process_location("invalid_zip", YelpLocationType.ZIP_CODE)
        assert result["valid"] is False
        assert "Invalid ZIP code format" in result["error"]
    
    def test_process_location_empty(self, service):
        """Test location processing for empty input."""
        result = service._process_location("", YelpLocationType.CITY)
        assert result["valid"] is False
        assert "Location cannot be empty" in result["error"]
    
    def test_build_search_params(self, service, sample_search_request):
        """Test building search parameters."""
        location_info = {"valid": True, "processed_location": "San Francisco", "type": "text"}
        params = service._build_search_params(sample_search_request, location_info)
        
        assert params["term"] == "restaurant"
        assert params["location"] == "San Francisco"
        assert params["limit"] == 20
        assert params["offset"] == 0
        assert params["radius"] == 40000
        assert params["categories"] == "restaurants,food"
        assert params["sort_by"] == "best_match"
        assert params["price"] == "$$"
        assert params["open_now"] is True
    
    def test_build_search_params_minimal(self, service):
        """Test building search parameters with minimal request."""
        request = YelpBusinessSearchRequest(
            term="restaurant",
            location="San Francisco"
        )
        location_info = {"valid": True, "processed_location": "San Francisco", "type": "text"}
        params = service._build_search_params(request, location_info)
        
        assert params["term"] == "restaurant"
        assert params["location"] == "San Francisco"
        assert params["limit"] == 20  # default
        assert params["offset"] == 0  # default
        assert params["radius"] == 40000  # radius has default value and is included
        assert "categories" not in params
    
    @patch('src.services.yelp_fusion_service.httpx.Client')
    def test_execute_search_success(self, mock_client, service, sample_search_request):
        """Test successful API search execution."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.record_request.return_value = None
        
        # Mock HTTP client response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "businesses": [{"id": "test1"}, {"id": "test2"}],
            "total": 2,
            "region": {"center": {"latitude": 37.7749, "longitude": -122.4194}}
        }
        
        # Mock the context manager properly
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        search_params = {"term": "restaurant", "location": "San Francisco"}
        result = service._execute_search(search_params, "test_run_123")
        
        assert result["success"] is True
        assert len(result["results"]) == 2
        assert result["total"] == 2
        assert "region" in result
    
    @patch('src.services.yelp_fusion_service.httpx.Client')
    def test_execute_search_unauthorized(self, mock_client, service):
        """Test API search execution with unauthorized error."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.record_request.return_value = None
        
        # Mock HTTP client response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        # Mock the context manager properly
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        search_params = {"term": "restaurant", "location": "San Francisco"}
        result = service._execute_search(search_params, "test_run_123")
        
        assert result["success"] is False
        assert result["error_code"] == "UNAUTHORIZED"
        assert "Authentication failed" in result["error"]
    
    @patch('src.services.yelp_fusion_service.httpx.Client')
    def test_execute_search_rate_limited(self, mock_client, service):
        """Test API search execution with rate limit error."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.record_request.return_value = None
        
        # Mock HTTP client response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate Limited"
        
        # Mock the context manager properly
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        search_params = {"term": "restaurant", "location": "San Francisco"}
        result = service._execute_search(search_params, "test_run_123")
        
        assert result["success"] is False
        assert result["error_code"] == "RATE_LIMITED"
        assert "Rate limit exceeded" in result["error"]
    
    @patch('src.services.yelp_fusion_service.httpx.Client')
    def test_execute_search_timeout(self, mock_client, service):
        """Test API search execution with timeout error."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.record_request.return_value = None
        
        # Mock timeout exception
        mock_client.return_value.__enter__.side_effect = Exception("timeout")
        
        search_params = {"term": "restaurant", "location": "San Francisco"}
        result = service._execute_search(search_params, "test_run_123")
        
        assert result["success"] is False
        assert "Unexpected error" in result["error"]
    
    def test_extract_business_hours(self, service):
        """Test extraction of business hours from raw data."""
        raw_hours = [
            {"day": 0, "start": "0900", "end": "2200", "is_overnight": False},
            {"day": 1, "start": "1000", "end": "2100", "is_overnight": False}
        ]
        
        hours = service._extract_business_hours(raw_hours)
        assert len(hours) == 2
        assert hours[0].day == 0
        assert hours[0].start == "0900"
        assert hours[0].end == "2200"
        assert hours[0].is_overnight is False
    
    def test_extract_business_hours_invalid(self, service):
        """Test extraction of business hours with invalid data."""
        raw_hours = [
            {"day": 0, "start": "0900", "end": "2200"},  # missing is_overnight - should pass
            {"day": "invalid", "start": "0900", "end": "2200"}  # invalid day - should fail
        ]
        
        hours = service._extract_business_hours(raw_hours)
        assert len(hours) == 1  # First one should pass, second should fail
        assert hours[0].day == 0
    
    def test_extract_categories(self, service):
        """Test extraction of business categories from raw data."""
        raw_categories = [
            {"alias": "restaurants", "title": "Restaurants"},
            {"alias": "food", "title": "Food"}
        ]
        
        categories = service._extract_categories(raw_categories)
        assert len(categories) == 2
        assert categories[0].alias == "restaurants"
        assert categories[0].title == "Restaurants"
    
    def test_extract_categories_invalid(self, service):
        """Test extraction of business categories with invalid data."""
        raw_categories = [
            {"alias": "restaurants"},  # missing title
            {"title": "Food"}  # missing alias
        ]
        
        categories = service._extract_categories(raw_categories)
        assert len(categories) == 0  # Should skip invalid entries
    
    def test_extract_coordinates(self, service):
        """Test extraction of business coordinates from raw data."""
        raw_coordinates = {"latitude": 37.7749, "longitude": -122.4194}
        
        coordinates = service._extract_coordinates(raw_coordinates)
        assert coordinates.latitude == 37.7749
        assert coordinates.longitude == -122.4194
    
    def test_extract_coordinates_default(self, service):
        """Test extraction of business coordinates with missing data."""
        raw_coordinates = {}
        
        coordinates = service._extract_coordinates(raw_coordinates)
        assert coordinates.latitude == 0.0
        assert coordinates.longitude == 0.0
    
    def test_extract_location(self, service):
        """Test extraction of business location from raw data."""
        raw_location = {
            "address1": "123 Test St",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94102",
            "country": "US",
            "display_address": ["123 Test St", "San Francisco, CA 94102"]
        }
        
        location = service._extract_location(raw_location)
        assert location.address1 == "123 Test St"
        assert location.city == "San Francisco"
        assert location.state == "CA"
        assert location.zip_code == "94102"
        assert location.country == "US"
        assert len(location.display_address) == 2
    
    def test_extract_location_minimal(self, service):
        """Test extraction of business location with minimal data."""
        raw_location = {}
        
        location = service._extract_location(raw_location)
        assert location.address1 == ""
        assert location.city == ""
        assert location.state == ""
        assert location.zip_code == ""
        assert location.country == ""
        assert len(location.display_address) == 0
    
    def test_extract_photos(self, service):
        """Test extraction of business photos from raw data."""
        raw_business = {
            "image_url": "https://example.com/main.jpg",
            "photos": ["https://example.com/photo1.jpg", "https://example.com/photo2.jpg"]
        }
        
        photos = service._extract_photos(raw_business)
        assert len(photos) == 3
        assert "https://example.com/main.jpg" in photos
        assert "https://example.com/photo1.jpg" in photos
        assert "https://example.com/photo2.jpg" in photos
    
    def test_extract_photos_main_only(self, service):
        """Test extraction of business photos with only main image."""
        raw_business = {
            "image_url": "https://example.com/main.jpg"
        }
        
        photos = service._extract_photos(raw_business)
        assert len(photos) == 1
        assert photos[0] == "https://example.com/main.jpg"
    
    def test_extract_photos_none(self, service):
        """Test extraction of business photos with no photos."""
        raw_business = {}
        
        photos = service._extract_photos(raw_business)
        assert len(photos) == 0
    
    def test_extract_attributes(self, service):
        """Test extraction of business attributes."""
        raw_attributes = {
            "Good for Kids": True,
            "Wheelchair Accessible": True,
            "Outdoor Seating": False,
            "Delivery": True,
            "Takeout": True,
            "Reservations": True,
            "COVID-19": {
                "delivery_or_takeout": "delivery_and_takeout",
                "dine_in": False
            }
        }
        
        attributes = service._extract_attributes(raw_attributes)
        assert attributes is not None
        assert attributes["Good for Kids"] is True
        assert attributes["Wheelchair Accessible"] is True
        assert attributes["Outdoor Seating"] is False
        assert "COVID-19" in attributes
        assert attributes["COVID-19"]["delivery_or_takeout"] == "delivery_and_takeout"
    
    def test_extract_attributes_empty(self, service):
        """Test extraction of business attributes with empty data."""
        raw_attributes = {}
        
        attributes = service._extract_attributes(raw_attributes)
        assert attributes is None
    
    def test_extract_attributes_filtered(self, service):
        """Test extraction of business attributes with filtering of None/empty values."""
        raw_attributes = {
            "Good for Kids": True,
            "Wheelchair Accessible": None,
            "Outdoor Seating": "",
            "Delivery": True,
            "Takeout": False
        }
        
        attributes = service._extract_attributes(raw_attributes)
        assert attributes is not None
        assert "Good for Kids" in attributes
        assert "Delivery" in attributes
        assert "Takeout" in attributes
        assert "Wheelchair Accessible" not in attributes
        assert "Outdoor Seating" not in attributes
    
    def test_extract_special_hours(self, service):
        """Test extraction of special hours."""
        raw_special_hours = [
            {
                "date": "2024-12-25",
                "start": "1000",
                "end": "1800",
                "is_closed": False,
                "is_overnight": False
            },
            {
                "date": "2024-12-26",
                "start": "0900",
                "end": "2000",
                "is_closed": False,
                "is_overnight": False
            }
        ]
        
        special_hours = service._extract_special_hours(raw_special_hours)
        assert special_hours is not None
        assert len(special_hours) == 2
        assert special_hours[0]["date"] == "2024-12-25"
        assert special_hours[0]["start"] == "1000"
        assert special_hours[1]["date"] == "2024-12-26"
    
    def test_extract_special_hours_invalid(self, service):
        """Test extraction of special hours with invalid data."""
        raw_special_hours = [
            {
                "date": "2024-12-25",
                "start": "1000"
                # missing end
            },
            {
                "date": "2024-12-26"
                # missing start and end
            }
        ]
        
        special_hours = service._extract_special_hours(raw_special_hours)
        assert special_hours is None  # Both entries are invalid
    
    def test_extract_business_status(self, service):
        """Test extraction of business status."""
        raw_business = {
            "is_closed": False,
            "attributes": {
                "temporary_closed": False,
                "COVID-19": {
                    "delivery_or_takeout": "delivery_and_takeout"
                }
            },
            "announcement": "Holiday hours apply"
        }
        
        status = service._extract_business_status(raw_business)
        assert status is not None
        assert "Announcement: Holiday hours apply" in status
    
    def test_extract_business_status_closed(self, service):
        """Test extraction of business status for closed business."""
        raw_business = {
            "is_closed": True,
            "attributes": {
                "temporary_closed": True
            }
        }
        
        status = service._extract_business_status(raw_business)
        assert status is not None
        assert "Permanently Closed" in status
        assert "Temporarily Closed" in status
    
    def test_extract_business_status_delivery_only(self, service):
        """Test extraction of business status for delivery-only business."""
        raw_business = {
            "is_closed": False,
            "attributes": {
                "COVID-19": {
                    "delivery_or_takeout": "delivery_only"
                }
            }
        }
        
        status = service._extract_business_status(raw_business)
        assert status is not None
        assert "Delivery Only" in status
    
    def test_extract_social_media(self, service):
        """Test extraction of social media links."""
        raw_business = {
            "facebook_url": "https://facebook.com/testbusiness",
            "instagram_url": "https://instagram.com/testbusiness",
            "attributes": {
                "Social Media": {
                    "LinkedIn": "https://linkedin.com/company/testbusiness"
                }
            }
        }
        
        social_media = service._extract_social_media(raw_business)
        assert social_media is not None
        assert social_media["facebook"] == "https://facebook.com/testbusiness"
        assert social_media["instagram"] == "https://instagram.com/testbusiness"
        assert social_media["linkedin"] == "https://linkedin.com/company/testbusiness"
    
    def test_extract_social_media_none(self, service):
        """Test extraction of social media links when none available."""
        raw_business = {}
        
        social_media = service._extract_social_media(raw_business)
        assert social_media is None
    
    @patch('src.services.yelp_fusion_service.YelpFusionService._execute_search')
    def test_search_businesses_success(self, mock_execute_search, service, sample_search_request):
        """Test successful business search."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        service.rate_limiter.get_rate_limit_info.return_value = {"requests_today": 0, "limit": 5000}
        
        # Mock search execution
        mock_execute_search.return_value = {
            "success": True,
            "results": [
                {"id": "test1", "name": "Test 1", "url": "https://www.yelp.com/biz/test1"},
                {"id": "test2", "name": "Test 2", "url": "https://www.yelp.com/biz/test2"}
            ],
            "total": 2,
            "region": {"center": {"latitude": 37.7749, "longitude": -122.4194}}
        }
        
        result = service.search_businesses(sample_search_request)
        
        assert isinstance(result, YelpBusinessSearchResponse)
        assert result.success is True
        assert result.total == 2
        assert len(result.businesses) == 2
        assert result.term == "restaurant"
        assert result.location == "San Francisco"
    
    @patch('src.services.yelp_fusion_service.YelpFusionService._execute_search')
    def test_search_businesses_rate_limit_exceeded(self, mock_execute_search, service, sample_search_request):
        """Test business search with rate limit exceeded."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (False, "Daily limit exceeded")
        
        result = service.search_businesses(sample_search_request)
        
        assert isinstance(result, YelpBusinessSearchError)
        assert result.success is False
        assert "Rate limit exceeded" in result.error
        assert result.context == "rate_limit_check"
    
    @patch('src.services.yelp_fusion_service.YelpFusionService._execute_search')
    def test_search_businesses_invalid_location(self, mock_execute_search, service, sample_search_request):
        """Test business search with invalid location."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        
        # Set invalid location type
        sample_search_request.location_type = YelpLocationType.COORDINATES
        sample_search_request.location = "invalid_coords"
        
        result = service.search_businesses(sample_search_request)
        
        assert isinstance(result, YelpBusinessSearchError)
        assert result.success is False
        assert "Invalid location" in result.error
        assert result.context == "location_validation"
    
    @patch('src.services.yelp_fusion_service.YelpFusionService._execute_search')
    def test_search_businesses_api_error(self, mock_execute_search, service, sample_search_request):
        """Test business search with API error."""
        # Mock rate limiter
        service.rate_limiter = Mock()
        service.rate_limiter.can_make_request.return_value = (True, None)
        
        # Mock search execution error
        mock_execute_search.return_value = {
            "success": False,
            "error": "API error occurred",
            "error_code": "API_ERROR"
        }
        
        result = service.search_businesses(sample_search_request)
        
        assert isinstance(result, YelpBusinessSearchError)
        assert result.success is False
        assert result.error == "API error occurred"
        assert result.error_code == "API_ERROR"
        assert result.context == "api_search_execution"
    
    def test_process_business_results(self, service):
        """Test processing of business results."""
        raw_businesses = [
            {
                "id": "test1",
                "name": "Test Business 1",
                "url": "https://www.yelp.com/biz/test1",
                "rating": 4.5,
                "review_count": 100,
                "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
                "location": {"city": "San Francisco", "state": "CA"},
                "categories": [{"alias": "restaurants", "title": "Restaurants"}],
                "hours": [{"day": 0, "start": "0900", "end": "2200", "is_overnight": False}],
                "image_url": "https://example.com/image1.jpg"
            },
            {
                "id": "test2",
                "name": "Test Business 2",
                "url": "https://www.yelp.com/biz/test2",
                "rating": 4.0,
                "review_count": 50,
                "coordinates": {"latitude": 37.7849, "longitude": -122.4094},
                "location": {"city": "San Francisco", "state": "CA"},
                "categories": [{"alias": "food", "title": "Food"}],
                "image_url": "https://example.com/image2.jpg"
            }
        ]
        
        businesses = service._process_business_results(raw_businesses, 10, "test_run_123")
        
        assert len(businesses) == 2
        assert businesses[0].id == "test1"
        assert businesses[0].name == "Test Business 1"
        assert businesses[0].rating == 4.5
        assert businesses[1].id == "test2"
        assert businesses[1].name == "Test Business 2"
        assert businesses[1].rating == 4.0
    
    def test_process_business_results_limit(self, service):
        """Test processing of business results with limit."""
        raw_businesses = [
            {"id": "test1", "name": "Test 1", "url": "https://www.yelp.com/biz/test1", "rating": 4.5, "review_count": 100,
             "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
             "location": {"city": "San Francisco", "state": "CA"},
             "categories": [], "hours": [], "image_url": None},
            {"id": "test2", "name": "Test 2", "url": "https://www.yelp.com/biz/test2", "rating": 4.0, "review_count": 50,
             "coordinates": {"latitude": 37.7849, "longitude": -122.4094},
             "location": {"city": "San Francisco", "state": "CA"},
             "categories": [], "hours": [], "image_url": None},
            {"id": "test3", "name": "Test 3", "url": "https://www.yelp.com/biz/test3", "rating": 3.5, "review_count": 25,
             "coordinates": {"latitude": 37.7949, "longitude": -122.3994},
             "location": {"city": "San Francisco", "state": "CA"},
             "categories": [], "hours": [], "image_url": None}
        ]
        
        businesses = service._process_business_results(raw_businesses, 2, "test_run_123")
        
        assert len(businesses) == 2
        assert businesses[0].id == "test1"
        assert businesses[1].id == "test2"
    
    def test_process_business_results_empty(self, service):
        """Test processing of empty business results."""
        businesses = service._process_business_results([], 10, "test_run_123")
        
        assert len(businesses) == 0
    
    def test_process_business_results_invalid_data(self, service):
        """Test processing of business results with invalid data."""
        raw_businesses = [
            {"id": "test1", "name": "Test 1", "url": "https://www.yelp.com/biz/test1", "rating": 4.5, "review_count": 100,
             "coordinates": {"latitude": 37.7749, "longitude": -122.4194},
             "location": {"city": "San Francisco", "state": "CA"},
             "categories": [], "hours": [], "image_url": None},
            {"invalid": "data"},  # Invalid business data
            {"id": "test3", "name": "Test 3", "url": "https://www.yelp.com/biz/test3", "rating": 3.5, "review_count": 25,
             "coordinates": {"latitude": 37.7949, "longitude": -122.4194},
             "location": {"city": "San Francisco", "state": "CA"},
             "categories": [], "hours": [], "image_url": None}
        ]
        
        businesses = service._process_business_results(raw_businesses, 10, "test_run_123")
        
        # Should process valid businesses and skip invalid ones
        assert len(businesses) == 2
        assert businesses[0].id == "test1"
        assert businesses[1].id == "test3"
