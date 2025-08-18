"""
Integration tests for SerpAPIService with GeoapifyService.
Tests the dynamic country code extraction functionality.
"""

import pytest
import os
from unittest.mock import patch, Mock
from src.services.serpapi_service import SerpAPIService
from src.services.geoapify_service import GeoapifyService
from src.schemas.business_search import BusinessSearchRequest, LocationType


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GEOAPIFY_API_KEY") or os.getenv("GEOAPIFY_API_KEY") in ["test_key", "your_geoapify_api_key_here"],
    reason="Valid GEOAPIFY_API_KEY not set for integration testing"
)
class TestSerpAPIGeoapifyIntegration:
    """Integration tests for SerpAPI with Geoapify country code extraction."""
    
    @pytest.fixture
    def serpapi_service(self):
        """Create SerpAPIService instance."""
        return SerpAPIService()
    
    @pytest.fixture
    def geoapify_service(self):
        """Create GeoapifyService instance."""
        return GeoapifyService()
    
    def test_geoapify_service_initialization(self, geoapify_service):
        """Test that GeoapifyService initializes correctly."""
        assert geoapify_service.name == "GeoapifyService"
        assert geoapify_service.api_key is not None
        assert geoapify_service.base_url == "https://api.geoapify.com/v1/geocode/autocomplete"
    
    def test_serpapi_service_has_geoapify(self, serpapi_service):
        """Test that SerpAPIService has GeoapifyService integrated."""
        assert hasattr(serpapi_service, 'geoapify_service')
        assert isinstance(serpapi_service.geoapify_service, GeoapifyService)
    
    def test_country_code_extraction_us_location(self, geoapify_service):
        """Test country code extraction for US location."""
        country_code = geoapify_service.extract_country_code("Austin, Texas")
        assert country_code == "us"
    
    def test_country_code_extraction_international_location(self, geoapify_service):
        """Test country code extraction for international location."""
        # Test with a known international location
        country_code = geoapify_service.extract_country_code("London, England")
        assert country_code == "gb"  # Great Britain
        
        # Test with another international location
        country_code = geoapify_service.extract_country_code("Toronto, Canada")
        assert country_code == "ca"  # Canada
    
    def test_country_code_extraction_philippines(self, geoapify_service):
        """Test country code extraction for Philippines location."""
        country_code = geoapify_service.extract_country_code("Manila, Philippines")
        assert country_code == "ph"
    
    def test_serpapi_build_params_with_dynamic_country_code(self, serpapi_service):
        """Test that SerpAPIService builds params with dynamic country code."""
        # Test US location
        request = BusinessSearchRequest(
            query="gyms",
            location="Austin, Texas",
            location_type=LocationType.CITY,
            max_results=5,
            run_id="test_geoapify_integration"
        )
        
        params = serpapi_service._build_search_params(request)
        assert params["gl"] == "us"
        assert params["location"] == "Austin, Texas"
        
        # Test international location
        request = BusinessSearchRequest(
            query="restaurants",
            location="Manila, Philippines",
            location_type=LocationType.CITY,
            max_results=5,
            run_id="test_geoapify_integration"
        )
        
        params = serpapi_service._build_search_params(request)
        assert params["gl"] == "ph"
        assert params["location"] == "Manila, Philippines"
    
    def test_serpapi_build_params_fallback_to_us(self, serpapi_service):
        """Test that SerpAPIService falls back to 'us' when Geoapify fails."""
        # Mock Geoapify service to return None
        with patch.object(serpapi_service.geoapify_service, 'extract_country_code', return_value=None):
            request = BusinessSearchRequest(
                query="gyms",
                location="Unknown Location",
                location_type=LocationType.CITY,
                max_results=5,
                run_id="test_geoapify_integration"
            )
            
            params = serpapi_service._build_search_params(request)
            assert params["gl"] == "us"  # Should fallback to US
    
    def test_location_info_retrieval(self, geoapify_service):
        """Test detailed location information retrieval."""
        location_info = geoapify_service.get_location_info("Austin, Texas")
        
        assert location_info is not None
        assert location_info['country_code'] == "us"
        assert location_info['country'] == "United States"
        assert location_info['state'] == "Texas"
        assert location_info['city'] == "Austin"
        assert 'lat' in location_info
        assert 'lon' in location_info
        assert 'formatted_address' in location_info
    
    def test_multiple_location_formats(self, geoapify_service):
        """Test country code extraction with various location formats."""
        test_locations = [
            ("Austin, TX", "us"),
            ("New York, NY", "us"),
            ("Los Angeles, California", "us"),
            ("London, UK", "gb"),
            ("Paris, France", "fr"),
            ("Tokyo, Japan", "jp"),
            ("Sydney, Australia", "au"),
            ("Toronto, Ontario", "ca"),
            ("Mexico City, Mexico", "mx"),
            ("São Paulo, Brazil", "br")
        ]
        
        for location, expected_country in test_locations:
            country_code = geoapify_service.extract_country_code(location)
            if country_code:  # Some locations might not resolve
                assert country_code == expected_country, f"Expected {expected_country} for {location}, got {country_code}"
    
    def test_serpapi_search_with_dynamic_country(self, serpapi_service):
        """Test that SerpAPI search uses the correct country code."""
        # This test requires a valid SERPAPI_API_KEY
        if not os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_API_KEY") in ["test_key", "your_serpapi_api_key_here"]:
            pytest.skip("Valid SERPAPI_API_KEY not set")
        
        # Test with US location
        request = BusinessSearchRequest(
            query="gyms",
            location="Austin, Texas",
            location_type=LocationType.CITY,
            max_results=3,
            run_id="test_geoapify_integration"
        )
        
        # Mock the actual SerpAPI call to avoid rate limiting
        with patch.object(serpapi_service, '_execute_search') as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "results": [{"title": "Test Gym", "address": "Test Address"}]
            }
            
            # Build params to test country code extraction
            params = serpapi_service._build_search_params(request)
            assert params["gl"] == "us"
            
            # Test the full search flow
            result = serpapi_service.search_businesses(request)
            assert result.success is True


@pytest.mark.performance
class TestSerpAPIGeoapifyPerformance:
    """Performance tests for SerpAPI with Geoapify integration."""
    
    @pytest.fixture
    def serpapi_service(self):
        """Create SerpAPIService instance."""
        return SerpAPIService()
    
    def test_country_code_extraction_performance(self, serpapi_service):
        """Test performance of country code extraction."""
        import time
        
        locations = [
            "Austin, Texas",
            "New York, NY",
            "London, UK",
            "Paris, France",
            "Tokyo, Japan"
        ]
        
        start_time = time.time()
        
        for location in locations:
            # Mock the Geoapify call to avoid actual API calls
            with patch.object(serpapi_service.geoapify_service, 'extract_country_code') as mock_extract:
                mock_extract.return_value = "us" if "Texas" in location or "NY" in location else "gb"
                
                request = BusinessSearchRequest(
                    query="test",
                    location=location,
                    location_type=LocationType.CITY,
                    max_results=5,
                    run_id="test_performance"
                )
                
                params = serpapi_service._build_search_params(request)
                assert "gl" in params
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete quickly (under 1 second for mocked calls)
        assert execution_time < 1.0, f"Country code extraction took {execution_time:.2f}s, expected under 1s"
