"""
Unit tests for Category Mapper Service.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any
from src.services import CategoryMapperService


class TestCategoryMapperService:
    """Test cases for CategoryMapperService."""
    
    @pytest.fixture
    def service(self):
        """Create a CategoryMapperService instance for testing."""
        return CategoryMapperService()
    
    def test_validate_input_valid(self, service):
        """Test input validation with valid data."""
        assert service.validate_input(["restaurant", "food"]) is True
        assert service.validate_input("restaurant") is True
        assert service.validate_input(None) is True
    
    def test_validate_input_invalid(self, service):
        """Test input validation with invalid data."""
        assert service.validate_input(123) is False
        assert service.validate_input(True) is False
    
    def test_map_google_to_yelp_basic(self, service):
        """Test basic Google to Yelp category mapping."""
        google_categories = ["restaurant", "food"]
        yelp_categories = service.map_google_to_yelp(google_categories)
        
        assert "restaurants" in yelp_categories
        assert "food" in yelp_categories
        assert len(yelp_categories) == 2
    
    def test_map_google_to_yelp_shopping(self, service):
        """Test Google to Yelp mapping for shopping categories."""
        google_categories = ["clothing_store", "jewelry_store"]
        yelp_categories = service.map_google_to_yelp(google_categories)
        
        assert "shopping" in yelp_categories
        assert "fashion" in yelp_categories
        assert "jewelry" in yelp_categories
    
    def test_map_yelp_to_google_basic(self, service):
        """Test basic Yelp to Google category mapping."""
        yelp_categories = ["restaurants", "food"]
        google_categories = service.map_yelp_to_google(yelp_categories)
        
        assert "restaurant" in google_categories
        assert "food" in google_categories
    
    def test_map_google_to_yelp_empty_input(self, service):
        """Test Google to Yelp mapping with empty input."""
        yelp_categories = service.map_google_to_yelp([])
        assert yelp_categories == []
    
    def test_get_mapping_info(self, service):
        """Test getting mapping information."""
        info = service.get_mapping_info()
        
        assert "google_categories_count" in info
        assert "yelp_categories_count" in info
        assert info["google_categories_count"] > 0
        assert info["yelp_categories_count"] > 0
    
    def test_validate_category_mapping(self, service):
        """Test category mapping validation."""
        source_categories = ["restaurant"]
        target_categories = ["restaurants", "food"]
        
        validation = service.validate_category_mapping(
            source_categories, target_categories, "google"
        )
        
        assert "accuracy_percentage" in validation
        assert "validation_score" in validation
        assert validation["accuracy_percentage"] > 0
