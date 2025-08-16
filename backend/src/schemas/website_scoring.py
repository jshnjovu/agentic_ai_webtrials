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

    performance: float = Field(
        ..., ge=0, le=100, description="Performance score (0-100)"
    )
    accessibility: float = Field(
        ..., ge=0, le=100, description="Accessibility score (0-100)"
    )
    best_practices: float = Field(
        ..., ge=0, le=100, description="Best practices score (0-100)"
    )
    seo: float = Field(..., ge=0, le=100, description="SEO score (0-100)")
    overall: float = Field(
        ..., ge=0, le=100, description="Overall weighted score (0-100)"
    )

    @validator("overall")
    def validate_overall_score(cls, v, values):
        """Validate that overall score is within expected range."""
        if v < 0 or v > 100:
            raise ValueError("Overall score must be between 0 and 100")
        return v


class HeuristicScore(BaseModel):
    """Heuristic evaluation scores across different categories."""

    trust_score: float = Field(
        ..., ge=0, le=100, description="Trust signal score (0-100)"
    )
    cro_score: float = Field(
        ..., ge=0, le=100, description="Conversion optimization score (0-100)"
    )
    mobile_score: float = Field(
        ..., ge=0, le=100, description="Mobile usability score (0-100)"
    )
    content_score: float = Field(
        ..., ge=0, le=100, description="Content quality score (0-100)"
    )
    social_score: float = Field(
        ..., ge=0, le=100, description="Social proof score (0-100)"
    )
    overall_heuristic_score: float = Field(
        ..., ge=0, le=100, description="Overall heuristic score (0-100)"
    )
    confidence_level: ConfidenceLevel = Field(
        ..., description="Confidence level of heuristic evaluation"
    )

    @validator("overall_heuristic_score")
    def validate_overall_heuristic_score(cls, v, values):
        """Validate that overall heuristic score is within expected range."""
        if v < 0 or v > 100:
            raise ValueError("Overall heuristic score must be between 0 and 100")
        return v


class TrustSignals(BaseModel):
    """Trust signal elements detected on the website."""

    has_https: bool = Field(False, description="Website uses HTTPS")
    has_privacy_policy: bool = Field(False, description="Privacy policy page exists")
    has_contact_info: bool = Field(False, description="Contact information is visible")
    has_about_page: bool = Field(False, description="About page exists")
    has_terms_of_service: bool = Field(
        False, description="Terms of service page exists"
    )
    has_ssl_certificate: bool = Field(False, description="Valid SSL certificate")
    has_business_address: bool = Field(False, description="Business address is visible")
    has_phone_number: bool = Field(False, description="Phone number is visible")
    has_email: bool = Field(False, description="Email address is visible")


class CROElements(BaseModel):
    """Conversion rate optimization elements detected."""

    has_cta_buttons: bool = Field(False, description="Call-to-action buttons present")
    has_contact_forms: bool = Field(False, description="Contact forms present")
    has_pricing_tables: bool = Field(False, description="Pricing information visible")
    has_testimonials: bool = Field(False, description="Customer testimonials present")
    has_reviews: bool = Field(False, description="Customer reviews visible")
    has_social_proof: bool = Field(False, description="Social proof elements present")
    has_urgency_elements: bool = Field(False, description="Urgency/scarcity elements")
    has_trust_badges: bool = Field(False, description="Trust badges or certifications")


class MobileUsability(BaseModel):
    """Mobile usability heuristics evaluation."""

    has_viewport_meta: bool = Field(False, description="Viewport meta tag present")
    has_touch_targets: bool = Field(False, description="Adequate touch target sizes")
    has_responsive_design: bool = Field(
        False, description="Responsive design implemented"
    )
    has_mobile_navigation: bool = Field(False, description="Mobile-friendly navigation")
    has_readable_fonts: bool = Field(False, description="Readable font sizes on mobile")
    has_adequate_spacing: bool = Field(
        False, description="Adequate spacing between elements"
    )


class ContentQuality(BaseModel):
    """Content quality assessment metrics."""

    has_proper_headings: bool = Field(
        False, description="Proper heading structure (H1, H2, etc.)"
    )
    has_alt_text: bool = Field(False, description="Images have alt text")
    has_meta_description: bool = Field(False, description="Meta description present")
    has_meta_keywords: bool = Field(False, description="Meta keywords present")
    has_structured_data: bool = Field(
        False, description="Structured data markup present"
    )
    has_internal_links: bool = Field(False, description="Internal linking structure")
    has_external_links: bool = Field(False, description="External links present")
    has_blog_content: bool = Field(False, description="Blog or content section present")


