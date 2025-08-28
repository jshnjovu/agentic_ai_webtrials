"""
Business Search Fallback Service.
Automatically falls back from SerpAPI to Yelp Fusion when the primary API fails.
"""

import logging
from typing import Dict, Any, Optional, Union
from ...core.base_service import BaseService
from ...schemas.business_search import BusinessSearchRequest, BusinessSearchResponse, BusinessSearchError, BusinessData
from ...schemas.yelp_fusion import YelpBusinessSearchRequest, YelpBusinessSearchResponse, YelpBusinessSearchError
from ..external_apis.serpapi_service import SerpAPIService
from ..external_apis.yelp_fusion_service import YelpFusionService
from ..scoring.confidence_scoring_service import ConfidenceScoringService


class BusinessSearchFallbackService(BaseService):
    """Service that automatically falls back between business search APIs."""
    
    def __init__(self):
        super().__init__("BusinessSearchFallbackService")
        self.serpapi_service = SerpAPIService()
        self.yelp_fusion_service = YelpFusionService()
        self.confidence_service = ConfidenceScoringService()
        
        # API configuration
        self.primary_api = "serpapi"
        self.enable_automatic_fallback = False
        
        # Error patterns that trigger immediate fallback
        self.immediate_fallback_errors = [
            "BILLING_DISABLED",
            "PERMISSION_DENIED", 
            "API_NOT_ENABLED",
            "QUOTA_EXCEEDED",
            "RATE_LIMIT_EXCEEDED"
        ]
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, BusinessSearchRequest)
    
    async def search_businesses_with_fallback(self, request: BusinessSearchRequest) -> Union[BusinessSearchResponse, BusinessSearchError]:
        """
        Search for businesses using SerpAPI as primary API.
        
        Args:
            request: Business search request
            
        Returns:
            Business search response or error details
        """
        try:
            self.log_operation(
                f"Starting business search with SerpAPI: '{request.query}' in {request.location}", 
                run_id=request.run_id
            )
            
            # Use SerpAPI as primary API
            serpapi_result = self._try_serpapi_search(request)
            
            if serpapi_result.success:
                self.log_operation(
                    f"SerpAPI search successful: {len(serpapi_result.results)} results",
                    run_id=request.run_id
                )
                
                # Add confidence scores to SerpAPI results
                return self._add_confidence_scores(serpapi_result, request)
            
            else:
                self.log_operation(
                    f"SerpAPI failed: {serpapi_result.error}",
                    run_id=request.run_id
                )
                
                # Try Yelp Fusion as fallback
                yelp_result = await self._try_yelp_fusion_search(request)
                if yelp_result.success:
                    self.log_operation(
                        f"Yelp Fusion fallback successful: {len(yelp_result.businesses)} results",
                        run_id=request.run_id
                    )
                    return self._convert_yelp_to_standard_response(yelp_result, request)
                else:
                    return BusinessSearchError(
                        error=f"Both SerpAPI and Yelp Fusion failed. SerpAPI: {serpapi_result.error}, Yelp: {yelp_result.error}",
                        error_code="ALL_APIS_FAILED",
                        context="fallback_search",
                        query=request.query,
                        location=request.location,
                        run_id=request.run_id,
                        details={
                            "serpapi_error": serpapi_result.error,
                            "yelp_error": yelp_result.error
                        }
                    )
                
        except Exception as e:
            self.log_error(e, "business_search_with_fallback", request.run_id)
            return BusinessSearchError(
                error=f"Unexpected error during business search: {str(e)}",
                context="unexpected_error",
                query=request.query,
                location=request.location,
                run_id=request.run_id
            )
    
    def _try_serpapi_search(self, request: BusinessSearchRequest) -> Union[BusinessSearchResponse, BusinessSearchError]:
        """Try SerpAPI search."""
        try:
            return self.serpapi_service.search_businesses(request)
        except Exception as e:
            self.logger.warning(f"SerpAPI search failed: {str(e)}")
            return BusinessSearchError(
                error=f"SerpAPI search failed: {str(e)}",
                error_code="SERPAPI_FAILED",
                context="serpapi_search",
                query=request.query,
                location=request.location,
                run_id=request.run_id
            )
    
    async def _try_yelp_fusion_search(self, request: BusinessSearchRequest) -> Union[YelpBusinessSearchResponse, YelpBusinessSearchError]:
        """Try Yelp Fusion search."""
        try:
            # Convert BusinessSearchRequest to YelpBusinessSearchRequest
            yelp_request = YelpBusinessSearchRequest(
                term=request.query,
                location=request.location,
                location_type=self._convert_location_type(request.location_type),
                categories=[request.category] if request.category else None,
                radius=request.radius,
                limit=request.max_results,
                run_id=request.run_id
            )
            
            return await self.yelp_fusion_service.search_businesses(yelp_request)
            
        except Exception as e:
            self.logger.warning(f"Yelp Fusion search failed: {str(e)}")
            return YelpBusinessSearchError(
                error=f"Yelp Fusion search failed: {str(e)}",
                error_code="YELP_FUSION_FAILED",
                context="yelp_fusion_search",
                term=request.query,
                location=request.location,
                run_id=request.run_id
            )
    
    def _should_fallback(self, primary_result: BusinessSearchError) -> bool:
        """Determine if we should fallback based on the error."""
        if not self.enable_automatic_fallback:
            return False
        
        # Check for immediate fallback errors
        error_code = primary_result.error_code or ""
        error_message = primary_result.error or ""
        
        for fallback_error in self.immediate_fallback_errors:
            if fallback_error in error_code.upper() or fallback_error in error_message.upper():
                self.logger.info(f"Immediate fallback triggered due to error: {fallback_error}")
                return True
        
        # Check for other fallback-worthy errors
        if "HTTP_403" in error_code or "PERMISSION_DENIED" in error_message:
            return True
        
        if "HTTP_429" in error_code or "RATE_LIMIT" in error_message:
            return True
        
        if "HTTP_500" in error_code or "INTERNAL_SERVER_ERROR" in error_message:
            return True
        
        return False
    
    def _convert_location_type(self, location_type) -> str:
        """Convert BusinessSearchRequest location type to Yelp location type."""
        type_mapping = {
            "city": "city",
            "coordinates": "coordinates", 
            "address": "address",
            "zip_code": "zip_code"
        }
        return type_mapping.get(location_type.value, "city")
    
    def _add_confidence_scores(self, serpapi_result: BusinessSearchResponse, request: BusinessSearchRequest) -> BusinessSearchResponse:
        """Add confidence scores to SerpAPI results."""
        try:
            for business in serpapi_result.results:
                # Calculate confidence score for each business
                confidence_score = self._calculate_simple_confidence(business)
                business.confidence_level = confidence_score
            
            return serpapi_result
            
        except Exception as e:
            self.logger.warning(f"Error adding confidence scores: {str(e)}")
            # Return original result if confidence calculation fails
            return serpapi_result
    
    def _convert_yelp_to_standard_response(self, yelp_result: YelpBusinessSearchResponse, request: BusinessSearchRequest) -> BusinessSearchResponse:
        """Convert Yelp response to standard BusinessSearchResponse format."""
        try:
            from src.schemas.business_search import BusinessData
            
            # Convert Yelp businesses to standard format
            standard_businesses = []
            
            for yelp_business in yelp_result.businesses:
                # Create standard business data
                business_data = BusinessData(
                    place_id=yelp_business.id,
                    name=yelp_business.name,
                    address=yelp_business.location.display_address[0] if yelp_business.location.display_address else None,
                    phone=yelp_business.phone,
                    website=yelp_business.url,
                    rating=yelp_business.rating,
                    user_ratings_total=yelp_business.review_count,
                    price_level=self._convert_yelp_price_to_standard(yelp_business.price),
                    types=[cat.title for cat in yelp_business.categories],
                    geometry={
                        "location": {
                            "lat": yelp_business.coordinates.latitude,
                            "lng": yelp_business.coordinates.longitude
                        }
                    },
                    formatted_address=", ".join(yelp_business.location.display_address) if yelp_business.location.display_address else None,
                    international_phone_number=yelp_business.display_phone,
                    opening_hours=self._convert_yelp_hours(yelp_business.hours),
                    photos=[{"url": photo} for photo in (yelp_business.photos or [])] if yelp_business.photos else [],
                    reviews=None  # Yelp doesn't provide reviews in basic search
                )
                
                # Add confidence score using adapted data format
                business_data.confidence_level = self._calculate_confidence_for_business_data(business_data)
                
                standard_businesses.append(business_data)
            
            # Create standard response
            return BusinessSearchResponse(
                success=True,
                query=request.query,
                location=request.location,
                total_results=len(standard_businesses),
                results=standard_businesses,
                next_page_token=None,  # Yelp uses offset-based pagination
                run_id=request.run_id,
                search_metadata={
                    "source": "yelp_fusion_primary",
                    "original_request": request.model_dump(),
                    "api_used": "yelp_fusion"
                }
            )
            
        except Exception as e:
            self.log_error(e, "convert_yelp_to_standard_response", request.run_id)
            raise
    
    def _convert_yelp_price_to_standard(self, yelp_price: Optional[str]) -> Optional[int]:
        """Convert Yelp price format ($, $$, $$$, $$$$) to standard format (1, 2, 3, 4)."""
        if not yelp_price:
            return None
        
        price_mapping = {
            "$": 1,
            "$$": 2, 
            "$$$": 3,
            "$$$$": 4
        }
        
        return price_mapping.get(yelp_price, None)
    
    def _convert_yelp_hours(self, yelp_hours: Optional[list]) -> Optional[Dict[str, Any]]:
        """Convert Yelp hours format to standard format."""
        if not yelp_hours:
            return None
        
        # Convert Yelp hours to standard format
        # This is a simplified conversion - you might want to enhance this
        return {
            "open_now": None,  # Yelp doesn't provide this in basic search
            "periods": yelp_hours,
            "weekday_text": []  # Would need to generate this from periods
        }
    
    def _calculate_confidence_for_business_data(self, business_data: BusinessData) -> str:
        """
        Calculate confidence for BusinessData by adapting it to the format expected by ConfidenceScoringService.
        """
        try:
            from src.schemas.business_matching import BusinessSourceData, BusinessLocation, BusinessContactInfo
            
            # Extract coordinates from geometry
            lat = None
            lng = None
            if business_data.geometry and "location" in business_data.geometry:
                lat = business_data.geometry["location"].get("lat")
                lng = business_data.geometry["location"].get("lng")
            
            # Parse address components (simplified)
            address_parts = business_data.formatted_address.split(", ") if business_data.formatted_address else []
            city = address_parts[1] if len(address_parts) > 1 else None
            state = address_parts[2] if len(address_parts) > 2 else None
            zip_code = address_parts[3] if len(address_parts) > 3 else None
            
            # Create BusinessLocation object
            location = BusinessLocation(
                latitude=lat,
                longitude=lng,
                address=business_data.address,
                city=city,
                state=state,
                zip_code=zip_code,
                country="UK" if "UK" in (business_data.formatted_address or "") else None
            )
            
            # Create BusinessContactInfo object
            contact_info = BusinessContactInfo(
                phone=business_data.phone,
                website=business_data.website,
                email=None,  # Yelp doesn't provide email
                social_media=None  # Yelp doesn't provide social media
            )
            
            # Create BusinessSourceData object that the confidence service expects
            source_data = BusinessSourceData(
                source="yelp_fusion",
                source_id=business_data.place_id,
                name=business_data.name,
                location=location,
                contact_info=contact_info,
                rating=business_data.rating,
                review_count=business_data.user_ratings_total,
                categories=business_data.types,
                price_level=business_data.price_level,
                hours=business_data.opening_hours,
                photos=business_data.photos,
                raw_data=None,
                last_updated=None
            )
            
            # Now use the confidence service
            confidence_score = self.confidence_service.calculate_data_confidence(source_data)
            confidence_level = self.confidence_service.assign_confidence_level(confidence_score)
            
            # Convert ConfidenceLevel enum to string
            return confidence_level.value
            
        except Exception as e:
            self.logger.warning(f"Error calculating confidence using service: {str(e)}")
            # Fallback to simple confidence calculation
            return self._calculate_simple_confidence(business_data)
    
    def _calculate_simple_confidence(self, business_data: BusinessData) -> str:
        """
        Simple confidence calculation as fallback when the main service fails.
        """
        try:
            confidence_score = 0.0
            total_fields = 0
            
            # Name confidence
            if business_data.name and business_data.name.strip():
                confidence_score += 0.8
            total_fields += 1
            
            # Location confidence
            if business_data.geometry and business_data.geometry.get("location"):
                confidence_score += 0.9
            elif business_data.address:
                confidence_score += 0.7
            total_fields += 1
            
            # Contact confidence
            if business_data.phone or business_data.website:
                confidence_score += 0.8
            total_fields += 1
            
            # Rating confidence
            if business_data.rating is not None:
                confidence_score += 0.9
            total_fields += 1
            
            # Categories confidence
            if business_data.types and len(business_data.types) > 0:
                confidence_score += 0.8
            total_fields += 1
            
            # Hours confidence
            if business_data.opening_hours:
                confidence_score += 0.6
            total_fields += 1
            
            # Calculate average confidence
            avg_confidence = confidence_score / total_fields if total_fields > 0 else 0.0
            
            # Assign confidence level
            if avg_confidence >= 0.8:
                return "high"
            elif avg_confidence >= 0.6:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            self.logger.warning(f"Error in simple confidence calculation: {str(e)}")
            return "medium"  # Default fallback
