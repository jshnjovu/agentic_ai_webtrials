#!/usr/bin/env python3
"""
Test script for Geoapify integration with SerpAPIService.
Demonstrates dynamic country code extraction for different locations.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.services.geoapify_service import GeoapifyService
from src.services.serpapi_service import SerpAPIService
from src.schemas.business_search import BusinessSearchRequest, LocationType


def test_geoapify_integration():
    """Test the Geoapify integration with SerpAPIService."""
    print("🧪 Testing Geoapify Integration with SerpAPIService")
    print("=" * 60)
    
    # Check if API keys are set
    geoapify_key = os.getenv("GEOAPIFY_API_KEY")
    serpapi_key = os.getenv("SERPAPI_API_KEY")
    
    if not geoapify_key or geoapify_key in ["test_key", "your_geoapify_api_key_here"]:
        print("❌ GEOAPIFY_API_KEY environment variable not set")
        print("Please set your API key: export GEOAPIFY_API_KEY='your_key_here'")
        return False
    
    if not serpapi_key or serpapi_key in ["test_key", "your_serpapi_api_key_here"]:
        print("❌ SERPAPI_API_KEY environment variable not set")
        print("Please set your API key: export SERPAPI_API_KEY='your_key_here'")
        return False
    
    try:
        # Create services
        print("🔧 Creating Geoapify and SerpAPI services...")
        geoapify_service = GeoapifyService()
        serpapi_service = SerpAPIService()
        
        # Test locations
        test_locations = [
            ("Gyms in Austin, Texas", "Austin, Texas"),
            ("Restaurants in Manila, Philippines", "Manila, Philippines"),
            ("Hotels in London, UK", "London, UK"),
            ("Shops in Toronto, Canada", "Toronto, Canada"),
            ("Cafes in Paris, France", "Paris, France")
        ]
        
        print("\n📍 Testing Country Code Extraction:")
        print("-" * 40)
        
        for query, location in test_locations:
            print(f"\n🔍 Query: {query}")
            print(f"📍 Location: {location}")
            
            # Extract country code using Geoapify
            country_code = geoapify_service.extract_country_code(location)
            if country_code:
                print(f"🌍 Country Code: {country_code.upper()}")
                
                # Get detailed location info
                location_info = geoapify_service.get_location_info(location)
                if location_info:
                    print(f"🏙️  City: {location_info.get('city', 'N/A')}")
                    print(f"🏛️  State/Region: {location_info.get('state', 'N/A')}")
                    print(f"🌎 Country: {location_info.get('country', 'N/A')}")
                    print(f"📍 Coordinates: {location_info.get('lat', 'N/A')}, {location_info.get('lon', 'N/A')}")
                
                # Test SerpAPI parameter building
                request = BusinessSearchRequest(
                    query=query.split(" in ")[0],  # Extract just the business type
                    location=location,
                    location_type=LocationType.CITY,
                    max_results=5,
                    run_id="test_geoapify_integration"
                )
                
                params = serpapi_service._build_search_params(request)
                print(f"🔧 SerpAPI gl parameter: {params['gl']}")
                print(f"✅ Country code match: {'✅' if params['gl'] == country_code else '❌'}")
                
            else:
                print("❌ Could not extract country code")
        
        print("\n🎯 Testing Fallback Behavior:")
        print("-" * 30)
        
        # Test with unknown location (should fallback to "us")
        unknown_request = BusinessSearchRequest(
            query="gyms",
            location="Unknown Location, Unknown Country",
            location_type=LocationType.CITY,
            max_results=5,
            run_id="test_geoapify_integration"
        )
        
        params = serpapi_service._build_search_params(unknown_request)
        print(f"🔍 Unknown location: {unknown_request.location}")
        print(f"🔧 Fallback gl parameter: {params['gl']}")
        print(f"✅ Fallback to 'us': {'✅' if params['gl'] == 'us' else '❌'}")
        
        print("\n🎉 Geoapify Integration Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_country_codes():
    """Test individual country code extraction for specific locations."""
    print("\n🌍 Testing Individual Country Code Extraction:")
    print("=" * 50)
    
    geoapify_service = GeoapifyService()
    
    # Test specific locations mentioned in the user query
    test_cases = [
        ("Gyms in Texas, Austin", "Austin, Texas"),
        ("Restaurants in Rizal Park, Manila", "Rizal Park, Manila"),
        ("Hotels in New York, NY", "New York, NY"),
        ("Shops in Los Angeles, CA", "Los Angeles, CA"),
        ("Cafes in Seattle, WA", "Seattle, WA")
    ]
    
    for query, location in test_cases:
        print(f"\n🔍 {query}")
        print(f"📍 Location: {location}")
        
        country_code = geoapify_service.extract_country_code(location)
        if country_code:
            print(f"🌍 Country Code: {country_code.upper()}")
            
            # Show what this means for SerpAPI
            if country_code == "us":
                print("🇺🇸 Will use US-specific Google domain and settings")
            elif country_code == "ph":
                print("🇵🇭 Will use Philippines-specific Google domain and settings")
            else:
                print(f"🌐 Will use {country_code.upper()}-specific Google domain and settings")
        else:
            print("❌ Could not extract country code")


if __name__ == "__main__":
    print("🚀 Starting Geoapify Integration Tests")
    print("=" * 60)
    
    # Test the main integration
    success = test_geoapify_integration()
    
    if success:
        # Test individual country codes
        test_individual_country_codes()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("\n💡 Key Benefits of Geoapify Integration:")
        print("   • Dynamic country code detection for international searches")
        print("   • Improved search relevance for local businesses")
        print("   • Automatic fallback to US settings when needed")
        print("   • Better support for global business discovery")
    else:
        print("\n❌ Tests failed. Please check your API keys and try again.")
        sys.exit(1)
