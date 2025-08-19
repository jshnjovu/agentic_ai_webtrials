#!/usr/bin/env python3
"""
Test script for the new Comprehensive Speed Service.
Demonstrates the enhanced PageSpeed and Pingdom integration.
"""

import asyncio
import json
import time
from datetime import datetime
from src.services.comprehensive_speed_service import ComprehensiveSpeedService
from src.services.google_pagespeed_service import GooglePageSpeedService
from src.services.pingdom_service import PingdomService


async def test_comprehensive_speed_service():
    """Test the comprehensive speed service."""
    print("🚀 Testing Comprehensive Speed Service")
    print("=" * 60)
    
    # Initialize service
    service = ComprehensiveSpeedService()
    
    # Test websites
    test_websites = [
        {
            "url": "https://www.google.com",
            "business_id": "test_business_001",
            "name": "Google"
        },
        {
            "url": "https://www.github.com", 
            "business_id": "test_business_002",
            "name": "GitHub"
        }
    ]
    
    print(f"📊 Testing {len(test_websites)} websites...")
    
    for website in test_websites:
        print(f"\n🔍 Analyzing: {website['name']} ({website['url']})")
        print("-" * 40)
        
        try:
            # Run comprehensive analysis
            result = await service.run_comprehensive_analysis(
                website_url=website['url'],
                business_id=website['business_id'],
                run_id=f"test_run_{int(time.time())}",
                strategy="mobile",
                include_pingdom=True
            )
            
            if result.get("success"):
                scores = result.get("scores", {})
                print(f"✅ Analysis completed in {result.get('analysis_time', 0):.2f}s")
                print(f"🏆 Overall Score: {scores.get('overall', 0)}/100")
                print(f"📱 Performance: {scores.get('performance', 0)}/100")
                print(f"♿ Accessibility: {scores.get('accessibility', 0)}/100")
                print(f"🔒 Best Practices: {scores.get('best_practices', 0)}/100")
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
    health = service.get_service_health()
    print(f"Status: {health['status']}")
    print(f"PageSpeed: {health['services']['pagespeed']}")
    print(f"Pingdom: {health['services']['pingdom']}")
    print(f"Features: {', '.join(health['features'].keys())}")


async def test_hybrid_audit():
    """Test the hybrid audit functionality."""
    print(f"\n🔄 Testing Hybrid Audit")
    print("=" * 60)
    
    service = ComprehensiveSpeedService()
    
    test_url = "https://www.google.com"
    business_id = "test_business_003"
    
    print(f"🔍 Running hybrid audit for: {test_url}")
    
    try:
        result = await service.run_hybrid_audit(
            website_url=test_url,
            business_id=business_id,
            run_id=f"hybrid_test_{int(time.time())}",
            strategy="mobile"
        )
        
        if result.get("success"):
            print(f"✅ Hybrid audit completed")
            print(f"📊 Scoring Method: {result.get('scoring_method')}")
            print(f"🔧 Services Used: {', '.join(result.get('services_used', []))}")
            
            if "scores" in result:
                scores = result["scores"]
                print(f"🏆 Overall: {scores.get('overall', 0)}/100")
                print(f"📱 Performance: {scores.get('performance', 0)}/100")
                print(f"🛡️ Trust: {scores.get('trust', 0)}/100")
                print(f"💰 CRO: {scores.get('cro', 0)}/100")
        else:
            print(f"❌ Hybrid audit failed: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error in hybrid audit: {e}")


async def test_batch_analysis():
    """Test batch analysis functionality."""
    print(f"\n📦 Testing Batch Analysis")
    print("=" * 60)
    
    service = ComprehensiveSpeedService()
    
    batch_requests = [
        {
            "website_url": "https://www.google.com",
            "business_id": "batch_001",
            "strategy": "mobile"
        },
        {
            "website_url": "https://www.github.com",
            "business_id": "batch_002", 
            "strategy": "mobile"
        }
    ]
    
    print(f"📊 Running batch analysis for {len(batch_requests)} websites...")
    
    try:
        results = await service.run_batch_analysis(
            analysis_requests=batch_requests,
            max_concurrent=2,
            include_pingdom=True
        )
        
        successful = [r for r in results if r.get("success")]
        failed = [r for r in results if not r.get("success")]
        
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        
        # Generate summary
        if successful:
            summary = await service.get_analysis_summary(results)
            print(f"\n📋 Analysis Summary")
            print("-" * 40)
            print(f"Total Websites: {summary.get('total_websites', 0)}")
            print(f"Average Overall Score: {summary.get('average_scores', {}).get('overall', 0)}/100")
            print(f"Top Performer: {summary.get('top_performers', [{}])[0].get('website_url', 'N/A')}")
            
            if "insights" in summary:
                print(f"\n💡 Insights:")
                for insight in summary["insights"]:
                    print(f"  • {insight}")
                    
    except Exception as e:
        print(f"❌ Error in batch analysis: {e}")


async def main():
    """Main test function."""
    print("🧪 Comprehensive Speed Service Test Suite")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Comprehensive Speed Service
        await test_comprehensive_speed_service()
        
        # Test 2: Hybrid Audit
        await test_hybrid_audit()
        
        # Test 3: Batch Analysis
        await test_batch_analysis()
        
        print(f"\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
