"""
Website scoring schemas for Lighthouse API integration.
Defines data models for website performance audits and scoring results.
"""

from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field, field_validator, HttpUrl
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
    
    @field_validator('overall')
    @classmethod
    def validate_overall_score(cls, v):
        """Validate that overall score is within expected range."""
        if v < 0 or v > 100:
            raise ValueError('Overall score must be between 0 and 100')
        return v


class HeuristicScore(BaseModel):
    """Heuristic evaluation scores across different categories."""
    
    trust_score: float = Field(..., ge=0, le=100, description="Trust signal score (0-100)")
    cro_score: float = Field(..., ge=0, le=100, description="Conversion optimization score (0-100)")
    mobile_score: float = Field(..., ge=0, le=100, description="Mobile usability score (0-100)")
    content_score: float = Field(..., ge=0, le=100, description="Content quality score (0-100)")
    social_score: float = Field(..., ge=0, le=100, description="Social proof score (0-100)")
    overall_heuristic_score: float = Field(..., ge=0, le=100, description="Overall heuristic score (0-100)")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level of heuristic evaluation")
    
    @field_validator('overall_heuristic_score')
    @classmethod
    def validate_overall_heuristic_score(cls, v):
        """Validate that overall heuristic score is within expected range."""
        if v < 0 or v > 100:
            raise ValueError('Overall heuristic score must be between 0 and 100')
        return v


class TrustSignals(BaseModel):
    """Trust signal elements detected on the website."""
    
    has_https: bool = Field(False, description="Website uses HTTPS")
    has_privacy_policy: bool = Field(False, description="Privacy policy page exists")
    has_contact_info: bool = Field(False, description="Contact information is visible")
    has_about_page: bool = Field(False, description="About page exists")
    has_terms_of_service: bool = Field(False, description="Terms of service page exists")
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
    has_responsive_design: bool = Field(False, description="Responsive design implemented")
    has_mobile_navigation: bool = Field(False, description="Mobile-friendly navigation")
    has_readable_fonts: bool = Field(False, description="Readable font sizes on mobile")
    has_adequate_spacing: bool = Field(False, description="Adequate spacing between elements")


class ContentQuality(BaseModel):
    """Content quality heuristics evaluation."""
    
    has_clear_headlines: bool = Field(False, description="Clear and descriptive headlines")
    has_structured_content: bool = Field(False, description="Well-structured content")
    has_internal_links: bool = Field(False, description="Internal linking structure")
    has_external_links: bool = Field(False, description="Relevant external links")
    has_meta_descriptions: bool = Field(False, description="Meta descriptions present")
    has_alt_text: bool = Field(False, description="Alt text for images")
    has_faq_section: bool = Field(False, description="FAQ section present")
    has_blog_content: bool = Field(False, description="Blog or content section")


class SocialProof(BaseModel):
    """Social proof elements detected."""
    
    has_customer_count: bool = Field(False, description="Customer count displayed")
    has_case_studies: bool = Field(False, description="Case studies present")
    has_awards: bool = Field(False, description="Awards or recognition")
    has_partnerships: bool = Field(False, description="Partnership logos")
    has_media_mentions: bool = Field(False, description="Media mentions or press")
    has_social_media: bool = Field(False, description="Social media presence")


