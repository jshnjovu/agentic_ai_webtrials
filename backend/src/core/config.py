"""
Configuration management for the LeadGen Makeover Agent API.
Handles environment variables, API keys, and rate limiting settings.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict


class APIConfig(BaseSettings):
    """Configuration for external API integrations."""
    
    # Google Places API Configuration
    GOOGLE_PLACES_API_KEY: str
    
    # Yelp Fusion API Configuration  
    YELP_FUSION_API_KEY: str
    
    # Rate Limiting Configuration
    GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE: int = 100
    YELP_FUSION_RATE_LIMIT_PER_DAY: int = 5000
    
    # API Timeout Settings
    API_TIMEOUT_SECONDS: int = 30
    
    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60
    
    @field_validator('GOOGLE_PLACES_API_KEY')
    @classmethod
    def validate_google_places_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('GOOGLE_PLACES_API_KEY cannot be empty')
        return v.strip()
    
    @field_validator('YELP_FUSION_API_KEY')
    @classmethod
    def validate_yelp_fusion_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('YELP_FUSION_API_KEY cannot be empty')
        return v.strip()
    
    @field_validator('GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE')
    @classmethod
    def validate_google_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('YELP_FUSION_RATE_LIMIT_PER_DAY must be positive')
        return v
    
    @field_validator('YELP_FUSION_RATE_LIMIT_PER_DAY')
    @classmethod
    def validate_yelp_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('YELP_FUSION_RATE_LIMIT_PER_MINUTE must be positive')
        return v
    
    model_config = ConfigDict(
        env_file = ".env",
        case_sensitive = True
    )


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application Configuration
    APP_NAME: str = "LeadGen Makeover Agent API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LeadGen Makeover Agent"
    
    # External APIs
    api: APIConfig = APIConfig()
    
    model_config = ConfigDict(
        env_file = ".env",
        case_sensitive = True
    )


# Global settings instance
settings = Settings()


def get_api_config() -> APIConfig:
    """Get the API configuration instance."""
    return settings.api


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    try:
        # This will raise validation errors if required vars are missing
        _ = settings.api
        return True
    except Exception as e:
        print(f"Environment validation failed: {e}")
        return False
