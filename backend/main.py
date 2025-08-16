from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import csv
from datetime import datetime
import os
import sys
from pathlib import Path
import uuid

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our configuration and services
from src.core.config import get_google_places_key, get_yelp_fusion_key, get_business_discovery_config
from src.schemas.business_search import BusinessSearchRequest, BusinessSearchResponse
from src.services.google_places_service import GooglePlacesService
from src.services.business_discovery_service import BusinessDiscoveryService

app = FastAPI(title="Agentic AI LeadGen Backend")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class BusinessData(BaseModel):
    business_name: str
    niche: str
    location: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    score_overall: Optional[int] = None
    score_perf: Optional[int] = None
    score_access: Optional[int] = None
    score_seo: Optional[int] = None
    score_trust: Optional[int] = None
    score_cro: Optional[int] = None
    top_issues: Optional[List[str]] = None
    generated_site_url: Optional[str] = None
    outreach_email: Optional[str] = None
    outreach_whatsapp: Optional[str] = None
    outreach_sms: Optional[str] = None
    notes: Optional[str] = None


class BusinessDiscoveryRequest(BaseModel):
    """Request model for business discovery"""
    location: str
    niche: str
    radius: Optional[int] = 5000
    max_results: Optional[int] = 20


class BusinessDiscoveryResponse(BaseModel):
    """Response model for business discovery"""
    success: bool
    businesses: List[dict]
    total_found: int
    location: str
    niche: str
    message: str
    source: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None


@app.get("/")
def root():
    return {
        "message": "Agentic AI LeadGen API running",
        "version": "1.0.0",
        "description": "Business discovery and website scoring API with intelligent fallback system",
        "available_endpoints": {
            "health": "/health - Check API health and configuration status",
            "config": "/config - View current configuration and API key status",
            "discover_businesses": "/discover_businesses - Discover businesses by location and niche",
            "discover_businesses_help": "/discover_businesses/help - Get detailed help for business discovery",
            "save_results": "/save_results - Save business data to CSV (POST)"
        },
        "quick_start": {
            "discover_gyms_in_london": "/discover_businesses?location=London&niche=gym",
            "discover_restaurants_in_manchester": "/discover_businesses?location=Manchester&niche=restaurant",
            "get_help": "/discover_businesses/help"
        },
        "fallback_system": "Uses Lighthouse → Google Places → Yelp Fusion for reliable business discovery"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test configuration loading
        google_key = get_google_places_key()
        yelp_key = get_yelp_fusion_key()
        business_config = get_business_discovery_config()
        
        return {
            "status": "healthy",
            "service": "LeadGen Makeover Agent API",
            "configuration": {
                "google_places_api": "✅ Configured" if google_key else "❌ Not configured",
                "yelp_fusion_api": "✅ Configured" if yelp_key else "❌ Not configured",
                "business_discovery": "✅ Ready" if google_key and yelp_key else "❌ Not ready"
            },
            "business_discovery_config": {
                "default_radius": business_config.DEFAULT_SEARCH_RADIUS_METERS,
                "max_results": business_config.MAX_SEARCH_RESULTS,
                "supported_niches": business_config.SUPPORTED_NICHES
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/discover_businesses", response_model=BusinessDiscoveryResponse)
async def discover_businesses(request: BusinessDiscoveryRequest):
    """
    Discover businesses using intelligent fallback system.
    Tries Lighthouse first, then Google Places API, then Yelp Fusion.
    """
    try:
        # Generate run_id if not provided
        run_id = str(uuid.uuid4())
        
        # Validate request
        if not request.location or not request.niche:
            raise HTTPException(status_code=400, detail="Location and niche are required")
        
        # Get configuration
        business_config = get_business_discovery_config()
        
        # Validate niche
        if request.niche.lower() not in [n.lower() for n in business_config.SUPPORTED_NICHES]:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported niche. Supported niches: {business_config.SUPPORTED_NICHES}"
            )
        
        # Create business discovery service
        discovery_service = BusinessDiscoveryService()
        
        # Execute discovery with fallback system
        discovery_result = await discovery_service.discover_businesses(
            location=request.location,
            niche=request.niche,
            radius=request.radius,
            max_results=request.max_results,
            run_id=run_id
        )
        
        if discovery_result["success"]:
            return BusinessDiscoveryResponse(
                success=True,
                businesses=discovery_result["businesses"],
                total_found=discovery_result["total_found"],
                location=request.location,
                niche=request.niche,
                message=discovery_result.get("message", "Businesses discovered successfully"),
                source=discovery_result.get("source", "unknown")
            )
        else:
            # Return error response
            return BusinessDiscoveryResponse(
                success=False,
                businesses=[],
                total_found=0,
                location=request.location,
                niche=request.niche,
                message="Business discovery failed",
                error=discovery_result.get("error", "Unknown error"),
                error_type=discovery_result.get("error_type", "unknown")
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/discover_businesses/help")
def discover_businesses_help():
    """Get help information for the business discovery endpoint"""
    return {
        "endpoint": "/discover_businesses",
        "method": "GET",
        "description": "Discover businesses using intelligent fallback system",
        "required_parameters": {
            "location": {
                "type": "string",
                "description": "Location to search in (e.g., 'London', 'Manchester', 'Birmingham')",
                "example": "London"
            },
            "niche": {
                "type": "string", 
                "description": "Business niche/category to search for",
                "example": "gym",
                "supported_values": get_business_discovery_config().SUPPORTED_NICHES
            }
        },
        "optional_parameters": {
            "radius": {
                "type": "integer",
                "description": "Search radius in meters",
                "default": 5000,
                "min": 100,
                "max": 50000,
                "example": 5000
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 20,
                "min": 1,
                "max": 50,
                "example": 20
            }
        },
        "fallback_system": {
            "description": "The system automatically tries multiple discovery methods in order:",
            "priority": [
                "1. 🏠 Lighthouse (existing business websites)",
                "2. 🔍 Google Places API",
                "3. ⭐ Yelp Fusion API"
            ]
        },
        "example_requests": [
            "GET /discover_businesses?location=London&niche=gym",
            "GET /discover_businesses?location=Manchester&niche=restaurant&radius=3000&max_results=10",
            "GET /discover_businesses?location=Birmingham&niche=spa"
        ],
        "response_format": {
            "success": "boolean - whether the discovery was successful",
            "businesses": "array - list of discovered businesses",
            "total_found": "integer - total number of businesses found",
            "location": "string - the location that was searched",
            "niche": "string - the niche that was searched",
            "message": "string - description of the result",
            "source": "string - which service provided the results (lighthouse, google_places, yelp_fusion)"
        }
    }


@app.get("/discover_businesses")
async def discover_businesses_get(
    location: Optional[str] = Query(None, description="Location to search in"),
    niche: Optional[str] = Query(None, description="Business niche/category"),
    radius: int = Query(default=5000, description="Search radius in meters"),
    max_results: int = Query(default=20, description="Maximum number of results")
):
    """
    Discover businesses using GET request (easier for testing).
    Uses intelligent fallback system: Lighthouse → Google Places → Yelp Fusion
    """
    # Check if required parameters are provided
    if not location or not niche:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing required parameters",
                "required": ["location", "niche"],
                "received": {
                    "location": location,
                    "niche": niche,
                    "radius": radius,
                    "max_results": max_results
                },
                "message": "Both 'location' and 'niche' parameters are required for business discovery",
                "help": "Use /discover_businesses/help for detailed parameter information and examples"
            }
        )
    
    request = BusinessDiscoveryRequest(
        location=location,
        niche=niche,
        radius=radius,
        max_results=max_results
    )
    return await discover_businesses(request)


@app.post("/save_results")
def save_results(data: List[BusinessData]):
    os.makedirs("../data", exist_ok=True)
    filename = f"../data/output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    fieldnames = list(BusinessData.model_fields.keys())
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row.model_dump())
    return {"status": "success", "file": filename}


