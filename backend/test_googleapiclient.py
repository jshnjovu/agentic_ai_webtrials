#!/usr/bin/env python3
"""
Test script to verify the updated unified.py with googleapiclient integration.
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
    
    # Test a simple PageSpeed analysis
    test_url = "https://www.google.com"
    print(f"\n🚀 Testing PageSpeed analysis for: {test_url}")
    
    try:
        result = await analyzer.run_page_speed_analysis(test_url, "mobile")
        
        if result.get("mobile") or result.get("desktop"):
            print("✅ PageSpeed analysis completed successfully!")
            print(f"   - Mobile result: {'✅' if result.get('mobile') else '❌'}")
            print(f"   - Desktop result: {'✅' if result.get('desktop') else '❌'}")
            print(f"   - Errors: {len(result.get('errors', []))}")
            
            # Show some sample scores if available
            mobile = result.get("mobile")
            if mobile and mobile.get("scores"):
                scores = mobile["scores"]
                print(f"   - Mobile Performance Score: {scores.get('performance', 'N/A')}")
                print(f"   - Mobile Accessibility Score: {scores.get('accessibility', 'N/A')}")
                print(f"   - Mobile SEO Score: {scores.get('seo', 'N/A')}")
            
            return True
        else:
            print("❌ PageSpeed analysis failed - no results returned")
            if result.get("errors"):
                print(f"   - Errors: {result['errors']}")
            return False
            
    except Exception as e:
        print(f"❌ PageSpeed analysis failed with exception: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing UnifiedAnalyzer with googleapiclient integration")
    print("=" * 60)
    
    try:
        success = asyncio.run(test_unified_analyzer())
        
        if success:
            print("\n🎉 All tests passed! The googleapiclient integration is working correctly.")
        else:
            print("\n💥 Some tests failed. Please check the configuration and try again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
