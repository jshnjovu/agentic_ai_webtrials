"""
Database models for the LeadGen Makeover Agent API.
"""

from .website_scoring import (
    WebsiteScore,
    LighthouseAuditResult
)

__all__ = [
    'WebsiteScore',
    'LighthouseAuditResult'
]
