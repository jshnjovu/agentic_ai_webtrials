"""
Data models and schemas
"""

from .authentication import (
    GooglePlacesAuthRequest,
    YelpFusionAuthRequest,
    AuthenticationResponse,
    HealthCheckResponse,
)

from .business_search import (
    BusinessSearchRequest,
    BusinessSearchResponse,
    BusinessSearchError,
    BusinessData,
    LocationType,
)

from .yelp_fusion import (
    YelpBusinessSearchRequest,
    YelpBusinessSearchResponse,
    YelpBusinessSearchError,
    YelpBusinessData,
    YelpLocationType,
)

from .business_matching import (
    ConfidenceLevel,
    BusinessLocation,
    BusinessContactInfo,
    BusinessSourceData,
    BusinessMatchScore,
    BusinessMatchCandidate,
    BusinessMatchingRequest,
    BusinessMatchingResponse,
    BusinessMatchingError,
)

from .business_merging import (
    DataCompletenessScore,
    MergedBusinessData,
    MergeConflict,
    BusinessMergeRequest,
    BusinessMergeResponse,
    BusinessMergeError,
)

from .duplicate_detection import (
    DuplicateType,
    BusinessFingerprint,
    DuplicateGroup,
    DuplicateDetectionRequest,
    DuplicateDetectionResponse,
    DuplicateRemovalRequest,
    DuplicateRemovalResponse,
    DuplicateDetectionError,
)

from .review_management import (
    ReviewStatus,
    ReviewPriority,
    ReviewFlag,
    ReviewWorkflow,
    ReviewAssignmentRequest,
    ReviewStatusUpdateRequest,
    ReviewResolutionRequest,
    ReviewFlagResponse,
    ReviewWorkflowResponse,
    PendingReviewsResponse,
    ReviewManagementError,
)

from .website_scoring import (
    AuditStrategy,
    ConfidenceLevel as ScoringConfidenceLevel,
    WebsiteScore,
    CoreWebVitals,
    LighthouseAuditRequest,
    LighthouseAuditResponse,
    LighthouseAuditError,
    WebsiteScoringSummary,
    AuditThresholds,
    AuditConfiguration,
    WebsiteScoringResponse,
)

__all__ = [
    # Authentication schemas
    "GooglePlacesAuthRequest",
    "YelpFusionAuthRequest",
    "AuthenticationResponse",
    "HealthCheckResponse",
    # Business search schemas
    "BusinessSearchRequest",
    "BusinessSearchResponse",
    "BusinessSearchError",
    "BusinessData",
    "LocationType",
    # Yelp Fusion schemas
    "YelpBusinessSearchRequest",
    "YelpBusinessSearchResponse",
    "YelpBusinessSearchError",
    "YelpBusinessData",
    "YelpLocationType",
    # Business matching schemas
    "ConfidenceLevel",
    "BusinessLocation",
    "BusinessContactInfo",
    "BusinessSourceData",
    "BusinessMatchScore",
    "BusinessMatchCandidate",
    "BusinessMatchingRequest",
    "BusinessMatchingResponse",
    "BusinessMatchingError",
    # Business merging schemas
    "DataCompletenessScore",
    "MergedBusinessData",
    "MergeConflict",
    "BusinessMergeRequest",
    "BusinessMergeResponse",
    "BusinessMergeError",
    # Duplicate detection schemas
    "DuplicateType",
    "BusinessFingerprint",
    "DuplicateGroup",
    "DuplicateDetectionRequest",
    "DuplicateDetectionResponse",
    "DuplicateRemovalRequest",
    "DuplicateRemovalResponse",
    "DuplicateDetectionError",
    # Review management schemas
    "ReviewStatus",
    "ReviewPriority",
    "ReviewFlag",
    "ReviewWorkflow",
    "ReviewAssignmentRequest",
    "ReviewStatusUpdateRequest",
    "ReviewResolutionRequest",
    "ReviewFlagResponse",
    "ReviewWorkflowResponse",
    "PendingReviewsResponse",
    "ReviewManagementError",
    # Website scoring schemas
    "AuditStrategy",
    "ScoringConfidenceLevel",
    "WebsiteScore",
    "CoreWebVitals",
    "LighthouseAuditRequest",
    "LighthouseAuditResponse",
    "LighthouseAuditError",
    "WebsiteScoringSummary",
    "AuditThresholds",
    "AuditConfiguration",
    "WebsiteScoringResponse",
]
