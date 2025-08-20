"""
Integration tests for website analysis using real API calls.
Tests the actual PageSpeed Insights API integration through the unified analyzer.
"""

import pytest
import asyncio
from unittest.mock import patch

from src.services.unified import UnifiedAnalyzer
from src.core.config import get_api_config


class TestPageSpeedRealAPI:
    """Integration tests using real Google PageSpeed API calls through unified analyzer."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.analyzer = UnifiedAnalyzer()
        self.api_config = get_api_config()
        
        # Skip tests if no real API key configured
        if not self.api_config.GOOGLE_GENERAL_API_KEY:
            pytest.skip("Real Google General API key not configured")
    
    @pytest.mark.asyncio
    async def test_real_pagespeed_audit_desktop(self):
        """Test real PageSpeed audit with desktop strategy."""
        # Use a known website for testing
        test_url = "https://www.google.com"
        
        result = await self.analyzer.run_page_speed_analysis(
            url=test_url,
            strategy="desktop"
        )
        
        assert result is not None
        assert "scores" in result
        assert "coreWebVitals" in result
        
        # Verify scores are within expected range (0-100 scale)
        scores = result["scores"]
        assert 0 <= scores["performance"] <= 100
        assert 0 <= scores["accessibility"] <= 100
        assert 0 <= scores["bestPractices"] <= 100
        assert 0 <= scores["seo"] <= 100
    
    @pytest.mark.asyncio
    async def test_real_pagespeed_audit_mobile(self):
        """Test real PageSpeed audit with mobile strategy."""
        test_url = "https://www.google.com"
        
        result = await self.analyzer.run_page_speed_analysis(
            url=test_url,
            strategy="mobile"
        )
        
        assert result is not None
        assert "scores" in result
        assert "coreWebVitals" in result
        assert "mobileUsability" in result
        
        # Verify mobile usability data
        mobile_data = result["mobileUsability"]
        assert "mobileFriendly" in mobile_data
        assert "score" in mobile_data
        assert "checks" in mobile_data
    
    @pytest.mark.asyncio
    async def test_real_pagespeed_audit_core_web_vitals(self):
        """Test real PageSpeed audit with core web vitals."""
        test_url = "https://www.google.com"
        
        result = await self.analyzer.run_page_speed_analysis(
            url=test_url,
            strategy="desktop"
        )
        
        assert result is not None
        assert "coreWebVitals" in result
        
        cwv = result["coreWebVitals"]
        # Check that core web vitals are present (may be None if not available)
        assert "largestContentfulPaint" in cwv
        assert "firstInputDelay" in cwv
        assert "cumulativeLayoutShift" in cwv
        assert "firstContentfulPaint" in cwv
        assert "speedIndex" in cwv
    
    @pytest.mark.asyncio
    async def test_pagespeed_audit_invalid_url(self):
        """Test PageSpeed audit with invalid URL."""
        invalid_url = "not_a_valid_url"
        
        try:
            result = await self.analyzer.run_page_speed_analysis(
                url=invalid_url,
                strategy="desktop"
            )
            # If we get here, the URL was processed (unlikely for invalid URL)
            assert result is not None
        except Exception as e:
            # Expected behavior for invalid URL
            assert "error" in str(e) or "failed" in str(e).lower()
    
    def test_analyzer_health(self):
        """Test unified analyzer health check."""
        health_data = self.analyzer.get_service_health()
        
        assert health_data["service"] == "unified_analyzer"
        assert "status" in health_data
        assert "services" in health_data
        assert "features" in health_data
        
        # Check service status
        services = health_data["services"]
        assert "pagespeed" in services
        assert "domain_analysis" in services
        
        # Check features
        features = health_data["features"]
        assert features["caching"] is True
        assert features["retry_logic"] is True
        assert features["batch_processing"] is True
        assert features["health_monitoring"] is True
        assert features["rate_limiting"] is True
        assert features["comprehensive_analysis"] is True
    
    def test_analyzer_initialization(self):
        """Test that unified analyzer initializes correctly."""
        # This test should always pass regardless of API key configuration
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'api_config')
        assert hasattr(self.analyzer, 'rate_limiter')
        assert hasattr(self.analyzer, 'pagespeed_base_url')
        assert self.analyzer.pagespeed_base_url == "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    def test_rate_limit_configuration(self):
        """Test that rate limits are properly configured."""
        health_data = self.analyzer.get_service_health()
        rate_limits = health_data["rate_limits"]
        
        assert "unified_analyzer" in rate_limits
        assert "unified_comprehensive" in rate_limits
        assert rate_limits["unified_analyzer"] > 0
        assert rate_limits["unified_comprehensive"] > 0


class TestPageSpeedBasicFunctionality:
    """Basic functionality tests that don't require real API key."""
    
    def test_analyzer_initialization(self):
        """Test that unified analyzer initializes correctly."""
        analyzer = UnifiedAnalyzer()
        
        assert analyzer is not None
        assert hasattr(analyzer, 'api_config')
        assert hasattr(analyzer, 'rate_limiter')
        assert hasattr(analyzer, 'pagespeed_base_url')
        assert analyzer.pagespeed_base_url == "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    def test_analyzer_health_without_api_key(self):
        """Test analyzer health when API key is not configured."""
        analyzer = UnifiedAnalyzer()
        health_data = analyzer.get_service_health()
        
        assert health_data["service"] == "unified_analyzer"
        assert "status" in health_data
        assert "services" in health_data
        assert "features" in health_data
        
        # The status depends on whether the API key is configured
        # If configured, should be "healthy", if not configured, should be "unconfigured"
        assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Check services status
        services = health_data["services"]
        assert "pagespeed" in services
        assert "domain_analysis" in services
    
    def test_analyzer_statistics(self):
        """Test that analyzer statistics are properly configured."""
        analyzer = UnifiedAnalyzer()
        stats = analyzer.get_analysis_statistics()
        
        assert "statistics" in stats
        assert "cache_info" in stats
        assert "retry_config" in stats
        
        # Check statistics structure
        statistics = stats["statistics"]
        assert "total_analyses" in statistics
        assert "successful_analyses" in statistics
        assert "failed_analyses" in statistics
        assert "cache_hits" in statistics
        assert "cache_misses" in statistics
        
        # Check cache info
        cache_info = stats["cache_info"]
        assert "total_entries" in cache_info
        assert "cache_ttl" in cache_info
        assert "cache_hit_rate" in cache_info
        
        # Check retry config
        retry_config = stats["retry_config"]
        assert "max_attempts" in retry_config
        assert "base_delay" in retry_config
        assert "max_delay" in retry_config
        assert "exponential_backoff" in retry_config
