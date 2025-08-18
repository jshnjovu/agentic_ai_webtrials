"""
Unit tests for GeoapifyService.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.geoapify_service import GeoapifyService


class TestGeoapifyService:
    """Test cases for GeoapifyService."""
    
    @pytest.fixture
    def geoapify_service(self):
        """Create a GeoapifyService instance for testing."""
        with patch('src.services.geoapify_service.get_api_config') as mock_config:
            mock_config.return_value.GEOAPIFY_API_KEY = "test_geoapify_key"
            return GeoapifyService()
    
    @pytest.fixture
    def mock_location_response(self):
        """Mock response from Geoapify API - exactly matching GEOAPIFY.md structure."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "country_code": "US",
                        "country": "United States",
                        "state": "Texas",
                        "city": "Austin",
                        "lat": 30.2672,
                        "lon": -97.7431,
                        "formatted": "Austin, TX, USA"
                    }
                }
            ]
        }
    
    def test_service_initialization(self, geoapify_service):
        """Test GeoapifyService initialization."""
        assert geoapify_service.name == "GeoapifyService"
        assert geoapify_service.api_key == "test_geoapify_key"
        assert geoapify_service.base_url == "https://api.geoapify.com/v1/geocode/autocomplete"
    
    def test_service_initialization_no_api_key(self):
        """Test GeoapifyService initialization without API key."""
        with patch('src.services.geoapify_service.get_api_config') as mock_config:
            mock_config.return_value.GEOAPIFY_API_KEY = None
            service = GeoapifyService()
            assert service.api_key is None
    
    @patch('src.services.geoapify_service.httpx.Client')
    def test_extract_country_code_success(self, mock_client_class, geoapify_service, mock_location_response):
        """Test successful country code extraction."""
        # Mock the HTTP client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_location_response
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        # Test country code extraction
        country_code = geoapify_service.extract_country_code("Austin, Texas")
        
        # Verify result
        assert country_code == "us"  # Should be lowercase
        
        # Verify API call was made correctly
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "https://api.geoapify.com/v1/geocode/autocomplete"
        
        # Check parameters - exactly matching GEOAPIFY.md pattern
        params = call_args[1]['params']
        assert params['text'] == "Austin, Texas"
        assert params['apiKey'] == "test_geoapify_key"
        # No extra parameters like format, limit, or type
    
    @patch('src.services.geoapify_service.httpx.Client')
    def test_extract_country_code_philippines(self, mock_client_class, geoapify_service):
        """Test country code extraction for Philippines location."""
        philippines_response = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "country_code": "PH",
                        "country": "Philippines",
                        "city": "Manila",
                        "formatted": "Manila, Philippines"
                    }
                }
            ]
        }
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = philippines_response
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        country_code = geoapify_service.extract_country_code("Rizal Park, Manila")
        assert country_code == "ph"
    
    @patch('src.services.geoapify_service.httpx.Client')
    def test_extract_country_code_no_results(self, mock_client_class, geoapify_service):
        """Test country code extraction when no results are found."""
        no_results_response = {"type": "FeatureCollection", "features": []}
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = no_results_response
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        country_code = geoapify_service.extract_country_code("Invalid Location")
        assert country_code is None
    
    @patch('src.services.geoapify_service.httpx.Client')
    def test_extract_country_code_no_country_code(self, mock_client_class, geoapify_service):
        """Test country code extraction when result has no country_code field."""
        response_without_country = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "country": "Unknown Country",
                        "city": "Unknown City"
                    }
                }
            ]
        }
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = response_without_country
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        country_code = geoapify_service.extract_country_code("Unknown Location")
        assert country_code is None
    
    def test_extract_country_code_no_api_key(self):
        """Test country code extraction without API key."""
        with patch('src.services.geoapify_service.get_api_config') as mock_config:
            mock_config.return_value.GEOAPIFY_API_KEY = None
            service = GeoapifyService()
            
            country_code = service.extract_country_code("Austin, Texas")
            assert country_code is None
    
    @patch('src.services.geoapify_service.httpx.Client')
    def test_extract_country_code_http_error(self, mock_client_class, geoapify_service):
        """Test country code extraction with HTTP error."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP Error")
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        country_code = geoapify_service.extract_country_code("Austin, Texas")
        assert country_code is None
    
    @patch('src.services.geoapify_service.httpx.Client')
    def test_get_location_info_success(self, mock_client_class, geoapify_service, mock_location_response):
        """Test successful location info retrieval."""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_location_response
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        location_info = geoapify_service.get_location_info("Austin, Texas")
        
        assert location_info is not None
        assert location_info['country_code'] == "us"
        assert location_info['country'] == "United States"
        assert location_info['state'] == "Texas"
        assert location_info['city'] == "Austin"
        assert location_info['lat'] == 30.2672
        assert location_info['lon'] == -97.7431
        assert location_info['formatted_address'] == "Austin, TX, USA"
    
    @patch('src.services.geoapify_service.httpx.Client')
    def test_get_location_info_no_results(self, mock_client_class, geoapify_service):
        """Test location info retrieval when no results are found."""
        no_results_response = {"type": "FeatureCollection", "features": []}
        
        mock_client = Mock()
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = no_results_response
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client
        
        location_info = geoapify_service.get_location_info("Invalid Location")
        assert location_info is None
