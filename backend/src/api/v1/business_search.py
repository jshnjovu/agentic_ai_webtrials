"""
Business search API endpoints for SerpAPI integration.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import uuid
from src.schemas import (
    BusinessSearchRequest, BusinessSearchResponse, BusinessSearchError,
    LocationType
)
from src.schemas.yelp_fusion import (
    YelpBusinessSearchRequest, YelpBusinessSearchResponse, YelpBusinessSearchError,
    YelpLocationType
)
from src.services import SerpAPIService, YelpFusionService, BusinessSearchFallbackService

router = APIRouter(prefix="/business-search", tags=["business-search"])


def get_business_search_service() -> BusinessSearchFallbackService:
    """Dependency to get business search service with automatic fallback."""
    return BusinessSearchFallbackService()


def get_yelp_fusion_service() -> YelpFusionService:
    """Dependency to get Yelp Fusion service instance."""
    return YelpFusionService()


def get_serpapi_service() -> SerpAPIService:
    """Dependency to get SerpAPI service instance."""
    return SerpAPIService()


@router.post("/serpapi/search", response_model=BusinessSearchResponse)
async def search_businesses(
    request: BusinessSearchRequest,
    service: SerpAPIService = Depends(get_serpapi_service)
) -> BusinessSearchResponse:
    """
    Search for businesses using SerpAPI directly.
    
    Args:
        request: Business search request with query, location, and filters
        service: SerpAPI service instance
        
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
        
        # Execute SerpAPI search directly (async)
        result = await service.search_businesses(request)
        
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


@router.post("/serpapi/search/with-fallback", response_model=BusinessSearchResponse)
async def search_businesses_with_fallback(
    request: BusinessSearchRequest,
    service: BusinessSearchFallbackService = Depends(get_business_search_service)
) -> BusinessSearchResponse:
    """
    Search for businesses using SerpAPI with automatic fallback to Yelp Fusion.
    
    Args:
        request: Business search request with query, location, and filters
        service: Business search service with automatic fallback
        
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
        
        # Execute search with automatic fallback
        result = service.search_businesses_with_fallback(request)
        
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


@router.get("/serpapi/search", response_model=BusinessSearchResponse)
async def search_businesses_get(
    query: str = Query(..., description="Search query for businesses", min_length=1, max_length=200),
    location: str = Query(..., description="Location to search in (city, address, coordinates, or zip code)"),
    location_type: LocationType = Query(default=LocationType.CITY, description="Type of location input"),
    category: Optional[str] = Query(None, description="Business category or type to filter by", max_length=100),
    radius: Optional[int] = Query(default=5000, description="Search radius in meters (max 50000)", ge=100, le=50000),
    max_results: Optional[int] = Query(default=4, description="Maximum number of results to return", ge=1, le=20),
    run_id: Optional[str] = Query(None, description="Unique identifier for the processing run"),
    service: SerpAPIService = Depends(get_serpapi_service)
) -> BusinessSearchResponse:
    """
    Search for businesses using SerpAPI directly (GET endpoint).
    
    Args:
        query: Search query for businesses
        location: Location to search in
        location_type: Type of location input
        category: Business category filter
        radius: Search radius in meters
        max_results: Maximum number of results
        run_id: Optional run identifier
        service: SerpAPI service instance
        
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
        
        # Execute SerpAPI search directly (async)
        result = await service.search_businesses(request)
        
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
    service: BusinessSearchFallbackService = Depends(get_business_search_service)
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
        
        # Execute search with automatic fallback
        result = service.search_businesses_with_fallback(request)
        
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
async def get_google_places_next_page(
    next_page_token: str = Query(..., description="Token for next page from previous search"),
    run_id: Optional[str] = Query(None, description="Unique identifier for the processing run"),
    service: SerpAPIService = Depends(get_serpapi_service)
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


@router.get("/serpapi/next-page")
async def get_serpapi_next_page(
    next_page_token: str = Query(..., description="Token for next page from previous search"),
    run_id: Optional[str] = Query(None, description="Unique identifier for the processing run"),
    service: SerpAPIService = Depends(get_serpapi_service)
):
    """
    Get next page of results for SerpAPI search.
    
    Args:
        next_page_token: Token for next page from previous search
        run_id: Optional run identifier
        service: SerpAPI service instance
        
    Returns:
        Next page of business search results
        
    Raises:
        HTTPException: If next page retrieval fails
    """
    try:
        # Generate run_id if not provided
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # For now, return a placeholder response since SerpAPI doesn't have next-page tokens
        # This endpoint is kept for compatibility but will need to be implemented differently
        raise HTTPException(
            status_code=501,
            detail="Next page functionality not yet implemented for SerpAPI"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during next page retrieval: {str(e)}"
        )


@router.post("/yelp-fusion/search", response_model=YelpBusinessSearchResponse)
async def search_yelp_businesses(
    request: YelpBusinessSearchRequest,
    service: YelpFusionService = Depends(get_yelp_fusion_service)
) -> YelpBusinessSearchResponse:
    """
    Search for businesses using Yelp Fusion API.
    
    Args:
        request: Yelp business search request with term, location, and filters
        service: Yelp Fusion service instance
        
    Returns:
        Yelp business search response with results
        
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
                detail="Invalid Yelp business search request"
            )
        
        # Execute search
        result = service.search_businesses(request)
        
        # Handle error responses
        if isinstance(result, YelpBusinessSearchError):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result.error,
                    "error_code": result.error_code,
                    "context": result.context,
                    "term": result.term,
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
            detail=f"Internal server error during Yelp business search: {str(e)}"
        )


@router.get("/yelp-fusion/search", response_model=YelpBusinessSearchResponse)
async def search_yelp_businesses_get(
    term: str = Query(..., description="Search term for businesses", min_length=1, max_length=200),
    location: str = Query(..., description="Location to search in (city, address, coordinates, or zip code)"),
    location_type: YelpLocationType = Query(default=YelpLocationType.CITY, description="Type of location input"),
    categories: Optional[str] = Query(None, description="Comma-separated list of business categories to filter by"),
    radius: Optional[int] = Query(default=40000, description="Search radius in meters (max 40000)", ge=100, le=40000),
    limit: Optional[int] = Query(default=20, description="Maximum number of results to return", ge=1, le=50),
    offset: Optional[int] = Query(default=0, description="Offset for pagination", ge=0),
    sort_by: Optional[str] = Query(default="best_match", description="Sort order: best_match, rating, review_count, distance"),
    price: Optional[str] = Query(None, description="Price filter: 1, 2, 3, 4 (1=$, 4=$$$$)"),
    open_now: Optional[bool] = Query(None, description="Filter for businesses currently open"),
    run_id: Optional[str] = Query(None, description="Unique identifier for the processing run"),
    service: YelpFusionService = Depends(get_yelp_fusion_service)
) -> YelpBusinessSearchResponse:
    """
    Search for businesses using Yelp Fusion API (GET endpoint).
    
    Args:
        term: Search term for businesses
        location: Location to search in
        location_type: Type of location input
        categories: Business category filters
        radius: Search radius in meters
        limit: Maximum number of results
        offset: Offset for pagination
        sort_by: Sort order
        price: Price filter
        open_now: Open now filter
        run_id: Optional run identifier
        service: Yelp Fusion service instance
        
    Returns:
        Yelp business search response with results
        
    Raises:
        HTTPException: If search fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not run_id:
            run_id = str(uuid.uuid4())
        
        # Parse categories if provided
        category_list = None
        if categories:
            category_list = [cat.strip() for cat in categories.split(",") if cat.strip()]
        
        # Create request object
        request = YelpBusinessSearchRequest(
            term=term,
            location=location,
            location_type=location_type,
            categories=category_list,
            radius=radius,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            price=price,
            open_now=open_now,
            run_id=run_id
        )
        
        # Validate request
        if not service.validate_input(request):
            raise HTTPException(
                status_code=400,
                detail="Invalid Yelp business search request"
            )
        
        # Execute search
        result = service.search_businesses(request)
        
        # Handle error responses
        if isinstance(result, YelpBusinessSearchError):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result.error,
                    "error_code": result.error_code,
                    "context": result.context,
                    "term": result.term,
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
            detail=f"Internal server error during Yelp business search: {str(e)}"
        )


