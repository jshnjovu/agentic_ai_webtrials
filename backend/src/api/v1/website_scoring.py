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
    ConfidenceLevel,
    HeuristicEvaluationRequest,
    HeuristicEvaluationResponse,
    HeuristicEvaluationError
)
from src.services.lighthouse_service import LighthouseService
from src.services.heuristic_evaluation_service import HeuristicEvaluationService
from src.models.website_scoring import WebsiteScore, LighthouseAuditResult
from src.utils.score_calculation import calculate_overall_score, get_score_insights

router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])


def get_lighthouse_service() -> LighthouseService:
    """Dependency to get Lighthouse service instance."""
    return LighthouseService()


def get_heuristic_evaluation_service() -> HeuristicEvaluationService:
    """Dependency to get HeuristicEvaluationService instance."""
    return HeuristicEvaluationService()


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


@router.post("/heuristics", response_model=HeuristicEvaluationResponse)
async def run_heuristic_evaluation(
    request: HeuristicEvaluationRequest,
    background_tasks: BackgroundTasks,
    service: HeuristicEvaluationService = Depends(get_heuristic_evaluation_service)
) -> HeuristicEvaluationResponse:
    """
    Run heuristic evaluation for website trust signals, CRO elements, and usability.
    
    Args:
        request: Heuristic evaluation request with website URL and parameters
        background_tasks: FastAPI background tasks for async processing
        service: Heuristic evaluation service instance
        
    Returns:
        Heuristic evaluation response with scores and detailed breakdown
        
    Raises:
        HTTPException: If evaluation fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not request.run_id:
            request.run_id = str(uuid.uuid4())
        
        # Validate request
        if not service.validate_input(request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Invalid heuristic evaluation request"
            )
        
        # Execute evaluation
        evaluation_result = service.run_heuristic_evaluation(
            website_url=str(request.website_url),
            business_id=request.business_id,
            run_id=request.run_id
        )
        
        # Handle error responses
        if not evaluation_result.get("success", False):
            error_response = HeuristicEvaluationError(
                success=False,
                error=evaluation_result.get("error", "Unknown error occurred"),
                context=evaluation_result.get("context", "evaluation_execution"),
                website_url=str(request.website_url),
                business_id=request.business_id,
                run_id=request.run_id,
                evaluation_timestamp=time.time(),
                error_code=evaluation_result.get("error_code"),
                scores={
                    'trust_score': 0.0,
                    'cro_score': 0.0,
                    'mobile_score': 0.0,
                    'content_score': 0.0,
                    'social_score': 0.0,
                    'overall_heuristic_score': 0.0,
                    'confidence_level': ConfidenceLevel.LOW
                },
                trust_signals={},
                cro_elements={},
                mobile_usability={},
                content_quality={},
                social_proof={},
                confidence=ConfidenceLevel.LOW
            )
            
            # Return error response with appropriate HTTP status
            if evaluation_result.get("error_code") == "TIMEOUT":
                raise HTTPException(
                    status_code=408,
                    detail={
                        "error": "Heuristic evaluation timed out",
                        "error_code": "TIMEOUT",
                        "context": "evaluation_execution",
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
            elif evaluation_result.get("error_code") == "RATE_LIMIT_EXCEEDED":
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded for heuristic evaluation",
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
                        "error": evaluation_result.get("error", "Evaluation failed"),
                        "error_code": evaluation_result.get("error_code"),
                        "context": evaluation_result.get("context", "evaluation_execution"),
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
        
        # Create successful response
        response = HeuristicEvaluationResponse(
            success=True,
            website_url=str(request.website_url),
            business_id=request.business_id,
            run_id=request.run_id,
            evaluation_timestamp=evaluation_result.get("evaluation_timestamp", time.time()),
            scores=evaluation_result.get("scores"),
            trust_signals=evaluation_result.get("trust_signals"),
            cro_elements=evaluation_result.get("cro_elements"),
            mobile_usability=evaluation_result.get("mobile_usability"),
            content_quality=evaluation_result.get("content_quality"),
            social_proof=evaluation_result.get("social_proof"),
            confidence=ConfidenceLevel(evaluation_result.get("confidence", "low")),
            raw_data=evaluation_result.get("raw_data")
        )
        
        # Add background task for data persistence (if database is configured)
        background_tasks.add_task(
            _persist_heuristic_results,
            evaluation_result,
            request.business_id,
            request.run_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during heuristic evaluation: {str(e)}"
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


@router.get("/health")
async def website_scoring_health_check(
    lighthouse_service: LighthouseService = Depends(get_lighthouse_service),
    heuristic_service: HeuristicEvaluationService = Depends(get_heuristic_evaluation_service)
) -> dict:
    """
    Health check endpoint for website scoring services.
    
    Returns:
        Health status of the website scoring services
    """
    try:
        # Basic health check - verify services can be instantiated
        return {
            "status": "healthy",
            "service": "Website Scoring API",
            "timestamp": time.time(),
            "features": [
                "lighthouse_auditing",
                "performance_scoring",
                "accessibility_evaluation",
                "seo_analysis",
                "best_practices_assessment",
                "heuristic_evaluation",
                "trust_signal_detection",
                "cro_element_identification",
                "mobile_usability_assessment",
                "content_quality_evaluation",
                "social_proof_detection"
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Website scoring services unhealthy: {str(e)}"
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


async def _persist_heuristic_results(
    evaluation_result: dict,
    business_id: str,
    run_id: str
) -> None:
    """
    Background task to persist heuristic evaluation results to database.
    
    Args:
        evaluation_result: Heuristic evaluation result data
        business_id: Business identifier
        run_id: Run identifier
    """
    try:
        # This would typically save to database using the models
        # For now, just log the persistence attempt
        print(f"Would persist heuristic evaluation results for business {business_id}, run {run_id}")
        
        # Example of what would be saved:
        # heuristic_score = HeuristicScore.from_schema_data(evaluation_result)
        # evaluation_result_model = HeuristicEvaluationResult.from_schema_data(evaluation_result)
        # database.session.add(heuristic_score)
        # database.session.add(evaluation_result_model)
        # database.session.commit()
        
    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to persist heuristic evaluation results: {str(e)}")
