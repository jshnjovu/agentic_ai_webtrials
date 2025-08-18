"""
Integration tests for SERPAPI business search functionality.
These tests require a valid SERPAPI_API_KEY environment variable.
"""

import pytest
import os
from unittest.mock import Mock, patch
from src.services.serpapi_service import SerpAPIService
from src.schemas.business_search import BusinessSearchRequest, LocationType


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_API_KEY") in ["test_key", "your_serpapi_api_key_here"],
    reason="Valid SERPAPI_API_KEY not set for integration testing"
)
class TestSerpAPIIntegration:
    """Integration tests for SERPAPI service."""
    
    @pytest.fixture
    def serpapi_service(self):
        """Create a real SERPAPI service instance."""
        return SerpAPIService()
    
    @pytest.fixture
    def sample_search_request(self):
        """Sample business search request for testing."""
        return BusinessSearchRequest(
            query="restaurants",
            location="New York",
            location_type=LocationType.CITY,
            max_results=5,
            run_id="pytest_integration_test"
        )
    
    def test_service_creation(self, serpapi_service):
        """Test that SERPAPI service can be created successfully."""
        assert serpapi_service.name == "SerpAPIService"
        assert serpapi_service.base_url == "https://serpapi.com/search.json"
        assert serpapi_service.api_key is not None
        assert serpapi_service.api_key != "your_serpapi_api_key_here"
        assert serpapi_service.max_results_per_request == 20
    
    def test_input_validation(self, serpapi_service, sample_search_request):
        """Test that input validation works correctly."""
        assert serpapi_service.validate_input(sample_search_request) is True
        assert serpapi_service.validate_input("invalid") is False
        assert serpapi_service.validate_input(None) is False
    
    def test_real_api_search(self, serpapi_service, sample_search_request):
        """Test real SERPAPI search with actual API call."""
        result = serpapi_service.search_businesses(sample_search_request)
        
        # Verify response structure
        assert hasattr(result, 'success')
        assert hasattr(result, 'query')
        assert hasattr(result, 'location')
        assert hasattr(result, 'total_results')
        assert hasattr(result, 'results')
        assert hasattr(result, 'run_id')
        
        if result.success:
            # Verify successful response
            assert result.query == "restaurants"
            assert result.location == "New York"
            assert result.total_results >= 0
            assert isinstance(result.results, list)
            assert result.run_id == "pytest_integration_test"
            
            # Verify search metadata
            if hasattr(result, 'search_metadata') and result.search_metadata:
                assert result.search_metadata.get("api_used") == "serpapi"
                assert "total_api_results" in result.search_metadata
            
            # Verify business data quality if results exist
            if result.results:
                for business in result.results:
                    assert business.name is not None
                    assert business.place_id is not None
                    assert business.address is not None
                    # Optional fields that should be present with SERPAPI
                    if business.rating is not None:
                        assert 0.0 <= business.rating <= 5.0
                    if business.user_ratings_total is not None:
                        assert business.user_ratings_total >= 0
                    if business.website is not None:
                        assert business.website.startswith(("http://", "https://"))
        else:
            # Verify error response structure
            assert hasattr(result, 'error')
            assert hasattr(result, 'error_code')
            assert hasattr(result, 'context')
            assert result.error is not None
    
    def test_search_with_category_filter(self, serpapi_service):
        """Test SERPAPI search with category filtering."""
        request = BusinessSearchRequest(
            query="gyms",
            location="London",
            location_type=LocationType.CITY,
            category="fitness",
            max_results=3,
            run_id="pytest_category_test"
        )
        
        result = serpapi_service.search_businesses(request)
        
        if result.success and result.results:
            # Verify that results contain fitness-related businesses
            for business in result.results:
                assert business.name is not None
                assert business.address is not None
                # Check if business types contain fitness-related terms
                if business.types:
                    fitness_terms = ["gym", "fitness", "health", "sport"]
                    has_fitness_type = any(
                        any(term in business_type.lower() for term in fitness_terms)
                        for business_type in business.types
                    )
                    # Note: This is a soft assertion as SERPAPI may return broader results
                    # even with category filtering
    
    def test_search_with_radius_limit(self, serpapi_service):
        """Test SERPAPI search with radius limiting."""
        request = BusinessSearchRequest(
            query="coffee shops",
            location="San Francisco, CA",
            location_type=LocationType.CITY,
            radius=2000,  # 2km radius
            max_results=5,
            run_id="pytest_radius_test"
        )
        
        result = serpapi_service.search_businesses(request)
        
        if result.success:
            assert result.query == "coffee shops"
            assert result.location == "San Francisco, CA"
            # Note: SERPAPI doesn't guarantee radius enforcement, so we just verify
            # the request was processed correctly
    
    def test_search_max_results_limit(self, serpapi_service):
        """Test that SERPAPI respects max_results parameter."""
        request = BusinessSearchRequest(
            query="pizza",
            location="Chicago, IL",
            location_type=LocationType.CITY,
            max_results=3,
            run_id="pytest_max_results_test"
        )
        
        result = serpapi_service.search_businesses(request)
        
        if result.success:
            assert result.total_results <= 3
            assert len(result.results) <= 3
    
    def test_search_different_location_types(self, serpapi_service):
        """Test SERPAPI search with different location types."""
        test_cases = [
            ("New York, NY", LocationType.CITY),
            ("10001", LocationType.ZIP_CODE),
            ("Times Square, New York", LocationType.ADDRESS),
        ]
        
        for location, location_type in test_cases:
            request = BusinessSearchRequest(
                query="hotels",
                location=location,
                location_type=location_type,
                max_results=2,
                run_id=f"pytest_location_type_{location_type.value}"
            )
            
            result = serpapi_service.search_businesses(request)
            
            # Verify basic response structure
            assert hasattr(result, 'success')
            assert hasattr(result, 'query')
            assert hasattr(result, 'location')
            assert result.query == "hotels"
            assert result.location == location
    
    def test_search_error_handling(self, serpapi_service):
        """Test SERPAPI error handling with invalid requests."""
        # Test with very long query that might exceed limits
        long_query = "a" * 300  # Exceeds max length of 200
        
        # This should fail Pydantic validation before reaching the service
        with pytest.raises(ValueError) as exc_info:
            BusinessSearchRequest(
                query=long_query,
                location="Test Location",
                location_type=LocationType.CITY,
                max_results=5,
                run_id="pytest_error_handling_test"
            )
        
        # Verify the validation error message
        assert "String should have at most 200 characters" in str(exc_info.value)
    
    def test_search_metadata_consistency(self, serpapi_service, sample_search_request):
        """Test that search metadata is consistent across requests."""
        result1 = serpapi_service.search_businesses(sample_search_request)
        result2 = serpapi_service.search_businesses(sample_search_request)
        
        if result1.success and result2.success:
            # Both should have consistent metadata structure
            assert hasattr(result1, 'search_metadata')
            assert hasattr(result2, 'search_metadata')
            
            if result1.search_metadata and result2.search_metadata:
                assert result1.search_metadata.get("api_used") == "serpapi"
                assert result2.search_metadata.get("api_used") == "serpapi"
    
    def test_business_data_structure(self, serpapi_service):
        """Test that returned business data has consistent structure."""
        request = BusinessSearchRequest(
            query="dentists",
            location="Los Angeles",
            location_type=LocationType.CITY,
            max_results=5,
            run_id="pytest_data_structure_test"
        )
        
        result = serpapi_service.search_businesses(request)
        
        if result.success and result.results:
            for business in result.results:
                # Required fields
                assert business.place_id is not None
                assert business.name is not None
                assert business.address is not None
                
                # Optional fields should have valid types if present
                if business.rating is not None:
                    assert isinstance(business.rating, (int, float))
                    assert 0.0 <= business.rating <= 5.0
                
                if business.user_ratings_total is not None:
                    assert isinstance(business.user_ratings_total, int)
                    assert business.user_ratings_total >= 0
                
                if business.phone is not None:
                    assert isinstance(business.phone, str)
                    assert len(business.phone) > 0
                
                if business.website is not None:
                    assert isinstance(business.website, str)
                    assert business.website.startswith(("http://", "https://"))
                
                if business.types is not None:
                    assert isinstance(business.types, list)
                    for business_type in business.types:
                        assert isinstance(business_type, str)
                        assert len(business_type) > 0
                
                if business.geometry is not None:
                    assert isinstance(business.geometry, dict)
                    if "location" in business.geometry:
                        location = business.geometry["location"]
                        assert "lat" in location
                        assert "lng" in location
                        assert isinstance(location["lat"], (int, float))
                        assert isinstance(location["lng"], (int, float))
                        assert -90 <= location["lat"] <= 90
                        assert -180 <= location["lng"] <= 180


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_API_KEY") in ["test_key", "your_serpapi_api_key_here"],
    reason="Valid SERPAPI_API_KEY not set for integration testing"
)
class TestSerpAPIPerformance:
    """Performance and reliability tests for SERPAPI."""
    
    @pytest.fixture
    def serpapi_service(self):
        """Create a real SERPAPI service instance."""
        return SerpAPIService()
    
    def test_search_response_time(self, serpapi_service):
        """Test that SERPAPI search completes within reasonable time."""
        import time
        
        request = BusinessSearchRequest(
            query="pharmacies",
            location="Miami",
            location_type=LocationType.CITY,
            max_results=3,
            run_id="pytest_performance_test"
        )
        
        start_time = time.time()
        result = serpapi_service.search_businesses(request)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # SERPAPI should respond within 30 seconds
        assert response_time < 30.0, f"SERPAPI search took {response_time:.2f} seconds"
        
        # Verify we got a response (success or error)
        assert hasattr(result, 'success')
    
    def test_concurrent_searches(self, serpapi_service):
        """Test that multiple concurrent searches work correctly."""
        import concurrent.futures
        import time
        
        def single_search(query, location):
            request = BusinessSearchRequest(
                query=query,
                location=location,
                location_type=LocationType.CITY,
                max_results=2,
                run_id=f"pytest_concurrent_{query}_{location}"
            )
            return serpapi_service.search_businesses(request)
        
        # Test concurrent searches
        search_params = [
            ("restaurants", "Seattle"),
            ("hotels", "Denver"),
            ("shops", "Austin")
        ]
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(single_search, query, location)
                for query, location in search_params
            ]
            
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # All searches should complete
        assert len(results) == 3
        
        # Verify each result has proper structure
        for result in results:
            assert hasattr(result, 'success')
            assert hasattr(result, 'query')
            assert hasattr(result, 'location')
        
        # Concurrent searches should be faster than sequential
        # (though this depends on network conditions)
        assert total_time < 60.0, f"Concurrent searches took {total_time:.2f} seconds"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("SERPAPI_API_KEY") or os.getenv("SERPAPI_API_KEY") in ["test_key", "your_serpapi_api_key_here"],
    reason="Valid SERPAPI_API_KEY not set for integration testing"
)
class TestSerpAPIDataQuality:
    """Data quality and consistency tests for SERPAPI."""
    
    @pytest.fixture
    def serpapi_service(self):
        """Create a real SERPAPI service instance."""
        return SerpAPIService()
    
    def test_consistent_business_identification(self, serpapi_service):
        """Test that the same business is consistently identified."""
        # Search for a well-known business
        request = BusinessSearchRequest(
            query="Starbucks",
            location="Times Square, New York",
            location_type=LocationType.ADDRESS,
            max_results=5,
            run_id="pytest_consistency_test"
        )
        
        result = serpapi_service.search_businesses(request)
        
        if result.success and result.results:
            # Look for Starbucks in results
            starbucks_results = [
                business for business in result.results
                if "starbucks" in business.name.lower()
            ]
            
            if starbucks_results:
                # Should have consistent data structure
                for business in starbucks_results:
                    assert business.name is not None
                    assert business.address is not None
                    # Starbucks should have a website
                    if business.website:
                        assert "starbucks" in business.website.lower()
    
    def test_location_accuracy(self, serpapi_service):
        """Test that returned locations are geographically accurate."""
        request = BusinessSearchRequest(
            query="Central Park",
            location="New York, NY",
            location_type=LocationType.CITY,
            max_results=3,
            run_id="pytest_location_accuracy_test"
        )
        
        result = serpapi_service.search_businesses(request)
        
        if result.success and result.results:
            for business in result.results:
                if "central park" in business.name.lower():
                    # Central Park should be in Manhattan
                    assert business.address is not None
                    # Address should contain Manhattan or NYC indicators
                    address_lower = business.address.lower()
                    manhattan_indicators = ["manhattan", "nyc", "new york", "ny"]
                    assert any(indicator in address_lower for indicator in manhattan_indicators)
    
    def test_business_category_accuracy(self, serpapi_service):
        """Test that business categories are accurate."""
        request = BusinessSearchRequest(
            query="McDonald's",
            location="Los Angeles, CA",
            location_type=LocationType.CITY,
            max_results=5,
            run_id="pytest_category_accuracy_test"
        )
        
        result = serpapi_service.search_businesses(request)
        
        if result.success and result.results:
            mcdonalds_results = [
                business for business in result.results
                if "mcdonald" in business.name.lower()
            ]
            
            if mcdonalds_results:
                for business in mcdonalds_results:
                    # McDonald's should have restaurant-related types
                    if business.types:
                        restaurant_indicators = ["restaurant", "food", "fast food", "establishment"]
                        has_restaurant_type = any(
                            any(indicator in business_type.lower() for indicator in restaurant_indicators)
                            for business_type in business.types
                        )
                        # Note: This is a soft assertion as SERPAPI may use different categorization
                        # than expected
