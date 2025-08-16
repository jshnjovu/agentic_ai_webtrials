"""
Authentication API endpoints for external API integrations.
Provides endpoints for testing authentication and connection status.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import uuid
from datetime import datetime

from src.schemas import (
    GooglePlacesAuthRequest,
    YelpFusionAuthRequest,
    AuthenticationResponse,
    HealthCheckResponse,
)
from src.services import GooglePlacesAuthService, YelpFusionAuthService
from src.core import validate_environment

router = APIRouter(prefix="/auth", tags=["authentication"])

# Service instances
google_places_service = GooglePlacesAuthService()
yelp_fusion_service = YelpFusionAuthService()


def get_run_id() -> str:
    """Generate a unique run ID for tracking operations."""
    return str(uuid.uuid4())


@router.post("/google-places", response_model=AuthenticationResponse)
async def authenticate_google_places(
    request: GooglePlacesAuthRequest,
) -> AuthenticationResponse:
    """
    Authenticate with Google Places API.

    Args:
        request: Authentication request with run ID

    Returns:
        Authentication result
    """
    try:
        # Validate environment configuration
        if not validate_environment():
            raise HTTPException(
                status_code=500, detail="Environment configuration validation failed"
            )

        # Authenticate with Google Places API
        result = google_places_service.authenticate(request.run_id)

        if result["success"]:
            return AuthenticationResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/yelp-fusion", response_model=AuthenticationResponse)
async def authenticate_yelp_fusion(
    request: YelpFusionAuthRequest,
) -> AuthenticationResponse:
    """
    Authenticate with Yelp Fusion API.

    Args:
        request: Authentication request with run ID

    Returns:
        Authentication result
    """
    try:
        # Validate environment configuration
        if not validate_environment():
            raise HTTPException(
                status_code=500, detail="Environment configuration validation failed"
            )

        # Authenticate with Yelp Fusion API
        result = yelp_fusion_service.authenticate(request.run_id)

        if result["success"]:
            return AuthenticationResponse(**result)
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint for API connectivity.

    Returns:
        Overall health status of all APIs
    """
    try:
        run_id = get_run_id()

        # Check Google Places API health
        google_health = google_places_service.get_health_status(run_id)

        # Check Yelp Fusion API health
        yelp_health = yelp_fusion_service.get_health_status(run_id)

        # Determine overall status
        overall_status = "healthy"
        if not google_health["success"] or not yelp_health["success"]:
            overall_status = "unhealthy"

        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.utcnow().isoformat(),
            apis={"google_places": google_health, "yelp_fusion": yelp_health},
            run_id=run_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/google-places/health")
async def google_places_health() -> Dict[str, Any]:
    """
    Health check for Google Places API only.

    Returns:
        Google Places API health status
    """
    try:
        run_id = get_run_id()
        result = google_places_service.get_health_status(run_id)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Google Places health check failed: {str(e)}"
        )


@router.get("/yelp-fusion/health")
async def yelp_fusion_health() -> Dict[str, Any]:
    """
    Health check for Yelp Fusion API only.

    Returns:
        Yelp Fusion API health status
    """
    try:
        run_id = get_run_id()
        result = yelp_fusion_service.get_health_status(run_id)
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Yelp Fusion health check failed: {str(e)}"
        )
