"""
Website scoring API endpoints for comprehensive speed analysis using unified analyzer.
Provides endpoints for website analysis using enhanced unified analyzer with caching, retry logic, and comprehensive metrics.
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
from src.services.unified import UnifiedAnalyzer
from src.services.rate_limiter import RateLimiter
from src.models.website_scoring import WebsiteScore
from src.utils.score_calculation import calculate_overall_score, get_score_insights

router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])


def get_unified_analyzer() -> UnifiedAnalyzer:
    """Dependency to get UnifiedAnalyzer instance."""
    return UnifiedAnalyzer()


def get_rate_limiter() -> RateLimiter:
    """Dependency to get RateLimiter instance."""
    return RateLimiter()


@router.post("/pagespeed", response_model=PageSpeedAuditResponse)
async def run_pagespeed_audit(
    request: PageSpeedAuditRequest,
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
) -> PageSpeedAuditResponse:
    """
    Run a PageSpeed audit using enhanced unified analyzer.
    
    Args:
        request: PageSpeed audit request with website URL and parameters
        analyzer: Unified analyzer instance
        
    Returns:
        PageSpeed audit response with analysis scores and metrics
    """
    try:
        # Run PageSpeed analysis using unified analyzer
        analysis_result = await analyzer.run_page_speed_analysis(
            url=request.website_url,
            strategy=request.strategy
        )
        
        # Convert unified analyzer result to PageSpeed response format
        response = PageSpeedAuditResponse(
            success=True,
            website_url=request.website_url,
            business_id=request.business_id,
            run_id=request.run_id,
            audit_timestamp=datetime.now().isoformat(),
            strategy=request.strategy,
            scores=analysis_result["scores"],
            core_web_vitals=analysis_result["coreWebVitals"],
            raw_data=analysis_result
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during PageSpeed audit: {str(e)}"
        )


@router.post("/pagespeed/batch")
async def run_batch_pagespeed_audits(
    requests: List[PageSpeedAuditRequest],
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
):
    """
    Run multiple PageSpeed audits concurrently using unified analyzer.
    
    Args:
        requests: List of PageSpeed audit requests
        analyzer: Unified analyzer instance
        
    Returns:
        List of PageSpeed audit responses
    """
    try:
        # Extract URLs from requests
        urls = [req.website_url for req in requests]
        
        # Run batch analysis using unified analyzer
        results = await analyzer.run_batch_analysis(urls, strategy=requests[0].strategy)
        
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
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
) -> WebsiteScoringSummary:
    """
    Get PageSpeed audit summary for a business using unified analyzer.
    
    Args:
        business_id: Business identifier
        analyzer: Unified analyzer instance
        
    Returns:
        Website scoring summary with PageSpeed results
    """
    try:
        # For now, return a placeholder summary since we don't have audit history
        # In a real implementation, you would query a database for historical results
        summary = WebsiteScoringSummary(
            business_id=business_id,
            total_audits=0,
            average_performance_score=0,
            average_accessibility_score=0,
            average_best_practices_score=0,
            average_seo_score=0,
            last_audit_date=None,
            confidence_level=ConfidenceLevel.LOW,
            audit_strategy=AuditStrategy.MOBILE
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving PageSpeed summary: {str(e)}"
        )


@router.post("/comprehensive")
async def run_comprehensive_analysis(
    request: dict,
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
):
    """
    Run comprehensive website analysis using unified analyzer.
    
    Args:
        request: Analysis request with website URL and parameters
        analyzer: Unified analyzer instance
        
    Returns:
        Comprehensive analysis results
    """
    try:
        url = request.get("website_url")
        strategy = request.get("strategy", "mobile")
        
        if not url:
            raise HTTPException(status_code=400, detail="Website URL is required")
        
        # Run comprehensive analysis using unified analyzer
        result = await analyzer.run_comprehensive_analysis(url, strategy)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during comprehensive analysis: {str(e)}"
        )


@router.post("/comprehensive/batch")
async def run_batch_comprehensive_analysis(
    request: dict,
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
):
    """
    Run comprehensive analysis on multiple URLs using unified analyzer.
    
    Args:
        request: Batch analysis request with list of URLs
        analyzer: Unified analyzer instance
        
    Returns:
        Batch analysis results
    """
    try:
        urls = request.get("urls", [])
        strategy = request.get("strategy", "mobile")
        max_concurrent = request.get("max_concurrent", 3)
        
        if not urls:
            raise HTTPException(status_code=400, detail="URLs list is required")
        
        # Run batch comprehensive analysis using unified analyzer
        results = await analyzer.run_batch_analysis(urls, strategy, max_concurrent)
        
        return {
            "success": True,
            "total_urls": len(urls),
            "successful_analyses": sum(1 for r in results if r.get("success", False)),
            "failed_analyses": sum(1 for r in results if not r.get("success", False)),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch comprehensive analysis: {str(e)}"
        )


@router.get("/health")
async def get_analyzer_health(
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
):
    """
    Get health status of the unified analyzer.
    
    Args:
        analyzer: Unified analyzer instance
        
    Returns:
        Health status information
    """
    try:
        health_status = analyzer.get_service_health()
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving health status: {str(e)}"
        )


@router.get("/statistics")
async def get_analyzer_statistics(
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
):
    """
    Get analysis statistics from the unified analyzer.
    
    Args:
        analyzer: Unified analyzer instance
        
    Returns:
        Analysis performance statistics
    """
    try:
        stats = analyzer.get_analysis_statistics()
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving statistics: {str(e)}"
        )


@router.post("/validate-score")
async def validate_score(
    request: ScoreValidationRequest,
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
) -> ScoreValidationResponse:
    """
    Validate website score using unified analyzer.
    
    Args:
        request: Score validation request
        analyzer: Unified analyzer instance
        
    Returns:
        Score validation response
    """
    try:
        # Run a quick analysis to validate the score
        url = request.website_url
        strategy = request.audit_strategy.value if request.audit_strategy else "mobile"
        
        analysis_result = await analyzer.run_page_speed_analysis(url, strategy)
        
        # Extract the relevant score for validation
        score_to_validate = getattr(request, request.score_type.lower(), 0)
        actual_score = analysis_result["scores"].get(request.score_type.lower(), 0)
        
        # Calculate confidence based on score difference
        score_difference = abs(score_to_validate - actual_score)
        if score_difference <= 5:
            confidence = ConfidenceLevel.HIGH
        elif score_difference <= 15:
            confidence = ConfidenceLevel.MEDIUM
        else:
            confidence = ConfidenceLevel.LOW
        
        validation_response = ScoreValidationResponse(
            business_id=request.business_id,
            website_url=request.website_url,
            score_type=request.score_type,
            submitted_score=score_to_validate,
            validated_score=actual_score,
            confidence_level=confidence,
            validation_timestamp=datetime.now().isoformat(),
            score_difference=score_difference,
            is_valid=score_difference <= 10
        )
        
        return validation_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during score validation: {str(e)}"
        )


@router.post("/fallback-scoring")
async def run_fallback_scoring(
    request: FallbackScoringRequest,
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
) -> FallbackScoringResponse:
    """
    Run fallback scoring using unified analyzer when primary services fail.
    
    Args:
        request: Fallback scoring request
        analyzer: Unified analyzer instance
        
    Returns:
        Fallback scoring response
    """
    try:
        url = request.website_url
        strategy = request.fallback_strategy.value if request.fallback_strategy else "mobile"
        
        # Use unified analyzer's comprehensive analysis as fallback
        fallback_result = await analyzer.run_comprehensive_analysis(url, strategy)
        
        if not fallback_result.get("success", False):
            raise FallbackScoringError(
                success=False,
                error=fallback_result.get("error", "Fallback analysis failed"),
                error_code=fallback_result.get("error_code", "FALLBACK_FAILED"),
                context="fallback_scoring"
            )
        
        # Extract scores from fallback result
        scores = fallback_result.get("scores", {})
        
        fallback_response = FallbackScoringResponse(
            success=True,
            business_id=request.business_id,
            website_url=request.website_url,
            fallback_strategy=request.fallback_strategy,
            scores=scores,
            analysis_timestamp=datetime.now().isoformat(),
            fallback_reason=request.fallback_reason,
            confidence_level=ConfidenceLevel.MEDIUM  # Fallback results have medium confidence
        )
        
        return fallback_response
        
    except FallbackScoringError:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during fallback scoring: {str(e)}"
        )


@router.get("/fallback-monitoring")
async def get_fallback_monitoring(
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
) -> FallbackMonitoringResponse:
    """
    Get fallback system monitoring information.
    
    Args:
        analyzer: Unified analyzer instance
        
    Returns:
        Fallback monitoring response
    """
    try:
        # Get health status to monitor fallback system
        health_status = analyzer.get_service_health()
        
        monitoring_response = FallbackMonitoringResponse(
            fallback_system_status="operational" if health_status["status"] != "unhealthy" else "degraded",
            last_fallback_triggered=datetime.now().isoformat(),
            fallback_success_rate=100.0,  # Placeholder - would be calculated from actual usage
            active_fallback_strategies=["unified_analyzer"],
            system_health=health_status
        )
        
        return monitoring_response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error retrieving fallback monitoring: {str(e)}"
        )
