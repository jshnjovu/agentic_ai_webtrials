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
    HeuristicEvaluationError,
    ScoreValidationRequest,
    ScoreValidationResponse,
    RateLimitExceededError,
    FallbackScoringRequest,
    FallbackScoringResponse,
    FallbackScoringError,
    FallbackMonitoringResponse
)
from src.services.lighthouse_service import LighthouseService
from src.services.heuristic_evaluation_service import HeuristicEvaluationService
from src.services.score_validation_service import ScoreValidationService
from src.services.fallback_scoring_service import FallbackScoringService
from src.services.rate_limiter import RateLimiter
from src.models.website_scoring import WebsiteScore, LighthouseAuditResult
from src.utils.score_calculation import calculate_overall_score, get_score_insights

router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])


def get_lighthouse_service() -> LighthouseService:
    """Dependency to get Lighthouse service instance."""
    return LighthouseService()


def get_heuristic_evaluation_service() -> HeuristicEvaluationService:
    """Dependency to get HeuristicEvaluationService instance."""
    return HeuristicEvaluationService()


def get_score_validation_service() -> ScoreValidationService:
    """Dependency to get ScoreValidationService instance."""
    return ScoreValidationService()


def get_rate_limiter() -> RateLimiter:
    """Dependency to get RateLimiter instance."""
    return RateLimiter()


def get_fallback_scoring_service() -> FallbackScoringService:
    """Dependency to get FallbackScoringService instance."""
    return FallbackScoringService()


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


