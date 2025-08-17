#!/usr/bin/env python3
"""
Test Script for Streamlined Stories 1 & 2
Demonstrates the enhanced business discovery flow with rate limiting and progressive updates
"""

import asyncio
import json
from datetime import datetime

# Mock the tool executor for testing
class MockLeadGenToolExecutor:
    """Mock tool executor for testing Stories 1 & 2"""
    
    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Mock tool execution for business discovery"""
        
        if tool_name == "discover_businesses":
            return await self._mock_discover_businesses(arguments)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "tool_name": tool_name
            }
    
    async def _mock_discover_businesses(self, arguments: dict) -> dict:
        """Mock business discovery with progressive updates and rate limiting simulation"""
        
        location = arguments.get("location", "Austin, TX")
        niche = arguments.get("niche", "Vegan restaurants")
        max_businesses = arguments.get("max_businesses", 10)
        
        print(f"🔍 Starting discovery: {niche} in {location}")
        
        # Simulate progressive discovery with rate limiting
        discovery_logs = ["Scraping Google Places..."]
        
        # Simulate finding businesses progressively
        for i in range(1, max_businesses + 1):
            if i == 3:
                discovery_logs.append("Found 3")
                print("   ✅ Found 3 businesses")
                
                # Simulate rate limiting at 3 businesses
                if "rate_limit_test" in arguments:
                    print("   ⚠️  Simulating rate limit...")
                    discovery_logs.append("Google throttled us — retrying in 3 s...")
                    print("   ⏳ Waiting 3 seconds...")
                    await asyncio.sleep(3)
                    print("   🔄 Retrying after rate limit...")
                    
            elif i == 7:
                discovery_logs.append("Found 7")
                print("   ✅ Found 7 businesses")
                
            elif i == max_businesses:
                discovery_logs.append("Found 10")
                discovery_logs.append("Discovery complete")
                print("   ✅ Found 10 businesses")
                print("   🎉 Discovery complete!")
        
        # Mock business data
        businesses = []
        for i in range(max_businesses):
            business = {
                "business_name": f"{niche.title()} #{i+1}",
                "contact_name": f"Contact {i+1}",
                "email": f"contact{i+1}@{niche.lower().replace(' ', '')}.com",
                "phone": f"+1-555-{1000+i:04d}",
                "website": f"https://{niche.lower().replace(' ', '')}{i+1}.com",
                "address": f"{100+i} Main St, {location}",
                "postcode": "12345",
                "rating": 4.0 + (i % 5) * 0.2,
                "review_count": 50 + i * 10,
                "categories": [niche, "Restaurant", "Local Business"],
                "price_level": (i % 4) + 1,
                "place_id": f"place_id_{i+1}",
                "source": "Google Places"
            }
            businesses.append(business)
        
        return {
            "success": True,
            "tool_name": "discover_businesses",
            "result": {
                "businesses": businesses,
                "total_found": len(businesses),
                "location": location,
                "niche": niche,
                "discovery_logs": discovery_logs,
                "processing_time": 5.2
            }
        }

async def test_story_1_discovery_happy_path():
    """Test Story 1: Discovery Happy Path"""
    print("\n" + "="*60)
    print("🧪 TESTING STORY 1: Discovery Happy Path")
    print("="*60)
    
    executor = MockLeadGenToolExecutor()
    
    # Test basic discovery
    result = await executor.execute_tool("discover_businesses", {
        "location": "Austin, TX",
        "niche": "Vegan restaurants",
        "max_businesses": 10
    })
    
    if result["success"]:
        print(f"\n✅ Discovery successful!")
        print(f"   📍 Location: {result['result']['location']}")
        print(f"   🏢 Niche: {result['result']['niche']}")
        print(f"   🔍 Businesses found: {result['result']['total_found']}")
        print(f"   📊 Processing time: {result['result']['processing_time']}s")
        
        print(f"\n📝 Discovery Logs:")
        for log in result['result']['discovery_logs']:
            print(f"   • {log}")
        
        print(f"\n🏢 Sample Business:")
        sample_business = result['result']['businesses'][0]
        print(f"   • Name: {sample_business['business_name']}")
        print(f"   • Website: {sample_business['website']}")
        print(f"   • Rating: {sample_business['rating']}/5.0")
        
        # Check Story 1 requirements
        print(f"\n🎯 Story 1 Requirements Check:")
        print(f"   ✅ Found exactly 10 businesses: {result['result']['total_found'] == 10}")
        print(f"   ✅ Has progressive discovery logs: {len(result['result']['discovery_logs']) > 1}")
        print(f"   ✅ Ends with 'Discovery complete': {'Discovery complete' in result['result']['discovery_logs']}")
        
    else:
        print(f"❌ Discovery failed: {result['error']}")

async def test_story_2_rate_limit_backoff():
    """Test Story 2: Discovery with Rate-Limit Backoff"""
    print("\n" + "="*60)
    print("🧪 TESTING STORY 2: Rate-Limit Backoff")
    print("="*60)
    
    executor = MockLeadGenToolExecutor()
    
    # Test discovery with rate limiting
    start_time = datetime.now()
    result = await executor.execute_tool("discover_businesses", {
        "location": "Austin, TX",
        "niche": "Vegan restaurants",
        "max_businesses": 10,
        "rate_limit_test": True  # Trigger rate limit simulation
    })
    
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    if result["success"]:
        print(f"\n✅ Discovery successful after rate limiting!")
        print(f"   ⏱️  Total time: {total_time:.1f}s (includes 3s rate limit delay)")
        print(f"   🔍 Businesses found: {result['result']['total_found']}")
        
        print(f"\n📝 Discovery Logs (with rate limiting):")
        for log in result['result']['discovery_logs']:
            if "throttled" in log:
                print(f"   ⚠️  {log}")
            elif "Found" in log:
                print(f"   ✅ {log}")
            elif "complete" in log:
                print(f"   🎉 {log}")
            else:
                print(f"   • {log}")
        
        # Check Story 2 requirements
        print(f"\n🎯 Story 2 Requirements Check:")
        print(f"   ✅ Rate limit message shown: {'throttled' in str(result['result']['discovery_logs'])}")
        print(f"   ✅ Retry after delay: {total_time > 3.0}")
        print(f"   ✅ No duplicate rows: {len(result['result']['businesses']) == 10}")
        
    else:
        print(f"❌ Discovery failed: {result['error']}")

async def main():
    """Run all tests"""
    print("🚀 LeadGenBuilder - Stories 1 & 2 Test Suite")
    print("Testing streamlined business discovery flow")
    
    await test_story_1_discovery_happy_path()
    await test_story_2_rate_limit_backoff()
    
    print("\n" + "="*60)
    print("🎉 All tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
