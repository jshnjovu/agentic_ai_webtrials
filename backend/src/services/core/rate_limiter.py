"""
Rate limiting service with circuit breaker pattern.
Implements rate limiting for external APIs and circuit breaker for failure handling.
"""

import time
from typing import Dict, Optional, Tuple
from datetime import datetime

# Handle absolute vs package-relative imports so the module works both when
# `src` is a package (tests) and when `src` is on PYTHONPATH root.
try:
    from core.base_service import BaseService
    from core.config import get_api_config
except ImportError:  # Running inside the src package
    from ...core.base_service import BaseService
    from ...core.config import get_api_config


class RateLimiter(BaseService):
    """Rate limiting service with a circuit-breaker pattern."""

    def __init__(self):
        super().__init__("RateLimiter")
        self.api_config = get_api_config()
        self._rate_limits: Dict[str, Dict] = {}
        self._circuit_breakers: Dict[str, Dict] = {}
        self._setup_rate_limits()

    # ---------------------------------------------------------------------
    # Rate-limit bookkeeping
    # ---------------------------------------------------------------------
    def _setup_rate_limits(self):
        """Initialise per-API rate-limit windows and circuit-breakers."""
        self._rate_limits["serpapi"] = {
            "limit": self.api_config.SERPAPI_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # seconds
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["google_places"] = {
            "limit": self.api_config.GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # seconds
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["yelp_fusion"] = {
            "limit": self.api_config.YELP_FUSION_RATE_LIMIT_PER_DAY,
            "window": 86_400,  # 24 h
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["google_pagespeed"] = {
            "limit": self.api_config.PAGESPEED_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # seconds
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["google_pagespeed_daily"] = {
            "limit": self.api_config.PAGESPEED_RATE_LIMIT_PER_DAY,
            "window": 86_400,  # 24 h
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["pingdom"] = {
            "limit": self.api_config.PINGDOM_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # seconds
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["comprehensive_speed"] = {
            "limit": self.api_config.COMPREHENSIVE_SPEED_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # seconds
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["validation"] = {
            "limit": self.api_config.VALIDATION_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # seconds
            "requests": [],
            "last_reset": time.time(),
        }
        self._rate_limits["fallback"] = {
            "limit": self.api_config.FALLBACK_RATE_LIMIT_PER_MINUTE,
            "window": 60,  # seconds
            "requests": [],
            "last_reset": time.time(),
        }
        for api in self._rate_limits:
            self._circuit_breakers[api] = {
                "failures": 0,
                "last_failure": None,
                "state": "CLOSED",  # CLOSED | OPEN | HALF_OPEN
                "threshold": self.api_config.CIRCUIT_BREAKER_FAILURE_THRESHOLD,
                "recovery_timeout": self.api_config.CIRCUIT_BREAKER_RECOVERY_TIMEOUT,
            }

    def _cleanup_old_requests(self, api: str):
        rl = self._rate_limits[api]
        now = time.time()
        window_start = now - rl["window"]
        rl["requests"] = [t for t in rl["requests"] if t >= window_start]
        if now - rl["last_reset"] >= rl["window"]:
            rl["last_reset"] = now

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def can_make_request(self, api: str, run_id: Optional[str] = None) -> Tuple[bool, str]:
        if api not in self._rate_limits:
            return False, f"Unknown API: {api}"
        state = self._check_circuit_breaker(api)
        if state != "CLOSED":
            return False, f"Circuit breaker is {state}"
        self._cleanup_old_requests(api)
        rl = self._rate_limits[api]
        if len(rl["requests"]) >= rl["limit"]:
            return False, f"Rate limit exceeded: {len(rl['requests'])}/{rl['limit']}"
        return True, "OK"

    def record_request(self, api: str, success: bool, run_id: Optional[str] = None, failure_type: Optional[str] = None):
        if api not in self._rate_limits:
            return
        now = time.time()
        self._rate_limits[api]["requests"].append(now)
        if success:
            self._record_success(api)
        else:
            # Don't count legitimate site downtime as API failures
            if failure_type == "SITE_UNRESPONSIVE":
                self.log_operation(f"Site unresponsive - not counting as API failure for {api}", run_id=run_id)
            elif failure_type == "NETWORK_ERROR":
                self.log_operation(f"Network error - not counting as API failure for {api}", run_id=run_id)
            else:
                self._record_failure(api, now)
        self.log_operation(
            f"Recorded {'successful' if success else 'failed'} request to {api}",
            run_id=run_id,
        )

    def get_rate_limit_info(self, api: str):
        if api not in self._rate_limits:
            return None
        self._cleanup_old_requests(api)
        rl = self._rate_limits[api]
        return {
            "api_name": api,
            "current_usage": len(rl["requests"]),
            "limit": rl["limit"],
            "remaining": rl["limit"] - len(rl["requests"]),
            "reset_time": datetime.fromtimestamp(rl["last_reset"] + rl["window"]).isoformat(),
        }

    # ------------------------------------------------------------------
    # Circuit-breaker helpers
    # ------------------------------------------------------------------
    def _check_circuit_breaker(self, api: str) -> str:
        cb = self._circuit_breakers[api]
        now = time.time()
        if cb["state"] == "OPEN" and cb["last_failure"] and now - cb["last_failure"] >= cb["recovery_timeout"]:
            cb["state"] = "HALF_OPEN"
        return cb["state"]

    def _record_failure(self, api: str, when: float):
        cb = self._circuit_breakers[api]
        cb["failures"] += 1
        cb["last_failure"] = when
        if cb["failures"] >= cb["threshold"]:
            cb["state"] = "OPEN"
            self.log_operation(f"Circuit breaker for {api} opened due to failures")

    def _record_success(self, api: str):
        cb = self._circuit_breakers[api]
        if cb["state"] == "HALF_OPEN":
            cb.update({"state": "CLOSED", "failures": 0, "last_failure": None})
            self.log_operation(f"Circuit breaker for {api} closed after recovery")

    # ------------------------------------------------------------------
    # Boilerplate
    # ------------------------------------------------------------------
    def validate_input(self, data: any) -> bool:  # noqa: ANN401
        return isinstance(data, str) and data in self._rate_limits

    def reset_circuit_breaker(self, api: str, run_id: Optional[str] = None):
        if api in self._circuit_breakers:
            self._circuit_breakers[api].update({
                "state": "CLOSED",
                "failures": 0,
                "last_failure": None,
            })
            self.log_operation(f"Manually reset circuit breaker for {api}", run_id=run_id)

    def reset_circuit_breaker_if_site_issues(self, api: str, run_id: Optional[str] = None):
        """Reset circuit breaker if it was opened due to site unresponsiveness rather than API failures."""
        if api in self._circuit_breakers:
            cb = self._circuit_breakers[api]
            # Only reset if the circuit breaker is open and we have recent failures
            if cb["state"] == "OPEN" and cb["last_failure"]:
                # Check if the last failure was recent (within last 5 minutes)
                if time.time() - cb["last_failure"] < 300:  # 5 minutes
                    cb.update({
                        "state": "CLOSED",
                        "failures": 0,
                        "last_failure": None,
                    })
                    self.log_operation(f"Reset circuit breaker for {api} due to site issues", run_id=run_id)
                    return True
        return False
