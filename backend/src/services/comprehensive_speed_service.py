"""
Comprehensive Speed Service for website performance analysis.
Orchestrates unified analysis for complete website health assessment.
Based on best practices from temp_place_z implementation.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.base_service import BaseService
from src.core.config import get_api_config
from src.services.rate_limiter import RateLimiter
from src.services.unified import UnifiedAnalyzer

logger = logging.getLogger(__name__)


class ComprehensiveSpeedService(BaseService):
    """Service for comprehensive website speed and health analysis."""
    
    def __init__(self):
        super().__init__("ComprehensiveSpeedService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        
        # Initialize unified analyzer service
        self.unified_analyzer = UnifiedAnalyzer()
        
        # Analysis configuration
        self.analysis_timeout = self.api_config.COMPREHENSIVE_ANALYSIS_TIMEOUT_SECONDS
        
        # Service health tracking
        self.service_health = {
            "unified": "unknown",
            "overall": "unknown"
        }
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for comprehensive analysis."""
        if not isinstance(data, dict):
            return False
        
        required_fields = ['website_url', 'business_id']
        return all(field in data for field in required_fields)
    
    async def run_comprehensive_analysis(
        self,
        website_url: str,
        business_id: str,
        run_id: Optional[str] = None,
        strategy: str = "mobile"
    ) -> Dict[str, Any]:
        """
        Run comprehensive website analysis using unified analyzer.
        
        Args:
            website_url: URL of the website to analyze
            business_id: Business identifier for tracking
            run_id: Run identifier for tracking
            strategy: Analysis strategy ('mobile' or 'desktop')
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        start_time = time.time()
        
        try:
            self.log_operation(
                "Starting comprehensive speed analysis",
                run_id=run_id,
                business_id=business_id,
                website_url=website_url
            )
            
            # Check rate limiting
            can_proceed, message = self.rate_limiter.can_make_request("comprehensive_speed", run_id)
            if not can_proceed:
                self.log_operation(
                    f"Rate limit exceeded: {message}",
                    run_id=run_id,
                    business_id=business_id
                )
                return {
                    "success": False,
                    "error": f"Rate limit exceeded: {message}",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "context": "rate_limit_check",
                    "run_id": run_id,
                    "business_id": business_id
                }
            
            # Initialize analysis result
            analysis_result = {
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id,
                "analysis_timestamp": time.time(),
                "strategy": strategy,
                "scores": {},
                "details": {},
                "scoring_method": "comprehensive",
                "services_used": []
            }
            
            # 1. Unified Analysis (Performance, Accessibility, Best Practices, SEO, Trust, CRO)
            logger.info(f"Running unified analysis for {website_url}")
            try:
                unified_result = await self.unified_analyzer.run_comprehensive_analysis(
                    website_url, strategy
                )
                
                if unified_result.get("success", False):
                    analysis_result["details"]["unified"] = unified_result
                    analysis_result["services_used"].append("unified")
                    
                    # Extract all scores from unified analysis
                    unified_scores = unified_result.get("scores", {})
                    analysis_result["scores"].update({
                        "performance": unified_scores.get("performance", 0.0),
                        "accessibility": unified_scores.get("accessibility", 0.0),
                        "bestPractices": unified_scores.get("bestPractices", 0.0),
                        "seo": unified_scores.get("seo", 0.0),
                        "cro": unified_scores.get("cro", 0.0)
                    })
                    
                    # Add Core Web Vitals and other details
                    if "details" in unified_result:
                        if "pagespeed" in unified_result["details"]:
                            analysis_result["details"]["pagespeed"] = unified_result["details"]["pagespeed"]
                        if "trust" in unified_result["details"]:
                            analysis_result["details"]["trust"] = unified_result["details"]["trust"]
                        if "cro" in unified_result["details"]:
                            analysis_result["details"]["cro"] = unified_result["details"]["cro"]
                        if "uptime" in unified_result["details"]:
                            analysis_result["details"]["uptime"] = unified_result["details"]["uptime"]
                    
                    logger.info(f"Unified analysis completed successfully for {website_url}")
                else:
                    logger.warning(f"Unified analysis failed for {website_url}: {unified_result.get('error')}")
                    # Set default scores for failed analysis
                    analysis_result["scores"].update({
                        "performance": 0.0,
                        "accessibility": 0.0,
                        "bestPractices": 0.0,
                        "seo": 0.0,
                        "cro": 0.0
                    })
                    
            except Exception as e:
                logger.error(f"Unified analysis error for {website_url}: {e}")
                analysis_result["scores"].update({
                    "performance": 0.0,
                    "accessibility": 0.0,
                    "bestPractices": 0.0,
                    "seo": 0.0,
                    "cro": 0.0
                })
            
            # 3. Calculate overall score using unified analyzer's get_overall_score method
            # Create a mock analysis_result structure that unified.py expects
            mock_analysis_result = {
                "pageSpeed": {
                    "mobile": {
                        "scores": analysis_result["scores"]
                    },
                    "desktop": {
                        "scores": analysis_result["scores"]
                    }
                },
                "trustAndCRO": {
                    "trust": {
                        "parsed": {
                            "score": analysis_result["scores"].get("trust", 0)
                        }
                    },
                    "cro": {
                        "parsed": {
                            "score": analysis_result["scores"].get("cro", 0)
                        }
                    }
                }
            }
            
            overall_score = self.unified_analyzer.get_overall_score(mock_analysis_result)
            analysis_result["scores"]["overall"] = overall_score
            
            # 4. Add analysis metadata
            analysis_time = time.time() - start_time
            analysis_result["analysis_time"] = analysis_time
            analysis_result["success"] = True
            
            # 5. Update service health
            self._update_service_health()
            
            # Record successful request
            self.rate_limiter.record_request("comprehensive_speed", True, run_id)
            
            self.log_operation(
                f"Completed comprehensive analysis in {analysis_time:.2f}s",
                run_id=run_id,
                business_id=business_id,
                analysis_time=analysis_time,
                overall_score=overall_score
            )
            
            return analysis_result
            
        except Exception as e:
            # Record failed request
            self.rate_limiter.record_request("comprehensive_speed", False, run_id)
            
            self.log_error(e, "comprehensive_analysis", run_id, business_id)
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "ANALYSIS_FAILED",
                "context": "comprehensive_analysis",
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id
            }
    
    async def run_hybrid_audit(
        self,
        website_url: str,
        business_id: str,
        run_id: Optional[str] = None,
        strategy: str = "mobile"
    ) -> Dict[str, Any]:
        """
        Run hybrid audit using unified analyzer's comprehensive method.
        
        Args:
            website_url: URL of the website to analyze
            business_id: Business identifier for tracking
            run_id: Run identifier for tracking
            strategy: Analysis strategy ('mobile' or 'desktop')
            
        Returns:
            Dictionary containing hybrid audit results
        """
        try:
            logger.info(f"Running hybrid audit for {website_url}")
            
            result = await self.unified_analyzer.run_comprehensive_analysis(
                website_url, strategy
            )
            
            # Add service metadata
            result["services_used"] = ["unified_analyzer"]
            result["scoring_method"] = "unified_comprehensive"
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid audit failed for {website_url}: {e}")
            return {
                "success": False,
                "error": f"Hybrid audit failed: {str(e)}",
                "error_code": "HYBRID_AUDIT_FAILED",
                "context": "hybrid_audit",
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id
            }
    
    async def run_batch_analysis(
        self,
        analysis_requests: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Run comprehensive analysis on multiple websites concurrently.
        Delegates to unified analyzer for consistent batch processing.
        
        Args:
            analysis_requests: List of analysis request dictionaries with keys:
                - website_url: URL to analyze
                - business_id: Business identifier
                - run_id: Optional run identifier
                - strategy: Optional strategy ('mobile' or 'desktop')
            max_concurrent: Maximum concurrent analyses
            
        Returns:
            List of analysis results from unified analyzer
        """
        try:
            # Extract URLs from analysis requests
            urls = [request['website_url'] for request in analysis_requests]
            
            # Use the first request's strategy or default to mobile
            strategy = analysis_requests[0].get('strategy', 'mobile') if analysis_requests else 'mobile'
            
            # Delegate to unified analyzer for batch processing
            logger.info(f"🚀 Running batch analysis for {len(urls)} URLs using unified analyzer")
            results = await self.unified_analyzer.run_batch_analysis(
                urls=urls,
                strategy=strategy,
                max_concurrent=max_concurrent
            )
            
            # Enhance results with business_id and run_id from original requests
            enhanced_results = []
            for i, result in enumerate(results):
                if i < len(analysis_requests):
                    # Add business context from original request
                    original_request = analysis_requests[i]
                    result["business_id"] = original_request.get('business_id')
                    result["run_id"] = original_request.get('run_id')
                    
                    # Ensure success field is present for compatibility
                    if "summary" in result and result["summary"].get("servicesCompleted", 0) > 0:
                        result["success"] = True
                    else:
                        result["success"] = False
                
                enhanced_results.append(result)
            
            logger.info(f"✅ Batch analysis completed: {len(enhanced_results)} results")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"❌ Batch analysis failed: {e}")
            # Return error results for all requests
            return [
                {
                    "success": False,
                    "error": f"Batch analysis failed: {str(e)}",
                    "error_code": "BATCH_ANALYSIS_FAILED",
                    "context": "comprehensive_batch_analysis",
                    "website_url": request.get('website_url'),
                    "business_id": request.get('business_id'),
                    "run_id": request.get('run_id')
                }
                for request in analysis_requests
            ]
    

    
    def _update_service_health(self):
        """Update service health status."""
        try:
            # Check unified analyzer service health
            unified_health = self.unified_analyzer.get_service_health()
            self.service_health["unified"] = unified_health.get("status", "unknown")
            
            # Determine overall health
            if self.service_health["unified"] == "healthy":
                self.service_health["overall"] = "healthy"
            elif self.service_health["unified"] == "degraded":
                self.service_health["overall"] = "degraded"
            else:
                self.service_health["overall"] = "unhealthy"
                
        except Exception as e:
            logger.error(f"Error updating service health: {e}")
            self.service_health["overall"] = "unknown"
    
    def get_service_health(self) -> Dict[str, Any]:
        """Get comprehensive service health status."""
        self._update_service_health()
        
        return {
            "service": "comprehensive_speed",
            "status": self.service_health["overall"],
            "services": {
                "unified": self.service_health["unified"]
            },
            "rate_limits": {
                "comprehensive_speed": getattr(self.api_config, 'COMPREHENSIVE_SPEED_RATE_LIMIT_PER_MINUTE', 30)
            },
            "features": {
                "smart_retry": True,
                "intelligent_caching": True,
                "unified_scoring": True,
                "batch_processing": True
            }
        }
    
    async def get_analysis_summary(
        self,
        analysis_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate analysis summary and insights from multiple results.
        Based on temp_place_z serpapi-pagespeed-summary.js implementation.
        """
        try:
            if not analysis_results:
                return {"error": "No analysis results provided"}
            
            successful_results = [r for r in analysis_results if r.get("success", False)]
            
            if not successful_results:
                return {"error": "No successful analysis results"}
            
            # Calculate statistics
            total_websites = len(successful_results)
            
            # Performance distribution
            performance_scores = [r.get("scores", {}).get("performance", 0) for r in successful_results]
            performance_distribution = self._categorize_scores(performance_scores)
            
            # Overall score distribution
            overall_scores = [r.get("scores", {}).get("overall", 0) for r in successful_results]
            overall_distribution = self._categorize_scores(overall_scores)
            
            # Find top performers
            top_performers = sorted(
                successful_results,
                key=lambda x: x.get("scores", {}).get("overall", 0),
                reverse=True
            )[:5]
            
            # Calculate averages
            avg_scores = {
                "performance": sum(performance_scores) / len(performance_scores),
                "accessibility": sum([r.get("scores", {}).get("accessibility", 0) for r in successful_results]) / total_websites,
                "best_practices": sum([r.get("scores", {}).get("bestPractices", 0) for r in successful_results]) / total_websites,
                "seo": sum([r.get("scores", {}).get("seo", 0) for r in successful_results]) / total_websites,
                "cro": sum([r.get("scores", {}).get("cro", 0) for r in successful_results]) / total_websites,
                "overall": sum(overall_scores) / len(overall_scores)
            }
            
            summary = {
                "total_websites": total_websites,
                "successful_analyses": len(successful_results),
                "failed_analyses": len(analysis_results) - len(successful_results),
                "timestamp": time.time(),
                "performance_distribution": performance_distribution,
                "overall_distribution": overall_distribution,
                "average_scores": {k: round(v, 2) for k, v in avg_scores.items()},
                "top_performers": [
                    {
                        "website_url": r.get("website_url"),
                        "overall_score": r.get("scores", {}).get("overall", 0),
                        "performance_score": r.get("scores", {}).get("performance", 0),
                        "best_practices_score": r.get("scores", {}).get("bestPractices", 0)
                    }
                    for r in top_performers
                ],
                "insights": self._generate_insights(successful_results)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating analysis summary: {e}")
            return {"error": f"Failed to generate summary: {str(e)}"}
    
    def _categorize_scores(self, scores: List[float]) -> Dict[str, int]:
        """Categorize scores into performance levels."""
        categories = {
            "excellent": 0,  # 90-100
            "good": 0,       # 70-89
            "fair": 0,       # 50-69
            "poor": 0        # 0-49
        }
        
        for score in scores:
            if score >= 90:
                categories["excellent"] += 1
            elif score >= 70:
                categories["good"] += 1
            elif score >= 50:
                categories["fair"] += 1
            else:
                categories["poor"] += 1
        
        return categories
    
    def _generate_insights(self, results: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from analysis results."""
        insights = []
        
        try:
            # Performance insights
            performance_scores = [r.get("scores", {}).get("performance", 0) for r in results]
            avg_performance = sum(performance_scores) / len(performance_scores)
            
            if avg_performance < 50:
                insights.append("Most websites have poor performance scores - optimization needed")
            elif avg_performance < 70:
                insights.append("Performance scores are below industry standards")
            elif avg_performance >= 90:
                insights.append("Excellent performance across analyzed websites")
            
            # Best Practices insights
            best_practices_scores = [r.get("scores", {}).get("bestPractices", 0) for r in results]
            avg_best_practices = sum(best_practices_scores) / len(best_practices_scores)
            
            if avg_best_practices < 60:
                insights.append("Low best practices scores indicate room for improvement in coding standards")
            elif avg_best_practices >= 80:
                insights.append("High best practices scores show good coding standards")
            
            # CRO insights
            cro_scores = [r.get("scores", {}).get("cro", 0) for r in results]
            avg_cro = sum(cro_scores) / len(cro_scores)
            
            if avg_cro < 50:
                insights.append("Conversion optimization needs improvement across websites")
            elif avg_cro >= 75:
                insights.append("Good conversion optimization practices observed")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append("Unable to generate insights due to data processing error")
        
        return insights
