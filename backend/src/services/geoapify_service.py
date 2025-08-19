"""
Geoapify service for geocoding and extracting location information.
Used to determine country codes for SerpAPI searches.
"""

import httpx
import logging
from typing import Optional, Dict, Any
from src.core.base_service import BaseService
from src.core.config import get_api_config


class GeoapifyService(BaseService):
    """Service for interacting with Geoapify API to extract location information."""
    
    def __init__(self):
        super().__init__("GeoapifyService")
        self.api_config = get_api_config()
        self.api_key = self.api_config.GEOAPIFY_API_KEY
        self.base_url = "https://api.geoapify.com/v1/geocode/autocomplete"
        
        if not self.api_key:
            self.logger.warning("GEOAPIFY_API_KEY not configured")
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, str) and len(data.strip()) > 0
    
    async def extract_country_code(self, location: str) -> Optional[str]:
        """
        Extract country code from a location string.
        
        Args:
            location: Location string (e.g., "Austin, Texas", "Manila, Philippines")
            
        Returns:
            Two-letter country code (e.g., "us", "ph") or None if not found
        """
        if not self.api_key:
            self.logger.warning("Cannot extract country code: GEOAPIFY_API_KEY not configured")
            return None
        
        try:
            # Build search parameters - exactly matching GEOAPIFY.md pattern
            # Limit to 1 result for better performance since we only need country code
            params = {
                "text": location,
                "apiKey": self.api_key,
                "limit": 1  # Only get 1 result for country code extraction
            }
            
            # Make async API request
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract country code from features - exactly matching GEOAPIFY.md structure
                if data.get("features") and len(data["features"]) > 0:
                    result = data["features"][0]
                    country_code = result.get("properties", {}).get("country_code")
                    
                    if country_code:
                        self.logger.info(f"Extracted country code '{country_code}' for location '{location}'")
                        return country_code.lower()
                    else:
                        self.logger.warning(f"No country code found for location '{location}'")
                        return None
                else:
                    self.logger.warning(f"No features found for location '{location}'")
                    return None
                    
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error extracting country code for '{location}': {e}")
            return None
        except httpx.RequestError as e:
            self.logger.error(f"Request error extracting country code for '{location}': {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error extracting country code for '{location}': {e}")
            return None
    
    def get_location_info(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed location information from Geoapify.
        
        Args:
            location: Location string
            
        Returns:
            Dictionary with location details or None if not found
        """
        if not self.api_key:
            self.logger.warning("Cannot get location info: GEOAPIFY_API_KEY not configured")
            return None
        
        try:
            params = {
                "text": location,
                "apiKey": self.api_key
            }
            
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("features") and len(data["features"]) > 0:
                    result = data["features"][0]
                    properties = result.get("properties", {})
                    return {
                        "country_code": properties.get("country_code", "").lower(),
                        "country": properties.get("country"),
                        "state": properties.get("state"),
                        "city": properties.get("city"),
                        "lat": properties.get("lat"),
                        "lon": properties.get("lon"),
                        "formatted_address": properties.get("formatted")
                    }
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"Error getting location info for '{location}': {e}")
            return None


def get_geoapify_service() -> GeoapifyService:
    """Dependency injection function for GeoapifyService."""
    return GeoapifyService()
