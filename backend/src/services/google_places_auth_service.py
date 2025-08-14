"""
Google Places API authentication service.
Handles authentication and connection testing for Google Places API.
"""

import httpx
from typing import Dict, Any, Optional
from ..core.base_service import BaseService
from ..core.config import get_api_config
from ..services.rate_limiter import RateLimiter


class GooglePlacesAuthService(BaseService):
    """Google Places API authentication service."""
    
    def __init__(self):
        super().__init__("GooglePlacesAuthService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.api_key = self.api_config.GOOGLE_PLACES_API_KEY
    
    def validate_input(self, data: any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, dict) and "run_id" in data
    
    def authenticate(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate with Google Places API.
        
        Args:
            run_id: Optional run identifier for logging
            
        Returns:
            Authentication result dictionary
        """
        try:
            self.log_operation("Starting Google Places API authentication", run_id=run_id)
            
            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request("google_places", run_id)
            if not can_request:
                return self.handle_error(
                    Exception(f"Rate limit check failed: {reason}"),
                    "authentication_rate_limit_check",
                    run_id
                )
            
            # Test connection with a simple API call
            test_url = f"{self.base_url}/findplacefromtext/json"
            params = {
                "input": "test",
                "inputtype": "textquery",
                "key": self.api_key
            }
            
            with httpx.Client(timeout=self.api_config.API_TIMEOUT_SECONDS) as client:
                response = client.get(test_url, params=params)
                
                # Record the request
                self.rate_limiter.record_request("google_places", response.status_code == 200, run_id)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("status") in ["OK", "ZERO_RESULTS"]:
                        self.log_operation("Google Places API authentication successful", run_id=run_id)
                        return {
                            "success": True,
                            "api_name": "google_places",
                            "message": "Successfully authenticated with Google Places API",
                            "run_id": run_id,
                            "details": {
                                "status": result.get("status"),
                                "rate_limit_info": self.rate_limiter.get_rate_limit_info("google_places")
                            }
                        }
                    else:
                        error_msg = f"API returned status: {result.get('status')}"
                        if result.get("error_message"):
                            error_msg += f" - {result['error_message']}"
                        
                        return self.handle_error(
                            Exception(error_msg),
                            "authentication_api_error",
                            run_id
                        )
                else:
                    return self.handle_error(
                        Exception(f"HTTP {response.status_code}: {response.text}"),
                        "authentication_http_error",
                        run_id
                    )
                    
        except httpx.TimeoutException:
            return self.handle_error(
                Exception("Request timeout during authentication"),
                "authentication_timeout",
                run_id
            )
        except httpx.RequestError as e:
            return self.handle_error(
                Exception(f"Request error during authentication: {str(e)}"),
                "authentication_request_error",
                run_id
            )
        except Exception as e:
            return self.handle_error(
                e,
                "authentication_general_error",
                run_id
            )
    
    def test_connection(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Test connection to Google Places API.
        
        Args:
            run_id: Optional run identifier for logging
            
        Returns:
            Connection test result dictionary
        """
        try:
            self.log_operation("Testing Google Places API connection", run_id=run_id)
            
            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request("google_places", run_id)
            if not can_request:
                return self.handle_error(
                    Exception(f"Rate limit check failed: {reason}"),
                    "connection_test_rate_limit_check",
                    run_id
                )
            
            # Simple connection test
            test_url = f"{self.base_url}/findplacefromtext/json"
            params = {
                "input": "test",
                "inputtype": "textquery",
                "key": self.api_key
            }
            
            with httpx.Client(timeout=self.api_config.API_TIMEOUT_SECONDS) as client:
                response = client.get(test_url, params=params)
                
                # Record the request
                self.rate_limiter.record_request("google_places", response.status_code == 200, run_id)
                
                if response.status_code == 200:
                    self.log_operation("Google Places API connection test successful", run_id=run_id)
                    return {
                        "success": True,
                        "api_name": "google_places",
                        "message": "Connection test successful",
                        "run_id": run_id,
                        "details": {
                            "response_time_ms": response.elapsed.total_seconds() * 1000,
                            "rate_limit_info": self.rate_limiter.get_rate_limit_info("google_places")
                        }
                    }
                else:
                    return self.handle_error(
                        Exception(f"Connection test failed with HTTP {response.status_code}"),
                        "connection_test_http_error",
                        run_id
                    )
                    
        except httpx.TimeoutException:
            return self.handle_error(
                Exception("Connection test timeout"),
                "connection_test_timeout",
                run_id
            )
        except httpx.RequestError as e:
            return self.handle_error(
                Exception(f"Connection test request error: {str(e)}"),
                "connection_test_request_error",
                run_id
            )
        except Exception as e:
            return self.handle_error(
                e,
                "connection_test_general_error",
                run_id
            )
    
    def get_health_status(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get health status of Google Places API.
        
        Args:
            run_id: Optional run identifier for logging
            
        Returns:
            Health status dictionary
        """
        try:
            self.log_operation("Getting Google Places API health status", run_id=run_id)
            
            # Test connection
            connection_test = self.test_connection(run_id)
            
            if connection_test["success"]:
                rate_limit_info = self.rate_limiter.get_rate_limit_info("google_places")
                circuit_breaker = self.rate_limiter._circuit_breakers["google_places"]
                
                return {
                    "success": True,
                    "api_name": "google_places",
                    "message": "API is healthy",
                    "run_id": run_id,
                    "details": {
                        "status": "healthy",
                        "rate_limit_info": rate_limit_info,
                        "circuit_breaker_state": circuit_breaker["state"],
                        "last_failure": circuit_breaker["last_failure"]
                    }
                }
            else:
                return connection_test
                
        except Exception as e:
            return self.handle_error(
                e,
                "health_status_check",
                run_id
            )
