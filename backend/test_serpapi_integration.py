#!/usr/bin/env python3
"""
Test script to verify SerpAPI integration in the backend.
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from src.services.serpapi_service import SerpAPIService
from src.schemas.business_search import BusinessSearchRequest, LocationType

def test_serpapi_integration():
    """Test the SerpAPI integration."""
    print("🧪 Testing SerpAPI Integration in Backend")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        print("❌ SERPAPI_API_KEY environment variable not set")
        print("Please set your API key: export SERPAPI_API_KEY='your_key_here'")
        return False
    
    try:
        # Create SerpAPI service
        print("🔧 Creating SerpAPI service...")
        serpapi_service = SerpAPIService()
        
        # Create test request
        print("📝 Creating test business search request...")
        test_request = BusinessSearchRequest(
            query="gyms",
            location="London, UK",
            location_type=LocationType.CITY,
            max_results=5,
            run_id="test_serpapi_integration"
        )
        
        # Test input validation
        print("✅ Testing input validation...")
        if not serpapi_service.validate_input(test_request):
            print("❌ Input validation failed")
            return False
        
        print("✅ Input validation passed")
        
        # Test business search
        print("🔍 Testing business search...")
        result = serpapi_service.search_businesses(test_request)
        
        if hasattr(result, 'success') and result.success:
            print(f"✅ Search successful! Found {len(result.results)} businesses")
            
            # Show sample results
            print("\n📊 Sample Results:")
            for i, business in enumerate(result.results[:3], 1):
                print(f"{i}. {business.name}")
                print(f"   Address: {business.address}")
                print(f"   Rating: {business.rating}/5 ({business.user_ratings_total} reviews)")
                print(f"   Phone: {business.phone}")
                print(f"   Website: {business.website}")
                print()
            
            # Save results to file
            output_file = backend_dir / "serpapi_test_results.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "success": True,
                    "query": test_request.query,
                    "location": test_request.location,
                    "total_results": len(result.results),
                    "results": [
                        {
                            "name": business.name,
                            "address": business.address,
                            "rating": business.rating,
                            "reviews": business.user_ratings_total,
                            "phone": business.phone,
                            "website": business.website,
                            "place_id": business.place_id
                        }
                        for business in result.results
                    ]
                }, f, indent=2)
            
            print(f"💾 Results saved to: {output_file}")
            return True
            
        else:
            print(f"❌ Search failed: {result.error}")
            return False
            
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_serpapi_integration()
    if success:
        print("\n🎉 SerpAPI integration test completed successfully!")
    else:
        print("\n💥 SerpAPI integration test failed!")
        sys.exit(1)
