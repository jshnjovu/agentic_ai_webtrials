"""
Yelp Fusion API authentication service.
Handles authentication and connection testing for Yelp Fusion API.
"""

import httpx
from typing import Dict, Any, Optional
from src.core import BaseService, get_api_config
from src.services import RateLimiter


class YelpFusionAuthService(BaseService):
    """Yelp Fusion API authentication service."""

    def __init__(self):
        super().__init__("YelpFusionAuthService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.base_url = "https://api.yelp.com/v3"
        self.api_key = self.api_config.YELP_FUSION_API_KEY

    def validate_input(self, data: any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, dict) and "run_id" in data

    def authenticate(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate with Yelp Fusion API.

        Args:
            run_id: Optional run identifier for logging

        Returns:
            Authentication result dictionary
        """
        try:
            self.log_operation("Starting Yelp Fusion API authentication", run_id=run_id)

            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request(
                "yelp_fusion", run_id
            )
            if not can_request:
                return self.handle_error(
                    Exception(f"Rate limit check failed: {reason}"),
                    "authentication_rate_limit_check",
                    run_id,
                )

            # Test connection with a simple API call
            test_url = f"{self.base_url}/businesses/search"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            params = {"term": "test", "location": "test"}

            with httpx.Client(timeout=self.api_config.API_TIMEOUT_SECONDS) as client:
                response = client.get(test_url, headers=headers, params=params)

                # Record the request
                self.rate_limiter.record_request(
                    "yelp_fusion", response.status_code == 200, run_id
                )

                if response.status_code == 200:
                    result = response.json()
                    if "businesses" in result:
                        self.log_operation(
                            "Yelp Fusion API authentication successful", run_id=run_id
                        )
                        return {
                            "success": True,
                            "api_name": "yelp_fusion",
                            "message": "Successfully authenticated with Yelp Fusion API",
                            "run_id": run_id,
                            "details": {
                                "total_businesses": len(result.get("businesses", [])),
                                "rate_limit_info": self.rate_limiter.get_rate_limit_info(
                                    "yelp_fusion"
                                ),
                            },
                        }
                    else:
                        return self.handle_error(
                            Exception(
                                "API response missing expected 'businesses' field"
                            ),
                            "authentication_api_error",
                            run_id,
                        )
                elif response.status_code == 401:
                    return self.handle_error(
                        Exception("Authentication failed - invalid API key"),
                        "authentication_unauthorized",
                        run_id,
                    )
                elif response.status_code == 429:
                    return self.handle_error(
                        Exception("Rate limit exceeded"),
                        "authentication_rate_limited",
                        run_id,
                    )
                else:
                    return self.handle_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "authentication_http_error",
                        run_id,
                    )

        except httpx.TimeoutException:
            return self.handle_error(
                Exception("Request timeout during authentication"),
                "authentication_timeout",
                run_id,
            )
        except httpx.RequestError as e:
            return self.handle_error(
                Exception(f"Request error during authentication: {str(e)}"),
                "authentication_request_error",
                run_id,
            )
        except Exception as e:
            return self.handle_error(e, "authentication_general_error", run_id)

    def test_connection(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Test connection to Yelp Fusion API.

        Args:
            run_id: Optional run identifier for logging

        Returns:
            Connection test result dictionary
        """
        try:
            self.log_operation("Testing Yelp Fusion API connection", run_id=run_id)

            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request(
                "yelp_fusion", run_id
            )
            if not can_request:
                return self.handle_error(
                    Exception(f"Rate limit check failed: {reason}"),
                    "connection_test_rate_limit_check",
                    run_id,
                )

            # Simple connection test
            test_url = f"{self.base_url}/businesses/search"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            params = {"term": "test", "location": "test"}

            with httpx.Client(timeout=self.api_config.API_TIMEOUT_SECONDS) as client:
                response = client.get(test_url, headers=headers, params=params)

                # Record the request
                self.rate_limiter.record_request(
                    "yelp_fusion", response.status_code == 200, run_id
                )

                if response.status_code == 200:
                    self.log_operation(
                        "Yelp Fusion API connection test successful", run_id=run_id
                    )
                    return {
                        "success": True,
                        "api_name": "yelp_fusion",
                        "message": "Connection test successful",
                        "run_id": run_id,
                        "details": {
                            "response_time_ms": response.elapsed.total_seconds() * 1000,
                            "rate_limit_info": self.rate_limiter.get_rate_limit_info(
                                "yelp_fusion"
                            ),
                        },
                    }
                else:
                    return self.handle_error(
                        Exception(
                            f"Connection test failed with HTTP {response.status_code}"
                        ),
                        "connection_test_http_error",
                        run_id,
                    )

        except httpx.TimeoutException:
            return self.handle_error(
                Exception("Connection test timeout"), "connection_test_timeout", run_id
            )
        except httpx.RequestError as e:
            return self.handle_error(
                Exception(f"Connection test request error: {str(e)}"),
                "connection_test_request_error",
                run_id,
            )
        except Exception as e:
            return self.handle_error(e, "connection_test_general_error", run_id)

    def get_health_status(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health status of Yelp Fusion API.

        Args:
            run_id: Optional run identifier for logging

        Returns:
            Health status dictionary
        """
        try:
            self.log_operation("Getting Yelp Fusion API health status", run_id=run_id)

            # Test connection
            connection_test = self.test_connection(run_id)

            if connection_test["success"]:
                rate_limit_info = self.rate_limiter.get_rate_limit_info("yelp_fusion")
                circuit_breaker = self.rate_limiter._circuit_breakers["yelp_fusion"]

                return {
                    "success": True,
                    "api_name": "yelp_fusion",
                    "message": "API is healthy",
                    "run_id": run_id,
                    "details": {
                        "status": "healthy",
                        "rate_limit_info": rate_limit_info,
                        "circuit_breaker_state": circuit_breaker["state"],
                        "last_failure": circuit_breaker["last_failure"],
                    },
                }
            else:
                return connection_test

        except Exception as e:
            return self.handle_error(e, "health_status_check", run_id)
