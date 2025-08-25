#!/usr/bin/env python3
print("Testing simple Python execution")
print("If you see this, Python is working")

# Test the import
try:
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from src.services.unified import UnifiedAnalyzer
    print("✅ Successfully imported UnifiedAnalyzer")
    
    # Test initialization
    analyzer = UnifiedAnalyzer()
    print("✅ Successfully created UnifiedAnalyzer instance")
    print(f"PageSpeed service: {'✅' if analyzer.pagespeed_service else '❌'}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
