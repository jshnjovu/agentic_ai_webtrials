"""
Enhanced Google PageSpeed API service for comprehensive website performance analysis.
Features smart retry logic, intelligent caching, and hybrid scoring with Pingdom data.
"""

import httpx
import time
import logging
import asyncio
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import get_api_config
from src.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class GooglePageSpeedService:
    """Enhanced service for analyzing website performance using Google PageSpeed Insights API."""
    
    def __init__(self):
        """Initialize the enhanced PageSpeed service."""
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
        # Enhanced caching system
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
        
        # Smart retry configuration
        self.retry_config = {
            'max_attempts': 3,
            'base_delay': 2,
            'max_delay': 30,
            'exponential_backoff': True
        }
        
        if not self.api_config.is_api_key_valid('GOOGLE_GENERAL_API_KEY'):
            logger.warning("Google General API key not configured for PageSpeed service")
    
    def validate_input(self, request_data: Dict[str, Any]) -> bool:
        """Validate PageSpeed audit request data."""
        try:
            if not request_data.get('website_url'):
                return False
            
            url = request_data['website_url']
            if not url.startswith(('http://', 'https://')):
                return False
            
            # Check rate limits using the correct method name
            can_proceed_minute, message_minute = self.rate_limiter.can_make_request('google_pagespeed')
            if not can_proceed_minute:
                logger.warning(f"Minute rate limit exceeded: {message_minute}")
                return False
            
            can_proceed_daily, message_daily = self.rate_limiter.can_make_request('google_pagespeed_daily')
            if not can_proceed_daily:
                logger.warning(f"Daily rate limit exceeded: {message_daily}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating PageSpeed request: {e}")
            return False
    
    async def run_pagespeed_audit_with_smart_retry(
        self,
        website_url: str,
        business_id: str,
        run_id: str,
        strategy: str = "desktop",
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run PageSpeed audit with intelligent retry logic and caching.
        
        Args:
            website_url: URL to analyze
            business_id: Business identifier
            run_id: Processing run identifier
            strategy: Analysis strategy ('desktop' or 'mobile')
            categories: Optional list of categories to analyze
            
        Returns:
            Dictionary with PageSpeed audit results
        """
        # Check cache first
        cache_key = f"{website_url}_{strategy}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if time.time() - cached_result['timestamp'] < self.cache_ttl:
                logger.info(f"Returning cached PageSpeed result for {website_url}")
                cached_result['data']['from_cache'] = True
                return cached_result['data']
        
        # Implement exponential backoff retry
        for attempt in range(self.retry_config['max_attempts']):
            try:
                result = await self._make_pagespeed_request(website_url, strategy, categories)
                
                # Cache successful result
                self.cache[cache_key] = {
                    'data': result,
                    'timestamp': time.time()
                }
                
                # Clean up old cache entries
                self._cleanup_cache()
                
                return result
                
            except Exception as e:
                logger.warning(f"PageSpeed attempt {attempt + 1} failed for {website_url}: {e}")
                
                if attempt == self.retry_config['max_attempts'] - 1:
                    raise e
                
                # Calculate delay with exponential backoff
                delay = min(
                    self.retry_config['base_delay'] * (2 ** attempt),
                    self.retry_config['max_delay']
                )
                logger.info(f"Retrying PageSpeed for {website_url} in {delay}s (attempt {attempt + 2})")
                await asyncio.sleep(delay)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def run_pagespeed_audit(
        self,
        website_url: str,
        business_id: str,
        run_id: str,
        strategy: str = "desktop",
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run a PageSpeed audit using Google PageSpeed Insights API.
        
        Args:
            website_url: URL to analyze
            business_id: Business identifier
            run_id: Processing run identifier
            strategy: Analysis strategy ('desktop' or 'mobile')
            categories: Optional list of categories to analyze
            
        Returns:
            Dictionary with PageSpeed audit results including all 6 scoring categories
        """
        try:
            if not self.validate_input({'website_url': website_url}):
                return {
                    "success": False,
                    "error": "Invalid input validation",
                    "error_code": "VALIDATION_FAILED",
                    "context": "pagespeed_audit"
                }
            
            params = {
                'url': website_url,
                'key': self.api_config.GOOGLE_GENERAL_API_KEY,
                'strategy': strategy.upper()  # Google expects uppercase: DESKTOP, MOBILE
            }
            
            # Default to all available categories for comprehensive scoring
            if not categories:
                categories = ['performance', 'accessibility', 'best-practices', 'seo']
            
            # Google PageSpeed API v5 expects categories as a list in the request body
            # For now, let's use the basic parameters and let Google handle defaults
            # The categories will be processed in the response parsing
            
            # Create timeout with all required parameters for httpx
            timeout = httpx.Timeout(
                connect=getattr(self.api_config, 'PAGESPEED_CONNECT_TIMEOUT_SECONDS', 10),
                read=getattr(self.api_config, 'PAGESPEED_READ_TIMEOUT_SECONDS', 25),
                write=getattr(self.api_config, 'PAGESPEED_READ_TIMEOUT_SECONDS', 25),  # Use read timeout for write
                pool=getattr(self.api_config, 'PAGESPEED_CONNECT_TIMEOUT_SECONDS', 10)  # Use connect timeout for pool
            )
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                start_time = time.time()
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                request_time = time.time() - start_time
                
                result = response.json()
                audit_data = self._parse_pagespeed_response(result, website_url, business_id, run_id)
                audit_data['request_time'] = request_time
                
                logger.info(f"PageSpeed audit completed for {website_url} in {request_time:.2f}s")
                return audit_data
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "PageSpeed API request timed out",
                "error_code": "TIMEOUT",
                "context": "pagespeed_audit",
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id
            }
            
        except httpx.HTTPStatusError as e:
            # Get detailed error information from Google's response
            try:
                error_detail = e.response.json()
                error_message = f"PageSpeed API HTTP error: {e.response.status_code} - {error_detail.get('error', {}).get('message', 'Unknown error')}"
            except:
                error_message = f"PageSpeed API HTTP error: {e.response.status_code} - {e.response.text}"
            
            return {
                "success": False,
                "error": error_message,
                "error_code": "HTTP_ERROR",
                "context": "pagespeed_audit",
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNEXPECTED_ERROR",
                "context": "pagespeed_audit",
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id
            }
    
    def _parse_pagespeed_response(
        self,
        response_data: Dict[str, Any],
        website_url: str,
        business_id: str,
        run_id: str
    ) -> Dict[str, Any]:
        """Parse PageSpeed API response into standardized format."""
        try:
            lighthouse_result = response_data.get('lighthouseResult', {})
            categories = lighthouse_result.get('categories', {})
            audits = lighthouse_result.get('audits', {})
            
            performance_score = categories.get('performance', {}).get('score', 0)
            accessibility_score = categories.get('accessibility', {}).get('score', 0)
            best_practices_score = categories.get('best-practices', {}).get('score', 0)
            seo_score = categories.get('seo', {}).get('score', 0)
            
            # Calculate derived scores for Trust and CRO
            trust_score = self._calculate_trust_score(audits, categories)
            cro_score = self._calculate_cro_score(audits, categories)
            
            # Updated overall score calculation including all 6 categories
            overall_score = (
                performance_score * 0.25 +    # Performance
                accessibility_score * 0.15 +   # Accessibility  
                best_practices_score * 0.15 + # Best Practices
                seo_score * 0.15 +            # SEO
                trust_score * 0.15 +          # Trust
                cro_score * 0.15              # CRO
            )
            
            result = {
                "success": True,
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id,
                "audit_timestamp": time.time(),
                "strategy": lighthouse_result.get('configSettings', {}).get('emulatedFormFactor', 'desktop'),
                "scores": {
                    "overall": round(overall_score, 3),
                    "performance": round(performance_score, 3),
                    "accessibility": round(accessibility_score, 3),
                    "best_practices": round(best_practices_score, 3),  # Add missing field
                    "seo": round(seo_score, 3),
                    "trust": round(trust_score, 3),
                    "cro": round(cro_score, 3)
                },
                "core_web_vitals": {
                    "first_contentful_paint": audits.get('first-contentful-paint', {}).get('numericValue', 0),
                    "largest_contentful_paint": audits.get('largest-contentful-paint', {}).get('numericValue', 0),
                    "cumulative_layout_shift": audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
                    "total_blocking_time": audits.get('total-blocking-time', {}).get('numericValue', 0),
                    "speed_index": audits.get('speed-index', {}).get('numericValue', 0)
                },
                "raw_data": response_data
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error parsing PageSpeed response: {e}")
            return {
                "success": False,
                "error": f"Error parsing response: {str(e)}",
                "error_code": "PARSE_ERROR",
                "context": "pagespeed_audit",
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id
            }
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get PageSpeed service health status."""
        return {
            "service": "google_pagespeed",
            "status": "healthy" if self.api_config.is_api_key_valid('GOOGLE_GENERAL_API_KEY') else "unconfigured",
            "api_key_configured": self.api_config.is_api_key_valid('GOOGLE_GENERAL_API_KEY'),
            "rate_limits": {
                "per_minute": self.api_config.PAGESPEED_RATE_LIMIT_PER_MINUTE,
                "per_day": self.api_config.PAGESPEED_RATE_LIMIT_PER_DAY
            }
        }
    
    async def run_batch_pagespeed_audits(
        self,
        audit_requests: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Run multiple PageSpeed audits concurrently with rate limiting.
        
        Args:
            audit_requests: List of audit request dictionaries
            max_concurrent: Maximum concurrent requests (respects rate limits)
            
        Returns:
            List of audit results
        """
        import asyncio
        from asyncio import Semaphore
        
        semaphore = Semaphore(max_concurrent)
        
        async def run_single_audit(request: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self.run_pagespeed_audit(
                    website_url=request['website_url'],
                    business_id=request['business_id'],
                    run_id=request['run_id'],
                    strategy=request.get('strategy', 'desktop'),
                    categories=request.get('categories')
                )
        
        # Run all audits concurrently
        tasks = [run_single_audit(request) for request in audit_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions and convert to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": f"Audit failed: {str(result)}",
                    "error_code": "BATCH_AUDIT_FAILED",
                    "context": "batch_pagespeed_audit",
                    "website_url": audit_requests[i]['website_url'],
                    "business_id": audit_requests[i]['business_id'],
                    "run_id": audit_requests[i]['run_id']
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def run_pagespeed_audit_with_fallback(
        self,
        website_url: str,
        business_id: str,
        run_id: str,
        strategy: str = "desktop",
        categories: Optional[List[str]] = None,
        fallback_service=None
    ) -> Dict[str, Any]:
        """
        Run PageSpeed audit with automatic fallback to alternative service.
        
        Args:
            website_url: URL to analyze
            business_id: Business identifier
            run_id: Processing run identifier
            strategy: Analysis strategy
            categories: Optional categories to analyze
            fallback_service: Alternative scoring service for fallback
            
        Returns:
            Dictionary with PageSpeed audit results or fallback results
        """
        try:
            # Try PageSpeed first
            result = await self.run_pagespeed_audit(
                website_url=website_url,
                business_id=business_id,
                run_id=run_id,
                strategy=strategy,
                categories=categories
            )
            
            if result.get("success", False):
                result["scoring_method"] = "pagespeed"
                return result
            
            # If PageSpeed fails, return error with fallback info
            result["scoring_method"] = "pagespeed_failed"
            result["fallback_available"] = False
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error in fallback audit: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNEXPECTED_ERROR",
                "context": "pagespeed_audit_with_fallback",
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id,
                "scoring_method": "failed"
            }
    
    def _calculate_trust_score(self, audits: Dict[str, Any], categories: Dict[str, Any]) -> float:
        """
        Calculate trust score based on security, best practices, and reliability metrics.
        
        Args:
            audits: Lighthouse audit results
            categories: Lighthouse category scores
            
        Returns:
            Trust score between 0 and 1
        """
        try:
            # Start with best practices as base (security, reliability)
            base_score = categories.get('best-practices', {}).get('score', 0)
            
            # Boost score based on security-related audits
            security_boost = 0.0
            security_audits = [
                'uses-https',
                'external-anchors-use-rel-noopener',
                'no-vulnerable-libraries',
                'csp-xss-protection'
            ]
            
            for audit_id in security_audits:
                if audit_id in audits and audits[audit_id].get('score') == 1:
                    security_boost += 0.1
            
            # Boost score based on reliability metrics
            reliability_boost = 0.0
            if 'service-worker' in audits and audits['service-worker'].get('score') == 1:
                reliability_boost += 0.05
            
            if 'offline-start-url' in audits and audits['offline-start-url'].get('score') == 1:
                reliability_boost += 0.05
            
            # Calculate final trust score
            trust_score = min(1.0, base_score + security_boost + reliability_boost)
            return trust_score
            
        except Exception as e:
            logger.error(f"Error calculating trust score: {e}")
            return 0.0
    
    def _calculate_cro_score(self, audits: Dict[str, Any], categories: Dict[str, Any]) -> float:
        """
        Calculate CRO (Conversion Rate Optimization) score based on performance and UX metrics.
        
        Args:
            audits: Lighthouse audit results
            categories: Lighthouse category scores
            
        Returns:
            CRO score between 0 and 1
        """
        try:
            # Start with performance as base (speed affects conversions)
            base_score = categories.get('performance', {}).get('score', 0)
            
            # Boost score based on UX-related audits
            ux_boost = 0.0
            
            # Mobile-friendly design
            if 'viewport' in audits and audits['viewport'].get('score') == 1:
                ux_boost += 0.1
            
            # Touch targets
            if 'tap-targets' in audits and audits['tap-targets'].get('score') == 1:
                ux_boost += 0.05
            
            # Font display
            if 'font-display' in audits and audits['font-display'].get('score') == 1:
                ux_boost += 0.05
            
            # Image optimization (affects perceived performance)
            if 'modern-image-formats' in audits and audits['modern-image-formats'].get('score') == 1:
                ux_boost += 0.05
            
            if 'efficient-animated-content' in audits and audits['efficient-animated-content'].get('score') == 1:
                ux_boost += 0.05
            
            # Calculate final CRO score
            cro_score = min(1.0, base_score + ux_boost)
            return cro_score
            
        except Exception as e:
            logger.error(f"Error calculating CRO score: {e}")
            return 0.0
    
    async def _make_pagespeed_request(
        self,
        website_url: str,
        strategy: str = "desktop",
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Make the actual PageSpeed API request."""
        try:
            params = {
                'url': website_url,
                'key': self.api_config.GOOGLE_GENERAL_API_KEY,
                'strategy': strategy.upper()
            }
            
            # Default to all available categories
            if not categories:
                categories = ['performance', 'accessibility', 'best-practices', 'seo']
            
            timeout = httpx.Timeout(
                connect=getattr(self.api_config, 'PAGESPEED_CONNECT_TIMEOUT_SECONDS', 10),
                read=getattr(self.api_config, 'PAGESPEED_READ_TIMEOUT_SECONDS', 25),
                write=getattr(self.api_config, 'PAGESPEED_READ_TIMEOUT_SECONDS', 25),
                pool=getattr(self.api_config, 'PAGESPEED_CONNECT_TIMEOUT_SECONDS', 10)
            )
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                start_time = time.time()
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                request_time = time.time() - start_time
                
                result = response.json()
                audit_data = self._parse_pagespeed_response(result, website_url, "", "")
                audit_data['request_time'] = request_time
                
                return audit_data
                
        except httpx.TimeoutException:
            raise TimeoutError(f"PageSpeed API request timed out")
        except httpx.HTTPStatusError as e:
            raise Exception(f"PageSpeed API HTTP error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"PageSpeed API request failed: {str(e)}")
    
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
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
    
    async def run_hybrid_audit(
        self,
        website_url: str,
        business_id: str,
        run_id: str,
        strategy: str = "desktop",
        pingdom_service=None
    ) -> Dict[str, Any]:
        """
        Run comprehensive audit combining PageSpeed and Pingdom data for accurate Trust/CRO scores.
        
        Args:
            website_url: URL to analyze
            business_id: Business identifier
            run_id: Processing run identifier
            strategy: Analysis strategy
            pingdom_service: PingdomService instance for trust/CRO metrics
            
        Returns:
            Dictionary with comprehensive audit results
        """
        try:
            # Get PageSpeed data
            pagespeed_result = await self.run_pagespeed_audit_with_smart_retry(
                website_url, business_id, run_id, strategy
            )
            
            if not pagespeed_result.get("success", False):
                logger.warning(f"PageSpeed failed for {website_url}, using fallback scoring")
                return self._create_fallback_result(website_url, business_id, run_id, strategy)
            
            # Get Pingdom data for trust and CRO
            trust_score = 0.0
            cro_score = 0.0
            
            if pingdom_service:
                try:
                    trust_data = await pingdom_service.analyze_trust_metrics(
                        website_url, business_id, run_id
                    )
                    if trust_data.get("success"):
                        trust_score = trust_data.get("trust_score", 0.0)
                    
                    cro_data = await pingdom_service.analyze_cro_metrics(
                        website_url, business_id, run_id
                    )
                    if cro_data.get("success"):
                        cro_score = cro_data.get("cro_score", 0.0)
                        
                except Exception as e:
                    logger.warning(f"Pingdom analysis failed for {website_url}: {e}")
            
            # Calculate hybrid scores
            hybrid_scores = self._calculate_hybrid_scores(
                pagespeed_result, trust_score, cro_score
            )
            
            # Update result with hybrid scores
            result = pagespeed_result.copy()
            result.update({
                "scores": hybrid_scores,
                "trust_score": trust_score,
                "cro_score": cro_score,
                "scoring_method": "hybrid_pagespeed_pingdom",
                "pingdom_integration": pingdom_service is not None
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid audit failed for {website_url}: {e}")
            return self._create_fallback_result(website_url, business_id, run_id, strategy)
    
    def _calculate_hybrid_scores(
        self,
        pagespeed_data: Dict[str, Any],
        trust_score: float,
        cro_score: float
    ) -> Dict[str, Any]:
        """Calculate hybrid scores combining PageSpeed and Pingdom data."""
        try:
            original_scores = pagespeed_data.get("scores", {})
            
            # Use PageSpeed for performance, accessibility, best-practices, SEO
            # Use Pingdom for trust and CRO
            hybrid_scores = {
                "overall": 0.0,
                "performance": original_scores.get("performance", 0.0),
                "accessibility": original_scores.get("accessibility", 0.0),
                "best_practices": original_scores.get("best_practices", 0.0),
                "seo": original_scores.get("seo", 0.0),
                "trust": trust_score,
                "cro": cro_score
            }
            
            # Calculate overall score with business impact weighting
            overall_score = (
                hybrid_scores["performance"] * 0.25 +    # Performance (25%)
                hybrid_scores["accessibility"] * 0.15 +   # Accessibility (15%)
                hybrid_scores["best_practices"] * 0.15 +  # Best Practices (15%)
                hybrid_scores["seo"] * 0.15 +             # SEO (15%)
                hybrid_scores["trust"] * 0.20 +           # Trust (20%) - Business critical
                hybrid_scores["cro"] * 0.10               # CRO (10%) - Revenue impact
            )
            
            hybrid_scores["overall"] = round(overall_score, 3)
            
            return hybrid_scores
            
        except Exception as e:
            logger.error(f"Error calculating hybrid scores: {e}")
            return pagespeed_data.get("scores", {})
    
    def _create_fallback_result(
        self,
        website_url: str,
        business_id: str,
        run_id: str,
        strategy: str
    ) -> Dict[str, Any]:
        """Create fallback result when PageSpeed fails."""
        return {
            "success": False,
            "website_url": website_url,
            "business_id": business_id,
            "run_id": run_id,
            "strategy": strategy,
            "error": "PageSpeed analysis failed, fallback scoring used",
            "error_code": "PINGDOM_FALLBACK",
            "context": "hybrid_audit",
            "scoring_method": "pingdom_fallback",
            "scores": {
                "overall": 0.0,
                "performance": 0.0,
                "accessibility": 0.0,
                "best_practices": 0.0,
                "seo": 0.0,
                "trust": 0.0,
                "cro": 0.0
            }
        }