class PageSpeedAuditRequest(BaseModel):
    """Request model for PageSpeed audit."""
    
    website_url: str = Field(..., description="Website URL to analyze")
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Run identifier")
    strategy: AuditStrategy = Field(AuditStrategy.MOBILE, description="Analysis strategy")
    categories: Optional[List[str]] = Field(
        default=["performance", "accessibility", "best-practices", "seo"],
        description="Lighthouse categories to analyze"
    )
    
    @field_validator('website_url')
    @classmethod
    def validate_website_url(cls, v):
        """Validate website URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Website URL must start with http:// or https://')
        return v


class CoreWebVitals(BaseModel):
    """Core Web Vitals metrics from PageSpeed audit."""
    
    first_contentful_paint: Optional[float] = Field(None, description="First Contentful Paint in milliseconds")
    largest_contentful_paint: Optional[float] = Field(None, description="Largest Contentful Paint in milliseconds")
    cumulative_layout_shift: Optional[float] = Field(None, description="Cumulative Layout Shift score")
    total_blocking_time: Optional[float] = Field(None, description="Total Blocking Time in milliseconds")
    speed_index: Optional[float] = Field(None, description="Speed Index in milliseconds")


class PageSpeedAuditResponse(BaseModel):
    """Response model for PageSpeed audit."""
    
    success: bool = Field(..., description="Whether the audit was successful")
    website_url: str = Field(..., description="Website URL analyzed")
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Run identifier")
    audit_timestamp: float = Field(..., description="Audit timestamp")
    strategy: str = Field(..., description="Analysis strategy used")
    scores: WebsiteScore = Field(..., description="Performance scores")
    core_web_vitals: CoreWebVitals = Field(..., description="Core Web Vitals metrics")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw API response data")


class PageSpeedAuditError(BaseModel):
    """Error model for PageSpeed audit failures."""
    
    success: bool = Field(False, description="Audit was not successful")
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    context: str = Field(..., description="Error context")
    run_id: str = Field(..., description="Run identifier")
    business_id: str = Field(..., description="Business identifier")


class HeuristicEvaluationRequest(BaseModel):
    """Request model for heuristic evaluation."""
    
    website_url: HttpUrl = Field(..., description="URL of the website to evaluate")
    business_id: str = Field(..., description="Business identifier for tracking")
    run_id: Optional[str] = Field(None, description="Run identifier for tracking")
    evaluation_parameters: Optional[Dict[str, Any]] = Field(None, description="Additional evaluation parameters")
    
    @field_validator('website_url')
    @classmethod
    def validate_website_url(cls, v):
        """Validate website URL format."""
        if not str(v).startswith(('http://', 'https://')):
            raise ValueError('Website URL must start with http:// or https://')
        return v


class HeuristicEvaluationResponse(BaseModel):
    """Response model for heuristic evaluation results."""
    
    success: bool = Field(..., description="Whether the evaluation was successful")
    website_url: str = Field(..., description="URL that was evaluated")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    evaluation_timestamp: float = Field(..., description="Unix timestamp of evaluation completion")
    scores: HeuristicScore = Field(..., description="Heuristic evaluation scores")
    trust_signals: TrustSignals = Field(..., description="Trust signal elements detected")
    cro_elements: CROElements = Field(..., description="CRO elements detected")
    mobile_usability: MobileUsability = Field(..., description="Mobile usability assessment")
    content_quality: ContentQuality = Field(..., description="Content quality assessment")
    social_proof: SocialProof = Field(..., description="Social proof elements detected")
    confidence: ConfidenceLevel = Field(..., description="Confidence level of results")
    error: Optional[str] = Field(None, description="Error message if evaluation failed")
    error_code: Optional[str] = Field(None, description="Error code if evaluation failed")
    context: Optional[str] = Field(None, description="Error context if evaluation failed")
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
    confidence: ConfidenceLevel = Field(ConfidenceLevel.LOW, description="Low confidence due to error")


class LighthouseAuditRequest(BaseModel):
    """Request model for Lighthouse audit."""
    
    website_url: HttpUrl = Field(..., description="URL of the website to audit")
    business_id: str = Field(..., description="Business identifier for tracking")
    run_id: Optional[str] = Field(None, description="Run identifier for tracking")
    strategy: AuditStrategy = Field(AuditStrategy.MOBILE, description="Audit strategy (desktop/mobile)")
    audit_parameters: Optional[Dict[str, Any]] = Field(None, description="Additional audit parameters")
    
    @field_validator('website_url')
    @classmethod
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
    
    @field_validator('overall_min')
    @classmethod
    def validate_overall_threshold(cls, v, info):
        """Validate that overall threshold is reasonable given category thresholds."""
        category_thresholds = [
            info.data.get('performance_min', 70),
            info.data.get('accessibility_min', 80),
            info.data.get('best_practices_min', 80),
            info.data.get('seo_min', 80)
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


# Score Validation Schemas

class ValidationMetrics(BaseModel):
    """Statistical metrics for score validation and confidence calculation."""
    
    correlation_coefficient: float = Field(..., ge=-1.0, le=1.0, description="Pearson correlation between scoring methods")
    statistical_significance: float = Field(..., ge=0.0, le=1.0, description="Statistical significance of correlation")
    variance_analysis: float = Field(..., ge=0.0, description="Standard deviation of score differences")
    reliability_indicator: float = Field(..., ge=0.0, le=1.0, description="Overall reliability score")
    sample_size: int = Field(..., ge=1, description="Number of score pairs analyzed")
    confidence_interval: Tuple[float, float] = Field(..., description="95% confidence interval for correlation")


class IssuePriority(str, Enum):
    """Priority levels for identified issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(str, Enum):
    """Categories for identified issues."""
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    SEO = "seo"
    BEST_PRACTICES = "best_practices"
    TECHNICAL = "technical"
    CONTENT = "content"
    MOBILE = "mobile"
    SECURITY = "security"


