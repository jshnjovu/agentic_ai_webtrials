"""
Business matching, merging, and duplicate detection schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum


class ConfidenceLevel(str, Enum):
    """Confidence levels for business matching and data quality."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BusinessLocation(BaseModel):
    """Business location coordinates."""

    latitude: Optional[float] = Field(
        None, description="Latitude coordinate", ge=-90, le=90
    )
    longitude: Optional[float] = Field(
        None, description="Longitude coordinate", ge=-180, le=180
    )
    address: Optional[str] = Field(None, description="Formatted address string")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State or province")
    zip_code: Optional[str] = Field(None, description="Postal/ZIP code")
    country: Optional[str] = Field(None, description="Country code")


class BusinessContactInfo(BaseModel):
    """Business contact information."""

    phone: Optional[str] = Field(None, description="Phone number")
    website: Optional[str] = Field(None, description="Website URL")
    email: Optional[str] = Field(None, description="Email address")
    social_media: Optional[Dict[str, str]] = Field(
        None, description="Social media links"
    )


class BusinessSourceData(BaseModel):
    """Business data from a specific source."""

    source: str = Field(
        ..., description="Data source (e.g., 'google_places', 'yelp_fusion')"
    )
    source_id: str = Field(..., description="Unique identifier from the source")
    name: str = Field(..., description="Business name")
    location: BusinessLocation = Field(..., description="Business location")
    contact_info: Optional[BusinessContactInfo] = Field(
        None, description="Contact information"
    )
    rating: Optional[float] = Field(None, description="Business rating", ge=0.0, le=5.0)
    review_count: Optional[int] = Field(None, description="Number of reviews", ge=0)
    categories: Optional[List[str]] = Field(None, description="Business categories")
    price_level: Optional[int] = Field(
        None, description="Price level indicator", ge=0, le=4
    )
    hours: Optional[Dict[str, Any]] = Field(None, description="Business hours")
    photos: Optional[List[Dict[str, Any]]] = Field(None, description="Business photos")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw data from source")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")

    @validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v is not None and (v < 0.0 or v > 5.0):
            raise ValueError("Rating must be between 0.0 and 5.0")
        return v


class BusinessMatchScore(BaseModel):
    """Score for business matching."""

    name_similarity: float = Field(
        ..., description="Name similarity score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    address_similarity: float = Field(
        ..., description="Address similarity score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    coordinate_proximity: float = Field(
        ..., description="Coordinate proximity score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    combined_score: float = Field(
        ..., description="Combined weighted score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    confidence_level: ConfidenceLevel = Field(
        ..., description="Overall confidence level"
    )

    @validator(
        "name_similarity",
        "address_similarity",
        "coordinate_proximity",
        "combined_score",
    )
    @classmethod
    def validate_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class BusinessMatchCandidate(BaseModel):
    """Candidate for business matching."""

    source_data: BusinessSourceData = Field(
        ..., description="Business data from source"
    )
    match_score: BusinessMatchScore = Field(..., description="Matching score")
    is_duplicate: bool = Field(default=False, description="Whether this is a duplicate")
    needs_review: bool = Field(
        default=False, description="Whether this needs manual review"
    )


class BusinessMatchingRequest(BaseModel):
    """Request for business matching."""

    businesses: List[BusinessSourceData] = Field(
        ..., description="List of businesses to match", min_length=2
    )
    name_weight: float = Field(
        default=0.4,
        description="Weight for name similarity (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    address_weight: float = Field(
        default=0.3,
        description="Weight for address similarity (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    coordinate_weight: float = Field(
        default=0.3,
        description="Weight for coordinate proximity (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    similarity_threshold: float = Field(
        default=0.7,
        description="Threshold for considering businesses similar",
        ge=0.0,
        le=1.0,
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )

    @validator("name_weight", "address_weight", "coordinate_weight")
    @classmethod
    def validate_weights(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Weight must be between 0.0 and 1.0")
        return v

    @validator("similarity_threshold")
    @classmethod
    def validate_threshold(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v


class BusinessMatchingResponse(BaseModel):
    """Response for business matching."""

    success: bool = Field(..., description="Whether the matching was successful")
    total_businesses: int = Field(
        ..., description="Total number of businesses processed", ge=0
    )
    matched_groups: List[List[BusinessMatchCandidate]] = Field(
        ..., description="Groups of matched businesses"
    )
    unmatched_businesses: List[BusinessSourceData] = Field(
        ..., description="Businesses that couldn't be matched"
    )
    matching_metadata: Dict[str, Any] = Field(
        ..., description="Matching process metadata"
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )


class BusinessMatchingError(BaseModel):
    """Error model for business matching failures."""

    success: bool = Field(default=False, description="Matching was not successful")
    error: str = Field(..., description="Error message describing what went wrong")
    error_code: Optional[str] = Field(
        None, description="Specific error code if available"
    )
    context: str = Field(..., description="Context where the error occurred")
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
