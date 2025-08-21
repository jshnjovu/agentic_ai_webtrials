#!/usr/bin/env python3
"""
Test script to check if UnifiedAnalyzer can access the API key.
"""

import os
import sys
sys.path.append('src')

print("🧪 Testing UnifiedAnalyzer API Key Access...")
print("=" * 50)

# First, let's manually load the .env file
try:
    from dotenv import load_dotenv
    load_dotenv('.env')
    print("✅ .env file loaded manually")
    print(f"📋 GOOGLE_GENERAL_API_KEY: {os.getenv('GOOGLE_GENERAL_API_KEY', 'NOT_SET')}")
except Exception as e:
    print(f"❌ Failed to load .env: {e}")

# Now try to import and test UnifiedAnalyzer
try:
    from src.services.unified import UnifiedAnalyzer
    print("✅ UnifiedAnalyzer imported successfully")
    
    # Create instance
    analyzer = UnifiedAnalyzer()
    print("✅ UnifiedAnalyzer instance created")
    
    # Check API key
    print(f"🔑 API Key in analyzer: {analyzer.google_api_key}")
    print(f"🔑 API Key valid: {analyzer.google_api_key is not None and len(analyzer.google_api_key) > 0}")
    
    # Check service health
    health = analyzer.get_service_health()
    print(f"🏥 Service health: {health}")
    
except Exception as e:
    print(f"❌ UnifiedAnalyzer test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🧪 Test complete!")
