"""
Website scoring API endpoints for comprehensive speed analysis using PageSpeed and Pingdom.
Provides endpoints for website analysis using Google PageSpeed API and comprehensive speed evaluation.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from datetime import datetime
import uuid
import time

from src.schemas.website_scoring import (
    WebsiteScoringSummary,
    AuditStrategy,
    ConfidenceLevel,
    ScoreValidationRequest,
    ScoreValidationResponse,
    RateLimitExceededError,
    FallbackScoringRequest,
    FallbackScoringResponse,
    FallbackScoringError,
    FallbackMonitoringResponse,
    PageSpeedAuditRequest,
    PageSpeedAuditResponse,
    PageSpeedAuditError
)
from src.services.comprehensive_speed_service import ComprehensiveSpeedService
from src.services.score_validation_service import ScoreValidationService
from src.services.fallback_scoring_service import FallbackScoringService
from src.services.google_pagespeed_service import GooglePageSpeedService
from src.services.rate_limiter import RateLimiter
from src.models.website_scoring import WebsiteScore
from src.utils.score_calculation import calculate_overall_score, get_score_insights

router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])


def get_comprehensive_speed_service() -> ComprehensiveSpeedService:
    """Dependency to get ComprehensiveSpeedService instance."""
    return ComprehensiveSpeedService()


def get_score_validation_service() -> ScoreValidationService:
    """Dependency to get ScoreValidationService instance."""
    return ScoreValidationService()


def get_rate_limiter() -> RateLimiter:
    """Dependency to get RateLimiter instance."""
    return RateLimiter()


def get_fallback_scoring_service() -> FallbackScoringService:
    """Dependency to get FallbackScoringService instance."""
    return FallbackScoringService()


def get_pagespeed_service() -> GooglePageSpeedService:
    """Dependency to get GooglePageSpeedService instance."""
    return GooglePageSpeedService()


@router.post("/pagespeed", response_model=PageSpeedAuditResponse)
async def run_pagespeed_audit(
    request: PageSpeedAuditRequest,
    service: GooglePageSpeedService = Depends(get_pagespeed_service)
) -> PageSpeedAuditResponse:
    """
    Run a PageSpeed audit using Google PageSpeed Insights API.
    
    Args:
        request: PageSpeed audit request with website URL and parameters
        service: PageSpeed service instance
        
    Returns:
        PageSpeed audit response with analysis scores and metrics
    """
    try:
        # Validate request
        if not service.validate_input(request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Invalid PageSpeed audit request"
            )
        
        # Run PageSpeed audit
        audit_result = await service.run_pagespeed_audit(
            website_url=request.website_url,
            business_id=request.business_id,
            run_id=request.run_id,
            strategy=request.strategy,
            categories=request.categories
        )
        
        if not audit_result.get("success", False):
            error_response = PageSpeedAuditError(
                success=False,
                error=audit_result.get("error", "Unknown error"),
                error_code=audit_result.get("error_code", "AUDIT_FAILED"),
                context=audit_result.get("context", "pagespeed_audit"),
                run_id=request.run_id,
                business_id=request.business_id
            )
            raise HTTPException(
                status_code=500,
                detail=error_response.dict()
            )
        
        # Convert to response model
        response = PageSpeedAuditResponse(
            success=True,
            website_url=audit_result["website_url"],
            business_id=audit_result["business_id"],
            run_id=audit_result["run_id"],
            audit_timestamp=audit_result["audit_timestamp"],
            strategy=audit_result["strategy"],
            scores=audit_result["scores"],
            core_web_vitals=audit_result["core_web_vitals"],
            raw_data=audit_result.get("raw_data", {})
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during PageSpeed audit: {str(e)}"
        )


@router.post("/pagespeed/batch")
async def run_batch_pagespeed_audits(
    requests: List[PageSpeedAuditRequest],
    service: GooglePageSpeedService = Depends(get_pagespeed_service)
):
    """
    Run multiple PageSpeed audits concurrently.
    
    Args:
        requests: List of PageSpeed audit requests
        service: PageSpeed service instance
        
    Returns:
        List of PageSpeed audit responses
    """
    try:
        # Convert requests to the format expected by batch method
        audit_requests = [
            {
                'website_url': req.website_url,
                'business_id': req.business_id,
                'run_id': req.run_id,
                'strategy': req.strategy,
                'categories': req.categories
            }
            for req in requests
        ]
        
        # Run batch audits
        results = await service.run_batch_pagespeed_audits(audit_requests)
        
        return {
            "success": True,
            "total_requests": len(requests),
            "successful_audits": sum(1 for r in results if r.get("success", False)),
            "failed_audits": sum(1 for r in results if not r.get("success", False)),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch PageSpeed audit: {str(e)}"
        )


@router.get("/pagespeed/{business_id}/summary", response_model=WebsiteScoringSummary)
async def get_pagespeed_summary(
    business_id: str,
    service: GooglePageSpeedService = Depends(get_pagespeed_service)
) -> WebsiteScoringSummary:
    """
    Get PageSpeed audit summary for a business.
    
    Args:
        business_id: Business identifier
        service: PageSpeed service instance
        
    Returns:
        Website scoring summary with PageSpeed results
    """
    try:
        # Get PageSpeed audit history
        audit_history = service.get_audit_history(business_id)
        
        if not audit_history:
            raise HTTPException(
                status_code=404,
                detail=f"No PageSpeed audits found for business: {business_id}"
            )
        
        # Calculate summary statistics
        total_audits = len(audit_history)
        successful_audits = sum(1 for audit in audit_history if audit.get("success", False))
        average_score = sum(audit.get("scores", {}).get("overall", 0) for audit in audit_history) / total_audits
        
        summary = WebsiteScoringSummary(
            business_id=business_id,
            total_evaluations=total_audits,
            successful_evaluations=successful_audits,
            average_score=average_score,
            last_evaluation=audit_history[-1] if audit_history else None,
            evaluation_history=audit_history
        )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error getting PageSpeed summary: {str(e)}"
        )


@router.get("/pagespeed/health")
async def pagespeed_health_check(
    service: GooglePageSpeedService = Depends(get_pagespeed_service)
):
    """Health check endpoint for PageSpeed service."""
    health_data = service.get_service_health()
    return {
        "status": "healthy",
        "service": "pagespeed",
        "timestamp": time.time(),
        "version": "2.0.0",
        "health_data": health_data
    }


@router.post("/comprehensive", response_model=dict)
async def run_comprehensive_analysis(
    request: dict,
    service: ComprehensiveSpeedService = Depends(get_comprehensive_speed_service)
) -> dict:
    """
    Run comprehensive website analysis combining PageSpeed and Pingdom data.
    
    Args:
        request: Comprehensive analysis request with website URL and parameters
        service: Comprehensive speed service instance
        
    Returns:
        Comprehensive analysis response with all scores and metrics
    """
    try:
        # Validate request
        if not service.validate_input(request):
            raise HTTPException(
                status_code=400,
                detail="Invalid comprehensive analysis request"
            )
        
        # Run comprehensive analysis
        analysis_result = await service.run_comprehensive_analysis(
            website_url=request["website_url"],
            business_id=request["business_id"],
            run_id=request.get("run_id"),
            strategy=request.get("strategy", "mobile"),
            include_pingdom=request.get("include_pingdom", True)
        )
        
        if not analysis_result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": analysis_result.get("error", "Unknown error"),
                    "error_code": analysis_result.get("error_code", "ANALYSIS_FAILED"),
                    "context": analysis_result.get("context", "comprehensive_analysis")
                }
            )
        
        return analysis_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during comprehensive analysis: {str(e)}"
        )


@router.post("/hybrid", response_model=dict)
async def run_hybrid_audit(
    request: dict,
    service: ComprehensiveSpeedService = Depends(get_comprehensive_speed_service)
) -> dict:
    """
    Run hybrid audit combining PageSpeed and Pingdom data.
    
    Args:
        request: Hybrid audit request with website URL and parameters
        service: Comprehensive speed service instance
        
    Returns:
        Hybrid audit response with combined scores
    """
    try:
        # Validate request
        if not service.validate_input(request):
            raise HTTPException(
                status_code=400,
                detail="Invalid hybrid audit request"
            )
        
        # Run hybrid audit
        audit_result = await service.run_hybrid_audit(
            website_url=request["website_url"],
            business_id=request["business_id"],
            run_id=request.get("run_id"),
            strategy=request.get("strategy", "mobile")
        )
        
        if not audit_result.get("success", False):
            raise HTTPException(
                status_code=500,
                detail={
                    "success": False,
                    "error": audit_result.get("error", "Unknown error"),
                    "error_code": audit_result.get("error_code", "HYBRID_AUDIT_FAILED"),
                    "context": audit_result.get("context", "hybrid_audit")
                }
            )
        
        return audit_result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during hybrid audit: {str(e)}"
        )


@router.get("/health")
async def get_service_health(
    service: ComprehensiveSpeedService = Depends(get_comprehensive_speed_service)
) -> dict:
    """
    Get comprehensive speed service health status.
    
    Returns:
        Service health information
    """
    try:
        health_status = service.get_service_health()
        return {
            "success": True,
            "service": "comprehensive_speed",
            "health": health_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "service": "comprehensive_speed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/comprehensive/batch")
async def run_batch_comprehensive_analysis(
    requests: List[dict],
    service: ComprehensiveSpeedService = Depends(get_comprehensive_speed_service)
):
    """
    Run multiple comprehensive analyses concurrently.
    
    Args:
        requests: List of comprehensive analysis requests
        service: Comprehensive speed service instance
        
    Returns:
        List of comprehensive analysis responses
    """
    try:
        # Run batch analyses
        results = await service.run_batch_analysis(
            analysis_requests=requests,
            max_concurrent=3,
            include_pingdom=True
        )
        
        return {
            "success": True,
            "total_requests": len(requests),
            "successful_analyses": sum(1 for r in results if r.get("success", False)),
            "failed_analyses": sum(1 for r in results if not r.get("success", False)),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch comprehensive analysis: {str(e)}"
        )


@router.get("/comprehensive/{business_id}/summary", response_model=dict)
async def get_comprehensive_summary(
    business_id: str,
    service: ComprehensiveSpeedService = Depends(get_comprehensive_speed_service)
) -> dict:
    """
    Get comprehensive analysis summary for a business.
    
    Args:
        business_id: Business identifier
        service: Comprehensive speed service instance
        
    Returns:
        Comprehensive analysis summary with results
    """
    try:
        # For now, return a placeholder summary
        # In production, this would query a database for analysis history
        summary = {
            "business_id": business_id,
            "total_analyses": 0,
            "successful_analyses": 0,
            "average_overall_score": 0.0,
            "last_analysis": None,
            "analysis_history": [],
            "message": "Comprehensive analysis summary endpoint - implementation pending"
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error getting comprehensive summary: {str(e)}"
        )


@router.post("/validate-scores", response_model=ScoreValidationResponse)
async def validate_website_scores(
    request: ScoreValidationRequest,
    service: ScoreValidationService = Depends(get_score_validation_service)
) -> ScoreValidationResponse:
    """
    Validate and compare website scores from different sources.
    
    Args:
        request: Score validation request with heuristic scores
        service: Score validation service instance
        
    Returns:
        Score validation response with validation results
    """
    try:
        # Validate request
        if not service.validate_input(request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Invalid score validation request"
            )
        
        # Run score validation
        validation_result = service.validate_scores(
            heuristic_scores=[],  # No heuristic scores in new system
            heuristic_weight=0.0,  # No heuristic weight
            business_id=request.business_id,
            run_id=request.run_id
        )
        
        if not validation_result.get("success", False):
            error_response = ScoreValidationResponse(
                success=False,
                error=validation_result.get("error", "Unknown error"),
                error_code=validation_result.get("error_code", "VALIDATION_FAILED"),
                context=validation_result.get("context", "score_validation"),
                run_id=request.run_id,
                business_id=request.business_id
            )
            raise HTTPException(
                status_code=500,
                detail=error_response.dict()
            )
        
        # Convert to response model
        response = ScoreValidationResponse(
            success=True,
            business_id=validation_result["business_id"],
            run_id=validation_result["run_id"],
            validation_timestamp=validation_result["validation_timestamp"],
            validated_scores=validation_result["validated_scores"],
            confidence_score=validation_result["confidence_score"],
            validation_insights=validation_result["validation_insights"],
            raw_data=validation_result.get("raw_data", {})
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during score validation: {str(e)}"
        )


@router.post("/fallback", response_model=FallbackScoringResponse)
async def run_fallback_scoring(
    request: FallbackScoringRequest,
    service: FallbackScoringService = Depends(get_fallback_scoring_service)
) -> FallbackScoringResponse:
    """
    Run fallback scoring when primary evaluation fails.
    
    Args:
        request: Fallback scoring request with failure details
        service: Fallback scoring service instance
        
    Returns:
        Fallback scoring response with alternative scores
    """
    try:
        # Validate request
        if not service.validate_input(request.dict()):
            raise HTTPException(
                status_code=400,
                detail="Invalid fallback scoring request"
            )
        
        # Run fallback scoring
        fallback_result = service.run_fallback_scoring(
            website_url=request.website_url,
            business_id=request.business_id,
            primary_failure_reason=request.primary_failure_reason,
            run_id=request.run_id
        )
        
        if not fallback_result.get("success", False):
            error_response = FallbackScoringResponse(
                success=False,
                error=fallback_result.get("error", "Unknown error"),
                error_code=fallback_result.get("error_code", "FALLBACK_FAILED"),
                context=fallback_result.get("context", "fallback_scoring"),
                run_id=request.run_id,
                business_id=request.business_id
            )
            raise HTTPException(
                status_code=500,
                detail=error_response.dict()
            )
        
        # Convert to response model
        response = FallbackScoringResponse(
            success=True,
            website_url=fallback_result["website_url"],
            business_id=fallback_result["business_id"],
            run_id=fallback_result["run_id"],
            scoring_timestamp=fallback_result["scoring_timestamp"],
            fallback_scores=fallback_result["fallback_scores"],
            fallback_method=fallback_result["fallback_method"],
            confidence_level=fallback_result["confidence_level"],
            raw_data=fallback_result.get("raw_data", {})
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
    Get fallback scoring system monitoring data.
    
    Args:
        service: Fallback scoring service instance
        
    Returns:
        Fallback monitoring response with system health data
    """
    try:
        # Get monitoring data
        monitoring_data = service.get_monitoring_data()
        
        response = FallbackMonitoringResponse(
            success=True,
            system_health=monitoring_data.get("system_health", "unknown"),
            fallback_success_rate=monitoring_data.get("fallback_success_rate", 0.0),
            average_response_time=monitoring_data.get("average_response_time", 0.0),
            total_fallback_requests=monitoring_data.get("total_fallback_requests", 0),
            successful_fallback_requests=monitoring_data.get("successful_fallback_requests", 0),
            monitoring_timestamp=time.time()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error getting fallback monitoring: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for website scoring service."""
    return {
        "status": "healthy",
        "service": "website-scoring",
        "timestamp": time.time(),
        "version": "2.0.0"
    }
