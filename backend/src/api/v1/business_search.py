"""
Business search API endpoints for Google Places integration.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import uuid
from src.schemas import (
    BusinessSearchRequest, BusinessSearchResponse, BusinessSearchError,
    LocationType
)
from src.services import GooglePlacesService

router = APIRouter(prefix="/business-search", tags=["business-search"])


def get_google_places_service() -> GooglePlacesService:
    """Dependency to get Google Places service instance."""
    return GooglePlacesService()


@router.post("/google-places/search", response_model=BusinessSearchResponse)
async def search_businesses(
    request: BusinessSearchRequest,
    service: GooglePlacesService = Depends(get_google_places_service)
) -> BusinessSearchResponse:
    """
    Search for businesses using Google Places API.
    
    Args:
        request: Business search request with query, location, and filters
        service: Google Places service instance
        
    Returns:
        Business search response with results
        
    Raises:
        HTTPException: If search fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not request.run_id:
            request.run_id = str(uuid.uuid4())
        
        # Validate request
        if not service.validate_input(request):
            raise HTTPException(
                status_code=400,
                detail="Invalid business search request"
            )
        
        # Execute search
        result = service.search_businesses(request)
        
        # Handle error responses
        if isinstance(result, BusinessSearchError):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result.error,
                    "error_code": result.error_code,
                    "context": result.context,
                    "query": result.query,
                    "location": result.location
                }
            )
        
        # Return successful response
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during business search: {str(e)}"
        )


@router.get("/google-places/search", response_model=BusinessSearchResponse)
async def search_businesses_get(
    query: str = Query(..., description="Search query for businesses", min_length=1, max_length=200),
    location: str = Query(..., description="Location to search in (city, address, coordinates, or zip code)"),
    location_type: LocationType = Query(default=LocationType.CITY, description="Type of location input"),
    category: Optional[str] = Query(None, description="Business category or type to filter by", max_length=100),
    radius: Optional[int] = Query(default=5000, description="Search radius in meters (max 50000)", ge=100, le=50000),
    max_results: Optional[int] = Query(default=10, description="Maximum number of results to return", ge=1, le=20),
    run_id: Optional[str] = Query(None, description="Unique identifier for the processing run"),
    service: GooglePlacesService = Depends(get_google_places_service)
) -> BusinessSearchResponse:
    """
    Search for businesses using Google Places API (GET endpoint).
    
    Args:
        query: Search query for businesses
        location: Location to search in
        location_type: Type of location input
        category: Business category filter
        radius: Search radius in meters
        max_results: Maximum number of results
        run_id: Optional run identifier
        service: Google Places service instance
        
    Returns:
        Business search response with results
        
    Raises:
        HTTPException: If search fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Create request object
        request = BusinessSearchRequest(
            query=query,
            location=location,
            location_type=location_type,
            category=category,
            radius=radius,
            max_results=max_results,
            run_id=run_id
        )
        
        # Validate request
        if not service.validate_input(request):
            raise HTTPException(
                status_code=400,
                detail="Invalid business search request"
            )
        
        # Execute search
        result = service.search_businesses(request)
        
        # Handle error responses
        if isinstance(result, BusinessSearchError):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result.error,
                    "error_code": result.error_code,
                    "context": result.context,
                    "query": result.query,
                    "location": result.location
                }
            )
        
        # Return successful response
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during business search: {str(e)}"
        )


@router.get("/google-places/next-page")
async def get_next_page(
    next_page_token: str = Query(..., description="Token for next page from previous search"),
    run_id: Optional[str] = Query(None, description="Unique identifier for the processing run"),
    service: GooglePlacesService = Depends(get_google_places_service)
):
    """
    Get next page of business search results using pagination token.
    
    Args:
        next_page_token: Token for next page from previous search
        run_id: Optional run identifier for the processing run
        service: Google Places service instance
        
    Returns:
        Next page of business search results
        
    Raises:
        HTTPException: If pagination fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Validate token
        if not next_page_token or len(next_page_token.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Next page token is required"
            )
        
        # Execute pagination request
        result = service.get_next_page(next_page_token, run_id)
        
        # Handle error responses
        if not result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result.get("error", "Unknown error"),
                    "error_code": result.get("error_code"),
                    "context": "pagination_request"
                }
            )
        
        # Return successful response
        return {
            "success": True,
            "results": result.get("results", []),
            "next_page_token": result.get("next_page_token"),
            "api_status": result.get("api_status"),
            "run_id": run_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during pagination: {str(e)}"
        )


@router.get("/google-places/search/health")
async def health_check(
    service: GooglePlacesService = Depends(get_google_places_service)
):
    """
    Health check endpoint for Google Places business search service.
    
    Args:
        service: Google Places service instance
        
    Returns:
        Health status of the service
    """
    try:
        # Simple health check - try to create service instance
        if service and hasattr(service, 'search_businesses'):
            return {
                "status": "healthy",
                "service": "GooglePlacesService",
                "message": "Service is operational",
                "capabilities": [
                    "business_search",
                    "location_validation",
                    "pagination",
                    "rate_limiting"
                ]
            }
        else:
            return {
                "status": "unhealthy",
                "service": "GooglePlacesService",
                "message": "Service not properly initialized"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "GooglePlacesService",
            "message": f"Service health check failed: {str(e)}"
        }
