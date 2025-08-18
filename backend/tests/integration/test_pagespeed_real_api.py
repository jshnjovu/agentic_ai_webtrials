"""
Integration tests for Google PageSpeed API using real API calls.
Tests the actual PageSpeed Insights API integration.
"""

import pytest
import asyncio
from unittest.mock import patch

from src.services.google_pagespeed_service import GooglePageSpeedService
from src.core.config import get_api_config


class TestPageSpeedRealAPI:
    """Integration tests using real Google PageSpeed API calls."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.service = GooglePageSpeedService()
        self.api_config = get_api_config()
        
        # Skip tests if no real API key configured
        if not self.api_config.is_api_key_valid('GOOGLE_GENERAL_API_KEY'):
            pytest.skip("Real Google General API key not configured")
    
    @pytest.mark.asyncio
    async def test_real_pagespeed_audit_desktop(self):
        """Test real PageSpeed audit with desktop strategy."""
        # Use a known website for testing
        test_url = "https://www.google.com"
        
        result = await self.service.run_pagespeed_audit(
            website_url=test_url,
            business_id="test_business_123",
            run_id="test_run_456",
            strategy="desktop"
        )
        
        assert result["success"] is True
        assert result["website_url"] == test_url
        assert result["business_id"] == "test_business_123"
        assert result["run_id"] == "test_run_456"
        assert "scores" in result
        assert "core_web_vitals" in result
        assert "raw_data" in result
        
        # Verify scores are within expected range
        scores = result["scores"]
        assert 0 <= scores["overall"] <= 1
        assert 0 <= scores["performance"] <= 1
        assert 0 <= scores["accessibility"] <= 1
        assert 0 <= scores["best_practices"] <= 1
        assert 0 <= scores["seo"] <= 1
    
    @pytest.mark.asyncio
    async def test_real_pagespeed_audit_mobile(self):
        """Test real PageSpeed audit with mobile strategy."""
        test_url = "https://www.google.com"
        
        result = await self.service.run_pagespeed_audit(
            website_url=test_url,
            business_id="test_business_123",
            run_id="test_run_789",
            strategy="mobile"
        )
        
        assert result["success"] is True
        assert result["strategy"] == "mobile"
        assert "scores" in result
        assert "core_web_vitals" in result
    
    @pytest.mark.asyncio
    async def test_real_pagespeed_audit_with_categories(self):
        """Test real PageSpeed audit with specific categories."""
        test_url = "https://www.google.com"
        
        result = await self.service.run_pagespeed_audit(
            website_url=test_url,
            business_id="test_business_123",
            run_id="test_run_101",
            strategy="desktop",
            categories=["performance", "seo"]
        )
        
        assert result["success"] is True
        assert "scores" in result
        # Should still have all scores even with limited categories
        assert "performance" in result["scores"]
        assert "seo" in result["scores"]
    
    @pytest.mark.asyncio
    async def test_pagespeed_audit_invalid_url(self):
        """Test PageSpeed audit with invalid URL."""
        invalid_url = "not_a_valid_url"
        
        result = await self.service.run_pagespeed_audit(
            website_url=invalid_url,
            business_id="test_business_123",
            run_id="test_run_202",
            strategy="desktop"
        )
        
        # Should fail validation
        assert result["success"] is False
        assert "error" in result
    
    def test_service_health(self):
        """Test PageSpeed service health check."""
        health_data = self.service.get_service_health()
        
        assert health_data["service"] == "google_pagespeed"
        assert "status" in health_data
        assert "api_key_configured" in health_data
        assert "rate_limits" in health_data
        
        # Should be healthy if API key is configured
        if self.api_config.is_api_key_valid('GOOGLE_GENERAL_API_KEY'):
            assert health_data["status"] == "healthy"
            assert health_data["api_key_configured"] is True
        else:
            assert health_data["status"] == "unconfigured"
            assert health_data["api_key_configured"] is False
    
    def test_service_initialization(self):
        """Test that PageSpeed service initializes correctly."""
        # This test should always pass regardless of API key configuration
        assert self.service is not None
        assert hasattr(self.service, 'api_config')
        assert hasattr(self.service, 'rate_limiter')
        assert hasattr(self.service, 'base_url')
        assert self.service.base_url == "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    def test_rate_limit_configuration(self):
        """Test that rate limits are properly configured."""
        health_data = self.service.get_service_health()
        rate_limits = health_data["rate_limits"]
        
        assert "per_minute" in rate_limits
        assert "per_day" in rate_limits
        assert rate_limits["per_minute"] > 0
        assert rate_limits["per_day"] > 0


class TestPageSpeedBasicFunctionality:
    """Basic functionality tests that don't require real API key."""
    
    def test_service_initialization(self):
        """Test that PageSpeed service initializes correctly."""
        service = GooglePageSpeedService()
        
        assert service is not None
        assert hasattr(service, 'api_config')
        assert hasattr(service, 'rate_limiter')
        assert hasattr(service, 'base_url')
        assert service.base_url == "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    def test_service_health_without_api_key(self):
        """Test service health when API key is not configured."""
        service = GooglePageSpeedService()
        health_data = service.get_service_health()
        
        assert health_data["service"] == "google_pagespeed"
        assert "status" in health_data
        assert "api_key_configured" in health_data
        assert "rate_limits" in health_data
        
        # The status depends on whether the API key is configured
        # If configured, should be "healthy", if not configured, should be "unconfigured"
        assert health_data["status"] in ["healthy", "unconfigured"]
        assert isinstance(health_data["api_key_configured"], bool)
    
    def test_rate_limit_configuration(self):
        """Test that rate limits are properly configured."""
        service = GooglePageSpeedService()
        health_data = service.get_service_health()
        rate_limits = health_data["rate_limits"]
        
        assert "per_minute" in rate_limits
        assert "per_day" in rate_limits
        assert rate_limits["per_minute"] > 0
        assert rate_limits["per_day"] > 0
