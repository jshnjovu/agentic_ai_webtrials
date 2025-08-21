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
                
                # Log individual score calculations for debugging
                for category, score_data in scores.items():
                    raw_score = score_data.get("score", 0)
                    calculated_score = self._calculate_score(raw_score)
                    log.info(f"📊 {category}: raw={raw_score}, calculated={calculated_score}")
                
                # Detect minimal content sites and adjust scores if necessary
                adjusted_scores = self._adjust_scores_for_minimal_content(scores, audits, url)
                
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

    def _adjust_scores_for_minimal_content(self, scores: Dict[str, Any], audits: Dict[str, Any], url: str) -> Dict[str, int]:
        """Adjust scores for minimal content sites to prevent artificially high scores."""
        try:
            # Calculate base scores
            base_scores = {
                "performance": self._calculate_score(scores.get("performance", {}).get("score", 0)),
                "accessibility": self._calculate_score(scores.get("accessibility", {}).get("score", 0)),
                "bestPractices": self._calculate_score(scores.get("best-practices", {}).get("score", 0)),
                "seo": self._calculate_score(scores.get("seo", {}).get("score", 0)),
            }
            
            # Detect minimal content indicators
            minimal_content_indicators = []
            
            # Check for very small page sizes (likely minimal content)
            if "total-byte-weight" in audits:
                total_bytes = audits.get("total-byte-weight", {}).get("numericValue", 0)
                if total_bytes and total_bytes < 50000:  # Less than 50KB
                    minimal_content_indicators.append(f"small_page_size({total_bytes} bytes)")
            
            # Check for minimal DOM elements
            if "dom-size" in audits:
                dom_size = audits.get("dom-size", {}).get("numericValue", 0)
                if dom_size and dom_size < 100:  # Less than 100 DOM nodes
                    minimal_content_indicators.append(f"small_dom({dom_size} nodes)")
            
            # Check for minimal text content
            if "document-title" in audits:
                title = audits.get("document-title", {}).get("details", {}).get("items", [{}])[0].get("title", "")
                if title and len(title) < 20:  # Very short title
                    minimal_content_indicators.append(f"short_title({title})")
            
            # Check for minimal images
            if "image-alt" in audits:
                image_count = len(audits.get("image-alt", {}).get("details", {}).get("items", []))
                if image_count < 3:  # Very few images
                    minimal_content_indicators.append(f"few_images({image_count})")
            
            # Check for meaningful content length
            if "document-title" in audits:
                title_details = audits.get("document-title", {}).get("details", {})
                if title_details:
                    # Check if title suggests minimal content (parked domain, etc.)
                    title_text = title_details.get("items", [{}])[0].get("title", "").lower()
                    minimal_keywords = ["buy this domain", "domain for sale", "parked", "coming soon", "under construction"]
                    if any(keyword in title_text for keyword in minimal_keywords):
                        minimal_content_indicators.append(f"minimal_title_keywords({title_text})")
            
            # Check for minimal interactive elements
            if "button-name" in audits:
                button_count = len(audits.get("button-name", {}).get("details", {}).get("items", []))
                if button_count < 2:  # Very few interactive elements
                    minimal_content_indicators.append(f"few_buttons({button_count})")
            
            # Check for minimal links
            if "link-name" in audits:
                link_count = len(audits.get("link-name", {}).get("details", {}).get("items", []))
                if link_count < 5:  # Very few links
                    minimal_content_indicators.append(f"few_links({link_count})")
            
            # Check for minimal form elements
            if "label" in audits:
                form_count = len(audits.get("label", {}).get("details", {}).get("items", []))
                if form_count < 2:  # Very few form elements
                    minimal_content_indicators.append(f"few_forms({form_count})")
            
            # If minimal content is detected, adjust scores
            if minimal_content_indicators:
                log.warning(f"🌐 Minimal content detected for {url}: {', '.join(minimal_content_indicators)}")
                log.warning(f"📊 Adjusting scores to prevent artificially high results")
                
                # Calculate adjustment severity based on indicators
                severity_score = len(minimal_content_indicators)
                if any("minimal_title_keywords" in indicator for indicator in minimal_content_indicators):
                    severity_score += 3  # Heavy penalty for parked domains
                if any("small_page_size" in indicator for indicator in minimal_content_indicators):
                    severity_score += 2  # Medium penalty for very small pages
                
                # Apply adjustment factors for minimal content
                adjusted_scores = {}
                for category, score in base_scores.items():
                    if score > 70:  # Adjust scores above 70
                        # More aggressive reduction for higher scores
                        if severity_score >= 5:
                            reduction_factor = 0.6  # 40% reduction for severe cases
                        elif severity_score >= 3:
                            reduction_factor = 0.7  # 30% reduction for moderate cases
                        else:
                            reduction_factor = 0.8  # 20% reduction for mild cases
                        
                        adjusted_score = round(score * reduction_factor)
                        adjusted_scores[category] = adjusted_score
                        log.info(f"📊 {category}: {score} → {adjusted_score} (minimal content adjustment, severity: {severity_score})")
                    else:
                        adjusted_scores[category] = score
                
                # Add adjustment metadata
                adjusted_scores["_adjustment_metadata"] = {
                    "minimal_content_detected": True,
                    "indicators": minimal_content_indicators,
                    "severity_score": severity_score,
                    "adjustment_reason": "Scores adjusted due to minimal content detection"
                }
                
                # Calculate content quality score
                content_quality_score = self._calculate_content_quality_score(audits, minimal_content_indicators)
                adjusted_scores["content_quality"] = content_quality_score
                
                return adjusted_scores
            
            # No adjustment needed, but still calculate content quality
            base_scores["content_quality"] = self._calculate_content_quality_score(audits, [])
            return base_scores
            
        except Exception as e:
            log.warning(f"⚠️ Error adjusting scores for minimal content: {e}")
            # Return base scores if adjustment fails
            return {
                "performance": self._calculate_score(scores.get("performance", {}).get("score", 0)),
                "accessibility": self._calculate_score(scores.get("accessibility", {}).get("score", 0)),
                "bestPractices": self._calculate_score(scores.get("best-practices", {}).get("score", 0)),
                "seo": self._calculate_score(scores.get("seo", {}).get("score", 0)),
                "content_quality": 50,  # Default content quality score
            }

    def _calculate_content_quality_score(self, audits: Dict[str, Any], minimal_indicators: List[str]) -> int:
        """Calculate a content quality score based on various content indicators."""
        try:
            quality_score = 50  # Base score
            
            # Positive indicators
            if "document-title" in audits:
                title_details = audits.get("document-title", {}).get("details", {})
                if title_details:
                    title_text = title_details.get("items", [{}])[0].get("title", "").lower()
                    # Check for meaningful content indicators
                    meaningful_keywords = ["gym", "fitness", "health", "training", "exercise", "workout"]
                    if any(keyword in title_text for keyword in meaningful_keywords):
                        quality_score += 20
            
            # Check for substantial content
            if "total-byte-weight" in audits:
                total_bytes = audits.get("total-byte-weight", {}).get("numericValue", 0)
                if total_bytes > 100000:  # More than 100KB
                    quality_score += 15
                elif total_bytes > 50000:  # More than 50KB
                    quality_score += 10
            
            # Check for interactive elements
            if "button-name" in audits:
                button_count = len(audits.get("button-name", {}).get("details", {}).get("items", []))
                if button_count >= 5:
                    quality_score += 10
                elif button_count >= 2:
                    quality_score += 5
            
            # Check for images
            if "image-alt" in audits:
                image_count = len(audits.get("image-alt", {}).get("details", {}).get("items", []))
                if image_count >= 10:
                    quality_score += 15
                elif image_count >= 5:
                    quality_score += 10
                elif image_count >= 3:
                    quality_score += 5
            
            # Negative indicators (minimal content)
            if minimal_indicators:
                quality_score -= len(minimal_indicators) * 5
                if any("minimal_title_keywords" in indicator for indicator in minimal_indicators):
                    quality_score -= 20  # Heavy penalty for parked domains
            
            # Clamp to 0-100 range
            quality_score = max(0, min(100, quality_score))
            
            log.info(f"📊 Content quality score calculated: {quality_score}")
            return quality_score
            
        except Exception as e:
            log.warning(f"⚠️ Error calculating content quality score: {e}")
            return 50  # Default score

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
    async def analyze_trust(self, url: str) -> Dict[str, Any]:
        try:
            domain = urlparse(url).hostname
            trust = {
                "ssl": False,
                "securityHeaders": [],
                "domainAge": "unknown",
                "score": 0,
                "realData": {"ssl": True, "securityHeaders": True, "domainAge": False},
                "warnings": [],
            }

            # SSL
            try:
                ssl_resp = requests.get(
                    f"https://{domain}", timeout=10, allow_redirects=True
                )
                trust["ssl"] = ssl_resp.status_code < 400
                trust["score"] += 30 if trust["ssl"] else 0
            except Exception as e:
                trust["warnings"].append(f"SSL check failed: {e}")

            # Security headers
            try:
                hdr_resp = requests.get(
                    f"https://{domain}", timeout=10, allow_redirects=True
                )
                headers = {k.lower(): v for k, v in hdr_resp.headers.items()}

                sec_headers = [
                    "x-frame-options",
                    "x-content-type-options",
                    "strict-transport-security",
                    "content-security-policy",
                    "x-xss-protection",
                ]
                trust["securityHeaders"] = [h for h in sec_headers if h in headers]
                trust["score"] += min(40, len(trust["securityHeaders"]) * 8)
            except Exception as e:
                trust["warnings"].append(f"Security headers check failed: {e}")

            # Domain age
            if self.domain_service:
                try:
                    analysis = await self.domain_service.analyze_domain(domain)
                    age = analysis["domainAge"]
                    trust["domainAge"] = (
                        f"{age['years']} years, {age['months']} months, {age['days']} days"
                    )
                    trust["realData"]["domainAge"] = True

                    if age["years"] >= 10:
                        trust["score"] += 15
                    elif age["years"] >= 5:
                        trust["score"] += 12
                    elif age["years"] >= 2:
                        trust["score"] += 8
                    elif age["years"] >= 1:
                        trust["score"] += 5
                    else:
                        trust["score"] += 2

                except Exception as e:
                    trust["warnings"].append(f"Domain age analysis failed: {e}")
                    trust["domainAge"] = self.estimate_domain_age(domain)
                    trust["realData"]["domainAge"] = False
                    trust["score"] += 3
            else:
                trust["domainAge"] = self.estimate_domain_age(domain)
                trust["realData"]["domainAge"] = False
                trust["score"] += 3
                trust["warnings"].append("Domain age estimation only - service not available")

            return trust

        except Exception as e:
            raise RuntimeError(f"Trust analysis error: {e}") from e

    # ------------------------------------------------------------------ #
    def estimate_domain_age(self, domain: str) -> str:
        if len(domain) <= 8 and "-" not in domain and "2" not in domain:
            return "5+ years (estimated)"
        if any(year in domain for year in ["2020", "2021", "2022"]):
            return "2-3 years (estimated)"
        if "new" in domain or "latest" in domain:
            return "1-2 years (estimated)"
        return "3-5 years (estimated)"

    # ------------------------------------------------------------------ #
    async def analyze_cro(self, url: str) -> Dict[str, Any]:
        try:
            mobile_data = await self.run_page_speed_analysis(url, "mobile")
            desktop_data = await self.run_page_speed_analysis(url, "desktop")

            cro = {
                "mobileFriendly": mobile_data["mobileUsability"]["mobileFriendly"],
                "mobileUsabilityScore": mobile_data["mobileUsability"]["score"],
                "mobileIssues": mobile_data["mobileUsability"]["issues"],
                "pageSpeed": {
                    "mobile": mobile_data["scores"]["performance"],
                    "desktop": desktop_data["scores"]["performance"],
                    "average": round(
                        (
                            mobile_data["scores"]["performance"]
                            + desktop_data["scores"]["performance"]
                        )
                        / 2
                    ),
                },
                "userExperience": {
                    "loadingTime": self.calculate_ux_score(mobile_data["coreWebVitals"]),
                    "interactivity": self.calculate_interactivity_score(
                        mobile_data["serverMetrics"]
                    ),
                    "visualStability": self.calculate_visual_stability_score(
                        mobile_data["coreWebVitals"]
                    ),
                },
                "score": 0,
                "realData": True,
            }

            cro["score"] = round(
                cro["mobileUsabilityScore"] * 0.3
                + cro["pageSpeed"]["average"] * 0.4
                + cro["userExperience"]["loadingTime"] * 0.3
            )

            return cro

        except Exception as e:
            raise RuntimeError(f"CRO analysis error: {e}") from e

    # ------------------------------------------------------------------ #
    def calculate_ux_score(self, cwv: Dict[str, Any]) -> int:
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

    # ------------------------------------------------------------------ #
    def calculate_interactivity_score(self, sm: Dict[str, Any]) -> int:
        score = 100
        tti = (sm.get("timeToInteractive") or {}).get("value") or 0
        if tti > 5000:
            score -= 30
        elif tti > 3000:
            score -= 15

        tbt = (sm.get("totalBlockingTime") or {}).get("value") or 0
        if tbt > 600:
            score -= 25
        elif tbt > 300:
            score -= 10

        return max(0, score)

    # ------------------------------------------------------------------ #
    def calculate_visual_stability_score(self, cwv: Dict[str, Any]) -> int:
        cls = (cwv.get("cumulativeLayoutShift") or {}).get("value") or 0
        if cls <= 0.1:
            return 100
        if cls <= 0.25:
            return 80
        return 50

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
                    
                    analysis_time = time.time() - start_time
                    result["analysis_time"] = analysis_time
                    result["url"] = url
                    
                    # Update statistics
                    self.analysis_stats["total_analyses"] += 1
                    if result.get("success", False):
                        self.analysis_stats["successful_analyses"] += 1
                    else:
                        self.analysis_stats["failed_analyses"] += 1
                    
                    return result
                    
                except Exception as e:
                    self.analysis_stats["total_analyses"] += 1
                    self.analysis_stats["failed_analyses"] += 1
                    
                    return {
                        "success": False,
                        "error": f"Analysis failed: {str(e)}",
                        "error_code": "BATCH_ANALYSIS_FAILED",
                        "context": "batch_analysis",
                        "url": url,
                        "analysis_time": 0
                    }
        
        # Run all analyses concurrently
        tasks = [run_single_analysis(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions and convert to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": f"Analysis failed: {str(result)}",
                    "error_code": "BATCH_ANALYSIS_FAILED",
                    "context": "batch_analysis",
                    "url": urls[i],
                    "analysis_time": 0
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
        Run comprehensive website analysis including all available metrics.
        
        Args:
            url: URL to analyze
            strategy: Analysis strategy ('mobile' or 'desktop')
            
        Returns:
            Dictionary with comprehensive analysis results
        """
        try:
            start_time = time.time()
            
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
            
            # Initialize result
            result = {
                "url": url,
                "strategy": strategy,
                "analysis_timestamp": time.time(),
                "success": True,
                "scores": {},
                "details": {},
                "services_used": []
            }
            
            # 1. PageSpeed Analysis
            try:
                pagespeed_result = await self.run_page_speed_analysis(url, strategy)
                result["details"]["pagespeed"] = pagespeed_result
                result["scores"].update(pagespeed_result["scores"])
                result["services_used"].append("pagespeed")
            except Exception as e:
                log.warning(f"PageSpeed analysis failed for {url}: {e}")
                result["scores"].update({
                    "performance": 0,
                    "accessibility": 0,
                    "bestPractices": 0,
                    "seo": 0
                })
            
            # 2. Trust Analysis
            try:
                trust_result = await self.analyze_trust(url)
                result["details"]["trust"] = trust_result
                result["scores"]["trust"] = trust_result.get("score", 0)
                result["services_used"].append("trust")
            except Exception as e:
                log.warning(f"Trust analysis failed for {url}: {e}")
                result["scores"]["trust"] = 0
            
            # 3. CRO Analysis
            try:
                cro_result = await self.analyze_cro(url)
                result["details"]["cro"] = cro_result
                result["scores"]["cro"] = cro_result.get("score", 0)
                result["services_used"].append("cro")
            except Exception as e:
                log.warning(f"CRO analysis failed for {url}: {e}")
                result["scores"]["cro"] = 0
            
            # 4. Uptime Analysis
            try:
                uptime_result = await self.analyze_uptime(url)
                result["details"]["uptime"] = uptime_result
                result["scores"]["uptime"] = uptime_result.get("score", 0)
                result["services_used"].append("uptime")
            except Exception as e:
                log.warning(f"Uptime analysis failed for {url}: {e}")
                result["scores"]["uptime"] = 0
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(result["scores"])
            result["scores"]["overall"] = overall_score
            
            # Add analysis metadata
            analysis_time = time.time() - start_time
            result["analysis_time"] = analysis_time
            
            # Record successful request
            self.rate_limiter.record_request('comprehensive_speed', True)
            
            return result
            
        except Exception as e:
            # Record failed request
            self.rate_limiter.record_request('comprehensive_speed', False)
            
            log.error(f"Comprehensive analysis failed for {url}: {e}")
            return {
                "success": False,
                "error": f"Comprehensive analysis failed: {str(e)}",
                "error_code": "ANALYSIS_FAILED",
                "context": "comprehensive_analysis",
                "url": url
            }
    
    def _calculate_overall_score(self, scores: Dict[str, Any]) -> float:
        """
        Calculate overall score with business impact weighting.
        """
        try:
            # Business impact weighting
            weights = {
                'performance': 0.25,      # Speed affects user experience and SEO
                'accessibility': 0.15,    # Legal compliance and user inclusivity
                'bestPractices': 0.15,    # Security and reliability
                'seo': 0.15,              # Search engine visibility
                'trust': 0.20,            # Critical for business credibility
                'cro': 0.10               # Revenue optimization
            }
            
            overall_score = 0.0
            total_weight = 0.0
            
            for metric, weight in weights.items():
                if metric in scores and scores[metric] is not None:
                    overall_score += scores[metric] * weight
                    total_weight += weight
            
            # Normalize score if some metrics are missing
            if total_weight > 0:
                final_score = overall_score / total_weight
            else:
                final_score = 0.0
            
            return round(final_score, 2)
            
        except Exception as e:
            log.error(f"Error calculating overall score: {e}")
            return 0.0
    
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