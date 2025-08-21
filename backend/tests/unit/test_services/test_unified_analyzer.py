"""
Unit tests for UnifiedAnalyzer service.
Tests comprehensive website analysis, caching, retry logic, and health monitoring.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from unittest.mock import call
from tenacity import RetryError

from src.services.unified import UnifiedAnalyzer
from src.services.domain_analysis import DomainAnalysisService


class TestUnifiedAnalyzer:
    """Test cases for UnifiedAnalyzer service."""
    
    @pytest.fixture
    def mock_rate_limiter(self):
        """Create a mock rate limiter."""
        mock = Mock()
        mock.can_make_request.return_value = (True, "OK")
        mock.record_request.return_value = None
        return mock
    
    @pytest.fixture
    def mock_domain_service(self):
        """Create a mock domain analysis service."""
        mock = Mock()
        mock.analyze_domain = AsyncMock(return_value={
            "domainAge": {
                "years": 5,
                "months": 2,
                "days": 15,
                "totalDays": 1890,
                "createdDate": "2019-10-04T00:00:00+00:00",
                "ageDescription": "Established"
            }
        })
        return mock
    
    @pytest.fixture
    def mock_api_config(self):
        """Create a mock API configuration."""
        mock = Mock()
        mock.GOOGLE_GENERAL_API_KEY = "test_google_api_key"
        mock.SERPAPI_RATE_LIMIT_PER_MINUTE = 100
        mock.GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE = 100
        mock.YELP_FUSION_RATE_LIMIT_PER_DAY = 5000
        mock.PAGESPEED_RATE_LIMIT_PER_DAY = 25000
        mock.PAGESPEED_RATE_LIMIT_PER_MINUTE = 240
        mock.PINGDOM_RATE_LIMIT_PER_MINUTE = 60
        mock.COMPREHENSIVE_SPEED_RATE_LIMIT_PER_MINUTE = 30
        mock.VALIDATION_RATE_LIMIT_PER_MINUTE = 120
        mock.FALLBACK_RATE_LIMIT_PER_MINUTE = 60
        mock.CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
        mock.CIRCUIT_BREAKER_RECOVERY_TIMEOUT = 60
        return mock
    
    @pytest.fixture
    def analyzer(self, mock_rate_limiter, mock_api_config):
        """Create a UnifiedAnalyzer instance with mocked dependencies."""
        with patch('src.services.unified.get_api_config', return_value=mock_api_config), \
             patch('src.services.unified.RateLimiter', return_value=mock_rate_limiter), \
             patch('src.services.unified.DomainAnalysisService', return_value=Mock()):
            
            analyzer = UnifiedAnalyzer()
            print(f"\n🔧 Created UnifiedAnalyzer instance: {analyzer}")
            print(f"📊 Initial service health: {analyzer.service_health}")
            print(f"📈 Initial analysis stats: {analyzer.analysis_stats}")
            return analyzer
    
    def test_initialization(self, analyzer):
        """Test that the analyzer initializes with correct configuration."""
        print(f"\n✅ Testing UnifiedAnalyzer initialization")
        print(f"📋 Cache TTL: {analyzer.cache_ttl}s")
        print(f"🔄 Retry config: {analyzer.retry_config}")
        print(f"🏥 Service health: {analyzer.service_health}")
        print(f"📊 Analysis stats: {analyzer.analysis_stats}")
        
        assert analyzer.cache_ttl == 3600  # 1 hour
        assert analyzer.retry_config['max_attempts'] == 3
        assert analyzer.retry_config['base_delay'] == 2
        assert analyzer.retry_config['max_delay'] == 30
        assert analyzer.retry_config['exponential_backoff'] is True
        assert 'pagespeed' in analyzer.service_health
        assert 'domain_analysis' in analyzer.service_health
        assert 'overall' in analyzer.service_health
        assert 'total_analyses' in analyzer.analysis_stats
    
    def test_extract_metric(self, analyzer):
        """Test metric extraction from PageSpeed audit data."""
        print(f"\n✅ Testing metric extraction")
        
        # Test with valid metric data
        valid_metric = {
            "numericValue": 2500,
            "displayValue": "2.5s",
            "numericUnit": "ms"
        }
        result = analyzer.extract_metric(valid_metric)
        print(f"📊 Valid metric input: {valid_metric}")
        print(f"📊 Extracted result: {result}")
        
        assert result is not None
        assert result["value"] == 2500
        assert result["displayValue"] == "2.5s"
        assert result["unit"] == "ms"
        
        # Test with None input
        result_none = analyzer.extract_metric(None)
        print(f"📊 None input result: {result_none}")
        assert result_none is None
        
        # Test with empty dict
        result_empty = analyzer.extract_metric({})
        print(f"📊 Empty dict result: {result_empty}")
        assert result_empty is None
    
    def test_extract_opportunities(self, analyzer):
        """Test opportunity extraction from PageSpeed audits."""
        print(f"\n✅ Testing opportunity extraction")
        
        # Mock audit data with opportunities
        mock_audits = {
            "opportunity-1": {
                "title": "Reduce unused CSS",
                "description": "Remove unused CSS to reduce bytes",
                "details": {"type": "opportunity"},
                "numericValue": 15000,
                "numericUnit": "ms"
            },
            "opportunity-2": {
                "title": "Optimize images",
                "description": "Optimize images for faster loading",
                "details": {"type": "opportunity"},
                "numericValue": 8000,
                "numericUnit": "ms"
            },
            "not-opportunity": {
                "title": "Some other audit",
                "details": {"type": "diagnostic"},
                "numericValue": 0
            }
        }
        
        opportunities = analyzer.extract_opportunities(mock_audits)
        print(f"📊 Mock audits: {mock_audits}")
        print(f"📊 Extracted opportunities: {opportunities}")
        
        assert len(opportunities) == 2
        assert opportunities[0]["title"] == "Reduce unused CSS"
        assert opportunities[0]["potentialSavings"] == 15000
        assert opportunities[1]["title"] == "Optimize images"
        assert opportunities[1]["potentialSavings"] == 8000
    
    def test_analyze_mobile_usability_from_pagespeed(self, analyzer):
        """Test mobile usability analysis from PageSpeed data."""
        print(f"\n✅ Testing mobile usability analysis")
        
        # Mock audits with mobile usability checks
        mock_audits = {
            "viewport": {"score": 1},
            "content-width": {"score": 1},
            "tap-targets": {"score": 0},  # Failed check
            "font-size": {"score": 1}
        }
        
        result = analyzer.analyze_mobile_usability_from_pagespeed(mock_audits)
        print(f"📊 Mock audits: {mock_audits}")
        print(f"📊 Mobile usability result: {result}")
        
        assert result["mobileFriendly"] is True  # 4/5 checks passed = 80% (meets threshold)
        assert result["score"] == 80
        assert len(result["checks"]) == 5
        assert result["checks"]["tapTargetsAppropriateSize"] is False
        assert len(result["issues"]) > 0
        assert "Tap targets too small" in result["issues"]
    
    def test_get_mobile_issues(self, analyzer):
        """Test mobile issue generation from check results."""
        print(f"\n✅ Testing mobile issue generation")
        
        checks = {
            "hasViewportMetaTag": True,
            "contentSizedCorrectly": False,
            "tapTargetsAppropriateSize": True,
            "textReadable": False,
            "isResponsive": True
        }
        
        issues = analyzer.get_mobile_issues(checks)
        print(f"📊 Mock checks: {checks}")
        print(f"📊 Generated issues: {issues}")
        
        assert len(issues) == 2
        assert "Content not sized correctly for viewport" in issues
        assert "Text too small to read" in issues
        assert "Missing viewport meta tag" not in issues  # This check passed
    
    def test_estimate_domain_age(self, analyzer):
        """Test domain age estimation logic."""
        print(f"\n✅ Testing domain age estimation")
        
        test_cases = [
            ("example", "5+ years (estimated)"),
            ("new-business-2020", "2-3 years (estimated)"),
            ("latest-tech-2021", "2-3 years (estimated)"),
            ("newstartup", "1-2 years (estimated)"),
            ("established-company", "3-5 years (estimated)")
        ]
        
        for domain, expected in test_cases:
            result = analyzer.estimate_domain_age(domain)
            print(f"📊 Domain: {domain} -> Estimated age: {result}")
            assert result == expected
    
    def test_calculate_ux_score(self, analyzer):
        """Test UX score calculation from Core Web Vitals."""
        print(f"\n✅ Testing UX score calculation")
        
        # Test with good Core Web Vitals
        good_cwv = {
            "largestContentfulPaint": {"value": 2000},  # Good
            "cumulativeLayoutShift": {"value": 0.05}    # Good
        }
        good_score = analyzer.calculate_ux_score(good_cwv)
        print(f"📊 Good CWV: {good_cwv} -> Score: {good_score}")
        assert good_score == 100
        
        # Test with poor Core Web Vitals
        poor_cwv = {
            "largestContentfulPaint": {"value": 5000},  # Poor
            "cumulativeLayoutShift": {"value": 0.3}     # Poor
        }
        poor_score = analyzer.calculate_ux_score(poor_cwv)
        print(f"📊 Poor CWV: {poor_cwv} -> Score: {poor_score}")
        assert poor_score < 100
        assert poor_score >= 0
    
    def test_calculate_interactivity_score(self, analyzer):
        """Test interactivity score calculation from server metrics."""
        print(f"\n✅ Testing interactivity score calculation")
        
        # Test with good server metrics
        good_metrics = {
            "timeToInteractive": {"value": 2000},  # Good
            "totalBlockingTime": {"value": 200}    # Good
        }
        good_score = analyzer.calculate_interactivity_score(good_metrics)
        print(f"📊 Good metrics: {good_metrics} -> Score: {good_score}")
        assert good_score == 100
        
        # Test with poor server metrics
        poor_metrics = {
            "timeToInteractive": {"value": 6000},  # Poor
            "totalBlockingTime": {"value": 800}    # Poor
        }
        poor_score = analyzer.calculate_interactivity_score(poor_metrics)
        print(f"📊 Poor metrics: {poor_metrics} -> Score: {poor_score}")
        assert poor_score < 100
        assert poor_score >= 0
    
    def test_calculate_visual_stability_score(self, analyzer):
        """Test visual stability score calculation."""
        print(f"\n✅ Testing visual stability score calculation")
        
        test_cases = [
            (0.05, 100),   # Excellent
            (0.15, 80),    # Good
            (0.3, 50)      # Poor
        ]
        
        for cls_value, expected_score in test_cases:
            cwv = {"cumulativeLayoutShift": {"value": cls_value}}
            result = analyzer.calculate_visual_stability_score(cwv)
            print(f"📊 CLS: {cls_value} -> Score: {result}")
            assert result == expected_score
    
    def test_cache_management(self, analyzer):
        """Test cache management functionality."""
        print(f"\n✅ Testing cache management")
        
        # Test cache cleanup
        initial_cache_size = len(analyzer.cache)
        print(f"📊 Initial cache size: {initial_cache_size}")
        
        # Add some test cache entries
        test_time = time.time()
        analyzer.cache["test_key_1"] = {"timestamp": test_time - 4000, "data": "old"}
        analyzer.cache["test_key_2"] = {"timestamp": test_time - 100, "data": "recent"}
        analyzer.cache["test_key_3"] = {"timestamp": test_time, "data": "current"}
        
        print(f"📊 Cache before cleanup: {analyzer.cache}")
        print(f"📊 Cache size before cleanup: {len(analyzer.cache)}")
        
        # Run cleanup
        analyzer._cleanup_cache()
        
        print(f"📊 Cache after cleanup: {analyzer.cache}")
        print(f"📊 Cache size after cleanup: {len(analyzer.cache)}")
        
        # Should have removed expired entries
        assert "test_key_1" not in analyzer.cache  # Expired
        assert "test_key_2" in analyzer.cache      # Still valid
        assert "test_key_3" in analyzer.cache      # Still valid
    
    def test_service_health_monitoring(self, analyzer):
        """Test service health monitoring functionality."""
        print(f"\n✅ Testing service health monitoring")
        
        # Test initial health update
        initial_health = analyzer.service_health.copy()
        print(f"📊 Initial health: {initial_health}")
        
        # Update health
        analyzer._update_overall_health()
        updated_health = analyzer.service_health.copy()
        print(f"📊 Updated health: {updated_health}")
        
        # Test health status retrieval
        health_status = analyzer.get_service_health()
        print(f"📊 Health status: {health_status}")
        
        assert "service" in health_status
        assert "status" in health_status
        assert "services" in health_status
        assert "features" in health_status
        assert health_status["service"] == "unified_analyzer"
        assert "caching" in health_status["features"]
        assert "retry_logic" in health_status["features"]
        assert "batch_processing" in health_status["features"]
    
    def test_analysis_statistics(self, analyzer):
        """Test analysis statistics tracking."""
        print(f"\n✅ Testing analysis statistics")
        
        # Get initial stats
        initial_stats = analyzer.get_analysis_statistics()
        print(f"📊 Initial stats: {initial_stats}")
        
        # Verify structure
        assert "statistics" in initial_stats
        assert "cache_info" in initial_stats
        assert "retry_config" in initial_stats
        
        # Test cache info
        cache_info = initial_stats["cache_info"]
        print(f"📊 Cache info: {cache_info}")
        assert "total_entries" in cache_info
        assert "cache_ttl" in cache_info
        assert "cache_hit_rate" in cache_info
        assert cache_info["cache_ttl"] == 3600
    
    def test_overall_score_calculation(self, analyzer):
        """Test overall score calculation with business impact weighting."""
        print(f"\n✅ Testing overall score calculation")
        
        # Test with complete scores
        complete_scores = {
            "performance": 85,
            "accessibility": 90,
            "bestPractices": 88,
            "seo": 92,
            "trust": 78,
            "cro": 82
        }
        
        overall_score = analyzer._calculate_overall_score(complete_scores)
        print(f"📊 Complete scores: {complete_scores}")
        print(f"📊 Calculated overall score: {overall_score}")
        
        # Verify calculation
        expected_score = (
            85 * 0.25 +  # performance
            90 * 0.15 +  # accessibility
            88 * 0.15 +  # bestPractices
            92 * 0.15 +  # seo
            78 * 0.20 +  # trust
            82 * 0.10    # cro
        )
        print(f"📊 Expected score: {expected_score}")
        assert abs(overall_score - expected_score) < 0.01
        
        # Test with missing scores
        partial_scores = {
            "performance": 85,
            "accessibility": 90,
            "trust": 78
        }
        
        partial_overall = analyzer._calculate_overall_score(partial_scores)
        print(f"📊 Partial scores: {partial_scores}")
        print(f"📊 Partial overall score: {partial_overall}")
        
        # Should still calculate correctly with available weights
        expected_partial = (85 * 0.25 + 90 * 0.15 + 78 * 0.20) / (0.25 + 0.15 + 0.20)
        print(f"📊 Expected partial score: {expected_partial}")
        assert abs(partial_overall - expected_partial) < 0.01
    
    @pytest.mark.asyncio
    async def test_make_request_with_rate_limiting(self, analyzer):
        """Test request method with rate limiting."""
        print(f"\n✅ Testing request method with rate limiting")
        
        # Mock successful request
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "success"}
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = await analyzer.make_request("https://test.com")
            print(f"📊 Request result: {result}")
            
            assert result == {"status": "success"}
            mock_get.assert_called_once_with("https://test.com")
            
            # Verify rate limiter was called
            analyzer.rate_limiter.can_make_request.assert_called_once_with('unified_analyzer')
            analyzer.rate_limiter.record_request.assert_called_once_with('unified_analyzer', True)
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_exceeded(self, analyzer):
        """Test request method when rate limit is exceeded."""
        print(f"\n✅ Testing request method with rate limit exceeded")
        
        # Mock rate limit exceeded
        analyzer.rate_limiter.can_make_request.return_value = (False, "Rate limit exceeded")
        
        # The @retry decorator wraps the entire method, so it will retry 3 times
        # even though the rate limit check happens first
        with pytest.raises(RetryError):
            await analyzer.make_request("https://test.com")
        
        # Verify rate limiter was called (should be called 3 times due to retries)
        assert analyzer.rate_limiter.can_make_request.call_count == 3
        # Should record failed requests when rate limited (3 times due to retries)
        assert analyzer.rate_limiter.record_request.call_count == 3
        # Verify the failed requests were recorded with False (failed)
        analyzer.rate_limiter.record_request.assert_has_calls([
            call('unified_analyzer', False),
            call('unified_analyzer', False),
            call('unified_analyzer', False)
        ])
    
    @pytest.mark.asyncio
    async def test_make_request_http_error(self, analyzer):
        """Test request method with HTTP error."""
        print(f"\n✅ Testing request method with HTTP error")
        
        with patch('requests.get') as mock_get:
            from requests.exceptions import HTTPError
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.reason = "Too Many Requests"
            mock_get.return_value = mock_response
            
            # Mock HTTPError
            mock_response.raise_for_status.side_effect = HTTPError(
                response=mock_response,
                request=Mock()
            )
            
            # The @retry decorator will retry 3 times, so we expect a tenacity.RetryError
            # that wraps the RuntimeError after all retries are exhausted
            from tenacity import RetryError
            with pytest.raises(RetryError):
                await analyzer.make_request("https://test.com")
            
            # Verify failed request was recorded (should be called 3 times due to retries)
            assert analyzer.rate_limiter.record_request.call_count == 3
    
    @pytest.mark.asyncio
    async def test_make_request_general_error(self, analyzer):
        """Test request method with general error."""
        print(f"\n✅ Testing request method with general error")
        
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Network error")
            
            # The @retry decorator will retry 3 times, so we expect a tenacity.RetryError
            # that wraps the RuntimeError after all retries are exhausted
            from tenacity import RetryError
            with pytest.raises(RetryError):
                await analyzer.make_request("https://test.com")
            
            # Verify failed request was recorded (should be called 3 times due to retries)
            assert analyzer.rate_limiter.record_request.call_count == 3
    
    def test_cleanup_cache_edge_cases(self, analyzer):
        """Test cache cleanup with edge cases."""
        print(f"\n✅ Testing cache cleanup edge cases")
        
        # Test with empty cache
        analyzer.cache = {}
        analyzer._cleanup_cache()
        assert len(analyzer.cache) == 0
        
        # Test with all expired entries
        current_time = time.time()
        analyzer.cache = {
            "expired1": {"timestamp": current_time - 4000, "data": "old1"},
            "expired2": {"timestamp": current_time - 5000, "data": "old2"}
        }
        analyzer._cleanup_cache()
        assert len(analyzer.cache) == 0
        
        # Test with mixed valid/expired entries
        analyzer.cache = {
            "expired": {"timestamp": current_time - 4000, "data": "old"},
            "valid": {"timestamp": current_time, "data": "current"}
        }
        analyzer._cleanup_cache()
        assert len(analyzer.cache) == 1
        assert "valid" in analyzer.cache
        assert "expired" not in analyzer.cache
    
    def test_service_health_edge_cases(self, analyzer):
        """Test service health monitoring with edge cases."""
        print(f"\n✅ Testing service health edge cases")
        
        # Test with all services healthy
        analyzer.service_health = {
            "pagespeed": "healthy",
            "domain_analysis": "healthy"
        }
        analyzer._update_overall_health()
        assert analyzer.service_health["overall"] == "healthy"
        
        # Test with one service unhealthy
        analyzer.service_health = {
            "pagespeed": "healthy",
            "domain_analysis": "unhealthy"
        }
        analyzer._update_overall_health()
        assert analyzer.service_health["overall"] == "degraded"
        
        # Test with all services unhealthy
        analyzer.service_health = {
            "pagespeed": "unhealthy",
            "domain_analysis": "unhealthy"
        }
        analyzer._update_overall_health()
        assert analyzer.service_health["overall"] == "unhealthy"
        
        # Test with unknown status
        analyzer.service_health = {
            "pagespeed": "unknown",
            "domain_analysis": "unknown"
        }
        analyzer._update_overall_health()
        assert analyzer.service_health["overall"] == "unknown"
    
    def test_overall_score_edge_cases(self, analyzer):
        """Test overall score calculation with edge cases."""
        print(f"\n✅ Testing overall score edge cases")
        
        # Test with empty scores
        empty_scores = {}
        result = analyzer._calculate_overall_score(empty_scores)
        print(f"📊 Empty scores result: {result}")
        assert result == 0.0
        
        # Test with None scores
        none_scores = {
            "performance": None,
            "accessibility": None
        }
        result = analyzer._calculate_overall_score(none_scores)
        print(f"📊 None scores result: {result}")
        assert result == 0.0
        
        # Test with zero scores
        zero_scores = {
            "performance": 0,
            "accessibility": 0,
            "trust": 0
        }
        result = analyzer._calculate_overall_score(zero_scores)
        print(f"📊 Zero scores result: {result}")
        assert result == 0.0
        
        # Test with very high scores
        high_scores = {
            "performance": 100,
            "accessibility": 100,
            "trust": 100
        }
        result = analyzer._calculate_overall_score(high_scores)
        print(f"📊 High scores result: {result}")
        assert result == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
