"""
Tests for the review management service.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.review_management_service import ReviewManagementService
from src.schemas.business_matching import BusinessSourceData, BusinessLocation, ConfidenceLevel
from src.schemas.business_merging import MergedBusinessData, MergeConflict
from src.schemas.review_management import ReviewStatus, ReviewPriority, ReviewFlag, ReviewWorkflow


class TestReviewManagementService:
    """Test cases for ReviewManagementService."""
    
    @pytest.fixture
    def service(self):
        """Create a review management service instance."""
        return ReviewManagementService()
    
    @pytest.fixture
    def sample_merged_business(self):
        """Create sample merged business data for testing."""
        return MergedBusinessData(
            business_id="test_business_id",
            name="Test Business",
            location=BusinessLocation(
                latitude=40.7128,
                longitude=-74.0060,
                address="123 Test Street",
                city="New York",
                state="NY",
                zip_code="10001"
            ),
            contact_info=None,
            rating=4.0,
            review_count=50,
            categories=["Restaurant"],
            price_level=2,
            hours={},
            photos=[],
            confidence_level=ConfidenceLevel.MEDIUM,
            source_contributions=["google_places", "yelp_fusion"],
            merge_metadata={},
            last_updated="2024-01-01T00:00:00Z",
            needs_review=False
        )
    
    @pytest.fixture
    def sample_conflicts(self):
        """Create sample conflicts for testing."""
        return [
            MergeConflict(
                field_name="phone",
                source_values={"google": "+1-555-123-4567", "yelp": "+1-555-123-4568"},
                resolution_strategy="completeness",
                resolved_value="+1-555-123-4567",
                confidence=0.6
            ),
            MergeConflict(
                field_name="website",
                source_values={"google": "https://testbusiness.com", "yelp": "https://testbusiness.org"},
                resolution_strategy="completeness",
                resolved_value="https://testbusiness.com",
                confidence=0.5
            )
        ]
    
    @pytest.fixture
    def sample_source_data(self):
        """Create sample source data for testing."""
        return [
            BusinessSourceData(
                source="google_places",
                source_id="google_id",
                name="Test Business",
                location=BusinessLocation(),
                contact_info=None,
                rating=4.0,
                review_count=50,
                categories=["Restaurant"],
                price_level=2,
                hours={},
                photos=[],
                raw_data={},
                last_updated="2024-01-01T00:00:00Z"
            ),
            BusinessSourceData(
                source="yelp_fusion",
                source_id="yelp_id",
                name="Test Business",
                location=BusinessLocation(),
                contact_info=None,
                rating=4.0,
                review_count=50,
                categories=["Restaurant"],
                price_level=2,
                hours={},
                photos=[],
                raw_data={},
                last_updated="2024-01-01T00:00:00Z"
            )
        ]
    
    def test_validate_input(self, service):
        """Test input validation."""
        assert service.validate_input("test") is True
        assert service.validate_input(None) is False
    
    def test_flag_uncertain_matches_low_confidence(self, service, sample_merged_business, sample_conflicts, sample_source_data):
        """Test flagging uncertain matches with low confidence."""
        # Set low confidence
        sample_merged_business.confidence_level = ConfidenceLevel.LOW
        
        flag = service.flag_uncertain_matches(sample_merged_business, sample_conflicts, sample_source_data)
        
        assert flag is not None
        assert flag.business_id == "test_business_id"
        assert flag.flag_type == "low_confidence"
        assert flag.priority == ReviewPriority.HIGH
        assert flag.status == ReviewStatus.PENDING
        assert "Low confidence" in flag.reason
        assert flag.confidence_score == 0.4  # LOW confidence level score
    
    def test_flag_uncertain_matches_with_conflicts(self, service, sample_merged_business, sample_conflicts, sample_source_data):
        """Test flagging uncertain matches with low confidence conflicts."""
        # Set medium confidence but low conflict confidence
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        
        flag = service.flag_uncertain_matches(sample_merged_business, sample_conflicts, sample_source_data)
        
        assert flag is not None
        assert flag.flag_type == "data_conflict"
        # With 2 low-confidence conflicts (0.5 < 0.7 threshold), should get HIGH priority
        assert flag.priority == ReviewPriority.HIGH
        assert "data conflicts detected" in flag.reason
        assert "Critical field conflicts: phone, website" in flag.reason
    
    def test_flag_uncertain_matches_no_flagging_needed(self, service, sample_merged_business, sample_source_data):
        """Test that no flagging occurs when confidence is high and no conflicts."""
        # Set high confidence and no conflicts
        sample_merged_business.confidence_level = ConfidenceLevel.HIGH
        
        flag = service.flag_uncertain_matches(sample_merged_business, [], sample_source_data)
        
        assert flag is None
    
    def test_flag_uncertain_matches_high_confidence_conflicts(self, service, sample_merged_business, sample_source_data):
        """Test flagging with high confidence conflicts."""
        # Create high confidence conflicts
        high_confidence_conflicts = [
            MergeConflict(
                field_name="phone",
                source_values={"google": "+1-555-123-4567", "yelp": "+1-555-123-4568"},
                resolution_strategy="completeness",
                resolved_value="+1-555-123-4567",
                confidence=0.8
            )
        ]
        
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        
        flag = service.flag_uncertain_matches(sample_merged_business, high_confidence_conflicts, sample_source_data)
        
        # Should NOT flag due to high confidence conflicts (0.8) with medium business confidence
        assert flag is None
    
    def test_create_review_workflow(self, service):
        """Test review workflow creation."""
        review_flag = ReviewFlag(
            flag_id="test_flag_id",
            business_id="test_business_id",
            flag_type="data_conflict",
            priority=ReviewPriority.HIGH,
            status=ReviewStatus.PENDING,
            reason="Test reason",
            confidence_score=0.6,
            source_data=[],
            conflicts=[],
            created_at="2024-01-01T00:00:00Z",
            run_id="test_run"
        )
        
        workflow_steps = service.create_review_workflow(review_flag)
        
        assert len(workflow_steps) == 4  # Should have 4 workflow steps
        assert workflow_steps[0].step_name == "initial_assessment"
        assert workflow_steps[1].step_name == "data_verification"
        assert workflow_steps[2].step_name == "conflict_resolution"
        assert workflow_steps[3].step_name == "final_approval"
        
        # Check workflow step properties
        for i, step in enumerate(workflow_steps, 1):
            assert step.flag_id == "test_flag_id"
            assert step.step_number == i
            assert step.status == "pending"
            assert step.created_at is not None
    
    def test_assign_review(self, service):
        """Test review assignment."""
        review_flag = ReviewFlag(
            flag_id="test_flag_id",
            business_id="test_business_id",
            flag_type="data_conflict",
            priority=ReviewPriority.HIGH,
            status=ReviewStatus.PENDING,
            reason="Test reason",
            confidence_score=0.6,
            source_data=[],
            conflicts=[],
            created_at="2024-01-01T00:00:00Z",
            run_id="test_run"
        )
        
        success = service.assign_review(review_flag, "user123")
        
        assert success is True
        assert review_flag.assigned_to == "user123"
        assert review_flag.assigned_at is not None
        assert review_flag.status == ReviewStatus.IN_REVIEW
    
    def test_assign_review_invalid_input(self, service):
        """Test review assignment with invalid input."""
        success = service.assign_review(None, "user123")
        assert success is False
        
        success = service.assign_review(Mock(), "")
        assert success is False
    
    def test_update_review_status(self, service):
        """Test review status update."""
        review_flag = ReviewFlag(
            flag_id="test_flag_id",
            business_id="test_business_id",
            flag_type="data_conflict",
            priority=ReviewPriority.HIGH,
            status=ReviewStatus.IN_REVIEW,
            reason="Test reason",
            confidence_score=0.6,
            source_data=[],
            conflicts=[],
            created_at="2024-01-01T00:00:00Z",
            assigned_to="user123",
            assigned_at="2024-01-01T00:00:00Z",
            run_id="test_run"
        )
        
        success = service.update_review_status(
            review_flag, 
            ReviewStatus.APPROVED,
            "Looks good to me",
            "Approved after verification"
        )
        
        assert success is True
        assert review_flag.status == ReviewStatus.APPROVED
        assert review_flag.review_notes == "Looks good to me"
        assert review_flag.resolution == "Approved after verification"
        assert review_flag.reviewed_at is not None
    
    def test_update_review_status_invalid_input(self, service):
        """Test review status update with invalid input."""
        success = service.update_review_status(None, ReviewStatus.APPROVED)
        assert success is False
    
    def test_get_pending_reviews(self, service):
        """Test getting pending reviews."""
        reviews = service.get_pending_reviews()
        
        # Should return empty list for now (placeholder implementation)
        assert isinstance(reviews, list)
        assert len(reviews) == 0
    
    def test_get_pending_reviews_with_filters(self, service):
        """Test getting pending reviews with filters."""
        # Test with priority filter
        reviews = service.get_pending_reviews(priority=ReviewPriority.HIGH)
        assert isinstance(reviews, list)
        
        # Test with assigned_to filter
        reviews = service.get_pending_reviews(assigned_to="user123")
        assert isinstance(reviews, list)
    
    def test_resolve_review_flag(self, service):
        """Test review flag resolution."""
        review_flag = ReviewFlag(
            flag_id="test_flag_id",
            business_id="test_business_id",
            flag_type="data_conflict",
            priority=ReviewPriority.HIGH,
            status=ReviewStatus.IN_REVIEW,
            reason="Test reason",
            confidence_score=0.6,
            source_data=[],
            conflicts=[],
            created_at="2024-01-01T00:00:00Z",
            assigned_to="user123",
            assigned_at="2024-01-01T00:00:00Z",
            run_id="test_run"
        )
        
        success = service.resolve_review_flag(
            review_flag,
            "merge_confirmed",
            "Confirmed as same business, merged successfully"
        )
        
        assert success is True
        assert review_flag.status == ReviewStatus.RESOLVED
        assert review_flag.resolution == "merge_confirmed"
        assert review_flag.review_notes == "Confirmed as same business, merged successfully"
        assert review_flag.reviewed_at is not None
    
    def test_resolve_review_flag_invalid_input(self, service):
        """Test review flag resolution with invalid input."""
        success = service.resolve_review_flag(None, "action", "notes")
        assert success is False
    
    def test_should_flag_for_review_low_confidence(self, service, sample_merged_business):
        """Test review flagging decision for low confidence."""
        sample_merged_business.confidence_level = ConfidenceLevel.LOW
        
        should_flag = service._should_flag_for_review(sample_merged_business, [])
        assert should_flag is True
    
    def test_should_flag_for_review_low_confidence_conflicts(self, service, sample_merged_business, sample_conflicts):
        """Test review flagging decision for low confidence conflicts."""
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        
        should_flag = service._should_flag_for_review(sample_merged_business, sample_conflicts)
        assert should_flag is True
    
    def test_should_flag_for_review_high_confidence_conflicts(self, service, sample_merged_business):
        """Test review flagging decision for high confidence conflicts."""
        high_confidence_conflicts = [
            MergeConflict(
                field_name="phone",
                source_values={"google": "+1-555-123-4567", "yelp": "+1-555-123-4568"},
                resolution_strategy="completeness",
                resolved_value="+1-555-123-4567",
                confidence=0.8
            )
        ]
        
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        
        should_flag = service._should_flag_for_review(sample_merged_business, high_confidence_conflicts)
        assert should_flag is False  # Should NOT flag due to high confidence conflicts (0.8 >= 0.7 threshold)
    
    def test_should_flag_for_review_needs_review_flag(self, service, sample_merged_business):
        """Test review flagging decision when business already marked for review."""
        sample_merged_business.needs_review = True
        
        should_flag = service._should_flag_for_review(sample_merged_business, [])
        assert should_flag is True
    
    def test_determine_flag_type(self, service, sample_merged_business, sample_conflicts):
        """Test flag type determination."""
        # Test low confidence
        sample_merged_business.confidence_level = ConfidenceLevel.LOW
        flag_type = service._determine_flag_type(sample_merged_business, [])
        assert flag_type == "low_confidence"
        
        # Test data conflict
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        flag_type = service._determine_flag_type(sample_merged_business, sample_conflicts)
        assert flag_type == "data_conflict"
        
        # Test manual review required
        sample_merged_business.needs_review = True
        flag_type = service._determine_flag_type(sample_merged_business, [])
        assert flag_type == "manual_review_required"
        
        # Test uncertain match
        sample_merged_business.needs_review = False
        flag_type = service._determine_flag_type(sample_merged_business, [])
        assert flag_type == "uncertain_match"
    
    def test_determine_priority(self, service, sample_merged_business, sample_conflicts):
        """Test priority determination."""
        # Test high priority for low confidence
        sample_merged_business.confidence_level = ConfidenceLevel.LOW
        priority = service._determine_priority(sample_merged_business, [])
        assert priority == ReviewPriority.HIGH
        
        # Test high priority for many conflicts (4 conflicts > 3 threshold)
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        many_conflicts = [Mock() for _ in range(4)]  # More than 3 conflicts
        priority = service._determine_priority(sample_merged_business, many_conflicts)
        assert priority == ReviewPriority.HIGH
        
        # Test HIGH priority for medium confidence with low confidence conflicts (0.5 < 0.7 threshold)
        priority = service._determine_priority(sample_merged_business, sample_conflicts)
        assert priority == ReviewPriority.HIGH
        
        # Test low priority for high confidence with no conflicts
        sample_merged_business.confidence_level = ConfidenceLevel.HIGH
        priority = service._determine_priority(sample_merged_business, [])
        assert priority == ReviewPriority.LOW
    
    def test_generate_flag_reason(self, service, sample_merged_business, sample_conflicts):
        """Test flag reason generation."""
        # Test low confidence reason
        sample_merged_business.confidence_level = ConfidenceLevel.LOW
        reason = service._generate_flag_reason(sample_merged_business, [])
        assert "Low confidence" in reason
        
        # Test conflicts reason
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        reason = service._generate_flag_reason(sample_merged_business, sample_conflicts)
        assert "data conflicts detected" in reason
        
        # Test manual review reason
        sample_merged_business.needs_review = True
        reason = service._generate_flag_reason(sample_merged_business, [])
        assert "Manual review required" in reason
        
        # Test uncertain match reason
        sample_merged_business.needs_review = False
        sample_merged_business.confidence_level = ConfidenceLevel.HIGH
        reason = service._generate_flag_reason(sample_merged_business, [])
        assert "Uncertain match" in reason
    
    def test_confidence_level_to_score(self, service):
        """Test confidence level to score conversion."""
        assert service._confidence_level_to_score(ConfidenceLevel.HIGH) == 0.9
        assert service._confidence_level_to_score(ConfidenceLevel.MEDIUM) == 0.7
        assert service._confidence_level_to_score(ConfidenceLevel.LOW) == 0.4
    
    def test_error_handling(self, service):
        """Test error handling in service methods."""
        # Test with invalid data that would cause errors
        invalid_business = Mock()
        invalid_business.confidence_level = None
        invalid_business.needs_review = None
        
        # Should handle errors gracefully
        flag = service.flag_uncertain_matches(invalid_business, [], [])
        assert flag is None
    
    def test_logging_integration(self, service, sample_merged_business, sample_conflicts, sample_source_data):
        """Test that logging is properly integrated."""
        with patch.object(service.logger, 'info') as mock_info:
            service.flag_uncertain_matches(sample_merged_business, sample_conflicts, sample_source_data)
            mock_info.assert_called()
    
    def test_workflow_step_creation(self, service):
        """Test that workflow steps are created with proper structure."""
        review_flag = ReviewFlag(
            flag_id="test_flag_id",
            business_id="test_business_id",
            flag_type="data_conflict",
            priority=ReviewPriority.HIGH,
            status=ReviewStatus.PENDING,
            reason="Test reason",
            confidence_score=0.6,
            source_data=[],
            conflicts=[],
            created_at="2024-01-01T00:00:00Z",
            run_id="test_run"
        )
        
        workflow_steps = service.create_review_workflow(review_flag)
        
        # Verify each step has required fields
        for step in workflow_steps:
            assert hasattr(step, 'workflow_id')
            assert hasattr(step, 'flag_id')
            assert hasattr(step, 'step_number')
            assert hasattr(step, 'step_name')
            assert hasattr(step, 'status')
            assert hasattr(step, 'created_at')
    
    def test_review_flag_properties(self, service, sample_merged_business, sample_conflicts, sample_source_data):
        """Test that review flags have all required properties."""
        sample_merged_business.confidence_level = ConfidenceLevel.LOW
        
        flag = service.flag_uncertain_matches(sample_merged_business, sample_conflicts, sample_source_data)
        
        assert flag is not None
        assert hasattr(flag, 'flag_id')
        assert hasattr(flag, 'business_id')
        assert hasattr(flag, 'flag_type')
        assert hasattr(flag, 'priority')
        assert hasattr(flag, 'status')
        assert hasattr(flag, 'reason')
        assert hasattr(flag, 'confidence_score')
        assert hasattr(flag, 'source_data')
        assert hasattr(flag, 'conflicts')
        assert hasattr(flag, 'created_at')
        assert hasattr(flag, 'run_id')
    
    def test_review_workflow_sequence(self, service):
        """Test that workflow steps are created in correct sequence."""
        review_flag = ReviewFlag(
            flag_id="test_flag_id",
            business_id="test_business_id",
            flag_type="data_conflict",
            priority=ReviewPriority.HIGH,
            status=ReviewStatus.PENDING,
            reason="Test reason",
            confidence_score=0.6,
            source_data=[],
            conflicts=[],
            created_at="2024-01-01T00:00:00Z",
            run_id="test_run"
        )
        
        workflow_steps = service.create_review_workflow(review_flag)
        
        # Verify step sequence
        expected_steps = ["initial_assessment", "data_verification", "conflict_resolution", "final_approval"]
        for i, step in enumerate(workflow_steps):
            assert step.step_name == expected_steps[i]
            assert step.step_number == i + 1

    def test_hybrid_scoring_system(self, service, sample_merged_business, sample_source_data):
        """Test the hybrid scoring system with various conflict scenarios."""
        # Test 1: Single high-confidence conflict (0.9) with medium business confidence → NOT flagged
        single_high_conflict = [
            MergeConflict(
                field_name="rating",
                source_values={"google": "4.5", "yelp": "4.6"},
                resolution_strategy="accuracy",
                resolved_value="4.5",
                confidence=0.9
            )
        ]
        
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        flag = service.flag_uncertain_matches(sample_merged_business, single_high_conflict, sample_source_data)
        
        # Should NOT flag due to high confidence conflicts (0.9 > 0.7 threshold)
        assert flag is None
        
        # Test 2: Multiple low-confidence conflicts with high business confidence
        multiple_low_conflicts = [
            MergeConflict(
                field_name="phone",
                source_values={"google": "+1-555-123-4567", "yelp": "+1-555-123-4568"},
                resolution_strategy="completeness",
                resolved_value="+1-555-123-4567",
                confidence=0.4
            ),
            MergeConflict(
                field_name="website",
                source_values={"google": "https://test.com", "yelp": "https://test.org"},
                resolution_strategy="completeness",
                resolved_value="https://test.com",
                confidence=0.3
            )
        ]
        
        sample_merged_business.confidence_level = ConfidenceLevel.HIGH
        flag = service.flag_uncertain_matches(sample_merged_business, multiple_low_conflicts, sample_source_data)
        
        # Should flag with HIGH priority due to multiple low-confidence conflicts
        assert flag is not None
        assert flag.priority == ReviewPriority.HIGH
        assert "2 low-confidence data conflicts detected" in flag.reason
        assert "Critical field conflicts: phone, website" in flag.reason
    
    def test_field_importance_weighting(self, service, sample_merged_business, sample_source_data):
        """Test that field importance affects priority scoring."""
        # Create conflicts with different field importance
        critical_field_conflicts = [
            MergeConflict(
                field_name="name",  # Most critical field
                source_values={"google": "Test Business", "yelp": "Test Business Inc"},
                resolution_strategy="accuracy",
                resolved_value="Test Business",
                confidence=0.7
            ),
            MergeConflict(
                field_name="hours",  # Less critical field
                source_values={"google": "9-5", "yelp": "9:00-17:00"},
                resolution_strategy="completeness",
                resolved_value="9-5",
                confidence=0.7
            )
        ]
        
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        flag = service.flag_uncertain_matches(sample_merged_business, critical_field_conflicts, sample_source_data)
        
        # Should NOT flag due to high confidence conflicts (0.7 >= 0.7 threshold)
        assert flag is None
    
    def test_resolution_strategy_weighting(self, service, sample_merged_business, sample_source_data):
        """Test that resolution strategy affects complexity scoring."""
        # Create conflicts with different resolution strategies
        complex_resolution_conflicts = [
            MergeConflict(
                field_name="phone",
                source_values={"google": "+1-555-123-4567", "yelp": "+1-555-123-4568"},
                resolution_strategy="manual",  # Highest complexity
                resolved_value="+1-555-123-4567",
                confidence=0.6
            ),
            MergeConflict(
                field_name="website",
                source_values={"google": "https://test.com", "yelp": "https://test.org"},
                resolution_strategy="completeness",  # Medium complexity
                resolved_value="https://test.com",
                confidence=0.6
            )
        ]
        
        sample_merged_business.confidence_level = ConfidenceLevel.MEDIUM
        flag = service.flag_uncertain_matches(sample_merged_business, complex_resolution_conflicts, sample_source_data)
        
        # Should flag with HIGH priority due to low confidence conflicts (0.6 < 0.7 threshold)
        assert flag is not None
        assert flag.priority == ReviewPriority.HIGH
        # Check for key elements in the reason, format may vary
        assert "Medium confidence requiring validation" in flag.reason
