"""
Yelp Fusion API schemas for business search integration.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any


class YelpBusinessSearchRequest(BaseModel):
    """Request model for Yelp Fusion business search."""
    
    term: str = Field(..., description="Search term for businesses", min_length=1, max_length=200)
    location: str = Field(..., description="Location to search in (city, address, coordinates, or zip code)")
    limit: Optional[int] = Field(default=20, description="Maximum number of results to return", ge=1, le=50)
    offset: Optional[int] = Field(default=0, description="Offset for pagination", ge=0)
    sort_by: Optional[str] = Field(default="best_match", description="Sort order: best_match, rating, review_count, distance")
    price: Optional[str] = Field(None, description="Price filter: 1, 2, 3, 4 (1=$, 4=$$$$)")
    open_now: Optional[bool] = Field(None, description="Filter for businesses currently open")
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v):
        if v is not None and (v < 1 or v > 50):
            raise ValueError('Limit must be between 1 and 50')
        return v
    
    @field_validator('offset')
    @classmethod
    def validate_offset(cls, v):
        if v is not None and v < 0:
            raise ValueError('Offset must be non-negative')
        return v


class YelpBusinessHours(BaseModel):
    """Model for Yelp business operating hours."""
    
    day: int = Field(..., description="Day of week (0=Monday, 6=Sunday)", ge=0, le=6)
    start: str = Field(..., description="Opening time in HHMM format")
    end: str = Field(..., description="Closing time in HHMM format")
    is_overnight: bool = Field(default=False, description="Whether business operates overnight")


class YelpBusinessCategory(BaseModel):
    """Model for Yelp business category."""
    
    alias: str = Field(..., description="Category alias")
    title: str = Field(..., description="Category title")


class YelpBusinessCoordinates(BaseModel):
    """Model for Yelp business coordinates."""
    
    latitude: float = Field(..., description="Business latitude")
    longitude: float = Field(..., description="Business longitude")


class YelpBusinessLocation(BaseModel):
    """Model for Yelp business location."""
    
    address1: Optional[str] = Field(None, description="Primary address line")
    address2: Optional[str] = Field(None, description="Secondary address line")
    address3: Optional[str] = Field(None, description="Tertiary address line")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State code")
    zip_code: Optional[str] = Field(None, description="ZIP code")
    country: Optional[str] = Field(None, description="Country code")
    display_address: List[str] = Field(default_factory=list, description="Formatted display address")
    cross_streets: Optional[str] = Field(None, description="Cross streets")


class YelpBusinessData(BaseModel):
    """Model for individual Yelp business data."""
    
    id: str = Field(..., description="Yelp business unique identifier")
    alias: str = Field(..., description="Business alias")
    name: str = Field(..., description="Business name")
    image_url: Optional[str] = Field(None, description="Business image URL")
    is_closed: bool = Field(..., description="Whether business is permanently closed")
    url: str = Field(..., description="Yelp business page URL")
    review_count: int = Field(..., description="Number of reviews", ge=0)
    categories: List[YelpBusinessCategory] = Field(default_factory=list, description="Business categories")
    rating: float = Field(..., description="Business rating (0.0 to 5.0)", ge=0.0, le=5.0)
    coordinates: YelpBusinessCoordinates = Field(..., description="Business coordinates")
    transactions: List[str] = Field(default_factory=list, description="Available transaction types")
    price: Optional[str] = Field(None, description="Price level indicator (1-4)")
    location: YelpBusinessLocation = Field(..., description="Business location information")
    phone: Optional[str] = Field(None, description="Business phone number")
    display_phone: Optional[str] = Field(None, description="Formatted display phone number")
    distance: Optional[float] = Field(None, description="Distance from search location in meters")
    hours: Optional[List[YelpBusinessHours]] = Field(None, description="Business operating hours")
    photos: Optional[List[str]] = Field(None, description="Business photo URLs")
    # Enhanced data fields
    attributes: Optional[Dict[str, Any]] = Field(None, description="Business attributes (accessibility, amenities, etc.)")
    special_hours: Optional[List[Dict[str, Any]]] = Field(None, description="Special hours for holidays or events")
    business_status: Optional[str] = Field(None, description="Current business status or announcements")
    social_media: Optional[Dict[str, str]] = Field(None, description="Social media links if available")


class YelpBusinessSearchResponse(BaseModel):
    """Response model for Yelp Fusion business search results."""
    
    success: bool = Field(..., description="Whether the search was successful")
    term: str = Field(..., description="Original search term")
    location: str = Field(..., description="Location that was searched")
    total: int = Field(..., description="Total number of results found", ge=0)
    businesses: List[YelpBusinessData] = Field(..., description="List of business results")
    region: Optional[Dict[str, Any]] = Field(None, description="Search region information")
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")
    search_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional search metadata")


class YelpBusinessSearchError(BaseModel):
    """Error model for Yelp Fusion business search failures."""
    
    success: bool = Field(default=False, description="Search was not successful")
    error: str = Field(..., description="Error message describing what went wrong")
    error_code: Optional[str] = Field(None, description="Specific error code if available")
    context: str = Field(..., description="Context where the error occurred")
    term: Optional[str] = Field(None, description="Original search term that failed")
    location: Optional[str] = Field(None, description="Location that was searched")
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class YelpPaginationInfo(BaseModel):
    """Pagination information for Yelp search results."""
    
    current_offset: int = Field(..., description="Current offset number", ge=0)
    total_results: int = Field(..., description="Total number of results", ge=0)
    has_next_page: bool = Field(..., description="Whether there are more pages")
    has_previous_page: bool = Field(..., description="Whether there are previous pages")
    next_offset: Optional[int] = Field(None, description="Next offset for pagination")
    previous_offset: Optional[int] = Field(None, description="Previous offset for pagination")
