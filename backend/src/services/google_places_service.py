"""
Google Places business search service.
Handles business search functionality using Google Places API.
"""

import httpx
import re
from typing import Dict, Any, Optional, List
from src.core import BaseService, get_api_config
from src.services import RateLimiter
from src.schemas import (
    BusinessSearchRequest,
    BusinessData,
    BusinessSearchResponse,
    BusinessSearchError,
    LocationType,
)


class GooglePlacesService(BaseService):
    """Google Places business search service."""

    def __init__(self):
        super().__init__("GooglePlacesService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.api_key = self.api_config.GOOGLE_PLACES_API_KEY
        self.max_results_per_request = 20  # Google Places API limit

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, BusinessSearchRequest)

    def search_businesses(
        self, request: BusinessSearchRequest
    ) -> BusinessSearchResponse | BusinessSearchError:
        """
        Search for businesses using Google Places API.

        Args:
            request: Business search request with query, location, and filters

        Returns:
            Business search response with results or error details
        """
        try:
            self.log_operation(
                f"Starting business search: '{request.query}' in {request.location}",
                run_id=request.run_id,
            )

            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request(
                "google_places", request.run_id
            )
            if not can_request:
                return BusinessSearchError(
                    error=f"Rate limit exceeded: {reason}",
                    context="rate_limit_check",
                    query=request.query,
                    location=request.location,
                    run_id=request.run_id,
                )

            # Validate and process location
            location_info = self._process_location(
                request.location, request.location_type
            )
            if not location_info["valid"]:
                return BusinessSearchError(
                    error=f"Invalid location: {location_info['error']}",
                    context="location_validation",
                    query=request.query,
                    location=request.location,
                    run_id=request.run_id,
                )

            # Build search parameters
            search_params = self._build_search_params(request, location_info)

            # Execute search
            search_result = self._execute_search(search_params, request.run_id)
            if not search_result["success"]:
                return BusinessSearchError(
                    error=search_result["error"],
                    error_code=search_result.get("error_code"),
                    context="api_search_execution",
                    query=request.query,
                    location=request.location,
                    run_id=request.run_id,
                    details=search_result.get("details"),
                )

            # Process and limit results
            businesses = self._process_business_results(
                search_result["results"], request.max_results, request.run_id
            )

            # Build response
            response = BusinessSearchResponse(
                success=True,
                query=request.query,
                location=request.location,
                total_results=len(businesses),
                results=businesses,
                next_page_token=search_result.get("next_page_token"),
                run_id=request.run_id,
                search_metadata={
                    "location_type": request.location_type.value,
                    "radius_meters": request.radius,
                    "category_filter": request.category,
                    "api_status": search_result.get("api_status"),
                },
            )

            self.log_operation(
                f"Business search completed successfully: {len(businesses)} results found",
                run_id=request.run_id,
            )

            return response

        except Exception as e:
            self.log_error(e, "business_search", request.run_id)
            return BusinessSearchError(
                error=f"Unexpected error during business search: {str(e)}",
                context="unexpected_error",
                query=request.query,
                location=request.location,
                run_id=request.run_id,
            )

    def _process_location(
        self, location: str, location_type: LocationType
    ) -> Dict[str, Any]:
        """
        Process and validate location input.

        Args:
            location: Location string input
            location_type: Type of location input

        Returns:
            Dictionary with validation result and processed location data
        """
        try:
            if location_type == LocationType.COORDINATES:
                # Validate coordinate format (lat,lng)
                coord_pattern = r"^-?\d+\.?\d*,-?\d+\.?\d*$"
                if not re.match(coord_pattern, location):
                    return {
                        "valid": False,
                        "error": "Invalid coordinate format. Use 'latitude,longitude' (e.g., '37.7749,-122.4194')",
                    }
                return {"valid": True, "coordinates": location, "type": "coordinates"}

            elif location_type == LocationType.ZIP_CODE:
                # Validate ZIP code format
                zip_pattern = r"^\d{5}(-\d{4})?$"
                if not re.match(zip_pattern, location):
                    return {
                        "valid": False,
                        "error": "Invalid ZIP code format. Use 5-digit or 9-digit format (e.g., '12345' or '12345-6789')",
                    }
                return {"valid": True, "zip_code": location, "type": "zip_code"}

            else:  # CITY or ADDRESS
                # Basic validation for city/address
                if len(location.strip()) < 2:
                    return {
                        "valid": False,
                        "error": "Location must be at least 2 characters long",
                    }
                return {
                    "valid": True,
                    "text": location.strip(),
                    "type": location_type.value,
                }

        except Exception as e:
            return {"valid": False, "error": f"Location processing error: {str(e)}"}

    def _build_search_params(
        self, request: BusinessSearchRequest, location_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build search parameters for Google Places API.

        Args:
            request: Business search request
            location_info: Processed location information

        Returns:
            Dictionary of API search parameters
        """
        params = {
            "query": request.query,
            "key": self.api_key,
            "maxresults": min(request.max_results, self.max_results_per_request),
        }

        # Add location parameter based on type
        if location_info["type"] == "coordinates":
            params["location"] = location_info["coordinates"]
            params["radius"] = request.radius
        elif location_info["type"] == "zip_code":
            params["query"] = f"{request.query} in {location_info['zip_code']}"
        else:  # city or address
            params["query"] = f"{request.query} in {location_info['text']}"

        # Add category filter if specified
        if request.category:
            params["type"] = request.category

        return params

    def _execute_search(
        self, search_params: Dict[str, Any], run_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute the actual API search request.

        Args:
            search_params: Search parameters for the API
            run_id: Optional run identifier for logging

        Returns:
            Dictionary with search results or error information
        """
        try:
            search_url = f"{self.base_url}/textsearch/json"

            with httpx.Client(timeout=self.api_config.API_TIMEOUT_SECONDS) as client:
                response = client.get(search_url, params=search_params)

                # Record the request for rate limiting
                self.rate_limiter.record_request(
                    "google_places", response.status_code == 200, run_id
                )

                if response.status_code == 200:
                    result = response.json()
                    api_status = result.get("status")

                    if api_status == "OK":
                        return {
                            "success": True,
                            "results": result.get("results", []),
                            "next_page_token": result.get("next_page_token"),
                            "api_status": api_status,
                        }
                    elif api_status == "ZERO_RESULTS":
                        return {
                            "success": True,
                            "results": [],
                            "api_status": api_status,
                        }
                    else:
                        error_msg = f"API returned status: {api_status}"
                        if result.get("error_message"):
                            error_msg += f" - {result['error_message']}"

                        return {
                            "success": False,
                            "error": error_msg,
                            "error_code": api_status,
                            "details": {"api_response": result},
                        }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "error_code": f"HTTP_{response.status_code}",
                    }

        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout during search",
                "error_code": "TIMEOUT",
            }
        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request error during search: {str(e)}",
                "error_code": "REQUEST_ERROR",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error during search: {str(e)}",
                "error_code": "UNEXPECTED_ERROR",
            }

    def _process_business_results(
        self, raw_results: List[Dict[str, Any]], max_results: int, run_id: Optional[str]
    ) -> List[BusinessData]:
        """
        Process raw API results into BusinessData models.

        Args:
            raw_results: Raw results from Google Places API
            max_results: Maximum number of results to return
            run_id: Optional run identifier for logging

        Returns:
            List of processed BusinessData models
        """
        try:
            businesses = []

            for raw_business in raw_results[:max_results]:
                try:
                    business = BusinessData(
                        place_id=raw_business.get("place_id", ""),
                        name=raw_business.get("name", ""),
                        address=raw_business.get("formatted_address"),
                        phone=raw_business.get("formatted_phone_number"),
                        website=raw_business.get("website"),
                        rating=raw_business.get("rating"),
                        user_ratings_total=raw_business.get("user_ratings_total"),
                        price_level=raw_business.get("price_level"),
                        types=raw_business.get("types", []),
                        geometry=raw_business.get("geometry"),
                        formatted_address=raw_business.get("formatted_address"),
                        international_phone_number=raw_business.get(
                            "international_phone_number"
                        ),
                        opening_hours=raw_business.get("opening_hours"),
                        photos=raw_business.get("photos"),
                        reviews=raw_business.get("reviews"),
                    )
                    businesses.append(business)

                except Exception as e:
                    self.log_error(
                        e,
                        f"business_data_processing for place_id: {raw_business.get('place_id', 'unknown')}",
                        run_id,
                    )
                    # Continue processing other businesses
                    continue

            self.log_operation(
                f"Processed {len(businesses)} business results from {len(raw_results)} raw results",
                run_id=run_id,
            )

            return businesses

        except Exception as e:
            self.log_error(e, "business_results_processing", run_id)
            return []

    def get_next_page(
        self, next_page_token: str, run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get next page of results using pagination token.

        Args:
            next_page_token: Token for next page from previous search
            run_id: Optional run identifier for logging

        Returns:
            Dictionary with next page results or error information
        """
        try:
            self.log_operation("Fetching next page of results", run_id=run_id)

            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request(
                "google_places", run_id
            )
            if not can_request:
                return {
                    "success": False,
                    "error": f"Rate limit exceeded: {reason}",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                }

            # Build pagination request
            params = {"pagetoken": next_page_token, "key": self.api_key}

            pagination_url = f"{self.base_url}/textsearch/json"

            with httpx.Client(timeout=self.api_config.API_TIMEOUT_SECONDS) as client:
                response = client.get(pagination_url, params=params)

                # Record the request for rate limiting
                self.rate_limiter.record_request(
                    "google_places", response.status_code == 200, run_id
                )

                if response.status_code == 200:
                    result = response.json()
                    api_status = result.get("status")

                    if api_status == "OK":
                        businesses = self._process_business_results(
                            result.get("results", []),
                            20,  # Default max for pagination
                            run_id,
                        )

                        return {
                            "success": True,
                            "results": businesses,
                            "next_page_token": result.get("next_page_token"),
                            "api_status": api_status,
                        }
                    else:
                        error_msg = f"API returned status: {api_status}"
                        if result.get("error_message"):
                            error_msg += f" - {result['error_message']}"

                        return {
                            "success": False,
                            "error": error_msg,
                            "error_code": api_status,
                        }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "error_code": f"HTTP_{response.status_code}",
                    }

        except Exception as e:
            self.log_error(e, "next_page_fetch", run_id)
            return {
                "success": False,
                "error": f"Unexpected error fetching next page: {str(e)}",
                "error_code": "UNEXPECTED_ERROR",
            }
