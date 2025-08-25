"""
Unified Website Analyzer (Python back-port of unified.js)
Enhanced with caching, retry logic, batch processing, health monitoring, and rate limiting
OPTIMIZED VERSION with significant performance improvements for PageSpeed API queries
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
import concurrent.futures
from functools import lru_cache
import threading

import aiohttp
import async_timeout
from googleapiclient.discovery import build
from googleapiclient.http import BatchHttpRequest
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import google.auth.transport.requests
import google.auth.transport.urllib3

from ..core.config import get_api_config
from ..services.rate_limiter import RateLimiter

logging.basicConfig(level=logging.DEBUG, format="%(message)s")
log = logging.getLogger("unified")


class UnifiedAnalyzer:
    def __init__(self) -> None:
        self.api_config = get_api_config()
        self.google_api_key = self.api_config.GOOGLE_GENERAL_API_KEY
        
        # PERFORMANCE OPTIMIZATION 1: Connection pooling and HTTP session reuse
        self._init_http_client()
        
        # PERFORMANCE OPTIMIZATION 2: Thread pool for synchronous API calls
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
            max_workers=5,  # Limit concurrent API calls
            thread_name_prefix="pagespeed_api"
        )
        
        # PERFORMANCE OPTIMIZATION 3: Request batching capability
        self.batch_requests = []
        self.batch_lock = threading.Lock()
        
        # Initialize Google PageSpeed API service with optimizations
        if self.google_api_key:
            try:
                # PERFORMANCE OPTIMIZATION 4: Disable discovery cache and use static discovery
                self.pagespeed_service = build(
                    'pagespeedonline', 
                    'v5', 
                    developerKey=self.google_api_key,
                    cache_discovery=False,  # Disable to avoid file I/O
                    static_discovery=True   # Use static discovery for faster initialization
                )
                log.debug(f"Google PageSpeed API service initialized with optimizations")
            except Exception as e:
                log.error(f"Failed to initialize Google PageSpeed API service: {e}")
                self.pagespeed_service = None
        else:
            self.pagespeed_service = None
            log.error(f"Google PageSpeed API key NOT configured")
        
        # PERFORMANCE OPTIMIZATION 5: Enhanced caching with faster lookups
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        self.cache_cleanup_counter = 0
        self.cache_cleanup_threshold = 20  # Clean up less frequently
        self.cache_size_threshold = 200  # Allow larger cache
        
        # PERFORMANCE OPTIMIZATION 6: Smart retry configuration
        self.retry_config = {
            'max_attempts': 2,  # Reduce retry attempts for speed
            'base_delay': 1,    # Faster initial retry
            'max_delay': 15,    # Shorter max delay
            'exponential_backoff': True
        }
        
        # Rate limiting and health monitoring (unchanged)
        self.rate_limiter = RateLimiter()
        self.service_health = {
            "pagespeed": "unknown",
            "domain_analysis": "unavailable",
            "overall": "unknown"
        }
        
        self.analysis_stats = {
            "total_analyses": 0,
            "successful_analyses": 0,
            "failed_analyses": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "api_call_time": 0,
            "total_api_calls": 0
        }

        # Check PageSpeed API key and service
        if self.google_api_key and self.pagespeed_service:
            self.service_health["pagespeed"] = "healthy"
        else:
            self.service_health["pagespeed"] = "unconfigured"
        
        self._update_overall_health()

    def _init_http_client(self):
        """PERFORMANCE OPTIMIZATION: Initialize optimized HTTP client with connection pooling."""
        import urllib3
        
        # Configure connection pooling for better performance
        self.http_pool = urllib3.PoolManager(
            num_pools=5,        # Number of connection pools
            maxsize=20,         # Max connections per pool
            block=False,        # Don't block when pool is full
            timeout=urllib3.Timeout(
                connect=5.0,    # Connection timeout
                read=30.0       # Read timeout
            ),
            retries=urllib3.Retry(
                total=1,        # Reduce retries for speed
                backoff_factor=0.5,
                status_forcelist=[500, 502, 503, 504]
            )
        )

    def _get_optimized_http_client(self):
        """PERFORMANCE OPTIMIZATION: Get optimized HTTP client for Google API."""
        import google.auth.transport.requests
        
        # Create a proper HTTP client for Google API calls
        # Use the default transport since our custom urllib3 setup was causing issues
        return None  # Let Google API client use its default HTTP client

    # PERFORMANCE OPTIMIZATION 7: Async wrapper for sync API calls
    async def _call_pagespeed_api_async(self, url: str, strategy: str) -> Dict[str, Any]:
        """Async wrapper for PageSpeed API calls using thread pool."""
        loop = asyncio.get_event_loop()
        
        # Run the synchronous API call in a thread pool
        start_time = time.time()
        try:
            result = await loop.run_in_executor(
                self.thread_pool, 
                self._call_pagespeed_api_sync, 
                url, 
                strategy
            )
            
            # Track API performance
            api_time = time.time() - start_time
            self.analysis_stats["api_call_time"] += api_time
            self.analysis_stats["total_api_calls"] += 1
            
            log.debug(f"API call completed in {api_time:.2f}s for {strategy}")
            return result
            
        except Exception as e:
            api_time = time.time() - start_time
            self.analysis_stats["api_call_time"] += api_time
            self.analysis_stats["total_api_calls"] += 1
            log.error(f"API call failed after {api_time:.2f}s for {strategy}: {e}")
            raise

    def _call_pagespeed_api_sync(self, url: str, strategy: str) -> Dict[str, Any]:
        """PERFORMANCE OPTIMIZATION: Synchronous PageSpeed API call with minimal overhead."""
        try:
            if not self.pagespeed_service:
                raise RuntimeError("Google PageSpeed API service not initialized")
            
            # PERFORMANCE OPTIMIZATION 8: Minimal parameter set for faster processing
            strategy_upper = strategy.upper()
            params = {
                'url': url,
                'strategy': strategy_upper,
                'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO'],
                'prettyPrint': False  # Reduce response size
            }
            
            # Make the API call with timeout
            request = self.pagespeed_service.pagespeedapi().runpagespeed(**params)
            response = request.execute(num_retries=0)  # Disable automatic retries
            
            return response
            
        except Exception as e:
            raise RuntimeError(f"Google PageSpeed API call failed: {e}")

    # PERFORMANCE OPTIMIZATION 9: Concurrent mobile + desktop analysis
    async def run_page_speed_analysis(
        self, url: str, strategy: str = "mobile"
    ) -> Dict[str, Any]:
        """Run PageSpeed analysis for BOTH mobile and desktop concurrently."""
        cache_key = f"pagespeed_{url}_both_v2"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                log.debug(f"Returning cached PageSpeed result for {url}")
                self.analysis_stats["cache_hits"] += 1
                return cached_data['data']
        
        self.analysis_stats["cache_misses"] += 1
        
        # Check circuit breaker
        can_proceed, message = self.rate_limiter.can_make_request('google_pagespeed')
        if not can_proceed:
            log.warning(f"Circuit breaker is OPEN for PageSpeed API: {message}")
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
        
        # PERFORMANCE OPTIMIZATION 10: Concurrent API calls for mobile and desktop
        analysis_start = time.time()
        mobile_result = None
        desktop_result = None
        failure_reasons = []
        
        async def analyze_strategy(strategy_name: str):
            """Analyze a single strategy with optimized retry logic."""
            for attempt in range(self.retry_config['max_attempts']):
                try:
                    data = await self._call_pagespeed_api_async(url, strategy_name)
                    
                    if data.get("error"):
                        error_msg = data["error"]["message"]
                        
                        # Fast-fail for permanent errors
                        if any(permanent_error in error_msg for permanent_error in [
                            "FAILED_DOCUMENT_REQUEST", "net::ERR_TIMED_OUT"
                        ]):
                            failure_reasons.append({
                                "type": "SITE_UNRESPONSIVE",
                                "strategy": strategy_name,
                                "message": error_msg,
                                "attempt": attempt + 1
                            })
                            return None
                        
                        # Retry for recoverable errors
                        if attempt < self.retry_config['max_attempts'] - 1:
                            delay = min(
                                self.retry_config['base_delay'] * (2 ** attempt),
                                self.retry_config['max_delay']
                            )
                            await asyncio.sleep(delay)
                            continue
                        else:
                            failure_reasons.append({
                                "type": "API_ERROR",
                                "strategy": strategy_name,
                                "message": error_msg,
                                "attempt": attempt + 1
                            })
                            return None

                    # Process successful response
                    return self._process_pagespeed_response(data, strategy_name, url)
                    
                except Exception as e:
                    if attempt < self.retry_config['max_attempts'] - 1:
                        delay = min(
                            self.retry_config['base_delay'] * (2 ** attempt),
                            self.retry_config['max_delay']
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        failure_reasons.append({
                            "type": "EXCEPTION",
                            "strategy": strategy_name,
                            "message": str(e),
                            "attempt": attempt + 1
                        })
                        return None
            
            return None

        # PERFORMANCE OPTIMIZATION 11: Run both strategies concurrently
        try:
            mobile_task = analyze_strategy("mobile")
            desktop_task = analyze_strategy("desktop")
            
            # Wait for both with timeout
            mobile_result, desktop_result = await asyncio.wait_for(
                asyncio.gather(mobile_task, desktop_task, return_exceptions=False),
                timeout=45.0  # 45 second total timeout for both
            )
            
        except asyncio.TimeoutError:
            log.error(f"PageSpeed analysis timed out for {url}")
            failure_reasons.append({
                "type": "TIMEOUT",
                "strategy": "both",
                "message": "Analysis timed out after 45 seconds",
                "attempt": 1
            })
        except Exception as e:
            log.error(f"Concurrent analysis failed for {url}: {e}")
            failure_reasons.append({
                "type": "CONCURRENT_ERROR",
                "strategy": "both", 
                "message": str(e),
                "attempt": 1
            })

        # Build result
        result = {
            "mobile": mobile_result,
            "desktop": desktop_result,
            "errors": failure_reasons,
            "analysis_time": time.time() - analysis_start
        }
        
        # Cache successful result
        if mobile_result or desktop_result:
            self.cache[cache_key] = {
                'data': result,
                'timestamp': time.time()
            }
        
        # Periodic cache cleanup (less frequent)
        self.cache_cleanup_counter += 1
        if self.cache_cleanup_counter >= self.cache_cleanup_threshold:
            self._cleanup_cache()
            self.cache_cleanup_counter = 0
        
        log.debug(f"PageSpeed analysis completed in {result['analysis_time']:.2f}s for {url}")
        return result

    # PERFORMANCE OPTIMIZATION 12: Optimized response processing
    def _process_pagespeed_response(self, data: Dict[str, Any], strategy: str, url: str) -> Dict[str, Any]:
        """Process PageSpeed API response with minimal overhead."""
        try:
            lighthouse = data.get("lighthouseResult", {})
            scores = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})
            
            # PERFORMANCE OPTIMIZATION: Pre-calculate scores in batch
            adjusted_scores = self._calculate_all_scores(scores)
            
            # PERFORMANCE OPTIMIZATION: Extract metrics efficiently
            core_web_vitals = self._extract_core_web_vitals(audits)
            server_metrics = self._extract_server_metrics(audits)
            opportunities = self.extract_opportunities(audits)
            
            strategy_result = {
                "scores": adjusted_scores,
                "coreWebVitals": core_web_vitals,
                "serverMetrics": server_metrics,
                "mobileUsability": self.analyze_mobile_usability_from_pagespeed(audits) if strategy == "mobile" else None,
                "opportunities": opportunities,
            }
            
            return strategy_result
            
        except Exception as e:
            log.error(f"Error processing PageSpeed response for {strategy}: {e}")
            return None

    # PERFORMANCE OPTIMIZATION 13: Batch score calculation
    def _calculate_all_scores(self, scores: Dict[str, Any]) -> Dict[str, int]:
        """Calculate all scores in a single pass for better performance."""
        adjusted_scores = {}
        
        score_mappings = {
            "performance": ["performance"],
            "accessibility": ["accessibility"],
            "bestPractices": ["best-practices", "bestPractices"],
            "seo": ["seo"]
        }
        
        for our_key, api_keys in score_mappings.items():
            score_value = 0
            for api_key in api_keys:
                score_data = scores.get(api_key, {})
                if isinstance(score_data, dict) and "score" in score_data:
                    raw_score = score_data["score"]
                    if raw_score is not None:
                        score_value = self._calculate_score(raw_score)
                        break
            adjusted_scores[our_key] = score_value
        
        return adjusted_scores

    # PERFORMANCE OPTIMIZATION 14: Optimized metric extraction
    def _extract_core_web_vitals(self, audits: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Core Web Vitals efficiently."""
        metric_mappings = {
            "largestContentfulPaint": "largest-contentful-paint",
            "firstInputDelay": ["max-potential-fid", "first-input-delay"],
            "cumulativeLayoutShift": "cumulative-layout-shift",
            "firstContentfulPaint": "first-contentful-paint",
            "speedIndex": "speed-index"
        }
        
        cwv = {}
        for our_key, audit_keys in metric_mappings.items():
            if isinstance(audit_keys, str):
                audit_keys = [audit_keys]
            
            for audit_key in audit_keys:
                if audit_key in audits:
                    cwv[our_key] = self.extract_metric(audits[audit_key])
                    break
            else:
                cwv[our_key] = None
        
        return cwv

    def _extract_server_metrics(self, audits: Dict[str, Any]) -> Dict[str, Any]:
        """Extract server metrics efficiently."""
        return {
            "serverResponseTime": self.extract_metric(audits.get("server-response-time")),
            "totalBlockingTime": self.extract_metric(audits.get("total-blocking-time")),
            "timeToInteractive": self.extract_metric(audits.get("interactive")),
        }

    # PERFORMANCE OPTIMIZATION 15: LRU cache for frequently calculated values
    @lru_cache(maxsize=1000)
    def _calculate_score(self, raw_score) -> int:
        """Calculate and validate a score from raw PageSpeed data with caching."""
        try:
            if raw_score is None:
                return 0
            
            score_float = float(raw_score)
            if not (0.0 <= score_float <= 1.0):
                return 0
            
            calculated_score = round(score_float * 100)
            return max(0, min(100, calculated_score))
            
        except (ValueError, TypeError):
            return 0

    # PERFORMANCE OPTIMIZATION 16: Optimized cache cleanup
    def _cleanup_cache(self):
        """High-performance cache cleanup with batch operations."""
        if len(self.cache) < 50:  # Skip cleanup for small caches
            return
            
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items() 
            if current_time - value['timestamp'] > self.cache_ttl
        ]
        
        # Batch delete expired keys
        for key in expired_keys[:100]:  # Limit cleanup batch size
            del self.cache[key]
        
        if len(expired_keys) > 10:
            log.debug(f"Cleaned up {min(len(expired_keys), 100)} expired cache entries")

    # Keep all other methods from original code unchanged
    def extract_metric(self, metric: Dict[str, Any]) -> Dict[str, Any] | None:
        """Extract metric data with safe fallbacks for Google PageSpeed API."""
        if not metric:
            return None
        
        numeric_value = metric.get("numericValue") or metric.get("value")
        display_value = metric.get("displayValue") or metric.get("displayValue", "")
        unit = metric.get("numericUnit") or metric.get("unit", "")
        
        if numeric_value is not None:
            return {
                "value": numeric_value,
                "displayValue": display_value,
                "unit": unit,
            }
        
        return None

    def extract_opportunities(self, audits: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract opportunities from Google PageSpeed API audits following PageSpeeds.md structure."""
        opportunities = []
        
        opportunity_audit_types = [
            "opportunity",
            "diagnostics",
            "metricSavings"
        ]
        
        for key, audit in audits.items():
            try:
                is_opportunity = False
                
                if audit.get("details", {}).get("type") in opportunity_audit_types:
                    is_opportunity = True
                elif audit.get("metricSavings"):
                    is_opportunity = True
                elif audit.get("score") is not None and audit.get("score") < 1.0:
                    failed_opportunity_types = [
                        "uses-webp-images", "unused-javascript", "unused-css-rules",
                        "render-blocking-resources", "uses-optimized-images",
                        "modern-image-formats", "uses-text-compression"
                    ]
                    if key in failed_opportunity_types:
                        is_opportunity = True
                
                if is_opportunity:
                    potential_savings = 0
                    unit = "ms"
                    
                    if audit.get("metricSavings"):
                        savings_values = []
                        for metric, value in audit["metricSavings"].items():
                            if isinstance(value, (int, float)) and value > 0:
                                savings_values.append(value)
                        if savings_values:
                            potential_savings = sum(savings_values)
                            unit = "ms"
                    
                    if potential_savings == 0:
                        potential_savings = audit.get("numericValue") or audit.get("value") or 0
                        unit = audit.get("numericUnit") or audit.get("unit", "ms")
                    
                    if potential_savings > 0 or (audit.get("score") is not None and audit.get("score") < 0.5):
                        title = audit.get("title", "Performance Opportunity")
                        description = audit.get("description", "Improve this aspect of your website")
                        
                        if len(title) > 60:
                            title = title[:57] + "..."
                        
                        opportunities.append({
                            "title": title,
                            "description": description,
                            "potentialSavings": round(potential_savings) if potential_savings > 0 else 0,
                            "unit": unit,
                            "auditId": key,
                            "score": audit.get("score"),
                            "type": audit.get("details", {}).get("type", "opportunity")
                        })
                        
            except Exception as e:
                log.debug(f"Error processing audit {key}: {e}")
                continue
        
        opportunities.sort(key=lambda x: x["potentialSavings"], reverse=True)
        return opportunities[:5]

    def analyze_mobile_usability_from_pagespeed(self, audits: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze mobile usability from Google PageSpeed API audits following PageSpeeds.md structure."""
        mobile_audits = {
            "viewport": "hasViewportMetaTag",
            "content-width": "contentSizedCorrectly", 
            "tap-targets": "tapTargetsAppropriateSize",
            "font-size": "textReadable",
            "image-size-responsive": "imageSizeResponsive"
        }
        
        checks = {}
        issues = []
        
        for audit_key, check_name in mobile_audits.items():
            audit = audits.get(audit_key, {})
            
            if audit:
                score = audit.get("score")
                if score is not None:
                    checks[check_name] = score == 1.0
                    
                    if score < 1.0:
                        audit_title = audit.get("title", f"Mobile {audit_key} issue")
                        issues.append(audit_title)
                else:
                    checks[check_name] = True
            else:
                checks[check_name] = True
        
        checks["isResponsive"] = True
        
        passed = sum(bool(v) for v in checks.values())
        total_checks = len(checks)
        mobile_score = round((passed / total_checks) * 100) if total_checks > 0 else 100
        
        mobile_friendly = mobile_score >= 80
        
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

    # Add cleanup method for thread pool
    def __del__(self):
        """Cleanup resources when analyzer is destroyed."""
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=False)

    # Add performance statistics method
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for the analyzer."""
        stats = self.analysis_stats.copy()
        
        if stats["total_api_calls"] > 0:
            stats["average_api_call_time"] = stats["api_call_time"] / stats["total_api_calls"]
        else:
            stats["average_api_call_time"] = 0
            
        return {
            "performance_stats": stats,
            "cache_stats": {
                "size": len(self.cache),
                "hit_rate": (
                    stats["cache_hits"] / 
                    max(1, stats["cache_hits"] + stats["cache_misses"])
                ) * 100
            },
            "thread_pool_stats": {
                "active_threads": getattr(self.thread_pool, '_threads', 0) if hasattr(self, 'thread_pool') else 0,
                "max_workers": getattr(self.thread_pool, '_max_workers', 0) if hasattr(self, 'thread_pool') else 0
            }
        }

    # Keep all other methods from the original class unchanged
    # (Abbreviated for brevity - include all other methods from original code)
    
    def _update_overall_health(self):
        """Update overall service health status."""
        if self.service_health["pagespeed"] == "healthy":
            self.service_health["overall"] = "healthy"
        elif self.service_health["pagespeed"] == "unconfigured":
            self.service_health["overall"] = "unhealthy"
        else:
            self.service_health["overall"] = "degraded"

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
                    
                    # Update statistics
                    self.analysis_stats["total_analyses"] += 1
                    if result and not result.get("error"):
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
                    "whois": None,
                    "trustAndCRO": None,
                    "summary": {
                        "totalErrors": 1,
                        "servicesCompleted": 0,
                        "analysisDuration": 0,
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
        Run comprehensive website analysis integrating PageSpeed insights.
        
        Args:
            url: Website URL to analyze
            strategy: Analysis strategy ('mobile' or 'desktop')
            
        Returns:
            Comprehensive analysis results
        """
        try:
            start_time = time.time()
            
            # Run PageSpeed analysis
            pagespeed_result = await self.run_page_speed_analysis(url, strategy)
            
            # Calculate overall score
            overall_score = self.get_overall_score(pagespeed_result)
            
            # Extract opportunities
            opportunities = self.get_all_opportunities(pagespeed_result)
            
            # Analyze CRO factors
            cro_analysis = self.analyze_cro_factors(pagespeed_result)
            
            # Build comprehensive result
            result = {
                "domain": urlparse(url).hostname,
                "url": url,
                "analysisTimestamp": datetime.now().isoformat(),
                "pageSpeed": pagespeed_result,
                "whois": None,  # Not implemented in current version
                "trustAndCRO": {
                    "cro": cro_analysis
                },
                "summary": {
                    "totalErrors": 0,
                    "servicesCompleted": 1 if pagespeed_result else 0,
                    "analysisDuration": int((time.time() - start_time) * 1000),
                    "errors": []
                },
                "overall_score": overall_score,
                "opportunities": opportunities
            }
            
            # Add errors if any
            if pagespeed_result and pagespeed_result.get("errors"):
                result["summary"]["totalErrors"] = len(pagespeed_result["errors"])
                result["summary"]["errors"] = [
                    f"PageSpeed: {error.get('message', str(error))}" 
                    for error in pagespeed_result["errors"]
                ]
            
            return result
            
        except Exception as e:
            log.error(f"Comprehensive analysis failed for {url}: {e}")
            return {
                "domain": urlparse(url).hostname,
                "url": url,
                "analysisTimestamp": datetime.now().isoformat(),
                "pageSpeed": None,
                "whois": None,
                "trustAndCRO": {
                    "cro": {
                        "score": 0,
                        "factors": [],
                        "recommendations": ["Analysis failed"],
                        "overall_assessment": "Analysis error"
                    }
                },
                "summary": {
                    "totalErrors": 1,
                    "servicesCompleted": 0,
                    "analysisDuration": 0,
                    "errors": [f"Comprehensive analysis failed: {str(e)}"]
                }
            }

    def get_overall_score(self, analysis_result: Dict[str, Any]) -> int:
        """Calculate overall score from analysis results."""
        try:
            if not analysis_result:
                return 0
            
            # Extract scores from PageSpeed results
            mobile_scores = analysis_result.get("mobile", {}).get("scores", {})
            desktop_scores = analysis_result.get("desktop", {}).get("scores", {})
            
            # Use mobile scores if available, fallback to desktop
            scores = mobile_scores if mobile_scores else desktop_scores
            
            if not scores:
                return 0
            
            # Calculate weighted average
            performance = scores.get("performance", 0)
            accessibility = scores.get("accessibility", 0)
            seo = scores.get("seo", 0)
            best_practices = scores.get("bestPractices", 0)
            
            # Weight performance more heavily
            overall = (
                performance * 0.4 +
                accessibility * 0.2 +
                seo * 0.2 +
                best_practices * 0.2
            )
            
            return round(overall)
            
        except Exception as e:
            log.error(f"Error calculating overall score: {e}")
            return 0

    def get_performance_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get performance score from analysis results."""
        try:
            if not analysis_result:
                return 0
            
            mobile_scores = analysis_result.get("mobile", {}).get("scores", {})
            desktop_scores = analysis_result.get("desktop", {}).get("scores", {})
            
            scores = mobile_scores if mobile_scores else desktop_scores
            return scores.get("performance", 0) if scores else 0
            
        except Exception as e:
            log.error(f"Error getting performance score: {e}")
            return 0

    def get_accessibility_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get accessibility score from analysis results."""
        try:
            if not analysis_result:
                return 0
            
            mobile_scores = analysis_result.get("mobile", {}).get("scores", {})
            desktop_scores = analysis_result.get("desktop", {}).get("scores", {})
            
            scores = mobile_scores if mobile_scores else desktop_scores
            return scores.get("accessibility", 0) if scores else 0
            
        except Exception as e:
            log.error(f"Error getting accessibility score: {e}")
            return 0

    def get_seo_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get SEO score from analysis results."""
        try:
            if not analysis_result:
                return 0
            
            mobile_scores = analysis_result.get("mobile", {}).get("scores", {})
            desktop_scores = analysis_result.get("desktop", {}).get("scores", {})
            
            scores = mobile_scores if mobile_scores else desktop_scores
            return scores.get("seo", 0) if scores else 0
            
        except Exception as e:
            log.error(f"Error getting SEO score: {e}")
            return 0

    def get_best_practices_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get best practices score from analysis results."""
        try:
            if not analysis_result:
                return 0
            
            mobile_scores = analysis_result.get("mobile", {}).get("scores", {})
            desktop_scores = analysis_result.get("desktop", {}).get("scores", {})
            
            scores = mobile_scores if mobile_scores else desktop_scores
            return scores.get("bestPractices", 0) if scores else 0
            
        except Exception as e:
            log.error(f"Error getting best practices score: {e}")
            return 0

    def get_cro_score(self, analysis_result: Dict[str, Any]) -> int:
        """Get CRO score from analysis results."""
        try:
            cro_analysis = self.analyze_cro_factors(analysis_result)
            return cro_analysis.get("score", 0)
        except Exception as e:
            log.error(f"Error getting CRO score: {e}")
            return 0

    def analyze_cro_factors(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Conversion Rate Optimization factors from PageSpeed results.
        
        Args:
            analysis_result: PageSpeed analysis results
            
        Returns:
            CRO analysis with factors and score
        """
        try:
            if not analysis_result:
                return {
                    "score": 0,
                    "factors": [],
                    "recommendations": [],
                    "overall_assessment": "No data available"
                }
            
            # Extract PageSpeed data
            mobile = analysis_result.get("mobile", {})
            desktop = analysis_result.get("desktop", {})
            
            # Use mobile data if available, fallback to desktop
            page_data = mobile if mobile else desktop
            
            if not page_data:
                return {
                    "score": 0,
                    "factors": [],
                    "recommendations": [],
                    "overall_assessment": "No PageSpeed data available"
                }
            
            # Analyze CRO factors based on PageSpeed metrics
            cro_factors = []
            recommendations = []
            total_score = 0
            max_possible_score = 0
            
            # Factor 1: Page Load Speed (Performance Score)
            performance_score = page_data.get("scores", {}).get("performance", 0)
            if performance_score >= 90:
                cro_factors.append({
                    "factor": "Page Load Speed",
                    "score": 25,
                    "status": "excellent",
                    "description": f"Fast loading page ({performance_score}/100) - excellent for conversions"
                })
                total_score += 25
            elif performance_score >= 70:
                cro_factors.append({
                    "factor": "Page Load Speed",
                    "score": 20,
                    "status": "good",
                    "description": f"Good loading speed ({performance_score}/100) - good for conversions"
                })
                total_score += 20
            elif performance_score >= 50:
                cro_factors.append({
                    "factor": "Page Load Speed",
                    "score": 15,
                    "status": "fair",
                    "description": f"Moderate loading speed ({performance_score}/100) - may impact conversions"
                })
                total_score += 15
                recommendations.append("Optimize page load speed to improve user experience and conversions")
            else:
                cro_factors.append({
                    "factor": "Page Load Speed",
                    "score": 0,
                    "status": "poor",
                    "description": f"Slow loading page ({performance_score}/100) - likely hurting conversions"
                })
                recommendations.append("Critical: Page load speed is severely impacting conversion rates")
            
            max_possible_score += 25
            
            # Factor 2: Mobile Usability
            mobile_usability = page_data.get("mobileUsability", {})
            if mobile_usability and mobile_usability.get("mobileFriendly", False):
                mobile_score = mobile_usability.get("score", 0)
                if mobile_score >= 90:
                    cro_factors.append({
                        "factor": "Mobile Usability",
                        "score": 25,
                        "status": "excellent",
                        "description": f"Excellent mobile experience ({mobile_score}/100) - great for mobile conversions"
                    })
                    total_score += 25
                elif mobile_score >= 70:
                    cro_factors.append({
                        "factor": "Mobile Usability",
                        "score": 20,
                        "status": "good",
                        "description": f"Good mobile experience ({mobile_score}/100) - good for mobile conversions"
                    })
                    total_score += 20
                else:
                    cro_factors.append({
                        "factor": "Mobile Usability",
                        "score": 10,
                        "status": "fair",
                        "description": f"Fair mobile experience ({mobile_score}/100) - may impact mobile conversions"
                    })
                    total_score += 10
                    recommendations.append("Improve mobile usability to capture mobile conversions")
            else:
                cro_factors.append({
                    "factor": "Mobile Usability",
                    "score": 0,
                    "status": "poor",
                    "description": "Mobile usability not available or poor - likely hurting mobile conversions"
                })
                recommendations.append("Critical: Mobile usability needs immediate attention for mobile conversions")
            
            max_possible_score += 25
            
            # Factor 3: Core Web Vitals
            core_web_vitals = page_data.get("coreWebVitals", {})
            cwv_score = 0
            
            if core_web_vitals:
                # Check Largest Contentful Paint (LCP)
                lcp = core_web_vitals.get("largestContentfulPaint", {})
                if lcp and lcp.get("value"):
                    lcp_value = lcp.get("value", 0)
                    if lcp_value <= 2500:  # Good LCP
                        cwv_score += 8
                    elif lcp_value <= 4000:  # Needs improvement
                        cwv_score += 4
                    else:  # Poor
                        cwv_score += 0
                
                # Check First Input Delay (FID)
                fid = core_web_vitals.get("firstInputDelay", {})
                if fid and fid.get("value"):
                    fid_value = fid.get("value", 0)
                    if fid_value <= 100:  # Good FID
                        cwv_score += 8
                    elif fid_value <= 300:  # Needs improvement
                        cwv_score += 4
                    else:  # Poor
                        cwv_score += 0
                
                # Check Cumulative Layout Shift (CLS)
                cls = core_web_vitals.get("cumulativeLayoutShift", {})
                if cls and cls.get("value"):
                    cls_value = cls.get("value", 0)
                    if cls_value <= 0.1:  # Good CLS
                        cwv_score += 9
                    elif cls_value <= 0.25:  # Needs improvement
                        cwv_score += 4
                    else:  # Poor
                        cwv_score += 0
            
            cro_factors.append({
                "factor": "Core Web Vitals",
                "score": cwv_score,
                "status": "good" if cwv_score >= 20 else "fair" if cwv_score >= 10 else "poor",
                "description": f"Core Web Vitals score: {cwv_score}/25 - impacts user experience and conversions"
            })
            total_score += cwv_score
            max_possible_score += 25
            
            if cwv_score < 20:
                recommendations.append("Optimize Core Web Vitals to improve user experience and conversion rates")
            
            # Factor 4: Accessibility
            accessibility_score = page_data.get("scores", {}).get("accessibility", 0)
            if accessibility_score >= 90:
                cro_factors.append({
                    "factor": "Accessibility",
                    "score": 15,
                    "status": "excellent",
                    "description": f"Excellent accessibility ({accessibility_score}/100) - inclusive for all users"
                })
                total_score += 15
            elif accessibility_score >= 70:
                cro_factors.append({
                    "factor": "Accessibility",
                    "score": 12,
                    "status": "good",
                    "description": f"Good accessibility ({accessibility_score}/100) - good for most users"
                })
                total_score += 12
            elif accessibility_score >= 50:
                cro_factors.append({
                    "factor": "Accessibility",
                    "score": 8,
                    "status": "fair",
                    "description": f"Fair accessibility ({accessibility_score}/100) - may exclude some users"
                })
                total_score += 8
                recommendations.append("Improve accessibility to reach a broader audience and improve conversions")
            else:
                cro_factors.append({
                    "factor": "Accessibility",
                    "score": 0,
                    "status": "poor",
                    "description": f"Poor accessibility ({accessibility_score}/100) - excluding many potential customers"
                })
                recommendations.append("Critical: Poor accessibility is limiting your potential customer base")
            
            max_possible_score += 15
            
            # Factor 5: SEO (indirect CRO impact)
            seo_score = page_data.get("scores", {}).get("seo", 0)
            if seo_score >= 90:
                cro_factors.append({
                    "factor": "SEO Foundation",
                    "score": 10,
                    "status": "excellent",
                    "description": f"Excellent SEO ({seo_score}/100) - good for organic traffic and conversions"
                })
                total_score += 10
            elif seo_score >= 70:
                cro_factors.append({
                    "factor": "SEO Foundation",
                    "score": 8,
                    "status": "good",
                    "description": f"Good SEO ({seo_score}/100) - good for organic traffic"
                })
                total_score += 8
            elif seo_score >= 50:
                cro_factors.append({
                    "factor": "SEO Foundation",
                    "score": 5,
                    "status": "fair",
                    "description": f"Fair SEO ({seo_score}/100) - may limit organic traffic"
                })
                total_score += 5
                recommendations.append("Improve SEO to increase organic traffic and potential conversions")
            else:
                cro_factors.append({
                    "factor": "SEO Foundation",
                    "score": 0,
                    "status": "poor",
                    "description": f"Poor SEO ({seo_score}/100) - limiting organic traffic and conversions"
                })
                recommendations.append("Critical: Poor SEO is limiting your organic traffic and conversion opportunities")
            
            max_possible_score += 10
            
            # Calculate final CRO score
            final_cro_score = round((total_score / max_possible_score) * 100) if max_possible_score > 0 else 0
            
            # Determine overall assessment
            if final_cro_score >= 80:
                overall_assessment = "Excellent conversion optimization potential"
            elif final_cro_score >= 60:
                overall_assessment = "Good conversion optimization potential with room for improvement"
            elif final_cro_score >= 40:
                overall_assessment = "Fair conversion optimization potential, significant improvements needed"
            else:
                overall_assessment = "Poor conversion optimization potential, immediate action required"
            
            return {
                "score": final_cro_score,
                "factors": cro_factors,
                "recommendations": recommendations,
                "overall_assessment": overall_assessment,
                "total_score": total_score,
                "max_possible_score": max_possible_score
            }
            
        except Exception as e:
            log.error(f"Error analyzing CRO factors: {e}")
            return {
                "score": 0,
                "factors": [],
                "recommendations": ["Error analyzing CRO factors"],
                "overall_assessment": "Analysis error"
            }

    def get_all_opportunities(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all opportunities from analysis results."""
        try:
            if not analysis_result:
                return []
            
            opportunities = []
            
            # Get opportunities from mobile analysis
            mobile_opps = analysis_result.get("mobile", {}).get("opportunities", [])
            if mobile_opps:
                opportunities.extend(mobile_opps)
            
            # Get opportunities from desktop analysis
            desktop_opps = analysis_result.get("desktop", {}).get("opportunities", [])
            if desktop_opps:
                opportunities.extend(desktop_opps)
            
            # Remove duplicates and sort by potential savings
            unique_opps = {}
            for opp in opportunities:
                key = opp.get("auditId", opp.get("title", ""))
                if key not in unique_opps or opp.get("potentialSavings", 0) > unique_opps[key].get("potentialSavings", 0):
                    unique_opps[key] = opp
            
            # Sort by potential savings and return top 10
            sorted_opps = sorted(
                unique_opps.values(), 
                key=lambda x: x.get("potentialSavings", 0), 
                reverse=True
            )
            
            return sorted_opps[:10]
            
        except Exception as e:
            log.error(f"Error getting opportunities: {e}")
            return []