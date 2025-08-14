"""
Tests for the confidence scoring service.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.confidence_scoring_service import ConfidenceScoringService
from src.schemas.business_matching import (
    BusinessSourceData, BusinessLocation, BusinessContactInfo, ConfidenceLevel
)
from src.schemas.business_merging import DataCompletenessScore, MergedBusinessData, MergeConflict


class TestConfidenceScoringService:
    """Test cases for ConfidenceScoringService."""
    
    @pytest.fixture
    def service(self):
        """Create a confidence scoring service instance."""
        return ConfidenceScoringService()
    
    @pytest.fixture
    def sample_business_data(self):
        """Create sample business data for testing."""
        return BusinessSourceData(
            source="google_places",
            source_id="test_id_1",
            name="Test Business Name",
            location=BusinessLocation(
                latitude=40.7128,
                longitude=-74.0060,
                address="123 Test Street",
                city="New York",
                state="NY",
                zip_code="10001"
            ),
            contact_info=BusinessContactInfo(
                phone="+1-555-123-4567",
                website="https://testbusiness.com",
                email="info@testbusiness.com"
            ),
            rating=4.5,
            review_count=100,
            categories=["Restaurant", "Italian"],
            price_level=2,
            hours={"Monday": "9:00 AM - 5:00 PM"},
            photos=[{"url": "https://example.com/photo1.jpg"}],
            raw_data={},
            last_updated="2024-01-01T00:00:00Z"
        )
    
    @pytest.fixture
    def sample_completeness_scores(self):
        """Create sample completeness scores for testing."""
        return [
            DataCompletenessScore(
                source="google_places",
                overall_score=0.85,
                name_score=1.0,
                location_score=0.9,
                contact_score=0.8,
                rating_score=1.0,
                category_score=0.9,
                details={}
            ),
            DataCompletenessScore(
                source="yelp_fusion",
                overall_score=0.75,
                name_score=1.0,
                location_score=0.7,
                contact_score=0.6,
                rating_score=1.0,
                category_score=0.8,
                details={}
            )
        ]
    
    @pytest.fixture
    def sample_conflicts(self):
        """Create sample conflicts for testing."""
        return [
            MergeConflict(
                field_name="phone",
                source_values={"google": "+1-555-123-4567", "yelp": "+1-555-123-4568"},
                resolution_strategy="completeness",
                resolved_value="+1-555-123-4567",
                confidence=0.8
            ),
            MergeConflict(
                field_name="website",
                source_values={"google": "https://testbusiness.com", "yelp": "https://testbusiness.org"},
                resolution_strategy="completeness",
                resolved_value="https://testbusiness.com",
                confidence=0.7
            )
        ]
    
    def test_validate_input(self, service):
        """Test input validation."""
        assert service.validate_input("test") is True
        assert service.validate_input(None) is False
    
    def test_calculate_data_confidence_complete_data(self, service, sample_business_data):
        """Test confidence calculation for complete business data."""
        confidence = service.calculate_data_confidence(sample_business_data)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.8  # Should be high for complete data
    
    def test_calculate_data_confidence_incomplete_data(self, service):
        """Test confidence calculation for incomplete business data."""
        incomplete_data = BusinessSourceData(
            source="test_source",
            source_id="test_id",
            name="Test",
            location=BusinessLocation(),
            contact_info=None,
            rating=None,
            review_count=None,
            categories=None,
            price_level=None,
            hours=None,
            photos=None,
            raw_data={},
            last_updated=None
        )
        
        confidence = service.calculate_data_confidence(incomplete_data)
        assert 0.0 <= confidence <= 1.0
        assert confidence < 0.5  # Should be low for incomplete data
    
    def test_calculate_data_confidence_empty_name(self, service):
        """Test confidence calculation with empty business name."""
        data = BusinessSourceData(
            source="test_source",
            source_id="test_id",
            name="",
            location=BusinessLocation(),
            contact_info=None,
            rating=None,
            review_count=None,
            categories=None,
            price_level=None,
            hours=None,
            photos=None,
            raw_data={},
            last_updated=None
        )
        
        confidence = service.calculate_data_confidence(data)
        assert confidence == 0.0
    
    def test_assign_confidence_level_high(self, service):
        """Test confidence level assignment for high confidence."""
        level = service.assign_confidence_level(0.9)
        assert level == ConfidenceLevel.HIGH
        
        level = service.assign_confidence_level(0.8)
        assert level == ConfidenceLevel.HIGH
    
    def test_assign_confidence_level_medium(self, service):
        """Test confidence level assignment for medium confidence."""
        level = service.assign_confidence_level(0.7)
        assert level == ConfidenceLevel.MEDIUM
        
        level = service.assign_confidence_level(0.6)
        assert level == ConfidenceLevel.MEDIUM
    
    def test_assign_confidence_level_low(self, service):
        """Test confidence level assignment for low confidence."""
        level = service.assign_confidence_level(0.5)
        assert level == ConfidenceLevel.LOW
        
        level = service.assign_confidence_level(0.0)
        assert level == ConfidenceLevel.LOW
    
    def test_assign_confidence_level_edge_cases(self, service):
        """Test confidence level assignment edge cases."""
        # Test boundary values
        assert service.assign_confidence_level(0.8) == ConfidenceLevel.HIGH
        assert service.assign_confidence_level(0.79) == ConfidenceLevel.MEDIUM
        assert service.assign_confidence_level(0.6) == ConfidenceLevel.MEDIUM
        assert service.assign_confidence_level(0.59) == ConfidenceLevel.LOW
    
    def test_calculate_merged_confidence_no_conflicts(self, service, sample_completeness_scores):
        """Test merged confidence calculation with no conflicts."""
        confidence = service.calculate_merged_confidence(sample_completeness_scores, [])
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # Should be high for good data with no conflicts
    
    def test_calculate_merged_confidence_with_conflicts(self, service, sample_completeness_scores, sample_conflicts):
        """Test merged confidence calculation with conflicts."""
        confidence = service.calculate_merged_confidence(sample_completeness_scores, sample_conflicts)
        
        assert 0.0 <= confidence <= 1.0
        # Should be lower than no conflicts due to conflict resolution confidence
    
    def test_calculate_merged_confidence_empty_scores(self, service):
        """Test merged confidence calculation with empty scores."""
        confidence = service.calculate_merged_confidence([], [])
        assert confidence == 0.0
    
    def test_add_confidence_indicators(self, service):
        """Test adding confidence indicators to merged business."""
        merged_business = MergedBusinessData(
            business_id="test_id",
            name="Test Business",
            location=BusinessLocation(),
            confidence_level=ConfidenceLevel.HIGH,
            source_contributions=["google_places", "yelp_fusion"],
            merge_metadata={},
            last_updated="2024-01-01T00:00:00Z",
            needs_review=False
        )
        
        indicators = service.add_confidence_indicators(merged_business)
        
        assert "overall_confidence" in indicators
        assert "confidence_score" in indicators
        assert "review_required" in indicators
        assert "data_quality" in indicators
        assert "source_reliability" in indicators
        assert "last_assessment" in indicators
        
        assert indicators["overall_confidence"] == "high"
        assert indicators["review_required"] is False
        assert indicators["data_quality"] == "excellent"
        assert indicators["source_reliability"] == "medium"
    
    def test_calculate_name_confidence(self, service):
        """Test name confidence calculation."""
        # Test good name
        good_name_confidence = service._calculate_name_confidence("Excellent Business Name")
        assert good_name_confidence > 0.8
        
        # Test short name
        short_name_confidence = service._calculate_name_confidence("Test")
        assert short_name_confidence < good_name_confidence
        
        # Test name with special characters
        special_char_confidence = service._calculate_name_confidence("Test@Business#Name")
        assert special_char_confidence < good_name_confidence
    
    def test_calculate_location_confidence(self, service):
        """Test location confidence calculation."""
        # Test complete location
        complete_location = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Test Street",
            city="New York",
            state="NY",
            zip_code="10001"
        )
        complete_confidence = service._calculate_location_confidence(complete_location)
        assert complete_confidence > 0.8
        
        # Test incomplete location
        incomplete_location = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060
        )
        incomplete_confidence = service._calculate_location_confidence(incomplete_location)
        assert incomplete_confidence < complete_confidence
        
        # Test edge case coordinates (valid but edge case)
        edge_location = BusinessLocation(
            latitude=89.9,  # Valid but edge case latitude
            longitude=-179.9,  # Valid but edge case longitude
            address="Test Address",  # Add some address info
            city="Test City"
        )
        edge_confidence = service._calculate_location_confidence(edge_location)
        assert edge_confidence > 0.7  # Edge case with partial address info
    
    def test_calculate_contact_confidence(self, service):
        """Test contact information confidence calculation."""
        # Test complete contact info
        complete_contact = BusinessContactInfo(
            phone="+1-555-123-4567",
            website="https://testbusiness.com",
            email="info@testbusiness.com"
        )
        complete_confidence = service._calculate_contact_confidence(complete_contact)
        assert complete_confidence == 1.0
        
        # Test partial contact info
        partial_contact = BusinessContactInfo(
            phone="+1-555-123-4567",
            website=None,
            email=None
        )
        partial_confidence = service._calculate_contact_confidence(partial_contact)
        assert partial_confidence < complete_confidence
        
        # Test no contact info
        no_contact_confidence = service._calculate_contact_confidence(None)
        assert no_contact_confidence == 0.0
    
    def test_calculate_rating_confidence(self, service):
        """Test rating confidence calculation."""
        # Test valid rating
        assert service._calculate_rating_confidence(4.5) == 1.0
        assert service._calculate_rating_confidence(0.0) == 1.0
        assert service._calculate_rating_confidence(5.0) == 1.0
        
        # Test invalid rating
        assert service._calculate_rating_confidence(-1.0) == 0.0
        assert service._calculate_rating_confidence(6.0) == 0.0
        
        # Test None rating
        assert service._calculate_rating_confidence(None) == 0.0
    
    def test_calculate_categories_confidence(self, service):
        """Test categories confidence calculation."""
        # Test multiple categories (3 categories should return 0.9 according to the logic)
        assert service._calculate_categories_confidence(["Restaurant", "Italian", "Pizza"]) == 0.9
        
        # Test single category
        assert service._calculate_categories_confidence(["Restaurant"]) == 0.7
        
        # Test no categories
        assert service._calculate_categories_confidence([]) == 0.0
        assert service._calculate_categories_confidence(None) == 0.0
    
    def test_calculate_hours_confidence(self, service):
        """Test hours confidence calculation."""
        # Test valid hours
        assert service._calculate_hours_confidence({"Monday": "9:00 AM - 5:00 PM"}) == 0.8
        
        # Test empty hours
        assert service._calculate_hours_confidence({}) == 0.0
        
        # Test None hours
        assert service._calculate_hours_confidence(None) == 0.0
    
    def test_calculate_source_confidence(self, service, sample_completeness_scores):
        """Test source confidence calculation."""
        confidence = service._calculate_source_confidence(sample_completeness_scores)
        
        # Should be average of completeness scores
        expected = (0.85 + 0.75) / 2
        assert abs(confidence - expected) < 0.01
    
    def test_calculate_conflict_resolution_confidence(self, service, sample_conflicts):
        """Test conflict resolution confidence calculation."""
        confidence = service._calculate_conflict_resolution_confidence(sample_conflicts)
        
        # Should be average of conflict confidences
        expected = (0.8 + 0.7) / 2
        assert abs(confidence - expected) < 0.01
    
    def test_calculate_conflict_resolution_confidence_no_conflicts(self, service):
        """Test conflict resolution confidence with no conflicts."""
        confidence = service._calculate_conflict_resolution_confidence([])
        assert confidence == 1.0
    
    def test_calculate_data_consistency_confidence(self, service, sample_completeness_scores):
        """Test data consistency confidence calculation."""
        confidence = service._calculate_data_consistency_confidence(sample_completeness_scores)
        
        assert 0.0 <= confidence <= 1.0
        # Should be lower than 1.0 due to variance between sources
    
    def test_calculate_data_consistency_confidence_single_source(self, service):
        """Test data consistency confidence with single source."""
        single_score = [DataCompletenessScore(
            source="test",
            overall_score=0.8,
            name_score=0.8,
            location_score=0.8,
            contact_score=0.8,
            rating_score=0.8,
            category_score=0.8,
            details={}
        )]
        
        confidence = service._calculate_data_consistency_confidence(single_score)
        assert confidence == 1.0
    
    def test_confidence_level_to_score(self, service):
        """Test confidence level to score conversion."""
        assert service._confidence_level_to_score(ConfidenceLevel.HIGH) == 0.9
        assert service._confidence_level_to_score(ConfidenceLevel.MEDIUM) == 0.7
        assert service._confidence_level_to_score(ConfidenceLevel.LOW) == 0.4
    
    def test_assess_data_quality(self, service):
        """Test data quality assessment."""
        high_quality_business = Mock()
        high_quality_business.confidence_level = ConfidenceLevel.HIGH
        
        medium_quality_business = Mock()
        medium_quality_business.confidence_level = ConfidenceLevel.MEDIUM
        
        low_quality_business = Mock()
        low_quality_business.confidence_level = ConfidenceLevel.LOW
        
        assert service._assess_data_quality(high_quality_business) == "excellent"
        assert service._assess_data_quality(medium_quality_business) == "good"
        assert service._assess_data_quality(low_quality_business) == "fair"
    
    def test_assess_source_reliability(self, service):
        """Test source reliability assessment."""
        many_sources_business = Mock()
        many_sources_business.source_contributions = ["source1", "source2", "source3"]
        
        two_sources_business = Mock()
        two_sources_business.source_contributions = ["source1", "source2"]
        
        single_source_business = Mock()
        single_source_business.source_contributions = ["source1"]
        
        assert service._assess_source_reliability(many_sources_business) == "high"
        assert service._assess_source_reliability(two_sources_business) == "medium"
        assert service._assess_source_reliability(single_source_business) == "low"
    
    def test_validate_contact_field(self, service):
        """Test contact field validation."""
        # Test valid phone numbers
        assert service._validate_contact_field("+1-555-123-4567") is True
        assert service._validate_contact_field("(555) 123-4567") is True
        assert service._validate_contact_field("5551234567") is True
        
        # Test valid emails
        assert service._validate_contact_field("test@example.com") is True
        assert service._validate_contact_field("user.name@domain.co.uk") is True
        
        # Test valid websites
        assert service._validate_contact_field("https://example.com") is True
        assert service._validate_contact_field("http://www.example.org") is True
        assert service._validate_contact_field("www.example.net") is True
        
        # Test invalid fields
        assert service._validate_contact_field("invalid") is False
        assert service._validate_contact_field("test@") is False
        assert service._validate_contact_field("http://") is False
    
    def test_error_handling(self, service):
        """Test error handling in confidence calculations."""
        # Test with invalid data that would cause errors
        invalid_data = Mock()
        invalid_data.name = None
        invalid_data.location = None
        invalid_data.contact_info = None
        invalid_data.rating = None
        invalid_data.categories = None
        invalid_data.hours = None
        invalid_data.source = "test"
        
        # Should handle errors gracefully and return 0.0
        confidence = service.calculate_data_confidence(invalid_data)
        assert confidence == 0.0
    
    def test_logging_integration(self, service, sample_business_data):
        """Test that logging is properly integrated."""
        with patch.object(service.logger, 'debug') as mock_debug:
            service.calculate_data_confidence(sample_business_data)
            mock_debug.assert_called()
    
    def test_performance_with_large_datasets(self, service):
        """Test performance with larger datasets."""
        # Create multiple business records
        businesses = []
        for i in range(100):
            business = BusinessSourceData(
                source=f"source_{i}",
                source_id=f"id_{i}",
                name=f"Business {i}",
                location=BusinessLocation(
                    latitude=40.0 + (i * 0.001),
                    longitude=-74.0 + (i * 0.001)
                ),
                contact_info=None,
                rating=4.0,
                review_count=50,
                categories=["Category"],
                price_level=2,
                hours={},
                photos=[],
                raw_data={},
                last_updated="2024-01-01T00:00:00Z"
            )
            businesses.append(business)
        
        # Test performance of confidence calculation
        start_time = datetime.now()
        for business in businesses:
            service.calculate_data_confidence(business)
        end_time = datetime.now()
        
        # Should complete within reasonable time (less than 1 second for 100 records)
        duration = (end_time - start_time).total_seconds()
        assert duration < 1.0
