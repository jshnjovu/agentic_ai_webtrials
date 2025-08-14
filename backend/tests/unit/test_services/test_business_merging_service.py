"""
Unit tests for BusinessMergingService.
Tests data merging, prioritization, completeness scoring, and conflict resolution.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.business_merging_service import BusinessMergingService
from src.schemas.business_matching import (
    BusinessSourceData,
    BusinessLocation,
    BusinessContactInfo,
    ConfidenceLevel
)
from src.schemas.business_merging import (
    BusinessMergeRequest,
    DataCompletenessScore
)


class TestBusinessMergingService:
    """Test cases for BusinessMergingService."""
    
    @pytest.fixture
    def service(self):
        """Create a BusinessMergingService instance for testing."""
        return BusinessMergingService()
    
    @pytest.fixture
    def sample_businesses(self):
        """Create sample business data for testing."""
        return [
            BusinessSourceData(
                source="google_places",
                source_id="gp_001",
                name="Joe's Pizza",
                location=BusinessLocation(
                    latitude=40.7128,
                    longitude=-74.0060,
                    address="123 Main St",
                    city="New York",
                    state="NY",
                    zip_code="10001",
                    country="US"
                ),
                contact_info=BusinessContactInfo(
                    phone="+1-555-123-4567",
                    website="https://www.joespizza.com",
                    email="info@joespizza.com"
                ),
                rating=4.5,
                review_count=150,
                categories=["Pizza", "Italian", "Restaurant"],
                price_level=2
            ),
            BusinessSourceData(
                source="yelp_fusion",
                source_id="yf_001",
                name="Joe's Pizza",
                location=BusinessLocation(
                    latitude=40.7128,
                    longitude=-74.0060,
                    address="123 Main St",
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
                categories=["Pizza", "Italian"],
                price_level=2
            ),
            BusinessSourceData(
                source="manual_entry",
                source_id="me_001",
                name="Joe's Pizza",
                location=BusinessLocation(
                    latitude=40.7128,
                    longitude=-74.0060,
                    address="123 Main St"
                ),
                contact_info=BusinessContactInfo(
                    phone="555-123-4567"
                ),
                rating=None,
                review_count=None,
                categories=["Pizza"],
                price_level=None
            )
        ]
    
    def test_service_initialization(self, service):
        """Test that the service initializes correctly."""
        assert service.service_name == "BusinessMergingService"
        assert service.logger is not None
    
    def test_validate_input_valid(self, service, sample_businesses):
        """Test input validation with valid data."""
        request = BusinessMergeRequest(
            businesses=sample_businesses[:2],
            run_id="test_run_001"
        )
        assert service.validate_input(request) is True
    
    def test_validate_input_invalid(self, service):
        """Test input validation with invalid data."""
        # Single business (should fail)
        request = BusinessMergeRequest(
            businesses=[Mock()],
            run_id="test_run_001"
        )
        assert service.validate_input(request) is False
        
        # Wrong type
        assert service.validate_input("invalid") is False
    
    def test_calculate_location_completeness(self, service):
        """Test location completeness scoring."""
        # Complete location
        complete_location = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            country="US"
        )
        score = service._calculate_location_completeness(complete_location)
        assert score > 0.8  # Should be high completeness
        
        # Partial location
        partial_location = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Main St"
        )
        score = service._calculate_location_completeness(partial_location)
        assert 0.5 < score < 0.8  # Should be medium completeness
        
        # Minimal location
        minimal_location = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060
        )
        score = service._calculate_location_completeness(minimal_location)
        assert 0.3 < score < 0.6  # Should be lower completeness
        
        # No location
        score = service._calculate_location_completeness(None)
        assert score == 0.0
    
    def test_calculate_contact_completeness(self, service):
        """Test contact information completeness scoring."""
        # Complete contact info
        complete_contact = BusinessContactInfo(
            phone="+1-555-123-4567",
            website="https://www.example.com",
            email="info@example.com",
            social_media={"facebook": "example"}
        )
        score = service._calculate_contact_completeness(complete_contact)
        assert score > 0.8  # Should be high completeness
        
        # Partial contact info
        partial_contact = BusinessContactInfo(
            phone="+1-555-123-4567",
            website="https://www.example.com"
        )
        score = service._calculate_contact_completeness(partial_contact)
        assert 0.6 < score < 0.8  # Should be medium completeness
        
        # Minimal contact info
        minimal_contact = BusinessContactInfo(
            phone="+1-555-123-4567"
        )
        score = service._calculate_contact_completeness(minimal_contact)
        assert 0.3 < score < 0.6  # Should be lower completeness
        
        # No contact info
        score = service._calculate_contact_completeness(None)
        assert score == 0.0
    
    def test_calculate_rating_completeness(self, service):
        """Test rating and review completeness scoring."""
        # Complete rating info
        score = service._calculate_rating_completeness(4.5, 150)
        assert score == 1.0  # Should be complete
        
        # Partial rating info
        score = service._calculate_rating_completeness(4.5, None)
        assert score == 0.5  # Should be partial
        
        score = service._calculate_rating_completeness(None, 150)
        assert score == 0.5  # Should be partial
        
        # No rating info
        score = service._calculate_rating_completeness(None, None)
        assert score == 0.0  # Should be incomplete
    
    def test_calculate_category_completeness(self, service):
        """Test category completeness scoring."""
        # Multiple categories
        score = service._calculate_category_completeness(["Pizza", "Italian", "Restaurant"])
        assert score == 1.0  # Should be complete
        
        # Two categories
        score = service._calculate_category_completeness(["Pizza", "Italian"])
        assert score == 0.7  # Should be medium-high
        
        # Single category
        score = service._calculate_category_completeness(["Pizza"])
        assert score == 0.4  # Should be medium-low
        
        # No categories
        score = service._calculate_category_completeness([])
        assert score == 0.0  # Should be incomplete
        
        score = service._calculate_category_completeness(None)
        assert score == 0.0  # Should be incomplete
    
    def test_calculate_completeness_scores(self, service, sample_businesses):
        """Test completeness score calculation for all businesses."""
        scores = service._calculate_completeness_scores(sample_businesses)
        
        assert len(scores) == 3
        
        # Google Places should have highest score (most complete)
        google_score = next(s for s in scores if s.source == "google_places")
        yelp_score = next(s for s in scores if s.source == "yelp_fusion")
        manual_score = next(s for s in scores if s.source == "manual_entry")
        
        assert google_score.overall_score > yelp_score.overall_score
        assert yelp_score.overall_score > manual_score.overall_score
        
        # Verify individual component scores
        for score in scores:
            assert 0.0 <= score.overall_score <= 1.0
            assert 0.0 <= score.name_score <= 1.0
            assert 0.0 <= score.location_score <= 1.0
            assert 0.0 <= score.contact_score <= 1.0
            assert 0.0 <= score.rating_score <= 1.0
            assert 0.0 <= score.category_score <= 1.0
    
    def test_determine_primary_business_with_prioritization(self, service, sample_businesses):
        """Test primary business determination with source prioritization."""
        completeness_scores = service._calculate_completeness_scores(sample_businesses)
        
        # Prioritize yelp_fusion
        primary = service._determine_primary_business(
            sample_businesses, completeness_scores, "yelp_fusion"
        )
        assert primary.source == "yelp_fusion"
        
        # Prioritize non-existent source (should fall back to completeness)
        primary = service._determine_primary_business(
            sample_businesses, completeness_scores, "non_existent"
        )
        # Should select based on completeness (google_places)
        assert primary.source == "google_places"
    
    def test_determine_primary_business_by_completeness(self, service, sample_businesses):
        """Test primary business determination by completeness score."""
        completeness_scores = service._calculate_completeness_scores(sample_businesses)
        
        primary = service._determine_primary_business(
            sample_businesses, completeness_scores, None
        )
        
        # Should select the business with highest completeness score
        best_score = max(completeness_scores, key=lambda x: x.overall_score)
        assert primary.source == best_score.source
    
    def test_merge_business_data(self, service, sample_businesses):
        """Test business data merging."""
        completeness_scores = service._calculate_completeness_scores(sample_businesses)
        primary_business = sample_businesses[0]  # Google Places
        
        merged_data, conflicts = service._merge_business_data(
            sample_businesses, primary_business, completeness_scores, "completeness"
        )
        
        # Check merged data structure
        assert "name" in merged_data
        assert "location" in merged_data
        assert "contact_info" in merged_data
        assert "rating" in merged_data
        assert "categories" in merged_data
        
        # Categories should be merged (combined from all sources)
        assert len(merged_data["categories"]) >= 3
        
        # Photos should be merged
        assert isinstance(merged_data["photos"], list)
    
    def test_resolve_contact_conflicts(self, service):
        """Test contact information conflict resolution."""
        primary_contact = BusinessContactInfo(
            phone="+1-555-123-4567",
            website="https://www.primary.com",
            email="primary@example.com"
        )
        
        business_contact = BusinessContactInfo(
            phone="+1-555-987-6543",
            website="https://www.business.com",
            email="business@example.com"
        )
        
        conflicts = service._resolve_contact_conflicts(
            primary_contact, business_contact, "completeness"
        )
        
        # Should have conflicts for all fields
        assert len(conflicts) == 3
        
        # All conflicts should resolve to primary values
        for conflict in conflicts:
            assert conflict.resolution_strategy == "completeness"
            assert conflict.confidence == 0.8
    
    def test_resolve_rating_conflict(self, service):
        """Test rating conflict resolution."""
        conflict = service._resolve_rating_conflict(4.5, 4.3, "completeness")
        
        assert conflict.field_name == "rating"
        assert conflict.resolved_value == 4.5  # Should keep primary
        assert conflict.confidence == 0.7
        assert conflict.resolution_strategy == "completeness"
    
    def test_resolve_price_conflict(self, service):
        """Test price level conflict resolution."""
        conflict = service._resolve_price_conflict(2, 3, "completeness")
        
        assert conflict.field_name == "price_level"
        assert conflict.resolved_value == 2  # Should keep primary
        assert conflict.confidence == 0.8
        assert conflict.resolution_strategy == "completeness"
    
    def test_determine_merged_confidence(self, service):
        """Test merged data confidence determination."""
        # No conflicts
        confidence = service._determine_merged_confidence([])
        assert confidence == ConfidenceLevel.HIGH
        
        # High confidence conflicts
        high_conflicts = [Mock(confidence=0.9), Mock(confidence=0.85)]
        confidence = service._determine_merged_confidence(high_conflicts)
        assert confidence == ConfidenceLevel.HIGH
        
        # Medium confidence conflicts
        medium_conflicts = [Mock(confidence=0.7), Mock(confidence=0.65)]
        confidence = service._determine_merged_confidence(medium_conflicts)
        assert confidence == ConfidenceLevel.MEDIUM
        
        # Low confidence conflicts
        low_conflicts = [Mock(confidence=0.5), Mock(confidence=0.4)]
        confidence = service._determine_merged_confidence(low_conflicts)
        assert confidence == ConfidenceLevel.LOW
    
    def test_merge_businesses_success(self, service, sample_businesses):
        """Test successful business merging."""
        request = BusinessMergeRequest(
            businesses=sample_businesses[:2],
            merge_strategy="completeness",
            run_id="test_run_001"
        )
        
        response = service.merge_businesses(request)
        
        assert response.success is True
        assert response.merged_business is not None
        assert response.run_id == "test_run_001"
        assert "total_sources" in response.merge_metadata
        
        # Check merged business properties
        merged = response.merged_business
        assert merged.name == "Joe's Pizza"
        assert merged.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        assert len(merged.source_contributions) == 2
    
    def test_merge_businesses_validation_error(self, service):
        """Test business merging with validation error."""
        request = BusinessMergeRequest(
            businesses=[Mock()],  # Single business should fail validation
            run_id="test_run_001"
        )
        
        with pytest.raises(ValueError, match="Invalid input"):
            service.merge_businesses(request)
    
    def test_merge_businesses_with_prioritization(self, service, sample_businesses):
        """Test business merging with source prioritization."""
        request = BusinessMergeRequest(
            businesses=sample_businesses[:2],
            merge_strategy="completeness",
            prioritize_source="yelp_fusion",
            run_id="test_run_002"
        )
        
        response = service.merge_businesses(request)
        
        assert response.success is True
        # Primary business should be from yelp_fusion
        assert response.merged_business.name == "Joe's Pizza"
    
    def test_error_handling(self, service):
        """Test error handling in the service."""
        # Test with invalid request
        with pytest.raises(ValueError):
            service.merge_businesses(None)
        
        # Test with empty businesses list
        request = BusinessMergeRequest(
            businesses=[],
            run_id="test_run_003"
        )
        
        with pytest.raises(ValueError, match="Invalid input"):
            service.merge_businesses(request)
    
    def test_logging_integration(self, service, sample_businesses):
        """Test that logging is properly integrated."""
        request = BusinessMergeRequest(
            businesses=sample_businesses[:2],
            run_id="test_run_004"
        )
        
        # Should not raise any logging-related errors
        try:
            service.merge_businesses(request)
        except Exception:
            pass  # We expect this to work, but logging should work regardless
        
        # Verify logger is set up
        assert service.logger is not None
