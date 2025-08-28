"""
LeadGenBuilder Tool Executor
Handles the execution of tools called by the AI agent
"""

import asyncio
import logging
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..external_apis.google_places_service import GooglePlacesService
from ..external_apis.yelp_fusion_service import YelpFusionService
from ..core.unified import UnifiedAnalyzer
from ..scoring.score_validation_service import ScoreValidationService
from ..scoring.fallback_scoring_service import FallbackScoringService
from ..templates.website_template_service import WebsiteTemplateService
from ..templates.demo_hosting_service import DemoHostingService
from ..ai.ai_content_generation_service import AIContentGenerationService
from ...schemas.business_search import BusinessSearchRequest
# WebsiteScoringRequest not available, using ComprehensiveSpeedRequest instead

logger = logging.getLogger(__name__)


class LeadGenToolExecutor:
    """
    Executes tools for the LeadGenBuilder AI agent
    
    This class provides a bridge between the AI agent's tool calls
    and the actual LeadGen service implementations
    """
    
    def __init__(self):
        self.google_places_service = GooglePlacesService()
        self.yelp_service = YelpFusionService()
        self.unified_analyzer = UnifiedAnalyzer()
        self.score_validation_service = ScoreValidationService()
        self.fallback_scoring_service = FallbackScoringService()
        self.template_service = WebsiteTemplateService()
        self.hosting_service = DemoHostingService()
        self.ai_service = AIContentGenerationService()
        
        # Rate limiting state
        self.request_times = []
        self.max_requests_per_second = 2
        
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with the given arguments
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool
            
        Returns:
            Result of the tool execution
        """
        
        try:
            # Apply rate limiting
            await self._apply_rate_limiting()
            
            logger.info(f"🔧 Executing tool: {tool_name}")
            logger.info(f"📋 Arguments: {arguments}")
            logger.info(f"📋 Arguments type: {type(arguments)}")
            logger.info(f"📋 Arguments keys: {list(arguments.keys()) if isinstance(arguments, dict) else 'Not a dict'}")
            
            # Route to appropriate tool implementation
            if tool_name == "discover_businesses":
                return await self._discover_businesses(arguments)
            elif tool_name == "score_websites":
                return await self._score_websites(arguments)
            elif tool_name == "generate_demo_sites":
                return await self._generate_demo_sites(arguments)
            elif tool_name == "export_data":
                return await self._export_data(arguments)
            elif tool_name == "generate_outreach":
                return await self._generate_outreach(arguments)
            elif tool_name == "confirm_parameters":
                return await self._confirm_parameters(arguments)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}",
                    "tool_name": tool_name
                }
                
        except Exception as e:
            logger.error(f"❌ Tool execution failed for {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": tool_name
            }
    
    async def _apply_rate_limiting(self):
        """Apply rate limiting to respect API constraints"""
        
        current_time = datetime.now()
        
        # Remove requests older than 1 second
        self.request_times = [
            req_time for req_time in self.request_times
            if (current_time - req_time).total_seconds() < 1.0
        ]
        
        # If we're at the limit, wait
        if len(self.request_times) >= self.max_requests_per_second:
            wait_time = 1.0 - (current_time - self.request_times[0]).total_seconds()
            if wait_time > 0:
                logger.info(f"⏳ Rate limiting: waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.request_times.append(current_time)
    
    async def _discover_businesses(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover businesses using Google Places and Yelp APIs
        """
        
        # Validate required arguments
        if "location" not in arguments:
            error_msg = f"Missing required argument 'location' in arguments: {arguments}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool_name": "discover_businesses"
            }
        
        if "niche" not in arguments:
            error_msg = f"Missing required argument 'niche' in arguments: {arguments}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool_name": "discover_businesses"
            }
        
        location = arguments["location"]
        niche = arguments["niche"]
        max_businesses = arguments.get("max_businesses", 4)
        
        logger.info(f"🔍 Discovering {niche} businesses in {location}")
        
        try:
            businesses = []
            discovery_logs = []
            max_retries = 3
            retry_count = 0
            
            # Try Google Places first with retry logic
            while retry_count < max_retries:
                try:
                    logger.info(f"🔍 Searching with Google Places API (attempt {retry_count + 1})")
                    if retry_count == 0:
                        discovery_logs.append("Scraping Google Places...")
                    
                    search_request = BusinessSearchRequest(
                        query=f"{niche} {location}",
                        location=location,
                        max_results=max_businesses,
                        run_id=f"discover_{niche}_{location}"
                    )
                    
                    # Google Places service is now async, so await it
                    google_results = await self.google_places_service.search_businesses(search_request)
                    
                    # Check if we got an error response
                    if hasattr(google_results, 'error'):
                        logger.warning(f"Google Places search failed: {google_results.error}")
                        
                        # Check if it's a rate limit error
                        if hasattr(google_results, 'error_code') and google_results.error_code == "RATE_LIMIT_EXCEEDED":
                            retry_after = getattr(google_results, 'retry_after', 3)
                            discovery_logs.append(f"Google throttled us — retrying in {retry_after} s...")
                            
                            # Wait for the specified retry time
                            import asyncio
                            await asyncio.sleep(retry_after)
                            retry_count += 1
                            continue
                        else:
                            # Check if it's a robots.txt or scraping blocked error
                            error_msg = str(google_results.error).lower()
                            if any(blocked in error_msg for blocked in ['robots.txt', 'scraping blocked', 'access denied', 'forbidden']):
                                discovery_logs.append("robots.txt blocks Google Places")
                                logger.warning("Google Places blocked by robots.txt, switching to Yelp Fusion")
                                break
                            else:
                                discovery_logs.append(f"Google Places failed: {google_results.error}")
                                break
                            
                    elif hasattr(google_results, 'results'):
                        for business in google_results.results:
                            business_data = {
                                "business_name": business.name,
                                "contact_name": "",  # Not available in Google Places
                                "email": "",  # Not available in Google Places
                                "phone": business.phone or "",
                                "website": business.website or "",
                                "address": business.address or business.formatted_address or "",
                                "postcode": "",  # Extract from address if needed
                                "rating": business.rating,
                                "review_count": business.user_ratings_total,
                                "categories": business.types or [],
                                "price_level": business.price_level,
                                "place_id": business.place_id
                            }
                            businesses.append(business_data)
                        
                        # Add progressive discovery logs
                        if len(businesses) > 0:
                            discovery_logs.append(f"Found {len(businesses)}")
                            if len(businesses) >= max_businesses:
                                discovery_logs.append("Discovery complete")
                        
                        logger.info(f"✅ Google Places found {len(businesses)} businesses")
                        break  # Success, exit retry loop
                    else:
                        logger.warning(f"Unexpected Google Places response format: {type(google_results)}")
                        break
                        
                except Exception as e:
                    logger.warning(f"Google Places search failed: {e}")
                    discovery_logs.append(f"Google Places failed: {str(e)}")
                    break
            
            # If we need more businesses, try Yelp
            if len(businesses) < max_businesses:
                try:
                    logger.info("🔍 Searching with Yelp Fusion API")
                    if len(businesses) == 0:
                        discovery_logs.append("Switching to Yelp Fusion...")
                    remaining = max_businesses - len(businesses)
                    
                    # Create proper Yelp request object
                    from src.schemas.yelp_fusion import YelpBusinessSearchRequest
                    yelp_request = YelpBusinessSearchRequest(
                        term=niche,
                        location=location,
                        limit=remaining,
                        run_id=f"discover_{niche}_{location}"
                    )
                    
                    # Yelp service is now async, so await it
                    yelp_results = await self.yelp_service.search_businesses(yelp_request)
                    
                    # Check if we got an error response
                    if hasattr(yelp_results, 'error'):
                        logger.warning(f"Yelp search failed: {yelp_results.error}")
                        discovery_logs.append(f"Yelp failed: {yelp_results.error}")
                    elif hasattr(yelp_results, 'businesses'):
                        for business in yelp_results.businesses:
                            # Handle YelpBusinessData objects (not dictionaries)
                            business_data = {
                                "business_name": getattr(business, 'name', ''),
                                "contact_name": "",
                                "email": "",
                                "phone": getattr(business, 'phone', ''),
                                "website": getattr(business, 'url', ''),
                                "address": ', '.join([
                                    getattr(business.location, 'address1', '') if business.location else '',
                                    getattr(business.location, 'city', '') if business.location else '',
                                    getattr(business.location, 'state', '') if business.location else ''
                                ]).strip(', '),
                                "postcode": getattr(business.location, 'zip_code', '') if business.location else '',
                                "rating": getattr(business, 'rating', None),
                                "review_count": getattr(business, 'review_count', None),
                                "categories": [cat.title for cat in getattr(business, 'categories', [])] if hasattr(business, 'categories') else [],
                                "price_level": getattr(business, 'price', None),
                                "place_id": getattr(business, 'id', '')
                            }
                            businesses.append(business_data)
                        
                        # Add progressive discovery logs for Yelp results
                        if len(businesses) > 0:
                            discovery_logs.append(f"Found {len(businesses)}")
                            if len(businesses) >= max_businesses:
                                discovery_logs.append("Discovery complete")
                        
                        logger.info(f"✅ Yelp found {len(yelp_results.businesses)} businesses")
                    else:
                        logger.warning(f"Unexpected Yelp response format: {type(yelp_results)}")
                        
                except Exception as e:
                    logger.warning(f"Yelp search failed: {e}")
                    discovery_logs.append(f"Yelp failed: {str(e)}")
            
            # Limit to requested maximum
            businesses = businesses[:max_businesses]
            
            # Ensure we have the final discovery complete log
            if "Discovery complete" not in discovery_logs:
                discovery_logs.append("Discovery complete")
            
            logger.info(f"✅ Discovery completed: {len(businesses)} businesses found")
            
            return {
                "success": True,
                "tool_name": "discover_businesses",
                "result": {
                    "businesses": businesses,
                    "total_found": len(businesses),
                    "location": location,
                    "niche": niche,
                    "discovery_logs": discovery_logs,
                    "processing_time": 0.0  # Would be calculated in real implementation
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Business discovery failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": "discover_businesses"
            }
    
    async def _score_websites(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score business websites using UnifiedAnalyzer for comprehensive analysis
        """
        
        businesses = arguments["businesses"]
        
        logger.info(f"📊 Scoring {len(businesses)} business websites using UnifiedAnalyzer")
        
        try:
            scored_businesses = []
            
            for business in businesses:
                scored_business = business.copy()
                
                if business.get("website"):
                    try:
                        logger.info(f"📊 Scoring website: {business['website']}")
                        
                        # Run unified analysis using UnifiedAnalyzer for comprehensive scoring
                        unified_result = await self.unified_analyzer.run_comprehensive_analysis(
                            url=business["website"],
                            strategy="mobile"
                        )
                        
                        if unified_result.get("success"):
                            # Unified analysis succeeded - extract all available scores and metrics
                            scores = unified_result.get("scores", {})
                            details = unified_result.get("details", {})
                            
                            # Core performance scores
                            scored_business.update({
                                "score_perf": int(scores.get("performance", 0)),
                                "score_access": int(scores.get("accessibility", 0)),
                                "score_seo": int(scores.get("seo", 0)),
                                "score_trust": int(scores.get("trust", 0)),
                                "score_overall": int(scores.get("overall", 0)),
                                "scoring_method": "unified",
                                "confidence_level": "high"
                            })
                            
                            # Additional comprehensive metrics from unified analysis
                            if "pagespeed" in details:
                                pagespeed_data = details["pagespeed"]
                                if "coreWebVitals" in pagespeed_data:
                                    core_vitals = pagespeed_data["coreWebVitals"]
                                    scored_business.update({
                                        "lcp_score": core_vitals.get("largestContentfulPaint", {}).get("value", 0),
                                        "fid_score": core_vitals.get("firstInputDelay", {}).get("value", 0),
                                        "cls_score": core_vitals.get("cumulativeLayoutShift", {}).get("value", 0)
                                    })
                            
                            # Trust and CRO metrics from unified analysis
                            if "trust" in details:
                                trust_data = details["trust"]
                                scored_business.update({
                                    "ssl_status": trust_data.get("ssl", False),
                                    "security_headers": trust_data.get("securityHeaders", []),
                                    "domain_age": trust_data.get("domainAge", "unknown")
                                })
                            
                            # Mobile usability metrics
                            if "mobileUsability" in details:
                                mobile_data = details["mobileUsability"]
                                scored_business.update({
                                    "mobile_friendly": mobile_data.get("mobileFriendly", False),
                                    "mobile_score": mobile_data.get("score", 0),
                                    "mobile_issues": mobile_data.get("issues", [])
                                })
                            
                            # Opportunities for improvement
                            if "opportunities" in details:
                                scored_business["improvement_opportunities"] = details["opportunities"]
                            
                            # Step 2: Run score validation for confidence assessment
                            try:
                                # Create a simplified score structure for validation
                                validation_scores = {
                                    "overall_score": scores.get("overall", 0),
                                    "performance": scores.get("performance", 0),
                                    "accessibility": scores.get("accessibility", 0),
                                    "seo": scores.get("seo", 0),
                                    "bestPractices": scores.get("bestPractices", 0)
                                }
                                
                                validation_result = await self.score_validation_service.validate_scores(
                                    lighthouse_scores=[scored_business],
                                    comprehensive_scores=[validation_scores],
                                    business_id=business.get("business_id", "unknown"),
                                    run_id=arguments.get("run_id")
                                )
                                
                                if validation_result:
                                    scored_business.update({
                                        "validation_confidence": validation_result.confidence_level,
                                        "score_correlation": validation_result.score_correlation,
                                        "discrepancy_count": validation_result.discrepancy_count,
                                        "final_weighted_score": validation_result.final_weighted_score
                                    })
                                    
                            except Exception as validation_error:
                                logger.warning(f"Score validation failed for {business['website']}: {validation_error}")
                                scored_business["validation_confidence"] = "medium"
                                
                        else:
                            # Unified analysis failed - use fallback scoring service
                            logger.warning(f"Unified analysis failed for {business['website']}, using fallback scoring")
                            
                            fallback_result = await self.fallback_scoring_service.run_fallback_scoring(
                                website_url=business["website"],
                                business_id=business.get("business_id", "unknown"),
                                unified_failure_reason=unified_result.get("error", "unknown_error"),
                                run_id=arguments.get("run_id")
                            )
                            
                            if fallback_result.get("success"):
                                fallback_scores = fallback_result.get("scores", {})
                                scored_business.update({
                                    "score_perf": fallback_scores.get("performance_score", 0),
                                    "score_access": fallback_scores.get("accessibility_score", 0),
                                    "score_seo": fallback_scores.get("seo_score", 0),
                                    "score_trust": fallback_scores.get("best_practices_score", 0),
                                    "score_overall": fallback_scores.get("overall_score", 0),
                                    "scoring_method": "fallback_comprehensive",
                                    "confidence_level": "medium",
                                    "fallback_reason": unified_result.get("error"),
                                    "fallback_quality": fallback_result.get("quality_metrics", {})
                                })
                            else:
                                # Both unified analysis and fallback failed
                                logger.error(f"Both unified analysis and fallback failed for {business['website']}")
                                scored_business.update({
                                    "score_perf": 0,
                                    "score_access": 0,
                                    "score_seo": 0,
                                    "score_trust": 0,
                                    "score_overall": 0,
                                    "scoring_method": "failed",
                                    "confidence_level": "low",
                                    "error": "All scoring methods failed"
                                })
                        
                        # Business categorization based on Epic 2 scoring (Story 4 & 5)
                        score_overall = scored_business.get("score_overall", 0)
                        confidence = scored_business.get("confidence_level", "low")
                        
                        if score_overall >= 80 and confidence in ["high", "medium"]:
                            scored_business["score_category"] = "excellent"
                            scored_business["demo_eligible"] = False
                        elif score_overall >= 70 and confidence in ["high", "medium"]:
                            scored_business["score_category"] = "good"
                            scored_business["demo_eligible"] = False
                        elif score_overall >= 50:
                            scored_business["score_category"] = "fair"
                            scored_business["demo_eligible"] = True
                        else:
                            scored_business["score_category"] = "poor"
                            scored_business["demo_eligible"] = True
                        
                        # Demo priority based on score and confidence
                        if score_overall < 50 and confidence == "low":
                            scored_business["demo_priority"] = "high"
                        elif score_overall < 70:
                            scored_business["demo_priority"] = "medium"
                        else:
                            scored_business["demo_priority"] = "none"
                        
                        # Generate top issues for low scorers using unified analysis data
                        issues = []
                        if scored_business.get("score_perf", 0) < 60:
                            issues.append(f"Poor performance score ({scored_business['score_perf']}/100)")
                        if scored_business.get("score_access", 0) < 60:
                            issues.append(f"Accessibility issues ({scored_business['score_access']}/100)")
                        if scored_business.get("score_seo", 0) < 60:
                            issues.append(f"SEO optimization needed ({scored_business['score_seo']}/100)")
                        if scored_business.get("score_trust", 0) < 60:
                            issues.append(f"Trust signals missing ({scored_business['score_trust']}/100)")
                        
                        # Add unified analysis specific issues
                        if scored_business.get("ssl_status") == False:
                            issues.append("SSL certificate missing or invalid")
                        if scored_business.get("mobile_friendly") == False:
                            issues.append("Mobile usability improvements required")
                        if scored_business.get("improvement_opportunities"):
                            # Add first opportunity as an issue
                            first_opp = scored_business["improvement_opportunities"][0] if scored_business["improvement_opportunities"] else None
                            if first_opp:
                                issues.append(f"Performance opportunity: {first_opp.get('title', 'Unknown')}")
                        
                        scored_business["top_issues"] = issues[:3]  # Top 3 issues
                        
                    except Exception as e:
                        logger.error(f"❌ Website scoring failed for {business['website']}: {e}")
                        scored_business.update({
                            " score_perf": 0,
                            "score_access": 0,
                            "score_seo": 0,
                            "score_trust": 0,
                            "score_overall": 0,
                            "scoring_method": "error",
                            "confidence_level": "low",
                            "error": str(e)
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
            
            # Calculate statistics using unified analysis data
            valid_scores = [b for b in scored_businesses if b.get("scoring_method") not in ["failed", "error", "no_website"]]
            if valid_scores:
                average_score = sum(b["score_overall"] for b in valid_scores) / len(valid_scores)
                low_scorers = len([b for b in valid_scores if b["score_overall"] < 70])
                high_confidence = len([b for b in valid_scores if b.get("confidence_level") == "high"])
                
                logger.info(f"✅ Website scoring completed using UnifiedAnalyzer: avg score {average_score:.1f}, {low_scorers} low scorers, {high_confidence} high confidence")
            else:
                average_score = 0
                low_scorers = 0
                high_confidence = 0
                logger.warning("⚠️ No valid scores generated - all scoring methods failed")
            
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
                    "processing_time": 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Website scoring failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": "score_websites"
            }
    
    async def _generate_demo_sites(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and deploy demo sites for businesses with low scores using unified analysis data
        """
        
        businesses = arguments["businesses"]
        location = arguments["location"]
        niche = arguments["niche"]
        
        logger.info(f"🏗️ Generating demo sites for qualifying businesses using unified analysis scoring")
        
        try:
            updated_businesses = []
            demo_count = 0
            skipped_count = 0
            
            for business in businesses:
                updated_business = business.copy()
                score_overall = business.get("score_overall", 0)
                confidence_level = business.get("confidence_level", "low")
                scoring_method = business.get("scoring_method", "unknown")
                
                # Generate demo for businesses with score < 70 (Story 4)
                # Use unified analysis confidence levels to determine eligibility
                if score_overall < 70 and confidence_level in ["high", "medium"]:
                    try:
                        logger.info(f"🏗️ Generating demo for {business['business_name']} (score: {score_overall}, confidence: {confidence_level}, method: {scoring_method})")
                        
                        # Generate template using the template service
                        template_result = await self.template_service.generate_template(
                            business, niche, location
                        )
                        
                        # Deploy the template to hosting service
                        deployment_result = await self.hosting_service.deploy_demo_site(
                            template_result, business["business_name"]
                        )
                        
                        updated_business.update({
                            "generated_site_url": deployment_result['demo_url'],
                            "demo_status": "generated",
                            "demo_generated_at": datetime.now().isoformat(),
                            "demo_source": f"Unified Analysis {scoring_method} scoring",
                            "demo_confidence": confidence_level
                        })
                        demo_count += 1
                        
                        logger.info(f"✅ Demo site deployed: {deployment_result['demo_url']}")
                        
                    except Exception as e:
                        logger.warning(f"Failed to generate demo site for {business['business_name']}: {e}")
                        updated_business.update({
                            "demo_status": "failed",
                            "demo_error": str(e),
                            "demo_source": f"Unified Analysis {scoring_method} scoring"
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
                    
                    logger.info(f"⏭️ Skipping demo for {business['business_name']}: {skip_reason}")
                    updated_business.update({
                        "demo_status": "skipped",
                        "demo_skip_reason": skip_reason,
                        "demo_source": f"Unified Analysis {scoring_method} scoring",
                        "demo_confidence": confidence_level
                    })
                    skipped_count += 1
                
                # Handle edge cases (no score, failed scoring, etc.)
                else:
                    logger.warning(f"⚠️ Undetermined demo eligibility for {business['business_name']} (score: {score_overall}, confidence: {confidence_level})")
                    updated_business.update({
                        "demo_status": "pending_review",
                        "demo_skip_reason": "Manual review required - insufficient scoring data",
                        "demo_source": f"Unified Analysis {scoring_method} scoring",
                        "demo_confidence": confidence_level
                    })
                
                updated_businesses.append(updated_business)
            
            logger.info(f"✅ Demo site generation completed using unified analysis data: {demo_count} generated, {skipped_count} skipped")
            
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
                    "processing_time": 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Demo site generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": "generate_demo_sites"
            }
    
    async def _export_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export business data to CSV format
        """
        
        businesses = arguments["businesses"]
        
        logger.info(f"📊 Exporting data for {len(businesses)} businesses")
        
        try:
            # In a real implementation, this would create an actual CSV file
            # and upload it to cloud storage or Google Sheets
            import uuid
            export_id = str(uuid.uuid4())[:8]
            download_url = f"https://exports.leadgen-demos.com/export-{export_id}.csv"
            
            logger.info(f"✅ Data export completed: {download_url}")
            
            return {
                "success": True,
                "tool_name": "export_data",
                "result": {
                    "download_url": download_url,
                    "business_count": len(businesses),
                    "export_id": export_id,
                    "processing_time": 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Data export failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": "export_data"
            }
    
    async def _generate_outreach(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate personalized outreach messages for businesses
        """
        
        businesses = arguments["businesses"]
        
        logger.info(f"💬 Generating outreach messages for {len(businesses)} businesses")
        
        try:
            businesses_with_outreach = []
            
            for business in businesses:
                business_with_outreach = business.copy()
                
                try:
                    # Generate personalized outreach messages
                    issues_text = ", ".join(business.get("top_issues", [])[:2]) if business.get("top_issues") else "general website improvements"
                    demo_mention = f" I've created a demo website at {business['generated_site_url']} to show the potential." if business.get("generated_site_url") else ""
                    
                    # Email
                    business_with_outreach["outreach_email"] = {
                        "subject": f"Quick Website Enhancement for {business['business_name']}",
                        "body": f"""Hi there,

I came across {business['business_name']} and noticed some opportunities to enhance your online presence. 

Based on my analysis, I identified these areas for improvement: {issues_text}.{demo_mention}

I'd love to discuss how we can help boost your website's performance and attract more customers.

Would you be interested in a brief 15-minute call this week?

Best regards,
[Your Name]"""
                    }
                    
                    # WhatsApp
                    business_with_outreach["outreach_whatsapp"] = f"""Hi! I analyzed {business['business_name']}'s website and found some quick wins to attract more customers: {issues_text}.{demo_mention} Interested in a brief chat about improving your online presence?"""
                    
                    # SMS (≤ 280 chars)
                    sms_demo = f" See demo: {business['generated_site_url']}" if business.get("generated_site_url") else ""
                    business_with_outreach["outreach_sms"] = f"Hi! Found quick wins for {business['business_name']}'s website.{sms_demo} 15min call to discuss? Reply YES"
                    
                    # Ensure SMS is under 280 characters
                    if len(business_with_outreach["outreach_sms"]) > 280:
                        business_with_outreach["outreach_sms"] = f"Website improvements available for {business['business_name']}. Quick call? Reply YES"
                    
                except Exception as e:
                    logger.warning(f"Failed to generate outreach for {business['business_name']}: {e}")
                    business_with_outreach["outreach_email"] = {"subject": "Website Enhancement Opportunity", "body": "Hi, I'd like to discuss improving your website."}
                    business_with_outreach["outreach_whatsapp"] = f"Hi! I have some suggestions to improve {business['business_name']}'s website. Interested?"
                    business_with_outreach["outreach_sms"] = f"Website tips for {business['business_name']}. Quick call? Reply YES"
                
                businesses_with_outreach.append(business_with_outreach)
            
            logger.info(f"✅ Outreach generation completed for {len(businesses_with_outreach)} businesses")
            
            return {
                "success": True,
                "tool_name": "generate_outreach",
                "result": {
                    "businesses": businesses_with_outreach,
                    "outreach_generated": len(businesses_with_outreach),
                    "processing_time": 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Outreach generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": "generate_outreach"
            }
    
    async def _confirm_parameters(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle parameter confirmation (this is more of a UI flow)
        """
        
        # Validate required arguments
        if "location" not in arguments:
            error_msg = f"Missing required argument 'location' in arguments: {arguments}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool_name": "confirm_parameters"
            }
        
        if "niche" not in arguments:
            error_msg = f"Missing required argument 'niche' in arguments: {arguments}"
            logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "tool_name": "confirm_parameters"
            }
        
        location = arguments["location"]
        niche = arguments["niche"]
        assumptions = arguments.get("assumptions", [])
        
        return {
            "success": True,
            "tool_name": "confirm_parameters",
            "requires_confirmation": True,
            "result": {
                "location": location,
                "niche": niche,
                "assumptions": assumptions,
                "confirmation_message": f"I'll search for {niche} businesses in {location}. Is this correct?",
                "processing_time": 0.0
            }
        }
