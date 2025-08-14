"""
Data models and schemas
"""

from .authentication import (
    GooglePlacesAuthRequest,
    YelpFusionAuthRequest,
    AuthenticationResponse,
    HealthCheckResponse
)

from .business_search import (
    BusinessSearchRequest,
    BusinessSearchResponse,
    BusinessSearchError,
    BusinessData,
    LocationType
)

from .business_merging import (
    DataSource,
    BusinessInput,
    MatchDetails,
    MergedBusiness,
    MergeRequest,
    MergeResponse
)

__all__ = [
    # Authentication schemas
    'GooglePlacesAuthRequest',
    'YelpFusionAuthRequest', 
    'AuthenticationResponse',
    'HealthCheckResponse',
    # Business search schemas
    'BusinessSearchRequest',
    'BusinessSearchResponse',
    'BusinessSearchError',
    'BusinessData',
    'LocationType',
    # Business merging schemas
    'DataSource',
    'BusinessInput',
    'MatchDetails',
    'MergedBusiness',
    'MergeRequest',
    'MergeResponse'
]
