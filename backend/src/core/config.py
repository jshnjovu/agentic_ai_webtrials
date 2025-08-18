"""
Configuration management for the LeadGen Makeover Agent API.
Handles environment variables, API keys, and rate limiting settings.
"""

import os
from pathlib import Path
from typing import Optional, List, Union
from pydantic_settings import BaseSettings
from pydantic import field_validator, ConfigDict
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)


def load_environment_files() -> None:
    """
    Load environment variables from .env files with proper fallback hierarchy.
    
    Loading order (first found takes precedence):
    1. .env.local (for local development overrides)
    2. .env (main environment file)
    3. .env.example (fallback with defaults)
    """
    current_dir = Path(__file__).parent.parent.parent  # backend directory
    
    env_files = [
        current_dir / ".env.local",
        current_dir / ".env", 
        current_dir / ".env.example"
    ]
    
    loaded_files = []
    for env_file in env_files:
        if env_file.exists():
            try:
                load_dotenv(env_file, override=False)  # Don't override already set variables
                loaded_files.append(str(env_file))
                logger.info(f"Loaded environment file: {env_file}")
            except Exception as e:
                logger.warning(f"Failed to load {env_file}: {e}")
    
    if not loaded_files:
        logger.warning("No environment files found. Using system environment variables only.")
    else:
        logger.info(f"Loaded environment from: {', '.join(loaded_files)}")


# Load environment files on module import
load_environment_files()


class APIConfig(BaseSettings):
    """Configuration for external API integrations."""
    
    # SerpAPI Configuration
    SERPAPI_API_KEY: Optional[str] = None
    
    # Google Places API Configuration (deprecated - replaced by SerpAPI)
    GOOGLE_PLACES_API_KEY: Optional[str] = None
    
    # Yelp Fusion API Configuration  
    YELP_FUSION_API_KEY: Optional[str] = None
    
    # Google PageSpeed API Configuration
    GOOGLE_GENERAL_API_KEY: Optional[str] = None
    
    # Rate Limiting Configuration
    SERPAPI_RATE_LIMIT_PER_MINUTE: int = 100
    GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE: int = 100
    YELP_FUSION_RATE_LIMIT_PER_DAY: int = 5000
    PAGESPEED_RATE_LIMIT_PER_DAY: int = 25000
    PAGESPEED_RATE_LIMIT_PER_MINUTE: int = 240
    HEURISTICS_RATE_LIMIT_PER_MINUTE: int = 60
    VALIDATION_RATE_LIMIT_PER_MINUTE: int = 120
    FALLBACK_RATE_LIMIT_PER_MINUTE: int = 60
    
    # API Timeout Settings
    API_TIMEOUT_SECONDS: int = 30
    PAGESPEED_AUDIT_TIMEOUT_SECONDS: int = 30
    PAGESPEED_CONNECT_TIMEOUT_SECONDS: int = 10
    PAGESPEED_READ_TIMEOUT_SECONDS: int = 25
    PAGESPEED_FALLBACK_TIMEOUT_SECONDS: int = 15
    HEURISTICS_EVALUATION_TIMEOUT_SECONDS: int = 15
    
    # Circuit Breaker Configuration
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_RECOVERY_TIMEOUT: int = 60
    
    @field_validator('GOOGLE_PLACES_API_KEY')
    @classmethod
    def validate_google_places_key(cls, v):
        if v is not None and isinstance(v, str):
            v = v.strip()
            if len(v) == 0:
                return None
            if v in ['your_google_places_api_key_here', 'test_key', 'test']:
                logger.warning("Using placeholder Google Places API key")
                return v
        return v
    
    @field_validator('SERPAPI_API_KEY')
    @classmethod
    def validate_serpapi_key(cls, v):
        if v is not None and isinstance(v, str):
            v = v.strip()
            if len(v) == 0:
                return None
            if v in ['your_serpapi_api_key_here', 'test_key', 'test']:
                logger.warning("Using placeholder SerpAPI key")
                return v
        return v
    
    @field_validator('YELP_FUSION_API_KEY')
    @classmethod
    def validate_yelp_fusion_key(cls, v):
        if v is not None and isinstance(v, str):
            v = v.strip()
            if len(v) == 0:
                return None
            if v in ['your_yelp_fusion_api_key_here', 'test_key', 'test']:
                logger.warning("Using placeholder Yelp Fusion API key")
                return v
        return v
    
    @field_validator('GOOGLE_GENERAL_API_KEY')
    @classmethod
    def validate_google_general_key(cls, v):
        if v is not None and isinstance(v, str):
            v = v.strip()
            if len(v) == 0:
                return None
            if v in ['your_google_general_api_key_here', 'test_key', 'test']:
                logger.warning("Using placeholder Google General API key")
                return v
        return v
    
    @field_validator('GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE')
    @classmethod
    def validate_google_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE must be positive')
        return v
    
    @field_validator('SERPAPI_RATE_LIMIT_PER_MINUTE')
    @classmethod
    def validate_serpapi_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('SERPAPI_RATE_LIMIT_PER_MINUTE must be positive')
        return v
    
    @field_validator('YELP_FUSION_RATE_LIMIT_PER_DAY')
    @classmethod
    def validate_yelp_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('YELP_FUSION_RATE_LIMIT_PER_DAY must be positive')
        return v
    
    @field_validator('PAGESPEED_RATE_LIMIT_PER_DAY')
    @classmethod
    def validate_pagespeed_daily_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('PAGESPEED_RATE_LIMIT_PER_DAY must be positive')
        return v
    
    @field_validator('PAGESPEED_RATE_LIMIT_PER_MINUTE')
    @classmethod
    def validate_pagespeed_minute_rate_limit(cls, v):
        if v <= 0:
            raise ValueError('PAGESPEED_RATE_LIMIT_PER_MINUTE must be positive')
        return v
    
    model_config = ConfigDict(
        env_file = [".env.local", ".env", ".env.example"],
        env_file_encoding = "utf-8",
        case_sensitive = True,
        extra = "ignore",
        validate_default = True,
        use_enum_values = True
    )
    
    def is_api_key_valid(self, key_name: str) -> bool:
        """Check if an API key is valid (not None, not empty, not placeholder)."""
        key_value = getattr(self, key_name, None)
        if not key_value:
            return False
        
        placeholder_values = [
            'your_google_places_api_key_here',
            'your_yelp_fusion_api_key_here', 
            'your_google_general_api_key_here',
            'test_key',
            'test'
        ]
        
        return key_value not in placeholder_values
    
    def get_available_apis(self) -> List[str]:
        """Get list of APIs with valid configuration."""
        available = []
        
        if self.is_api_key_valid('SERPAPI_API_KEY'):
            available.append('serpapi')
            
        if self.is_api_key_valid('GOOGLE_PLACES_API_KEY'):
            available.append('google_places')
            
        if self.is_api_key_valid('YELP_FUSION_API_KEY'):
            available.append('yelp_fusion')
            
        if self.is_api_key_valid('GOOGLE_GENERAL_API_KEY'):
            available.append('google_pagespeed')
            
        return available


