"""
SerpAPI business search service.
Handles business search functionality using SerpAPI instead of Google Places API.
"""

import httpx
import re
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import quote_plus
from src.core import BaseService, get_api_config
from src.services.rate_limiter import RateLimiter
from src.services.geoapify_service import GeoapifyService
from src.schemas import (
    BusinessSearchRequest, BusinessData, BusinessSearchResponse, 
    BusinessSearchError, LocationType
)


class SerpAPIService(BaseService):
    """SerpAPI business search service."""
    
    def __init__(self):
        super().__init__("SerpAPIService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.geoapify_service = GeoapifyService()
        self.base_url = "https://serpapi.com/search.json"
        self.api_key = self.api_config.SERPAPI_API_KEY
        self.max_results_per_request = 20
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, BusinessSearchRequest)
    
    async def search_businesses(self, request: BusinessSearchRequest) -> BusinessSearchResponse | BusinessSearchError:
        """Search for businesses using SerpAPI."""
        try:
            self.log_operation(
                f"Starting SerpAPI business search: '{request.query}' in {request.location}", 
                run_id=request.run_id
            )
            
            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request("serpapi", request.run_id)
            if not can_request:
                return BusinessSearchError(
                    error=f"Rate limit exceeded: {reason}",
                    context="rate_limit_check",
                    query=request.query,
                    location=request.location,
                    run_id=request.run_id
                )
            
            # Build search parameters (async)
            search_params = await self._build_search_params(request)
            
            # Execute search
            search_result = self._execute_search(search_params, request.run_id)
            if not search_result["success"]:
                return BusinessSearchError(
                    error=search_result["error"],
                    error_code=search_result.get("error_code"),
                    context="api_search_execution",
                    query=request.query,
                    location=request.location,
                    run_id=request.run_id
                )
            
            # Process and limit results
            businesses = self._process_business_results(
                search_result["results"], 
                request.max_results,
                request.run_id
            )
            
            # Build response
            response = BusinessSearchResponse(
                success=True,
                query=request.query,
                location=request.location,
                total_results=len(businesses),
                results=businesses,
                run_id=request.run_id,
                search_metadata={
                    "api_used": "serpapi",
                    "total_api_results": len(search_result["results"])
                }
            )
            
            return response
            
        except Exception as e:
            self.log_error(e, "serpapi_business_search", request.run_id)
            return BusinessSearchError(
                error=f"Unexpected error during SerpAPI search: {str(e)}",
                context="unexpected_error",
                query=request.query,
                location=request.location,
                run_id=request.run_id
            )
    
    async def _build_search_params(self, request: BusinessSearchRequest) -> Dict[str, Any]:
        """Build SerpAPI search parameters - exactly matching SERPAPI.md pattern."""
        # Extract country code from location using Geoapify (async)
        country_code = await self.geoapify_service.extract_country_code(request.location)
        
        # Use extracted country code or fallback to "us"
        gl_param = country_code if country_code else "us"
        
        # Build query exactly like SERPAPI.md: "Gym London UK" format
        query = f"{request.query} {request.location}"
        
        params = {
            "q": query,  # Combined query like "Gym London UK"
            "engine": "google_local",
            "google_domain": "google.com",
            "hl": "en",
            "gl": gl_param,  # Dynamic country code from Geoapify
            "device": "desktop"
        }
        
        # Add category filter if specified
        if request.category:
            params["q"] = f"{request.query} {request.category} {request.location}"
        
        # Log the country code being used
        self.logger.info(f"Using country code '{gl_param}' for location '{request.location}'")
        
        return params
    
    def _execute_search(self, search_params: Dict[str, Any], run_id: str) -> Dict[str, Any]:
        """Execute the SerpAPI search request."""
        try:
            # Add API key
            search_params["api_key"] = self.api_key
            
            # Make the request
            with httpx.Client(timeout=30.0) as client:
                response = client.get(self.base_url, params=search_params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check for SerpAPI errors
                    if data.get("error"):
                        return {
                            "success": False,
                            "error": f"SerpAPI error: {data['error']}",
                            "error_code": "SERPAPI_ERROR"
                        }
                    
                    # Extract local results
                    local_results = data.get('local_results', [])
                    if not local_results:
                        return {
                            "success": False,
                            "error": "No local results found",
                            "error_code": "NO_RESULTS"
                        }
                    
                    return {
                        "success": True,
                        "results": local_results
                    }
                    
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "error_code": f"HTTP_{response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Request error: {str(e)}",
                "error_code": "REQUEST_ERROR"
            }
    
    def _process_business_results(self, raw_results: List[Dict[str, Any]], max_results: int, run_id: str) -> List[BusinessData]:
        """Process raw SerpAPI results into BusinessData format."""
        processed_businesses = []
        
        for i, place in enumerate(raw_results[:max_results]):
            try:
                # Debug logging to see raw data
                self.logger.info(f"Processing place {i+1}: {place.get('title', 'Unknown')}")
                self.logger.info(f"Raw address field: {place.get('address')}")
                self.logger.info(f"Raw place data keys: {list(place.keys())}")
                
                # Extract website from links
                website = None
                if 'links' in place and isinstance(place['links'], dict):
                    website = place['links'].get('website')
                
                # Extract GPS coordinates
                geometry = None
                if 'gps_coordinates' in place and isinstance(place['gps_coordinates'], dict):
                    coords = place['gps_coordinates']
                    geometry = {
                        "location": {
                            "lat": coords.get('latitude'),
                            "lng": coords.get('longitude')
                        }
                    }
                
                # Create BusinessData object
                business = BusinessData(
                    place_id=place.get('place_id', f"serpapi_{i}"),
                    name=place.get('title', 'Unknown'),
                    address=place.get('address'),
                    phone=place.get('phone'),
                    website=website,
                    rating=place.get('rating'),
                    user_ratings_total=place.get('reviews'),
                    types=[place.get('type', 'Business')] if place.get('type') else None,
                    geometry=geometry,
                    formatted_address=place.get('address'),
                    confidence_level="high"
                )
                
                processed_businesses.append(business)
                
            except Exception as e:
                self.log_error(e, f"processing_business_result_{i}", run_id)
                continue
        
        return processed_businesses
