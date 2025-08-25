#!/usr/bin/env python3
"""
Test script to verify the updated PageSpeed endpoint works correctly.
"""

import asyncio
import sys
import os
import json

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.unified import UnifiedAnalyzer
from src.core.config import get_api_config

async def test_pagespeed_analysis():
    """Test the PageSpeed analysis directly using the unified analyzer."""
    
    print("🧪 Testing PageSpeed analysis with unified analyzer")
    print("=" * 60)
    
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
        
        if not analyzer.pagespeed_service:
            print("❌ PageSpeed service not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Failed to initialize UnifiedAnalyzer: {e}")
        return False
    
    # Test PageSpeed analysis
    test_url = "https://www.google.com"
    print(f"\n🚀 Testing PageSpeed analysis for: {test_url}")
    
    try:
        result = await analyzer.run_page_speed_analysis(test_url, "mobile")
        
        print(f"✅ PageSpeed analysis completed!")
        print(f"   - Result keys: {list(result.keys())}")
        
        # Check mobile data
        mobile_data = result.get("mobile")
        if mobile_data:
            print(f"   - Mobile data keys: {list(mobile_data.keys())}")
            
            scores = mobile_data.get("scores", {})
            if scores:
                print(f"   - Mobile scores: {scores}")
                print(f"     - Performance: {scores.get('performance', 'N/A')}")
                print(f"     - Accessibility: {scores.get('accessibility', 'N/A')}")
                print(f"     - SEO: {scores.get('seo', 'N/A')}")
            else:
                print(f"   - ❌ No scores in mobile data")
        else:
            print(f"   - ❌ No mobile data")
        
        # Check desktop data
        desktop_data = result.get("desktop")
        if desktop_data:
            print(f"   - Desktop data keys: {list(desktop_data.keys())}")
            
            scores = desktop_data.get("scores", {})
            if scores:
                print(f"   - Desktop scores: {scores}")
                print(f"     - Performance: {scores.get('performance', 'N/A')}")
                print(f"     - Accessibility: {scores.get('accessibility', 'N/A')}")
                print(f"     - SEO: {scores.get('seo', 'N/A')}")
            else:
                print(f"   - ❌ No scores in desktop data")
        else:
            print(f"   - ❌ No desktop data")
        
        # Check for errors
        errors = result.get("errors", [])
        if errors:
            print(f"   - ⚠️ Errors encountered: {len(errors)}")
            for i, error in enumerate(errors[:3]):  # Show first 3 errors
                print(f"     {i+1}. {error.get('type', 'UNKNOWN')}: {error.get('message', 'No message')}")
        
        # Test the score extraction methods
        print(f"\n🔍 Testing score extraction methods:")
        try:
            performance = analyzer.get_performance_score(result)
            accessibility = analyzer.get_accessibility_score(result)
            seo = analyzer.get_seo_score(result)
            overall = analyzer.get_overall_score(result)
            
            print(f"   - Performance: {performance}")
            print(f"   - Accessibility: {accessibility}")
            print(f"   - SEO: {seo}")
            print(f"   - Overall: {overall}")
            
        except Exception as e:
            print(f"   - ❌ Score extraction failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ PageSpeed analysis failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    try:
        success = asyncio.run(test_pagespeed_analysis())
        
        if success:
            print("\n🎉 Test completed successfully!")
        else:
            print("\n💥 Test failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
