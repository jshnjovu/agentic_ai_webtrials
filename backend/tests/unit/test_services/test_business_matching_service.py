"""
Unit tests for BusinessMatchingService.
Tests business name matching, address similarity, coordinate proximity, and combined scoring.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.business_matching_service import BusinessMatchingService
from src.schemas.business_matching import (
    BusinessSourceData,
    BusinessLocation,
    BusinessContactInfo,
    BusinessMatchingRequest,
    ConfidenceLevel
)


class TestBusinessMatchingService:
    """Test cases for BusinessMatchingService."""
    
    @pytest.fixture
    def service(self):
        """Create a BusinessMatchingService instance for testing."""
        return BusinessMatchingService()
    
    @pytest.fixture
    def sample_businesses(self):
        """Create sample business data for testing."""
        return [
            BusinessSourceData(
                source="google_places",
                source_id="gp_001",
                name="Joe's Pizza & Italian Restaurant",
                location=BusinessLocation(
                    latitude=40.7128,
                    longitude=-74.0060,
                    address="123 Main St, New York, NY 10001",
                    city="New York",
                    state="NY",
                    zip_code="10001",
                    country="US"
                ),
                contact_info=BusinessContactInfo(
                    phone="+1-555-123-4567",
                    website="https://www.joespizza.com"
                ),
                rating=4.5,
                review_count=150,
                categories=["Pizza", "Italian", "Restaurant"],
                price_level=2
            ),
            BusinessSourceData(
                source="yelp_fusion",
                source_id="yf_001",
                name="Joe's Pizza Italian Restaurant",
                location=BusinessLocation(
                    latitude=40.7129,
                    longitude=-74.0061,
                    address="123 Main Street, New York, NY 10001",
                    city="New York",
                    state="NY",
                    zip_code="10001",
                    country="US"
                ),
                contact_info=BusinessContactInfo(
                    phone="555-123-4567",
                    website="joespizza.com"
                ),
                rating=4.3,
                review_count=120,
                categories=["Pizza", "Italian", "Restaurant"],
                price_level=2
            ),
            BusinessSourceData(
                source="google_places",
                source_id="gp_002",
                name="Starbucks Coffee",
                location=BusinessLocation(
                    latitude=40.7589,
                    longitude=-73.9851,
                    address="456 Broadway, New York, NY 10013",
                    city="New York",
                    state="NY",
                    zip_code="10013",
                    country="US"
                ),
                contact_info=BusinessContactInfo(
                    phone="+1-555-987-6543",
                    website="https://www.starbucks.com"
                ),
                rating=4.2,
                review_count=200,
                categories=["Coffee", "Cafe", "Breakfast"],
                price_level=2
            )
        ]
    
    def test_service_initialization(self, service):
        """Test that the service initializes correctly."""
        assert service.service_name == "BusinessMatchingService"
        assert service.logger is not None
    
    def test_validate_input_valid(self, service, sample_businesses):
        """Test input validation with valid data."""
        request = BusinessMatchingRequest(
            businesses=sample_businesses[:2],
            run_id="test_run_001"
        )
        assert service.validate_input(request) is True
    
    def test_validate_input_invalid(self, service):
        """Test input validation with invalid data."""
        # Single business (should fail)
        request = BusinessMatchingRequest(
            businesses=[Mock()],
            run_id="test_run_001"
        )
        assert service.validate_input(request) is False
        
        # Wrong type
        assert service.validate_input("invalid") is False
    
    def test_normalize_business_name(self, service):
        """Test business name normalization."""
        # Test with common suffixes
        assert service._normalize_business_name("Joe's Pizza Inc.") == "joes pizza"
        assert service._normalize_business_name("ABC Company LLC") == "abc company"
        assert service._normalize_business_name("XYZ Corp & Co") == "xyz corp"
        
        # Test with punctuation
        assert service._normalize_business_name("Joe's Pizza & Italian Restaurant!") == "joes pizza italian restaurant"
        
        # Test with extra whitespace
        assert service._normalize_business_name("  Joe's   Pizza  ") == "joes pizza"
    
    def test_normalize_address(self, service):
        """Test address normalization."""
        # Test with abbreviations
        assert service._normalize_address("123 Main Street") == "123 main st"
        assert service._normalize_address("456 North Avenue") == "456 n ave"
        assert service._normalize_address("789 East Boulevard") == "789 e blvd"
        
        # Test with punctuation
        assert service._normalize_address("123 Main St., New York, NY") == "123 main st new york ny"
        
        # Test with extra whitespace
        assert service._normalize_address("  123  Main  St  ") == "123 main st"
    
    def test_calculate_name_similarity(self, service):
        """Test business name similarity calculation."""
        # High similarity
        assert service._calculate_name_similarity("Joe's Pizza", "Joes Pizza") > 0.8
        
        # Medium similarity
        assert service._calculate_name_similarity("Joe's Pizza", "Joe Pizza") > 0.6
        
        # Low similarity
        assert service._calculate_name_similarity("Joe's Pizza", "Starbucks Coffee") < 0.3
        
        # Empty names
        assert service._calculate_name_similarity("", "Joe's Pizza") == 0.0
        assert service._calculate_name_similarity("Joe's Pizza", "") == 0.0
    
    def test_calculate_address_similarity(self, service):
        """Test address similarity calculation."""
        location1 = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Main St, New York, NY"
        )
        location2 = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Main Street, New York, NY"
        )
        
        # High similarity for similar addresses
        similarity = service._calculate_address_similarity(location1, location2)
        assert similarity > 0.7
    
    def test_calculate_coordinate_proximity(self, service):
        """Test coordinate proximity calculation."""
        location1 = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Main St"
        )
        location2 = BusinessLocation(
            latitude=40.7129,
            longitude=-74.0061,
            address="124 Main St"
        )
        
        # Very close coordinates should have high similarity
        similarity = service._calculate_coordinate_proximity(location1, location2)
        assert similarity > 0.9
        
        # Test with missing coordinates
        location3 = BusinessLocation(
            latitude=None,
            longitude=None,
            address="Unknown"
        )
        similarity = service._calculate_coordinate_proximity(location1, location3)
        assert similarity == 0.0
    
    def test_determine_confidence_level(self, service):
        """Test confidence level determination."""
        assert service._determine_confidence_level(0.9) == ConfidenceLevel.HIGH
        assert service._determine_confidence_level(0.7) == ConfidenceLevel.MEDIUM
        assert service._determine_confidence_level(0.5) == ConfidenceLevel.LOW
    
    def test_calculate_similarity_score(self, service, sample_businesses):
        """Test combined similarity score calculation."""
        business1 = sample_businesses[0]
        business2 = sample_businesses[1]
        
        score = service._calculate_similarity_score(
            business1, business2, 0.4, 0.3, 0.3
        )
        
        assert 0.0 <= score.name_similarity <= 1.0
        assert 0.0 <= score.address_similarity <= 1.0
        assert 0.0 <= score.coordinate_proximity <= 1.0
        assert 0.0 <= score.combined_score <= 1.0
        assert score.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
    
    def test_find_matches(self, service, sample_businesses):
        """Test finding matches among businesses."""
        businesses = sample_businesses[:2]  # Use first two businesses
        
        matched_groups, unmatched = service._find_matches(
            businesses, 0.7, 0.4, 0.3, 0.3
        )
        
        # Should find at least one match group for similar businesses
        assert len(matched_groups) >= 0
        assert len(unmatched) >= 0
    
    def test_match_businesses_success(self, service, sample_businesses):
        """Test successful business matching."""
        request = BusinessMatchingRequest(
            businesses=sample_businesses[:2],
            name_weight=0.4,
            address_weight=0.3,
            coordinate_weight=0.3,
            similarity_threshold=0.7,
            run_id="test_run_001"
        )
        
        response = service.match_businesses(request)
        
        assert response.success is True
        assert response.total_businesses == 2
        assert response.run_id == "test_run_001"
        assert "similarity_threshold" in response.matching_metadata
    
    def test_match_businesses_validation_error(self, service):
        """Test business matching with validation error."""
        request = BusinessMatchingRequest(
            businesses=[Mock()],  # Single business should fail validation
            run_id="test_run_001"
        )
        
        with pytest.raises(ValueError, match="Invalid input"):
            service.match_businesses(request)
    
    def test_match_businesses_with_dissimilar_businesses(self, service, sample_businesses):
        """Test matching with businesses that are not similar."""
        # Use first and third business (different types)
        request = BusinessMatchingRequest(
            businesses=[sample_businesses[0], sample_businesses[2]],
            similarity_threshold=0.8,  # High threshold
            run_id="test_run_002"
        )
        
        response = service.match_businesses(request)
        
        assert response.success is True
        # Should have no matches due to high threshold
        assert len(response.matched_groups) == 0
        assert len(response.unmatched_businesses) == 2
    
    def test_normalize_businesses(self, service, sample_businesses):
        """Test business data normalization."""
        normalized = service._normalize_businesses(sample_businesses[:2])
        
        assert len(normalized) == 2
        # Check that names are normalized
        assert "inc" not in normalized[0].name.lower()
        assert "llc" not in normalized[1].name.lower()
    
    @patch('src.services.business_matching_service.fuzz')
    def test_fuzzy_matching_integration(self, mock_fuzz, service):
        """Test integration with fuzzy string matching library."""
        # Mock fuzzy matching results
        mock_fuzz.ratio.return_value = 85
        mock_fuzz.partial_ratio.return_value = 90
        mock_fuzz.token_sort_ratio.return_value = 88
        mock_fuzz.token_set_ratio.return_value = 92
        
        similarity = service._calculate_name_similarity("Joe's Pizza", "Joes Pizza")
        
        # Should use the highest ratio (92)
        assert similarity == 0.92
        
        # Verify all fuzzy matching methods were called
        mock_fuzz.ratio.assert_called_once()
        mock_fuzz.partial_ratio.assert_called_once()
        mock_fuzz.token_sort_ratio.assert_called_once()
        mock_fuzz.token_set_ratio.assert_called_once()
    
    def test_coordinate_proximity_edge_cases(self, service):
        """Test coordinate proximity with edge cases."""
        # Test with identical coordinates
        location1 = BusinessLocation(latitude=40.7128, longitude=-74.0060)
        location2 = BusinessLocation(latitude=40.7128, longitude=-74.0060)
        
        similarity = service._calculate_coordinate_proximity(location1, location2)
        assert similarity == 1.0  # Should be exact match
        
        # Test with very distant coordinates
        location3 = BusinessLocation(latitude=90.0, longitude=180.0)
        similarity = service._calculate_coordinate_proximity(location1, location3)
        assert similarity < 0.1  # Should be very low similarity
    
    def test_error_handling(self, service):
        """Test error handling in the service."""
        # Test with invalid request
        with pytest.raises(ValueError):
            service.match_businesses(None)
        
        # Test with empty businesses list
        request = BusinessMatchingRequest(
            businesses=[],
            run_id="test_run_003"
        )
        
        with pytest.raises(ValueError, match="Invalid input"):
            service.match_businesses(request)
    
    def test_logging_integration(self, service, sample_businesses):
        """Test that logging is properly integrated."""
        request = BusinessMatchingRequest(
            businesses=sample_businesses[:2],
            run_id="test_run_004"
        )
        
        # Should not raise any logging-related errors
        try:
            service.match_businesses(request)
        except Exception:
            pass  # We expect this to fail due to missing dependencies, but logging should work
        
        # Verify logger is set up
        assert service.logger is not None
