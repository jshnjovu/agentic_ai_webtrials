"""
Unified Website Analyzer (Python back-port of unified.js)
Enhanced with caching, retry logic, batch processing, health monitoring, and rate limiting
"""

import logging
import math
import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlparse
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime

import requests

from .domain_analysis import DomainAnalysisService
from ..core.config import get_api_config
from ..services.rate_limiter import RateLimiter

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("unified")


class UnifiedAnalyzer:
    def __init__(self) -> None:
        self.pagespeed_base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.api_config = get_api_config()
        self.google_api_key = self.api_config.GOOGLE_GENERAL_API_KEY
        
        # 1. Caching System
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
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

        try:
            self.domain_service = DomainAnalysisService()
            self.service_health["domain_analysis"] = "healthy"
        except Exception as e:
            log.warning("⚠️ Domain Analysis Service not available: %s", e)
            self.domain_service = None
            self.service_health["domain_analysis"] = "unhealthy"
        
        # Check PageSpeed API key
        if self.google_api_key:
            self.service_health["pagespeed"] = "healthy"
            log.info(f"✅ PageSpeed API key configured: {self.google_api_key[:10]}...")
        else:
            self.service_health["pagespeed"] = "unconfigured"
            log.error(f"❌ PageSpeed API key NOT configured - this will cause failures!")
        
        # Log configuration summary
        log.info(f"🔧 UnifiedAnalyzer initialized with:")
        log.info(f"   - PageSpeed API Key: {'SET' if self.google_api_key else 'NOT_SET'}")
        log.info(f"   - Cache TTL: {self.cache_ttl}s")
        log.info(f"   - Retry attempts: {self.retry_config['max_attempts']}")
        log.info(f"   - Rate limiter: {'enabled' if self.rate_limiter else 'disabled'}")
        
        self._update_overall_health()

    # ------------------------------------------------------------------ #
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def make_request(self, url: str, **kwargs) -> Dict[str, Any]:
        """Enhanced request method with retry logic and rate limiting."""
        try:
            log.info(f"🌐 Making HTTP request to: {url[:100]}...")
            
            # Check rate limits - use google_pagespeed since this is for PageSpeed API calls
            can_proceed, message = self.rate_limiter.can_make_request('google_pagespeed')
            if not can_proceed:
                log.warning(f"⚠️ Rate limit exceeded: {message}")
                raise RuntimeError(f"Rate limit exceeded: {message}")
            
            log.info(f"📡 Sending request...")
            resp = requests.get(url, **kwargs)
            
            log.info(f"📊 Response status: {resp.status_code} {resp.reason}")
            log.info(f"📋 Response headers: {dict(resp.headers)}")
            
            resp.raise_for_status()
            
            # Record successful request
            self.rate_limiter.record_request('google_pagespeed', True)
            log.info(f"✅ Request successful, parsing JSON response...")
            
            return resp.json()
            
        except requests.HTTPError as e:
            # Record failed request
            self.rate_limiter.record_request('google_pagespeed', False)
            
            log.error(f"❌ HTTP request failed: {e.response.status_code} {e.response.reason}")
            log.error(f"🔍 Response headers: {dict(e.response.headers)}")
            log.error(f"📋 Response body: {e.response.text[:500]}...")
            
            raise RuntimeError(
                f"Request failed with status {e.response.status_code}: {e.response.reason}"
            ) from e
            
        except Exception as e:
            # Record failed request
            self.rate_limiter.record_request('google_pagespeed', False)
            
            log.error(f"❌ Request failed with exception: {type(e).__name__}: {e}")
            log.error(f"🔍 Exception details: {str(e)}")
            
            raise RuntimeError(f"Request failed: {e}") from e

    # ------------------------------------------------------------------ #
    def extract_metric(self, metric: Dict[str, Any]) -> Dict[str, Any] | None:
        """Extract metric data with safe fallbacks."""
        if not metric:
            return None
        return {
            "value": metric.get("numericValue"),
            "displayValue": metric.get("displayValue"),
            "unit": metric.get("numericUnit", ""),
        }
    

    


    # ------------------------------------------------------------------ #
    def extract_opportunities(self, audits: Dict[str, Any]) -> List[Dict[str, Any]]:
        opportunities = []
        for key, audit in audits.items():
            if audit.get("details", {}).get("type") == "opportunity" and audit.get(
                "numericValue", 0
            ) > 0:
                opportunities.append(
                    {
                        "title": audit["title"],
                        "description": audit["description"],
                        "potentialSavings": round(audit["numericValue"]),
                        "unit": audit.get("numericUnit", "ms"),
                    }
                )
        return opportunities[:3]

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
        
        # Check if WHOIS analysis failed
        whois = analysis_result.get("whois", {})
        if whois and whois.get("errors") and len(whois["errors"]) > 0:
            generic_opportunities.append({
                "title": "Domain Information Unavailable",
                "description": "Unable to retrieve domain registration information, which may affect trust and credibility assessment.",
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
        This ensures the UI always has meaningful improvement suggestions to display.
        """
        all_opportunities = []
        
        # First, try to get specific PageSpeed opportunities
        page_speed = analysis_result.get("pageSpeed", {})
        if page_speed:
            # Check mobile opportunities first
            mobile = page_speed.get("mobile")
            if mobile and mobile.get("opportunities"):
                all_opportunities.extend(mobile["opportunities"])
            
            # Add desktop opportunities if we don't have enough
            if len(all_opportunities) < 3:
                desktop = page_speed.get("desktop")
                if desktop and desktop.get("opportunities"):
                    for opp in desktop["opportunities"]:
                        if len(all_opportunities) >= 3:
                            break
                        # Avoid duplicates by checking title
                        if not any(existing["title"] == opp["title"] for existing in all_opportunities):
                            all_opportunities.append(opp)
        
        # If we don't have enough specific opportunities, add generic ones
        if len(all_opportunities) < 3:
            generic_opps = self.get_generic_opportunities(analysis_result)
            for opp in generic_opps:
                if len(all_opportunities) >= 3:
                    break
                # Avoid duplicates
                if not any(existing["title"] == opp["title"] for existing in all_opportunities):
                    all_opportunities.append(opp)
        
        # Ensure we return exactly 3 opportunities
        return all_opportunities[:3]

    # ------------------------------------------------------------------ #
    async def run_page_speed_analysis(
        self, url: str, strategy: str = "mobile"
    ) -> Dict[str, Any]:
        """Run PageSpeed analysis for BOTH mobile and desktop following the new ethos."""
        cache_key = f"pagespeed_{url}_both"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                log.info(f"📋 Returning cached PageSpeed result for {url}")
                self.analysis_stats["cache_hits"] += 1
                return cached_data['data']
        
        # Cache miss - increment counter
        self.analysis_stats["cache_misses"] += 1
        
        log.info(f"🚀 Starting PageSpeed analysis for {url} (mobile + desktop)")
        log.info(f"🔑 API Key status: {'SET' if self.google_api_key else 'NOT_SET'}")
        
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
            log.info(f"📱 Analyzing {strategy_name} for {url}")
            
            # Implement intelligent retry logic for each strategy
            for attempt in range(self.retry_config['max_attempts']):
                try:
                    log.info(f"📡 {strategy_name.capitalize()} attempt {attempt + 1}/{self.retry_config['max_attempts']} for {url}")
                    
                    categories = ["performance", "accessibility", "best-practices", "seo"]
                    category_params = "&".join([f"category={c}" for c in categories])
                    api_url = (
                        f"{self.pagespeed_base_url}?url={url}&strategy={strategy_name}"
                        f"&{category_params}&prettyPrint=true&key={self.google_api_key}"
                    )
                    
                    log.info(f"🌐 Calling PageSpeed API for {strategy_name}: {api_url[:100]}...")

                    data = await self.make_request(api_url)

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

                    log.info(f"✅ {strategy_name.capitalize()} analysis successful for {url}")
                    log.info(f"📊 Raw scores from API: {scores}")
                    
                    # Calculate scores directly following the new ethos
                    adjusted_scores = {
                        "performance": self._calculate_score(scores.get("performance", {}).get("score", 0)),
                        "accessibility": self._calculate_score(scores.get("accessibility", {}).get("score", 0)),
                        "seo": self._calculate_score(scores.get("seo", {}).get("score", 0)),
                    }
                    
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
                    log.info(f"🔄 Retrying {strategy_name} for {url} in {delay}s (attempt {attempt + 2})")
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
        
        # Clean up old cache entries
        self._cleanup_cache()
        
        log.info(f"✅ PageSpeed analysis completed for {url} (mobile: {'✅' if mobile_result else '❌'}, desktop: {'✅' if desktop_result else '❌'})")
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
        checks = {
            "hasViewportMetaTag": (audits.get("viewport") or {}).get("score") == 1,
            "contentSizedCorrectly": (audits.get("content-width") or {}).get("score")
            == 1,
            "tapTargetsAppropriateSize": (audits.get("tap-targets") or {}).get("score")
            == 1,
            "textReadable": (audits.get("font-size") or {}).get("score") == 1,
            "isResponsive": True,
        }

        passed = sum(bool(v) for v in checks.values())
        mobile_score = round((passed / len(checks)) * 100)

        return {
            "mobileFriendly": mobile_score >= 80,
            "score": mobile_score,
            "checks": checks,
            "issues": self.get_mobile_issues(checks),
            "realData": True,
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
        """Clean up expired cache entries."""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value['timestamp'] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            log.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    def _update_overall_health(self):
        """Update overall service health status."""
        try:
            if (self.service_health["pagespeed"] == "healthy" and 
                self.service_health["domain_analysis"] == "healthy"):
                self.service_health["overall"] = "healthy"
            elif (self.service_health["pagespeed"] == "healthy" or 
                  self.service_health["domain_analysis"] == "healthy"):
                self.service_health["overall"] = "degraded"
            elif (self.service_health["pagespeed"] == "unknown" and 
                  self.service_health["domain_analysis"] == "unknown"):
                self.service_health["overall"] = "unknown"
            else:
                self.service_health["overall"] = "unhealthy"
        except Exception as e:
            log.error(f"Error updating service health: {e}")
            self.service_health["overall"] = "unknown"
    

    

    

    

    
    async def _get_whois_data(self, url: str) -> Dict[str, Any]:
        """Get WHOIS data using existing domain analysis service."""
        try:
            domain = urlparse(url).hostname
            
            if not self.domain_service:
                return {
                    "domain": domain,
                    "timestamp": datetime.now().isoformat(),
                    "whois": None,
                    "whoisHistory": None,
                    "domainAge": None,
                    "credibility": None,
                    "errors": ["Domain analysis service not available"]
                }
            
            # Use existing domain analysis service
            domain_analysis = await self.domain_service.analyze_domain(domain)
            
            return {
                "domain": domain,
                "timestamp": datetime.now().isoformat(),
                "whois": {
                    "rawResponse": domain_analysis["whois"],
                    "parsed": domain_analysis["whois"]
                },
                "whoisHistory": {
                    "rawResponse": domain_analysis["whoisHistory"],
                    "parsed": domain_analysis["whoisHistory"]
                },
                "domainAge": domain_analysis["domainAge"],
                "credibility": domain_analysis["analysis"]["credibility"],
                "errors": []
            }
            
        except Exception as e:
            log.error(f"❌ WHOIS data retrieval failed for {url}: {e}")
            return {
                "domain": urlparse(url).hostname,
                "timestamp": datetime.now().isoformat(),
                "whois": None,
                "whoisHistory": None,
                "domainAge": None,
                "credibility": None,
                "errors": [f"WHOIS lookup failed: {e}"]
            }
    
    
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
            
            whois = result.get("whois")
            if whois and isinstance(whois, dict) and whois.get("errors"):
                total_errors += len(whois["errors"])
            
            trust_cro = result.get("trustAndCRO")
            if trust_cro and isinstance(trust_cro, dict) and trust_cro.get("errors"):
                total_errors += len(trust_cro["errors"])
            
            # Count completed services - handle None values safely
            if page_speed and isinstance(page_speed, dict):
                services_completed += 1
            if whois and isinstance(whois, dict):
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
                    "whois": None,
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
        Run comprehensive website analysis following the data structure from whoispageSpeed.md
        and integrating domain analysis insights without replacing existing working systems.
        
        Args:
            url: URL to analyze
            strategy: Analysis strategy ('mobile' or 'desktop')
            
        Returns:
            Dictionary with comprehensive analysis results matching whoispageSpeed.md structure
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
            
            # Initialize result following whoispageSpeed.md structure
            result = {
                "domain": domain,
                "url": url,
                "analysisTimestamp": datetime.now().isoformat(),
                "pageSpeed": None,
                "whois": None,
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
                log.info(f"✅ PageSpeed analysis completed for {url}")
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
                log.info(f"📋 Added {len(result['genericOpportunities'])} generic opportunities for {url}")
            
            # 2. WHOIS Analysis (use domain_analysis.py)
            try:
                whois_result = await self._get_whois_data(url)
                result["whois"] = whois_result
                log.info(f"✅ WHOIS analysis completed for {url}")
            except Exception as e:
                log.warning(f"WHOIS analysis failed for {url}: {e}")
                result["whois"] = {
                    "domain": domain,
                    "timestamp": datetime.now().isoformat(),
                    "whois": None,
                    "whoisHistory": None,
                    "domainAge": None,
                    "credibility": None,
                    "errors": [f"WHOIS lookup failed: {e}"]
                }
            
            # 3. Trust and CRO Analysis (implemented using available data)
            try:
                # Calculate Trust score based on domain credibility and WHOIS data
                trust_score = 0
                if result.get("whois") and result["whois"].get("credibility"):
                    trust_score = min(100, result["whois"]["credibility"])
                elif result.get("whois") and result["whois"].get("whois"):
                    # Fallback: basic trust scoring based on WHOIS data
                    whois_data = result["whois"]["whois"]
                    if whois_data and isinstance(whois_data, dict):
                        # Score based on registration status, registrar, etc.
                        if whois_data.get("status") and "expired" not in str(whois_data["status"]).lower():
                            trust_score += 30
                        if whois_data.get("registrar") and whois_data["registrar"] != "Unknown":
                            trust_score += 20
                        if whois_data.get("nameServers") and len(whois_data["nameServers"]) >= 2:
                            trust_score += 25
                        if result.get("whois", {}).get("domainAge", {}).get("years", 0) >= 2:
                            trust_score += 25
                
                # Calculate CRO score based on PageSpeed performance and accessibility
                cro_score = 0
                if result.get("pageSpeed", {}).get("mobile"):
                    mobile = result["pageSpeed"]["mobile"]
                    if mobile and "scores" in mobile:
                        scores = mobile["scores"]
                        # CRO score based on performance, accessibility, and SEO
                        performance = scores.get("performance", 0)
                        accessibility = scores.get("accessibility", 0)
                        seo = scores.get("seo", 0)
                        
                        # Weighted average: Performance (40%), Accessibility (30%), SEO (30%)
                        if performance is not None and accessibility is not None and seo is not None:
                            cro_score = int((performance * 0.4) + (accessibility * 0.3) + (seo * 0.3))
                
                result["trustAndCRO"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                "trust": {
                        "rawResponse": {"score": trust_score},
                        "parsed": {"score": trust_score},
                        "errors": []
                },
                "cro": {
                        "rawResponse": {"score": cro_score},
                        "parsed": {"score": cro_score},
                        "errors": []
                    },
                    "errors": []
                }
                log.info(f"✅ Trust and CRO analysis completed for {url} - Trust: {trust_score}, CRO: {cro_score}")
            except Exception as e:
                log.warning(f"Trust and CRO analysis failed for {url}: {e}")
                result["trustAndCRO"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "trust": {
                        "rawResponse": {"score": 0},
                        "parsed": {"score": 0},
                        "errors": [f"Trust analysis failed: {e}"]
                    },
                    "cro": {
                        "rawResponse": {"score": 0},
                        "parsed": {"score": 0},
                        "errors": [f"CRO analysis failed: {e}"]
                    },
                    "errors": [f"Trust/CRO analysis failed: {e}"]
            }
            

            
            # 5. Domain insights integration (simplified)
            try:
                if self.domain_service:
                    domain_analysis = await self.domain_service.analyze_domain(domain)
                    result["domainInsights"] = {
                        "businessMaturity": {
                            "isEstablished": domain_analysis["analysis"]["isEstablished"],
                            "isVeteran": domain_analysis["analysis"]["isVeteran"],
                            "ageCategory": domain_analysis["domainAge"]["ageDescription"],
                            "yearsInBusiness": domain_analysis["domainAge"]["years"],
                            "totalDays": domain_analysis["domainAge"]["totalDays"]
                        },
                        "credibility": {
                            "score": domain_analysis["analysis"]["credibility"],
                            "registrar": domain_analysis["whois"]["registrar"],
                            "registrationStatus": domain_analysis["whois"]["status"],
                            "nameServerCount": len(domain_analysis["whois"]["nameServers"]),
                            "whoisHistoryRecords": domain_analysis["whoisHistory"]["totalRecords"] if domain_analysis["whoisHistory"] else 0
                        }
                    }
                    log.info(f"✅ Domain insights integration completed for {url}")
            except Exception as e:
                log.warning(f"Domain insights integration failed for {url}: {e}")
            
            # 6. Calculate summary following whoispageSpeed.md structure
            result["summary"] = self._calculate_summary(result, start_time)
            
            # Update analysis statistics
            self.analysis_stats["total_analyses"] += 1
            if result["summary"]["servicesCompleted"] > 0:
                self.analysis_stats["successful_analyses"] += 1
            else:
                self.analysis_stats["failed_analyses"] += 1
            
            # Record successful request
            self.rate_limiter.record_request('comprehensive_speed', True)
            
            log.info(f"✅ Comprehensive analysis completed for {url}")
            return result
            
        except Exception as e:
            # Update analysis statistics for failed analysis
            self.analysis_stats["total_analyses"] += 1
            self.analysis_stats["failed_analyses"] += 1
            
            # Record failed request
            self.rate_limiter.record_request('comprehensive_speed', False)
            
            log.error(f"Comprehensive analysis failed for {url}: {e}")
            # Return error structure following whoispageSpeed.md format
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
                "whois": {
                    "domain": urlparse(url).hostname,
                    "timestamp": datetime.now().isoformat(),
                    "whois": None,
                    "whoisHistory": None,
                    "domainAge": None,
                    "credibility": None,
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
                "domain_analysis": self.service_health["domain_analysis"]
            },
            "rate_limits": {
                "google_pagespeed": getattr(self.api_config, 'PAGESPEED_RATE_LIMIT_PER_MINUTE', 240),
                "comprehensive_speed": getattr(self.api_config, 'COMPREHENSIVE_SPEED_RATE_LIMIT_PER_MINUTE', 30)
            },
            "features": {
                "caching": True,
                "retry_logic": True,
                "batch_processing": True,
                "health_monitoring": True,
                "rate_limiting": True,
                "comprehensive_analysis": True
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
                ) * 100
            },
            "retry_config": self.retry_config.copy()
        }
    
    # --- New Ethos: Score Extraction Methods ---
    
    def _get_mobile_score(self, analysis_result: Dict[str, Any], key: str) -> Optional[int]:
        """Prefer mobile score, fallback to desktop.
        
        Args:
            analysis_result: The analysis result dictionary
            key: The score key to look up (e.g., "performance", "accessibility", "seo")
            
        Returns:
            The score as an int if found, otherwise None
        """
        # Check if we have PageSpeed data
        if "pageSpeed" not in analysis_result:
            return None
        
        # Prefer mobile, fallback to desktop
        mobile = analysis_result["pageSpeed"].get("mobile")
        desktop = analysis_result["pageSpeed"].get("desktop")
        
        for src in (mobile, desktop):
            if src and "scores" in src and key in src["scores"]:
                score = src["scores"][key]
                if score is not None:
                    return int(score)
        
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
        """Get best practices score with mobile preference (legacy support)."""
        # Note: bestPractices is deprecated, use trust and cro scores instead
        return 0  # Return 0 since bestPractices is no longer part of the new KPI structure
    
    def get_trust_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get trust score."""
        return self._get_trust_score(analysis_result) or 0
    
    def get_cro_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get CRO score."""
        return self._get_cro_score(analysis_result) or 0
    

    
    def get_overall_score(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall score from all five categories including Trust and CRO as real zeros."""
        values = [
            self.get_performance_score(analysis_result),
            self.get_accessibility_score(analysis_result),
            self.get_seo_score(analysis_result),
            self.get_trust_score(analysis_result),
            self.get_cro_score(analysis_result)
        ]
        # Include all five categories - Trust and CRO are treated as real zeros, not excluded
        # This ensures we always have 5 values to average
        total_score = sum(values)
        return round(total_score / 5.0, 2)
    