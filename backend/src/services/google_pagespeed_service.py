"""
Google PageSpeed API service for website performance analysis.
Replaces the previous Lighthouse service with Google's PageSpeed Insights API v5.
"""

import httpx
import time
import logging
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import get_api_config
from src.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class GooglePageSpeedService:
    """Service for analyzing website performance using Google PageSpeed Insights API."""
    
    def __init__(self):
        """Initialize the PageSpeed service."""
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        
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
            
            if not self.rate_limiter.check_rate_limit('google_pagespeed', 'minute'):
                return False
            
            if not self.rate_limiter.check_rate_limit('google_pagespeed_daily', 'day'):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating PageSpeed request: {e}")
            return False
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def run_pagespeed_audit(
        self,
        website_url: str,
        business_id: str,
        run_id: str,
        strategy: str = "desktop",
        categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Run a PageSpeed audit using Google PageSpeed Insights API."""
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
                'strategy': strategy
            }
            
            if categories:
                params['category'] = ','.join(categories)
            
            timeout = httpx.Timeout(
                connect=self.api_config.PAGESPEED_CONNECT_TIMEOUT_SECONDS,
                read=self.api_config.PAGESPEED_READ_TIMEOUT_SECONDS
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
            return {
                "success": False,
                "error": f"PageSpeed API HTTP error: {e.response.status_code}",
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
            
            performance_score = categories.get('performance', {}).get('score', 0)
            accessibility_score = categories.get('accessibility', {}).get('score', 0)
            best_practices_score = categories.get('best-practices', {}).get('score', 0)
            seo_score = categories.get('seo', {}).get('score', 0)
            
            overall_score = (
                performance_score * 0.4 +
                accessibility_score * 0.2 +
                best_practices_score * 0.2 +
                seo_score * 0.2
            )
            
            audits = lighthouse_result.get('audits', {})
            
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
                    "best_practices": round(best_practices_score, 3),
                    "seo": round(seo_score, 3)
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
