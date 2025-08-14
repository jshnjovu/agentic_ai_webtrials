"""
Website scoring API endpoints for Lighthouse integration.
Provides endpoints for triggering website performance audits.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
import uuid
import time

from src.schemas.website_scoring import (
    LighthouseAuditRequest,
    LighthouseAuditResponse,
    LighthouseAuditError,
    WebsiteScoringSummary,
    AuditStrategy,
    ConfidenceLevel
)
from src.services.lighthouse_service import LighthouseService
from src.models.website_scoring import WebsiteScore, LighthouseAuditResult
from src.utils.score_calculation import calculate_overall_score, get_score_insights

router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])


def get_lighthouse_service() -> LighthouseService:
    """Dependency to get Lighthouse service instance."""
    return LighthouseService()


@router.post("/lighthouse", response_model=LighthouseAuditResponse)
async def run_lighthouse_audit(
    request: LighthouseAuditRequest,
    background_tasks: BackgroundTasks,
    service: LighthouseService = Depends(get_lighthouse_service)
) -> LighthouseAuditResponse:
    """
    Run a Lighthouse audit for website performance evaluation.
    
    Args:
        request: Lighthouse audit request with website URL and parameters
        background_tasks: FastAPI background tasks for async processing
        service: Lighthouse service instance
        
    Returns:
        Lighthouse audit response with performance scores and metrics
        
    Raises:
        HTTPException: If audit fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not request.run_id:
            request.run_id = str(uuid.uuid4())
        
        # Validate request
        if not service.validate_input(request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Invalid Lighthouse audit request"
            )
        
        # Execute audit
        audit_result = service.run_lighthouse_audit(
            website_url=str(request.website_url),
            business_id=request.business_id,
            run_id=request.run_id,
            strategy=request.strategy.value
        )
        
        # Handle error responses
        if not audit_result.get("success", False):
            error_response = LighthouseAuditError(
                success=False,
                error=audit_result.get("error", "Unknown error occurred"),
                context=audit_result.get("context", "audit_execution"),
                website_url=str(request.website_url),
                business_id=request.business_id,
                run_id=request.run_id,
                audit_timestamp=time.time(),
                error_code=audit_result.get("error_code"),
                scores={
                    'performance': 0.0,
                    'accessibility': 0.0,
                    'best_practices': 0.0,
                    'seo': 0.0,
                    'overall': 0.0
                },
                core_web_vitals={},
                confidence=ConfidenceLevel.LOW,
                strategy=request.strategy.value
            )
            
            # Return error response with appropriate HTTP status
            if audit_result.get("error_code") == "TIMEOUT":
                raise HTTPException(
                    status_code=408,
                    detail={
                        "error": "Lighthouse audit timed out",
                        "error_code": "TIMEOUT",
                        "context": "audit_execution",
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
            elif audit_result.get("error_code") == "RATE_LIMIT_EXCEEDED":
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded for Lighthouse API",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "context": "rate_limit_check",
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": audit_result.get("error", "Audit failed"),
                        "error_code": audit_result.get("error_code"),
                        "context": audit_result.get("context", "audit_execution"),
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
        
        # Create successful response
        response = LighthouseAuditResponse(
            success=True,
            website_url=str(request.website_url),
            business_id=request.business_id,
            run_id=request.run_id,
            audit_timestamp=audit_result.get("audit_timestamp", time.time()),
            strategy=audit_result.get("strategy", request.strategy.value),
            scores={
                'performance': audit_result.get("scores", {}).get("performance", 0.0),
                'accessibility': audit_result.get("scores", {}).get("accessibility", 0.0),
                'best_practices': audit_result.get("scores", {}).get("best_practices", 0.0),
                'seo': audit_result.get("scores", {}).get("seo", 0.0),
                'overall': audit_result.get("overall_score", 0.0)
            },
            core_web_vitals=audit_result.get("core_web_vitals", {}),
            confidence=ConfidenceLevel(audit_result.get("confidence", "low")),
            raw_data=audit_result.get("raw_data")
        )
        
        # Add background task for data persistence (if database is configured)
        background_tasks.add_task(
            _persist_audit_results,
            audit_result,
            request.business_id,
            request.run_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during Lighthouse audit: {str(e)}"
        )


@router.get("/lighthouse/{business_id}/summary", response_model=WebsiteScoringSummary)
async def get_website_scoring_summary(
    business_id: str,
    limit: Optional[int] = 10,
    service: LighthouseService = Depends(get_lighthouse_service)
) -> WebsiteScoringSummary:
    """
    Get website scoring summary for a business.
    
    Args:
        business_id: Business identifier
        limit: Maximum number of audit results to include
        service: Lighthouse service instance
        
    Returns:
        Website scoring summary with audit history and statistics
    """
    try:
        # This would typically query the database for historical results
        # For now, return a placeholder response
        summary = WebsiteScoringSummary(
            business_id=business_id,
            total_audits=0,
            successful_audits=0,
            failed_audits=0,
            average_scores={
                'performance': 0.0,
                'accessibility': 0.0,
                'best_practices': 0.0,
                'seo': 0.0,
                'overall': 0.0
            },
            audit_history=[]
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving scoring summary: {str(e)}"
        )


@router.get("/lighthouse/health")
async def lighthouse_health_check(
    service: LighthouseService = Depends(get_lighthouse_service)
) -> dict:
    """
    Health check endpoint for Lighthouse service.
    
    Returns:
        Health status of the Lighthouse service
    """
    try:
        # Basic health check - verify service can be instantiated
        return {
            "status": "healthy",
            "service": "Lighthouse API",
            "timestamp": time.time(),
            "features": [
                "website_auditing",
                "performance_scoring",
                "accessibility_evaluation",
                "seo_analysis",
                "best_practices_assessment"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Lighthouse service unhealthy: {str(e)}"
        )


async def _persist_audit_results(
    audit_result: dict,
    business_id: str,
    run_id: str
) -> None:
    """
    Background task to persist audit results to database.
    
    Args:
        audit_result: Audit result data
        business_id: Business identifier
        run_id: Run identifier
    """
    try:
        # This would typically save to database using the models
        # For now, just log the persistence attempt
        print(f"Would persist audit results for business {business_id}, run {run_id}")
        
        # Example of what would be saved:
        # website_score = WebsiteScore.from_schema_data(audit_result)
        # audit_result_model = LighthouseAuditResult.from_schema_data(audit_result)
        # database.session.add(website_score)
        # database.session.add(audit_result_model)
        # database.session.commit()
        
    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to persist audit results: {str(e)}")
