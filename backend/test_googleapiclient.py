#!/usr/bin/env python3
"""
Enhanced test script to verify the updated unified.py with googleapiclient integration.
Tests CRO and TRUST metrics for multiple URLs including se1gym.co.uk and thethirdspace.com.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.unified import UnifiedAnalyzer
from src.core.config import get_api_config

async def test_unified_analyzer():
    """Test the UnifiedAnalyzer with googleapiclient integration."""
    
    print("🔧 Testing UnifiedAnalyzer with googleapiclient integration...")
    
    # Check configuration
    api_config = get_api_config()
    print(f"📋 API Config loaded:")
    print(f"   - GOOGLE_GENERAL_API_KEY: {'SET' if api_config.GOOGLE_GENERAL_API_KEY else 'NOT_SET'}")
    
    if not api_config.GOOGLE_GENERAL_API_KEY:
        print("❌ GOOGLE_GENERAL_API_KEY not configured. Please check your .env file.")
        return False
    
    # Initialize the analyzer
    try:
        analyzer = UnifiedAnalyzer()
        print(f"✅ UnifiedAnalyzer initialized successfully")
        print(f"   - PageSpeed Service: {'INITIALIZED' if analyzer.pagespeed_service else 'NOT_INITIALIZED'}")
        print(f"   - Service Health: {analyzer.service_health}")
        
        if not analyzer.pagespeed_service:
            print("❌ PageSpeed service not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize UnifiedAnalyzer: {e}")
        return False
    
    # Test URLs including the specific ones requested
    test_urls = [
        "https://www.google.com",  # Control test
        "http://www.se1gym.co.uk/",  # Requested URL 1
        "http://www.thethirdspace.com"  # Requested URL 2
    ]
    
    all_tests_passed = True
    
    for test_url in test_urls:
        print(f"\n{'='*60}")
        print(f"🚀 Testing comprehensive analysis for: {test_url}")
        print(f"{'='*60}")
        
        try:
            # Test comprehensive analysis (includes PageSpeed, Trust, and CRO)
            print(f"📊 Running comprehensive analysis...")
            result = await analyzer.run_comprehensive_analysis(test_url)
            
            if result.get("success") is False:
                print(f"❌ Comprehensive analysis failed: {result.get('error', 'Unknown error')}")
                all_tests_passed = False
                continue
            
            # Display PageSpeed results
            page_speed = result.get("pageSpeed", {})
            if page_speed:
                print(f"📱 PageSpeed Analysis:")
                mobile = page_speed.get("mobile")
                desktop = page_speed.get("desktop")
                
                if mobile and mobile.get("scores"):
                    scores = mobile["scores"]
                    print(f"   📱 Mobile Scores:")
                    print(f"      - Performance: {scores.get('performance', 'N/A')}")
                    print(f"      - Accessibility: {scores.get('accessibility', 'N/A')}")
                    print(f"      - Best Practices: {scores.get('bestPractices', 'N/A')}")
                    print(f"      - SEO: {scores.get('seo', 'N/A')}")
                
                if desktop and desktop.get("scores"):
                    scores = desktop["scores"]
                    print(f"   💻 Desktop Scores:")
                    print(f"      - Performance: {scores.get('performance', 'N/A')}")
                    print(f"      - Accessibility: {scores.get('accessibility', 'N/A')}")
                    print(f"      - Best Practices: {scores.get('bestPractices', 'N/A')}")
                    print(f"      - SEO: {scores.get('seo', 'N/A')}")
                
                # Show opportunities if available
                if mobile and mobile.get("opportunities"):
                    print(f"   📋 Mobile Opportunities: {len(mobile['opportunities'])} found")
                    for i, opp in enumerate(mobile["opportunities"][:3]):  # Show first 3
                        print(f"      {i+1}. {opp.get('title', 'No title')} - {opp.get('potentialSavings', 0)} {opp.get('unit', '')}")
                
                if page_speed.get("errors"):
                    print(f"   ⚠️ PageSpeed Errors: {len(page_speed['errors'])}")
                    for error in page_speed["errors"][:2]:  # Show first 2 errors
                        print(f"      - {error.get('message', 'Unknown error')}")
            else:
                print(f"❌ No PageSpeed data available")
            
            # Display Trust and CRO results
            trust_cro = result.get("trustAndCRO", {})
            if trust_cro:
                print(f"🔒 Trust and CRO Analysis:")
                
                # Trust analysis
                trust = trust_cro.get("trust", {})
                if trust:
                    trust_parsed = trust.get("parsed", {})
                    trust_score = trust_parsed.get("score", "N/A")
                    print(f"   🛡️ Trust Score: {trust_score}")
                    
                    # Show trust details if available
                    trust_raw = trust.get("rawResponse", {})
                    if trust_raw:
                        print(f"      - SSL: {'✅' if trust_raw.get('ssl') else '❌'}")
                        print(f"      - Security Headers: {len(trust_raw.get('securityHeaders', []))}")
                        if trust_raw.get("pagespeedInsights"):
                            insights = trust_raw["pagespeedInsights"]
                            print(f"      - Protocol: {insights.get('protocol', 'N/A')}")
                            print(f"      - Best Practices Rating: {insights.get('bestPracticesRating', 'N/A')}")
                
                # CRO analysis
                cro = trust_cro.get("cro", {})
                if cro:
                    cro_parsed = cro.get("parsed", {})
                    cro_score = cro_parsed.get("score", "N/A")
                    print(f"   📈 CRO Score: {cro_score}")
                    
                    # Show CRO details if available
                    cro_raw = cro.get("rawResponse", {})
                    if cro_raw:
                        print(f"      - Mobile Friendly: {'✅' if cro_raw.get('mobileFriendly') else '❌'}")
                        print(f"      - Mobile Usability Score: {cro_raw.get('mobileUsabilityScore', 'N/A')}")
                        if cro_raw.get("pageSpeed"):
                            ps = cro_raw["pageSpeed"]
                            print(f"      - PageSpeed Average: {ps.get('average', 'N/A')}")
                
                if trust_cro.get("errors"):
                    print(f"   ⚠️ Trust/CRO Errors: {len(trust_cro['errors'])}")
                    for error in trust_cro["errors"][:2]:  # Show first 2 errors
                        print(f"      - {error}")
            else:
                print(f"❌ No Trust/CRO data available")
            
            # Display summary
            summary = result.get("summary", {})
            if summary:
                print(f"📋 Analysis Summary:")
                print(f"   - Services Completed: {summary.get('servicesCompleted', 0)}")
                print(f"   - Total Errors: {summary.get('totalErrors', 0)}")
                print(f"   - Analysis Duration: {summary.get('analysisDuration', 0)}ms")
            
            # Test score extraction methods
            print(f"🎯 Testing Score Extraction Methods:")
            try:
                performance = analyzer.get_performance_score(result)
                accessibility = analyzer.get_accessibility_score(result)
                best_practices = analyzer.get_best_practices_score(result)
                seo = analyzer.get_seo_score(result)
                trust_score = analyzer.get_trust_score(result)
                cro_score = analyzer.get_cro_score(result)
                overall = analyzer.get_overall_score(result)
                
                print(f"   📊 Extracted Scores:")
                print(f"      - Performance: {performance}")
                print(f"      - Accessibility: {accessibility}")
                print(f"      - Best Practices: {best_practices}")
                print(f"      - SEO: {seo}")
                print(f"      - Trust: {trust_score}")
                print(f"      - CRO: {cro_score}")
                print(f"      - Overall: {overall}")
                
                # Verify score ranges
                scores = [performance, accessibility, best_practices, seo, trust_score, cro_score, overall]
                if all(0 <= score <= 100 for score in scores):
                    print(f"   ✅ All scores are within valid range (0-100)")
                else:
                    print(f"   ⚠️ Some scores are outside valid range")
                    all_tests_passed = False
                
            except Exception as e:
                print(f"   ❌ Score extraction failed: {e}")
                all_tests_passed = False
            
            print(f"✅ Analysis completed for {test_url}")
            
        except Exception as e:
            print(f"❌ Analysis failed for {test_url}: {e}")
            all_tests_passed = False
    
    # Test service health and statistics
    print(f"\n{'='*60}")
    print(f"🏥 Testing Service Health and Statistics")
    print(f"{'='*60}")
    
    try:
        health = analyzer.get_service_health()
        print(f"📊 Service Health: {health['status']}")
        print(f"   - PageSpeed: {health['services']['pagespeed']}")
        print(f"   - Domain Analysis: {health['services']['domain_analysis']}")
        print(f"   - Features: {list(health['features'].keys())}")
        
        stats = analyzer.get_analysis_statistics()
        print(f"📈 Analysis Statistics:")
        print(f"   - Total Analyses: {stats['statistics']['total_analyses']}")
        print(f"   - Successful: {stats['statistics']['successful_analyses']}")
        print(f"   - Failed: {stats['statistics']['failed_analyses']}")
        print(f"   - Cache Hit Rate: {stats['cache_info']['cache_hit_rate']:.1f}%")
        
    except Exception as e:
        print(f"❌ Service health/statistics check failed: {e}")
        all_tests_passed = False
    
    return all_tests_passed

def main():
    """Main test function."""
    print("🧪 Enhanced Testing of UnifiedAnalyzer with googleapiclient integration")
    print("=" * 80)
    print("Testing URLs:")
    print("  - https://www.google.com (control)")
    print("  - http://www.se1gym.co.uk/ (requested)")
    print("  - http://www.thethirdspace.com (requested)")
    print("=" * 80)
    
    try:
        success = asyncio.run(test_unified_analyzer())
        
        if success:
            print("\n🎉 All tests passed! The enhanced googleapiclient integration is working correctly.")
            print("✅ All metrics (Performance, Accessibility, Best Practices, SEO, Trust, CRO) are functioning.")
        else:
            print("\n💥 Some tests failed. Please check the configuration and try again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
