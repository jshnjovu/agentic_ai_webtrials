"""
Authentication schemas for API requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class AuthenticationRequest(BaseModel):
    """Base authentication request model."""

    api_name: str = Field(..., description="Name of the API to authenticate with")
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )


class AuthenticationResponse(BaseModel):
    """Base authentication response model."""

    success: bool = Field(..., description="Whether authentication was successful")
    api_name: str = Field(..., description="Name of the API that was authenticated")
    message: str = Field(
        ..., description="Human-readable message about the authentication result"
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )
    error: Optional[str] = Field(
        None, description="Error message if authentication failed"
    )
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional authentication details"
    )


class GooglePlacesAuthRequest(AuthenticationRequest):
    """Google Places API authentication request."""

    api_name: str = Field(default="google_places", description="Google Places API")


class YelpFusionAuthRequest(AuthenticationRequest):
    """Yelp Fusion API authentication request."""

    api_name: str = Field(default="yelp_fusion", description="Yelp Fusion API")


class RateLimitInfo(BaseModel):
    """Rate limiting information for an API."""

    api_name: str = Field(..., description="Name of the API")
    current_usage: int = Field(..., description="Current usage count")
    limit: int = Field(..., description="Rate limit threshold")
    reset_time: Optional[str] = Field(None, description="When the rate limit resets")
    remaining: int = Field(..., description="Remaining requests allowed")


class HealthCheckResponse(BaseModel):
    """Health check response for API connectivity."""

    status: str = Field(..., description="Overall health status")
    timestamp: str = Field(..., description="When the health check was performed")
    apis: Dict[str, Dict[str, Any]] = Field(
        ..., description="Status of individual APIs"
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )
