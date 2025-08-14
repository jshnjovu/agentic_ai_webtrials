"""
Website scoring API endpoints for Lighthouse integration.
Provides endpoints for triggering website performance audits.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
import uuid
import time
from datetime import datetime

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
    FallbackScoringRequest,
    FallbackScoringResponse,
    FallbackScoringError,
    FallbackMonitoringResponse,
    FallbackScore,
    ScoreValidationRequest,
    ScoreValidationResponse,
    ScoreValidationError
)
from src.services.lighthouse_service import LighthouseService
from src.services.heuristic_evaluation_service import HeuristicEvaluationService
from src.services.fallback_scoring_service import FallbackScoringService
from src.services.score_validation_service import ScoreValidationService
from src.models.website_scoring import WebsiteScore, LighthouseAuditResult
from src.utils.score_calculation import calculate_overall_score, get_score_insights
from src.services.rate_limiter import RateLimiter

router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])


class RateLimitExceededError(Exception):
    """Custom exception for rate limit exceeded."""
    pass


def get_lighthouse_service() -> LighthouseService:
    """Dependency to get Lighthouse service instance."""
    return LighthouseService()


def get_heuristic_evaluation_service() -> HeuristicEvaluationService:
    """Dependency to get HeuristicEvaluationService instance."""
    return HeuristicEvaluationService()


def get_fallback_scoring_service() -> FallbackScoringService:
    """Dependency to get FallbackScoringService instance."""
    return FallbackScoringService()


def get_score_validation_service() -> ScoreValidationService:
    """Dependency to get ScoreValidationService instance."""
    return ScoreValidationService()


def get_rate_limiter() -> RateLimiter:
    """Dependency to get RateLimiter instance."""
    return RateLimiter()


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


@router.post("/fallback", response_model=FallbackScoringResponse)
async def run_fallback_scoring(
    request: FallbackScoringRequest,
    background_tasks: BackgroundTasks,
    service: FallbackScoringService = Depends(get_fallback_scoring_service)
) -> FallbackScoringResponse:
    """
    Run fallback scoring when Lighthouse fails.
    
    Args:
        request: Fallback scoring request with website URL and failure reason
        background_tasks: FastAPI background tasks for async processing
        service: Fallback scoring service instance
        
    Returns:
        Fallback scoring response with heuristic-only scores and quality assessment
        
    Raises:
        HTTPException: If fallback scoring fails or validation errors occur
    """
    try:
        # Generate run_id if not provided
        if not request.run_id:
            request.run_id = str(uuid.uuid4())
        
        # Validate request
        if not service.validate_input(request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Invalid fallback scoring request"
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
                context=fallback_result.get("context", "fallback_execution"),
                website_url=str(request.website_url),
                business_id=request.business_id,
                run_id=request.run_id,
                fallback_timestamp=time.time(),
                error_code=fallback_result.get("error_code"),
                fallback_score=FallbackScore(
                    trust_score=0.0,
                    cro_score=0.0,
                    mobile_score=0.0,
                    content_score=0.0,
                    social_score=0.0,
                    overall_score=0.0,
                    confidence_level=ConfidenceLevel.LOW,
                    fallback_reason=request.lighthouse_failure_reason,
                    fallback_timestamp=time.time()
                ),
                fallback_reason={
                    'failure_type': 'UNKNOWN_ERROR',
                    'error_message': fallback_result.get("error", "Unknown error"),
                    'severity_level': 'medium',
                    'fallback_decision': 'immediate_fallback',
                    'retry_attempts': 0,
                    'success_status': False,
                    'fallback_timestamp': time.time()
                },
                fallback_quality={
                    'reliability_score': 0.0,
                    'data_completeness': 0.0,
                    'confidence_adjustment': 0.0,
                    'quality_indicators': {},
                    'recommendation': 'Unable to assess quality due to error'
                }
            )
            
            # Return error response with appropriate HTTP status
            if fallback_result.get("error_code") == "RATE_LIMIT_EXCEEDED":
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded for fallback scoring",
                        "error_code": "RATE_LIMIT_EXCEEDED",
                        "context": "rate_limit_check",
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
            elif fallback_result.get("context") == "fallback_strategy":
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": "Fallback not recommended for this failure type",
                        "error_code": "FALLBACK_NOT_RECOMMENDED",
                        "context": "fallback_strategy",
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": fallback_result.get("error", "Fallback scoring failed"),
                        "error_code": fallback_result.get("error_code"),
                        "context": fallback_result.get("context", "fallback_execution"),
                        "website_url": str(request.website_url),
                        "business_id": request.business_id,
                        "run_id": request.run_id
                    }
                )
        
        # Create successful response
        response = FallbackScoringResponse(
            success=True,
            website_url=str(request.website_url),
            business_id=request.business_id,
            run_id=request.run_id,
            fallback_timestamp=fallback_result.get("fallback_timestamp", time.time()),
            fallback_score=fallback_result.get("fallback_score"),
            fallback_reason=fallback_result.get("fallback_reason"),
            fallback_quality=fallback_result.get("fallback_quality"),
            retry_attempts=fallback_result.get("retry_attempts", 0)
        )
        
        # Add background task for data persistence (if database is configured)
        background_tasks.add_task(
            _persist_fallback_results,
            fallback_result,
            request.business_id,
            request.run_id
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during fallback scoring: {str(e)}"
        )


@router.get("/fallback/monitoring", response_model=FallbackMonitoringResponse)
async def get_fallback_monitoring(
    service: FallbackScoringService = Depends(get_fallback_scoring_service)
) -> FallbackMonitoringResponse:
    """
    Get fallback scoring monitoring and analytics data.
    
    Args:
        service: Fallback scoring service instance
        
    Returns:
        Fallback monitoring response with metrics and recommendations
    """
    try:
        # Get fallback metrics
        metrics = service.get_fallback_metrics()
        
        # Create monitoring response
        monitoring_response = FallbackMonitoringResponse(
            success=True,
            timestamp=time.time(),
            metrics=metrics,
            recent_fallbacks=[],  # This would typically query the database
            failure_patterns={},   # This would typically analyze historical data
            recommendations=[
                "Monitor timeout failures for potential performance improvements",
                "Consider implementing circuit breaker for high-severity failures",
                "Track fallback success rates to optimize heuristic algorithms"
            ]
        )
        
        return monitoring_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving fallback monitoring: {str(e)}"
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
async def validate_website_scores(
    request: ScoreValidationRequest,
    score_validation_service: ScoreValidationService = Depends(get_score_validation_service),
    rate_limiter: RateLimiter = Depends(get_rate_limiter)
) -> ScoreValidationResponse:
    """
    Validate website scores and calculate confidence levels.
    
    This endpoint performs cross-validation between Lighthouse and heuristic scoring methods,
    calculates confidence levels, detects discrepancies, and provides weighted final scores.
    
    Args:
        request: Score validation request with business_id, run_id, and scoring data
        score_validation_service: Service for score validation and confidence calculation
        rate_limiter: Rate limiting service for API protection
        
    Returns:
        ScoreValidationResponse with validation results, confidence metrics, and issue priorities
        
    Raises:
        HTTPException: For validation errors, rate limiting violations, or service failures
    """
    start_time = time.time()
    
    try:
        # Rate limiting check
        can_request, reason = rate_limiter.can_make_request("validation")
        if not can_request:
            raise RateLimitExceededError(f"Rate limit exceeded: {reason}")
        
        # Validate scores using the service
        validation_result = await score_validation_service.validate_scores(
            lighthouse_scores=request.lighthouse_scores,
            heuristic_scores=request.heuristic_scores,
            business_id=request.business_id,
            run_id=request.run_id
        )
        
        # Record successful request
        rate_limiter.record_request("validation", True)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create response
        response = ScoreValidationResponse(
            success=True,
            validation_result=validation_result,
            processing_time=processing_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Background task to persist validation results
        BackgroundTasks().add_task(
            _persist_validation_results,
            validation_result.model_dump(),
            request.business_id,
            request.run_id
        )
        
        return response
        
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during score validation: {str(e)}"
        )


@router.get("/health")
async def website_scoring_health_check(
    lighthouse_service: LighthouseService = Depends(get_lighthouse_service),
    heuristic_service: HeuristicEvaluationService = Depends(get_heuristic_evaluation_service),
    fallback_service: FallbackScoringService = Depends(get_fallback_scoring_service),
    score_validation_service: ScoreValidationService = Depends(get_score_validation_service)
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
                "social_proof_detection",
                "fallback_scoring",
                "automatic_fallback_detection",
                "retry_logic_with_exponential_backoff",
                "fallback_quality_assessment",
                "fallback_monitoring_and_analytics",
                "score_validation_and_confidence",
                "cross_validation_between_methods",
                "confidence_level_calculation",
                "discrepancy_detection",
                "weighted_final_score_calculation",
                "issue_prioritization_ranking"
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
    Background task to persist fallback results to database.
    
    Args:
        fallback_result: Fallback result data
        business_id: Business identifier
        run_id: Run identifier
    """
    try:
        # This would typically save to database using the models
        # For now, just log the persistence attempt
        print(f"Would persist fallback results for business {business_id}, run {run_id}")
        
        # Example of what would be saved:
        # fallback_score = FallbackScore.from_schema_data(fallback_result)
        # fallback_reason = FallbackReason.from_schema_data(fallback_result)
        # fallback_quality = FallbackQuality.from_schema_data(fallback_result)
        # database.session.add(fallback_score)
        # database.session.add(fallback_reason)
        # database.session.add(fallback_quality)
        # database.session.commit()
        
    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to persist fallback results: {str(e)}")