@app.get("/config")
def get_config():
    """Get current configuration status"""
    try:
        google_key = get_google_places_key()
        yelp_key = get_yelp_fusion_key()
        business_config = get_business_discovery_config()
        
        return {
            "api_keys": {
                "google_places": "✅ Configured" if google_key else "❌ Not configured",
                "yelp_fusion": "✅ Configured" if yelp_key else "❌ Not configured",
                "lighthouse": "✅ Configured" if os.getenv("LIGHTHOUSE_API_KEY") else "❌ Not configured",
                "openai": "✅ Configured" if os.getenv("OPENAI_API_KEY") else "❌ Not configured"
            },
            "business_discovery": {
                "default_radius": business_config.DEFAULT_SEARCH_RADIUS_METERS,
                "max_results": business_config.MAX_SEARCH_RESULTS,
                "supported_niches": business_config.SUPPORTED_NICHES,
                "min_rating_threshold": business_config.MIN_RATING_THRESHOLD
            },
            "rate_limiting": {
                "google_places_per_minute": os.getenv("GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE"),
                "yelp_fusion_per_day": os.getenv("YELP_FUSION_RATE_LIMIT_PER_DAY"),
                "lighthouse_per_minute": os.getenv("LIGHTHOUSE_RATE_LIMIT_PER_MINUTE")
            },
            "fallback_system": {
                "enabled": True,
                "priority_order": ["lighthouse", "google_places", "yelp_fusion"],
                "timeouts": {
                    "lighthouse": 15,
                    "google_places": 10,
                    "yelp_fusion": 10
                }
            }
        }
    except Exception as e:
        return {"error": str(e)}