class SocialProof(BaseModel):
    """Social proof elements detected."""

    has_social_media_links: bool = Field(
        False, description="Social media links present"
    )
    has_customer_reviews: bool = Field(False, description="Customer reviews visible")
    has_testimonials: bool = Field(False, description="Customer testimonials present")
    has_case_studies: bool = Field(False, description="Case studies or success stories")
    has_awards_certifications: bool = Field(
        False, description="Awards or certifications"
    )
    has_partner_logos: bool = Field(
        False, description="Partner or client logos visible"
    )
    has_user_generated_content: bool = Field(
        False, description="User-generated content present"
    )


class HeuristicEvaluationRequest(BaseModel):
    """Request model for heuristic evaluation."""

    website_url: HttpUrl = Field(..., description="URL of the website to evaluate")
    business_id: str = Field(..., description="Business identifier for tracking")
    run_id: Optional[str] = Field(None, description="Run identifier for tracking")
    evaluation_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Additional evaluation parameters"
    )

    @validator("website_url")
    def validate_website_url(cls, v):
        """Validate website URL format."""
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("Website URL must start with http:// or https://")
        return v


class HeuristicEvaluationResponse(BaseModel):
    """Response model for heuristic evaluation results."""

    success: bool = Field(..., description="Whether the evaluation was successful")
    website_url: str = Field(..., description="URL that was evaluated")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    evaluation_timestamp: float = Field(
        ..., description="Unix timestamp of evaluation completion"
    )
    scores: HeuristicScore = Field(..., description="Heuristic evaluation scores")
    trust_signals: TrustSignals = Field(
        ..., description="Trust signal elements detected"
    )
    cro_elements: CROElements = Field(..., description="CRO elements detected")
    mobile_usability: MobileUsability = Field(
        ..., description="Mobile usability assessment"
    )
    content_quality: ContentQuality = Field(
        ..., description="Content quality assessment"
    )
    social_proof: SocialProof = Field(..., description="Social proof elements detected")
    confidence: ConfidenceLevel = Field(..., description="Confidence level of results")
    error: Optional[str] = Field(None, description="Error message if evaluation failed")
    error_code: Optional[str] = Field(
        None, description="Error code if evaluation failed"
    )
    context: Optional[str] = Field(
        None, description="Error context if evaluation failed"
    )
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw evaluation data")


class HeuristicEvaluationError(BaseModel):
    """Error response model for heuristic evaluation failures."""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    context: str = Field(..., description="Error context")
    website_url: str = Field(..., description="URL that failed to evaluate")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    evaluation_timestamp: float = Field(..., description="Unix timestamp of error")
    error_code: Optional[str] = Field(None, description="Error code")
    scores: HeuristicScore = Field(..., description="Default scores (all 0)")
    trust_signals: TrustSignals = Field(..., description="Empty trust signals")
    cro_elements: CROElements = Field(..., description="Empty CRO elements")
    mobile_usability: MobileUsability = Field(..., description="Empty mobile usability")
    content_quality: ContentQuality = Field(..., description="Empty content quality")
    social_proof: SocialProof = Field(..., description="Empty social proof")
    confidence: ConfidenceLevel = Field(
        ConfidenceLevel.LOW, description="Low confidence due to error"
    )


class CoreWebVitals(BaseModel):
    """Core Web Vitals metrics from Lighthouse audit."""

    first_contentful_paint: Optional[float] = Field(
        None, description="First Contentful Paint in milliseconds"
    )
    largest_contentful_paint: Optional[float] = Field(
        None, description="Largest Contentful Paint in milliseconds"
    )
    cumulative_layout_shift: Optional[float] = Field(
        None, description="Cumulative Layout Shift score"
    )
    total_blocking_time: Optional[float] = Field(
        None, description="Total Blocking Time in milliseconds"
    )
    speed_index: Optional[float] = Field(
        None, description="Speed Index in milliseconds"
    )


class LighthouseAuditRequest(BaseModel):
    """Request model for Lighthouse audit."""

    website_url: HttpUrl = Field(..., description="URL of the website to audit")
    business_id: str = Field(..., description="Business identifier for tracking")
    run_id: Optional[str] = Field(None, description="Run identifier for tracking")
    strategy: AuditStrategy = Field(
        AuditStrategy.DESKTOP, description="Audit strategy (desktop/mobile)"
    )
    audit_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Additional audit parameters"
    )

    @validator("website_url")
    def validate_website_url(cls, v):
        """Validate website URL format."""
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("Website URL must start with http:// or https://")
        return v


