"""
Website scoring API endpoints for comprehensive speed analysis using unified analyzer.
Provides endpoints for website analysis using enhanced unified analyzer with caching, retry logic, and comprehensive metrics.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
import time
import logging

from src.schemas.website_scoring import (
    WebsiteScoringSummary,
    AuditStrategy,
    ConfidenceLevel,
    ScoreValidationRequest,
    ScoreValidationResponse,
    PageSpeedAuditRequest,
    PageSpeedAuditResponse,
    WebsiteScore
)
from src.services.unified import UnifiedAnalyzer


router = APIRouter(prefix="/website-scoring", tags=["website-scoring"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_unified_analyzer() -> UnifiedAnalyzer:
    """Dependency to get UnifiedAnalyzer instance."""
    return UnifiedAnalyzer()





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
        logger.info(f"🚀 Starting PageSpeed audit for {request.website_url}")
        
        # Run PageSpeed analysis using unified analyzer
        analysis_result = await analyzer.run_page_speed_analysis(
            url=request.website_url,
            strategy=request.strategy.value  # Convert enum to string value
        )
        
        # Check if this is a fallback result
        is_fallback = analysis_result.get("fallback_reason", {}).get("fallback_scores_used", False)
        
        if is_fallback:
            logger.warning(f"⚠️ Using fallback scores for {request.website_url}")
        
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
        
        logger.info(f"✅ PageSpeed analysis completed for {request.website_url}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ PageSpeed audit failed for {request.website_url}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during PageSpeed audit: {str(e)}"
        )


def _validate_and_log_scores(scores: WebsiteScore, website_url: str):
    """Validate scores and log any anomalies for debugging."""
    try:
        # Check for extreme scores that might indicate calculation errors
        if any(score == 100 for score in [scores.performance, scores.accessibility, scores.best_practices, scores.seo]):
            logger.warning(f"⚠️ Perfect scores detected for {website_url} - verify calculation accuracy")
        
        # Check for very low scores that might indicate issues
        low_scores = [score for score in [scores.performance, scores.accessibility, scores.best_practices, scores.seo] if score <= 10]
        if low_scores:
            logger.info(f"📊 Very low scores for {website_url}: {low_scores}")
        
        # Log overall score calculation
        expected_overall = round(sum([scores.performance, scores.accessibility, scores.best_practices, scores.seo]) / 4)
        if expected_overall != scores.overall:
            logger.warning(f"⚠️ Score calculation mismatch for {website_url}: expected {expected_overall}, got {scores.overall}")
        
    except Exception as e:
        logger.error(f"❌ Error validating scores for {website_url}: {e}")


@router.post("/batch")
async def run_batch_analysis(
    request: dict,
    analyzer: UnifiedAnalyzer = Depends(get_unified_analyzer)
):
    """
    Run batch analysis on multiple URLs using unified analyzer.
    
    Args:
        request: Batch analysis request with list of URLs and analysis type
        analyzer: Unified analyzer instance
        
    Returns:
        Batch analysis results
    """
    try:
        urls = request.get("urls", [])
        analysis_type = request.get("type", "pagespeed")  # "pagespeed" or "comprehensive"
        strategy = request.get("strategy", "mobile")
        max_concurrent = request.get("max_concurrent", 3)
        
        if not urls:
            raise HTTPException(status_code=400, detail="URLs list is required")
        
        # Run batch analysis using unified analyzer
        if analysis_type == "comprehensive":
            results = await analyzer.run_batch_analysis(urls, strategy, max_concurrent)
        else:
            results = await analyzer.run_batch_analysis(urls, strategy, max_concurrent)
        
        return {
            "success": True,
            "total_urls": len(urls),
            "analysis_type": analysis_type,
            "successful_analyses": sum(1 for r in results if r.get("success", False)),
            "failed_analyses": sum(1 for r in results if not r.get("success", False)),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during batch analysis: {str(e)}"
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
        confidence = (
            ConfidenceLevel.HIGH if score_difference <= 5 else
            ConfidenceLevel.MEDIUM if score_difference <= 15 else
            ConfidenceLevel.LOW
        )
        
        return ScoreValidationResponse(
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
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during score validation: {str(e)}"
        )






