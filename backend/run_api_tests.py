#!/usr/bin/env python3
"""
Simple test runner for batch processing API tests.
Run this to test all the real-time API endpoints.
"""

import asyncio
import sys
import os

# Add tests to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def main():
    """Run the API tests."""
    try:
        from test_batch_processing_api import run_all_tests
        
        print("🚀 **Starting Batch Processing API Tests**")
        print("=" * 60)
        
        success = await run_all_tests()
        
        if success:
            print("\n🎉 **All API Tests Passed!**")
            print("The batch processing system is working correctly.")
            return 0
        else:
            print("\n⚠️  **Some API Tests Failed**")
            print("Please review the failed tests above.")
            return 1
            
    except ImportError as e:
        print(f"❌ **Import Error: {e}**")
        print("Make sure you're running from the backend directory with venv activated.")
        return 1
    except Exception as e:
        print(f"❌ **Unexpected Error: {e}**")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
