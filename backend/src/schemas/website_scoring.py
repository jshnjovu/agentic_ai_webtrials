"""
Website scoring schemas for Lighthouse API integration.
Defines data models for website performance audits and scoring results.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum


class AuditStrategy(str, Enum):
    """Audit strategy options for Lighthouse."""
    DESKTOP = "desktop"
    MOBILE = "mobile"


class ConfidenceLevel(str, Enum):
    """Confidence level for audit results."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WebsiteScore(BaseModel):
    """Website performance scores across different categories."""
    
    performance: float = Field(..., ge=0, le=100, description="Performance score (0-100)")
    accessibility: float = Field(..., ge=0, le=100, description="Accessibility score (0-100)")
    best_practices: float = Field(..., ge=0, le=100, description="Best practices score (0-100)")
    seo: float = Field(..., ge=0, le=100, description="SEO score (0-100)")
    overall: float = Field(..., ge=0, le=100, description="Overall weighted score (0-100)")
    
    @validator('overall')
    def validate_overall_score(cls, v, values):
        """Validate that overall score is within expected range."""
        if v < 0 or v > 100:
            raise ValueError('Overall score must be between 0 and 100')
        return v


class CoreWebVitals(BaseModel):
    """Core Web Vitals metrics from Lighthouse audit."""
    
    first_contentful_paint: Optional[float] = Field(None, description="First Contentful Paint in milliseconds")
    largest_contentful_paint: Optional[float] = Field(None, description="Largest Contentful Paint in milliseconds")
    cumulative_layout_shift: Optional[float] = Field(None, description="Cumulative Layout Shift score")
    total_blocking_time: Optional[float] = Field(None, description="Total Blocking Time in milliseconds")
    speed_index: Optional[float] = Field(None, description="Speed Index in milliseconds")


class LighthouseAuditRequest(BaseModel):
    """Request model for Lighthouse audit."""
    
    website_url: HttpUrl = Field(..., description="URL of the website to audit")
    business_id: str = Field(..., description="Business identifier for tracking")
    run_id: Optional[str] = Field(None, description="Run identifier for tracking")
    strategy: AuditStrategy = Field(AuditStrategy.DESKTOP, description="Audit strategy (desktop/mobile)")
    audit_parameters: Optional[Dict[str, Any]] = Field(None, description="Additional audit parameters")
    
    @validator('website_url')
    def validate_website_url(cls, v):
        """Validate website URL format."""
        if not str(v).startswith(('http://', 'https://')):
            raise ValueError('Website URL must start with http:// or https://')
        return v


class LighthouseAuditResponse(BaseModel):
    """Response model for Lighthouse audit results."""
    
    success: bool = Field(..., description="Whether the audit was successful")
    website_url: str = Field(..., description="URL that was audited")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    audit_timestamp: float = Field(..., description="Unix timestamp of audit completion")
    strategy: str = Field(..., description="Audit strategy used")
    scores: WebsiteScore = Field(..., description="Website performance scores")
    core_web_vitals: CoreWebVitals = Field(..., description="Core Web Vitals metrics")
    confidence: ConfidenceLevel = Field(..., description="Confidence level of results")
    error: Optional[str] = Field(None, description="Error message if audit failed")
    error_code: Optional[str] = Field(None, description="Error code if audit failed")
    context: Optional[str] = Field(None, description="Error context if audit failed")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw audit data from Lighthouse")


class LighthouseAuditError(BaseModel):
    """Error response model for Lighthouse audit failures."""
    
    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    context: str = Field(..., description="Error context")
    website_url: str = Field(..., description="URL that failed to audit")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    audit_timestamp: float = Field(..., description="Unix timestamp of error")
    error_code: Optional[str] = Field(None, description="Error code")
    scores: WebsiteScore = Field(..., description="Default scores (all 0)")
    core_web_vitals: CoreWebVitals = Field(..., description="Empty Core Web Vitals")
    confidence: ConfidenceLevel = Field(ConfidenceLevel.LOW, description="Low confidence due to error")
    strategy: str = Field("unknown", description="Unknown strategy due to error")


class WebsiteScoringSummary(BaseModel):
    """Summary of website scoring results for multiple audits."""
    
    business_id: str = Field(..., description="Business identifier")
    total_audits: int = Field(..., description="Total number of audits performed")
    successful_audits: int = Field(..., description="Number of successful audits")
    failed_audits: int = Field(..., description="Number of failed audits")
    average_scores: WebsiteScore = Field(..., description="Average scores across all audits")
    latest_audit: Optional[LighthouseAuditResponse] = Field(None, description="Most recent audit result")
    audit_history: List[LighthouseAuditResponse] = Field(default_factory=list, description="Audit history")


class AuditThresholds(BaseModel):
    """Configurable thresholds for audit scoring."""
    
    performance_min: float = Field(70.0, ge=0, le=100, description="Minimum acceptable performance score")
    accessibility_min: float = Field(80.0, ge=0, le=100, description="Minimum acceptable accessibility score")
    best_practices_min: float = Field(80.0, ge=0, le=100, description="Minimum acceptable best practices score")
    seo_min: float = Field(80.0, ge=0, le=100, description="Minimum acceptable SEO score")
    overall_min: float = Field(75.0, ge=0, le=100, description="Minimum acceptable overall score")
    
    @validator('overall_min')
    def validate_overall_threshold(cls, v, values):
        """Validate that overall threshold is reasonable given category thresholds."""
        category_thresholds = [
            values.get('performance_min', 70),
            values.get('accessibility_min', 80),
            values.get('best_practices_min', 80),
            values.get('seo_min', 80)
        ]
        min_category = min(category_thresholds)
        if v > min_category:
            raise ValueError('Overall threshold cannot be higher than the lowest category threshold')
        return v


class AuditConfiguration(BaseModel):
    """Configuration for Lighthouse audits."""
    
    timeout_seconds: int = Field(30, ge=10, le=120, description="Audit timeout in seconds")
    max_retries: int = Field(3, ge=1, le=5, description="Maximum number of retry attempts")
    retry_delay_base: float = Field(1.0, ge=0.5, le=5.0, description="Base delay for exponential backoff")
    enable_core_web_vitals: bool = Field(True, description="Whether to extract Core Web Vitals")
    enable_raw_data: bool = Field(False, description="Whether to include raw audit data in response")
    thresholds: AuditThresholds = Field(default_factory=AuditThresholds, description="Scoring thresholds")
