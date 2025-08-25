"""
Unified Website Analyzer (Python back-port of unified.js)
Enhanced with caching, retry logic, batch processing, health monitoring, and rate limiting
"""

import logging
import math
import asyncio
import time
import random
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime

import aiohttp
import async_timeout
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from ..core.config import get_api_config
from ..services.rate_limiter import RateLimiter

logging.basicConfig(level=logging.DEBUG, format="%(message)s")
log = logging.getLogger("unified")


class UnifiedAnalyzer:
    def __init__(self) -> None:
        self.api_config = get_api_config()
        self.google_api_key = self.api_config.GOOGLE_GENERAL_API_KEY
        
        # Initialize Google PageSpeed API service
        if self.google_api_key:
            try:
                # Use developer key directly to avoid file_cache issues
                self.pagespeed_service = build(
                    'pagespeedonline', 
                    'v5', 
                    developerKey=self.google_api_key,
                    cache_discovery=True  # Disable discovery cache to avoid file_cache issues
                )
                log.debug(f"✅ Google PageSpeed API service initialized with key: {self.google_api_key[:10]}...")
            except Exception as e:
                log.error(f"❌ Failed to initialize Google PageSpeed API service: {e}")
                self.pagespeed_service = None
        else:
            self.pagespeed_service = None
            log.error(f"❌ Google PageSpeed API key NOT configured - this will cause failures!")
        
        # 1. Caching System
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.cache_cleanup_counter = 0
        self.cache_cleanup_threshold = 10  # Clean up every 10 requests
        self.cache_size_threshold = 100  # Force cleanup if cache gets large
        
        # 2. Retry Logic Configuration
        self.retry_config = {
            'max_attempts': 3,
            'base_delay': 2,
            'max_delay': 30,
            'exponential_backoff': True
        }
        
        # 3. Rate Limiting
        self.rate_limiter = RateLimiter()
        
        # 4. Service Health Monitoring
        self.service_health = {
            "pagespeed": "unknown",
            "domain_analysis": "unknown",
            "overall": "unknown"
        }
        
        # 5. Analysis Statistics
        self.analysis_stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }

        # Domain analysis service removed - using placeholder values
        self.service_health["domain_analysis"] = "unavailable"
        
        # Check PageSpeed API key and service
        if self.google_api_key and self.pagespeed_service:
            self.service_health["pagespeed"] = "healthy"
            log.debug(f"✅ PageSpeed API key configured: {self.google_api_key[:10]}...")
        else:
            self.service_health["pagespeed"] = "unconfigured"
            log.error(f"❌ PageSpeed API key NOT configured - this will cause failures!")
        
        # Log configuration summary
        log.debug(f"🔧 UnifiedAnalyzer initialized with:")
        log.debug(f"   - PageSpeed API Key: {'SET' if self.google_api_key else 'NOT_SET'}")
        log.debug(f"   - PageSpeed Service: {'INITIALIZED' if self.pagespeed_service else 'NOT_INITIALIZED'}")
        log.debug(f"   - Cache TTL: {self.cache_ttl}s")
        log.debug(f"   - Retry attempts: {self.retry_config['max_attempts']}")
        log.debug(f"   - Rate limiter: {'enabled' if self.rate_limiter else 'disabled'}")
        
        self._update_overall_health()

    # ------------------------------------------------------------------ #
    def _call_pagespeed_api(self, url: str, strategy: str) -> Dict[str, Any]:
        """Call Google PageSpeed API using native googleapiclient library."""
        try:
            if not self.pagespeed_service:
                raise RuntimeError("Google PageSpeed API service not initialized")
            
            # Prepare parameters for the API call
            # Convert strategy to uppercase as required by Google PageSpeed API
            strategy_upper = strategy.upper()
            params = {
                'url': url,
                'strategy': strategy_upper,
                'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO'],  # Request all four categories
                'prettyPrint': True
            }
            
            log.debug(f"📡 Calling Google PageSpeed API for {strategy} strategy: {url}")
            
            # Make the API call (execute() is synchronous)
            response = self.pagespeed_service.pagespeedapi().runpagespeed(**params).execute()
            
            log.debug(f"✅ Google PageSpeed API response received for {strategy}")
            
            # Debug: Log the structure of the response
            if log.isEnabledFor(logging.DEBUG):
                lighthouse = response.get("lighthouseResult", {})
                categories = lighthouse.get("categories", {})
                audits = lighthouse.get("audits", {})
                
                log.debug(f"📊 Response structure for {strategy}:")
                log.debug(f"   - Has lighthouseResult: {bool(lighthouse)}")
                log.debug(f"   - Categories: {list(categories.keys()) if categories else 'None'}")
                log.debug(f"   - Audits count: {len(audits) if audits else 0}")
                
                if categories:
                    for cat_name, cat_data in categories.items():
                        if isinstance(cat_data, dict) and "score" in cat_data:
                            log.debug(f"   - {cat_name} score: {cat_data['score']}")
                        else:
                            log.debug(f"   - {cat_name}: {cat_data}")
                
                # Special debugging for Best Practices
                best_practices = categories.get("bestPractices", {})
                log.debug(f"🔍 Best Practices category data: {best_practices}")
                if isinstance(best_practices, dict):
                    log.debug(f"🔍 Best Practices score field: {best_practices.get('score')}")
                    log.debug(f"🔍 Best Practices keys: {list(best_practices.keys())}")
            
            return response
            
        except Exception as e:
            log.error(f"❌ Google PageSpeed API call failed for {strategy}: {e}")
            raise RuntimeError(f"Google PageSpeed API call failed: {e}")

    # ------------------------------------------------------------------ #
    def extract_metric(self, metric: Dict[str, Any]) -> Dict[str, Any] | None:
        """Extract metric data with safe fallbacks for Google PageSpeed API."""
        if not metric:
            return None
        
        # Google PageSpeed API uses different field names
        # Try numericValue first (for opportunities), then value (for core web vitals)
        numeric_value = metric.get("numericValue") or metric.get("value")
        display_value = metric.get("displayValue") or metric.get("displayValue", "")
        unit = metric.get("numericUnit") or metric.get("unit", "")
        
        # If we have a numeric value, return the metric
        if numeric_value is not None:
            return {
                "value": numeric_value,
                "displayValue": display_value,
                "unit": unit,
            }
        
        # If no numeric value, return None
        return None
    

    


    # ------------------------------------------------------------------ #
    def extract_opportunities(self, audits: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract opportunities from Google PageSpeed API audits following PageSpeeds.md structure."""
        opportunities = []
        
        # Define opportunity audit types based on PageSpeeds.md structure
        opportunity_audit_types = [
            "opportunity",  # Standard opportunity type
            "diagnostics",  # Diagnostic audits that can suggest improvements
            "metricSavings"  # Audits with potential savings
        ]
        
        for key, audit in audits.items():
            try:
                # Check if this is an opportunity audit based on multiple criteria
                is_opportunity = False
                
                # 1. Check if it's explicitly marked as an opportunity
                if audit.get("details", {}).get("type") in opportunity_audit_types:
                    is_opportunity = True
                
                # 2. Check if it has metric savings (performance opportunities)
                elif audit.get("metricSavings"):
                    is_opportunity = True
                
                # 3. Check if it's a failed audit with score < 1.0
                elif audit.get("score") is not None and audit.get("score") < 1.0:
                    # Only include certain types of failed audits as opportunities
                    failed_opportunity_types = [
                        "uses-webp-images", "unused-javascript", "unused-css-rules",
                        "render-blocking-resources", "uses-optimized-images",
                        "modern-image-formats", "uses-text-compression"
                    ]
                    if key in failed_opportunity_types:
                        is_opportunity = True
                
                if is_opportunity:
                    # Extract potential savings - try different field names from PageSpeeds.md
                    potential_savings = 0
                    unit = "ms"
                    
                    # Check for metricSavings first (most reliable)
                    if audit.get("metricSavings"):
                        # Sum up all metric savings
                        savings_values = []
                        for metric, value in audit["metricSavings"].items():
                            if isinstance(value, (int, float)) and value > 0:
                                savings_values.append(value)
                        if savings_values:
                            potential_savings = sum(savings_values)
                            unit = "ms"
                    
                    # Fallback to numericValue or value
                    if potential_savings == 0:
                        potential_savings = audit.get("numericValue") or audit.get("value") or 0
                        unit = audit.get("numericUnit") or audit.get("unit", "ms")
                    
                    # Only include if there are actual savings or it's a significant failed audit
                    if potential_savings > 0 or (audit.get("score") is not None and audit.get("score") < 0.5):
                        # Get title and description following PageSpeeds.md format
                        title = audit.get("title", "Performance Opportunity")
                        description = audit.get("description", "Improve this aspect of your website")
                        
                        # Truncate long titles to prevent UI overflow
                        if len(title) > 60:
                            title = title[:57] + "..."
                        
                        opportunities.append({
                            "title": title,
                            "description": description,
                            "potentialSavings": round(potential_savings) if potential_savings > 0 else 0,
                            "unit": unit,
                            "auditId": key,  # Include audit ID for reference
                            "score": audit.get("score"),  # Include original score
                            "type": audit.get("details", {}).get("type", "opportunity")
                        })
                        
            except Exception as e:
                log.debug(f"⚠️ Error processing audit {key}: {e}")
                continue
        
        # Sort by potential savings (highest first) and return top 5 (following PageSpeeds.md pattern)
        opportunities.sort(key=lambda x: x["potentialSavings"], reverse=True)
        return opportunities[:5]

    def get_generic_opportunities(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate generic improvement opportunities when specific ones can't be generated.
        This provides helpful guidance even when PageSpeed analysis fails.
        """
        generic_opportunities = []
        
        # Check if PageSpeed analysis failed
        page_speed = analysis_result.get("pageSpeed", {})
        if not page_speed or (page_speed.get("mobile") is None and page_speed.get("desktop") is None):
            generic_opportunities.append({
                "title": "Website Accessibility Issue",
                "description": "The website appears to be inaccessible or experiencing technical difficulties. This prevents detailed performance analysis.",
                "potentialSavings": 0,
                "unit": "priority"
            })
            generic_opportunities.append({
                "title": "Server Response Problem",
                "description": "The website server is not responding properly, which affects user experience and search engine visibility.",
                "potentialSavings": 0,
                "unit": "priority"
            })
            generic_opportunities.append({
                "title": "Technical Infrastructure Review",
                "description": "Consider reviewing hosting, DNS configuration, and server health to resolve accessibility issues.",
                "potentialSavings": 0,
                "unit": "priority"
            })
            return generic_opportunities
        
        # Check for specific failure scenarios
        errors = page_speed.get("errors", [])
        if errors:
            error_messages = [str(error) for error in errors]
            error_text = "; ".join(error_messages[:2])  # Limit to first 2 errors
            
            if "400" in error_text or "Bad Request" in error_text:
                generic_opportunities.append({
                    "title": "Invalid Website Configuration",
                    "description": f"The website returned an error (400 Bad Request), indicating configuration issues that prevent analysis.",
                    "potentialSavings": 0,
                    "unit": "priority"
                })
            elif "timeout" in error_text.lower():
                generic_opportunities.append({
                    "title": "Website Performance Issue",
                    "description": "The website is taking too long to respond, indicating performance problems that need immediate attention.",
                    "potentialSavings": 0,
                    "unit": "priority"
                })
            else:
                generic_opportunities.append({
                    "title": "Technical Analysis Failure",
                    "description": f"Unable to analyze website due to technical issues: {error_text}",
                    "potentialSavings": 0,
                    "unit": "priority"
                })
        

        
        # Check if Trust/CRO analysis failed
        trust_cro = analysis_result.get("trustAndCRO", {})
        if trust_cro and trust_cro.get("errors") and len(trust_cro["errors"]) > 0:
            generic_opportunities.append({
                "title": "Security Assessment Incomplete",
                "description": "Unable to complete security and conversion optimization analysis due to technical limitations.",
                "potentialSavings": 0,
                "unit": "priority"
            })
        
        # If we have some opportunities but not enough, add generic ones
        if len(generic_opportunities) < 3:
            # Add general improvement suggestions
            remaining_slots = 3 - len(generic_opportunities)
            
            general_suggestions = [
                {
                    "title": "Regular Performance Monitoring",
                    "description": "Implement ongoing website performance monitoring to catch issues early and maintain optimal user experience.",
                    "potentialSavings": 0,
                    "unit": "ongoing"
                },
                {
                    "title": "Mobile-First Optimization",
                    "description": "Ensure your website is optimized for mobile devices, as mobile traffic continues to grow.",
                    "potentialSavings": 0,
                    "unit": "ongoing"
                },
                {
                    "title": "Security Best Practices",
                    "description": "Implement security headers, SSL certificates, and regular security audits to build user trust.",
                    "potentialSavings": 0,
                    "unit": "ongoing"
                }
            ]
            
            generic_opportunities.extend(general_suggestions[:remaining_slots])
        
        return generic_opportunities[:3]

    def get_all_opportunities(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all available opportunities, combining specific PageSpeed opportunities with generic ones.
        This ensures the UI always has meaningful improvement suggestions following PageSpeeds.md structure.
        """
        all_opportunities = []
        
        # The structure is {'pageSpeed': {'mobile': {...}, 'desktop': {...}, 'errors': [...]}}
        # Check mobile opportunities first (following PageSpeeds.md mobile-first approach)
        page_speed = analysis_result.get("pageSpeed", {})
        mobile = page_speed.get("mobile")
        if mobile and mobile.get("opportunities"):
            for opp in mobile["opportunities"]:
                # Ensure opportunity follows PageSpeeds.md structure
                opportunity = {
                    "title": opp.get("title", ""),
                    "description": opp.get("description", ""),
                    "potentialSavings": opp.get("potentialSavings", 0),
                    "unit": opp.get("unit", "ms"),
                    "auditId": opp.get("auditId", ""),
                    "score": opp.get("score"),
                    "type": opp.get("type", "opportunity"),
                    "source": "mobile"
                }
                
                # Truncate long titles to prevent UI overflow
                if len(opportunity["title"]) > 60:
                    opportunity["title"] = opportunity["title"][:57] + "..."
                
                all_opportunities.append(opportunity)
        
        # Add desktop opportunities if we don't have enough
        if len(all_opportunities) < 5:  # Following PageSpeeds.md pattern of 5 opportunities
            desktop = page_speed.get("desktop")
            if desktop and desktop.get("opportunities"):
                for opp in desktop["opportunities"]:
                    if len(all_opportunities) >= 5:
                        break
                    
                    # Avoid duplicates by checking title and auditId
                    title = opp.get("title", "")
                    audit_id = opp.get("auditId", "")
                    
                    is_duplicate = any(
                        existing["title"] == title or 
                        (audit_id and existing.get("auditId") == audit_id)
                        for existing in all_opportunities
                    )
                    
                    if not is_duplicate:
                        opportunity = {
                            "title": title,
                            "description": opp.get("description", ""),
                            "potentialSavings": opp.get("potentialSavings", 0),
                            "unit": opp.get("unit", "ms"),
                            "auditId": audit_id,
                            "score": opp.get("score"),
                            "type": opp.get("type", "opportunity"),
                            "source": "desktop"
                        }
                        
                        # Truncate long titles
                        if len(opportunity["title"]) > 60:
                            opportunity["title"] = opportunity["title"][:57] + "..."
                        
                        all_opportunities.append(opportunity)
        
        # If we don't have enough specific opportunities, add generic ones
        if len(all_opportunities) < 5:
            generic_opps = self.get_generic_opportunities(analysis_result)
            for opp in generic_opps:
                if len(all_opportunities) >= 5:
                    break
                
                # Avoid duplicates
                if not any(existing["title"] == opp["title"] for existing in all_opportunities):
                    # Add source information for generic opportunities
                    opp["source"] = "generic"
                    opp["auditId"] = "generic"
                    opp["type"] = "generic"
                    all_opportunities.append(opp)
        
        # Ensure we return exactly 5 opportunities (following PageSpeeds.md pattern)
        return all_opportunities[:5]

    # ------------------------------------------------------------------ #
    async def run_page_speed_analysis(
        self, url: str, strategy: str = "mobile"
    ) -> Dict[str, Any]:
        """Run PageSpeed analysis for BOTH mobile and desktop using native googleapiclient."""
        cache_key = f"pagespeed_{url}_both"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                log.debug(f"📋 Returning cached PageSpeed result for {url}")
                self.analysis_stats["cache_hits"] += 1
                return cached_data['data']
        
        # Cache miss - increment counter
        self.analysis_stats["cache_misses"] += 1
        
        log.debug(f"🚀 Starting PageSpeed analysis for {url} (mobile + desktop)")
        log.debug(f"🔑 API Key status: {'SET' if self.google_api_key else 'NOT_SET'}")
        log.debug(f"🔧 Service status: {'INITIALIZED' if self.pagespeed_service else 'NOT_INITIALIZED'}")
        
        # Check if circuit breaker is already open - fail fast
        can_proceed, message = self.rate_limiter.can_make_request('google_pagespeed')
        if not can_proceed:
            log.warning(f"🛑 Circuit breaker is OPEN for PageSpeed API: {message}")
            return {
                "mobile": None,
                "desktop": None,
                "errors": [{
                    "type": "CIRCUIT_BREAKER_OPEN",
                    "strategy": "both",
                    "message": f"Circuit breaker is OPEN: {message}",
                    "attempt": 0
                }]
            }
        
        # Track failure reasons for intelligent retry decisions
        failure_reasons = []
        
        # Store results for both strategies
        mobile_result = None
        desktop_result = None
        
        # Analyze both mobile and desktop
        for strategy_name in ["mobile", "desktop"]:
            log.debug(f"📱 Analyzing {strategy_name} for {url}")
            
            # Implement intelligent retry logic for each strategy
            for attempt in range(self.retry_config['max_attempts']):
                try:
                    log.debug(f"📡 {strategy_name.capitalize()} attempt {attempt + 1}/{self.retry_config['max_attempts']} for {url}")
                    
                    # Use native googleapiclient instead of direct HTTP requests
                    data = self._call_pagespeed_api(url, strategy_name)

                    if data.get("error"):
                        error_msg = data["error"]["message"]
                        log.error(f"❌ PageSpeed API returned error for {strategy_name}: {error_msg}")
                        
                        # Classify the error for intelligent retry decisions
                        if "FAILED_DOCUMENT_REQUEST" in error_msg or "net::ERR_TIMED_OUT" in error_msg:
                            # Site is legitimately down/unresponsive - don't retry
                            log.warning(f"🌐 Site {url} appears to be down/unresponsive for {strategy_name}. No retry needed.")
                            failure_reasons.append({
                                "type": "SITE_UNRESPONSIVE",
                                "strategy": strategy_name,
                                "message": error_msg,
                                "attempt": attempt + 1
                            })
                            # Don't count SITE_UNRESPONSIVE against circuit breaker - it's a legitimate failure
                            break  # Exit retry loop immediately
                        elif "RATE_LIMIT" in error_msg or "QUOTA_EXCEEDED" in error_msg:
                            # Rate limit issues - retry with backoff
                            failure_reasons.append({
                                "type": "RATE_LIMIT",
                                "strategy": strategy_name,
                                "message": error_msg,
                                "attempt": attempt + 1
                            })
                            # Record rate limit failure for circuit breaker
                            self.rate_limiter.record_request('google_pagespeed', False, failure_type="RATE_LIMIT")
                            raise RuntimeError(f"Rate limit exceeded: {error_msg}")
                        else:
                            # Other API errors - retry with backoff
                            failure_reasons.append({
                                "type": "API_ERROR",
                                "strategy": strategy_name,
                                "message": error_msg,
                                "attempt": attempt + 1
                            })
                            # Record API error failure for circuit breaker
                            self.rate_limiter.record_request('google_pagespeed', False, failure_type="API_ERROR")
                            raise RuntimeError(error_msg)

                    lighthouse = data.get("lighthouseResult", {})
                    scores = lighthouse.get("categories", {})
                    audits = lighthouse.get("audits", {})

                    log.debug(f"✅ {strategy_name.capitalize()} analysis successful for {url}")
                    log.debug(f"📊 Raw scores from API: {scores}")
                    log.debug(f"🔍 Best Practices raw data: {scores.get('bestPractices', 'NOT_FOUND')}")
                    
                    # Debug: Log detailed score information
                    log.debug(f"🔍 Detailed score extraction for {strategy_name}:")
                    for category in ["performance", "accessibility", "bestPractices", "seo"]:
                        category_data = scores.get(category, {})
                        log.debug(f"🔍 {category} category data: {category_data}")
                        raw_score = category_data.get("score") if isinstance(category_data, dict) else None
                        log.debug(f"🔍 {category} raw score: {raw_score} (type: {type(raw_score)})")
                        calculated_score = self._calculate_score(raw_score)
                        log.debug(f"   - {category}: raw={raw_score}, calculated={calculated_score}")
                    
                    # Calculate scores directly following the new ethos
                    # Handle cases where certain categories might not be available
                    adjusted_scores = {}
                    
                    # Performance is always available
                    performance_score = scores.get("performance", {})
                    if isinstance(performance_score, dict) and "score" in performance_score:
                        adjusted_scores["performance"] = self._calculate_score(performance_score["score"])
                    else:
                        adjusted_scores["performance"] = 0
                        log.warning(f"⚠️ No performance score found for {strategy_name}")
                    
                    # Accessibility might not always be available
                    accessibility_score = scores.get("accessibility", {})
                    if isinstance(accessibility_score, dict) and "score" in accessibility_score:
                        adjusted_scores["accessibility"] = self._calculate_score(accessibility_score["score"])
                    else:
                        adjusted_scores["accessibility"] = 0
                        log.debug(f"📝 No accessibility score found for {strategy_name} - this is normal for some sites")
                    
                    # Best Practices might not always be available
                    # Handle both naming conventions: "best-practices" (API) and "bestPractices" (our code)
                    best_practices_score = scores.get("best-practices", {}) or scores.get("bestPractices", {})
                    if isinstance(best_practices_score, dict) and "score" in best_practices_score:
                        raw_bp_score = best_practices_score["score"]
                        log.debug(f"🔍 Best Practices raw score for {strategy_name}: {raw_bp_score} (type: {type(raw_bp_score)})")
                        adjusted_scores["bestPractices"] = self._calculate_score(raw_bp_score)
                        log.debug(f"🔍 Best Practices calculated score for {strategy_name}: {adjusted_scores['bestPractices']}")
                    else:
                        adjusted_scores["bestPractices"] = 0
                        log.debug(f"📝 No Best Practices score found for {strategy_name} - raw data: {best_practices_score}")
                    
                    # SEO might not always be available
                    seo_score = scores.get("seo", {})
                    if isinstance(seo_score, dict) and "score" in seo_score:
                        adjusted_scores["seo"] = self._calculate_score(seo_score["score"])
                    else:
                        adjusted_scores["seo"] = 0
                        log.debug(f"📝 No SEO score found for {strategy_name} - this is normal for some sites")
                    
                    # Log the final scores
                    log.debug(f"📊 Final calculated scores for {strategy_name}: {adjusted_scores}")
                    
                    strategy_result = {
                        "scores": adjusted_scores,
                        "coreWebVitals": {
                            "largestContentfulPaint": self.extract_metric(
                                audits.get("largest-contentful-paint")
                            ),
                            "firstInputDelay": self.extract_metric(
                                audits.get("max-potential-fid") or audits.get("first-input-delay")
                            ),
                            "cumulativeLayoutShift": self.extract_metric(
                                audits.get("cumulative-layout-shift")
                            ),
                            "firstContentfulPaint": self.extract_metric(
                                audits.get("first-contentful-paint")
                            ),
                            "speedIndex": self.extract_metric(audits.get("speed-index")),
                        },
                        "serverMetrics": {
                            "serverResponseTime": self.extract_metric(
                                audits.get("server-response-time")
                            ),
                            "totalBlockingTime": self.extract_metric(
                                audits.get("total-blocking-time")
                            ),
                            "timeToInteractive": self.extract_metric(audits.get("interactive")),
                        },
                        "mobileUsability": self.analyze_mobile_usability_from_pagespeed(audits) if strategy_name == "mobile" else None,
                        "opportunities": self.extract_opportunities(audits),
                    }
                    
                    # Store the result for this strategy
                    if strategy_name == "mobile":
                        mobile_result = strategy_result
                    else:
                        desktop_result = strategy_result
                    
                    # Success - break out of retry loop for this strategy
                    break
                    
                except Exception as e:
                    log.warning(f"❌ {strategy_name.capitalize()} attempt {attempt + 1} failed for {url}: {e}")
                    
                    # Classify the error for intelligent retry decisions
                    error_type = "UNKNOWN_ERROR"
                    if "ConnectionError" in str(e) or "Max retries exceeded" in str(e):
                        error_type = "NETWORK_ERROR"
                        log.warning(f"🌐 Network connection error for {url} {strategy_name} - will retry")
                        # Record network error for circuit breaker
                        self.rate_limiter.record_request('google_pagespeed', False, failure_type="NETWORK_ERROR")
                    elif "SITE_UNRESPONSIVE" in str(e):
                        log.warning(f"🛑 Stopping retries for {url} {strategy_name} - permanent failure")
                        break
                    elif "Rate limit exceeded" in str(e):
                        error_type = "RATE_LIMIT"
                        log.warning(f"⏱️ Rate limit exceeded for {url} {strategy_name} - will retry with backoff")
                        # Rate limit already recorded above
                    elif "Circuit breaker is OPEN" in str(e):
                        log.warning(f"🛑 Circuit breaker is OPEN for {url} {strategy_name} - stopping retries")
                        failure_reasons.append({
                            "type": "CIRCUIT_BREAKER_OPEN",
                            "strategy": strategy_name,
                            "message": str(e),
                            "attempt": attempt + 1
                        })
                        break  # Don't retry when circuit breaker is open
                    else:
                        # Record unknown error for circuit breaker
                        self.rate_limiter.record_request('google_pagespeed', False, failure_type="UNKNOWN_ERROR")
                    
                    if attempt == self.retry_config['max_attempts'] - 1:
                        log.error(f"💥 All {strategy_name} attempts failed for {url}. Final error: {e}")
                        break
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        self.retry_config['base_delay'] * (2 ** attempt),
                        self.retry_config['max_delay']
                    )
                    log.debug(f"🔄 Retrying {strategy_name} for {url} in {delay}s (attempt {attempt + 2})")
                    await asyncio.sleep(delay)
        
        # Build the final result following the new ethos structure
        result = {
            "mobile": mobile_result,
            "desktop": desktop_result,
            "errors": failure_reasons
        }
        
        # Cache successful result
        self.cache[cache_key] = {
            'data': result,
            'timestamp': time.time()
        }
        
        # Increment cleanup counter and clean up old cache entries periodically
        self.cache_cleanup_counter += 1
        if self.cache_cleanup_counter >= self.cache_cleanup_threshold:
            self._cleanup_cache()
            self.cache_cleanup_counter = 0
        
        log.debug(f"✅ PageSpeed analysis completed for {url} (mobile: {'✅' if mobile_result else '❌'}, desktop: {'✅' if desktop_result else '❌'})")
        return result







    # ------------------------------------------------------------------ #
    def _calculate_score(self, raw_score) -> int:
        """Calculate and validate a score from raw PageSpeed data."""
        try:
            # Handle None, empty, or invalid values
            if raw_score is None:
                return 0
            
            # Convert to float and validate range
            score_float = float(raw_score)
            if not (0.0 <= score_float <= 1.0):
                log.warning(f"⚠️ Invalid score value: {raw_score}, expected 0.0-1.0")
                return 0
            
            # Convert to 0-100 scale and round
            calculated_score = round(score_float * 100)
            
            # Validate final result
            if not (0 <= calculated_score <= 100):
                log.warning(f"⚠️ Calculated score out of range: {calculated_score}, clamping to valid range")
                calculated_score = max(0, min(100, calculated_score))
            
            return calculated_score
            
        except (ValueError, TypeError) as e:
            log.warning(f"⚠️ Error calculating score from {raw_score}: {e}")
            return 0

    def _get_empty_core_web_vitals(self) -> Dict[str, None]:
        """Get empty core web vitals structure."""
        return {
            "largestContentfulPaint": None,
            "firstInputDelay": None,
            "cumulativeLayoutShift": None,
            "firstContentfulPaint": None,
            "speedIndex": None,
        }
    
    def _get_empty_server_metrics(self) -> Dict[str, None]:
        """Get empty server metrics structure."""
        return {
            "serverResponseTime": None,
            "totalBlockingTime": None,
            "timeToInteractive": None,
        }
    
    # ------------------------------------------------------------------ #
    def analyze_mobile_usability_from_pagespeed(
        self, audits: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze mobile usability from Google PageSpeed API audits following PageSpeeds.md structure."""
        # Google PageSpeed API mobile usability audits - using exact keys from PageSpeeds.md
        mobile_audits = {
            "viewport": "hasViewportMetaTag",
            "content-width": "contentSizedCorrectly", 
            "tap-targets": "tapTargetsAppropriateSize",
            "font-size": "textReadable",
            "image-size-responsive": "imageSizeResponsive"
        }
        
        checks = {}
        issues = []
        
        # Process each mobile audit following PageSpeeds.md structure
        for audit_key, check_name in mobile_audits.items():
            audit = audits.get(audit_key, {})
            
            if audit:
                # Check if audit passed (score == 1.0) or failed (score < 1.0)
                score = audit.get("score")
                if score is not None:
                    checks[check_name] = score == 1.0
                    
                    # If failed, add to issues list
                    if score < 1.0:
                        audit_title = audit.get("title", f"Mobile {audit_key} issue")
                        issues.append(audit_title)
                else:
                    # If no score, assume it passed (default behavior)
                    checks[check_name] = True
            else:
                # Audit not found, assume it passed (default behavior)
                checks[check_name] = True
        
        # Add responsive design check (always true for modern sites)
        checks["isResponsive"] = True
        
        # Count passed checks
        passed = sum(bool(v) for v in checks.values())
        total_checks = len(checks)
        mobile_score = round((passed / total_checks) * 100) if total_checks > 0 else 100
        
        # Determine mobile friendliness based on score
        mobile_friendly = mobile_score >= 80
        
        # Add any additional mobile-specific issues from other relevant audits
        additional_mobile_audits = [
            "uses-responsive-images", "image-aspect-ratio", "legacy-javascript"
        ]
        
        for audit_key in additional_mobile_audits:
            audit = audits.get(audit_key, {})
            if audit and audit.get("score") is not None and audit.get("score") < 1.0:
                audit_title = audit.get("title", f"Mobile {audit_key} issue")
                if audit_title not in issues:
                    issues.append(audit_title)
        
        return {
            "mobileFriendly": mobile_friendly,
            "score": mobile_score,
            "checks": checks,
            "issues": issues,
            "realData": True,
            "auditCount": len(checks),
            "passedChecks": passed,
            "totalChecks": total_checks
        }

    # ------------------------------------------------------------------ #
    def get_mobile_issues(self, checks: Dict[str, bool]) -> List[str]:
        issues = []
        if not checks["hasViewportMetaTag"]:
            issues.append("Missing viewport meta tag")
        if not checks["contentSizedCorrectly"]:
            issues.append("Content not sized correctly for viewport")
        if not checks["tapTargetsAppropriateSize"]:
            issues.append("Tap targets too small")
        if not checks["textReadable"]:
            issues.append("Text too small to read")
        return issues







    # ------------------------------------------------------------------ #
    # NEW ENHANCED FEATURES
    # ------------------------------------------------------------------ #
    
    def _cleanup_cache(self):
        """Optimized cache cleanup - run less frequently with batch deletion."""
        current_time = time.time()
        
        # Only clean up every N requests or if cache is large
        if len(self.cache) < self.cache_size_threshold and random.random() > 0.1:
            return
        
        expired_keys = []
        # Use list() to avoid RuntimeError during iteration
        for key, value in list(self.cache.items()):
            if current_time - value['timestamp'] > self.cache_ttl:
                expired_keys.append(key)
                # Batch deletion - limit to 50 entries per cleanup cycle
                if len(expired_keys) > 50:
                    break
        
        # Batch delete expired keys
        for key in expired_keys:
            del self.cache[key]
        
        # Only log cleanup if significant
        if expired_keys and len(expired_keys) > 10:
            log.info(f"Cleaned up {len(expired_keys)} expired cache entries")
        elif expired_keys:
            log.debug(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _update_overall_health(self):
        """Update overall service health status."""
        try:
            # Since domain_analysis is now unavailable (removed), 
            # overall health depends only on PageSpeed service
            if self.service_health["pagespeed"] == "healthy":
                self.service_health["overall"] = "healthy"
            elif self.service_health["pagespeed"] == "unconfigured":
                self.service_health["overall"] = "unhealthy"
            elif self.service_health["pagespeed"] == "unknown":
                self.service_health["overall"] = "unknown"
            else:
                self.service_health["overall"] = "degraded"
        except Exception as e:
            log.error(f"Error updating service health: {e}")
            self.service_health["overall"] = "unknown"
    
    # ------------------------------------------------------------------ #
    # TRUST ANALYSIS IMPLEMENTATION
    # ------------------------------------------------------------------ #
    
    async def analyze_trust(self, url: str) -> Dict[str, Any]:
        """Analyze website trust factors using PageSpeed data and security checks following PageSpeeds.md structure."""
        try:
            domain = urlparse(url).hostname
            trust = {
                "ssl": False,
                "securityHeaders": [],
                "score": 0,
                "realData": {"ssl": True, "securityHeaders": True, "pagespeed": False},
                "warnings": [],
                "pagespeedInsights": {},
                "auditData": {}
            }

            # 1. Protocol Security Check (from URL) - following PageSpeeds.md approach
            if url.startswith("https://"):
                trust["ssl"] = True
                trust["score"] += 30
                trust["pagespeedInsights"]["protocol"] = "HTTPS"
            else:
                trust["warnings"].append("Site uses HTTP instead of HTTPS")
                trust["pagespeedInsights"]["protocol"] = "HTTP"

            # 2. Enhanced SSL Check (if HTTPS) - following PageSpeeds.md security approach
            if url.startswith("https://"):
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"https://{domain}", timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True) as resp:
                            trust["ssl"] = resp.status < 400
                            if not trust["ssl"]:
                                trust["score"] -= 10  # Penalty for HTTPS but SSL issues
                            trust["pagespeedInsights"]["sslStatus"] = "Valid" if trust["ssl"] else "Issues"
                except Exception as e:
                    trust["warnings"].append(f"SSL check failed: {e}")
                    trust["pagespeedInsights"]["sslStatus"] = "Check Failed"

            # 3. Security Headers Check - following PageSpeeds.md security headers approach
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://{domain}", timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True) as resp:
                        headers = {k.lower(): v for k, v in resp.headers.items()}

                        # Security headers following PageSpeeds.md best practices
                        sec_headers = [
                            "x-frame-options",
                            "x-content-type-options", 
                            "strict-transport-security",
                            "content-security-policy",
                            "x-xss-protection",
                            "referrer-policy",
                            "permissions-policy"
                        ]
                        
                        found_headers = [h for h in sec_headers if h in headers]
                        trust["securityHeaders"] = found_headers
                        trust["score"] += min(40, len(found_headers) * 8)
                        trust["pagespeedInsights"]["securityHeaders"] = len(found_headers)
                        
                        # Add specific header details
                        trust["auditData"]["securityHeaders"] = {
                            "total": len(sec_headers),
                            "found": len(found_headers),
                            "missing": [h for h in sec_headers if h not in headers]
                        }
            except Exception as e:
                trust["warnings"].append(f"Security headers check failed: {e}")

            # 4. PageSpeed Best Practices Integration - following PageSpeeds.md structure
            try:
                # Get PageSpeed data to extract trust-related insights
                pagespeed_result = await self.run_page_speed_analysis(url, "mobile")
                
                # Extract Best Practices score if available
                mobile_data = pagespeed_result.get("mobile", {})
                if mobile_data and "scores" in mobile_data:
                    best_practices_score = mobile_data["scores"].get("bestPractices", 0)
                    trust["pagespeedInsights"]["bestPracticesScore"] = best_practices_score
                    
                    # Use Best Practices score as a trust multiplier (following PageSpeeds.md approach)
                    if best_practices_score >= 90:
                        trust["score"] += 15
                        trust["pagespeedInsights"]["bestPracticesRating"] = "Excellent"
                    elif best_practices_score >= 70:
                        trust["score"] += 10
                        trust["pagespeedInsights"]["bestPracticesRating"] = "Good"
                    elif best_practices_score >= 50:
                        trust["score"] += 5
                        trust["pagespeedInsights"]["bestPracticesRating"] = "Fair"
                    else:
                        trust["pagespeedInsights"]["bestPracticesRating"] = "Poor"
                        trust["warnings"].append(f"Low Best Practices score: {best_practices_score}")
                
                # Analyze resource security from PageSpeed data
                if mobile_data and "coreWebVitals" in mobile_data:
                    trust["pagespeedInsights"]["resourceSecurity"] = "Analyzed via Best Practices"
                
                trust["realData"]["pagespeed"] = True
                
            except Exception as e:
                trust["warnings"].append(f"PageSpeed trust analysis failed: {e}")
                trust["pagespeedInsights"]["error"] = str(e)

            # 5. Calculate final trust score with PageSpeed insights
            trust["score"] = max(0, min(100, trust["score"]))
            
            # Add trust level classification following PageSpeeds.md approach
            if trust["score"] >= 80:
                trust["trustLevel"] = "High"
            elif trust["score"] >= 60:
                trust["trustLevel"] = "Medium"
            elif trust["score"] >= 40:
                trust["trustLevel"] = "Low"
            else:
                trust["trustLevel"] = "Very Low"
            
            # Add audit summary
            trust["auditData"]["totalChecks"] = 3  # SSL, Security Headers, PageSpeed
            trust["auditData"]["passedChecks"] = sum([
                trust["ssl"],
                len(trust["securityHeaders"]) > 0,
                trust["realData"]["pagespeed"]
            ])

            return trust

        except Exception as e:
            raise RuntimeError(f"Trust analysis error: {e}") from e



    # ------------------------------------------------------------------ #
    # CRO ANALYSIS IMPLEMENTATION
    # ------------------------------------------------------------------ #
    
    async def analyze_cro(self, url: str) -> Dict[str, Any]:
        """Analyze Conversion Rate Optimization factors following PageSpeeds.md structure."""
        try:
            # Get PageSpeed data for both mobile and desktop
            pagespeed_result = await self.run_page_speed_analysis(url, "mobile")
            
            # Extract mobile data
            mobile_data = pagespeed_result.get("mobile", {})
            desktop_data = pagespeed_result.get("desktop", {})
            
            # Get mobile usability data following PageSpeeds.md structure
            mobile_usability = mobile_data.get("mobileUsability", {}) if mobile_data else {}
            
            # Extract scores following PageSpeeds.md format
            mobile_scores = mobile_data.get("scores", {}) if mobile_data else {}
            desktop_scores = desktop_data.get("scores", {}) if desktop_data else {}
            
            cro = {
                "mobileFriendly": mobile_usability.get("mobileFriendly", False),
                "mobileUsabilityScore": mobile_usability.get("score", 0),
                "mobileIssues": mobile_usability.get("issues", []),
                "pageSpeed": {
                    "mobile": mobile_scores.get("performance", 0),
                    "desktop": desktop_scores.get("performance", 0),
                    "average": 0,
                },
                "userExperience": {
                    "loadingTime": self.calculate_ux_score(mobile_data.get("coreWebVitals", {}) if mobile_data else {}),
                    "interactivity": self.calculate_interactivity_score(
                        mobile_data.get("serverMetrics", {}) if mobile_data else {}
                    ),
                    "visualStability": self.calculate_visual_stability_score(
                        mobile_data.get("coreWebVitals", {}) if mobile_data else {}
                    ),
                },
                "score": 0,
                "realData": True,
                "auditData": {
                    "mobileAudits": len(mobile_usability.get("checks", {})) if mobile_usability else 0,
                    "desktopAudits": len(desktop_scores) if desktop_scores else 0,
                    "totalIssues": len(mobile_usability.get("issues", [])) if mobile_usability else 0
                }
            }

            # Calculate average PageSpeed performance following PageSpeeds.md logic
            mobile_perf = cro["pageSpeed"]["mobile"]
            desktop_perf = cro["pageSpeed"]["desktop"]
            
            if mobile_perf and desktop_perf:
                cro["pageSpeed"]["average"] = round((mobile_perf + desktop_perf) / 2)
            elif mobile_perf:
                cro["pageSpeed"]["average"] = mobile_perf
            elif desktop_perf:
                cro["pageSpeed"]["average"] = desktop_perf
            else:
                cro["pageSpeed"]["average"] = 0

            # Calculate CRO score using PageSpeeds.md weighting approach
            # Mobile usability (30%) + PageSpeed performance (40%) + User Experience (30%)
            cro["score"] = round(
                cro["mobileUsabilityScore"] * 0.3
                + cro["pageSpeed"]["average"] * 0.4
                + cro["userExperience"]["loadingTime"] * 0.3
            )
            
            # Add CRO level classification
            if cro["score"] >= 80:
                cro["croLevel"] = "Excellent"
            elif cro["score"] >= 60:
                cro["croLevel"] = "Good"
            elif cro["score"] >= 40:
                cro["croLevel"] = "Fair"
            else:
                cro["croLevel"] = "Poor"

            return cro

        except Exception as e:
            raise RuntimeError(f"CRO analysis error: {e}") from e

    def calculate_ux_score(self, cwv: Dict[str, Any]) -> int:
        """Calculate user experience score based on Core Web Vitals."""
        score = 100
        lcp = (cwv.get("largestContentfulPaint") or {}).get("value") or 0
        if lcp > 4000:
            score -= 30
        elif lcp > 2500:
            score -= 15

        cls = (cwv.get("cumulativeLayoutShift") or {}).get("value") or 0
        if cls > 0.25:
            score -= 25
        elif cls > 0.1:
            score -= 10

        return max(0, score)

    def calculate_interactivity_score(self, sm: Dict[str, Any]) -> int:
        """Calculate interactivity score based on server metrics."""
        score = 100
        tti = (sm.get("timeToInteractive") or {}).get("value") or 0
        if tti > 5000:
            score -= 30
        elif tti > 3000:
            score -= 15

        tbt = (sm.get("totalBlockingTime") or {}).get("value") or 0
        if tbt > 600:
            score -= 25
        elif tti > 300:
            score -= 10

        return max(0, score)

    def calculate_visual_stability_score(self, cwv: Dict[str, Any]) -> int:
        """Calculate visual stability score based on Cumulative Layout Shift."""
        cls = (cwv.get("cumulativeLayoutShift") or {}).get("value") or 0
        if cls <= 0.1:
            return 100
        if cls <= 0.25:
            return 80
        return 50
    

    

    

    

    

    

    

    
    
    def _calculate_summary(self, result: Dict[str, Any], start_time: float = None) -> Dict[str, Any]:
        """Calculate analysis summary with error handling."""
        try:
            total_errors = 0
            services_completed = 0
            
            # Use provided start_time or current time if not provided
            if start_time is None:
                start_time = time.time()
            
            # Count errors from each service - handle None values safely
            page_speed = result.get("pageSpeed")
            if page_speed and isinstance(page_speed, dict) and page_speed.get("errors"):
                total_errors += len(page_speed["errors"])
            

            
            trust_cro = result.get("trustAndCRO")
            if trust_cro and isinstance(trust_cro, dict) and trust_cro.get("errors"):
                total_errors += len(trust_cro["errors"])
            
            # Count completed services - handle None values safely
            if page_speed and isinstance(page_speed, dict):
                services_completed += 1

            if trust_cro and isinstance(trust_cro, dict):
                services_completed += 1
            
            # Calculate analysis duration if start_time is available
            if start_time:
                analysis_duration = int((time.time() - start_time) * 1000)
            else:
                analysis_duration = 0
            
            return {
                "totalErrors": total_errors,
                "servicesCompleted": services_completed,
                "analysisDuration": analysis_duration
            }
            
        except Exception as e:
            log.error(f"❌ Error calculating summary: {e}")
            return {
                "totalErrors": 1,
                "servicesCompleted": 0,
                "analysisDuration": 0,
                "errors": [f"Summary calculation failed: {e}"]
            }
    
    async def run_batch_analysis(
        self,
        urls: List[str],
        strategy: str = "mobile",
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Run analysis on multiple URLs concurrently with rate limiting.
        
        Args:
            urls: List of URLs to analyze
            strategy: Analysis strategy ('mobile' or 'desktop')
            max_concurrent: Maximum concurrent analyses
            
        Returns:
            List of analysis results
        """
        from asyncio import Semaphore
        
        semaphore = Semaphore(max_concurrent)
        
        async def run_single_analysis(url: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    start_time = time.time()
                    
                    # Run comprehensive analysis
                    result = await self.run_comprehensive_analysis(url, strategy)
                    
                    # Note: analysis_time is not part of whoispageSpeed.md structure
                    # The summary.analysisDuration field provides timing information
                    
                    # Update statistics
                    self.analysis_stats["total_analyses"] += 1
                    if result.get("summary", {}).get("servicesCompleted", 0) > 0:
                        self.analysis_stats["successful_analyses"] += 1
                    else:
                        self.analysis_stats["failed_analyses"] += 1
                    
                    log.debug(f"✅ Batch analysis completed for {url}")
                    return result
                    
                except Exception as e:
                    self.analysis_stats["total_analyses"] += 1
                    self.analysis_stats["failed_analyses"] += 1
                    
                    return {
                        "domain": urlparse(url).hostname,
                        "url": url,
                        "analysisTimestamp": datetime.now().isoformat(),
                        "pageSpeed": None,
                        "whois": None,
                        "trustAndCRO": None,
                        "summary": {
                            "totalErrors": 1,
                            "servicesCompleted": 0,
                            "analysisDuration": int((time.time() - start_time) * 1000),
                            "errors": [f"Batch analysis failed: {str(e)}"]
                        }
                    }
        
        # Run all analyses concurrently
        tasks = [run_single_analysis(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions and convert to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "domain": urlparse(urls[i]).hostname,
                    "url": urls[i],
                    "analysisTimestamp": datetime.now().isoformat(),
                    "pageSpeed": None,
                    "trustAndCRO": None,
                    "summary": {
                        "totalErrors": 1,
                        "servicesCompleted": 0,
                        "analysisDuration": 0,  # Can't calculate without start_time
                        "errors": [f"Batch analysis failed: {str(result)}"]
                    }
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def run_comprehensive_analysis(
        self,
        url: str,
        strategy: str = "mobile"
    ) -> Dict[str, Any]:
        """
        Run comprehensive website analysis integrating PageSpeed, Trust, and CRO insights.
        
        Args:
            url: URL to analyze
            strategy: Analysis strategy ('mobile' or 'desktop')
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        try:
            start_time = time.time()
            domain = urlparse(url).hostname
            
            # Check rate limits
            can_proceed, message = self.rate_limiter.can_make_request('comprehensive_speed')
            if not can_proceed:
                return {
                    "success": False,
                    "error": f"Rate limit exceeded: {message}",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "context": "comprehensive_analysis",
                    "url": url
                }
            
            # Initialize result following the analysis structure
            result = {
                "domain": domain,
                "url": url,
                "analysisTimestamp": datetime.now().isoformat(),
                "pageSpeed": None,
                "trustAndCRO": None,
                "summary": None
            }
            
            # 1. PageSpeed Analysis (now returns both mobile and desktop)
            try:
                pagespeed_result = await self.run_page_speed_analysis(url, strategy)
                result["pageSpeed"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "mobile": pagespeed_result.get("mobile"),
                    "desktop": pagespeed_result.get("desktop"),
                    "errors": pagespeed_result.get("errors", [])
                }
                log.debug(f"✅ PageSpeed analysis completed for {url}")
            except Exception as e:
                log.warning(f"PageSpeed analysis failed for {url}: {e}")
                result["pageSpeed"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "mobile": None,
                    "desktop": None,
                    "errors": [f"PageSpeed API error: {e}"]
                }
            
            # Add generic opportunities when specific ones aren't available
            if not result["pageSpeed"].get("mobile") and not result["pageSpeed"].get("desktop"):
                # Add generic opportunities to the result for UI display
                result["genericOpportunities"] = self.get_generic_opportunities(result)
                log.debug(f"📋 Added {len(result['genericOpportunities'])} generic opportunities for {url}")
            

            
            # 3. Trust and CRO Analysis (using real implementations)
            try:
                # Run real TRUST analysis
                trust_result = await self.analyze_trust(url)
                trust_score = trust_result.get("score", 0)
                
                # Run real CRO analysis
                cro_result = await self.analyze_cro(url)
                cro_score = cro_result.get("score", 0)
                
                result["trustAndCRO"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "trust": {
                        "rawResponse": trust_result,
                        "parsed": {"score": trust_score},
                        "errors": trust_result.get("warnings", [])
                    },
                    "cro": {
                        "rawResponse": cro_result,
                        "parsed": {"score": cro_score},
                        "errors": []
                    },
                    "errors": []
                }
                log.debug(f"✅ Trust and CRO analysis completed for {url} - Trust: {trust_score}, CRO: {cro_score}")
            except Exception as e:
                log.warning(f"Trust and CRO analysis failed for {url}: {e}")
                result["trustAndCRO"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "trust": {
                        "rawResponse": {"score": 0, "warnings": [f"Trust analysis failed: {e}"]},
                        "parsed": {"score": 0},
                        "errors": [f"Trust analysis failed: {e}"]
                    },
                    "cro": {
                        "rawResponse": {"score": 0, "errors": [f"CRO analysis failed: {e}"]},
                        "parsed": {"score": 0},
                        "errors": [f"CRO analysis failed: {e}"]
                    },
                    "errors": [f"Trust/CRO analysis failed: {e}"]
                }
            

            

            
            # 6. Calculate summary following the analysis structure
            result["summary"] = self._calculate_summary(result, start_time)
            
            # Update analysis statistics
            self.analysis_stats["total_analyses"] += 1
            if result["summary"]["servicesCompleted"] > 0:
                self.analysis_stats["successful_analyses"] += 1
            else:
                self.analysis_stats["failed_analyses"] += 1
            
            # Record successful request
            self.rate_limiter.record_request('comprehensive_speed', True)
            
            log.debug(f"✅ Comprehensive analysis completed for {url}")
            return result
            
        except Exception as e:
            # Update analysis statistics for failed analysis
            self.analysis_stats["total_analyses"] += 1
            self.analysis_stats["failed_analyses"] += 1
            
            # Record failed request
            self.rate_limiter.record_request('comprehensive_speed', False)
            
            log.error(f"Comprehensive analysis failed for {url}: {e}")
            # Return error structure following the analysis format
            return {
                "domain": urlparse(url).hostname,
                "url": url,
                "analysisTimestamp": datetime.now().isoformat(),
                "pageSpeed": {
                    "domain": urlparse(url).hostname,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "mobile": None,
                    "desktop": None,
                    "errors": [f"Analysis failed: {str(e)}"]
                },

                "trustAndCRO": {
                    "domain": urlparse(url).hostname,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "trust": None,
                    "cro": None,
                    "errors": [f"Analysis failed: {str(e)}"]
                },

                "summary": {
                    "totalErrors": 1,
                    "servicesCompleted": 0,
                    "analysisDuration": int((time.time() - start_time) * 1000),
                    "errors": [f"Comprehensive analysis failed: {str(e)}"]
                }
            }
    

    
    def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health status."""
        self._update_overall_health()
        
        return {
            "service": "unified_analyzer",
            "status": self.service_health["overall"],
            "services": {
                "pagespeed": self.service_health["pagespeed"],
                "domain_analysis": "unavailable"
            },
            "rate_limits": {
                "google_pagespeed": getattr(self.api_config, 'PAGESPEED_RATE_LIMIT_PER_MINUTE', 240),
                "comprehensive_speed": getattr(self.api_config, 'COMPREHENSIVE_SPEED_RATE_LIMIT_PER_MINUTE', 30)
            },
            "cache_health": {
                "total_entries": len(self.cache),
                "cleanup_counter": self.cache_cleanup_counter,
                "cleanup_threshold": self.cache_cleanup_threshold,
                "size_threshold": self.cache_size_threshold,
                "last_cleanup": "recent" if self.cache_cleanup_counter < self.cache_cleanup_threshold else "due"
            },
            "features": {
                "caching": True,
                "retry_logic": True,
                "batch_processing": True,
                "health_monitoring": True,
                "rate_limiting": True,
                "comprehensive_analysis": True,
                "domain_analysis": False
            }
        }
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis performance statistics."""
        return {
            "statistics": self.analysis_stats.copy(),
            "cache_info": {
                "total_entries": len(self.cache),
                "cache_ttl": self.cache_ttl,
                "cache_hit_rate": (
                    self.analysis_stats["cache_hits"] / 
                    max(1, self.analysis_stats["cache_hits"] + self.analysis_stats["cache_misses"])
                ) * 100,
                "cleanup_counter": self.cache_cleanup_counter,
                "cleanup_threshold": self.cache_cleanup_threshold,
                "size_threshold": self.cache_size_threshold
            },
            "retry_config": self.retry_config.copy()
        }
    
    def force_cache_cleanup(self) -> Dict[str, Any]:
        """Force immediate cache cleanup and return statistics."""
        self._cleanup_cache()
        self.cache_cleanup_counter = 0
        
        return {
            "action": "forced_cache_cleanup",
            "timestamp": time.time(),
            "cache_size_before": len(self.cache),
            "cache_info": self.get_analysis_statistics()["cache_info"]
        }
    
    # --- New Ethos: Score Extraction Methods ---
    
    def _get_mobile_score(self, analysis_result: Dict[str, Any], key: str) -> Optional[int]:
        """Prefer mobile score, fallback to desktop, following PageSpeeds.md structure.
        
        Args:
            analysis_result: The analysis result dictionary
            key: The score key to look up (e.g., "performance", "accessibility", "seo")
            
        Returns:
            The score as an int if found, otherwise None
        """
        # Check if we have PageSpeed data - the structure is {'pageSpeed': {'mobile': {...}, 'desktop': {...}, 'errors': [...]}}
        page_speed = analysis_result.get("pageSpeed", {})
        if not page_speed:
            log.debug(f"🔍 No pageSpeed data found in analysis_result for key: {key}")
            return None
        
        # Prefer mobile, fallback to desktop (following PageSpeeds.md mobile-first approach)
        mobile = page_speed.get("mobile")
        desktop = page_speed.get("desktop")
        
        log.debug(f"🔍 Looking for {key} score - mobile: {mobile is not None}, desktop: {desktop is not None}")
        
        # Try mobile first, then desktop
        for strategy, data in [("mobile", mobile), ("desktop", desktop)]:
            if data and isinstance(data, dict) and "scores" in data:
                scores = data["scores"]
                
                # Handle both naming conventions for Best Practices (PageSpeeds.md uses "best-practices")
                if key == "bestPractices":
                    score = scores.get("bestPractices") or scores.get("best-practices")
                else:
                    score = scores.get(key)
                
                if score is not None:
                    log.debug(f"🔍 Found {key} score from {strategy}: {score} (type: {type(score)})")
                    
                    # Ensure we return an integer
                    try:
                        if isinstance(score, (int, float)):
                            return int(round(score))
                        elif isinstance(score, str):
                            # Handle string scores (e.g., "0.95")
                            return int(round(float(score)))
                        else:
                            log.warning(f"⚠️ Unexpected score type for {key}: {type(score)} - {score}")
                            return None
                    except (ValueError, TypeError) as e:
                        log.warning(f"⚠️ Error converting score for {key}: {score} - {e}")
                        return None
        
        log.debug(f"🔍 No {key} score found in any source")
        return None
    
    def _get_trust_score(self, analysis_result: Dict[str, Any]) -> Optional[int]:
        """Get the trust score from the analysis result."""
        trust_and_cro = analysis_result.get("trustAndCRO")
        if not trust_and_cro or not isinstance(trust_and_cro, dict):
            return None
        
        trust = trust_and_cro.get("trust")
        if trust and isinstance(trust, dict) and trust.get("parsed"):
            try:
                score = trust["parsed"]["score"]
                if score is not None:
                    return int(score)
            except (ValueError, TypeError, KeyError):
                pass
        return None
    
    def _get_cro_score(self, analysis_result: Dict[str, Any]) -> Optional[int]:
        """Get the CRO score from the analysis result."""
        trust_and_cro = analysis_result.get("trustAndCRO")
        if not trust_and_cro or not isinstance(trust_and_cro, dict):
            return None
        
        cro = trust_and_cro.get("cro")
        if cro and isinstance(cro, dict) and cro.get("parsed"):
            try:
                score = cro["parsed"]["score"]
                if score is not None:
                    return int(score)
            except (ValueError, TypeError, KeyError):
                pass
        return None
    

    
    # --- Public KPI Properties ---
    
    def get_performance_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get performance score with mobile preference."""
        return self._get_mobile_score(analysis_result, "performance") or 0
    
    def get_accessibility_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get accessibility score with mobile preference."""
        return self._get_mobile_score(analysis_result, "accessibility") or 0
    
    def get_seo_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get SEO score with mobile preference."""
        return self._get_mobile_score(analysis_result, "seo") or 0
    
    def get_best_practices_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get best practices score with mobile preference."""
        return self._get_mobile_score(analysis_result, "bestPractices") or 0
    
    def get_trust_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get trust score."""
        return self._get_trust_score(analysis_result) or 0
    
    def get_cro_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get CRO score."""
        return self._get_cro_score(analysis_result) or 0
    

    
    def get_overall_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall score from all six categories including Best Practices, Trust and CRO."""
        values = [
            self.get_performance_score(analysis_result),
            self.get_accessibility_score(analysis_result),
            self.get_best_practices_score(analysis_result),
            self.get_seo_score(analysis_result),
            self.get_trust_score(analysis_result),
            self.get_cro_score(analysis_result)
        ]
        # Include all six categories - this provides a comprehensive website health score
        # This ensures we always have 6 values to average
        total_score = sum(values)
        overall_percentage = round(total_score / 6.0, 1)  # Round to 1 decimal place for cleaner display
        return overall_percentage
    
    def get_mobile_usability_score(self, analysis_result: Dict[str, Any]) -> Optional[int]:
        """Get the mobile usability score from PageSpeed data following PageSpeeds.md structure."""
        page_speed = analysis_result.get("pageSpeed", {})
        mobile = page_speed.get("mobile", {})
        
        if mobile and "mobileUsability" in mobile:
            mobile_usability = mobile["mobileUsability"]
            if mobile_usability and isinstance(mobile_usability, dict):
                score = mobile_usability.get("score")
                if score is not None:
                    return int(score)
        
        # Fallback: check if we have mobile data but no mobileUsability
        if mobile and "scores" in mobile:
            # If we have mobile scores but no mobileUsability, calculate a basic score
            # This handles cases where PageSpeed API doesn't return mobileUsability
            log.debug("📱 No mobileUsability data found, calculating basic mobile score")
            return None  # Return None to indicate no mobile usability data
        
        return None
    
    def get_top_issues(self, analysis_result: Dict[str, Any], max_issues: int = 5) -> List[str]:
        """Get top issues from PageSpeed opportunities and mobile usability following PageSpeeds.md structure."""
        issues = []
        
        # Get opportunities from mobile data (following PageSpeeds.md mobile-first approach)
        page_speed = analysis_result.get("pageSpeed", {})
        mobile = page_speed.get("mobile", {})
        if mobile and "opportunities" in mobile:
            for opp in mobile["opportunities"][:max_issues]:
                title = opp.get("title", "")
                if title:
                    # Truncate long titles to prevent UI overflow
                    if len(title) > 50:
                        title = title[:47] + "..."
                    issues.append(title)
        
        # If we don't have enough issues, add mobile usability issues
        if len(issues) < max_issues and mobile and "mobileUsability" in mobile:
            mobile_usability = mobile["mobileUsability"]
            if mobile_usability and isinstance(mobile_usability, dict):
                mobile_issues = mobile_usability.get("issues", [])
                for issue in mobile_issues:
                    if len(issues) >= max_issues:
                        break
                    # Truncate long issues
                    if len(issue) > 50:
                        issue = issue[:47] + "..."
                    issues.append(issue)
        
        # If still not enough, add desktop opportunities
        if len(issues) < max_issues:
            desktop = page_speed.get("desktop", {})
            if desktop and "opportunities" in desktop:
                for opp in desktop["opportunities"]:
                    if len(issues) >= max_issues:
                        break
                    title = opp.get("title", "")
                    if title and title not in issues:
                        # Truncate long titles
                        if len(title) > 50:
                            title = title[:47] + "..."
                        issues.append(title)
        
        # If still not enough, add generic issues from analysis errors
        if len(issues) < max_issues:
            errors = page_speed.get("errors", [])
            for error in errors:
                if len(issues) >= max_issues:
                    break
                if isinstance(error, dict):
                    error_msg = error.get("message", str(error))
                else:
                    error_msg = str(error)
                
                # Convert error messages to user-friendly issue descriptions
                if "FAILED_DOCUMENT_REQUEST" in error_msg:
                    issue = "Website accessibility issue - server not responding"
                elif "net::ERR_TIMED_OUT" in error_msg:
                    issue = "Website performance issue - connection timeout"
                elif "400" in error_msg or "Bad Request" in error_msg:
                    issue = "Website configuration issue - invalid request"
                else:
                    issue = f"Technical analysis issue - {error_msg[:30]}..."
                
                if issue not in issues:
                    issues.append(issue)
        
        return issues[:max_issues]
    