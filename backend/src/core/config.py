"""
Configuration management for the LeadGen Makeover Agent API.
Handles environment variables, API keys, and rate limiting settings.
"""

import os
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from dotenv import load_dotenv

# Load environment variables from env.local
env_path = Path(__file__).parent.parent.parent / "env.local"
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to .env if env.local doesn't exist
    load_dotenv()


class APIConfig(BaseSettings):
    """API configuration with rate limiting and timeout settings."""

    # API Keys (with defaults for development)
    GOOGLE_PLACES_API_KEY: str = "development_key"
    YELP_FUSION_API_KEY: str = "development_key"
    LIGHTHOUSE_API_KEY: str = "development_key"
    OPENAI_API_KEY: str = "development_key"

    # Rate Limiting Configuration
    GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE: int = 100
    YELP_FUSION_RATE_LIMIT_PER_DAY: int = 5000
    LIGHTHOUSE_RATE_LIMIT_PER_DAY: int = 25000
    LIGHTHOUSE_RATE_LIMIT_PER_MINUTE: int = 240

    # Heuristic Evaluation Configuration
    HEURISTICS_RATE_LIMIT_PER_MINUTE: int = 60
    HEURISTICS_EVALUATION_TIMEOUT_SECONDS: int = 15
    FALLBACK_RATE_LIMIT_PER_MINUTE: int = 120

    # API Timeout Settings
    API_TIMEOUT_SECONDS: int = 30
    LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS: int = 30
    LIGHTHOUSE_CONNECT_TIMEOUT_SECONDS: int = 10
    LIGHTHOUSE_READ_TIMEOUT_SECONDS: int = 25
    LIGHTHOUSE_FALLBACK_TIMEOUT_SECONDS: int = 15

    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60

    @field_validator("GOOGLE_PLACES_API_KEY")
    @classmethod
    def validate_google_places_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("GOOGLE_PLACES_API_KEY cannot be empty")
        return v.strip()

    @field_validator("YELP_FUSION_API_KEY")
    @classmethod
    def validate_yelp_fusion_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("YELP_FUSION_API_KEY cannot be empty")
        return v.strip()

    @field_validator("LIGHTHOUSE_API_KEY")
    @classmethod
    def validate_lighthouse_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("LIGHTHOUSE_API_KEY cannot be empty")
        return v.strip()

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("OPENAI_API_KEY cannot be empty")
        return v.strip()

    @field_validator("GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE")
    @classmethod
    def validate_google_rate_limit(cls, v):
        if v <= 0:
            raise ValueError("GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE must be positive")
        return v

    @field_validator("YELP_FUSION_RATE_LIMIT_PER_DAY")
    @classmethod
    def validate_yelp_rate_limit(cls, v):
        if v <= 0:
            raise ValueError("YELP_FUSION_RATE_LIMIT_PER_DAY must be positive")
        return v

    @field_validator("LIGHTHOUSE_RATE_LIMIT_PER_DAY")
    @classmethod
    def validate_lighthouse_daily_rate_limit(cls, v):
        if v <= 0:
            raise ValueError("LIGHTHOUSE_RATE_LIMIT_PER_DAY must be positive")
        return v

    @field_validator("LIGHTHOUSE_RATE_LIMIT_PER_MINUTE")
    @classmethod
    def validate_lighthouse_minute_rate_limit(cls, v):
        if v <= 0:
            raise ValueError("LIGHTHOUSE_RATE_LIMIT_PER_MINUTE must be positive")
        return v

    model_config = ConfigDict(env_file="env.local", case_sensitive=True, extra="ignore")


class BusinessDiscoveryConfig(BaseSettings):
    """Configuration for business discovery services."""
    
    # Default search parameters
    DEFAULT_SEARCH_RADIUS_METERS: int = 5000  # 5km radius
    MAX_SEARCH_RESULTS: int = 20
    MIN_RATING_THRESHOLD: float = 3.5
    
    # Business matching thresholds
    SIMILARITY_THRESHOLD: float = 0.8
    DUPLICATE_CONFIDENCE_THRESHOLD: float = 0.9
    
    # Search categories and niches
    SUPPORTED_NICHES: list = ["gym", "restaurant", "salon", "spa", "fitness", "wellness"]
    
    model_config = ConfigDict(env_file="env.local", case_sensitive=True, extra="ignore")


class Settings(BaseSettings):
    """Main application settings."""

    # Application Configuration
    APP_NAME: str = "LeadGen Makeover Agent API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LeadGen Makeover Agent"

    model_config = ConfigDict(env_file="env.local", case_sensitive=True, extra="ignore")

    @property
    def api(self) -> APIConfig:
        """Get API configuration."""
        return APIConfig()

    @property
    def business_discovery(self) -> BusinessDiscoveryConfig:
        """Get business discovery configuration."""
        return BusinessDiscoveryConfig()


# Global settings instance
settings = Settings()


def get_api_config() -> APIConfig:
    """Get the API configuration instance."""
    return settings.api


def get_business_discovery_config() -> BusinessDiscoveryConfig:
    """Get the business discovery configuration instance."""
    return settings.business_discovery


def validate_environment() -> bool:
    """Validate that all required environment variables are set."""
    try:
        # This will raise validation errors if required vars are missing
        _ = settings.api
        _ = settings.business_discovery
        return True
    except Exception as e:
        print(f"Environment validation failed: {e}")
        return False


def get_google_places_key() -> str:
    """Get Google Places API key for business discovery."""
    return settings.api.GOOGLE_PLACES_API_KEY


def get_yelp_fusion_key() -> str:
    """Get Yelp Fusion API key for business discovery."""
    return settings.api.YELP_FUSION_API_KEY


def get_openai_key() -> str:
    """Get OpenAI API key for AI-powered analysis."""
    return settings.api.OPENAI_API_KEY
