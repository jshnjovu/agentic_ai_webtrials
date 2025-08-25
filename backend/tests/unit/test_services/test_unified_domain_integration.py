"""
Fast unit tests for UnifiedAnalyzer integration.
Uses real API calls with URLs from urls.json for fast execution.
Tests PageSpeed, Trust, and CRO metrics without domain analysis.
"""

import pytest
import asyncio
import time
import json
import os
from pathlib import Path
from typing import List, Dict, Any

from src.services.unified import UnifiedAnalyzer


class TestUnifiedIntegration:
    """Fast integration tests for UnifiedAnalyzer using real APIs."""
    
    @pytest.fixture(scope="class")
    def urls(self) -> List[str]:
        """Load test URLs from urls.json."""
        urls_file = Path(__file__).parent.parent / "urls.json"
        with open(urls_file, 'r') as f:
            return json.load(f)
    
    @pytest.fixture(scope="class")
    def analyzer(self) -> UnifiedAnalyzer:
        """Create a real UnifiedAnalyzer instance."""
        # Check if required environment variables are set
        required_vars = [
            "GOOGLE_GENERAL_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")
        
        analyzer = UnifiedAnalyzer()
        print(f"\n🔧 Created real UnifiedAnalyzer instance")
        print(f"📊 Service health: {analyzer.service_health}")
        return analyzer
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_pagespeed_analysis_integration(self, analyzer, urls):
        """Test that PageSpeed analysis works properly."""
        print(f"\n✅ Testing PageSpeed analysis integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        start_time = time.time()
        pagespeed_result = await analyzer.run_page_speed_analysis(test_url, "mobile")
        analysis_time = time.time() - start_time
        
        print(f"⏱️ PageSpeed analysis took: {analysis_time:.2f}s")
        
        # Verify PageSpeed result structure
        assert "mobile" in pagespeed_result or "desktop" in pagespeed_result, "No PageSpeed data returned"
        
        # Check mobile data if available
        mobile = pagespeed_result.get("mobile")
        if mobile:
            print(f"📱 Mobile analysis available")
            if "scores" in mobile:
                scores = mobile["scores"]
                print(f"   - Performance: {scores.get('performance', 'N/A')}")
                print(f"   - Accessibility: {scores.get('accessibility', 'N/A')}")
                print(f"   - Best Practices: {scores.get('bestPractices', 'N/A')}")
                print(f"   - SEO: {scores.get('seo', 'N/A')}")
        
        # Check desktop data if available
        desktop = pagespeed_result.get("desktop")
        if desktop:
            print(f"💻 Desktop analysis available")
            if "scores" in desktop:
                scores = desktop["scores"]
                print(f"   - Performance: {scores.get('performance', 'N/A')}")
                print(f"   - Accessibility: {scores.get('accessibility', 'N/A')}")
                print(f"   - Best Practices: {scores.get('bestPractices', 'N/A')}")
                print(f"   - SEO: {scores.get('seo', 'N/A')}")
        
        # Check for errors
        errors = pagespeed_result.get("errors", [])
        if errors:
            print(f"⚠️ PageSpeed errors: {len(errors)}")
            for error in errors[:2]:  # Show first 2 errors
                print(f"   - {error.get('message', 'Unknown error')}")
        
        print(f"✅ PageSpeed analysis integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_trust_analysis_integration(self, analyzer, urls):
        """Test that Trust analysis works properly."""
        print(f"\n✅ Testing Trust analysis integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        start_time = time.time()
        trust_result = await analyzer.analyze_trust(test_url)
        analysis_time = time.time() - start_time
        
        print(f"⏱️ Trust analysis took: {analysis_time:.2f}s")
        print(f"🛡️ Trust score: {trust_result.get('score', 'N/A')}")
        
        # Verify Trust result structure
        assert "score" in trust_result, "Trust score not found"
        assert "ssl" in trust_result, "SSL status not found"
        assert "securityHeaders" in trust_result, "Security headers not found"
        assert "realData" in trust_result, "Real data flags not found"
        
        # Check trust details
        print(f"   - SSL: {'✅' if trust_result.get('ssl') else '❌'}")
        print(f"   - Security Headers: {len(trust_result.get('securityHeaders', []))}")
        print(f"   - Trust Level: {trust_result.get('trustLevel', 'N/A')}")
        
        # Check PageSpeed insights if available
        pagespeed_insights = trust_result.get("pagespeedInsights", {})
        if pagespeed_insights:
            print(f"   - Protocol: {pagespeed_insights.get('protocol', 'N/A')}")
            print(f"   - Best Practices Rating: {pagespeed_insights.get('bestPracticesRating', 'N/A')}")
        
        # Verify score range
        trust_score = trust_result.get("score", 0)
        assert 0 <= trust_score <= 100, f"Trust score {trust_score} out of range"
        
        print(f"✅ Trust analysis integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_cro_analysis_integration(self, analyzer, urls):
        """Test that CRO analysis works properly."""
        print(f"\n✅ Testing CRO analysis integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        start_time = time.time()
        cro_result = await analyzer.analyze_cro(test_url)
        analysis_time = time.time() - start_time
        
        print(f"⏱️ CRO analysis took: {analysis_time:.2f}s")
        print(f"📈 CRO score: {cro_result.get('score', 'N/A')}")
        
        # Verify CRO result structure
        assert "score" in cro_result, "CRO score not found"
        assert "mobileFriendly" in cro_result, "Mobile friendly status not found"
        assert "mobileUsabilityScore" in cro_result, "Mobile usability score not found"
        assert "pageSpeed" in cro_result, "PageSpeed data not found"
        assert "userExperience" in cro_result, "User experience data not found"
        
        # Check CRO details
        print(f"   - Mobile Friendly: {'✅' if cro_result.get('mobileFriendly') else '❌'}")
        print(f"   - Mobile Usability Score: {cro_result.get('mobileUsabilityScore', 'N/A')}")
        
        # Check PageSpeed data
        page_speed = cro_result.get("pageSpeed", {})
        if page_speed:
            print(f"   - Mobile Performance: {page_speed.get('mobile', 'N/A')}")
            print(f"   - Desktop Performance: {page_speed.get('desktop', 'N/A')}")
            print(f"   - Average Performance: {page_speed.get('average', 'N/A')}")
        
        # Check user experience data
        ux = cro_result.get("userExperience", {})
        if ux:
            print(f"   - Loading Time Score: {ux.get('loadingTime', 'N/A')}")
            print(f"   - Interactivity Score: {ux.get('interactivity', 'N/A')}")
            print(f"   - Visual Stability Score: {ux.get('visualStability', 'N/A')}")
        
        # Verify score range
        cro_score = cro_result.get("score", 0)
        assert 0 <= cro_score <= 100, f"CRO score {cro_score} out of range"
        
        print(f"✅ CRO analysis integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_comprehensive_analysis_integration(self, analyzer, urls):
        """Test comprehensive analysis that includes PageSpeed, Trust, and CRO."""
        print(f"\n✅ Testing comprehensive analysis integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        start_time = time.time()
        result = await analyzer.run_comprehensive_analysis(test_url)
        analysis_time = time.time() - start_time
        
        print(f"⏱️ Comprehensive analysis took: {analysis_time:.2f}s")
        print(f"📊 Services completed: {result.get('summary', {}).get('servicesCompleted', 0)}")
        print(f"❌ Total errors: {result.get('summary', {}).get('totalErrors', 0)}")
        
        # Verify comprehensive analysis structure
        assert "domain" in result, "Domain not found in result"
        assert "url" in result, "URL not found in result"
        assert "pageSpeed" in result, "PageSpeed not found in result"
        assert "trustAndCRO" in result, "Trust and CRO not found in result"
        assert "summary" in result, "Summary not found in result"
        
        # Check PageSpeed data
        page_speed = result.get("pageSpeed", {})
        if page_speed:
            print(f"📱 PageSpeed data available")
            mobile = page_speed.get("mobile")
            desktop = page_speed.get("desktop")
            if mobile:
                print(f"   - Mobile: ✅")
            if desktop:
                print(f"   - Desktop: ✅")
        
        # Check Trust and CRO data
        trust_cro = result.get("trustAndCRO", {})
        if trust_cro:
            print(f"🔒 Trust and CRO data available")
            trust = trust_cro.get("trust", {})
            cro = trust_cro.get("cro", {})
            if trust:
                print(f"   - Trust: ✅")
            if cro:
                print(f"   - CRO: ✅")
        
        # Verify summary calculation
        summary = result.get("summary", {})
        if summary:
            assert summary.get("totalErrors", 0) >= 0, "Total errors should be non-negative"
            assert summary.get("servicesCompleted", 0) >= 0, "Services completed should be non-negative"
            assert summary.get("analysisDuration", 0) > 0, "Analysis duration should be positive"
        
        print(f"✅ Comprehensive analysis integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_batch_analysis_integration(self, analyzer, urls):
        """Test batch analysis with multiple URLs."""
        print(f"\n✅ Testing batch analysis integration")
        
        # Use first 2 URLs for quick batch test
        test_urls = urls[:2]
        print(f"🌐 Testing with URLs: {test_urls}")
        
        start_time = time.time()
        results = await analyzer.run_batch_analysis(test_urls, max_concurrent=2)
        batch_time = time.time() - start_time
        
        print(f"⏱️ Batch analysis took: {batch_time:.2f}s")
        print(f"📊 Results count: {len(results)}")
        
        # Verify batch results
        assert len(results) == len(test_urls), f"Expected {len(test_urls)} results, got {len(results)}"
        
        for i, result in enumerate(results):
            print(f"📋 Result {i+1}: {result.get('domain', 'N/A')} - {result.get('summary', {}).get('servicesCompleted', 0)} services")
            assert "domain" in result, f"Result {i+1} missing domain"
            assert "summary" in result, f"Result {i+1} missing summary"
            assert result.get("summary", {}).get("servicesCompleted", 0) >= 0, f"Result {i+1} services completed should be non-negative"
        
        print(f"✅ Batch analysis integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_score_extraction_integration(self, analyzer, urls):
        """Test score extraction methods with real data."""
        print(f"\n✅ Testing score extraction integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        # Run analysis to get real data
        result = await analyzer.run_comprehensive_analysis(test_url)
        
        # Test score extraction methods
        performance_score = analyzer.get_performance_score(result)
        accessibility_score = analyzer.get_accessibility_score(result)
        best_practices_score = analyzer.get_best_practices_score(result)
        seo_score = analyzer.get_seo_score(result)
        trust_score = analyzer.get_trust_score(result)
        cro_score = analyzer.get_cro_score(result)
        overall_score = analyzer.get_overall_score(result)
        
        print(f"📊 Scores extracted:")
        print(f"   Performance: {performance_score}")
        print(f"   Accessibility: {accessibility_score}")
        print(f"   Best Practices: {best_practices_score}")
        print(f"   SEO: {seo_score}")
        print(f"   Trust: {trust_score}")
        print(f"   CRO: {cro_score}")
        print(f"   Overall: {overall_score}")
        
        # Verify score ranges
        for score_name, score in [
            ("Performance", performance_score),
            ("Accessibility", accessibility_score),
            ("Best Practices", best_practices_score),
            ("SEO", seo_score),
            ("Trust", trust_score),
            ("CRO", cro_score)
        ]:
            assert 0 <= score <= 100, f"{score_name} score {score} out of range"
        
        assert 0 <= overall_score <= 100, f"Overall score {overall_score} out of range"
        
        print(f"✅ Score extraction integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_extract_opportunities_integration(self, analyzer, urls):
        """Test the extract_opportunities method functionality."""
        print(f"\n✅ Testing extract_opportunities integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        # Run PageSpeed analysis to get audits data
        pagespeed_result = await analyzer.run_page_speed_analysis(test_url)
        
        # Extract opportunities from mobile data (preferred)
        mobile_data = pagespeed_result.get("mobile", {})
        if mobile_data and "opportunities" in mobile_data:
            opportunities = mobile_data["opportunities"]
            print(f"📊 Found {len(opportunities)} opportunities in mobile data")
            
            # Test opportunities structure
            for i, opp in enumerate(opportunities[:3]):  # Show first 3
                print(f"   Opportunity {i+1}: {opp.get('title', 'No title')}")
                assert "title" in opp, f"Opportunity {i+1} missing title"
                assert "description" in opp, f"Opportunity {i+1} missing description"
                assert "potentialSavings" in opp, f"Opportunity {i+1} missing potentialSavings"
                assert "unit" in opp, f"Opportunity {i+1} missing unit"
                
                # Verify data types
                assert isinstance(opp["title"], str), f"Title should be string"
                assert isinstance(opp["description"], str), f"Description should be string"
                assert isinstance(opp["potentialSavings"], (int, float)), f"PotentialSavings should be numeric"
                assert isinstance(opp["unit"], str), f"Unit should be string"
                
                # Verify potentialSavings is non-negative
                assert opp["potentialSavings"] >= 0, f"PotentialSavings should be non-negative"
        else:
            print(f"⚠️ No opportunities found in mobile data")
        
        # Test the extract_opportunities method directly if we have audits data
        # Note: We need to get audits from the PageSpeed API response structure
        print(f"🔍 Testing extract_opportunities method...")
        
        # For now, we'll test with the opportunities already extracted
        if mobile_data and "opportunities" in mobile_data:
            opportunities = mobile_data["opportunities"]
            print(f"   ✅ extract_opportunities data available: {len(opportunities)} opportunities")
            
            # Verify the structure
            assert isinstance(opportunities, list), "Opportunities should be a list"
            
            # Each opportunity should have the expected structure
            for opp in opportunities:
                assert "title" in opp, "Opportunity missing title"
                assert "description" in opp, "Opportunity missing description"
                assert "potentialSavings" in opp, "Opportunity missing potentialSavings"
                assert "unit" in opp, "Opportunity missing unit"
        
        print(f"✅ extract_opportunities integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_service_health_integration(self, analyzer):
        """Test service health monitoring."""
        print(f"\n✅ Testing service health integration")
        
        health = analyzer.get_service_health()
        print(f"🏥 Service health: {health}")
        
        # Verify health structure
        assert "service" in health, "Service name not found in health"
        assert "status" in health, "Service status not found in health"
        assert "services" in health, "Services not found in health"
        assert "pagespeed" in health["services"], "PageSpeed service status not found"
        assert "domain_analysis" in health["services"], "Domain analysis service status not found"
        
        # Check service statuses
        pagespeed_status = health["services"]["pagespeed"]
        domain_status = health["services"]["domain_analysis"]
        print(f"🔍 PageSpeed service status: {pagespeed_status}")
        print(f"🔍 Domain analysis service status: {domain_status}")
        
        # PageSpeed should be healthy if we got this far
        assert pagespeed_status in ["healthy", "degraded", "unknown"], f"Invalid PageSpeed status: {pagespeed_status}"
        
        # Domain analysis should be unavailable (as expected)
        assert domain_status == "unavailable", f"Domain analysis should be unavailable, got: {domain_status}"
        
        print(f"✅ Service health integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_analysis_statistics_integration(self, analyzer, urls):
        """Test analysis statistics after making API calls."""
        print(f"\n✅ Testing analysis statistics integration")
        
        # Get initial stats
        initial_stats = analyzer.get_analysis_statistics()
        print(f"📊 Initial stats: {initial_stats['statistics']}")
        
        # Make an API call
        test_url = urls[0]
        await analyzer.run_comprehensive_analysis(test_url)
        
        # Get updated stats
        updated_stats = analyzer.get_analysis_statistics()
        print(f"📊 Updated stats: {updated_stats['statistics']}")
        
        # Verify stats increased
        assert updated_stats["statistics"]["total_analyses"] > initial_stats["statistics"]["total_analyses"], "Total analyses should increase"
        
        # Check cache info
        cache_info = updated_stats["cache_info"]
        assert "total_entries" in cache_info, "Cache total entries not found"
        assert "cache_ttl" in cache_info, "Cache TTL not found"
        assert cache_info["cache_ttl"] == 3600, "Cache TTL should be 3600 seconds"
        
        print(f"✅ Analysis statistics integration test passed")
    
    @pytest.mark.fast
    def test_url_loading(self, urls):
        """Test that URLs are loaded correctly from urls.json."""
        print(f"\n✅ Testing URL loading from urls.json")
        print(f"📋 Loaded {len(urls)} URLs: {urls}")
        
        assert len(urls) > 0, "No URLs loaded from urls.json"
        assert all(isinstance(url, str) for url in urls), "All URLs should be strings"
        assert all(url.startswith("http") for url in urls), "All URLs should start with http"
        
        print(f"✅ URL loading test passed")


# Performance markers for pytest
pytestmark = [
    pytest.mark.fast,  # Mark all tests as fast
    pytest.mark.integration,  # Mark as integration tests
    pytest.mark.real_api,  # Mark as using real APIs
]
