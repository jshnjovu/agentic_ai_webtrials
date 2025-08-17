#!/usr/bin/env python3
"""
Test script to show comprehensive business data from Google Places API
"""

import sys
import os
import asyncio

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_google_places_detailed():
    """Test the Google Places service to show comprehensive business data"""
    
    print("🧪 Testing Google Places API - Comprehensive Business Data...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from src.services.google_places_service import GooglePlacesService
        from src.schemas.business_search import BusinessSearchRequest, LocationType
        
        print("✅ Imports successful")
        
        # Create service
        print("📋 Creating Google Places service...")
        service = GooglePlacesService()
        
        # Test business search
        print("🔍 Testing business search for gyms in London, UK...")
        
        request = BusinessSearchRequest(
            query="gyms",
            location="London, UK",
            location_type=LocationType.CITY,
            max_results=3,
            radius=5000,
            run_id="test_detailed_data"
        )
        
        print(f"📋 Request: {request}")
        
        # Execute the search
        result = await service.search_businesses(request)
        
        if result.success:
            print(f"✅ Search successful: {result.total_results} results found")
            print(f"📍 Location: {result.location}")
            print(f"🔍 Query: {result.query}")
            
            for i, business in enumerate(result.results, 1):
                print(f"\n🏢 Business {i}: {business.name}")
                print(f"   📍 Address: {business.address}")
                print(f"   📞 Phone: {business.phone or 'N/A'}")
                print(f"   🌐 Website: {business.website or 'N/A'}")
                print(f"   ⭐ Rating: {business.rating or 'N/A'}")
                print(f"   👥 Total Ratings: {business.user_ratings_total or 'N/A'}")
                print(f"   💰 Price Level: {business.price_level or 'N/A'}")
                print(f"   🏷️ Types: {', '.join(business.types) if business.types else 'N/A'}")
                print(f"   🆔 Place ID: {business.place_id}")
                
                if business.geometry and business.geometry.get('location'):
                    loc = business.geometry['location']
                    print(f"   📍 Coordinates: {loc.get('lat')}, {loc.get('lng')}")
        else:
            print(f"❌ Search failed: {result.error}")
            if hasattr(result, 'details') and result.details:
                print(f"   Details: {result.details}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_google_places_detailed())
    sys.exit(0 if success else 1)
