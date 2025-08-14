"""
Rate limiting middleware for Yelp Fusion API endpoints.
Implements per-endpoint rate limiting and monitoring.
"""

import time
from typing import Callable, Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.services import RateLimiter
from src.core.config import get_api_config


class YelpFusionRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware specifically for Yelp Fusion API endpoints."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.rate_limiter = RateLimiter()
        self.api_config = get_api_config()
        self.yelp_endpoints = {
            "/api/v1/business-search/yelp": "yelp_fusion",
            "/api/v1/business-search/yelp/": "yelp_fusion"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request with rate limiting checks."""
        # Check if this is a Yelp Fusion endpoint
        endpoint = self._get_endpoint_key(request.url.path)
        
        if endpoint and endpoint in self.yelp_endpoints:
            api_name = self.yelp_endpoints[endpoint]
            
            try:
                # Check rate limiting
                can_request, reason = self.rate_limiter.can_make_request(api_name)
                
                if not can_request:
                    # Get rate limit info for the error response
                    try:
                        rate_limit_info = self.rate_limiter.get_rate_limit_info(api_name)
                    except Exception:
                        rate_limit_info = None
                    
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": "Rate limit exceeded",
                            "message": reason,
                            "rate_limit_info": rate_limit_info,
                            "retry_after": self._calculate_retry_after(rate_limit_info) if rate_limit_info else 3600,
                            "endpoint": request.url.path
                        }
                    )
                
                # Add rate limit headers to response
                response = await call_next(request)
                try:
                    self._add_rate_limit_headers(response, api_name)
                except Exception:
                    # If adding headers fails, just continue without them
                    pass
                
                return response
                
            except Exception as e:
                # If rate limiting fails, allow the request to pass through (fail open)
                # Log the error for debugging
                print(f"Rate limiting error for {api_name}: {str(e)}")
                
                response = await call_next(request)
                return response
        
        # For non-Yelp endpoints, just pass through
        return await call_next(request)
    
    def _get_endpoint_key(self, path: str) -> str:
        """Get the endpoint key for rate limiting."""
        for endpoint in self.yelp_endpoints:
            if path.startswith(endpoint):
                return endpoint
        return ""
    
    def _add_rate_limit_headers(self, response: Response, api_name: str):
        """Add rate limit headers to the response."""
        rate_limit_info = self.rate_limiter.get_rate_limit_info(api_name)
        if rate_limit_info:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
            response.headers["X-RateLimit-Reset"] = rate_limit_info["reset_time"]
            
            # Parse timestamp for the timestamp header, handling microseconds
            try:
                reset_time_str = rate_limit_info["reset_time"]
                if "." in reset_time_str:
                    # Has microseconds, try parsing with microseconds
                    try:
                        reset_time = time.mktime(time.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%S.%f"))
                    except ValueError:
                        # Fall back to parsing without microseconds
                        reset_time = time.mktime(time.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%S"))
                else:
                    # No microseconds, parse normally
                    reset_time = time.mktime(time.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%S"))
                
                response.headers["X-RateLimit-Reset-Timestamp"] = str(int(reset_time))
            except (ValueError, TypeError):
                # If parsing fails, use current time + 1 hour as fallback
                response.headers["X-RateLimit-Reset-Timestamp"] = str(int(time.time() + 3600))
    
    def _calculate_retry_after(self, rate_limit_info: Dict[str, Any]) -> int:
        """Calculate retry-after value in seconds."""
        if not rate_limit_info or "reset_time" not in rate_limit_info:
            return 3600  # Default to 1 hour
        
        try:
            # Try to parse the timestamp with microseconds first
            reset_time_str = rate_limit_info["reset_time"]
            
            # Handle different timestamp formats
            if "." in reset_time_str:
                # Has microseconds, try parsing with microseconds
                try:
                    reset_time = time.mktime(time.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%S.%f"))
                except ValueError:
                    # Fall back to parsing without microseconds
                    reset_time = time.mktime(time.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%S"))
            else:
                # No microseconds, parse normally
                reset_time = time.mktime(time.strptime(reset_time_str, "%Y-%m-%dT%H:%M:%S"))
            
            retry_after = int(reset_time - time.time())
            return max(retry_after, 60)  # Minimum 1 minute
        except (ValueError, TypeError):
            return 3600  # Default to 1 hour
