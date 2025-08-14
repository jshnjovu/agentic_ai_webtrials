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

from .yelp_fusion import (
    YelpBusinessSearchRequest,
    YelpBusinessSearchResponse,
    YelpBusinessSearchError,
    YelpBusinessData,
    YelpLocationType
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
    # Yelp Fusion schemas
    'YelpBusinessSearchRequest',
    'YelpBusinessSearchResponse',
    'YelpBusinessSearchError',
    'YelpBusinessData',
    'YelpLocationType'
]
