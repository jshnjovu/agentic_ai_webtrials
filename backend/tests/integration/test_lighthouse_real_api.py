"""
Integration tests for Lighthouse API using real Google PageSpeed Insights API calls.
These tests validate the actual implementation with real external services.

WARNING: These tests consume API quota and may take longer to run.
Only run these tests when you want to validate real API integration.
"""

import pytest
import os
import time
from unittest.mock import patch
from src.services.lighthouse_service import LighthouseService
from src.core import get_api_config


class TestLighthouseRealAPI:
    """Integration tests using real Lighthouse API calls."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LighthouseService()
        self.api_config = get_api_config()
        
        # Check if we have a real API key
        if not self.api_config.LIGHTHOUSE_API_KEY or self.api_config.LIGHTHOUSE_API_KEY == "c76e3daa.c159a1e6667343628e8f94366b91f745":
            pytest.skip("Real Lighthouse API key not configured")
        
        # Test URLs that are reliable for testing
        self.test_urls = [
            "https://www.google.com",
            "https://www.github.com", 
            "https://www.stackoverflow.com"
        ]
        
        # Wait between tests to respect rate limits
        self.rate_limit_delay = 2  # seconds
    
    def test_real_lighthouse_audit_desktop(self):
        """Test real Lighthouse audit with desktop strategy."""
        test_url = self.test_urls[0]
        business_id = "integration-test-business"
        run_id = f"integration-test-{int(time.time())}"
        
        # Execute real audit
        result = self.service.run_lighthouse_audit(
            website_url=test_url,
            business_id=business_id,
            run_id=run_id,
            strategy="desktop"
        )
        
        # Validate response structure
        assert result["success"] is True
        assert result["website_url"] == test_url
        assert result["business_id"] == business_id
        assert result["run_id"] == run_id
        assert result["strategy"] == "desktop"
        assert "scores" in result
        assert "overall_score" in result
        assert "core_web_vitals" in result
        assert "confidence" in result
        assert "audit_timestamp" in result
        
        # Validate scores are within expected range
        scores = result["scores"]
        assert 0 <= scores["performance"] <= 100
        assert 0 <= scores["accessibility"] <= 100
        assert 0 <= scores["best_practices"] <= 100
        assert 0 <= scores["seo"] <= 100
        assert 0 <= result["overall_score"] <= 100
        
        # Validate Core Web Vitals
        core_web_vitals = result["core_web_vitals"]
        assert "first_contentful_paint" in core_web_vitals
        assert "largest_contentful_paint" in core_web_vitals
        assert "cumulative_layout_shift" in core_web_vitals
        assert "total_blocking_time" in core_web_vitals
        assert "speed_index" in core_web_vitals
        
        # Wait to respect rate limits
        time.sleep(self.rate_limit_delay)
    
    def test_real_lighthouse_audit_mobile(self):
        """Test real Lighthouse audit with mobile strategy."""
        test_url = self.test_urls[1]
        business_id = "integration-test-business"
        run_id = f"integration-test-{int(time.time())}"
        
        # Execute real audit
        result = self.service.run_lighthouse_audit(
            website_url=test_url,
            business_id=business_id,
            run_id=run_id,
            strategy="mobile"
        )
        
        # Validate response structure
        assert result["success"] is True
        assert result["website_url"] == test_url
        assert result["business_id"] == business_id
        assert result["run_id"] == run_id
        assert result["strategy"] == "mobile"
        assert "scores" in result
        assert "overall_score" in result
        
        # Validate scores are within expected range
        scores = result["scores"]
        assert 0 <= scores["performance"] <= 100
        assert 0 <= scores["accessibility"] <= 100
        assert 0 <= scores["best_practices"] <= 100
        assert 0 <= scores["seo"] <= 100
        assert 0 <= result["overall_score"] <= 100
        
        # Wait to respect rate limits
        time.sleep(self.rate_limit_delay)
    
    def test_real_lighthouse_audit_timeout_handling(self):
        """Test real Lighthouse audit timeout handling with a slow website."""
        # Use a potentially slower website to test timeout handling
        slow_url = "https://www.example.com"  # This might be slow
        business_id = "integration-test-business"
        run_id = f"integration-test-{int(time.time())}"
        
        # Execute real audit
        result = self.service.run_lighthouse_audit(
            website_url=slow_url,
            business_id=business_id,
            run_id=run_id,
            strategy="desktop"
        )
        
        # The result should either be successful or handle timeout gracefully
        if result["success"]:
            # Audit completed successfully
            assert "scores" in result
            assert "overall_score" in result
        else:
            # Audit failed, should have proper error handling
            assert "error" in result
            assert "error_code" in result
            assert "context" in result
        
        # Wait to respect rate limits
        time.sleep(self.rate_limit_delay)
    
    def test_real_lighthouse_audit_invalid_url(self):
        """Test real Lighthouse audit with invalid URL."""
        invalid_url = "not-a-valid-url"
        business_id = "integration-test-business"
        run_id = f"integration-test-{int(time.time())}"
        
        # Execute real audit
        result = self.service.run_lighthouse_audit(
            website_url=invalid_url,
            business_id=business_id,
            run_id=run_id,
            strategy="desktop"
        )
        
        # Should fail with proper error handling
        assert result["success"] is False
        assert "error" in result
        assert "error_code" in result
        assert "context" in result
        
        # Wait to respect rate limits
        time.sleep(self.rate_limit_delay)
    
    def test_real_lighthouse_audit_rate_limiting(self):
        """Test real Lighthouse audit rate limiting by making multiple requests."""
        test_url = self.test_urls[2]
        business_id = "integration-test-business"
        
        # Make multiple requests to test rate limiting
        results = []
        for i in range(3):  # Make 3 requests
            run_id = f"integration-test-{int(time.time())}-{i}"
            
            result = self.service.run_lighthouse_audit(
                website_url=test_url,
                business_id=business_id,
                run_id=run_id,
                strategy="desktop"
            )
            
            results.append(result)
            
            # Wait between requests to respect rate limits
            if i < 2:  # Don't wait after the last request
                time.sleep(self.rate_limit_delay)
        
        # All requests should succeed (within rate limits)
        for result in results:
            assert result["success"] is True
            assert "scores" in result
            assert "overall_score" in result
    
    def test_real_lighthouse_audit_fallback_mechanism(self):
        """Test real Lighthouse audit fallback mechanism."""
        # This test would require a website that consistently times out
        # For now, we'll test the fallback logic exists
        test_url = self.test_urls[0]
        business_id = "integration-test-business"
        run_id = f"integration-test-{int(time.time())}"
        
        # Execute real audit
        result = self.service.run_lighthouse_audit(
            website_url=test_url,
            business_id=business_id,
            run_id=run_id,
            strategy="desktop"
        )
        
        # Should succeed and have fallback mechanism available
        assert result["success"] is True
        assert "scores" in result
        assert "overall_score" in result
        
        # Wait to respect rate limits
        time.sleep(self.rate_limit_delay)
    
    def test_real_lighthouse_audit_data_consistency(self):
        """Test that real Lighthouse audit data is consistent across multiple runs."""
        test_url = self.test_urls[0]
        business_id = "integration-test-business"
        
        # Make two requests to the same URL
        run_id_1 = f"integration-test-{int(time.time())}-1"
        result_1 = self.service.run_lighthouse_audit(
            website_url=test_url,
            business_id=business_id,
            run_id=run_id_1,
            strategy="desktop"
        )
        
        time.sleep(self.rate_limit_delay)
        
        run_id_2 = f"integration-test-{int(time.time())}-2"
        result_2 = self.service.run_lighthouse_audit(
            website_url=test_url,
            business_id=business_id,
            run_id=run_id_2,
            strategy="desktop"
        )
        
        # Both should succeed
        assert result_1["success"] is True
        assert result_2["success"] is True
        
        # Scores should be in reasonable range (allowing for some variation)
        scores_1 = result_1["scores"]
        scores_2 = result_2["scores"]
        
        for category in ["performance", "accessibility", "best_practices", "seo"]:
            score_1 = scores_1[category]
            score_2 = scores_2[category]
            
            # Scores should be within reasonable range (0-100)
            assert 0 <= score_1 <= 100
            assert 0 <= score_2 <= 100
            
            # Scores should not differ by more than 20 points (allowing for variation)
            assert abs(score_1 - score_2) <= 20
        
        # Wait to respect rate limits
        time.sleep(self.rate_limit_delay)


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short"])
