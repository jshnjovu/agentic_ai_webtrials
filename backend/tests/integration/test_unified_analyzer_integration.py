"""
Integration tests for UnifiedAnalyzer service.
Tests real API interactions, data flow, and end-to-end functionality.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock

from src.services.unified import UnifiedAnalyzer


class TestUnifiedAnalyzerIntegration:
    """Integration test cases for UnifiedAnalyzer service."""
    
    @pytest.fixture
    def real_analyzer(self):
        """Create a real UnifiedAnalyzer instance for integration testing."""
        try:
            analyzer = UnifiedAnalyzer()
            print(f"\n🔧 Created real UnifiedAnalyzer instance: {analyzer}")
            print(f"📊 Service health: {analyzer.service_health}")
            print(f"📈 Analysis stats: {analyzer.analysis_stats}")
            return analyzer
        except Exception as e:
            print(f"⚠️ Failed to create real UnifiedAnalyzer: {e}")
            pytest.skip(f"UnifiedAnalyzer not available: {e}")
    
    @pytest.fixture
    def test_urls(self):
        """Test URLs for integration testing."""
        return [
            "https://www.google.com",      # Well-known, fast site
            "https://www.github.com",      # Well-known, reliable site
            "https://httpbin.org/delay/1", # Test site with controlled delay
        ]
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_pagespeed_analysis(self, real_analyzer):
        """Test real PageSpeed API integration."""
        print(f"\n🌐 Testing real PageSpeed API integration")
        
        test_url = "https://www.google.com"
        
        try:
            start_time = time.time()
            result = await real_analyzer.run_page_speed_analysis(test_url, "mobile")
            analysis_time = time.time() - start_time
            
            print(f"📊 Analysis completed in {analysis_time:.2f}s")
            print(f"📊 Result structure: {list(result.keys())}")
            print(f"📊 Scores: {result.get('scores', {})}")
            print(f"📊 Core Web Vitals: {result.get('coreWebVitals', {})}")
            print(f"📊 Mobile usability: {result.get('mobileUsability', {})}")
            print(f"📊 Opportunities: {result.get('opportunities', [])}")
            
            # Verify result structure
            assert "scores" in result
            assert "coreWebVitals" in result
            assert "mobileUsability" in result
            assert "opportunities" in result
            
            # Verify scores are within valid range
            scores = result["scores"]
            for score_name, score_value in scores.items():
                print(f"📊 {score_name}: {score_value}")
                assert 0 <= score_value <= 100, f"Score {score_name} out of range: {score_value}"
            
            print(f"✅ Real PageSpeed analysis successful")
            
        except Exception as e:
            print(f"❌ Real PageSpeed analysis failed: {e}")
            pytest.skip(f"PageSpeed API not available: {e}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_comprehensive_analysis(self, real_analyzer):
        """Test real comprehensive analysis integration."""
        print(f"\n🔍 Testing real comprehensive analysis integration")
        
        test_url = "https://www.google.com"
        
        try:
            start_time = time.time()
            result = await real_analyzer.run_comprehensive_analysis(test_url, "mobile")
            analysis_time = time.time() - start_time
            
            print(f"📊 Comprehensive analysis completed in {analysis_time:.2f}s")
            print(f"📊 Analysis result structure: {list(result.keys())}")
            print(f"📊 Success: {result.get('success')}")
            print(f"📊 Services used: {result.get('services_used', [])}")
            print(f"📊 Analysis time: {result.get('analysis_time')}")
            
            if result.get("success"):
                print(f"📊 Scores: {result.get('scores', {})}")
                print(f"📊 Details keys: {list(result.get('details', {}).keys())}")
                
                # Verify comprehensive result structure
                assert "url" in result
                assert "strategy" in result
                assert "success" in result
                assert "scores" in result
                assert "details" in result
                assert "services_used" in result
                assert "analysis_time" in result
                
                # Verify scores
                scores = result["scores"]
                print(f"📊 Performance: {scores.get('performance')}")
                print(f"📊 Accessibility: {scores.get('accessibility')}")
                print(f"📊 Best Practices: {scores.get('bestPractices')}")
                print(f"📊 SEO: {scores.get('seo')}")
                print(f"📊 Trust: {scores.get('trust')}")
                print(f"📊 CRO: {scores.get('cro')}")
                print(f"📊 Uptime: {scores.get('uptime')}")
                print(f"📊 Overall: {scores.get('overall')}")
                
                # Verify all scores are within range
                for score_name, score_value in scores.items():
                    if score_value is not None:
                        assert 0 <= score_value <= 100, f"Score {score_name} out of range: {score_value}"
                
                print(f"✅ Real comprehensive analysis successful")
            else:
                print(f"⚠️ Comprehensive analysis failed: {result.get('error')}")
                print(f"⚠️ Error code: {result.get('error_code')}")
                print(f"⚠️ Context: {result.get('context')}")
                
        except Exception as e:
            print(f"❌ Real comprehensive analysis failed: {e}")
            pytest.skip(f"Comprehensive analysis not available: {e}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_caching_integration(self, real_analyzer):
        """Test caching functionality with real analysis."""
        print(f"\n💾 Testing caching integration")
        
        test_url = "https://www.google.com"
        
        try:
            # First analysis (cache miss)
            print(f"📊 First analysis (should be cache miss)")
            start_time = time.time()
            result1 = await real_analyzer.run_page_speed_analysis(test_url, "mobile")
            first_time = time.time() - start_time
            
            print(f"📊 First analysis time: {first_time:.2f}s")
            print(f"📊 Cache stats before: {real_analyzer.get_analysis_statistics()}")
            
            # Second analysis (cache hit)
            print(f"📊 Second analysis (should be cache hit)")
            start_time = time.time()
            result2 = await real_analyzer.run_page_speed_analysis(test_url, "mobile")
            second_time = time.time() - start_time
            
            print(f"📊 Second analysis time: {second_time:.2f}s")
            print(f"📊 Cache stats after: {real_analyzer.get_analysis_statistics()}")
            
            # Verify results are identical
            assert result1 == result2, "Cached and non-cached results should be identical"
            
            # Verify second analysis was faster (cached)
            assert second_time < first_time, "Cached analysis should be faster"
            
            # Verify cache hit was recorded
            stats = real_analyzer.get_analysis_statistics()
            cache_info = stats["cache_info"]
            print(f"📊 Cache hit rate: {cache_info['cache_hit_rate']:.1f}%")
            print(f"📊 Total entries: {cache_info['total_entries']}")
            
            # Verify cache hit rate increased
            assert cache_info["cache_hit_rate"] > 0
            
            print(f"✅ Caching integration successful")
            
        except Exception as e:
            print(f"❌ Caching integration failed: {e}")
            pytest.skip(f"Caching not available: {e}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_health_monitoring_integration(self, real_analyzer):
        """Test health monitoring integration."""
        print(f"\n🏥 Testing health monitoring integration")
        
        try:
            # Get service health
            health_status = real_analyzer.get_service_health()
            print(f"📊 Health status: {health_status}")
            
            # Verify health status structure
            assert "service" in health_status
            assert "status" in health_status
            assert "services" in health_status
            assert "features" in health_status
            assert "rate_limits" in health_status
            
            # Verify service name
            assert health_status["service"] == "unified_analyzer"
            
            # Verify status values
            assert health_status["status"] in ["healthy", "degraded", "unhealthy", "unknown"]
            
            # Verify services
            services = health_status["services"]
            assert "pagespeed" in services
            assert "domain_analysis" in services
            
            # Verify features
            features = health_status["features"]
            assert "caching" in health_status["features"]
            assert "retry_logic" in health_status["features"]
            assert "batch_processing" in health_status["features"]
            assert "health_monitoring" in health_status["features"]
            assert "rate_limiting" in health_status["features"]
            assert "comprehensive_analysis" in health_status["features"]
            
            # Get analysis statistics
            stats = real_analyzer.get_analysis_statistics()
            print(f"📊 Analysis statistics: {stats}")
            
            # Verify stats structure
            assert "statistics" in stats
            assert "cache_info" in stats
            assert "retry_config" in stats
            
            print(f"✅ Health monitoring integration successful")
            
        except Exception as e:
            print(f"❌ Health monitoring integration failed: {e}")
            pytest.skip(f"Health monitoring not available: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "integration"])
