"""
Fast unit tests for UnifiedAnalyzer + DomainAnalysis integration.
Uses real API calls with URLs from urls.json for fast execution.
"""

import pytest
import asyncio
import time
import json
import os
from pathlib import Path
from typing import List, Dict, Any

from src.services.unified import UnifiedAnalyzer
from src.services.domain_analysis import DomainAnalysisService


class TestUnifiedDomainIntegration:
    """Fast integration tests for UnifiedAnalyzer + DomainAnalysis using real APIs."""
    
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
            "GOOGLE_GENERAL_API_KEY",
            "WHOIS_API_KEY",
            "WHOIS_API_BASE_URL",
            "WHOIS_HISTORY_API_BASE_URL"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            pytest.skip(f"Missing required environment variables: {missing_vars}")
        
        analyzer = UnifiedAnalyzer()
        print(f"\n🔧 Created real UnifiedAnalyzer instance")
        print(f"📊 Service health: {analyzer.service_health}")
        return analyzer
    
    @pytest.fixture(scope="class")
    def domain_service(self) -> DomainAnalysisService:
        """Create a real DomainAnalysisService instance."""
        try:
            service = DomainAnalysisService()
            print(f"🔧 Created real DomainAnalysisService instance")
            return service
        except Exception as e:
            pytest.skip(f"DomainAnalysisService not available: {e}")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_domain_analysis_integration(self, analyzer, domain_service, urls):
        """Test that domain analysis integrates properly with unified analyzer."""
        print(f"\n✅ Testing domain analysis integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        # Test domain analysis directly
        domain = test_url.replace("http://", "").replace("https://", "").split("/")[0]
        print(f"🔍 Analyzing domain: {domain}")
        
        start_time = time.time()
        domain_result = await domain_service.analyze_domain(domain)
        domain_time = time.time() - start_time
        
        print(f"⏱️ Domain analysis took: {domain_time:.2f}s")
        print(f"📊 Domain age: {domain_result['domainAge']['ageDescription']}")
        print(f"🏆 Credibility score: {domain_result['analysis']['credibility']}")
        
        # Verify domain analysis structure
        assert "domainAge" in domain_result
        assert "analysis" in domain_result
        assert "whois" in domain_result
        assert domain_result["domain"] == domain
        assert domain_result["analysis"]["credibility"] >= 0
        assert domain_result["analysis"]["credibility"] <= 100
        
        print(f"✅ Domain analysis integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_whois_data_integration(self, analyzer, urls):
        """Test WHOIS data integration in unified analyzer."""
        print(f"\n✅ Testing WHOIS data integration")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        start_time = time.time()
        whois_data = await analyzer._get_whois_data(test_url)
        whois_time = time.time() - start_time
        
        print(f"⏱️ WHOIS data retrieval took: {whois_time:.2f}s")
        print(f"📊 Domain: {whois_data['domain']}")
        print(f"🏆 Credibility: {whois_data['credibility']}")
        
        # Verify WHOIS data structure
        assert "domain" in whois_data
        assert "timestamp" in whois_data
        assert "whois" in whois_data
        assert "credibility" in whois_data
        assert whois_data["domain"] in test_url
        
        print(f"✅ WHOIS data integration test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_comprehensive_analysis_with_domain(self, analyzer, urls):
        """Test comprehensive analysis that includes domain insights."""
        print(f"\n✅ Testing comprehensive analysis with domain insights")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        start_time = time.time()
        result = await analyzer.run_comprehensive_analysis(test_url)
        analysis_time = time.time() - start_time
        
        print(f"⏱️ Comprehensive analysis took: {analysis_time:.2f}s")
        print(f"📊 Services completed: {result['summary']['servicesCompleted']}")
        print(f"❌ Total errors: {result['summary']['totalErrors']}")
        
        # Verify comprehensive analysis structure
        assert "domain" in result
        assert "url" in result
        assert "pageSpeed" in result
        assert "whois" in result
        assert "summary" in result
        
        # Check if domain insights were integrated
        if "domainInsights" in result:
            print(f"🏆 Domain insights found: {result['domainInsights']}")
            assert "businessMaturity" in result["domainInsights"]
            assert "credibility" in result["domainInsights"]
        else:
            print(f"⚠️ No domain insights found (may be expected for some URLs)")
        
        # Verify summary calculation
        assert result["summary"]["totalErrors"] >= 0
        assert result["summary"]["servicesCompleted"] >= 0
        assert result["summary"]["analysisDuration"] > 0
        
        print(f"✅ Comprehensive analysis with domain test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_batch_analysis_with_domains(self, analyzer, urls):
        """Test batch analysis with multiple URLs."""
        print(f"\n✅ Testing batch analysis with domains")
        
        # Use first 2 URLs for quick batch test
        test_urls = urls[:2]
        print(f"🌐 Testing with URLs: {test_urls}")
        
        start_time = time.time()
        results = await analyzer.run_batch_analysis(test_urls, max_concurrent=2)
        batch_time = time.time() - start_time
        
        print(f"⏱️ Batch analysis took: {batch_time:.2f}s")
        print(f"📊 Results count: {len(results)}")
        
        # Verify batch results
        assert len(results) == len(test_urls)
        
        for i, result in enumerate(results):
            print(f"📋 Result {i+1}: {result['domain']} - {result['summary']['servicesCompleted']} services")
            assert "domain" in result
            assert "summary" in result
            assert result["summary"]["servicesCompleted"] >= 0
        
        print(f"✅ Batch analysis with domains test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_score_extraction_with_domain_data(self, analyzer, urls):
        """Test score extraction methods with real domain data."""
        print(f"\n✅ Testing score extraction with domain data")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        # Run analysis to get real data
        result = await analyzer.run_comprehensive_analysis(test_url)
        
        # Test score extraction methods
        performance_score = analyzer.get_performance_score(result)
        accessibility_score = analyzer.get_accessibility_score(result)
        seo_score = analyzer.get_seo_score(result)
        trust_score = analyzer.get_trust_score(result)
        cro_score = analyzer.get_cro_score(result)
        overall_score = analyzer.get_overall_score(result)
        
        print(f"📊 Scores extracted:")
        print(f"   Performance: {performance_score}")
        print(f"   Accessibility: {accessibility_score}")
        print(f"   SEO: {seo_score}")
        print(f"   Trust: {trust_score}")
        print(f"   CRO: {cro_score}")
        print(f"   Overall: {overall_score}")
        
        # Verify score ranges
        for score_name, score in [
            ("Performance", performance_score),
            ("Accessibility", accessibility_score),
            ("SEO", seo_score),
            ("Trust", trust_score),
            ("CRO", cro_score)
        ]:
            assert 0 <= score <= 100, f"{score_name} score {score} out of range"
        
        assert 0 <= overall_score <= 100, f"Overall score {overall_score} out of range"
        
        # Test scores summary
        scores_summary = analyzer.get_scores_summary(result)
        print(f"📋 Scores summary: {scores_summary}")
        
        # Verify all required keys are present
        required_keys = ["Performance", "Accessibility", "SEO", "Trust", "CRO", "Overall"]
        for key in required_keys:
            assert key in scores_summary, f"Missing key '{key}' in scores summary"
            assert isinstance(scores_summary[key], (int, float)), f"Score '{key}' should be numeric"
            assert 0 <= scores_summary[key] <= 100, f"Score '{key}' out of range"
        
        print(f"✅ Score extraction with domain data test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_extract_opportunities_functionality(self, analyzer, urls):
        """Test the extract_opportunities method functionality."""
        print(f"\n✅ Testing extract_opportunities functionality")
        
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
            for i, opp in enumerate(opportunities):
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
                
                # Verify potentialSavings is positive
                assert opp["potentialSavings"] > 0, f"PotentialSavings should be positive"
        else:
            print(f"⚠️ No opportunities found in mobile data")
        
        # Test the extract_opportunities method directly
        if mobile_data and "audits" in mobile_data:
            audits = mobile_data["audits"]
            opportunities = analyzer.extract_opportunities(audits)
            print(f"🔍 extract_opportunities method returned {len(opportunities)} opportunities")
            
            # Verify the method works correctly
            assert isinstance(opportunities, list), "extract_opportunities should return a list"
            
            # Each opportunity should have the expected structure
            for opp in opportunities:
                assert "title" in opp, "Opportunity missing title"
                assert "description" in opp, "Opportunity missing description"
                assert "potentialSavings" in opp, "Opportunity missing potentialSavings"
                assert "unit" in opp, "Opportunity missing unit"
        
        print(f"✅ extract_opportunities functionality test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_comprehensive_analysis_opportunities(self, analyzer, urls):
        """Test that comprehensive analysis includes opportunities data."""
        print(f"\n✅ Testing comprehensive analysis opportunities")
        
        # Use first URL for quick test
        test_url = urls[0]
        print(f"🌐 Testing with URL: {test_url}")
        
        # Run comprehensive analysis
        result = await analyzer.run_comprehensive_analysis(test_url)
        
        # Check if opportunities are included in PageSpeed data
        page_speed = result.get("pageSpeed", {})
        mobile = page_speed.get("mobile", {})
        desktop = page_speed.get("desktop", {})
        
        print(f"📱 Mobile opportunities: {len(mobile.get('opportunities', [])) if mobile else 'No mobile data'}")
        print(f"💻 Desktop opportunities: {len(desktop.get('opportunities', [])) if desktop else 'No desktop data'}")
        
        # Verify opportunities structure if present
        for strategy, data in [("mobile", mobile), ("desktop", desktop)]:
            if data and "opportunities" in data:
                opportunities = data["opportunities"]
                print(f"📊 {strategy.capitalize()} opportunities structure:")
                
                for i, opp in enumerate(opportunities[:3]):  # Show first 3
                    print(f"   {i+1}. {opp.get('title', 'No title')} - {opp.get('potentialSavings', 0)} {opp.get('unit', '')}")
                
                # Verify opportunities structure
                assert isinstance(opportunities, list), f"{strategy} opportunities should be a list"
                
                for opp in opportunities:
                    assert "title" in opp, f"{strategy} opportunity missing title"
                    assert "description" in opp, f"{strategy} opportunity missing description"
                    assert "potentialSavings" in opp, f"{strategy} opportunity missing potentialSavings"
                    assert "unit" in opp, f"{strategy} opportunity missing unit"
        
        print(f"✅ Comprehensive analysis opportunities test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_service_health_with_domain_service(self, analyzer):
        """Test service health monitoring with domain service."""
        print(f"\n✅ Testing service health with domain service")
        
        health = analyzer.get_service_health()
        print(f"🏥 Service health: {health}")
        
        # Verify health structure
        assert "service" in health
        assert "status" in health
        assert "services" in health
        assert "domain_analysis" in health["services"]
        
        # Check domain analysis service status
        domain_status = health["services"]["domain_analysis"]
        print(f"🔍 Domain analysis service status: {domain_status}")
        
        # Domain service should be healthy if we got this far
        assert domain_status in ["healthy", "degraded", "unknown"]
        
        print(f"✅ Service health with domain service test passed")
    
    @pytest.mark.asyncio
    @pytest.mark.fast
    async def test_analysis_statistics_with_domain_calls(self, analyzer, urls):
        """Test analysis statistics after making domain-related calls."""
        print(f"\n✅ Testing analysis statistics with domain calls")
        
        # Get initial stats
        initial_stats = analyzer.get_analysis_statistics()
        print(f"📊 Initial stats: {initial_stats['statistics']}")
        
        # Make a domain-related call
        test_url = urls[0]
        await analyzer.run_comprehensive_analysis(test_url)
        
        # Get updated stats
        updated_stats = analyzer.get_analysis_statistics()
        print(f"📊 Updated stats: {updated_stats['statistics']}")
        
        # Verify stats increased
        assert updated_stats["statistics"]["total_analyses"] > initial_stats["statistics"]["total_analyses"]
        
        # Check cache info
        cache_info = updated_stats["cache_info"]
        assert "total_entries" in cache_info
        assert "cache_ttl" in cache_info
        assert cache_info["cache_ttl"] == 3600  # 1 hour
        
        print(f"✅ Analysis statistics with domain calls test passed")
    
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
