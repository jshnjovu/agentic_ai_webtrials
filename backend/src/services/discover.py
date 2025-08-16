"""
Discovery Service
This service is responsible for discovering businesses from multiple sources,
merging the results, and deduplicating the data.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from src.services import GooglePlacesService, YelpFusionService
from src.schemas import BusinessSearchRequest as GoogleBusinessSearchRequest
from src.schemas.yelp_fusion import YelpBusinessSearchRequest
from src.services.duplicate_detection_service import DuplicateDetectionService
from src.schemas.business_matching import BusinessSourceData, BusinessLocation, BusinessContactInfo

logger = logging.getLogger(__name__)


class DiscoveryService:
    """
    Orchestrates business discovery from multiple sources, merging, and deduplication.
    """

    def __init__(self):
        self.google_places_service = GooglePlacesService()
        self.yelp_fusion_service = YelpFusionService()
        self.duplicate_detection_service = DuplicateDetectionService()

    async def discover_businesses(
        self,
        location: str,
        niche: str,
        max_results: int = 10,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Discover businesses from multiple sources based on location and niche.
        Args:
            location: The location to search in (e.g., city, address, ZIP code).
            niche: The business niche or category to search for.
            max_results: The maximum number of businesses to discover.
            run_id: An optional unique identifier for the processing run.
        Returns:
            A dictionary containing the discovery results or an error message.
        """
        try:
            logger.info(
                f"🔍 Starting business discovery for niche '{niche}' in '{location}'"
            )
            google_request = GoogleBusinessSearchRequest(
                query=niche, location=location, max_results=max_results, run_id=run_id
            )
            yelp_request = YelpBusinessSearchRequest(
                term=niche, location=location, limit=max_results, run_id=run_id
            )
            results = await asyncio.gather(
                self._search_google_places(google_request),
                self._search_yelp_fusion(yelp_request),
            )
            
            processed_results = self._process_and_combine_results(results, run_id)
            
            return {"success": True, "results": processed_results}
        
        except Exception as e:
            logger.error(f"❌ Business discovery failed: {e}")
            return {
                "success": False,
                "error_details": f"An unexpected error occurred during business discovery: {str(e)}",
            }

    async def _search_google_places(
        self, request: GoogleBusinessSearchRequest
    ) -> Dict[str, Any]:
        """Helper method to search Google Places."""
        try:
            return self.google_places_service.search_businesses(request)
        except Exception as e:
            logger.error(f"❌ Google Places search failed: {e}")
            return {"error": "Google Places search failed", "details": str(e)}

    async def _search_yelp_fusion(
        self, request: YelpBusinessSearchRequest
    ) -> Dict[str, Any]:
        """Helper method to search Yelp Fusion."""
        try:
            return self.yelp_fusion_service.search_businesses(request)
        except Exception as e:
            logger.error(f"❌ Yelp Fusion search failed: {e}")
            return {"error": "Yelp Fusion search failed", "details": str(e)}

    def _process_and_combine_results(
        self, results: List[Dict[str, Any]], run_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Process and combine results from different search services."""
        
        google_results, yelp_results = results
        
        normalized_businesses = []
        
        if google_results and not google_results.get("error"):
            for business in google_results.get("results", []):
                normalized_businesses.append(self._normalize_google_business(business))
        
        if yelp_results and not yelp_results.get("error"):
            for business in yelp_results.get("businesses", []):
                normalized_businesses.append(self._normalize_yelp_business(business))
        
        if not normalized_businesses:
            return []

        business_source_data = [self._create_business_source_data(b) for b in normalized_businesses]

        deduplication_request = self.duplicate_detection_service.DuplicateDetectionRequest(
            businesses=business_source_data,
            detection_threshold=0.8,
            run_id=run_id
        )
        deduplication_response = self.duplicate_detection_service.detect_duplicates(deduplication_request)

        return [b.dict() for b in deduplication_response.unique_businesses]

    def _normalize_google_business(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a business from Google Places to a common format."""
        return {
            "id": business.get("place_id"),
            "name": business.get("name"),
            "address": business.get("formatted_address"),
            "latitude": business.get("geometry", {}).get("location", {}).get("lat"),
            "longitude": business.get("geometry", {}).get("location", {}).get("lng"),
            "phone": business.get("formatted_phone_number"),
            "website": business.get("website"),
            "categories": business.get("types", []),
            "source": "google",
        }

    def _normalize_yelp_business(self, business: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes a business from Yelp Fusion to a common format."""
        return {
            "id": business.get("id"),
            "name": business.get("name"),
            "address": " ".join(business.get("location", {}).get("display_address", [])),
            "latitude": business.get("coordinates", {}).get("latitude"),
            "longitude": business.get("coordinates", {}).get("longitude"),
            "phone": business.get("display_phone"),
            "website": business.get("url"),
            "categories": [c["alias"] for c in business.get("categories", [])],
            "source": "yelp",
        }

    def _create_business_source_data(self, business_data: Dict[str, Any]) -> BusinessSourceData:
        """Creates a BusinessSourceData object from a dictionary."""
        return BusinessSourceData(
            source_id=business_data.get("id"),
            name=business_data.get("name"),
            location=BusinessLocation(
                address=business_data.get("address"),
                latitude=business_data.get("latitude"),
                longitude=business_data.get("longitude"),
            ),
            contact_info=BusinessContactInfo(
                phone=business_data.get("phone"),
                website=business_data.get("website"),
            ),
            categories=business_data.get("categories", []),
        )
