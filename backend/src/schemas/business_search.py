"""
Business search schemas for Google Places API integration.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class LocationType(str, Enum):
    """Types of location input for business search."""

    CITY = "city"
    COORDINATES = "coordinates"
    ADDRESS = "address"
    ZIP_CODE = "zip_code"


class BusinessSearchRequest(BaseModel):
    """Request model for business search."""

    query: str = Field(
        ..., description="Search query for businesses", min_length=1, max_length=200
    )
    location: str = Field(
        ...,
        description="Location to search in (city, address, coordinates, or zip code)",
    )
    location_type: LocationType = Field(
        default=LocationType.CITY, description="Type of location input"
    )
    category: Optional[str] = Field(
        None, description="Business category or type to filter by", max_length=100
    )
    radius: Optional[int] = Field(
        default=5000,
        description="Search radius in meters (max 50000)",
        ge=100,
        le=50000,
    )
    max_results: Optional[int] = Field(
        default=10, description="Maximum number of results to return", ge=1, le=20
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )

    @validator("radius")
    @classmethod
    def validate_radius(cls, v):
        if v is not None and (v < 100 or v > 50000):
            raise ValueError("Radius must be between 100 and 50000 meters")
        return v

    @validator("max_results")
    @classmethod
    def validate_max_results(cls, v):
        if v is not None and (v < 1 or v > 20):
            raise ValueError("Max results must be between 1 and 20")
        return v


class BusinessData(BaseModel):
    """Model for individual business data."""

    place_id: str = Field(..., description="Google Places unique identifier")
    name: str = Field(..., description="Business name")
    address: Optional[str] = Field(None, description="Business address")
    phone: Optional[str] = Field(None, description="Business phone number")
    website: Optional[str] = Field(None, description="Business website URL")
    rating: Optional[float] = Field(
        None, description="Business rating (0.0 to 5.0)", ge=0.0, le=5.0
    )
    user_ratings_total: Optional[int] = Field(
        None, description="Total number of user ratings", ge=0
    )
    price_level: Optional[int] = Field(
        None, description="Price level indicator (0-4)", ge=0, le=4
    )
    types: Optional[List[str]] = Field(
        None, description="List of business types/categories"
    )
    geometry: Optional[Dict[str, Any]] = Field(
        None, description="Location coordinates and viewport"
    )
    formatted_address: Optional[str] = Field(
        None, description="Formatted address string"
    )
    international_phone_number: Optional[str] = Field(
        None, description="International phone number format"
    )
    opening_hours: Optional[Dict[str, Any]] = Field(
        None, description="Business hours information"
    )
    photos: Optional[List[Dict[str, Any]]] = Field(
        None, description="Business photos information"
    )
    reviews: Optional[List[Dict[str, Any]]] = Field(
        None, description="Business reviews information"
    )


class BusinessSearchResponse(BaseModel):
    """Response model for business search results."""

    success: bool = Field(..., description="Whether the search was successful")
    query: str = Field(..., description="Original search query")
    location: str = Field(..., description="Location that was searched")
    total_results: int = Field(..., description="Total number of results found", ge=0)
    results: List[BusinessData] = Field(..., description="List of business results")
    next_page_token: Optional[str] = Field(
        None, description="Token for next page of results"
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )
    search_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional search metadata"
    )


class BusinessSearchError(BaseModel):
    """Error model for business search failures."""

    success: bool = Field(default=False, description="Search was not successful")
    error: str = Field(..., description="Error message describing what went wrong")
    error_code: Optional[str] = Field(
        None, description="Specific error code if available"
    )
    context: str = Field(..., description="Context where the error occurred")
    query: Optional[str] = Field(None, description="Original search query that failed")
    location: Optional[str] = Field(None, description="Location that was searched")
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )


class PaginationInfo(BaseModel):
    """Pagination information for search results."""

    current_page: int = Field(..., description="Current page number", ge=1)
    total_pages: int = Field(..., description="Total number of pages", ge=1)
    has_next_page: bool = Field(..., description="Whether there are more pages")
    has_previous_page: bool = Field(..., description="Whether there are previous pages")
    next_page_token: Optional[str] = Field(None, description="Token for next page")
    previous_page_token: Optional[str] = Field(
        None, description="Token for previous page"
    )
