#!/usr/bin/env python3
"""
Test script for the enhanced Unified Analyzer.
Demonstrates the comprehensive website analysis capabilities.
"""

import asyncio
import json
import time
from datetime import datetime
from src.services.unified import UnifiedAnalyzer


async def test_unified_analyzer():
    """Test the unified analyzer service."""
    print("🚀 Testing Enhanced Unified Analyzer")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = UnifiedAnalyzer()
    
    # Test websites
    test_websites = [
        {
            "url": "https://www.google.com",
            "name": "Google"
        },
        {
            "url": "https://www.github.com", 
            "name": "GitHub"
        }
    ]
    
    print(f"📊 Testing {len(test_websites)} websites...")
    
    for website in test_websites:
        print(f"\n🔍 Analyzing: {website['name']} ({website['url']})")
        print("-" * 40)
        
        try:
            # Run comprehensive analysis
            result = await analyzer.run_comprehensive_analysis(
                url=website['url'],
                strategy="mobile"
            )
            
            if result.get("success"):
                scores = result.get("scores", {})
                print(f"✅ Analysis completed in {result.get('analysis_time', 0):.2f}s")
                print(f"🏆 Overall Score: {scores.get('overall', 0)}/100")
                print(f"📱 Performance: {scores.get('performance', 0)}/100")
                print(f"♿ Accessibility: {scores.get('accessibility', 0)}/100")
                print(f"🔒 Best Practices: {scores.get('bestPractices', 0)}/100")
                print(f"🔍 SEO: {scores.get('seo', 0)}/100")
                print(f"🛡️ Trust: {scores.get('trust', 0)}/100")
                print(f"💰 CRO: {scores.get('cro', 0)}/100")
                print(f"🔧 Services Used: {', '.join(result.get('services_used', []))}")
            else:
                print(f"❌ Analysis failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error analyzing {website['name']}: {e}")
    
    # Test service health
    print(f"\n🏥 Service Health Check")
    print("-" * 40)
    health = analyzer.get_service_health()
    print(f"Status: {health['status']}")
    print(f"PageSpeed: {health['services']['pagespeed']}")
    print(f"Domain Analysis: {health['services']['domain_analysis']}")
    print(f"Features: {', '.join(health['features'].keys())}")


async def test_comprehensive_analysis():
    """Test the comprehensive analysis functionality."""
    print(f"\n🔍 Testing Comprehensive Analysis")
    print("=" * 60)
    
    analyzer = UnifiedAnalyzer()
    
    test_url = "https://www.google.com"
    
    print(f"🔍 Running comprehensive analysis for: {test_url}")
    
    try:
        result = await analyzer.run_comprehensive_analysis(
            url=test_url,
            strategy="mobile"
        )
        
        if result.get("success"):
            print(f"✅ Comprehensive analysis completed")
            print(f"🔧 Services Used: {', '.join(result.get('services_used', []))}")
            
            if "scores" in result:
                scores = result["scores"]
                print(f"🏆 Overall: {scores.get('overall', 0)}/100")
                print(f"📱 Performance: {scores.get('performance', 0)}/100")
                print(f"🛡️ Trust: {scores.get('trust', 0)}/100")
                print(f"💰 CRO: {scores.get('cro', 0)}/100")
                print(f"📊 Uptime: {scores.get('uptime', 0)}/100")
        else:
            print(f"❌ Comprehensive analysis failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in comprehensive analysis: {e}")


async def test_batch_analysis():
    """Test batch analysis functionality."""
    print(f"\n📦 Testing Batch Analysis")
    print("=" * 60)
    
    analyzer = UnifiedAnalyzer()
    
    test_urls = [
        "https://www.google.com",
        "https://www.github.com"
    ]
    
    print(f"📊 Running batch analysis for {len(test_urls)} websites...")
    
    try:
        results = await analyzer.run_batch_analysis(
            urls=test_urls,
            strategy="mobile",
            max_concurrent=2
        )
        
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        # Show results summary
        if successful:
            print(f"\n📋 Analysis Results")
            print("-" * 40)
            for i, result in enumerate(successful):
                url = result.get("url", f"URL_{i}")
                scores = result.get("scores", {})
                overall = scores.get("overall", 0)
                analysis_time = result.get("analysis_time", 0)
                print(f"  • {url}: {overall}/100 ({analysis_time:.2f}s)")
            
            # Calculate average score
            if successful:
                avg_score = sum(r.get("scores", {}).get("overall", 0) for r in successful) / len(successful)
                print(f"\n📊 Average Overall Score: {avg_score:.1f}/100")
                    
    except Exception as e:
        print(f"❌ Error in batch analysis: {e}")


async def test_trust_analysis():
    """Test trust analysis functionality."""
    print(f"\n🛡️ Testing Trust Analysis")
    print("=" * 60)
    
    analyzer = UnifiedAnalyzer()
    
    test_url = "https://www.google.com"
    
    print(f"🔍 Running trust analysis for: {test_url}")
    
    try:
        result = await analyzer.analyze_trust(test_url)
        
        print(f"✅ Trust analysis completed")
        print(f"🛡️ Trust Score: {result.get('score', 0)}/100")
        print(f"🔒 SSL: {result.get('ssl', False)}")
        print(f"🛡️ Security Headers: {len(result.get('securityHeaders', []))}")
        print(f"📅 Domain Age: {result.get('domainAge', 'Unknown')}")
        print(f"⚠️ Warnings: {len(result.get('warnings', []))}")
        
        if result.get("warnings"):
            for warning in result["warnings"]:
                print(f"  • {warning}")
                
    except Exception as e:
        print(f"❌ Error in trust analysis: {e}")