@router.get("/yelp-fusion/search/health")
async def yelp_health_check(
    service: YelpFusionService = Depends(get_yelp_fusion_service)
):
    """
    Health check endpoint for Yelp Fusion business search service.
    
    Args:
        service: Yelp Fusion service instance
        
    Returns:
        Health status of the service
    """
    try:
        # Simple health check - try to create service instance
        if service and hasattr(service, 'search_businesses'):
            return {
                "status": "healthy",
                "service": "YelpFusionService",
                "message": "Service is operational",
                "capabilities": [
                    "business_search",
                    "location_validation",
                    "data_extraction",
                    "rate_limiting"
                ]
            }
        else:
            return {
                "status": "unhealthy",
                "service": "YelpFusionService",
                "message": "Service not properly initialized"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "YelpFusionService",
            "message": f"Service health check failed: {str(e)}"
        }


@router.get("/serpapi/search/health")
async def health_check(
    service: SerpAPIService = Depends(get_serpapi_service)
):
    """
    Health check endpoint for SerpAPI business search service.
    
    Args:
        service: SerpAPI service instance
        
    Returns:
        Health status of the service
    """
    try:
        # Simple health check - try to create service instance
        if service and hasattr(service, 'search_businesses'):
            return {
                "status": "healthy",
                "service": "SerpAPIService",
                "message": "Service is operational",
                "capabilities": [
                    "serpapi_business_search",
                    "business_search",
                    "location_validation",
                    "pagination",
                    "rate_limiting"
                ]
            }
        else:
            return {
                "status": "unhealthy",
                "service": "SerpAPIService",
                "message": "Service not properly initialized"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "SerpAPIService",
            "message": f"Service health check failed: {str(e)}"
        }


@router.get("/health")
async def business_search_health_check(
    service: BusinessSearchFallbackService = Depends(get_business_search_service)
):
    """
    Health check endpoint for the main business search service with fallback.
    
    Args:
        service: Business search fallback service instance
        
    Returns:
        Health status of the service
    """
    try:
        # Simple health check - try to create service instance
        if service and hasattr(service, 'search_businesses_with_fallback'):
            return {
                "status": "healthy",
                "service": "BusinessSearchFallbackService",
                "message": "Service is operational with SerpAPI primary and Yelp Fusion fallback",
                "capabilities": [
                    "serpapi_business_search",
                    "yelp_fusion_fallback",
                    "automatic_fallback",
                    "rate_limiting",
                    "confidence_scoring"
                ],
                "primary_api": "SerpAPI",
                "fallback_api": "Yelp Fusion"
            }
        else:
            return {
                "status": "unhealthy",
                "service": "BusinessSearchFallbackService",
                "message": "Service not properly initialized"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "BusinessSearchFallbackService",
            "message": f"Service health check failed: {str(e)}"
        }
