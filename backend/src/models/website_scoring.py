"""
Database models for website scoring and Lighthouse audit results.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, Index
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
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_website_scores_business_timestamp', 'business_id', 'audit_timestamp'),
        Index('idx_website_scores_url_timestamp', 'website_url', 'audit_timestamp'),
        Index('idx_website_scores_run_id', 'run_id'),
        Index('idx_website_scores_overall_score', 'overall_score'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            'id': str(self.id),
            'business_id': self.business_id,
            'run_id': self.run_id,
            'website_url': self.website_url,
            'audit_strategy': self.audit_strategy,
            'performance_score': self.performance_score,
            'accessibility_score': self.accessibility_score,
            'best_practices_score': self.best_practices_score,
            'seo_score': self.seo_score,
            'overall_score': self.overall_score,
            'first_contentful_paint': self.first_contentful_paint,
            'largest_contentful_paint': self.largest_contentful_paint,
            'cumulative_layout_shift': self.cumulative_layout_shift,
            'total_blocking_time': self.total_blocking_time,
            'speed_index': self.speed_index,
            'confidence_level': self.confidence_level,
            'audit_timestamp': self.audit_timestamp.isoformat() if self.audit_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_schema_data(cls, data: Dict[str, Any]) -> 'WebsiteScore':
        """Create model instance from schema data."""
        return cls(
            business_id=data.get('business_id'),
            run_id=data.get('run_id'),
            website_url=data.get('website_url'),
            audit_strategy=data.get('strategy', 'desktop'),
            performance_score=data.get('scores', {}).get('performance', 0.0),
            accessibility_score=data.get('scores', {}).get('accessibility', 0.0),
            best_practices_score=data.get('scores', {}).get('best_practices', 0.0),
            seo_score=data.get('scores', {}).get('seo', 0.0),
            overall_score=data.get('overall_score', 0.0),
            first_contentful_paint=data.get('core_web_vitals', {}).get('first_contentful_paint'),
            largest_contentful_paint=data.get('core_web_vitals', {}).get('largest_contentful_paint'),
            cumulative_layout_shift=data.get('core_web_vitals', {}).get('cumulative_layout_shift'),
            total_blocking_time=data.get('core_web_vitals', {}).get('total_blocking_time'),
            speed_index=data.get('core_web_vitals', {}).get('speed_index'),
            confidence_level=data.get('confidence', 'low'),
            audit_timestamp=datetime.fromtimestamp(data.get('audit_timestamp', datetime.utcnow().timestamp()))
        )


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
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_lighthouse_audit_business_timestamp', 'business_id', 'audit_timestamp'),
        Index('idx_lighthouse_audit_url_timestamp', 'website_url', 'audit_timestamp'),
        Index('idx_lighthouse_audit_run_id', 'run_id'),
        Index('idx_lighthouse_audit_success', 'success'),
        Index('idx_lighthouse_audit_confidence', 'confidence_level'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary representation."""
        return {
            'id': str(self.id),
            'business_id': self.business_id,
            'run_id': self.run_id,
            'website_url': self.website_url,
            'audit_strategy': self.audit_strategy,
            'success': self.success,
            'confidence_level': self.confidence_level,
            'raw_audit_data': self.raw_audit_data,
            'error_message': self.error_message,
            'error_code': self.error_code,
            'error_context': self.error_context,
            'audit_timestamp': self.audit_timestamp.isoformat() if self.audit_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_schema_data(cls, data: Dict[str, Any]) -> 'LighthouseAuditResult':
        """Create model instance from schema data."""
        return cls(
            business_id=data.get('business_id'),
            run_id=data.get('run_id'),
            website_url=data.get('website_url'),
            audit_strategy=data.get('strategy', 'desktop'),
            success=str(data.get('success', False)).lower(),
            confidence_level=data.get('confidence', 'low'),
            raw_audit_data=data.get('raw_data'),
            error_message=data.get('error'),
            error_code=data.get('error_code'),
            error_context=data.get('context'),
            audit_timestamp=datetime.fromtimestamp(data.get('audit_timestamp', datetime.utcnow().timestamp()))
        )
