"""
Review management schemas for handling uncertain business matches.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from .business_matching import BusinessSourceData
from .business_merging import MergeConflict


class ReviewStatus(str, Enum):
    """Review status enumeration."""

    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    RESOLVED = "resolved"


class ReviewPriority(str, Enum):
    """Review priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReviewFlag(BaseModel):
    """Model for review flags."""

    flag_id: str = Field(..., description="Unique identifier for the review flag")
    business_id: str = Field(..., description="Business ID that needs review")
    flag_type: str = Field(
        ..., description="Type of flag (e.g., 'uncertain_match', 'data_conflict')"
    )
    priority: ReviewPriority = Field(..., description="Review priority level")
    status: ReviewStatus = Field(
        default=ReviewStatus.PENDING, description="Current review status"
    )
    reason: str = Field(..., description="Reason for flagging")
    confidence_score: float = Field(
        ..., description="Confidence score that triggered the flag", ge=0.0, le=1.0
    )
    source_data: List[BusinessSourceData] = Field(
        ..., description="Source data that caused the flag"
    )
    conflicts: List[MergeConflict] = Field(
        default_factory=list, description="Conflicts that need resolution"
    )
    created_at: str = Field(..., description="Flag creation timestamp")
    assigned_to: Optional[str] = Field(None, description="User assigned to review")
    assigned_at: Optional[str] = Field(None, description="Assignment timestamp")
    reviewed_at: Optional[str] = Field(None, description="Review completion timestamp")
    review_notes: Optional[str] = Field(None, description="Notes from the reviewer")
    resolution: Optional[str] = Field(None, description="Resolution action taken")
    run_id: Optional[str] = Field(None, description="Processing run identifier")


class ReviewWorkflow(BaseModel):
    """Model for review workflow steps."""

    workflow_id: str = Field(..., description="Unique identifier for the workflow")
    flag_id: str = Field(..., description="Associated review flag ID")
    step_number: int = Field(..., description="Workflow step number")
    step_name: str = Field(..., description="Name of the workflow step")
    status: str = Field(..., description="Step status")
    created_at: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Step creation timestamp",
    )
    assigned_to: Optional[str] = Field(None, description="User assigned to this step")
    started_at: Optional[str] = Field(None, description="Step start timestamp")
    completed_at: Optional[str] = Field(None, description="Step completion timestamp")
    notes: Optional[str] = Field(None, description="Step notes")
    next_step: Optional[str] = Field(None, description="Next step in workflow")


class ReviewAssignmentRequest(BaseModel):
    """Request for assigning a review."""

    flag_id: str = Field(..., description="Review flag ID to assign")
    user_id: str = Field(..., description="User ID to assign the review to")
    run_id: Optional[str] = Field(None, description="Processing run identifier")


class ReviewStatusUpdateRequest(BaseModel):
    """Request for updating review status."""

    flag_id: str = Field(..., description="Review flag ID to update")
    new_status: ReviewStatus = Field(..., description="New review status")
    review_notes: Optional[str] = Field(None, description="Notes from reviewer")
    resolution: Optional[str] = Field(None, description="Resolution action taken")
    run_id: Optional[str] = Field(None, description="Processing run identifier")


class ReviewResolutionRequest(BaseModel):
    """Request for resolving a review flag."""

    flag_id: str = Field(..., description="Review flag ID to resolve")
    resolution_action: str = Field(..., description="Action taken to resolve the flag")
    resolution_notes: str = Field(..., description="Notes about the resolution")
    run_id: Optional[str] = Field(None, description="Processing run identifier")


class ReviewFlagResponse(BaseModel):
    """Response for review flag operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    review_flag: Optional[ReviewFlag] = Field(None, description="Review flag data")
    message: str = Field(..., description="Response message")
    run_id: Optional[str] = Field(None, description="Processing run identifier")


class ReviewWorkflowResponse(BaseModel):
    """Response for review workflow operations."""

    success: bool = Field(..., description="Whether the operation was successful")
    workflow_steps: List[ReviewWorkflow] = Field(
        ..., description="List of workflow steps"
    )
    message: str = Field(..., description="Response message")
    run_id: Optional[str] = Field(None, description="Processing run identifier")


class PendingReviewsResponse(BaseModel):
    """Response for pending reviews query."""

    success: bool = Field(..., description="Whether the query was successful")
    pending_reviews: List[ReviewFlag] = Field(
        ..., description="List of pending review flags"
    )
    total_count: int = Field(..., description="Total number of pending reviews")
    message: str = Field(..., description="Response message")
    run_id: Optional[str] = Field(None, description="Processing run identifier")


class ReviewManagementError(BaseModel):
    """Error model for review management failures."""

    success: bool = Field(default=False, description="Operation was not successful")
    error: str = Field(..., description="Error message describing what went wrong")
    error_code: Optional[str] = Field(
        None, description="Specific error code if available"
    )
    context: str = Field(..., description="Context where the error occurred")
    run_id: Optional[str] = Field(None, description="Processing run identifier")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
