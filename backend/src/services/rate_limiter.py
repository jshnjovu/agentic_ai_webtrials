"""
Rate limiting service with circuit breaker pattern.
Implements rate limiting for external APIs and circuit breaker for failure handling.
"""

import time
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from ..core.base_service import BaseService
from ..core.config import get_api_config


class RateLimiter(BaseService):
    """Rate limiting service with circuit breaker pattern."""
    
    def __init__(self):
        super().__init__("RateLimiter")
        self.api_config = get_api_config()
        self._rate_limits: Dict[str, Dict] = {}
        self._circuit_breakers: Dict[str, Dict] = {}
        self._setup_rate_limits()
    
    def _setup_rate_limits(self):
        """Initialize rate limiting configuration for all APIs."""
        # Google Places API - requests per minute
        self._rate_limits["google_places"] = {
            "limit": self.api_config.GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # 60 seconds
            "requests": [],
            "last_reset": time.time()
        }
        
        # Yelp Fusion API - requests per day
        self._rate_limits["yelp_fusion"] = {
            "limit": self.api_config.YELP_FUSION_RATE_LIMIT_PER_DAY,
            "window": 86400,  # 24 hours
            "requests": [],
            "last_reset": time.time()
        }
        
        # Initialize circuit breakers
        for api_name in self._rate_limits.keys():
            self._circuit_breakers[api_name] = {
                "failures": 0,
                "last_failure": None,
                "state": "CLOSED",  # CLOSED, OPEN, HALF_OPEN
                "threshold": self.api_config.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                "recovery_timeout": self.api_config.CIRCUIT_BREAKER_RECOVERY_TIMEOUT
            }
    
    def _cleanup_old_requests(self, api_name: str):
        """Remove old requests outside the rate limit window."""
        rate_limit = self._rate_limits[api_name]
        current_time = time.time()
        window_start = current_time - rate_limit["window"]
        
        # Remove requests older than the window
        rate_limit["requests"] = [
            req_time for req_time in rate_limit["requests"] 
            if req_time >= window_start
        ]
        
        # Update last reset time
        if current_time - rate_limit["last_reset"] >= rate_limit["window"]:
            rate_limit["last_reset"] = current_time
    
    def can_make_request(self, api_name: str, run_id: Optional[str] = None) -> Tuple[bool, str]:
        """
        Check if a request can be made to the specified API.
        
        Returns:
            Tuple of (can_make_request, reason)
        """
        if api_name not in self._rate_limits:
            return False, f"Unknown API: {api_name}"
        
        # Check circuit breaker state
        circuit_state = self._check_circuit_breaker(api_name)
        if circuit_state != "CLOSED":
            return False, f"Circuit breaker is {circuit_state}"
        
        # Clean up old requests
        self._cleanup_old_requests(api_name)
        
        # Check rate limit
        rate_limit = self._rate_limits[api_name]
        current_requests = len(rate_limit["requests"])
        
        if current_requests >= rate_limit["limit"]:
            return False, f"Rate limit exceeded: {current_requests}/{rate_limit['limit']}"
        
        return True, "OK"
    
    def record_request(self, api_name: str, success: bool, run_id: Optional[str] = None):
        """Record a request to the specified API."""
        if api_name not in self._rate_limits:
            return
        
        current_time = time.time()
        
        # Record the request
        self._rate_limits[api_name]["requests"].append(current_time)
        
        # Update circuit breaker
        if not success:
            self._record_failure(api_name, current_time)
        else:
            self._record_success(api_name)
        
        self.log_operation(
            f"Recorded {'successful' if success else 'failed'} request to {api_name}",
            run_id=run_id,
            business_id=None
        )
    
    def _check_circuit_breaker(self, api_name: str) -> str:
        """Check the current state of the circuit breaker for an API."""
        circuit = self._circuit_breakers[api_name]
        current_time = time.time()
        
        if circuit["state"] == "OPEN":
            # Check if recovery timeout has passed
            if (circuit["last_failure"] and 
                current_time - circuit["last_failure"] >= circuit["recovery_timeout"]):
                circuit["state"] = "HALF_OPEN"
                self.log_operation(f"Circuit breaker for {api_name} moved to HALF_OPEN")
        
        return circuit["state"]
    
    def _record_failure(self, api_name: str, failure_time: float):
        """Record a failure for the circuit breaker."""
        circuit = self._circuit_breakers[api_name]
        circuit["failures"] += 1
        circuit["last_failure"] = failure_time
        
        if circuit["failures"] >= circuit["threshold"]:
            circuit["state"] = "OPEN"
            self.log_operation(f"Circuit breaker for {api_name} opened due to failures")
    
    def _record_success(self, api_name: str):
        """Record a success for the circuit breaker."""
        circuit = self._circuit_breakers[api_name]
        if circuit["state"] == "HALF_OPEN":
            # Reset circuit breaker on success
            circuit["state"] = "CLOSED"
            circuit["failures"] = 0
            circuit["last_failure"] = None
            self.log_operation(f"Circuit breaker for {api_name} closed after recovery")
    
    def get_rate_limit_info(self, api_name: str) -> Optional[Dict]:
        """Get current rate limit information for an API."""
        if api_name not in self._rate_limits:
            return None
        
        self._cleanup_old_requests(api_name)
        rate_limit = self._rate_limits[api_name]
        
        return {
            "api_name": api_name,
            "current_usage": len(rate_limit["requests"]),
            "limit": rate_limit["limit"],
            "remaining": rate_limit["limit"] - len(rate_limit["requests"]),
            "reset_time": datetime.fromtimestamp(
                rate_limit["last_reset"] + rate_limit["window"]
            ).isoformat()
        }
    
    def validate_input(self, data: any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, str) and data in self._rate_limits
    
    def reset_circuit_breaker(self, api_name: str, run_id: Optional[str] = None):
        """Manually reset the circuit breaker for an API."""
        if api_name in self._circuit_breakers:
            circuit = self._circuit_breakers[api_name]
            circuit["state"] = "CLOSED"
            circuit["failures"] = 0
            circuit["last_failure"] = None
            
            self.log_operation(f"Manually reset circuit breaker for {api_name}", run_id=run_id)