class LighthouseAuditResponse(BaseModel):
    """Response model for Lighthouse audit results."""

    success: bool = Field(..., description="Whether the audit was successful")
    website_url: str = Field(..., description="URL that was audited")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    audit_timestamp: float = Field(
        ..., description="Unix timestamp of audit completion"
    )
    strategy: str = Field(..., description="Audit strategy used")
    scores: WebsiteScore = Field(..., description="Website performance scores")
    core_web_vitals: CoreWebVitals = Field(..., description="Core Web Vitals metrics")
    confidence: ConfidenceLevel = Field(..., description="Confidence level of results")
    error: Optional[str] = Field(None, description="Error message if audit failed")
    error_code: Optional[str] = Field(None, description="Error code if audit failed")
    context: Optional[str] = Field(None, description="Error context if audit failed")
    raw_data: Optional[Dict[str, Any]] = Field(
        None, description="Raw audit data from Lighthouse"
    )


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
    confidence: ConfidenceLevel = Field(
        ConfidenceLevel.LOW, description="Low confidence due to error"
    )
    strategy: str = Field("unknown", description="Unknown strategy due to error")


class WebsiteScoringSummary(BaseModel):
    """Summary of website scoring results for multiple audits."""

    business_id: str = Field(..., description="Business identifier")
    total_audits: int = Field(..., description="Total number of audits performed")
    successful_audits: int = Field(..., description="Number of successful audits")
    failed_audits: int = Field(..., description="Number of failed audits")
    average_scores: WebsiteScore = Field(
        ..., description="Average scores across all audits"
    )
    latest_audit: Optional[LighthouseAuditResponse] = Field(
        None, description="Most recent audit result"
    )
    audit_history: List[LighthouseAuditResponse] = Field(
        default_factory=list, description="Audit history"
    )


class AuditThresholds(BaseModel):
    """Configurable thresholds for audit scoring."""

    performance_min: float = Field(
        70.0, ge=0, le=100, description="Minimum acceptable performance score"
    )
    accessibility_min: float = Field(
        80.0, ge=0, le=100, description="Minimum acceptable accessibility score"
    )
    best_practices_min: float = Field(
        80.0, ge=0, le=100, description="Minimum acceptable best practices score"
    )
    seo_min: float = Field(
        80.0, ge=0, le=100, description="Minimum acceptable SEO score"
    )
    overall_min: float = Field(
        75.0, ge=0, le=100, description="Minimum acceptable overall score"
    )

    @validator("overall_min")
    def validate_overall_threshold(cls, v, values):
        """Validate that overall threshold is reasonable given category thresholds."""
        category_thresholds = [
            values.get("performance_min", 70),
            values.get("accessibility_min", 80),
            values.get("best_practices_min", 80),
            values.get("seo_min", 80),
        ]
        min_category = min(category_thresholds)
        if v > min_category:
            raise ValueError(
                "Overall threshold cannot be higher than the lowest category threshold"
            )
        return v


class AuditConfiguration(BaseModel):
    """Configuration for Lighthouse audits."""

    timeout_seconds: int = Field(
        30, ge=10, le=120, description="Audit timeout in seconds"
    )
    max_retries: int = Field(
        3, ge=1, le=5, description="Maximum number of retry attempts"
    )
    retry_delay_base: float = Field(
        1.0, ge=0.5, le=5.0, description="Base delay for exponential backoff"
    )
    enable_core_web_vitals: bool = Field(
        True, description="Whether to extract Core Web Vitals"
    )
    enable_raw_data: bool = Field(
        False, description="Whether to include raw audit data in response"
    )
    thresholds: AuditThresholds = Field(
        default_factory=AuditThresholds, description="Scoring thresholds"
    )


class FallbackScore(BaseModel):
    """Fallback scoring result with heuristic-only scoring and reduced confidence."""

    # Heuristic-only scores (0-100 scale)
    trust_score: float = Field(
        ..., ge=0, le=100, description="Trust signal score (0-100)"
    )
    cro_score: float = Field(
        ..., ge=0, le=100, description="Conversion optimization score (0-100)"
    )
    mobile_score: float = Field(
        ..., ge=0, le=100, description="Mobile usability score (0-100)"
    )
    content_score: float = Field(
        ..., ge=0, le=100, description="Content quality score (0-100)"
    )
    social_score: float = Field(
        ..., ge=0, le=100, description="Social proof score (0-100)"
    )
    overall_score: float = Field(
        ..., ge=0, le=100, description="Overall fallback score (0-100)"
    )

    # Reduced confidence for fallback scenarios
    confidence_level: ConfidenceLevel = Field(
        ..., description="Reduced confidence level for fallback"
    )
    fallback_reason: str = Field(..., description="Reason for using fallback scoring")
    fallback_timestamp: float = Field(
        ..., description="Unix timestamp of fallback decision"
    )

    @validator("overall_score")
    def validate_overall_score(cls, v):
        """Validate that overall score is within expected range."""
        if v < 0 or v > 100:
            raise ValueError("Overall score must be between 0 and 100")
        return v


