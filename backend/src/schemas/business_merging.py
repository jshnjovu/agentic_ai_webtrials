"""
Business data merging and prioritization schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from .business_matching import (
    BusinessSourceData,
    BusinessLocation,
    BusinessContactInfo,
    ConfidenceLevel,
)


class DataCompletenessScore(BaseModel):
    """Score for data completeness from a source."""

    source: str = Field(..., description="Data source identifier")
    overall_score: float = Field(
        ..., description="Overall completeness score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    name_score: float = Field(
        ..., description="Name completeness score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    location_score: float = Field(
        ..., description="Location completeness score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    contact_score: float = Field(
        ...,
        description="Contact information completeness score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    rating_score: float = Field(
        ...,
        description="Rating and review completeness score (0.0 to 1.0)",
        ge=0.0,
        le=1.0,
    )
    category_score: float = Field(
        ..., description="Category completeness score (0.0 to 1.0)", ge=0.0, le=1.0
    )
    details: Dict[str, float] = Field(
        default_factory=dict, description="Detailed scoring breakdown"
    )

    @validator(
        "overall_score",
        "name_score",
        "location_score",
        "contact_score",
        "rating_score",
        "category_score",
    )
    @classmethod
    def validate_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class MergedBusinessData(BaseModel):
    """Merged business data from multiple sources."""

    business_id: str = Field(
        ..., description="Unique identifier for the merged business"
    )
    name: str = Field(..., description="Primary business name")
    location: BusinessLocation = Field(..., description="Primary business location")
    contact_info: Optional[BusinessContactInfo] = Field(
        None, description="Merged contact information"
    )
    rating: Optional[float] = Field(None, description="Primary rating", ge=0.0, le=5.0)
    review_count: Optional[int] = Field(None, description="Total review count", ge=0)
    categories: List[str] = Field(
        default_factory=list, description="Combined categories from all sources"
    )
    price_level: Optional[int] = Field(
        None, description="Primary price level", ge=0, le=4
    )
    hours: Optional[Dict[str, Any]] = Field(None, description="Primary business hours")
    photos: List[Dict[str, Any]] = Field(
        default_factory=list, description="Combined photos from all sources"
    )
    confidence_level: ConfidenceLevel = Field(
        ..., description="Overall confidence in merged data"
    )
    source_contributions: List[str] = Field(
        ..., description="List of sources that contributed data"
    )
    merge_metadata: Dict[str, Any] = Field(
        ..., description="Metadata about the merging process"
    )
    last_updated: str = Field(..., description="Last update timestamp")
    needs_review: bool = Field(
        default=False, description="Whether this merged record needs manual review"
    )

    @validator("rating")
    @classmethod
    def validate_rating(cls, v):
        if v is not None and (v < 0.0 or v > 5.0):
            raise ValueError("Rating must be between 0.0 and 1.0")
        return v


class MergeConflict(BaseModel):
    """Information about conflicting data during merging."""

    field_name: str = Field(..., description="Name of the conflicting field")
    source_values: Dict[str, Any] = Field(
        ..., description="Values from different sources"
    )
    resolution_strategy: str = Field(
        ..., description="Strategy used to resolve the conflict"
    )
    resolved_value: Any = Field(..., description="Final resolved value")
    confidence: float = Field(
        ..., description="Confidence in the resolution (0.0 to 1.0)", ge=0.0, le=1.0
    )

    @validator("confidence")
    @classmethod
    def validate_confidence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class BusinessMergeRequest(BaseModel):
    """Request for merging business data."""

    businesses: List[BusinessSourceData] = Field(
        ..., description="List of businesses to merge", min_length=2
    )
    merge_strategy: str = Field(
        default="completeness", description="Strategy for merging conflicting data"
    )
    prioritize_source: Optional[str] = Field(
        None, description="Source to prioritize when conflicts exist"
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )


class BusinessMergeResponse(BaseModel):
    """Response for business data merging."""

    success: bool = Field(..., description="Whether the merging was successful")
    merged_business: MergedBusinessData = Field(
        ..., description="Merged business record"
    )
    conflicts_resolved: List[MergeConflict] = Field(
        ..., description="List of conflicts that were resolved"
    )
    merge_metadata: Dict[str, Any] = Field(
        ..., description="Metadata about the merging process"
    )
    run_id: Optional[str] = Field(
        None, description="Unique identifier for the processing run"
    )


class BusinessMergeError(BaseModel):
    """Error model for business merging failures."""

    success: bool = Field(default=False, description="Merging was not successful")
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