async def _persist_validation_results(
    validation_result: dict,
    business_id: str,
    run_id: str
) -> None:
    """
    Background task to persist validation results to database.
    
    Args:
        validation_result: Validation result data
        business_id: Business identifier
        run_id: Run identifier
    """
    try:
        # This would typically save to database using the models
        # For now, just log the persistence attempt
        print(f"Would persist validation results for business {business_id}, run {run_id}")
        
        # Example of what would be saved:
        # score_validation_result = ScoreValidationResult.from_schema_data(validation_result)
        # validation_metrics = ValidationMetrics.from_schema_data(validation_result.get('validation_metrics', {}))
        # final_score = FinalScore.from_schema_data(validation_result.get('final_score', {}))
        # 
        # # Save main validation result
        # database.session.add(score_validation_result)
        # database.session.commit()
        # 
        # # Save related metrics and scores
        # validation_metrics.validation_result_id = score_validation_result.id
        # final_score.validation_result_id = score_validation_result.id
        # database.session.add(validation_metrics)
        # database.session.add(final_score)
        # 
        # # Save issue priorities
        # for issue_data in validation_result.get('issue_priorities', []):
        #     issue_priority = IssuePriority.from_schema_data(issue_data)
        #     issue_priority.validation_result_id = score_validation_result.id
        #     database.session.add(issue_priority)
        # 
        # database.session.commit()
        
    except Exception as e:
        # Log error but don't fail the main request
        print(f"Failed to persist validation results: {str(e)}")
