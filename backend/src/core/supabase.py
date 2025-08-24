"""
Supabase client configuration for the LeadGen Makeover Agent API.
Uses the new environment variable names supplied by the Supabase dashboard.
"""

import os
from typing import Optional
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def load_supabase_environment() -> None:
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
                # Use override=True to ensure variables are loaded
                load_dotenv(env_file, override=True)
                loaded_files.append(str(env_file))
                logger.info(f"Supabase: Loaded environment file: {env_file}")
                
                # Verify key variables are loaded
                if env_file.name == ".env":
                    supabase_url = os.getenv('SUPABASE_URL') or os.getenv('NEXT_PUBLIC_SUPABASE_URL')
                    if supabase_url:
                        logger.info(f"✅ Supabase URL loaded: {supabase_url[:20]}...")
                    else:
                        logger.warning("⚠️ Supabase URL not found in .env file")
                        
            except Exception as e:
                logger.warning(f"Supabase: Failed to load {env_file}: {e}")
    
    if not loaded_files:
        logger.warning("Supabase: No environment files found. Using system environment variables only.")
    else:
        logger.info(f"Supabase: Loaded environment from: {', '.join(loaded_files)}")


class SupabaseConfig:
    """Configuration class for Supabase client using the new env vars."""

    def __init__(self) -> None:
        # Load environment files first
        load_supabase_environment()
        
        # Core credentials
        self.url: str = os.getenv("SUPABASE_URL") or os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
        self.anon_key: str = os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", "")
        self.service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

        # Direct PostgreSQL connection strings
        self.postgres_url: str = os.getenv("POSTGRES_URL", "")
        self.postgres_url_non_pooling: str = os.getenv("POSTGRES_URL_NON_POOLING", "")

        # Validate
        if not self.url or not self.anon_key or not self.service_role_key:
            raise ValueError(
                "SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL), "
                "SUPABASE_ANON_KEY (or NEXT_PUBLIC_SUPABASE_ANON_KEY), "
                "and SUPABASE_SERVICE_ROLE_KEY must be set."
            )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def get_client(self) -> Client:
        """
        Returns a Supabase client authenticated with the *service role* key
        (full RLS bypass). Use this from the backend only.
        """
        options = ClientOptions(
            schema="public",
            headers={"X-Client-Info": "leadgen-makeover-agent/1.0.0"},
        )
        return create_client(self.url, self.service_role_key, options)

    def get_database_url(self) -> str:
        """
        Returns a **pooler** (port 6543) connection string suitable for
        most serverless / backend use-cases.
        """
        return self.postgres_url or self.postgres_url_non_pooling

    def is_configured(self) -> bool:
        """Quick sanity check."""
        return bool(self.url and self.anon_key and self.service_role_key)


# Lazy loading - don't instantiate until needed
_supabase_config_instance: Optional[SupabaseConfig] = None


def _get_supabase_config() -> SupabaseConfig:
    """Get or create the Supabase configuration instance."""
    global _supabase_config_instance
    if _supabase_config_instance is None:
        try:
            _supabase_config_instance = SupabaseConfig()
            logger.info("Supabase configuration initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase configuration: {e}")
            raise
    return _supabase_config_instance


# ------------------------------------------------------------------
# Module-level convenience functions (unchanged API)
# ------------------------------------------------------------------
def get_supabase_client() -> Client:
    """Get a Supabase client instance."""
    config = _get_supabase_config()
    return config.get_client()


def get_database_url() -> str:
    """Get the database connection URL."""
    config = _get_supabase_config()
    return config.get_database_url()


def is_supabase_configured() -> bool:
    """Check if Supabase is properly configured."""
    try:
        config = _get_supabase_config()
        return config.is_configured()
    except Exception:
        return False