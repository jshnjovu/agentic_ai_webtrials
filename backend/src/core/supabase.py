"""
Supabase client configuration for the LeadGen Makeover Agent API.
Uses the new environment variable names supplied by the Supabase dashboard.
"""

import os
from typing import Optional
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
import logging
from dotenv import load_dotenv

# Load .env if it exists
load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseConfig:
    """Configuration class for Supabase client using the new env vars."""

    def __init__(self) -> None:
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


# Single, reusable config instance
supabase_config = SupabaseConfig()


# ------------------------------------------------------------------
# Module-level convenience functions (unchanged API)
# ------------------------------------------------------------------
def get_supabase_client() -> Client:
    return supabase_config.get_client()


def get_database_url() -> str:
    return supabase_config.get_database_url()


def is_supabase_configured() -> bool:
    return supabase_config.is_configured()