class Settings(BaseSettings):
    """Main application settings."""
    
    # Application Configuration
    APP_NAME: str = "LeadGen Makeover Agent API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LeadGen Makeover Agent"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    model_config = ConfigDict(
        env_file = [".env.local", ".env", ".env.example"],
        env_file_encoding = "utf-8",
        case_sensitive = True,
        extra = "ignore",
        validate_default = True,
        use_enum_values = True
    )
    
    @property
    def api(self) -> APIConfig:
        """Get API configuration."""
        return APIConfig()


# Global settings instance
settings = Settings()


def get_api_config() -> APIConfig:
    """Get the API configuration instance."""
    return settings.api


def validate_environment() -> bool:
    """
    Validate that the environment is properly configured.
    
    Returns:
        bool: True if environment is valid, False otherwise
    """
    try:
        # Test loading the API configuration
        api_config = settings.api
        
        # Check for at least one valid API configuration
        available_apis = api_config.get_available_apis()
        
        if not available_apis:
            logger.warning("No valid API keys found. The application will run in limited mode.")
            
        # Log configuration status
        logger.info(f"Environment validation successful")
        logger.info(f"Available APIs: {', '.join(available_apis) if available_apis else 'None'}")
        logger.info(f"Debug mode: {settings.DEBUG}")
        logger.info(f"Environment: {settings.ENVIRONMENT}")
        
        return True
        
    except Exception as e:
        logger.error(f"Environment validation failed: {e}")
        return False


def get_configuration_summary() -> dict:
    """
    Get a summary of the current configuration.
    
    Returns:
        dict: Configuration summary
    """
    try:
        api_config = settings.api
        available_apis = api_config.get_available_apis()
        
        return {
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "available_apis": available_apis,
            "api_configuration": {
                "serpapi_configured": api_config.is_api_key_valid('SERPAPI_API_KEY'),
                "google_places_configured": api_config.is_api_key_valid('GOOGLE_PLACES_API_KEY'),
                "yelp_fusion_configured": api_config.is_api_key_valid('YELP_FUSION_API_KEY'),
                "google_pagespeed_configured": api_config.is_api_key_valid('GOOGLE_GENERAL_API_KEY'),
            },
            "rate_limits": {
                "serpapi_per_minute": api_config.SERPAPI_RATE_LIMIT_PER_MINUTE,
                "google_places_per_minute": api_config.GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE,
                "yelp_fusion_per_day": api_config.YELP_FUSION_RATE_LIMIT_PER_DAY,
                "google_pagespeed_per_day": api_config.PAGESPEED_RATE_LIMIT_PER_DAY,
                "google_pagespeed_per_minute": api_config.PAGESPEED_RATE_LIMIT_PER_MINUTE,
                "heuristics_per_minute": api_config.HEURISTICS_RATE_LIMIT_PER_MINUTE,
            },
            "timeouts": {
                "api_timeout": api_config.API_TIMEOUT_SECONDS,
                "google_pagespeed_audit": api_config.PAGESPEED_AUDIT_TIMEOUT_SECONDS,
                "google_pagespeed_connect": api_config.PAGESPEED_CONNECT_TIMEOUT_SECONDS,
                "google_pagespeed_read": api_config.PAGESPEED_READ_TIMEOUT_SECONDS,
                "google_pagespeed_fallback": api_config.PAGESPEED_FALLBACK_TIMEOUT_SECONDS,
                "heuristics_evaluation": api_config.HEURISTICS_EVALUATION_TIMEOUT_SECONDS,
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to generate configuration summary: {e}")
        return {"error": str(e)}