@router.post("/validate", response_model=ScoreValidationResponse)
async def validate_scores(
    request: ScoreValidationRequest,
    background_tasks: BackgroundTasks,
    service: ScoreValidationService = Depends(get_score_validation_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> ScoreValidationResponse:
    """
    Validate website scores and calculate confidence levels.
    
    Args:
        request: Score validation request with Lighthouse and heuristic scores
        background_tasks: FastAPI background tasks for async processing
        service: Score validation service instance
        rate_limiter: Rate limiter service instance
        
    Returns:
        Score validation response with confidence metrics and final scores
        
    Raises:
        HTTPException: If validation fails or rate limit is exceeded
    """
    try:
        # Check rate limiting for validation API
        can_proceed, message = rate_limiter.can_make_request("validation")
        if not can_proceed:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded for validation API",
                    "message": message,
                    "retry_after": 60
                }
            )
        
        # Generate run_id if not provided
        if not request.run_id:
            request.run_id = str(uuid.uuid4())
        
        # Validate request
        if not service.validate_input(request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Invalid score validation request"
            )
        
        # Execute validation
        validation_result = await service.validate_scores(
            lighthouse_scores=request.lighthouse_scores,
            heuristic_scores=request.heuristic_scores,
            business_id=request.business_id,
            run_id=request.run_id
        )
        
        # Record successful request
        rate_limiter.record_request("validation", True, request.run_id)
        
        # Return successful response
        return ScoreValidationResponse(
            success=True,
            business_id=request.business_id,
            run_id=request.run_id,
            validation_result=validation_result,
            final_score=FinalScore(
                business_id=request.business_id,
                run_id=request.run_id,
                weighted_final_score=validation_result.final_weighted_score,
                confidence_level=validation_result.confidence_level,
                lighthouse_weight=0.8,
                heuristic_weight=0.2,
                discrepancy_flags=[],
                issue_priorities=validation_result.issue_priorities,
                validation_status=validation_result.validation_status,
                calculation_timestamp=time.time()
            ),
            validation_timestamp=time.time()
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Record failed request
        rate_limiter.record_request("validation", False, request.run_id)
        
        # Return error response
        raise HTTPException(
            status_code=500,
            detail=f"Score validation failed: {str(e)}"
        )


@router.post("/fallback", response_model=FallbackScoringResponse)
async def run_fallback_scoring(
    request: FallbackScoringRequest,
    background_tasks: BackgroundTasks,
    service: FallbackScoringService = Depends(get_fallback_scoring_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> FallbackScoringResponse:
    """
    Run fallback scoring when Lighthouse fails.
    
    Args:
        request: Fallback scoring request with website URL and failure reason
        background_tasks: FastAPI background tasks for async processing
        service: Fallback scoring service instance
        rate_limiter: Rate limiter instance
        
    Returns:
        Fallback scoring response with heuristic-only scores and confidence indicators
        
    Raises:
        HTTPException: If fallback scoring fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not request.run_id:
            request.run_id = str(uuid.uuid4())
        
        # Check rate limiting
        can_make_request, message = rate_limiter.can_make_request("fallback", request.business_id)
        if not can_make_request:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded: {message}"
            )
        
        # Execute fallback scoring
        fallback_result = service.run_fallback_scoring(
            website_url=str(request.website_url),
            business_id=request.business_id,
            lighthouse_failure_reason=request.lighthouse_failure_reason,
            run_id=request.run_id,
            fallback_parameters=request.fallback_parameters
        )
        
        # Handle error responses
        if not fallback_result.get("success", False):
            error_response = FallbackScoringError(
                success=False,
                error=fallback_result.get("error", "Unknown error occurred"),
                error_code=fallback_result.get("error_code", "UNKNOWN_ERROR"),
                context=fallback_result.get("context", "fallback_scoring"),
                website_url=str(request.website_url),
                business_id=request.business_id,
                run_id=request.run_id,
                fallback_timestamp=time.time()
            )
            raise HTTPException(
                status_code=400,
                detail=error_response.dict()
            )
        
        # Add background task for data persistence
        background_tasks.add_task(
            _persist_fallback_results,
            fallback_result,
            request.business_id,
            request.run_id
        )
        
        # Record successful request
        rate_limiter.record_request("fallback", True, request.run_id)
        
        # Return success response
        return FallbackScoringResponse(
            success=True,
            business_id=request.business_id,
            run_id=request.run_id,
            fallback_score=fallback_result.get("fallback_score"),
            error=None,
            error_code=None,
            fallback_timestamp=fallback_result.get("fallback_timestamp", time.time())
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Record failed request
        rate_limiter.record_request("fallback", False, request.run_id)
        
        # Return error response
        error_response = FallbackScoringError(
            success=False,
            error=str(e),
            error_code="INTERNAL_ERROR",
            context="fallback_scoring",
            website_url=str(request.website_url),
            business_id=request.business_id,
            run_id=request.run_id,
            fallback_timestamp=time.time()
        )
        
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )


@router.get("/fallback/monitoring", response_model=FallbackMonitoringResponse)
async def get_fallback_monitoring(
    business_id: str,
    run_id: Optional[str] = None,
    service: FallbackScoringService = Depends(get_fallback_scoring_service)
) -> FallbackMonitoringResponse:
    """
    Get fallback scoring monitoring and metrics.
    
    Args:
        business_id: Business identifier
        run_id: Optional run identifier for specific run
        service: Fallback scoring service instance
        
    Returns:
        Fallback monitoring response with metrics and performance data
        
    Raises:
        HTTPException: If monitoring data cannot be retrieved
    """
    try:
        # Get fallback metrics
        metrics = service.get_fallback_metrics()
        
        return FallbackMonitoringResponse(
            success=True,
            business_id=business_id,
            run_id=run_id or "monitoring",
            fallback_metrics=metrics,
            monitoring_timestamp=time.time()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve fallback monitoring data: {str(e)}"
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


async def _persist_fallback_results(
    fallback_result: dict,
    business_id: str,
    run_id: str
) -> None:
    """
    Background task to persist fallback scoring results to database.
    
    Args:
        fallback_result: Fallback scoring result data
        business_id: Business identifier
        run_id: Run identifier
    """
    try:
        # This would typically save to database using the models
        # For now, just log the persistence attempt
        print(f"Would persist fallback scoring results for business {business_id}, run {run_id}")
        
        # Example of what would be saved:
        # fallback_score = FallbackScore.from_schema_data(fallback_result)
        # database.session.add(fallback_score)
        # database.session.commit()
        
    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to persist fallback scoring results: {str(e)}")
