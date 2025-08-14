"""
Business data merging and deduplication API endpoints.
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from src.schemas import MergeRequest, MergeResponse
from src.services import DataMergingService

router = APIRouter(prefix="/business-management", tags=["business-management"])


def get_data_merging_service() -> DataMergingService:
    return DataMergingService()


@router.post("/merge", response_model=MergeResponse)
async def merge_and_deduplicate(
    request: MergeRequest,
    service: DataMergingService = Depends(get_data_merging_service),
) -> MergeResponse:
    try:
        if not request.run_id:
            request.run_id = str(uuid.uuid4())
        if not service.validate_input(request):
            raise HTTPException(status_code=400, detail="Invalid merge request payload")
        return service.merge_and_deduplicate(request)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error during merge: {str(e)}")


@router.get("/merge/health")
async def merge_health(service: DataMergingService = Depends(get_data_merging_service)):
    try:
        if service and hasattr(service, "merge_and_deduplicate"):
            return {
                "status": "healthy",
                "service": "DataMergingService",
                "message": "Service is operational",
                "capabilities": [
                    "name_similarity",
                    "address_similarity",
                    "proximity_scoring",
                    "confidence_scoring",
                    "manual_review_flags",
                ],
            }
        else:
            return {
                "status": "unhealthy",
                "service": "DataMergingService",
                "message": "Service not properly initialized",
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "DataMergingService",
            "message": f"Service health check failed: {str(e)}",
        }