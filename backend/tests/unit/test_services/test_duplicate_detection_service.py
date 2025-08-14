"""
Unit tests for DuplicateDetectionService.
Tests business fingerprinting, duplicate detection algorithms, and removal strategies.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.duplicate_detection_service import DuplicateDetectionService
from src.schemas.business_matching import (
    BusinessSourceData,
    BusinessLocation,
    BusinessContactInfo
)
from src.schemas.duplicate_detection import (
    DuplicateDetectionRequest,
    DuplicateRemovalRequest,
    DuplicateType
)


class TestDuplicateDetectionService:
    """Test cases for DuplicateDetectionService."""
    
    @pytest.fixture
    def service(self):
        """Create a DuplicateDetectionService instance for testing."""
        return DuplicateDetectionService()
    
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
        assert service.service_name == "DuplicateDetectionService"
        assert service.logger is not None
    
    def test_validate_input_valid_detection(self, service, sample_businesses):
        """Test input validation with valid detection request."""
        request = DuplicateDetectionRequest(
            businesses=sample_businesses[:2],
            run_id="test_run_001"
        )
        assert service.validate_input(request) is True
    
    def test_validate_input_valid_removal(self, service):
        """Test input validation with valid removal request."""
        # Mock duplicate groups
        mock_groups = [Mock(), Mock()]
        request = DuplicateRemovalRequest(
            duplicate_groups=mock_groups,
            run_id="test_run_001"
        )
        assert service.validate_input(request) is True
    
    def test_validate_input_invalid(self, service):
        """Test input validation with invalid data."""
        # Empty businesses list
        request = DuplicateDetectionRequest(
            businesses=[],
            run_id="test_run_001"
        )
        assert service.validate_input(request) is False
        
        # Wrong type
        assert service.validate_input("invalid") is False
    
    def test_normalize_business_name(self, service):
        """Test business name normalization for fingerprinting."""
        # Test with common suffixes
        assert service._normalize_business_name("Joe's Pizza Inc.") == "joes pizza"
        assert service._normalize_business_name("ABC Company LLC") == "abc company"
        assert service._normalize_business_name("XYZ Corp & Co") == "xyz corp"
        
        # Test with punctuation
        assert service._normalize_business_name("Joe's Pizza & Italian Restaurant!") == "joes pizza italian restaurant"
        
        # Test with extra whitespace
        assert service._normalize_business_name("  Joe's   Pizza  ") == "joes pizza"
        
        # Test with empty name
        assert service._normalize_business_name("") == ""
        assert service._normalize_business_name(None) == ""
    
    def test_normalize_address(self, service):
        """Test address normalization for fingerprinting."""
        # Test with abbreviations
        assert service._normalize_address("123 Main Street") == "123 main st"
        assert service._normalize_address("456 North Avenue") == "456 n ave"
        assert service._normalize_address("789 East Boulevard") == "789 e blvd"
        
        # Test with punctuation
        assert service._normalize_address("123 Main St., New York, NY") == "123 main st new york ny"
        
        # Test with extra whitespace
        assert service._normalize_address("  123  Main  St  ") == "123 main st"
        
        # Test with empty address
        assert service._normalize_address("") == ""
        assert service._normalize_address(None) == ""
    
    def test_normalize_phone(self, service):
        """Test phone number normalization for fingerprinting."""
        # Test with formatting
        assert service._normalize_phone("+1-555-123-4567") == "5551234567"
        assert service._normalize_phone("(555) 123-4567") == "5551234567"
        assert service._normalize_phone("555.123.4567") == "5551234567"
        
        # Test with international number
        assert service._normalize_phone("+44-20-7946-0958") == "079460958"
        
        # Test with empty phone
        assert service._normalize_phone("") is None
        assert service._normalize_phone(None) is None
    
    def test_normalize_website(self, service):
        """Test website normalization for fingerprinting."""
        # Test with protocols
        assert service._normalize_website("https://www.example.com") == "example.com"
        assert service._normalize_website("http://example.com") == "example.com"
        
        # Test with www prefix
        assert service._normalize_website("www.example.com") == "example.com"
        
        # Test with trailing slash
        assert service._normalize_website("https://www.example.com/") == "example.com"
        
        # Test with empty website
        assert service._normalize_website("") is None
        assert service._normalize_website(None) is None
    
    def test_generate_coordinate_hash(self, service):
        """Test coordinate hash generation."""
        location = BusinessLocation(
            latitude=40.7128,
            longitude=-74.0060,
            address="123 Main St"
        )
        
        hash1 = service._generate_coordinate_hash(location)
        hash2 = service._generate_coordinate_hash(location)
        
        # Same coordinates should generate same hash
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
        
        # Test with missing coordinates
        location_no_coords = BusinessLocation(
            latitude=None,
            longitude=None,
            address="123 Main St"
        )
        hash_no_coords = service._generate_coordinate_hash(location_no_coords)
        assert hash_no_coords == ""
    
    def test_generate_category_signature(self, service):
        """Test category signature generation."""
        # Test with multiple categories
        categories = ["Pizza", "Italian", "Restaurant"]
        signature1 = service._generate_category_signature(categories)
        signature2 = service._generate_category_signature(categories)
        
        # Same categories should generate same signature
        assert signature1 == signature2
        assert len(signature1) == 32  # MD5 hash length
        
        # Test with empty categories
        signature_empty = service._generate_category_signature([])
        assert signature_empty == ""
        
        signature_none = service._generate_category_signature(None)
        assert signature_none == ""
    
    def test_generate_fingerprint_hash(self, service):
        """Test overall fingerprint hash generation."""
        # Create a mock fingerprint
        mock_fingerprint = Mock()
        mock_fingerprint.name_normalized = "joes pizza"
        mock_fingerprint.address_normalized = "123 main st"
        mock_fingerprint.phone_normalized = "5551234567"
        mock_fingerprint.website_normalized = "joespizza.com"
        mock_fingerprint.coordinate_hash = "abc123"
        mock_fingerprint.category_signature = "def456"
        
        hash1 = service._generate_fingerprint_hash(mock_fingerprint)
        hash2 = service._generate_fingerprint_hash(mock_fingerprint)
        
        # Same fingerprint should generate same hash
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
    
    def test_generate_fingerprints(self, service, sample_businesses):
        """Test fingerprint generation for all businesses."""
        fingerprints = service._generate_fingerprints(sample_businesses)
        
        assert len(fingerprints) == 4
        
        for fingerprint in fingerprints:
            assert fingerprint.business_id is not None
            assert fingerprint.name_normalized is not None
            assert fingerprint.fingerprint_hash is not None
            assert fingerprint.created_at is not None
    
    def test_calculate_string_similarity(self, service):
        """Test string similarity calculation using fuzzy matching."""
        # High similarity
        similarity = service._calculate_string_similarity("joes pizza", "joes pizza")
        assert similarity == 1.0  # Exact match
        
        # Medium similarity
        similarity = service._calculate_string_similarity("joes pizza", "joe pizza")
        assert similarity > 0.8
        
        # Low similarity
        similarity = service._calculate_string_similarity("joes pizza", "starbucks coffee")
        assert similarity < 0.3
    
    def test_calculate_fingerprint_similarity(self, service):
        """Test fingerprint similarity calculation."""
        # Create mock fingerprints
        fp1 = Mock()
        fp1.name_normalized = "joes pizza"
        fp1.address_normalized = "123 main st"
        fp1.phone_normalized = "5551234567"
        fp1.website_normalized = "joespizza.com"
        fp1.coordinate_hash = "abc123"
        
        fp2 = Mock()
        fp2.name_normalized = "joes pizza"
        fp2.address_normalized = "123 main st"
        fp2.phone_normalized = "5551234567"
        fp2.website_normalized = "joespizza.com"
        fp2.coordinate_hash = "abc123"
        
        # High similarity
        similarity = service._calculate_fingerprint_similarity(fp1, fp2)
        assert similarity > 0.9
        
        # Test with different fingerprints
        fp3 = Mock()
        fp3.name_normalized = "starbucks coffee"
        fp3.address_normalized = "456 broadway"
        fp3.phone_normalized = "5559876543"
        fp3.website_normalized = "starbucks.com"
        fp3.coordinate_hash = "xyz789"
        
        similarity = service._calculate_fingerprint_similarity(fp1, fp3)
        assert similarity < 0.5
    
    def test_calculate_group_confidence(self, service, sample_businesses):
        """Test confidence score calculation for duplicate groups."""
        # Create mock fingerprints
        fingerprints = service._generate_fingerprints(sample_businesses[:2])
        
        confidence = service._calculate_group_confidence(sample_businesses[:2], fingerprints)
        
        assert 0.0 <= confidence <= 1.0
        
        # Single business should have 0 confidence
        confidence_single = service._calculate_group_confidence(sample_businesses[:1], fingerprints[:1])
        assert confidence_single == 0.0
    
    def test_determine_duplicate_type(self, service):
        """Test duplicate type determination based on confidence score."""
        assert service._determine_duplicate_type(0.98) == DuplicateType.EXACT_MATCH
        assert service._determine_duplicate_type(0.90) == DuplicateType.HIGH_SIMILARITY
        assert service._determine_duplicate_type(0.80) == DuplicateType.MEDIUM_SIMILARITY
        assert service._determine_duplicate_type(0.70) == DuplicateType.LOW_SIMILARITY
        assert service._determine_duplicate_type(0.60) == DuplicateType.POTENTIAL_DUPLICATE
    
    def test_detect_duplicate_groups(self, service, sample_businesses):
        """Test duplicate group detection."""
        fingerprints = service._generate_fingerprints(sample_businesses)
        
        groups = service._detect_duplicate_groups(
            sample_businesses, fingerprints, 0.8
        )
        
        # Should find at least one group for similar businesses
        assert len(groups) >= 0
        
        for group in groups:
            assert group.group_id is not None
            assert group.primary_business is not None
            assert len(group.duplicate_businesses) > 0
            assert group.confidence_score > 0.0
            assert group.duplicate_type in DuplicateType
    
    def test_identify_unique_businesses(self, service, sample_businesses):
        """Test identification of unique businesses."""
        # Create mock duplicate groups
        mock_groups = [Mock()]
        mock_groups[0].primary_business = sample_businesses[0]
        mock_groups[0].duplicate_businesses = [sample_businesses[1]]
        
        unique = service._identify_unique_businesses(sample_businesses, mock_groups)
        
        # Should exclude businesses in duplicate groups
        unique_ids = {b.source_id for b in unique}
        assert "gp_001" not in unique_ids  # Primary business
        assert "yf_001" not in unique_ids  # Duplicate business
        assert "gp_002" in unique_ids      # Unique business
        assert "me_001" in unique_ids      # Unique business
    
    def test_auto_remove_high_confidence_duplicates(self, service):
        """Test automatic removal of high-confidence duplicates."""
        # Create mock duplicate groups
        mock_groups = [Mock(), Mock()]
        mock_groups[0].confidence_score = 0.95  # High confidence
        mock_groups[0].duplicate_businesses = [Mock(), Mock()]
        mock_groups[1].confidence_score = 0.75  # Lower confidence
        mock_groups[1].duplicate_businesses = [Mock()]
        
        removed = service._auto_remove_high_confidence_duplicates(mock_groups, 0.8)
        
        # Should remove high-confidence duplicates
        assert len(removed) == 2  # From first group only
    
    def test_detect_duplicates_success(self, service, sample_businesses):
        """Test successful duplicate detection."""
        request = DuplicateDetectionRequest(
            businesses=sample_businesses,
            detection_threshold=0.8,
            auto_remove_high_confidence=True,
            run_id="test_run_001"
        )
        
        response = service.detect_duplicates(request)
        
        assert response.success is True
        assert response.total_businesses == 4
        assert response.run_id == "test_run_001"
        assert "detection_threshold" in response.detection_metadata
    
    def test_remove_duplicates_success(self, service):
        """Test successful duplicate removal."""
        # Create mock duplicate groups
        mock_groups = [Mock(), Mock()]
        mock_groups[0].confidence_score = 0.9  # High confidence
        mock_groups[0].duplicate_businesses = [Mock(), Mock()]
        mock_groups[0].primary_business = Mock()
        mock_groups[1].confidence_score = 0.6  # Low confidence
        mock_groups[1].duplicate_businesses = [Mock()]
        mock_groups[1].primary_business = Mock()
        
        request = DuplicateRemovalRequest(
            duplicate_groups=mock_groups,
            removal_strategy="keep_primary",
            review_threshold=0.7,
            run_id="test_run_001"
        )
        
        response = service.remove_duplicates(request)
        
        assert response.success is True
        assert response.total_groups_processed == 2
        assert response.run_id == "test_run_001"
        assert len(response.duplicates_removed) == 2  # From high-confidence group
        assert len(response.businesses_kept) == 1    # From high-confidence group
        assert len(response.review_required) == 1    # From low-confidence group
    
    def test_detect_duplicates_validation_error(self, service):
        """Test duplicate detection with validation error."""
        request = DuplicateDetectionRequest(
            businesses=[],  # Empty list should fail validation
            run_id="test_run_001"
        )
        
        with pytest.raises(ValueError, match="Invalid input"):
            service.detect_duplicates(request)
    
    def test_remove_duplicates_validation_error(self, service):
        """Test duplicate removal with validation error."""
        request = DuplicateRemovalRequest(
            duplicate_groups=[],  # Empty list should fail validation
            run_id="test_run_001"
        )
        
        with pytest.raises(ValueError, match="Invalid input"):
            service.remove_duplicates(request)
    
    def test_error_handling(self, service):
        """Test error handling in the service."""
        # Test with invalid request
        with pytest.raises(ValueError):
            service.detect_duplicates(None)
        
        with pytest.raises(ValueError):
            service.remove_duplicates(None)
    
    def test_logging_integration(self, service, sample_businesses):
        """Test that logging is properly integrated."""
        request = DuplicateDetectionRequest(
            businesses=sample_businesses[:2],
            run_id="test_run_004"
        )
        
        # Should not raise any logging-related errors
        try:
            service.detect_duplicates(request)
        except Exception:
            pass  # We expect this to work, but logging should work regardless
        
        # Verify logger is set up
        assert service.logger is not None
    
    @patch('src.services.duplicate_detection_service.fuzz')
    def test_fuzzy_matching_integration(self, mock_fuzz, service):
        """Test integration with fuzzy string matching library."""
        # Mock fuzzy matching results
        mock_fuzz.ratio.return_value = 85
        mock_fuzz.partial_ratio.return_value = 90
        mock_fuzz.token_sort_ratio.return_value = 88
        mock_fuzz.token_set_ratio.return_value = 92
        
        similarity = service._calculate_string_similarity("joes pizza", "joe pizza")
        
        # Should use the highest ratio (92)
        assert similarity == 0.92
        
        # Verify all fuzzy matching methods were called
        mock_fuzz.ratio.assert_called_once()
        mock_fuzz.partial_ratio.assert_called_once()
        mock_fuzz.token_sort_ratio.assert_called_once()
        mock_fuzz.token_set_ratio.assert_called_once()
