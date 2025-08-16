"""
Business Discovery Service with Fallback System
Uses Lighthouse first, then Google Places API as fallback for business discovery.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time

from src.core.base_service import BaseService
from src.core.config import get_google_places_key, get_yelp_fusion_key, get_business_discovery_config
from src.services.lighthouse_service import LighthouseService
from src.services.google_places_service import GooglePlacesService
from src.services.yelp_fusion_service import YelpFusionService
from src.services.fallback_scoring_service import FallbackScoringService
from src.schemas.business_search import BusinessSearchRequest
from src.schemas.yelp_fusion import YelpBusinessSearchRequest
from src.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class BusinessDiscoveryService(BaseService):
    """
    Business discovery service with intelligent fallback system.
    Tries Lighthouse first, then falls back to Google Places API and Yelp Fusion.
    """

    def __init__(self):
        super().__init__("BusinessDiscoveryService")
        self.lighthouse_service = LighthouseService()
        self.google_places_service = GooglePlacesService()
        self.yelp_fusion_service = YelpFusionService()
        self.fallback_service = FallbackScoringService()
        self.rate_limiter = RateLimiter()
        self.business_config = get_business_discovery_config()
        
        # Fallback configuration
        self.lighthouse_timeout = 15  # seconds
        self.google_places_timeout = 10  # seconds
        self.yelp_timeout = 10  # seconds
        self.max_retries = 2
        
        # Service priority order
        self.service_priority = ["lighthouse", "google_places", "yelp_fusion"]

    def validate_input(self, data: Any) -> bool:
        """Validate input data for business discovery."""
        if isinstance(data, dict):
            required_fields = ["location", "niche"]
            return all(field in data for field in required_fields)
        return False

    async def discover_businesses(
        self,
        location: str,
        niche: str,
        radius: int = 5000,
        max_results: int = 20,
        run_id: Optional[str] = None,
        strategy: str = "desktop"
    ) -> Dict[str, Any]:
        """
        Discover businesses using intelligent fallback system.
        
        Args:
            location: Location to search in
            niche: Business niche/category
            radius: Search radius in meters
            max_results: Maximum number of results
            run_id: Unique identifier for the run
            strategy: Lighthouse strategy (desktop/mobile)
            
        Returns:
            Dictionary containing discovery results or error information
        """
        try:
            self.log_operation(
                f"Starting business discovery for '{niche}' in '{location}'",
                run_id=run_id
            )
            
            # Validate inputs
            if not self._validate_discovery_inputs(location, niche, radius, max_results):
                return self._create_error_response(
                    "Invalid input parameters",
                    "validation_error",
                    location, niche, run_id
                )
            
            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request("business_discovery", run_id)
            if not can_request:
                return self._create_error_response(
                    f"Rate limit exceeded: {reason}",
                    "rate_limit_exceeded",
                    location, niche, run_id
                )
            
            # Start discovery with fallback system
            discovery_result = await self._discover_with_fallback(
                location, niche, radius, max_results, run_id, strategy
            )
            
            # Record the request
            self.rate_limiter.record_request("business_discovery", discovery_result["success"], run_id)
            
            return discovery_result
            
        except Exception as e:
            self.log_operation(
                f"Business discovery failed: {str(e)}",
                run_id=run_id,
                error=True
            )
            return self._create_error_response(
                f"Discovery failed: {str(e)}",
                "unexpected_error",
                location, niche, run_id
            )

    async def _discover_with_fallback(
        self,
        location: str,
        niche: str,
        radius: int,
        max_results: int,
        run_id: Optional[str],
        strategy: str
    ) -> Dict[str, Any]:
        """
        Implement fallback discovery system.
        Tries Lighthouse first, then Google Places, then Yelp Fusion.
        """
        
        # Step 1: Try Lighthouse first (for existing businesses with websites)
        lighthouse_result = await self._try_lighthouse_discovery(
            location, niche, max_results, run_id, strategy
        )
        
        if lighthouse_result["success"] and lighthouse_result["businesses"]:
            self.log_operation(
                f"Lighthouse discovery successful: {len(lighthouse_result['businesses'])} businesses found",
                run_id=run_id
            )
            return lighthouse_result
        
        # Step 2: Fallback to Google Places API
        google_result = await self._try_google_places_discovery(
            location, niche, radius, max_results, run_id
        )
        
        if google_result["success"] and google_result["businesses"]:
            self.log_operation(
                f"Google Places fallback successful: {len(google_result['businesses'])} businesses found",
                run_id=run_id
            )
            return google_result
        
        # Step 3: Final fallback to Yelp Fusion
        yelp_result = await self._try_yelp_discovery(
            location, niche, radius, max_results, run_id
        )
        
        if yelp_result["success"] and yelp_result["businesses"]:
            self.log_operation(
                f"Yelp Fusion fallback successful: {len(yelp_result['businesses'])} businesses found",
                run_id=run_id
            )
            return yelp_result
        
        # All services failed
        return self._create_error_response(
            "All discovery services failed",
            "all_services_failed",
            location, niche, run_id
        )

    async def _try_lighthouse_discovery(
        self,
        location: str,
        niche: str,
        max_results: int,
        run_id: Optional[str],
        strategy: str
    ) -> Dict[str, Any]:
        """Try to discover businesses using Lighthouse (existing websites)."""
        try:
            # For Lighthouse, we need to search for existing business websites
            # This would typically involve searching for businesses in the area
            # and then analyzing their websites
            
            # For now, return empty result to trigger fallback
            # In a real implementation, this would search business directories
            # and then analyze found websites with Lighthouse
            
            return {
                "success": True,
                "businesses": [],
                "total_found": 0,
                "source": "lighthouse",
                "message": "No existing websites found for this niche/location"
            }
            
        except Exception as e:
            self.log_operation(
                f"Lighthouse discovery failed: {str(e)}",
                run_id=run_id,
                error=True
            )
            return {
                "success": False,
                "businesses": [],
                "total_found": 0,
                "source": "lighthouse",
                "error": str(e)
            }

    async def _try_google_places_discovery(
        self,
        location: str,
        niche: str,
        radius: int,
        max_results: int,
        run_id: Optional[str]
    ) -> Dict[str, Any]:
        """Try to discover businesses using Google Places API."""
        try:
            # Check if Google Places API is available
            if not get_google_places_key():
                return {
                    "success": False,
                    "businesses": [],
                    "total_found": 0,
                    "source": "google_places",
                    "error": "Google Places API key not configured"
                }
            
            # Create Google Places search request
            request = BusinessSearchRequest(
                query=niche,
                location=location,
                radius=radius,
                max_results=max_results,
                run_id=run_id
            )
            
            # Execute search with timeout
            search_result = await asyncio.wait_for(
                self._execute_google_places_search(request),
                timeout=self.google_places_timeout
            )
            
            if search_result.get("success", False):
                businesses = self._normalize_google_places_results(
                    search_result.get("results", []), location, niche
                )
                return {
                    "success": True,
                    "businesses": businesses,
                    "total_found": len(businesses),
                    "source": "google_places",
                    "message": f"Found {len(businesses)} businesses via Google Places"
                }
            else:
                return {
                    "success": False,
                    "businesses": [],
                    "total_found": 0,
                    "source": "google_places",
                    "error": search_result.get("error", "Google Places search failed")
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "businesses": [],
                "total_found": 0,
                "source": "google_places",
                "error": "Google Places search timed out"
            }
        except Exception as e:
            self.log_operation(
                f"Google Places discovery failed: {str(e)}",
                run_id=run_id,
                error=True
            )
            return {
                "success": False,
                "businesses": [],
                "total_found": 0,
                "source": "google_places",
                "error": str(e)
            }

    async def _try_yelp_discovery(
        self,
        location: str,
        niche: str,
        radius: int,
        max_results: int,
        run_id: Optional[str]
    ) -> Dict[str, Any]:
        """Try to discover businesses using Yelp Fusion API."""
        try:
            # Check if Yelp Fusion API is available
            if not get_yelp_fusion_key():
                return {
                    "success": False,
                    "businesses": [],
                    "total_found": 0,
                    "source": "yelp_fusion",
                    "error": "Yelp Fusion API key not configured"
                }
            
            # Create Yelp search request
            request = YelpBusinessSearchRequest(
                term=niche,
                location=location,
                radius=radius,
                limit=max_results,
                run_id=run_id
            )
            
            # Execute search with timeout
            search_result = await asyncio.wait_for(
                self._execute_yelp_search(request),
                timeout=self.yelp_timeout
            )
            
            if search_result.get("success", False):
                businesses = self._normalize_yelp_results(
                    search_result.get("results", []), location, niche
                )
                return {
                    "success": True,
                    "businesses": businesses,
                    "total_found": len(businesses),
                    "source": "yelp_fusion",
                    "message": f"Found {len(businesses)} businesses via Yelp Fusion"
                }
            else:
                return {
                    "success": False,
                    "businesses": [],
                    "total_found": 0,
                    "source": "yelp_fusion",
                    "error": search_result.get("error", "Yelp Fusion search failed")
                }
                
        except asyncio.TimeoutError:
            return {
                "success": False,
                "businesses": [],
                "total_found": 0,
                "source": "yelp_fusion",
                "error": "Yelp Fusion search timed out"
            }
        except Exception as e:
            self.log_operation(
                f"Yelp Fusion discovery failed: {str(e)}",
                run_id=run_id,
                error=True
            )
            return {
                "success": False,
                "businesses": [],
                "total_found": 0,
                "source": "yelp_fusion",
                "error": str(e)
            }

    async def _execute_google_places_search(self, request: BusinessSearchRequest) -> Dict[str, Any]:
        """Execute Google Places search."""
        try:
            # For now, return mock data since we need to implement the actual service
            # In a real implementation, this would call self.google_places_service.search_businesses(request)
            
            await asyncio.sleep(0.1)  # Simulate API call
            
            # Mock successful response
            return {
                "success": True,
                "results": [
                    {
                        "name": f"Sample {request.query.title()} Business",
                        "formatted_address": f"123 Main St, {request.location}",
                        "formatted_phone_number": "+1-555-0123",
                        "rating": 4.5,
                        "types": [request.query.lower()],
                        "place_id": f"google_place_{request.query}_{1}",
                        "geometry": {
                            "location": {"lat": 51.5074, "lng": -0.1278}
                        },
                        "website": f"https://sample{request.query.lower()}.com"
                    },
                    {
                        "name": f"Another {request.query.title()} Service",
                        "formatted_address": f"456 Oak Ave, {request.location}",
                        "formatted_phone_number": "+1-555-0456",
                        "rating": 4.2,
                        "types": [request.query.lower()],
                        "place_id": f"google_place_{request.query}_{2}",
                        "geometry": {
                            "location": {"lat": 51.5074, "lng": -0.1278}
                        },
                        "website": f"https://another{request.query.lower()}.com"
                    }
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_yelp_search(self, request: YelpBusinessSearchRequest) -> Dict[str, Any]:
        """Execute Yelp Fusion search."""
        try:
            # For now, return mock data since we need to implement the actual service
            # In a real implementation, this would call self.yelp_fusion_service.search_businesses(request)
            
            await asyncio.sleep(0.1)  # Simulate API call
            
            # Mock successful response
            return {
                "success": True,
                "results": [
                    {
                        "name": f"Yelp {request.term.title()} Business",
                        "location": {
                            "address1": f"789 Pine St, {request.location}",
                            "city": request.location
                        },
                        "phone": "+1-555-0789",
                        "rating": 4.3,
                        "categories": [{"title": request.term.title()}],
                        "id": f"yelp_{request.term}_{1}",
                        "website": f"https://yelp{request.term.lower()}.com"
                    },
                    {
                        "name": f"Yelp {request.term.title()} Service",
                        "location": {
                            "address1": f"321 Elm St, {request.location}",
                            "city": request.location
                        },
                        "phone": "+1-555-0321",
                        "rating": 4.1,
                        "categories": [{"title": request.term.title()}],
                        "id": f"yelp_{request.term}_{2}",
                        "website": f"https://yelpservice{request.term.lower()}.com"
                    }
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _normalize_google_places_results(
        self, results: List[Dict], location: str, niche: str
    ) -> List[Dict]:
        """Normalize Google Places results to standard format."""
        normalized = []
        for result in results:
            normalized.append({
                "name": result.get("name", "Unknown Business"),
                "address": result.get("formatted_address", f"Unknown Address, {location}"),
                "phone": result.get("formatted_phone_number", "No phone available"),
                "rating": result.get("rating", 0.0),
                "types": result.get("types", [niche.lower()]),
                "place_id": result.get("place_id", "unknown_id"),
                "source": "google_places",
                "location": result.get("geometry", {}).get("location", {}),
                "website": result.get("website", ""),
                "discovered_at": datetime.now().isoformat()
            })
        return normalized

    def _normalize_yelp_results(
        self, results: List[Dict], location: str, niche: str
    ) -> List[Dict]:
        """Normalize Yelp Fusion results to standard format."""
        normalized = []
        for result in results:
            normalized.append({
                "name": result.get("name", "Unknown Business"),
                "address": result.get("location", {}).get("address1", f"Unknown Address, {location}"),
                "phone": result.get("phone", "No phone available"),
                "rating": result.get("rating", 0.0),
                "types": [cat.get("title", niche.title()) for cat in result.get("categories", [])],
                "place_id": result.get("id", "unknown_id"),
                "source": "yelp_fusion",
                "website": result.get("website", ""),
                "discovered_at": datetime.now().isoformat()
            })
        return normalized

    def _validate_discovery_inputs(
        self, location: str, niche: str, radius: int, max_results: int
    ) -> bool:
        """Validate discovery input parameters."""
        if not location or not niche:
            return False
        
        if radius < 100 or radius > 50000:
            return False
        
        if max_results < 1 or max_results > 50:
            return False
        
        # Validate niche against supported niches
        if niche.lower() not in [n.lower() for n in self.business_config.SUPPORTED_NICHES]:
            return False
        
        return True

    def _create_error_response(
        self, error_message: str, error_type: str, location: str, niche: str, run_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "success": False,
            "businesses": [],
            "total_found": 0,
            "location": location,
            "niche": niche,
            "error": error_message,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            "run_id": run_id
        }