class FallbackReason(BaseModel):
    """Model for tracking fallback reasons and decisions."""

    failure_type: str = Field(..., description="Type of Lighthouse failure")
    error_message: str = Field(..., description="Error message from Lighthouse")
    severity_level: str = Field(
        ..., description="Severity level (low/medium/high/critical)"
    )
    fallback_decision: str = Field(..., description="Decision made for fallback")
    retry_attempts: int = Field(0, ge=0, description="Number of retry attempts made")
    success_status: bool = Field(..., description="Whether fallback was successful")
    fallback_timestamp: float = Field(
        ..., description="Unix timestamp of fallback decision"
    )


class FallbackMetrics(BaseModel):
    """Metrics for tracking fallback performance and success rates."""

    fallback_success_rate: float = Field(
        ..., ge=0, le=100, description="Percentage of successful fallbacks"
    )
    average_fallback_score_quality: float = Field(
        ..., ge=0, le=100, description="Average quality of fallback scores"
    )
    failure_pattern_analysis: Dict[str, int] = Field(
        default_factory=dict, description="Analysis of failure patterns"
    )
    performance_metrics: Dict[str, float] = Field(
        default_factory=dict, description="Performance metrics for fallback"
    )
    total_fallbacks: int = Field(
        0, ge=0, description="Total number of fallbacks attempted"
    )
    successful_fallbacks: int = Field(
        0, ge=0, description="Number of successful fallbacks"
    )


class FallbackHistory(BaseModel):
    """Historical fallback data for trend analysis."""

    business_id: str = Field(..., description="Business identifier")
    website_url: str = Field(..., description="Website URL")
    run_id: str = Field(..., description="Run identifier")
    fallback_timestamp: float = Field(..., description="Unix timestamp of fallback")
    fallback_reason: FallbackReason = Field(..., description="Reason for fallback")
    fallback_score: FallbackScore = Field(..., description="Fallback scoring result")
    lighthouse_failure_context: Dict[str, Any] = Field(
        default_factory=dict, description="Context of Lighthouse failure"
    )


class FallbackQuality(BaseModel):
    """Quality assessment for heuristic-only fallback results."""

    reliability_score: float = Field(
        ..., ge=0, le=100, description="Reliability score of fallback results"
    )
    data_completeness: float = Field(
        ..., ge=0, le=100, description="Completeness of heuristic data"
    )
    confidence_adjustment: float = Field(
        ..., description="Confidence adjustment factor"
    )
    quality_indicators: Dict[str, bool] = Field(
        default_factory=dict, description="Quality indicators"
    )
    recommendation: str = Field(
        ..., description="Recommendation for using fallback results"
    )


class FallbackScoringRequest(BaseModel):
    """Request model for fallback scoring."""

    website_url: HttpUrl = Field(..., description="URL of the website to score")
    business_id: str = Field(..., description="Business identifier for tracking")
    run_id: Optional[str] = Field(None, description="Run identifier for tracking")
    lighthouse_failure_reason: str = Field(
        ..., description="Reason why Lighthouse failed"
    )
    fallback_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Additional fallback parameters"
    )

    @validator("website_url")
    def validate_website_url(cls, v):
        """Validate website URL format."""
        if not str(v).startswith(("http://", "https://")):
            raise ValueError("Website URL must start with http:// or https://")
        return v


class FallbackScoringResponse(BaseModel):
    """Response model for fallback scoring results."""

    success: bool = Field(
        ..., description="Whether the fallback scoring was successful"
    )
    website_url: str = Field(..., description="URL that was scored")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    fallback_timestamp: float = Field(
        ..., description="Unix timestamp of fallback scoring"
    )
    fallback_score: FallbackScore = Field(..., description="Fallback scoring results")
    fallback_reason: FallbackReason = Field(..., description="Reason for fallback")
    fallback_quality: FallbackQuality = Field(
        ..., description="Quality assessment of fallback results"
    )
    retry_attempts: int = Field(0, ge=0, description="Number of retry attempts made")
    error: Optional[str] = Field(None, description="Error message if fallback failed")
    error_code: Optional[str] = Field(None, description="Error code if fallback failed")
    context: Optional[str] = Field(None, description="Error context if fallback failed")


