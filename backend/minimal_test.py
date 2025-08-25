#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.services.unified import UnifiedAnalyzer
    print("✅ Import successful")
    
    analyzer = UnifiedAnalyzer()
    print("✅ Analyzer created")
    print(f"PageSpeed service: {'✅' if analyzer.pagespeed_service else '❌'}")
    
    # Test the API call method directly
    if analyzer.pagespeed_service:
        print("Testing direct API call...")
        result = analyzer._call_pagespeed_api("https://www.google.com", "mobile")
        print("✅ API call successful!")
        print(f"Response keys: {list(result.keys())}")
    else:
        print("❌ PageSpeed service not available")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
