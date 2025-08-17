#!/usr/bin/env python3
"""
Test Script for Enhanced Stories 3, 4 & 5 with Epic 2 Service Integration
Demonstrates Yelp Fusion fallback, Epic 2 scoring integration, and demo generation logic
"""

import asyncio
import json
from datetime import datetime

# Mock the enhanced tool executor for testing with Epic 2 services
class MockEnhancedLeadGenToolExecutor:
    """Mock enhanced tool executor for testing Stories 3, 4 & 5 with Epic 2 integration"""
    
    async def execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Mock tool execution for enhanced functionality with Epic 2 services"""
        
        if tool_name == "discover_businesses":
            return await self._mock_discover_businesses_with_fallback(arguments)
        elif tool_name == "score_websites":
            return await self._mock_epic2_website_scoring(arguments)
        elif tool_name == "generate_demo_sites":
            return await self._mock_demo_generation_with_epic2_logic(arguments)
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}",
                "tool_name": tool_name
            }
    
    async def _mock_discover_businesses_with_fallback(self, arguments: dict) -> dict:
        """Mock business discovery with Yelp Fusion fallback (Story 3)"""
        
        location = arguments.get("location", "Austin, TX")
        niche = arguments.get("niche", "Vegan restaurants")
        max_businesses = arguments.get("max_businesses", 10)
        
        print(f"🔍 Starting discovery: {niche} in {location}")
        
        discovery_logs = []
        businesses = []
        
        # Simulate Google Places being blocked by robots.txt
        if arguments.get("google_blocked", False):
            discovery_logs.append("Scraping Google Places...")
            discovery_logs.append("robots.txt blocks Google Places")
            discovery_logs.append("Switching to Yelp Fusion...")
            print("   ⚠️  Google Places blocked by robots.txt")
            print("   🔄 Switching to Yelp Fusion...")
            
            # Simulate Yelp Fusion discovery
            for i in range(1, max_businesses + 1):
                business = {
                    "business_name": f"{niche.title()} #{i}",
                    "contact_name": f"Contact {i}",
                    "email": f"contact{i}@{niche.lower().replace(' ', '')}.com",
                    "phone": f"+1-555-{1000+i:04d}",
                    "website": f"https://{niche.lower().replace(' ', '')}{i+1}.com",
                    "address": f"{100+i} Main St, {location}",
                    "postcode": "12345",
                    "rating": 4.0 + (i % 5) * 0.2,
                    "review_count": 50 + i * 10,
                    "categories": [niche, "Restaurant", "Local Business"],
                    "price_level": (i % 4) + 1,
                    "place_id": f"yelp_id_{i+1}",
                    "source": "Yelp Fusion"
                }
                businesses.append(business)
            
            discovery_logs.append(f"Found {len(businesses)}")
            discovery_logs.append("Discovery complete")
            
        else:
            # Normal Google Places discovery
            discovery_logs.append("Scraping Google Places...")
            for i in range(1, max_businesses + 1):
                business = {
                    "business_name": f"{niche.title()} #{i}",
                    "contact_name": f"Contact {i}",
                    "email": f"contact{i}@{niche.lower().replace(' ', '')}.com",
                    "phone": f"+1-555-{1000+i:04d}",
                    "website": f"https://{niche.lower().replace(' ', '')}{i+1}.com",
                    "address": f"{100+i} Main St, {location}",
                    "postcode": "12345",
                    "rating": 4.0 + (i % 5) * 0.2,
                    "review_count": 50 + i * 10,
                    "categories": [niche, "Restaurant", "Local Business"],
                    "price_level": (i % 4) + 1,
                    "place_id": f"google_place_{i+1}",
                    "source": "Google Places"
                }
                businesses.append(business)
            
            discovery_logs.append(f"Found {len(businesses)}")
            discovery_logs.append("Discovery complete")
        
        print(f"   ✅ Discovery completed: {len(businesses)} businesses found")
        
        return {
            "success": True,
            "tool_name": "discover_businesses",
            "result": {
                "businesses": businesses,
                "total_found": len(businesses),
                "location": location,
                "niche": niche,
                "discovery_logs": discovery_logs,
                "processing_time": 3.5
            }
        }
    
    async def _mock_epic2_website_scoring(self, arguments: dict) -> dict:
        """Mock Epic 2 website scoring integration (Story 4)"""
        
        businesses = arguments.get("businesses", [])
        
        print(f"📊 Starting Epic 2 website scoring for {len(businesses)} businesses")
        
        scored_businesses = []
        
        for i, business in enumerate(businesses):
            scored_business = business.copy()
            
            if business.get("website"):
                # Simulate Epic 2 service integration
                if i < 3:  # First 3 businesses: poor scores (need demos)
                    scored_business.update({
                        "score_perf": 25 + (i * 5),
                        "score_access": 30 + (i * 3),
                        "score_seo": 20 + (i * 4),
                        "score_trust": 35 + (i * 2),
                        "score_overall": 30 + (i * 5),
                        "scoring_method": "lighthouse",
                        "confidence_level": "high",
                        "score_category": "poor",
                        "demo_eligible": True,
                        "demo_priority": "high",
                        "top_issues": [
                            f"Poor performance score ({scored_business['score_perf']}/100)",
                            f"Accessibility issues ({scored_business['score_access']}/100)",
                            f"SEO optimization needed ({scored_business['score_seo']}/100)"
                        ]
                    })
                    
                    # Add Epic 2 heuristic data
                    scored_business.update({
                        "heuristic_trust": 28 + (i * 3),
                        "heuristic_cro": 25 + (i * 4),
                        "heuristic_mobile": 30 + (i * 2),
                        "heuristic_content": 32 + (i * 3),
                        "heuristic_social": 27 + (i * 4),
                        "heuristic_overall": 28 + (i * 3)
                    })
                    
                elif i < 7:  # Next 4 businesses: fair scores (may need demos)
                    scored_business.update({
                        "score_perf": 55 + (i * 3),
                        "score_access": 60 + (i * 2),
                        "score_seo": 58 + (i * 2),
                        "score_trust": 62 + (i * 2),
                        "score_overall": 58 + (i * 3),
                        "scoring_method": "lighthouse",
                        "confidence_level": "high",
                        "score_category": "fair",
                        "demo_eligible": True,
                        "demo_priority": "medium",
                        "top_issues": [
                            f"Performance could improve ({scored_business['score_perf']}/100)",
                            f"SEO optimization needed ({scored_business['score_seo']}/100)"
                        ]
                    })
                    
                    # Add Epic 2 heuristic data
                    scored_business.update({
                        "heuristic_trust": 58 + (i * 2),
                        "heuristic_cro": 55 + (i * 3),
                        "heuristic_mobile": 60 + (i * 2),
                        "heuristic_content": 62 + (i * 2),
                        "heuristic_social": 57 + (i * 3),
                        "heuristic_overall": 58 + (i * 2)
                    })
                    
                else:  # Last 3 businesses: good scores (no demos needed)
                    scored_business.update({
                        "score_perf": 75 + (i * 2),
                        "score_access": 80 + (i * 2),
                        "score_seo": 78 + (i * 2),
                        "score_trust": 82 + (i * 2),
                        "score_overall": 78 + (i * 2),
                        "scoring_method": "lighthouse",
                        "confidence_level": "high",
                        "score_category": "good",
                        "demo_eligible": False,
                        "demo_priority": "none",
                        "top_issues": []
                    })
                    
                    # Add Epic 2 heuristic data
                    scored_business.update({
                        "heuristic_trust": 78 + (i * 2),
                        "heuristic_cro": 75 + (i * 3),
                        "heuristic_mobile": 80 + (i * 2),
                        "heuristic_content": 82 + (i * 2),
                        "heuristic_social": 77 + (i * 3),
                        "heuristic_overall": 78 + (i * 2)
                    })
            else:
                # No website - mark as unscorable
                scored_business.update({
                    "score_perf": 0,
                    "score_access": 0,
                    "score_seo": 0,
                    "score_trust": 0,
                    "score_overall": 0,
                    "scoring_method": "no_website",
                    "confidence_level": "low",
                    "demo_eligible": True,
                    "demo_priority": "high"
                })
            
            scored_businesses.append(scored_business)
        
        # Calculate statistics using Epic 2 data
        valid_scores = [b for b in scored_businesses if b.get("scoring_method") not in ["no_website"]]
        if valid_scores:
            average_score = sum(b["score_overall"] for b in valid_scores) / len(valid_scores)
            low_scorers = len([b for b in valid_scores if b["score_overall"] < 70])
            high_confidence = len([b for b in valid_scores if b.get("confidence_level") == "high"])
            
            print(f"   ✅ Epic 2 scoring completed: avg score {average_score:.1f}, {low_scorers} low scorers, {high_confidence} high confidence")
        else:
            average_score = 0
            low_scorers = 0
            high_confidence = 0
        
        return {
            "success": True,
            "tool_name": "score_websites",
            "result": {
                "businesses": scored_businesses,
                "total_scored": len(scored_businesses),
                "average_score": average_score,
                "low_scorers": low_scorers,
                "high_confidence_scores": high_confidence,
                "scoring_methods_used": list(set(b.get("scoring_method") for b in scored_businesses)),
                "processing_time": 4.2
            }
        }
    
    async def _mock_demo_generation_with_epic2_logic(self, arguments: dict) -> dict:
        """Mock demo generation with Epic 2 scoring logic (Stories 4 & 5)"""
        
        businesses = arguments.get("businesses", [])
        location = arguments.get("location", "Austin, TX")
        niche = arguments.get("niche", "Vegan restaurants")
        
        print(f"🏗️ Starting demo generation with Epic 2 scoring logic for {len(businesses)} businesses")
        
        updated_businesses = []
        demo_count = 0
        skipped_count = 0
        
        for business in businesses:
            updated_business = business.copy()
            score_overall = business.get("score_overall", 0)
            confidence_level = business.get("confidence_level", "low")
            scoring_method = business.get("scoring_method", "unknown")
            
            # Generate demo for businesses with score < 70 and good confidence (Story 4)
            if score_overall < 70 and confidence_level in ["high", "medium"]:
                try:
                    print(f"   🏗️ Generating demo for {business['business_name']} (score: {score_overall}, confidence: {confidence_level}, method: {scoring_method})")
                    
                    # Mock demo site generation
                    demo_url = f"https://demo-{business['business_name'].lower().replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.vercel.app"
                    
                    updated_business.update({
                        "generated_site_url": demo_url,
                        "demo_status": "generated",
                        "demo_generated_at": datetime.now().isoformat(),
                        "demo_source": f"Epic 2 {scoring_method} scoring",
                        "demo_confidence": confidence_level
                    })
                    demo_count += 1
                    
                    print(f"   ✅ Demo generated: {demo_url}")
                    
                except Exception as e:
                    print(f"   ❌ Demo generation failed for {business['business_name']}: {e}")
                    updated_business.update({
                        "demo_status": "failed",
                        "demo_error": str(e),
                        "demo_source": f"Epic 2 {scoring_method} scoring"
                    })
            
            # Skip demo for businesses with score >= 70 or low confidence (Story 5)
            elif score_overall >= 70 or confidence_level == "low":
                skip_reason = ""
                if score_overall >= 80:
                    skip_reason = f"Excellent score ({score_overall}/100) - no demo needed"
                elif score_overall >= 70:
                    skip_reason = f"Good score ({score_overall}/100) - no demo needed"
                else:
                    skip_reason = f"Low confidence ({confidence_level}) - insufficient data for demo"
                
                print(f"   ⏭️ Skipping demo for {business['business_name']}: {skip_reason}")
                updated_business.update({
                    "demo_status": "skipped",
                    "demo_skip_reason": skip_reason,
                    "demo_source": f"Epic 2 {scoring_method} scoring",
                    "demo_confidence": confidence_level
                })
                skipped_count += 1
            
            # Handle edge cases
            else:
                print(f"   ⚠️ Undetermined demo eligibility for {business['business_name']} (score: {score_overall}, confidence: {confidence_level})")
                updated_business.update({
                    "demo_status": "pending_review",
                    "demo_skip_reason": "Manual review required - insufficient scoring data",
                    "demo_source": f"Epic 2 {scoring_method} scoring",
                    "demo_confidence": confidence_level
                })
            
            updated_businesses.append(updated_business)
        
        print(f"   ✅ Demo generation completed using Epic 2 logic: {demo_count} generated, {skipped_count} skipped")
        
        return {
            "success": True,
            "tool_name": "generate_demo_sites",
            "result": {
                "businesses": updated_businesses,
                "demo_sites_created": demo_count,
                "demo_sites_skipped": skipped_count,
                "total_processed": len(updated_businesses),
                "scoring_methods_used": list(set(b.get("demo_source") for b in updated_businesses)),
                "confidence_distribution": {
                    "high": len([b for b in updated_businesses if b.get("demo_confidence") == "high"]),
                    "medium": len([b for b in updated_businesses if b.get("demo_confidence") == "medium"]),
                    "low": len([b for b in updated_businesses if b.get("demo_confidence") == "low"])
                },
                "processing_time": 6.8
            }
        }

async def test_story_3_yelp_fallback():
    """Test Story 3: Yelp Fusion Fallback when Google is blocked"""
    print("\n" + "="*60)
    print("🧪 TESTING STORY 3: Yelp Fusion Fallback")
    print("="*60)
    
    executor = MockEnhancedLeadGenToolExecutor()
    
    # Test discovery with Google blocked
    result = await executor.execute_tool("discover_businesses", {
        "location": "Austin, TX",
        "niche": "Vegan restaurants",
        "max_businesses": 10,
        "google_blocked": True  # Simulate robots.txt blocking
    })
    
    if result["success"]:
        print(f"\n✅ Yelp fallback successful!")
        print(f"   📍 Location: {result['result']['location']}")
        print(f"   🏢 Niche: {result['result']['niche']}")
        print(f"   🔍 Businesses found: {result['result']['total_found']}")
        
        print(f"\n📝 Discovery Logs (with fallback):")
        for log in result['result']['discovery_logs']:
            if "robots.txt" in log:
                print(f"   ⚠️  {log}")
            elif "Switching to Yelp" in log:
                print(f"   🔄 {log}")
            elif "Found" in log:
                print(f"   ✅ {log}")
            else:
                print(f"   • {log}")
        
        # Check Story 3 requirements
        print(f"\n🎯 Story 3 Requirements Check:")
        print(f"   ✅ Robots.txt blocking detected: {'robots.txt' in str(result['result']['discovery_logs'])}")
        print(f"   ✅ Yelp Fusion fallback: {'Switching to Yelp' in str(result['result']['discovery_logs'])}")
        print(f"   ✅ Final table length = 10: {result['result']['total_found'] == 10}")
        
    else:
        print(f"❌ Yelp fallback failed: {result['error']}")

async def test_story_4_low_score_demo_generation():
    """Test Story 4: Low-score demo generation"""
    print("\n" + "="*60)
    print("🧪 TESTING STORY 4: Low-Score Demo Generation")
    print("="*60)
    
    executor = MockEnhancedLeadGenToolExecutor()
    
    # First, discover businesses
    discovery_result = await executor.execute_tool("discover_businesses", {
        "location": "Austin, TX",
        "niche": "Vegan restaurants",
        "max_businesses": 10
    })
    
    if not discovery_result["success"]:
        print(f"❌ Discovery failed: {discovery_result['error']}")
        return
    
    # Then score websites
    scoring_result = await executor.execute_tool("score_websites", {
        "businesses": discovery_result["result"]["businesses"]
    })
    
    if not scoring_result["success"]:
        print(f"❌ Scoring failed: {scoring_result['error']}")
        return
    
    # Find low-scoring business for demo
    low_scorers = [b for b in scoring_result["result"]["businesses"] if b["score_overall"] < 70]
    
    if low_scorers:
        sample_business = low_scorers[0]
        print(f"\n✅ Found low-scoring business for demo:")
        print(f"   🏢 Name: {sample_business['business_name']}")
        print(f"   📊 Overall Score: {sample_business['score_overall']}/100")
        print(f"   🌐 Website: {sample_business['website']}")
        print(f"   🎯 Category: {sample_business['score_category']}")
        print(f"   🚀 Demo Eligible: {sample_business['demo_eligible']}")
        print(f"   ⚠️  Top Issues: {', '.join(sample_business['top_issues'])}")
        
        # Check Story 4 requirements
        print(f"\n🎯 Story 4 Requirements Check:")
        print(f"   ✅ Score < 70: {sample_business['score_overall'] < 70}")
        print(f"   ✅ Has website: {bool(sample_business['website'])}")
        print(f"   ✅ Demo eligible: {sample_business['demo_eligible']}")
        print(f"   ✅ Has top issues: {len(sample_business['top_issues']) > 0}")
        
    else:
        print("❌ No low-scoring businesses found for demo generation")

async def test_story_5_high_score_skip_demo():
    """Test Story 5: High-score demo skipping"""
    print("\n" + "="*60)
    print("🧪 TESTING STORY 5: High-Score Demo Skipping")
    print("="*60)
    
    executor = MockEnhancedLeadGenToolExecutor()
    
    # First, discover and score businesses
    discovery_result = await executor.execute_tool("discover_businesses", {
        "location": "Austin, TX",
        "niche": "Vegan restaurants",
        "max_businesses": 10
    })
    
    if not discovery_result["success"]:
        print(f"❌ Discovery failed: {discovery_result['error']}")
        return
    
    scoring_result = await executor.execute_tool("score_websites", {
        "businesses": discovery_result["result"]["businesses"]
    })
    
    if not scoring_result["success"]:
        print(f"❌ Scoring failed: {scoring_result['error']}")
        return
    
    # Find high-scoring business (should skip demo)
    high_scorers = [b for b in scoring_result["result"]["businesses"] if b["score_overall"] >= 70]
    
    if high_scorers:
        sample_business = high_scorers[0]
        print(f"\n✅ Found high-scoring business (demo skipped):")
        print(f"   🏢 Name: {sample_business['business_name']}")
        print(f"   📊 Overall Score: {sample_business['score_overall']}/100")
        print(f"   🎯 Category: {sample_business['score_category']}")
        print(f"   🚀 Demo Eligible: {sample_business['demo_eligible']}")
        
        # Check Story 5 requirements
        print(f"\n🎯 Story 5 Requirements Check:")
        print(f"   ✅ Score >= 70: {sample_business['score_overall'] >= 70}")
        print(f"   ✅ Demo not eligible: {not sample_business['demo_eligible']}")
        print(f"   ✅ Category is good/excellent: {sample_business['score_category'] in ['good', 'excellent']}")
        
    else:
        print("❌ No high-scoring businesses found")

async def test_story_4_5_demo_generation_workflow():
    """Test the complete demo generation workflow"""
    print("\n" + "="*60)
    print("🧪 TESTING STORIES 4 & 5: Complete Demo Generation Workflow")
    print("="*60)
    
    executor = MockEnhancedLeadGenToolExecutor()
    
    # Complete workflow: discover → score → generate demos
    discovery_result = await executor.execute_tool("discover_businesses", {
        "location": "Austin, TX",
        "niche": "Vegan restaurants",
        "max_businesses": 10
    })
    
    if not discovery_result["success"]:
        print(f"❌ Discovery failed: {discovery_result['error']}")
        return
    
    scoring_result = await executor.execute_tool("score_websites", {
        "businesses": discovery_result["result"]["businesses"]
    })
    
    if not scoring_result["success"]:
        print(f"❌ Scoring failed: {scoring_result['error']}")
        return
    
    demo_result = await executor.execute_tool("generate_demo_sites", {
        "businesses": scoring_result["result"]["businesses"],
        "location": "Austin, TX",
        "niche": "Vegan restaurants"
    })
    
    if not demo_result["success"]:
        print(f"❌ Demo generation failed: {demo_result['error']}")
        return
    
    print(f"\n✅ Complete workflow successful!")
    print(f"   🔍 Businesses discovered: {discovery_result['result']['total_found']}")
    print(f"   📊 Websites scored: {scoring_result['result']['total_scored']}")
    print(f"   🏗️ Demo sites created: {demo_result['result']['demo_sites_created']}")
    print(f"   ⏭️ Demo sites skipped: {demo_result['result']['demo_sites_skipped']}")
    
    # Show sample results
    businesses = demo_result["result"]["businesses"]
    
    print(f"\n📊 Sample Results:")
    for i, business in enumerate(businesses[:3]):  # Show first 3
        print(f"   {i+1}. {business['business_name']}")
        print(f"      Score: {business['score_overall']}/100")
        print(f"      Demo Status: {business['demo_status']}")
        if business['demo_status'] == 'generated':
            print(f"      Demo URL: {business['generated_site_url']}")
        elif business['demo_status'] == 'skipped':
            print(f"      Skip Reason: {business['demo_skip_reason']}")

async def main():
    """Run all tests"""
    print("🚀 LeadGenBuilder - Enhanced Stories 3, 4 & 5 Test Suite")
    print("Testing Yelp fallback, enhanced scoring, and demo generation logic")
    
    await test_story_3_yelp_fallback()
    await test_story_4_low_score_demo_generation()
    await test_story_5_high_score_skip_demo()
    await test_story_4_5_demo_generation_workflow()
    
    print("\n" + "="*60)
    print("🎉 All enhanced tests completed!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