class FallbackScoringError(BaseModel):
    """Error response model for fallback scoring failures."""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    context: str = Field(..., description="Error context")
    website_url: str = Field(..., description="URL that failed to score")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    fallback_timestamp: float = Field(..., description="Unix timestamp of error")
    error_code: Optional[str] = Field(None, description="Error code")
    fallback_score: FallbackScore = Field(
        ..., description="Default fallback scores (all 0)"
    )
    fallback_reason: FallbackReason = Field(..., description="Default fallback reason")
    fallback_quality: FallbackQuality = Field(
        ..., description="Default fallback quality"
    )


class FallbackMonitoringResponse(BaseModel):
    """Response model for fallback monitoring and analytics."""

    success: bool = Field(
        ..., description="Whether the monitoring data was retrieved successfully"
    )
    timestamp: float = Field(..., description="Unix timestamp of monitoring data")
    metrics: FallbackMetrics = Field(..., description="Fallback performance metrics")
    recent_fallbacks: List[FallbackHistory] = Field(
        default_factory=list, description="Recent fallback history"
    )
    failure_patterns: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, description="Analysis of failure patterns"
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Recommendations for improvement"
    )


# Score Validation and Confidence Schemas


class ValidationMetrics(BaseModel):
    """Metrics for score validation and confidence calculation."""

    correlation_coefficient: float = Field(
        ...,
        ge=-1,
        le=1,
        description="Pearson correlation coefficient between scoring methods",
    )
    statistical_significance: float = Field(
        ..., ge=0, le=1, description="Statistical significance of correlation"
    )
    variance_analysis: float = Field(
        ..., ge=0, description="Variance analysis between score sets"
    )
    reliability_indicator: float = Field(
        ..., ge=0, le=1, description="Overall reliability indicator"
    )


class IssuePriority(BaseModel):
    """Priority ranking for detected issues."""

    category: str = Field(
        ..., description="Issue category (performance, accessibility, seo, etc.)"
    )
    priority_level: str = Field(
        ..., description="Priority level (critical, high, medium, low)"
    )
    business_impact_score: float = Field(
        ..., ge=0, le=1, description="Business impact score (0-1)"
    )
    recommended_action: str = Field(
        ..., description="Recommended action to resolve issue"
    )
    description: str = Field(..., description="Description of the issue")


class FinalScore(BaseModel):
    """Final weighted score with confidence indicators."""

    weighted_score: float = Field(
        ..., ge=0, le=100, description="Weighted final score (0-100)"
    )
    confidence_level: ConfidenceLevel = Field(
        ..., description="Confidence level of final score"
    )
    discrepancy_count: int = Field(
        ..., ge=0, description="Number of discrepancies detected"
    )
    validation_status: str = Field(..., description="Status of validation process")


class ScoreValidationResult(BaseModel):
    """Complete result of score validation and confidence calculation."""

    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    confidence_level: ConfidenceLevel = Field(
        ..., description="Overall confidence level"
    )
    correlation_coefficient: float = Field(
        ..., ge=-1, le=1, description="Correlation between scoring methods"
    )
    discrepancy_count: int = Field(
        ..., ge=0, description="Number of discrepancies detected"
    )
    final_score: FinalScore = Field(
        ..., description="Final weighted score with confidence"
    )
    validation_metrics: ValidationMetrics = Field(
        ..., description="Detailed validation metrics"
    )
    issue_priorities: List[IssuePriority] = Field(
        default_factory=list, description="Prioritized list of issues"
    )
    validation_timestamp: str = Field(..., description="ISO timestamp of validation")


class ScoreValidationRequest(BaseModel):
    """Request model for score validation."""

    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    lighthouse_scores: List[WebsiteScore] = Field(
        ..., description="Lighthouse scoring results"
    )
    heuristic_scores: List[HeuristicScore] = Field(
        ..., description="Heuristic scoring results"
    )
    validation_parameters: Optional[Dict[str, Any]] = Field(
        None, description="Additional validation parameters"
    )


class ScoreValidationResponse(BaseModel):
    """Response model for score validation."""

    success: bool = Field(..., description="Whether validation was successful")
    validation_result: ScoreValidationResult = Field(
        ..., description="Complete validation results"
    )
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(..., description="ISO timestamp of response")


class ScoreValidationError(BaseModel):
    """Error response model for score validation failures."""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    timestamp: str = Field(..., description="ISO timestamp of error")


class WebsiteScoringRequest(BaseModel):
    """Request model for website scoring."""

    website_url: str = Field(..., description="URL of the website to score")
    business_id: Optional[str] = Field(None, description="Business identifier")
    scoring_method: str = Field("comprehensive", description="Scoring method to use")
    run_id: Optional[str] = Field(None, description="Processing run identifier")
