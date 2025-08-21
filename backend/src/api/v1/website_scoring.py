"""
Website scoring API endpoints for comprehensive speed analysis using unified analyzer.
Provides endpoints for website analysis using enhanced unified analyzer with caching, retry logic, and comprehensive metrics.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from datetime import datetime
import uuid
import time
import logging

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
    PageSpeedAuditError,
    CoreWebVitals,
    WebsiteScore
)
from src.services.unified import UnifiedAnalyzer
from src.services.rate_limiter import RateLimiter
from src.utils.score_calculation import calculate_overall_score, get_score_insights

router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        # Log the request details
        logger.info(f"🚀 Starting PageSpeed audit for URL: {request.website_url}")
        logger.info(f"📋 Request details: business_id={request.business_id}, run_id={request.run_id}, strategy={request.strategy}")
        
        # Run PageSpeed analysis using unified analyzer
        analysis_result = await analyzer.run_page_speed_analysis(
            url=request.website_url,
            strategy=request.strategy.value  # Convert enum to string value
        )
        
        # Check if this is a fallback result
        is_fallback = analysis_result.get("fallback_reason", {}).get("fallback_scores_used", False)
        
        if is_fallback:
            logger.warning(f"⚠️ Using fallback scores for {request.website_url}")
            logger.warning(f"📋 Fallback reason: {analysis_result.get('fallback_reason', {}).get('primary_reason', 'UNKNOWN')}")
        
        # Extract scores from analysis result
        scores_data = analysis_result.get("scores", {})
        
        # Create WebsiteScore object with proper field mapping
        website_scores = WebsiteScore(
            performance=scores_data.get("performance", 0),
            accessibility=scores_data.get("accessibility", 0),
            best_practices=scores_data.get("bestPractices", 0),  # Note: unified uses camelCase
            seo=scores_data.get("seo", 0),
            overall=round(sum([
                scores_data.get("performance", 0),
                scores_data.get("accessibility", 0),
                scores_data.get("bestPractices", 0),
                scores_data.get("seo", 0)
            ]) / 4)  # Calculate overall as average
        )
        
        # Validate scores and log any anomalies
        _validate_and_log_scores(website_scores, request.website_url)
        
        # Extract and map core web vitals
        core_web_vitals_data = analysis_result.get("coreWebVitals", {})
        server_metrics_data = analysis_result.get("serverMetrics", {})
        
        # Create response with proper schema mapping
        response = PageSpeedAuditResponse(
            success=True,
            website_url=request.website_url,
            business_id=request.business_id,
            run_id=request.run_id,
            audit_timestamp=time.time(),
            strategy=request.strategy.value,  # Convert enum to string value
            scores=website_scores,
            core_web_vitals={
                "first_contentful_paint": core_web_vitals_data.get("firstContentfulPaint", {}).get("value") if core_web_vitals_data.get("firstContentfulPaint") else None,
                "largest_contentful_paint": core_web_vitals_data.get("largestContentfulPaint", {}).get("value") if core_web_vitals_data.get("largestContentfulPaint") else None,
                "cumulative_layout_shift": core_web_vitals_data.get("cumulativeLayoutShift", {}).get("value") if core_web_vitals_data.get("cumulativeLayoutShift") else None,
                "total_blocking_time": server_metrics_data.get("totalBlockingTime", {}).get("value") if server_metrics_data.get("totalBlockingTime") else None,
                "speed_index": core_web_vitals_data.get("speedIndex", {}).get("value") if core_web_vitals_data.get("speedIndex") else None
            },
            raw_data=analysis_result
        )
        
        # Add fallback information to response if applicable
        if is_fallback:
            response.raw_data = {
                **response.raw_data,
                "fallback_info": {
                    "fallback_scores_used": True,
                    "primary_reason": analysis_result.get("fallback_reason", {}).get("primary_reason", "UNKNOWN"),
                    "fallback_timestamp": analysis_result.get("fallback_reason", {}).get("timestamp"),
                    "message": f"PageSpeed analysis failed, using fallback scores. Reason: {analysis_result.get('fallback_reason', {}).get('primary_reason', 'UNKNOWN')}"
                }
            }
        
        # Log final results
        if is_fallback:
            logger.warning(f"⚠️ Final fallback scores for {request.website_url}: {website_scores}")
        else:
            logger.info(f"✅ PageSpeed analysis completed for {request.website_url}")
            logger.info(f"📊 Final scores: {website_scores}")
        
        return response
        
    except Exception as e:
        # Enhanced error logging
        error_context = {
            "website_url": request.website_url,
            "business_id": request.business_id,
            "run_id": request.run_id,
            "strategy": request.strategy.value,  # Convert enum to string value
            "error_type": type(e).__name__,
            "error_message": str(e),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.error(f"❌ PageSpeed audit failed for {request.website_url}")
        logger.error(f"🔍 Error context: {error_context}")
        logger.error(f"📋 Full error details: {e}")
        
        # Log additional debugging info if available
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error(f"📚 Traceback: {''.join(traceback.format_tb(e.__traceback__))}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during PageSpeed audit: {str(e)}"
        )


def _validate_and_log_scores(scores: WebsiteScore, website_url: str):
    """Validate scores and log any anomalies for debugging."""
    try:
        # Check for extreme scores that might indicate calculation errors
        extreme_scores = []
        if scores.performance == 100:
            extreme_scores.append(f"performance={scores.performance}")
        if scores.accessibility == 100:
            extreme_scores.append(f"accessibility={scores.accessibility}")
        if scores.best_practices == 100:
            extreme_scores.append(f"best_practices={scores.best_practices}")
        if scores.seo == 100:
            extreme_scores.append(f"seo={scores.seo}")
        
        if extreme_scores:
            logger.warning(f"⚠️ Perfect scores detected for {website_url}: {', '.join(extreme_scores)}")
            logger.warning(f"📋 This might indicate a calculation issue or extremely well-optimized site")
        
        # Check for very low scores that might indicate issues
        low_scores = []
        if scores.performance <= 10:
            low_scores.append(f"performance={scores.performance}")
        if scores.accessibility <= 10:
            low_scores.append(f"accessibility={scores.accessibility}")
        if scores.best_practices <= 10:
            low_scores.append(f"best_practices={scores.best_practices}")
        if scores.seo <= 10:
            low_scores.append(f"seo={scores.seo}")
        
        if low_scores:
            logger.info(f"📊 Very low scores for {website_url}: {', '.join(low_scores)}")
            logger.info(f"📋 This might indicate site issues or legitimate poor performance")
        
        # Log overall score calculation
        expected_overall = round(sum([scores.performance, scores.accessibility, scores.best_practices, scores.seo]) / 4)
        if expected_overall != scores.overall:
            logger.warning(f"⚠️ Score calculation mismatch for {website_url}")
            logger.warning(f"📋 Expected overall: {expected_overall}, got: {scores.overall}")
            logger.warning(f"📋 Individual scores: p={scores.performance}, a={scores.accessibility}, bp={scores.best_practices}, seo={scores.seo}")
        
    except Exception as e:
        logger.error(f"❌ Error validating scores for {website_url}: {e}")


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
        results = await analyzer.run_batch_analysis(urls, strategy=requests[0].strategy.value)
        
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
            audit_strategy="mobile"  # Use string value instead of enum
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
