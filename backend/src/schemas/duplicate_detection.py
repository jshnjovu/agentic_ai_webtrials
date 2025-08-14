"""
Duplicate detection and removal schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from .business_matching import BusinessSourceData, ConfidenceLevel


class DuplicateType(str, Enum):
    """Types of duplicate detection."""
    EXACT_MATCH = "exact_match"
    HIGH_SIMILARITY = "high_similarity"
    MEDIUM_SIMILARITY = "medium_similarity"
    LOW_SIMILARITY = "low_similarity"
    POTENTIAL_DUPLICATE = "potential_duplicate"


class BusinessFingerprint(BaseModel):
    """Business fingerprint for duplicate detection."""
    
    business_id: str = Field(..., description="Unique business identifier")
    name_normalized: str = Field(..., description="Normalized business name")
    address_normalized: str = Field(..., description="Normalized address")
    phone_normalized: Optional[str] = Field(None, description="Normalized phone number")
    website_normalized: Optional[str] = Field(None, description="Normalized website")
    coordinate_hash: str = Field(..., description="Hash of coordinates for proximity matching")
    category_signature: str = Field(..., description="Signature of business categories")
    fingerprint_hash: str = Field(..., description="Overall fingerprint hash")
    created_at: str = Field(..., description="Fingerprint creation timestamp")
    
    @validator('name_normalized', 'address_normalized')
    @classmethod
    def validate_normalized_string(cls, v):
        if not v or not v.strip():
            raise ValueError('Normalized string cannot be empty')
        return v.strip().lower()


class DuplicateGroup(BaseModel):
    """Group of duplicate businesses."""
    
    group_id: str = Field(..., description="Unique identifier for the duplicate group")
    primary_business: BusinessSourceData = Field(..., description="Primary business record")
    duplicate_businesses: List[BusinessSourceData] = Field(..., description="List of duplicate businesses")
    duplicate_type: DuplicateType = Field(..., description="Type of duplication detected")
    confidence_score: float = Field(..., description="Confidence in duplicate detection (0.0 to 1.0)", ge=0.0, le=1.0)
    detection_method: str = Field(..., description="Method used for duplicate detection")
    detection_metadata: Dict[str, Any] = Field(..., description="Metadata about detection process")
    created_at: str = Field(..., description="Group creation timestamp")
    needs_review: bool = Field(default=False, description="Whether this group needs manual review")
    
    @validator('confidence_score')
    @classmethod
    def validate_confidence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Confidence score must be between 0.0 and 1.0')
        return v


class DuplicateDetectionRequest(BaseModel):
    """Request for duplicate detection."""
    
    businesses: List[BusinessSourceData] = Field(..., description="List of businesses to check for duplicates", min_length=1)
    detection_threshold: float = Field(default=0.8, description="Threshold for duplicate detection", ge=0.0, le=1.0)
    auto_remove_high_confidence: bool = Field(default=True, description="Automatically remove high-confidence duplicates")
    include_fingerprints: bool = Field(default=True, description="Include business fingerprints in response")
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")
    
    @validator('detection_threshold')
    @classmethod
    def validate_threshold(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Detection threshold must be between 0.0 and 1.0')
        return v


class DuplicateDetectionResponse(BaseModel):
    """Response for duplicate detection."""
    
    success: bool = Field(..., description="Whether the detection was successful")
    total_businesses: int = Field(..., description="Total number of businesses processed", ge=0)
    duplicate_groups: List[DuplicateGroup] = Field(..., description="Groups of duplicate businesses found")
    unique_businesses: List[BusinessSourceData] = Field(..., description="Businesses with no duplicates")
    removed_duplicates: List[BusinessSourceData] = Field(..., description="Duplicates that were automatically removed")
    detection_metadata: Dict[str, Any] = Field(..., description="Metadata about detection process")
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")


class DuplicateRemovalRequest(BaseModel):
    """Request for removing duplicate businesses."""
    
    duplicate_groups: List[DuplicateGroup] = Field(..., description="Duplicate groups to process")
    removal_strategy: str = Field(default="keep_primary", description="Strategy for removing duplicates")
    review_threshold: float = Field(default=0.7, description="Threshold below which manual review is required", ge=0.0, le=1.0)
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")
    
    @validator('review_threshold')
    @classmethod
    def validate_threshold(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError('Review threshold must be between 0.0 and 1.0')
        return v


class DuplicateRemovalResponse(BaseModel):
    """Response for duplicate removal."""
    
    success: bool = Field(..., description="Whether the removal was successful")
    total_groups_processed: int = Field(..., description="Total number of duplicate groups processed", ge=0)
    duplicates_removed: List[BusinessSourceData] = Field(..., description="Duplicates that were removed")
    businesses_kept: List[BusinessSourceData] = Field(..., description="Businesses that were kept")
    review_required: List[DuplicateGroup] = Field(..., description="Groups requiring manual review")
    removal_metadata: Dict[str, Any] = Field(..., description="Metadata about removal process")
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")


class DuplicateDetectionError(BaseModel):
    """Error model for duplicate detection failures."""
    
    success: bool = Field(default=False, description="Detection was not successful")
    error: str = Field(..., description="Error message describing what went wrong")
    error_code: Optional[str] = Field(None, description="Specific error code if available")
    context: str = Field(..., description="Context where the error occurred")
    run_id: Optional[str] = Field(None, description="Unique identifier for the processing run")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
