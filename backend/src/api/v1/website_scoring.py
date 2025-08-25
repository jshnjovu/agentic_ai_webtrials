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
        
        # Debug logging to understand the response structure
        logger.debug(f"🔍 Analysis result structure: {list(analysis_result.keys())}")
        if analysis_result.get("mobile"):
            logger.debug(f"📱 Mobile data keys: {list(analysis_result['mobile'].keys())}")
            if analysis_result["mobile"].get("scores"):
                logger.debug(f"📊 Mobile scores: {analysis_result['mobile']['scores']}")
        if analysis_result.get("desktop"):
            logger.debug(f"💻 Desktop data keys: {list(analysis_result['desktop'].keys())}")
            if analysis_result["desktop"].get("scores"):
                logger.debug(f"📊 Desktop scores: {analysis_result['desktop']['scores']}")
        
        # Check if this is a fallback result
        is_fallback = analysis_result.get("fallback_reason", {}).get("fallback_scores_used", False)
        
        if is_fallback:
            logger.warning(f"⚠️ Using fallback scores for {request.website_url}")
        
        # Extract scores from analysis result - handle the new mobile/desktop structure
        # The unified analyzer returns {mobile: {...}, desktop: {...}, errors: [...]}
        mobile_data = analysis_result.get("mobile", {})
        desktop_data = analysis_result.get("desktop", {})
        
        # Prefer mobile scores, fallback to desktop (following the new ethos)
        scores_data = mobile_data.get("scores", {}) if mobile_data else desktop_data.get("scores", {})
        
        # If no scores data is available, log a warning and use defaults
        if not scores_data:
            logger.warning(f"⚠️ No scores data available for {request.website_url} - mobile: {bool(mobile_data)}, desktop: {bool(desktop_data)}")
            scores_data = {}
        
        # Extract scores from the unified analyzer response
        # The scores are already calculated in unified.py and returned in the scores field
        performance_score = scores_data.get("performance", 0)
        accessibility_score = scores_data.get("accessibility", 0)
        seo_score = scores_data.get("seo", 0)
        
        # Validate that we have valid scores
        if not isinstance(performance_score, (int, float)) or performance_score < 0:
            logger.warning(f"⚠️ Invalid performance score for {request.website_url}: {performance_score}, defaulting to 0")
            performance_score = 0
        if not isinstance(accessibility_score, (int, float)) or accessibility_score < 0:
            logger.warning(f"⚠️ Invalid accessibility score for {request.website_url}: {accessibility_score}, defaulting to 0")
            accessibility_score = 0
        if not isinstance(seo_score, (int, float)) or seo_score < 0:
            logger.warning(f"⚠️ Invalid SEO score for {request.website_url}: {seo_score}, defaulting to 0")
            seo_score = 0
        
        # For now, set trust to 0 since it's not provided by PageSpeed
        # Use mobile usability score as a CRO indicator since it affects user experience
        trust_score = 0
        cro_score = 0
        
        # Try to get mobile usability score as a CRO indicator
        try:
            analyzer = UnifiedAnalyzer()
            mobile_usability_score = analyzer.get_mobile_usability_score(analysis_result)
            if mobile_usability_score is not None:
                cro_score = mobile_usability_score
                logger.info(f"📱 Using mobile usability score as CRO indicator: {cro_score} for {request.website_url}")
        except Exception as e:
            logger.warning(f"⚠️ Could not extract mobile usability score for {request.website_url}: {e}")
        
        # Create WebsiteScore object with proper field mapping
        # Calculate overall as percentage (average of 5 metrics)
        overall_percentage = round(sum([
            performance_score,
            accessibility_score,
            seo_score,
            trust_score,
            cro_score
        ]) / 5, 1)  # Round to 1 decimal place for cleaner display
         
        website_scores = WebsiteScore(
            performance=performance_score,
            accessibility=accessibility_score,
            seo=seo_score,
            trust=trust_score,
            cro=cro_score,
            overall=overall_percentage
        )
        
        # Validate scores and log any anomalies
        _validate_and_log_scores(website_scores, request.website_url)
        
        # Extract and map core web vitals from the mobile/desktop data
        # Prefer mobile data, fallback to desktop
        source_data = mobile_data if mobile_data else desktop_data
        core_web_vitals_data = source_data.get("coreWebVitals", {})
        server_metrics_data = source_data.get("serverMetrics", {})
        
        # Extract core web vitals values safely
        # The unified analyzer returns metrics in the format: {"value": number, "displayValue": string, "unit": string}
        first_contentful_paint = None
        largest_contentful_paint = None
        cumulative_layout_shift = None
        total_blocking_time = None
        speed_index = None
        
        if core_web_vitals_data:
            if core_web_vitals_data.get("firstContentfulPaint"):
                first_contentful_paint = core_web_vitals_data["firstContentfulPaint"].get("value")
            if core_web_vitals_data.get("largestContentfulPaint"):
                largest_contentful_paint = core_web_vitals_data["largestContentfulPaint"].get("value")
            if core_web_vitals_data.get("cumulativeLayoutShift"):
                cumulative_layout_shift = core_web_vitals_data["cumulativeLayoutShift"].get("value")
            if core_web_vitals_data.get("speedIndex"):
                speed_index = core_web_vitals_data["speedIndex"].get("value")
        
        if server_metrics_data:
            if server_metrics_data.get("totalBlockingTime"):
                total_blocking_time = server_metrics_data["totalBlockingTime"].get("value")
        
        # Extract opportunities and top issues for the response
        opportunities = []
        top_issues = []
        try:
            # Get opportunities from the unified analyzer
            analyzer = UnifiedAnalyzer()
            opportunities = analyzer.get_all_opportunities(analysis_result)
            top_issues = analyzer.get_top_issues(analysis_result)
            logger.info(f"📋 Extracted {len(opportunities)} opportunities and {len(top_issues)} top issues for {request.website_url}")
        except Exception as e:
            logger.warning(f"⚠️ Could not extract opportunities/top issues for {request.website_url}: {e}")
            opportunities = []
            top_issues = []
        
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
                "first_contentful_paint": first_contentful_paint,
                "largest_contentful_paint": largest_contentful_paint,
                "cumulative_layout_shift": cumulative_layout_shift,
                "total_blocking_time": total_blocking_time,
                "speed_index": speed_index
            },
            raw_data=analysis_result,
            opportunities=opportunities,  # Add opportunities to the response
            top_issues=top_issues  # Add top issues to the response
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
        logger.info(f"📊 Scores extracted - Performance: {performance_score}, Accessibility: {accessibility_score}, SEO: {seo_score}, Overall: {website_scores.overall}")
        
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
        if any(score == 100 for score in [scores.performance, scores.accessibility, scores.seo, scores.trust, scores.cro]):
            logger.warning(f"⚠️ Perfect scores detected for {website_url} - verify calculation accuracy")
        
        # Check for very low scores that might indicate issues
        low_scores = [score for score in [scores.performance, scores.accessibility, scores.seo, scores.trust, scores.cro] if score <= 10]
        if low_scores:
            logger.info(f"📊 Very low scores for {website_url}: {low_scores}")
        
        # Log overall score calculation
        expected_overall = round(sum([scores.performance, scores.accessibility, scores.seo, scores.trust, scores.cro]) / 5)
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
        # Create a default WebsiteScore for the summary
        default_scores = WebsiteScore(
            performance=0,
            accessibility=0,
            seo=0,
            trust=0,
            cro=0,
            overall=0
        )
        
        summary = WebsiteScoringSummary(
            business_id=business_id,
            total_audits=0,
            successful_audits=0,
            failed_audits=0,
            average_scores=default_scores,
            latest_audit=None,
            audit_history=[]
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
        Comprehensive analysis results with calculated Overall score
    """
    try:
        url = request.get("website_url")
        strategy = request.get("strategy", "mobile")
        
        if not url:
            raise HTTPException(status_code=400, detail="Website URL is required")
        
        # Run comprehensive analysis using unified analyzer
        result = await analyzer.run_comprehensive_analysis(url, strategy)
        
        # Add the calculated Overall score from unified.py
        if result and not result.get("error"):
            try:
                overall_score = analyzer.get_overall_score(result)
                result["overall_score"] = overall_score
                logger.info(f"✅ Added calculated Overall score: {overall_score} for {url}")
                
                # Add opportunities (both specific and generic) to the result
                opportunities = analyzer.get_all_opportunities(result)
                result["opportunities"] = opportunities
                logger.info(f"📋 Added {len(opportunities)} opportunities for {url}")
                
                # Add individual scores for easier access
                result["scores"] = {
                    "performance": analyzer.get_performance_score(result),
                    "accessibility": analyzer.get_accessibility_score(result),
                    "seo": analyzer.get_seo_score(result),
                    "trust": analyzer.get_trust_score(result),
                    "cro": analyzer.get_cro_score(result),
                    "overall": overall_score
                }
                
            except Exception as score_error:
                logger.warning(f"⚠️ Could not calculate Overall score for {url}: {score_error}")
                result["overall_score"] = None
                result["scores"] = None
        
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






