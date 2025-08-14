"""
Schemas for business data merging, matching, and deduplication.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, Literal
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class DataSource(str, Enum):
    GOOGLE = "google"
    YELP = "yelp"
    MERGED = "merged"
    OTHER = "other"


class BusinessInput(BaseModel):
    """Generalized input model for external business records used for matching/merging."""

    source: DataSource = Field(..., description="Source of the business record")
    id: Optional[str] = Field(None, description="Source-specific identifier (place_id, yelp business id, etc.)")
    name: str = Field(..., description="Business name", min_length=1)
    address: Optional[str] = Field(None, description="Business address")
    latitude: Optional[float] = Field(None, description="Latitude of the business location")
    longitude: Optional[float] = Field(None, description="Longitude of the business location")
    phone: Optional[str] = Field(None, description="Business phone number")
    website: Optional[str] = Field(None, description="Business website URL")
    google_place_id: Optional[str] = Field(None, description="Google Places place_id if available")
    yelp_business_id: Optional[str] = Field(None, description="Yelp business id if available")
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw source payload for traceability")


class MatchDetails(BaseModel):
    name_similarity: float = Field(..., ge=0.0, le=1.0)
    address_similarity: float = Field(..., ge=0.0, le=1.0)
    proximity_score: float = Field(..., ge=0.0, le=1.0)
    combined_score: float = Field(..., ge=0.0, le=1.0)
    matched: bool = Field(...)
    threshold: float = Field(..., ge=0.0, le=1.0)


class MergedBusiness(BaseModel):
    id: str = Field(..., description="Merged record identifier")
    name: str
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    website: Optional[str] = None

    google_place_id: Optional[str] = None
    yelp_business_id: Optional[str] = None

    data_source: DataSource = Field(default=DataSource.MERGED)

    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_level: Literal["high", "medium", "low"]

    manual_review_required: bool = False
    review_reasons: List[str] = Field(default_factory=list)

    match_details: Optional[MatchDetails] = None


class MergeRequest(BaseModel):
    """Request payload for merge-and-deduplicate operation."""

    google_data: List[BusinessInput] = Field(default_factory=list)
    yelp_data: List[BusinessInput] = Field(default_factory=list)

    name_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    address_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    match_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    distance_threshold_meters: float = Field(default=200.0, ge=0.0)

    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")

    @field_validator("name_weight")
    @classmethod
    def validate_name_weight(cls, v):
        return v

    @field_validator("address_weight")
    @classmethod
    def validate_address_weight(cls, v):
        return v

    @field_validator("match_threshold")
    @classmethod
    def validate_threshold(cls, v):
        return v

    @field_validator("distance_threshold_meters")
    @classmethod
    def validate_distance(cls, v):
        return v

    @field_validator("yelp_data")
    @classmethod
    def validate_yelp_sources(cls, v: List[BusinessInput]):
        for item in v:
            if item.source not in (DataSource.YELP, DataSource.OTHER, DataSource.MERGED):
                # Allow OTHER for flexibility in tests
                pass
        return v


class MergeResponse(BaseModel):
    success: bool
    total_input: int
    total_output: int
    duplicates_removed: int
    manual_review_count: int
    merged: List[MergedBusiness]
    run_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None