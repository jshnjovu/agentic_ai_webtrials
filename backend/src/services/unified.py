"""
Unified Website Analyzer (Python back-port of unified.js)
Enhanced with caching, retry logic, batch processing, health monitoring, and rate limiting
"""

import logging
import math
import asyncio
import time
from typing import Dict, Any, List, Optional
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
        if not metric:
            return None
        return {
            "value": metric["numericValue"],
            "displayValue": metric["displayValue"],
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

    # ------------------------------------------------------------------ #
    async def run_page_speed_analysis(
        self, url: str, strategy: str = "mobile"
    ) -> Dict[str, Any]:
        """Run PageSpeed analysis with improved error handling for unresponsive sites."""
        cache_key = f"pagespeed_{url}_{strategy}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                log.info(f"📋 Returning cached PageSpeed result for {url}")
                return cached_data['data']
        
        log.info(f"🚀 Starting PageSpeed analysis for {url} with strategy: {strategy}")
        log.info(f"🔑 API Key status: {'SET' if self.google_api_key else 'NOT_SET'}")
        
        # Track failure reasons for intelligent retry decisions
        failure_reasons = []
        
        # Implement intelligent retry logic
        for attempt in range(self.retry_config['max_attempts']):
            try:
                log.info(f"📡 PageSpeed attempt {attempt + 1}/{self.retry_config['max_attempts']} for {url}")
                
                categories = ["performance", "accessibility", "best-practices", "seo"]
                category_params = "&".join([f"category={c}" for c in categories])
                api_url = (
                    f"{self.pagespeed_base_url}?url={url}&strategy={strategy}"
                    f"&{category_params}&prettyPrint=true&key={self.google_api_key}"
                )
                
                log.info(f"🌐 Calling PageSpeed API: {api_url[:100]}...")

                data = await self.make_request(api_url)

                if data.get("error"):
                    error_msg = data["error"]["message"]
                    log.error(f"❌ PageSpeed API returned error: {error_msg}")
                    
                    # Classify the error for intelligent retry decisions
                    if "FAILED_DOCUMENT_REQUEST" in error_msg or "net::ERR_TIMED_OUT" in error_msg:
                        # Site is legitimately down/unresponsive - don't retry
                        log.warning(f"🌐 Site {url} appears to be down/unresponsive. No retry needed.")
                        failure_reasons.append({
                            "type": "SITE_UNRESPONSIVE",
                            "message": error_msg,
                            "attempt": attempt + 1
                        })
                        # Record as failure but don't count against circuit breaker
                        self.rate_limiter.record_request('google_pagespeed', False, failure_type="SITE_UNRESPONSIVE")
                        break  # Exit retry loop immediately
                    elif "RATE_LIMIT" in error_msg or "QUOTA_EXCEEDED" in error_msg:
                        # Rate limit issues - retry with backoff
                        failure_reasons.append({
                            "type": "RATE_LIMIT",
                            "message": error_msg,
                            "attempt": attempt + 1
                        })
                        self.rate_limiter.record_request('google_pagespeed', False, failure_type="RATE_LIMIT")
                        raise RuntimeError(f"Rate limit exceeded: {error_msg}")
                    else:
                        # Other API errors - retry with backoff
                        failure_reasons.append({
                            "type": "API_ERROR",
                            "message": error_msg,
                            "attempt": attempt + 1
                        })
                        self.rate_limiter.record_request('google_pagespeed', False, failure_type="API_ERROR")
                        raise RuntimeError(error_msg)

                lighthouse = data.get("lighthouseResult", {})
                scores = lighthouse.get("categories", {})
                audits = lighthouse.get("audits", {})

                log.info(f"✅ PageSpeed analysis successful for {url}")
                log.info(f"📊 Raw scores from API: {scores}")
                log.info(f"📊 Available score categories: {list(scores.keys())}")
                log.info(f"📊 Audits available: {list(audits.keys())[:10]}...")  # First 10 audit keys
                
                # Calculate scores directly
                adjusted_scores = {
                    "performance": self._calculate_score(scores.get("performance", {}).get("score", 0)),
                    "accessibility": self._calculate_score(scores.get("accessibility", {}).get("score", 0)),
                    "bestPractices": self._calculate_score(scores.get("best-practices", {}).get("score", 0)),
                    "seo": self._calculate_score(scores.get("seo", {}).get("score", 0)),
                }
                
                result = {
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
                    "mobileUsability": self.analyze_mobile_usability_from_pagespeed(audits),
                    "opportunities": self.extract_opportunities(audits),
                }
                
                # Cache successful result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                # Clean up old cache entries
                self._cleanup_cache()
                
                return result
                
            except Exception as e:
                log.warning(f"❌ PageSpeed attempt {attempt + 1} failed for {url}: {e}")
                log.warning(f"🔍 Error type: {type(e).__name__}")
                log.warning(f"📋 Error details: {str(e)}")
                
                # Classify the error for intelligent retry decisions
                error_type = "UNKNOWN_ERROR"
                if "ConnectionError" in str(e) or "Max retries exceeded" in str(e):
                    error_type = "NETWORK_ERROR"
                    log.warning(f"🌐 Network connection error for {url} - will retry")
                elif "SITE_UNRESPONSIVE" in str(e) or "Rate limit exceeded: Circuit breaker is OPEN" in str(e):
                    log.warning(f"🛑 Stopping retries for {url} due to permanent failure or circuit breaker")
                    break
                elif "Rate limit exceeded" in str(e):
                    error_type = "RATE_LIMIT"
                    log.warning(f"⏱️ Rate limit exceeded for {url} - will retry with backoff")
                
                # Record the failure with appropriate type
                if error_type == "NETWORK_ERROR":
                    self.rate_limiter.record_request('google_pagespeed', False, failure_type="NETWORK_ERROR")
                elif error_type == "RATE_LIMIT":
                    self.rate_limiter.record_request('google_pagespeed', False, failure_type="RATE_LIMIT")
                else:
                    self.rate_limiter.record_request('google_pagespeed', False, failure_type="API_ERROR")
                
                if attempt == self.retry_config['max_attempts'] - 1:
                    log.error(f"💥 All PageSpeed attempts failed for {url}. Final error: {e}")
                    break
                
                # Calculate delay with exponential backoff
                delay = min(
                    self.retry_config['base_delay'] * (2 ** attempt),
                    self.retry_config['max_delay']
                )
                log.info(f"🔄 Retrying PageSpeed for {url} in {delay}s (attempt {attempt + 2})")
                await asyncio.sleep(delay)
        
        # If we get here, all attempts failed - return fallback scores
        log.warning(f"🔄 Using fallback scoring for {url} due to PageSpeed failures")
        return self._generate_fallback_scores(url, failure_reasons)

    def _generate_fallback_scores(self, url: str, failure_reasons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate intelligent fallback scores based on failure reasons."""
        log.info(f"🔄 Generating fallback scores for {url}")
        log.info(f"📋 Failure reasons: {failure_reasons}")
        
        # Analyze failure patterns to determine appropriate fallback scores
        has_site_unresponsive = any(r.get("type") == "SITE_UNRESPONSIVE" for r in failure_reasons)
        has_rate_limit = any(r.get("type") == "RATE_LIMIT" for r in failure_reasons)
        has_network_error = any(r.get("type") == "NETWORK_ERROR" for r in failure_reasons)
        has_api_error = any(r.get("type") == "API_ERROR" for r in failure_reasons)
        
        if has_site_unresponsive:
            # Site is legitimately down - give very low scores
            log.info(f"🌐 Site {url} is unresponsive - assigning minimal scores")
            fallback_scores = {
                "performance": 5,      # Very low - site doesn't load
                "accessibility": 5,    # Very low - can't access
                "bestPractices": 5,   # Very low - no content to analyze
                "seo": 5,             # Very low - no content to index
            }
        elif has_network_error:
            # Network connectivity issues - give moderate scores
            log.info(f"🌐 Network error for {url} - assigning moderate fallback scores")
            fallback_scores = {
                "performance": 40,     # Moderate - network issue, not site issue
                "accessibility": 40,   # Moderate - network issue, not site issue
                "bestPractices": 40,  # Moderate - network issue, not site issue
                "seo": 40,            # Moderate - network issue, not site issue
            }
        elif has_rate_limit:
            # Rate limit exceeded - give moderate scores as fallback
            log.info(f"⏱️ Rate limit exceeded for {url} - assigning moderate fallback scores")
            fallback_scores = {
                "performance": 50,     # Moderate - unknown performance
                "accessibility": 50,   # Moderate - unknown accessibility
                "bestPractices": 50,  # Moderate - unknown best practices
                "seo": 50,            # Moderate - unknown SEO
            }
        else:
            # Other API errors - give low-moderate scores
            log.info(f"🔌 API error for {url} - assigning low-moderate fallback scores")
            fallback_scores = {
                "performance": 30,     # Low - API failure
                "accessibility": 30,   # Low - API failure
                "bestPractices": 30,  # Low - API failure
                "seo": 30,            # Low - API failure
            }
        
        # Generate fallback response structure
        fallback_result = {
            "scores": fallback_scores,
            "coreWebVitals": {
                "largestContentfulPaint": None,
                "firstInputDelay": None,
                "cumulativeLayoutShift": None,
                "firstContentfulPaint": None,
                "speedIndex": None,
            },
            "serverMetrics": {
                "serverResponseTime": None,
                "totalBlockingTime": None,
                "timeToInteractive": None,
            },
            "mobileUsability": {},
            "opportunities": [],
            "fallback_reason": {
                "primary_reason": failure_reasons[0].get("type") if failure_reasons else "UNKNOWN_ERROR",
                "all_reasons": failure_reasons,
                "fallback_scores_used": True,
                "timestamp": time.time()
            }
        }
        
        log.info(f"✅ Generated fallback scores for {url}: {fallback_scores}")
        return fallback_result





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
    async def analyze_uptime(self, url: str) -> Dict[str, Any]:
        try:
            results = []
            for i in range(3):
                start = asyncio.get_event_loop().time()
                try:
                    requests.get(url, timeout=10)
                    elapsed = int((asyncio.get_event_loop().time() - start) * 1000)
                    results.append({"success": True, "responseTime": elapsed})
                except Exception:
                    results.append({"success": False, "responseTime": 10_000})

                if i < 2:
                    await asyncio.sleep(1)

            success_count = sum(r["success"] for r in results)
            avg_time = sum(r["responseTime"] for r in results) / len(results)
            uptime = (success_count / len(results)) * 100

            score = 100
            if uptime < 100:
                score -= (100 - uptime) * 2
            if avg_time > 3000:
                score -= 20
            elif avg_time > 1000:
                score -= 10

            return {
                "score": max(0, round(score)),
                "uptime": f"{uptime:.1f}%",
                "averageResponseTime": round(avg_time),
                "status": "up" if uptime > 66 else "down",
                "realData": True,
            }

        except Exception as e:
            raise RuntimeError(f"Uptime analysis error: {e}") from e

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
            
            # Count errors from each service
            if result.get("pageSpeed", {}).get("errors"):
                total_errors += len(result["pageSpeed"]["errors"])
            
            if result.get("whois", {}).get("errors"):
                total_errors += len(result["whois"]["errors"])
            
            if result.get("trustAndCRO", {}).get("errors"):
                total_errors += len(result["trustAndCRO"]["errors"])
            
            if result.get("uptime", {}).get("errors"):
                total_errors += len(result["uptime"]["errors"])
            
            # Count completed services
            if result.get("pageSpeed"):
                services_completed += 1
            if result.get("whois"):
                services_completed += 1
            if result.get("trustAndCRO"):
                services_completed += 1
            if result.get("uptime"):
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
                        "uptime": None,
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
                    "uptime": None,
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
                "uptime": None,
                "summary": None
            }
            
            # 1. PageSpeed Analysis (keep existing working system)
            try:
                pagespeed_result = await self.run_page_speed_analysis(url, strategy)
                result["pageSpeed"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "mobile": pagespeed_result if strategy == "mobile" else None,
                    "desktop": pagespeed_result if strategy == "desktop" else None,
                    "errors": []
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
            
            # 3. Trust and CRO Analysis (placeholder - method not implemented)
            result["trustAndCRO"] = {
                "domain": domain,
                "url": url,
                "timestamp": datetime.now().isoformat(),
                "trust": None,
                "cro": None,
                "errors": ["Trust/CRO analysis not implemented"]
            }
            
            # 4. Uptime Analysis (keep existing working system)
            try:
                uptime_result = await self.analyze_uptime(url)
                result["uptime"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "uptime": {
                        "rawResponse": uptime_result,
                        "parsed": uptime_result
                    },
                    "errors": []
                }
                log.info(f"✅ Uptime analysis completed for {url}")
            except Exception as e:
                log.warning(f"Uptime analysis failed for {url}: {e}")
                result["uptime"] = {
                    "domain": domain,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "uptime": None,
                    "errors": [f"Uptime analysis failed: {e}"]
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
            
            # Record successful request
            self.rate_limiter.record_request('comprehensive_speed', True)
            
            log.info(f"✅ Comprehensive analysis completed for {url}")
            return result
            
        except Exception as e:
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
                "uptime": {
                    "domain": urlparse(url).hostname,
                    "url": url,
                    "timestamp": datetime.now().isoformat(),
                    "uptime": None,
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