class IssuePriorityDetails(BaseModel):
    """Detailed information about issue priority and categorization."""
    
    priority: IssuePriority = Field(..., description="Priority level of the issue")
    category: IssueCategory = Field(..., description="Category of the issue")
    business_impact_score: float = Field(..., ge=0.0, le=10.0, description="Business impact score (0-10)")
    recommended_action: str = Field(..., description="Recommended action to resolve the issue")
    estimated_effort: str = Field(..., description="Estimated effort to resolve (low/medium/high)")
    dependencies: List[str] = Field(default_factory=list, description="List of dependent issues")


class ScoreValidationResult(BaseModel):
    """Result of score validation and confidence assessment."""
    
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    validation_timestamp: float = Field(..., description="Unix timestamp of validation completion")
    confidence_level: ConfidenceLevel = Field(..., description="Overall confidence level")
    score_correlation: float = Field(..., ge=-1.0, le=1.0, description="Correlation between scoring methods")
    discrepancy_count: int = Field(..., ge=0, description="Number of significant discrepancies found")
    validation_metrics: ValidationMetrics = Field(..., description="Statistical validation metrics")
    issue_priorities: List[IssuePriorityDetails] = Field(default_factory=list, description="Prioritized list of issues")
    final_weighted_score: float = Field(..., ge=0.0, le=100.0, description="Final weighted score (0-100)")
    validation_status: str = Field(..., description="Status of validation process")
    notes: Optional[str] = Field(None, description="Additional validation notes")
    
    @property
    def correlation_coefficient(self) -> float:
        """Alias for score_correlation for backward compatibility."""
        return self.score_correlation
    
    @property
    def final_score(self) -> Optional[float]:
        """Alias for final_weighted_score for backward compatibility."""
        return self.final_weighted_score


class FinalScore(BaseModel):
    """Final weighted score with confidence indicators."""
    
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    weighted_final_score: float = Field(..., ge=0.0, le=100.0, description="Final weighted score (0-100)")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level of the final score")
    lighthouse_weight: float = Field(0.8, ge=0.0, le=1.0, description="Weight applied to Lighthouse scores")
    heuristic_weight: float = Field(0.2, ge=0.0, le=1.0, description="Weight applied to heuristic scores")
    discrepancy_flags: List[str] = Field(default_factory=list, description="List of discrepancy flags")
    issue_priorities: List[IssuePriorityDetails] = Field(default_factory=list, description="Prioritized issues")
    validation_status: str = Field(..., description="Status of score validation")
    calculation_timestamp: float = Field(..., description="Unix timestamp of calculation")


# Fallback Scoring Schemas

