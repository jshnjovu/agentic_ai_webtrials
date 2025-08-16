"""
Yelp Fusion business search service.
Handles business search functionality using Yelp Fusion API.
"""

import httpx
import re
from typing import Dict, Any, Optional, List
from src.core import BaseService, get_api_config
from src.services import RateLimiter
from src.schemas.yelp_fusion import (
    YelpBusinessSearchRequest,
    YelpBusinessData,
    YelpBusinessSearchResponse,
    YelpBusinessSearchError,
    YelpLocationType,
    YelpBusinessHours,
    YelpBusinessCategory,
    YelpBusinessCoordinates,
    YelpBusinessLocation,
)


class YelpFusionService(BaseService):
    """Yelp Fusion business search service."""

    def __init__(self):
        super().__init__("YelpFusionService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.base_url = "https://api.yelp.com/v3"
        self.api_key = self.api_config.YELP_FUSION_API_KEY
        self.max_results_per_request = 50  # Yelp Fusion API limit

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, YelpBusinessSearchRequest)

    def search_businesses(
        self, request: YelpBusinessSearchRequest
    ) -> YelpBusinessSearchResponse | YelpBusinessSearchError:
        """
        Search for businesses using Yelp Fusion API.

        Args:
            request: Yelp business search request with term, location, and filters

        Returns:
            Yelp business search response with results or error details
        """
        try:
            self.log_operation(
                f"Starting Yelp business search: '{request.term}' in {request.location}",
                run_id=request.run_id,
            )

            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request(
                "yelp_fusion", request.run_id
            )
            if not can_request:
                return YelpBusinessSearchError(
                    error=f"Rate limit exceeded: {reason}",
                    context="rate_limit_check",
                    term=request.term,
                    location=request.location,
                    run_id=request.run_id,
                )

            # Validate and process location
            location_info = self._process_location(
                request.location, request.location_type
            )
            if not location_info["valid"]:
                return YelpBusinessSearchError(
                    error=f"Invalid location: {location_info['error']}",
                    context="location_validation",
                    term=request.term,
                    location=request.location,
                    run_id=request.run_id,
                )

            # Build search parameters
            search_params = self._build_search_params(request, location_info)

            # Execute search
            search_result = self._execute_search(search_params, request.run_id)
            if not search_result["success"]:
                return YelpBusinessSearchError(
                    error=search_result["error"],
                    error_code=search_result.get("error_code"),
                    context="api_search_execution",
                    term=request.term,
                    location=request.location,
                    run_id=request.run_id,
                    details=search_result.get("details"),
                )

            # Process and limit results
            businesses = self._process_business_results(
                search_result["results"], request.limit, request.run_id
            )

            # Build response
            response = YelpBusinessSearchResponse(
                success=True,
                term=request.term,
                location=request.location,
                total=len(businesses),
                businesses=businesses,
                region=search_result.get("region"),
                run_id=request.run_id,
                search_metadata={
                    "total_available": search_result.get("total", 0),
                    "search_params": search_params,
                    "rate_limit_info": self.rate_limiter.get_rate_limit_info(
                        "yelp_fusion"
                    ),
                },
            )

            self.log_operation(
                f"Yelp business search completed: {len(businesses)} results found",
                run_id=request.run_id,
                business_id="search_complete",
            )

            return response

        except Exception as e:
            self.log_error(e, "yelp_business_search", request.run_id)
            return YelpBusinessSearchError(
                error=f"Unexpected error during Yelp business search: {str(e)}",
                context="unexpected_error",
                term=request.term,
                location=request.location,
                run_id=request.run_id,
            )

    def _process_location(
        self, location: str, location_type: YelpLocationType
    ) -> Dict[str, Any]:
        """
        Process and validate location input for Yelp Fusion API.

        Args:
            location: Location string to process
            location_type: Type of location input

        Returns:
            Dictionary with validation result and processed location
        """
        try:
            if not location or not location.strip():
                return {"valid": False, "error": "Location cannot be empty"}

            location = location.strip()

            if location_type == YelpLocationType.COORDINATES:
                # Validate coordinate format (lat,lng)
                coord_pattern = r"^-?\d+\.?\d*,-?\d+\.?\d*$"
                if not re.match(coord_pattern, location):
                    return {
                        "valid": False,
                        "error": "Invalid coordinate format. Use 'lat,lng'",
                    }

                return {
                    "valid": True,
                    "processed_location": location,
                    "type": "coordinates",
                }

            elif location_type == YelpLocationType.ZIP_CODE:
                # Validate ZIP code format
                zip_pattern = r"^\d{5}(-\d{4})?$"
                if not re.match(zip_pattern, location):
                    return {"valid": False, "error": "Invalid ZIP code format"}

                return {
                    "valid": True,
                    "processed_location": location,
                    "type": "zip_code",
                }

            else:
                # City or address - just validate it's not empty
                return {"valid": True, "processed_location": location, "type": "text"}

        except Exception as e:
            return {"valid": False, "error": f"Location processing error: {str(e)}"}

    def _build_search_params(
        self, request: YelpBusinessSearchRequest, location_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build search parameters for Yelp Fusion API.

        Args:
            request: Search request object
            location_info: Processed location information

        Returns:
            Dictionary of API parameters
        """
        params = {
            "term": request.term,
            "location": location_info["processed_location"],
            "limit": min(request.limit, self.max_results_per_request),
            "offset": request.offset,
        }

        # Add optional parameters if provided
        if request.radius is not None:
            params["radius"] = request.radius

        if request.categories:
            params["categories"] = ",".join(request.categories)

        if request.sort_by is not None:
            params["sort_by"] = request.sort_by

        if request.price is not None:
            params["price"] = request.price

        if request.open_now is not None:
            params["open_now"] = request.open_now

        return params

    def _execute_search(
        self, search_params: Dict[str, Any], run_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Execute the search request to Yelp Fusion API.

        Args:
            search_params: Search parameters for the API
            run_id: Optional run identifier for logging

        Returns:
            Dictionary with search results or error information
        """
        try:
            search_url = f"{self.base_url}/businesses/search"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            self.log_operation(
                f"Executing Yelp Fusion API search with params: {search_params}",
                run_id=run_id,
            )

            with httpx.Client(timeout=self.api_config.API_TIMEOUT_SECONDS) as client:
                response = client.get(search_url, headers=headers, params=search_params)

                # Record the request for rate limiting
                self.rate_limiter.record_request(
                    "yelp_fusion", response.status_code == 200, run_id
                )

                if response.status_code == 200:
                    result = response.json()

                    # Extract businesses and total count
                    businesses = result.get("businesses", [])
                    total = result.get("total", 0)
                    region = result.get("region", {})

                    self.log_operation(
                        f"Yelp Fusion API search successful: {len(businesses)} businesses found",
                        run_id=run_id,
                    )

                    return {
                        "success": True,
                        "results": businesses,
                        "total": total,
                        "region": region,
                    }

                elif response.status_code == 401:
                    return {
                        "success": False,
                        "error": "Authentication failed - invalid API key",
                        "error_code": "UNAUTHORIZED",
                    }

                elif response.status_code == 429:
                    return {
                        "success": False,
                        "error": "Rate limit exceeded",
                        "error_code": "RATE_LIMITED",
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
                "error": "Request timeout",
                "error_code": "TIMEOUT",
            }

        except httpx.RequestError as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "error_code": "REQUEST_ERROR",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "UNEXPECTED_ERROR",
            }

    def _process_business_results(
        self,
        raw_businesses: List[Dict[str, Any]],
        max_results: int,
        run_id: Optional[str],
    ) -> List[YelpBusinessData]:
        """
        Process raw business results from Yelp Fusion API.

        Args:
            raw_businesses: Raw business data from API
            max_results: Maximum number of results to return
            run_id: Optional run identifier for logging

        Returns:
            List of processed YelpBusinessData objects
        """
        try:
            processed_businesses = []

            for i, raw_business in enumerate(raw_businesses[:max_results]):
                try:
                    # Validate required fields
                    if not isinstance(
                        raw_business.get("id"), str
                    ) or not raw_business.get("id"):
                        continue
                    if not isinstance(
                        raw_business.get("name"), str
                    ) or not raw_business.get("name"):
                        continue
                    if not isinstance(
                        raw_business.get("url"), str
                    ) or not raw_business.get("url"):
                        continue

                    # Extract business hours
                    hours = self._extract_business_hours(raw_business.get("hours", []))

                    # Extract categories
                    categories = self._extract_categories(
                        raw_business.get("categories", [])
                    )

                    # Extract coordinates
                    coordinates = self._extract_coordinates(
                        raw_business.get("coordinates", {})
                    )

                    # Extract location
                    location = self._extract_location(raw_business.get("location", {}))

                    # Extract photos
                    photos = self._extract_photos(raw_business)

                    # Extract enhanced data fields
                    attributes = self._extract_attributes(
                        raw_business.get("attributes", {})
                    )
                    special_hours = self._extract_special_hours(
                        raw_business.get("special_hours", [])
                    )
                    business_status = self._extract_business_status(raw_business)
                    social_media = self._extract_social_media(raw_business)

                    # Create business data object
                    business_data = YelpBusinessData(
                        id=raw_business.get("id", ""),
                        alias=raw_business.get("alias", ""),
                        name=raw_business.get("name", ""),
                        image_url=raw_business.get("image_url"),
                        is_closed=raw_business.get("is_closed", True),
                        url=raw_business.get("url", ""),
                        review_count=raw_business.get("review_count", 0),
                        categories=categories,
                        rating=raw_business.get("rating", 0.0),
                        coordinates=coordinates,
                        transactions=raw_business.get("transactions", []),
                        price=raw_business.get("price"),
                        location=location,
                        phone=raw_business.get("phone"),
                        display_phone=raw_business.get("display_phone"),
                        distance=raw_business.get("distance"),
                        hours=hours,
                        photos=photos,
                        attributes=attributes,
                        special_hours=special_hours,
                        business_status=business_status,
                        social_media=social_media,
                    )

                    processed_businesses.append(business_data)

                except Exception as e:
                    self.log_error(
                        e,
                        f"processing_business_{i}",
                        run_id,
                        business_id=raw_business.get("id", "unknown"),
                    )
                    # Continue processing other businesses
                    continue

            self.log_operation(
                f"Processed {len(processed_businesses)} business results", run_id=run_id
            )

            return processed_businesses

        except Exception as e:
            self.log_error(e, "processing_business_results", run_id)
            return []

    def _extract_business_hours(
        self, raw_hours: List[Dict[str, Any]]
    ) -> List[YelpBusinessHours]:
        """Extract and validate business hours from raw API data."""
        hours = []

        for hour_data in raw_hours:
            try:
                # Validate required fields
                if (
                    not isinstance(hour_data.get("day"), int)
                    or not isinstance(hour_data.get("start"), str)
                    or not isinstance(hour_data.get("end"), str)
                ):
                    continue

                hour = YelpBusinessHours(
                    day=hour_data.get("day", 0),
                    start=hour_data.get("start", "0000"),
                    end=hour_data.get("end", "2359"),
                    is_overnight=hour_data.get("is_overnight", False),
                )
                hours.append(hour)
            except Exception:
                # Skip invalid hour data
                continue

        return hours

    def _extract_categories(
        self, raw_categories: List[Dict[str, Any]]
    ) -> List[YelpBusinessCategory]:
        """Extract and validate business categories from raw API data."""
        categories = []

        for cat_data in raw_categories:
            try:
                # Validate required fields
                if not isinstance(cat_data.get("alias"), str) or not isinstance(
                    cat_data.get("title"), str
                ):
                    continue
                if not cat_data.get("alias") or not cat_data.get("title"):
                    continue

                category = YelpBusinessCategory(
                    alias=cat_data.get("alias", ""), title=cat_data.get("title", "")
                )
                categories.append(category)
            except Exception:
                # Skip invalid category data
                continue

        return categories

    def _extract_coordinates(
        self, raw_coordinates: Dict[str, Any]
    ) -> YelpBusinessCoordinates:
        """Extract and validate business coordinates from raw API data."""
        try:
            return YelpBusinessCoordinates(
                latitude=raw_coordinates.get("latitude", 0.0),
                longitude=raw_coordinates.get("longitude", 0.0),
            )
        except Exception:
            # Return default coordinates if extraction fails
            return YelpBusinessCoordinates(latitude=0.0, longitude=0.0)

    def _extract_location(self, raw_location: Dict[str, Any]) -> YelpBusinessLocation:
        """Extract and validate business location from raw API data."""
        try:
            return YelpBusinessLocation(
                address1=raw_location.get("address1") or "",
                address2=raw_location.get("address2"),
                address3=raw_location.get("address3"),
                city=raw_location.get("city") or "",
                state=raw_location.get("state") or "",
                zip_code=raw_location.get("zip_code") or "",
                country=raw_location.get("country") or "",
                display_address=raw_location.get("display_address", []),
                cross_streets=raw_location.get("cross_streets"),
            )
        except Exception:
            # Return minimal location if extraction fails
            return YelpBusinessLocation(
                address1="",
                city="",
                state="",
                zip_code="",
                country="",
                display_address=[],
            )

    def _extract_photos(self, raw_business: Dict[str, Any]) -> List[str]:
        """Extract photo URLs from business data."""
        photos = []

        # Add main image if available
        if raw_business.get("image_url"):
            photos.append(raw_business["image_url"])

        # Add additional photos if available
        if "photos" in raw_business and isinstance(raw_business["photos"], list):
            photos.extend(raw_business["photos"])

        return photos

    def _extract_attributes(
        self, raw_attributes: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Extract and validate business attributes from raw API data."""
        if not raw_attributes:
            return None

        # Filter out None values and empty strings
        filtered_attributes = {}
        for key, value in raw_attributes.items():
            if value is not None and value != "":
                if isinstance(value, dict):
                    # Handle nested attribute objects (e.g., {"Good for Kids": true})
                    filtered_nested = {
                        k: v for k, v in value.items() if v is not None and v != ""
                    }
                    if filtered_nested:
                        filtered_attributes[key] = filtered_nested
                else:
                    filtered_attributes[key] = value

        return filtered_attributes if filtered_attributes else None

    def _extract_special_hours(
        self, raw_special_hours: List[Dict[str, Any]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Extract and validate special hours from raw API data."""
        if not raw_special_hours:
            return None

        special_hours = []
        for special_hour in raw_special_hours:
            try:
                # Validate required fields for special hours
                if not isinstance(special_hour.get("date"), str):
                    continue
                if not isinstance(special_hour.get("start"), str) or not isinstance(
                    special_hour.get("end"), str
                ):
                    continue

                special_hours.append(
                    {
                        "date": special_hour.get("date"),
                        "start": special_hour.get("start"),
                        "end": special_hour.get("end"),
                        "is_closed": special_hour.get("is_closed", False),
                        "is_overnight": special_hour.get("is_overnight", False),
                    }
                )
            except Exception:
                # Skip invalid special hour data
                continue

        return special_hours if special_hours else None

    def _extract_business_status(self, raw_business: Dict[str, Any]) -> Optional[str]:
        """Extract business status information."""
        # Check for various status indicators
        status_indicators = []

        if raw_business.get("is_closed"):
            status_indicators.append("Permanently Closed")

        # Check for temporary closure indicators
        if "temporary_closed" in raw_business.get("attributes", {}):
            status_indicators.append("Temporarily Closed")

        # Check for special announcements
        if raw_business.get("announcement"):
            status_indicators.append(f"Announcement: {raw_business['announcement']}")

        # Check for COVID-19 related status
        covid_attributes = raw_business.get("attributes", {}).get("COVID-19", {})
        if covid_attributes:
            if covid_attributes.get("delivery_or_takeout") == "delivery_only":
                status_indicators.append("Delivery Only")
            elif covid_attributes.get("delivery_or_takeout") == "takeout_only":
                status_indicators.append("Takeout Only")

        return "; ".join(status_indicators) if status_indicators else None

    def _extract_social_media(
        self, raw_business: Dict[str, Any]
    ) -> Optional[Dict[str, str]]:
        """Extract social media links if available."""
        social_media = {}

        # Check for social media links in various possible locations
        if raw_business.get("facebook_url"):
            social_media["facebook"] = raw_business["facebook_url"]

        if raw_business.get("instagram_url"):
            social_media["instagram"] = raw_business["instagram_url"]

        if raw_business.get("twitter_url"):
            social_media["twitter"] = raw_business["twitter_url"]

        # Check for social media in attributes
        attributes = raw_business.get("attributes", {})
        if "Social Media" in attributes:
            social_attrs = attributes["Social Media"]
            if isinstance(social_attrs, dict):
                for platform, url in social_attrs.items():
                    if url and isinstance(url, str):
                        social_media[platform.lower()] = url

        return social_media if social_media else None
