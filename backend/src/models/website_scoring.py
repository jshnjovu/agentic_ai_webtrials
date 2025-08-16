"""
Database models for website scoring and Lighthouse audit results.
"""

from datetime import datetime
from typing import Dict, Any
from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Text,
    JSON,
    Index,
    Boolean,
    Integer,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class WebsiteScore(Base):
    """Database model for website performance scores."""

    __tablename__ = "website_scores"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=True, index=True)

    # Website information
    website_url = Column(String(500), nullable=False, index=True)
    audit_strategy = Column(String(50), nullable=False, default="desktop")

    # Performance scores (0-100 scale)
    performance_score = Column(Float, nullable=False)
    accessibility_score = Column(Float, nullable=False)
    best_practices_score = Column(Float, nullable=False)
    seo_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)

    # Core Web Vitals metrics
    first_contentful_paint = Column(Float, nullable=True)
    largest_contentful_paint = Column(Float, nullable=True)
    cumulative_layout_shift = Column(Float, nullable=True)
    total_blocking_time = Column(Float, nullable=True)
    speed_index = Column(Float, nullable=True)

    # Audit metadata
    confidence_level = Column(String(20), nullable=False, default="low")
    audit_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_website_scores_business_timestamp", "business_id", "audit_timestamp"
        ),
        Index("idx_website_scores_url_timestamp", "website_url", "audit_timestamp"),
        Index("idx_website_scores_run_id", "run_id"),
        Index("idx_website_scores_overall_score", "overall_score"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "run_id": self.run_id,
            "website_url": self.website_url,
            "audit_strategy": self.audit_strategy,
            "performance_score": self.performance_score,
            "accessibility_score": self.accessibility_score,
            "best_practices_score": self.best_practices_score,
            "seo_score": self.seo_score,
            "overall_score": self.overall_score,
            "first_contentful_paint": self.first_contentful_paint,
            "largest_contentful_paint": self.largest_contentful_paint,
            "cumulative_layout_shift": self.cumulative_layout_shift,
            "total_blocking_time": self.total_blocking_time,
            "speed_index": self.speed_index,
            "confidence_level": self.confidence_level,
            "audit_timestamp": (
                self.audit_timestamp.isoformat() if self.audit_timestamp else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_schema_data(cls, data: Dict[str, Any]) -> "WebsiteScore":
        """Create model instance from schema data."""
        return cls(
            business_id=data.get("business_id"),
            run_id=data.get("run_id"),
            website_url=data.get("website_url"),
            audit_strategy=data.get("strategy", "desktop"),
            performance_score=data.get("scores", {}).get("performance", 0.0),
            accessibility_score=data.get("scores", {}).get("accessibility", 0.0),
            best_practices_score=data.get("scores", {}).get("best_practices", 0.0),
            seo_score=data.get("scores", {}).get("seo", 0.0),
            overall_score=data.get("overall_score", 0.0),
            first_contentful_paint=data.get("core_web_vitals", {}).get(
                "first_contentful_paint"
            ),
            largest_contentful_paint=data.get("core_web_vitals", {}).get(
                "largest_contentful_paint"
            ),
            cumulative_layout_shift=data.get("core_web_vitals", {}).get(
                "cumulative_layout_shift"
            ),
            total_blocking_time=data.get("core_web_vitals", {}).get(
                "total_blocking_time"
            ),
            speed_index=data.get("core_web_vitals", {}).get("speed_index"),
            confidence_level=data.get("confidence", "low"),
            audit_timestamp=datetime.fromtimestamp(
                data.get("audit_timestamp", datetime.utcnow().timestamp())
            ),
        )


class HeuristicScore(Base):
    """Database model for heuristic evaluation scores."""

    __tablename__ = "heuristic_scores"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=True, index=True)

    # Website information
    website_url = Column(String(500), nullable=False, index=True)

    # Heuristic scores (0-100 scale)
    trust_score = Column(Float, nullable=False)
    cro_score = Column(Float, nullable=False)
    mobile_score = Column(Float, nullable=False)
    content_score = Column(Float, nullable=False)
    social_score = Column(Float, nullable=False)
    overall_heuristic_score = Column(Float, nullable=False)

    # Confidence level
    confidence_level = Column(String(20), nullable=False, default="low")

    # Evaluation metadata
    evaluation_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_heuristic_scores_business_timestamp",
            "business_id",
            "evaluation_timestamp",
        ),
        Index(
            "idx_heuristic_scores_url_timestamp", "website_url", "evaluation_timestamp"
        ),
        Index("idx_heuristic_scores_run_id", "run_id"),
        Index("idx_heuristic_scores_overall_score", "overall_heuristic_score"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "run_id": self.run_id,
            "website_url": self.website_url,
            "trust_score": self.trust_score,
            "cro_score": self.cro_score,
            "mobile_score": self.mobile_score,
            "content_score": self.content_score,
            "social_score": self.social_score,
            "overall_heuristic_score": self.overall_heuristic_score,
            "confidence_level": self.confidence_level,
            "evaluation_timestamp": (
                self.evaluation_timestamp.isoformat()
                if self.evaluation_timestamp
                else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class HeuristicEvaluationResult(Base):
    """Database model for storing raw heuristic evaluation results."""

    __tablename__ = "heuristic_evaluation_results"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=True, index=True)

    # Website information
    website_url = Column(String(500), nullable=False, index=True)

    # Evaluation results
    success = Column(String(10), nullable=False, default="false")  # 'true' or 'false'
    confidence_level = Column(String(20), nullable=False, default="low")

    # Trust signals detected
    has_https = Column(Boolean, nullable=False, default=False)
    has_privacy_policy = Column(Boolean, nullable=False, default=False)
    has_contact_info = Column(Boolean, nullable=False, default=False)
    has_about_page = Column(Boolean, nullable=False, default=False)
    has_terms_of_service = Column(Boolean, nullable=False, default=False)
    has_ssl_certificate = Column(Boolean, nullable=False, default=False)
    has_business_address = Column(Boolean, nullable=False, default=False)
    has_phone_number = Column(Boolean, nullable=False, default=False)
    has_email = Column(Boolean, nullable=False, default=False)

    # CRO elements detected
    has_cta_buttons = Column(Boolean, nullable=False, default=False)
    has_contact_forms = Column(Boolean, nullable=False, default=False)
    has_pricing_tables = Column(Boolean, nullable=False, default=False)
    has_testimonials = Column(Boolean, nullable=False, default=False)
    has_reviews = Column(Boolean, nullable=False, default=False)
    has_social_proof = Column(Boolean, nullable=False, default=False)
    has_urgency_elements = Column(Boolean, nullable=False, default=False)
    has_trust_badges = Column(Boolean, nullable=False, default=False)

    # Mobile usability
    has_viewport_meta = Column(Boolean, nullable=False, default=False)
    has_touch_targets = Column(Boolean, nullable=False, default=False)
    has_responsive_design = Column(Boolean, nullable=False, default=False)
    has_mobile_navigation = Column(Boolean, nullable=False, default=False)
    has_readable_fonts = Column(Boolean, nullable=False, default=False)
    has_adequate_spacing = Column(Boolean, nullable=False, default=False)

    # Content quality
    has_proper_headings = Column(Boolean, nullable=False, default=False)
    has_alt_text = Column(Boolean, nullable=False, default=False)
    has_meta_description = Column(Boolean, nullable=False, default=False)
    has_meta_keywords = Column(Boolean, nullable=False, default=False)
    has_structured_data = Column(Boolean, nullable=False, default=False)
    has_internal_links = Column(Boolean, nullable=False, default=False)
    has_external_links = Column(Boolean, nullable=False, default=False)
    has_blog_content = Column(Boolean, nullable=False, default=False)

    # Social proof
    has_social_media_links = Column(Boolean, nullable=False, default=False)
    has_customer_reviews = Column(Boolean, nullable=False, default=False)
    has_case_studies = Column(Boolean, nullable=False, default=False)
    has_awards_certifications = Column(Boolean, nullable=False, default=False)
    has_partner_logos = Column(Boolean, nullable=False, default=False)
    has_user_generated_content = Column(Boolean, nullable=False, default=False)

    # Raw evaluation data
    raw_evaluation_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    error_context = Column(String(100), nullable=True)

    # Evaluation metadata
    evaluation_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_heuristic_eval_business_timestamp",
            "business_id",
            "evaluation_timestamp",
        ),
        Index(
            "idx_heuristic_eval_url_timestamp", "website_url", "evaluation_timestamp"
        ),
        Index("idx_heuristic_eval_run_id", "run_id"),
        Index("idx_heuristic_eval_success", "success"),
        Index("idx_heuristic_eval_confidence", "confidence_level"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "run_id": self.run_id,
            "website_url": self.website_url,
            "success": self.success,
            "confidence_level": self.confidence_level,
            "has_https": self.has_https,
            "has_privacy_policy": self.has_privacy_policy,
            "has_contact_info": self.has_contact_info,
            "has_about_page": self.has_about_page,
            "has_terms_of_service": self.has_terms_of_service,
            "has_ssl_certificate": self.has_ssl_certificate,
            "has_business_address": self.has_business_address,
            "has_phone_number": self.has_phone_number,
            "has_email": self.has_email,
            "has_cta_buttons": self.has_cta_buttons,
            "has_contact_forms": self.has_contact_forms,
            "has_pricing_tables": self.has_pricing_tables,
            "has_testimonials": self.has_testimonials,
            "has_reviews": self.has_reviews,
            "has_social_proof": self.has_social_proof,
            "has_urgency_elements": self.has_urgency_elements,
            "has_trust_badges": self.has_trust_badges,
            "has_viewport_meta": self.has_viewport_meta,
            "has_touch_targets": self.has_touch_targets,
            "has_responsive_design": self.has_responsive_design,
            "has_mobile_navigation": self.has_mobile_navigation,
            "has_readable_fonts": self.has_readable_fonts,
            "has_adequate_spacing": self.has_adequate_spacing,
            "has_proper_headings": self.has_proper_headings,
            "has_alt_text": self.has_alt_text,
            "has_meta_description": self.has_meta_description,
            "has_meta_keywords": self.has_meta_keywords,
            "has_structured_data": self.has_structured_data,
            "has_internal_links": self.has_internal_links,
            "has_external_links": self.has_external_links,
            "has_blog_content": self.has_blog_content,
            "has_social_media_links": self.has_social_media_links,
            "has_customer_reviews": self.has_customer_reviews,
            "has_case_studies": self.has_case_studies,
            "has_awards_certifications": self.has_awards_certifications,
            "has_partner_logos": self.has_partner_logos,
            "has_user_generated_content": self.has_user_generated_content,
            "raw_evaluation_data": self.raw_evaluation_data,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "error_context": self.error_context,
            "evaluation_timestamp": (
                self.evaluation_timestamp.isoformat()
                if self.evaluation_timestamp
                else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class LighthouseAuditResult(Base):
    """Database model for storing raw Lighthouse audit results."""

    __tablename__ = "lighthouse_audit_results"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=True, index=True)

    # Website information
    website_url = Column(String(500), nullable=False, index=True)
    audit_strategy = Column(String(50), nullable=False, default="desktop")

    # Audit results
    success = Column(String(10), nullable=False, default="false")  # 'true' or 'false'
    confidence_level = Column(String(20), nullable=False, default="low")

    # Raw audit data
    raw_audit_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    error_code = Column(String(100), nullable=True)
    error_context = Column(String(100), nullable=True)

    # Audit metadata
    audit_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_lighthouse_audit_business_timestamp", "business_id", "audit_timestamp"
        ),
        Index("idx_lighthouse_audit_url_timestamp", "website_url", "audit_timestamp"),
        Index("idx_lighthouse_audit_run_id", "run_id"),
        Index("idx_lighthouse_audit_success", "success"),
        Index("idx_lighthouse_audit_confidence", "confidence_level"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "run_id": self.run_id,
            "website_url": self.website_url,
            "audit_strategy": self.audit_strategy,
            "success": self.success,
            "confidence_level": self.confidence_level,
            "raw_audit_data": self.raw_audit_data,
            "error_message": self.error_message,
            "error_code": self.error_code,
            "error_context": self.error_context,
            "audit_timestamp": (
                self.audit_timestamp.isoformat() if self.audit_timestamp else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_schema_data(cls, data: Dict[str, Any]) -> "LighthouseAuditResult":
        """Create model instance from schema data."""
        return cls(
            business_id=data.get("business_id"),
            run_id=data.get("run_id"),
            website_url=data.get("website_url"),
            audit_strategy=data.get("strategy", "desktop"),
            success=str(data.get("success", False)).lower(),
            confidence_level=data.get("confidence", "low"),
            raw_audit_data=data.get("raw_data"),
            error_message=data.get("error"),
            error_code=data.get("error_code"),
            error_context=data.get("context"),
            audit_timestamp=datetime.fromtimestamp(
                data.get("audit_timestamp", datetime.utcnow().timestamp())
            ),
        )


class FallbackScore(Base):
    """Database model for fallback scoring results."""

    __tablename__ = "fallback_scores"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=True, index=True)

    # Website information
    website_url = Column(String(500), nullable=False, index=True)

    # Heuristic-only scores (0-100 scale)
    trust_score = Column(Float, nullable=False)
    cro_score = Column(Float, nullable=False)
    mobile_score = Column(Float, nullable=False)
    content_score = Column(Float, nullable=False)
    social_score = Column(Float, nullable=False)
    overall_score = Column(Float, nullable=False)

    # Fallback-specific fields
    confidence_level = Column(String(20), nullable=False, default="low")
    fallback_reason = Column(String(500), nullable=False)
    fallback_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_fallback_scores_business_timestamp",
            "business_id",
            "fallback_timestamp",
        ),
        Index("idx_fallback_scores_url_timestamp", "website_url", "fallback_timestamp"),
        Index("idx_fallback_scores_run_id", "run_id"),
        Index("idx_fallback_scores_overall_score", "overall_score"),
        Index("idx_fallback_scores_confidence", "confidence_level"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "run_id": self.run_id,
            "website_url": self.website_url,
            "trust_score": self.trust_score,
            "cro_score": self.cro_score,
            "mobile_score": self.mobile_score,
            "content_score": self.content_score,
            "social_score": self.social_score,
            "overall_score": self.overall_score,
            "confidence_level": self.confidence_level,
            "fallback_reason": self.fallback_reason,
            "fallback_timestamp": (
                self.fallback_timestamp.isoformat() if self.fallback_timestamp else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FallbackReason(Base):
    """Database model for tracking fallback reasons and decisions."""

    __tablename__ = "fallback_reasons"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=True, index=True)

    # Fallback reason details
    failure_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    severity_level = Column(String(20), nullable=False)
    fallback_decision = Column(String(200), nullable=False)
    retry_attempts = Column(Integer, nullable=False, default=0)
    success_status = Column(Boolean, nullable=False, default=False)

    # Timestamps
    fallback_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_fallback_reasons_business_timestamp",
            "business_id",
            "fallback_timestamp",
        ),
        Index("idx_fallback_reasons_run_id", "run_id"),
        Index("idx_fallback_reasons_failure_type", "failure_type"),
        Index("idx_fallback_reasons_severity", "severity_level"),
        Index("idx_fallback_reasons_success", "success_status"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "run_id": self.run_id,
            "failure_type": self.failure_type,
            "error_message": self.error_message,
            "severity_level": self.severity_level,
            "fallback_decision": self.fallback_decision,
            "retry_attempts": self.retry_attempts,
            "success_status": self.success_status,
            "fallback_timestamp": (
                self.fallback_timestamp.isoformat() if self.fallback_timestamp else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FallbackMetrics(Base):
    """Database model for tracking fallback performance metrics."""

    __tablename__ = "fallback_metrics"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Metrics data
    fallback_success_rate = Column(Float, nullable=False)
    average_fallback_score_quality = Column(Float, nullable=False)
    failure_pattern_analysis = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    total_fallbacks = Column(Integer, nullable=False, default=0)
    successful_fallbacks = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_fallback_metrics_created", "created_at"),
        Index("idx_fallback_metrics_success_rate", "fallback_success_rate"),
        Index("idx_fallback_metrics_quality", "average_fallback_score_quality"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "fallback_success_rate": self.fallback_success_rate,
            "average_fallback_score_quality": self.average_fallback_score_quality,
            "failure_pattern_analysis": self.failure_pattern_analysis,
            "performance_metrics": self.performance_metrics,
            "total_fallbacks": self.total_fallbacks,
            "successful_fallbacks": self.successful_fallbacks,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FallbackHistory(Base):
    """Database model for historical fallback data."""

    __tablename__ = "fallback_history"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    website_url = Column(String(500), nullable=False, index=True)
    run_id = Column(String(255), nullable=True, index=True)

    # Fallback data
    fallback_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    fallback_reason_id = Column(UUID(as_uuid=True), nullable=True)
    fallback_score_id = Column(UUID(as_uuid=True), nullable=True)
    lighthouse_failure_context = Column(JSON, nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_fallback_history_business_timestamp",
            "business_id",
            "fallback_timestamp",
        ),
        Index(
            "idx_fallback_history_url_timestamp", "website_url", "fallback_timestamp"
        ),
        Index("idx_fallback_history_run_id", "run_id"),
        Index("idx_fallback_history_reason_id", "fallback_reason_id"),
        Index("idx_fallback_history_score_id", "fallback_score_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "website_url": self.website_url,
            "run_id": self.run_id,
            "fallback_timestamp": (
                self.fallback_timestamp.isoformat() if self.fallback_timestamp else None
            ),
            "fallback_reason_id": (
                str(self.fallback_reason_id) if self.fallback_reason_id else None
            ),
            "fallback_score_id": (
                str(self.fallback_score_id) if self.fallback_score_id else None
            ),
            "lighthouse_failure_context": self.lighthouse_failure_context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FallbackQuality(Base):
    """Database model for fallback quality assessment."""

    __tablename__ = "fallback_quality"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Quality metrics
    reliability_score = Column(Float, nullable=False)
    data_completeness = Column(Float, nullable=False)
    confidence_adjustment = Column(Float, nullable=False)
    quality_indicators = Column(JSON, nullable=True)
    recommendation = Column(Text, nullable=False)

    # Associated fallback score
    fallback_score_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_fallback_quality_score_id", "fallback_score_id"),
        Index("idx_fallback_quality_reliability", "reliability_score"),
        Index("idx_fallback_quality_completeness", "data_completeness"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "reliability_score": self.reliability_score,
            "data_completeness": self.data_completeness,
            "confidence_adjustment": self.confidence_adjustment,
            "quality_indicators": self.quality_indicators,
            "recommendation": self.recommendation,
            "fallback_score_id": str(self.fallback_score_id),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


# Score Validation and Confidence Models


class ScoreValidationResult(Base):
    """Database model for score validation results."""

    __tablename__ = "score_validation_results"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Business and run identification
    business_id = Column(String(255), nullable=False, index=True)
    run_id = Column(String(255), nullable=False, index=True)

    # Validation results
    confidence_level = Column(String(20), nullable=False, default="low")
    correlation_coefficient = Column(Float, nullable=False)
    discrepancy_count = Column(Integer, nullable=False, default=0)

    # Timestamps
    validation_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index(
            "idx_score_validation_business_timestamp",
            "business_id",
            "validation_timestamp",
        ),
        Index("idx_score_validation_run_id", "run_id"),
        Index("idx_score_validation_confidence", "confidence_level"),
        Index("idx_score_validation_correlation", "correlation_coefficient"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "business_id": self.business_id,
            "run_id": self.run_id,
            "confidence_level": self.confidence_level,
            "correlation_coefficient": self.correlation_coefficient,
            "discrepancy_count": self.discrepancy_count,
            "validation_timestamp": (
                self.validation_timestamp.isoformat()
                if self.validation_timestamp
                else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ValidationMetrics(Base):
    """Database model for validation metrics."""

    __tablename__ = "validation_metrics"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associated validation result
    validation_result_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Metrics
    correlation_coefficient = Column(Float, nullable=False)
    statistical_significance = Column(Float, nullable=False)
    variance_analysis = Column(Float, nullable=False)
    reliability_indicator = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_validation_metrics_result_id", "validation_result_id"),
        Index("idx_validation_metrics_reliability", "reliability_indicator"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "validation_result_id": str(self.validation_result_id),
            "correlation_coefficient": self.correlation_coefficient,
            "statistical_significance": self.statistical_significance,
            "variance_analysis": self.variance_analysis,
            "reliability_indicator": self.reliability_indicator,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class IssuePriority(Base):
    """Database model for issue priorities."""

    __tablename__ = "issue_priorities"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associated validation result
    validation_result_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Issue details
    category = Column(String(100), nullable=False, index=True)
    priority_level = Column(String(20), nullable=False, index=True)
    business_impact_score = Column(Float, nullable=False)
    recommended_action = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_issue_priorities_result_id", "validation_result_id"),
        Index("idx_issue_priorities_category", "category"),
        Index("idx_issue_priorities_priority", "priority_level"),
        Index("idx_issue_priorities_impact", "business_impact_score"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "validation_result_id": str(self.validation_result_id),
            "category": self.category,
            "priority_level": self.priority_level,
            "business_impact_score": self.business_impact_score,
            "recommended_action": self.recommended_action,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FinalScore(Base):
    """Database model for final weighted scores."""

    __tablename__ = "final_scores"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Associated validation result
    validation_result_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Score details
    weighted_score = Column(Float, nullable=False)
    confidence_level = Column(String(20), nullable=False)
    discrepancy_count = Column(Integer, nullable=False, default=0)
    validation_status = Column(String(50), nullable=False, default="completed")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_final_scores_result_id", "validation_result_id"),
        Index("idx_final_scores_weighted", "weighted_score"),
        Index("idx_final_scores_confidence", "confidence_level"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            "id": str(self.id),
            "validation_result_id": str(self.validation_result_id),
            "weighted_score": self.weighted_score,
            "confidence_level": self.confidence_level,
            "discrepancy_count": self.discrepancy_count,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
