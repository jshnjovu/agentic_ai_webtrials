#!/usr/bin/env python3
"""
Demo script for real Lighthouse API integration.
This script demonstrates the actual implementation using real Google PageSpeed Insights API calls.

Usage:
    python demo_real_lighthouse.py [website_url]

Examples:
    python demo_real_lighthouse.py https://www.google.com
    python demo_real_lighthouse.py https://www.github.com
    python demo_real_lighthouse.py https://www.stackoverflow.com
"""

import sys
import time
import json
from src.services.lighthouse_service import LighthouseService
from src.core import get_api_config


def demo_lighthouse_audit(website_url: str):
    """Demonstrate real Lighthouse audit functionality."""
    
    print(f"🚀 Starting real Lighthouse audit for: {website_url}")
    print("=" * 60)
    
    # Initialize service
    service = LighthouseService()
    api_config = get_api_config()
    
    # Check API key
    if not api_config.LIGHTHOUSE_API_KEY or api_config.LIGHTHOUSE_API_KEY == "c76e3daa.c159a1e6667343628e8f94366b91f745":
        print("⚠️  Warning: Using example API key. For production, set a real LIGHTHOUSE_API_KEY in your .env file")
        print("   The example key may have limited functionality or rate limits.")
        print()
    
    # Test parameters
    business_id = "demo-business-123"
    run_id = f"demo-run-{int(time.time())}"
    
    print(f"📊 Business ID: {business_id}")
    print(f"🆔 Run ID: {run_id}")
    print(f"⏱️  Timeout: {api_config.LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS}s")
    print(f"🔑 API Key: {api_config.LIGHTHOUSE_API_KEY[:20]}...")
    print()
    
    # Test desktop strategy
    print("🖥️  Testing Desktop Strategy...")
    start_time = time.time()
    
    desktop_result = service.run_lighthouse_audit(
        website_url=website_url,
        business_id=business_id,
        run_id=run_id,
        strategy="desktop"
    )
    
    desktop_time = time.time() - start_time
    
    if desktop_result["success"]:
        print(f"✅ Desktop audit completed in {desktop_time:.2f}s")
        print(f"📈 Performance Score: {desktop_result['scores']['performance']}/100")
        print(f"♿ Accessibility Score: {desktop_result['scores']['accessibility']}/100")
        print(f"🏆 Best Practices Score: {desktop_result['scores']['best_practices']}/100")
        print(f"🔍 SEO Score: {desktop_result['scores']['seo']}/100")
        print(f"🎯 Overall Score: {desktop_result['overall_score']}/100")
        print(f"🎭 Confidence: {desktop_result['confidence']}")
        
        # Show Core Web Vitals
        if desktop_result.get('core_web_vitals'):
            print("\n🌐 Core Web Vitals:")
            cwv = desktop_result['core_web_vitals']
            if cwv.get('first_contentful_paint'):
                print(f"   First Contentful Paint: {cwv['first_contentful_paint']:.0f}ms")
            if cwv.get('largest_contentful_paint'):
                print(f"   Largest Contentful Paint: {cwv['largest_contentful_paint']:.0f}ms")
            if cwv.get('cumulative_layout_shift'):
                print(f"   Cumulative Layout Shift: {cwv['cumulative_layout_shift']:.3f}")
            if cwv.get('total_blocking_time'):
                print(f"   Total Blocking Time: {cwv['total_blocking_time']:.0f}ms")
            if cwv.get('speed_index'):
                print(f"   Speed Index: {cwv['speed_index']:.0f}ms")
    else:
        print(f"❌ Desktop audit failed: {desktop_result.get('error', 'Unknown error')}")
        print(f"   Error Code: {desktop_result.get('error_code', 'N/A')}")
        print(f"   Context: {desktop_result.get('context', 'N/A')}")
    
    print()
    
    # Wait between requests to respect rate limits
    print("⏳ Waiting 3 seconds to respect API rate limits...")
    time.sleep(3)
    
    # Test mobile strategy
    print("📱 Testing Mobile Strategy...")
    start_time = time.time()
    
    mobile_result = service.run_lighthouse_audit(
        website_url=website_url,
        business_id=business_id,
        run_id=run_id,
        strategy="mobile"
    )
    
    mobile_time = time.time() - start_time
    
    if mobile_result["success"]:
        print(f"✅ Mobile audit completed in {mobile_time:.2f}s")
        print(f"📈 Performance Score: {mobile_result['scores']['performance']}/100")
        print(f"♿ Accessibility Score: {mobile_result['scores']['accessibility']}/100")
        print(f"🏆 Best Practices Score: {mobile_result['scores']['best_practices']}/100")
        print(f"🔍 SEO Score: {mobile_result['scores']['seo']}/100")
        print(f"🎯 Overall Score: {mobile_result['overall_score']}/100")
        print(f"🎭 Confidence: {mobile_result['confidence']}")
    else:
        print(f"❌ Mobile audit failed: {mobile_result.get('error', 'Unknown error')}")
        print(f"   Error Code: {mobile_result.get('error_code', 'N/A')}")
        print(f"   Context: {mobile_result.get('context', 'N/A')}")
    
    print()
    print("=" * 60)
    
    # Summary
    print("📊 Audit Summary:")
    print(f"   Website: {website_url}")
    print(f"   Total Time: {desktop_time + mobile_time + 3:.2f}s")
    print(f"   API Calls: 2 (desktop + mobile)")
    print(f"   Rate Limit Delay: 3s")
    
    if desktop_result["success"] and mobile_result["success"]:
        print("   Status: ✅ Both audits completed successfully")
        
        # Compare scores
        desktop_overall = desktop_result['overall_score']
        mobile_overall = mobile_result['overall_score']
        difference = abs(desktop_overall - mobile_overall)
        
        print(f"   Score Comparison:")
        print(f"     Desktop: {desktop_overall}/100")
        print(f"     Mobile:  {mobile_overall}/100")
        print(f"     Difference: {difference:.1f} points")
        
        if difference < 10:
            print("     📱📺 Good consistency between desktop and mobile")
        elif difference < 20:
            print("     ⚠️  Moderate difference between desktop and mobile")
        else:
            print("     🚨 Significant difference between desktop and mobile")
    else:
        print("   Status: ❌ Some audits failed")
    
    print()
    print("🎉 Demo completed! Check the logs above for detailed results.")


def main():
    """Main function to run the demo."""
    
    # Default URL if none provided
    default_url = "https://www.google.com"
    
    if len(sys.argv) > 1:
        website_url = sys.argv[1]
    else:
        website_url = default_url
        print(f"🌐 No URL provided, using default: {default_url}")
        print()
    
    try:
        demo_lighthouse_audit(website_url)
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("💡 Make sure you have:")
        print("   1. All dependencies installed (pip install -r requirements.txt)")
        print("   2. Proper environment configuration (.env file)")
        print("   3. Internet connection for API calls")
        sys.exit(1)


if __name__ == "__main__":
    main()