async def test_cro_analysis():
    """Test CRO analysis functionality."""
    print(f"\n💰 Testing CRO Analysis")
    print("=" * 60)
    
    analyzer = UnifiedAnalyzer()
    
    test_url = "https://www.google.com"
    
    print(f"🔍 Running CRO analysis for: {test_url}")
    
    try:
        result = await analyzer.analyze_cro(test_url)
        
        print(f"✅ CRO analysis completed")
        print(f"💰 CRO Score: {result.get('score', 0)}/100")
        print(f"📱 Mobile Friendly: {result.get('mobileFriendly', False)}")
        print(f"📱 Mobile Usability Score: {result.get('mobileUsabilityScore', 0)}/100")
        print(f"📊 Page Speed (Mobile): {result.get('pageSpeed', {}).get('mobile', 0)}/100")
        print(f"📊 Page Speed (Desktop): {result.get('pageSpeed', {}).get('desktop', 0)}/100")
        print(f"📊 Page Speed (Average): {result.get('pageSpeed', {}).get('average', 0)}/100")
        
        # User Experience scores
        ux = result.get("userExperience", {})
        print(f"⏱️ Loading Time Score: {ux.get('loadingTime', 0)}/100")
        print(f"🔄 Interactivity Score: {ux.get('interactivity', 0)}/100")
        print(f"📐 Visual Stability Score: {ux.get('visualStability', 0)}/100")
                
    except Exception as e:
        print(f"❌ Error in CRO analysis: {e}")


async def test_uptime_analysis():
    """Test uptime analysis functionality."""
    print(f"\n🔄 Testing Uptime Analysis")
    print("=" * 60)
    
    analyzer = UnifiedAnalyzer()
    
    test_url = "https://www.google.com"
    
    print(f"🔍 Running uptime analysis for: {test_url}")
    
    try:
        result = await analyzer.analyze_uptime(test_url)
        
        print(f"✅ Uptime analysis completed")
        print(f"🔄 Uptime Score: {result.get('score', 0)}/100")
        print(f"📊 Uptime: {result.get('uptime', 'Unknown')}")
        print(f"⏱️ Average Response Time: {result.get('averageResponseTime', 0)}ms")
        print(f"📈 Status: {result.get('status', 'Unknown')}")
                
    except Exception as e:
        print(f"❌ Error in uptime analysis: {e}")


async def test_analyzer_statistics():
    """Test analyzer statistics and health monitoring."""
    print(f"\n📊 Testing Analyzer Statistics")
    print("=" * 60)
    
    analyzer = UnifiedAnalyzer()
    
    try:
        # Get health status
        health = analyzer.get_service_health()
        print(f"🏥 Health Status: {health['status']}")
        print(f"🔧 Services:")
        for service, status in health['services'].items():
            print(f"  • {service}: {status}")
        
        print(f"✨ Features:")
        for feature, enabled in health['features'].items():
            print(f"  • {feature}: {'✅' if enabled else '❌'}")
        
        # Get statistics
        stats = analyzer.get_analysis_statistics()
        print(f"\n📈 Analysis Statistics:")
        statistics = stats['statistics']
        print(f"  • Total Analyses: {statistics['total_analyses']}")
        print(f"  • Successful: {statistics['successful_analyses']}")
        print(f"  • Failed: {statistics['failed_analyses']}")
        print(f"  • Cache Hits: {statistics['cache_hits']}")
        print(f"  • Cache Misses: {statistics['cache_misses']}")
        
        # Cache info
        cache_info = stats['cache_info']
        print(f"\n💾 Cache Information:")
        print(f"  • Total Entries: {cache_info['total_entries']}")
        print(f"  • Cache TTL: {cache_info['cache_ttl']}s")
        print(f"  • Hit Rate: {cache_info['cache_hit_rate']:.1f}%")
        
        # Retry config
        retry_config = stats['retry_config']
        print(f"\n🔄 Retry Configuration:")
        print(f"  • Max Attempts: {retry_config['max_attempts']}")
        print(f"  • Base Delay: {retry_config['base_delay']}s")
        print(f"  • Max Delay: {retry_config['max_delay']}s")
        print(f"  • Exponential Backoff: {retry_config['exponential_backoff']}")
                
    except Exception as e:
        print(f"❌ Error getting analyzer statistics: {e}")


async def main():
    """Main test function."""
    print("🧪 Enhanced Unified Analyzer Test Suite")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Basic Unified Analyzer
        await test_unified_analyzer()
        
        # Test 2: Comprehensive Analysis
        await test_comprehensive_analysis()
        
        # Test 3: Batch Analysis
        await test_batch_analysis()
        
        # Test 4: Trust Analysis
        await test_trust_analysis()
        
        # Test 5: CRO Analysis
        await test_cro_analysis()
        
        # Test 6: Uptime Analysis
        await test_uptime_analysis()
        
        # Test 7: Analyzer Statistics
        await test_analyzer_statistics()
        
        print(f"\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