class FallbackReason(str, Enum):
    """Reasons for using fallback scoring."""
    LIGHTHOUSE_FAILURE = "lighthouse_failure"
    HEURISTIC_FAILURE = "heuristic_failure"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INVALID_URL = "invalid_url"
    NETWORK_ERROR = "network_error"
    UNKNOWN_ERROR = "unknown_error"


class FallbackReasonDetails(BaseModel):
    """Detailed tracking of fallback reasons and decisions."""
    
    failure_type: str = Field(..., description="Type of failure that occurred")
    error_message: str = Field(..., description="Error message from the failure")
    severity_level: str = Field(..., description="Severity level of the failure")
    fallback_decision: str = Field(..., description="Decision made about fallback")
    retry_attempts: int = Field(..., ge=0, description="Number of retry attempts made")
    success_status: bool = Field(..., description="Whether the fallback was successful")
    fallback_timestamp: float = Field(..., description="Unix timestamp of fallback decision")


class FallbackQuality(str, Enum):
    """Quality assessment of fallback scoring."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNRELIABLE = "unreliable"


class FallbackQualityDetails(BaseModel):
    """Detailed quality assessment of fallback scoring."""
    
    reliability_score: float = Field(..., ge=0.0, le=100.0, description="Reliability score of fallback method")
    data_completeness: float = Field(..., ge=0.0, le=100.0, description="Completeness of available data")
    confidence_adjustment: float = Field(..., ge=0.0, le=1.0, description="Confidence adjustment factor")
    quality_indicators: Dict[str, Any] = Field(..., description="Quality indicators and flags")
    recommendation: str = Field(..., description="Recommendation for using fallback scores")


class FallbackMetrics(BaseModel):
    """Metrics for fallback scoring quality assessment."""
    
    # Quality assessment fields
    data_completeness: float = Field(..., ge=0.0, le=1.0, description="Completeness of available data")
    source_reliability: float = Field(..., ge=0.0, le=1.0, description="Reliability of data source")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in fallback scores")
    fallback_reason: FallbackReason = Field(..., description="Reason for using fallback scoring")
    quality_rating: FallbackQuality = Field(..., description="Overall quality rating")
    
    # Performance tracking fields
    fallback_success_rate: float = Field(..., ge=0.0, le=100.0, description="Percentage of successful fallbacks")
    average_fallback_score_quality: float = Field(..., ge=0.0, le=100.0, description="Average quality of fallback scores")
    failure_pattern_analysis: Dict[str, int] = Field(..., description="Analysis of failure patterns by type")
    performance_metrics: Dict[str, float] = Field(..., description="Performance metrics like execution time")
    total_fallbacks: int = Field(..., ge=0, description="Total number of fallback attempts")
    successful_fallbacks: int = Field(..., ge=0, description="Number of successful fallbacks")


class FallbackHistory(BaseModel):
    """History of fallback scoring usage."""
    
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    fallback_timestamp: float = Field(..., description="Unix timestamp of fallback usage")
    fallback_reason: FallbackReason = Field(..., description="Reason for fallback")
    original_error: Optional[str] = Field(None, description="Original error that triggered fallback")
    fallback_scores: Dict[str, float] = Field(..., description="Scores generated by fallback method")
    quality_metrics: FallbackMetrics = Field(..., description="Quality assessment metrics")


class FallbackScore(BaseModel):
    """Fallback scoring result when primary methods fail."""
    
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    website_url: str = Field(..., description="URL of the website scored")
    fallback_timestamp: float = Field(..., description="Unix timestamp of fallback scoring")
    fallback_reason: FallbackReason = Field(..., description="Reason for using fallback scoring")
    fallback_scores: Dict[str, float] = Field(..., description="Scores generated by fallback method")
    quality_metrics: FallbackMetrics = Field(..., description="Quality assessment of fallback scores")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level of fallback scores")
    notes: Optional[str] = Field(None, description="Additional notes about fallback scoring")
    fallback_history: List[FallbackHistory] = Field(default_factory=list, description="History of fallback usage")


# Rate Limiting Error Schema

class RateLimitExceededError(BaseModel):
    """Error response when rate limit is exceeded."""
    
    success: bool = Field(False, description="Request was not successful due to rate limiting")
    error: str = Field("Rate limit exceeded", description="Error message")
    error_code: str = Field("RATE_LIMIT_EXCEEDED", description="Error code for rate limiting")
    context: str = Field(..., description="Context where rate limit was exceeded")
    retry_after: Optional[int] = Field(None, description="Seconds to wait before retrying")
    business_id: Optional[str] = Field(None, description="Business identifier if available")
    run_id: Optional[str] = Field(None, description="Run identifier if available")


# Fallback Scoring Request/Response Schemas

class FallbackScoringRequest(BaseModel):
    """Request model for fallback scoring."""
    
    website_url: str = Field(..., description="URL of the website to score")
    business_id: str = Field(..., description="Business identifier")
    pagespeed_failure_reason: str = Field(..., description="Reason why PageSpeed failed")
    run_id: Optional[str] = Field(None, description="Run identifier")
    fallback_parameters: Optional[Dict[str, Any]] = Field(None, description="Additional fallback parameters")


class FallbackScoringResponse(BaseModel):
    """Response model for fallback scoring."""
    
    success: bool = Field(..., description="Whether fallback scoring was successful")
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Run identifier")
    fallback_score: Optional[FallbackScore] = Field(None, description="Fallback score if successful")
    error: Optional[str] = Field(None, description="Error message if fallback failed")
    error_code: Optional[str] = Field(None, description="Error code if fallback failed")
    fallback_timestamp: float = Field(..., description="Unix timestamp of fallback completion")


class FallbackScoringError(BaseModel):
    """Error model for fallback scoring failures."""
    
    success: bool = Field(False, description="Fallback scoring was not successful")
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    context: str = Field(..., description="Error context")
    website_url: str = Field(..., description="URL that failed fallback scoring")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    fallback_timestamp: float = Field(..., description="Unix timestamp of error")


class FallbackMonitoringResponse(BaseModel):
    """Response model for fallback monitoring."""
    
    success: bool = Field(..., description="Whether monitoring was successful")
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Run identifier")
    fallback_metrics: FallbackMetrics = Field(..., description="Fallback metrics")
    monitoring_timestamp: float = Field(..., description="Unix timestamp of monitoring")


# Score Validation Request/Response Schemas

class ScoreValidationRequest(BaseModel):
    """Request model for score validation."""
    
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    lighthouse_scores: List[WebsiteScore] = Field(..., description="Lighthouse scoring results")
    heuristic_scores: List[HeuristicScore] = Field(..., description="Heuristic scoring results")
    validation_parameters: Optional[Dict[str, Any]] = Field(None, description="Additional validation parameters")


class ScoreValidationResponse(BaseModel):
    """Response model for score validation."""
    
    success: bool = Field(..., description="Whether validation was successful")
    business_id: str = Field(..., description="Business identifier")
    run_id: str = Field(..., description="Processing run identifier")
    validation_result: Optional[ScoreValidationResult] = Field(None, description="Validation results if successful")
    final_score: Optional[FinalScore] = Field(None, description="Final weighted score if successful")
    error: Optional[str] = Field(None, description="Error message if validation failed")
    error_code: Optional[str] = Field(None, description="Error code if validation failed")
    validation_timestamp: float = Field(..., description="Unix timestamp of validation completion")


class ScoreValidationError(BaseModel):
    """Error model for score validation failures."""
    
    success: bool = Field(False, description="Score validation was not successful")
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    context: str = Field(..., description="Error context")
    business_id: str = Field(..., description="Business identifier")
    run_id: Optional[str] = Field(None, description="Run identifier")
    validation_timestamp: float = Field(..., description="Unix timestamp of error")
