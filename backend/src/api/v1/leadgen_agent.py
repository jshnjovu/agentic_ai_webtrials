from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import uuid
from src.services import LeadGenAIAgent

router = APIRouter(prefix="/leadgen-agent", tags=["leadgen-agent"])


def get_leadgen_agent_service() -> LeadGenAIAgent:
    """Dependency to get leadgen AI agent service instance."""
    return LeadGenAIAgent()


@router.post("/discover-businesses")
async def discover_businesses(
    location: str = Query(
        ..., description="Location to search in (e.g., city, address, ZIP code)"
    ),
    niche: str = Query(..., description="Business niche or category to search for"),
    max_results: int = Query(
        default=10, description="Maximum number of businesses to discover"
    ),
    run_id: Optional[str] = Query(
        None, description="Unique identifier for the processing run"
    ),
    service: LeadGenAIAgent = Depends(get_leadgen_agent_service),
):
    """
    Discover businesses based on location and niche, using multiple sources.

    Args:
        location: Location to search in
        niche: Business niche or category
        max_results: Maximum number of results to return
        run_id: Optional run identifier for the processing run
        service: Leadgen AI agent service instance

    Returns:
        A combined list of discovered businesses from all available sources.
    """
    try:
        # Generate run_id if not provided
        if not run_id:
            run_id = str(uuid.uuid4())

        # Discover businesses using the leadgen agent service
        discovery_result = await service.discover_businesses(
            location=location, niche=niche, max_results=max_results, run_id=run_id
        )

        # Handle errors during discovery
        if not discovery_result["success"]:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "Business discovery failed",
                    "details": discovery_result.get("error_details", "Unknown error"),
                },
            )

        # Return the combined results
        return {
            "success": True,
            "run_id": run_id,
            "location": location,
            "niche": niche,
            "total_discovered": len(discovery_result["results"]),
            "results": discovery_result["results"],
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during business discovery: {str(e)}",
        )
