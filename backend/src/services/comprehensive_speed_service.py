"""
Comprehensive Speed Service for website performance analysis.
Orchestrates PageSpeed Insights and Pingdom analysis for complete website health assessment.
Based on best practices from temp_place_z implementation.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.base_service import BaseService
from src.core.config import get_api_config
from src.services.rate_limiter import RateLimiter
from src.services.google_pagespeed_service import GooglePageSpeedService
from src.services.pingdom_service import PingdomService

logger = logging.getLogger(__name__)


class ComprehensiveSpeedService(BaseService):
    """Service for comprehensive website speed and health analysis."""
    
    def __init__(self):
        super().__init__("ComprehensiveSpeedService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        
        # Initialize sub-services
        self.pagespeed_service = GooglePageSpeedService()
        self.pingdom_service = PingdomService()
        
        # Analysis configuration
        self.analysis_timeout = self.api_config.COMPREHENSIVE_ANALYSIS_TIMEOUT_SECONDS
        
        # Service health tracking
        self.service_health = {
            "pagespeed": "unknown",
            "pingdom": "unknown",
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
        strategy: str = "mobile",
        include_pingdom: bool = True
    ) -> Dict[str, Any]:
        """
        Run comprehensive website analysis combining PageSpeed and Pingdom data.
        
        Args:
            website_url: URL of the website to analyze
            business_id: Business identifier for tracking
            run_id: Run identifier for tracking
            strategy: Analysis strategy ('mobile' or 'desktop')
            include_pingdom: Whether to include Pingdom analysis
            
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
            
            # 1. PageSpeed Analysis (Performance, Accessibility, Best Practices, SEO)
            logger.info(f"Running PageSpeed analysis for {website_url}")
            try:
                pagespeed_result = await self.pagespeed_service.run_pagespeed_audit_with_smart_retry(
                    website_url, business_id, run_id, strategy
                )
                
                if pagespeed_result.get("success", False):
                    analysis_result["details"]["pagespeed"] = pagespeed_result
                    analysis_result["services_used"].append("pagespeed")
                    
                    # Extract PageSpeed scores
                    pagespeed_scores = pagespeed_result.get("scores", {})
                    analysis_result["scores"].update({
                        "performance": pagespeed_scores.get("performance", 0.0),
                        "accessibility": pagespeed_scores.get("accessibility", 0.0),
                        "best_practices": pagespeed_scores.get("best_practices", 0.0),
                        "seo": pagespeed_scores.get("seo", 0.0)
                    })
                    
                    # Add Core Web Vitals
                    if "core_web_vitals" in pagespeed_result:
                        analysis_result["details"]["core_web_vitals"] = pagespeed_result["core_web_vitals"]
                    
                    logger.info(f"PageSpeed analysis completed successfully for {website_url}")
                else:
                    logger.warning(f"PageSpeed analysis failed for {website_url}: {pagespeed_result.get('error')}")
                    # Set default scores for failed analysis
                    analysis_result["scores"].update({
                        "performance": 0.0,
                        "accessibility": 0.0,
                        "best_practices": 0.0,
                        "seo": 0.0
                    })
                    
            except Exception as e:
                logger.error(f"PageSpeed analysis error for {website_url}: {e}")
                analysis_result["scores"].update({
                    "performance": 0.0,
                    "accessibility": 0.0,
                    "best_practices": 0.0,
                    "seo": 0.0
                })
            
            # 2. Pingdom Analysis (Trust & CRO)
            if include_pingdom:
                logger.info(f"Running Pingdom analysis for {website_url}")
                try:
                    # Trust analysis
                    trust_result = await self.pingdom_service.analyze_trust_metrics(
                        website_url, business_id, run_id
                    )
                    
                    if trust_result.get("success", False):
                        analysis_result["details"]["trust"] = trust_result
                        analysis_result["scores"]["trust"] = trust_result.get("trust_score", 0.0)
                        analysis_result["services_used"].append("pingdom_trust")
                        logger.info(f"Trust analysis completed for {website_url}")
                    else:
                        logger.warning(f"Trust analysis failed for {website_url}: {trust_result.get('error')}")
                        analysis_result["scores"]["trust"] = 0.0
                    
                    # CRO analysis
                    cro_result = await self.pingdom_service.analyze_cro_metrics(
                        website_url, business_id, run_id
                    )
                    
                    if cro_result.get("success", False):
                        analysis_result["details"]["cro"] = cro_result
                        analysis_result["scores"]["cro"] = cro_result.get("cro_score", 0.0)
                        analysis_result["services_used"].append("pingdom_cro")
                        logger.info(f"CRO analysis completed for {website_url}")
                    else:
                        logger.warning(f"CRO analysis failed for {website_url}: {cro_result.get('error')}")
                        analysis_result["scores"]["cro"] = 0.0
                        
                except Exception as e:
                    logger.error(f"Pingdom analysis error for {website_url}: {e}")
                    analysis_result["scores"]["trust"] = 0.0
                    analysis_result["scores"]["cro"] = 0.0
            else:
                # Set default scores if Pingdom is not included
                analysis_result["scores"]["trust"] = 0.0
                analysis_result["scores"]["cro"] = 0.0
            
            # 3. Calculate overall score
            overall_score = self._calculate_overall_score(analysis_result["scores"])
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
        Run hybrid audit using PageSpeed's hybrid method.
        
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
            
            result = await self.pagespeed_service.run_hybrid_audit(
                website_url, business_id, run_id, strategy, self.pingdom_service
            )
            
            # Add service metadata
            result["services_used"] = ["pagespeed_hybrid", "pingdom"]
            result["scoring_method"] = "hybrid_pagespeed_pingdom"
            
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
        max_concurrent: int = 3,
        include_pingdom: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run comprehensive analysis on multiple websites concurrently.
        
        Args:
            analysis_requests: List of analysis request dictionaries
            max_concurrent: Maximum concurrent analyses
            include_pingdom: Whether to include Pingdom analysis
            
        Returns:
            List of analysis results
        """
        import asyncio
        from asyncio import Semaphore
        
        semaphore = Semaphore(max_concurrent)
        
        async def run_single_analysis(request: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self.run_comprehensive_analysis(
                    website_url=request['website_url'],
                    business_id=request['business_id'],
                    run_id=request.get('run_id'),
                    strategy=request.get('strategy', 'mobile'),
                    include_pingdom=include_pingdom
                )
        
        # Run all analyses concurrently
        tasks = [run_single_analysis(request) for request in analysis_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions and convert to error responses
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": f"Analysis failed: {str(result)}",
                    "error_code": "BATCH_ANALYSIS_FAILED",
                    "context": "batch_comprehensive_analysis",
                    "website_url": analysis_requests[i]['website_url'],
                    "business_id": analysis_requests[i]['business_id'],
                    "run_id": analysis_requests[i].get('run_id')
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate overall score with business impact weighting.
        Based on best practices from temp_place_z implementation.
        """
        try:
            # Business impact weighting (what matters most for conversions)
            weights = {
                'performance': 0.25,      # Speed affects user experience and SEO
                'accessibility': 0.15,    # Legal compliance and user inclusivity
                'best_practices': 0.15,   # Security and reliability
                'seo': 0.15,              # Search engine visibility
                'trust': 0.20,            # Critical for business credibility
                'cro': 0.10               # Revenue optimization
            }
            
            overall_score = 0.0
            total_weight = 0.0
            
            for metric, weight in weights.items():
                if metric in scores and scores[metric] is not None:
                    overall_score += scores[metric] * weight
                    total_weight += weight
            
            # Normalize score if some metrics are missing
            if total_weight > 0:
                final_score = overall_score / total_weight
            else:
                final_score = 0.0
            
            return round(final_score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating overall score: {e}")
            return 0.0
    
    def _update_service_health(self):
        """Update service health status."""
        try:
            # Check PageSpeed service health
            pagespeed_health = self.pagespeed_service.get_service_health()
            self.service_health["pagespeed"] = pagespeed_health.get("status", "unknown")
            
            # Check Pingdom service health
            pingdom_health = self.pingdom_service.get_service_health()
            self.service_health["pingdom"] = pingdom_health.get("status", "unknown")
            
            # Determine overall health
            if (self.service_health["pagespeed"] == "healthy" and 
                self.service_health["pingdom"] == "healthy"):
                self.service_health["overall"] = "healthy"
            elif (self.service_health["pagespeed"] == "healthy" or 
                  self.service_health["pingdom"] == "healthy"):
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
                "pagespeed": self.service_health["pagespeed"],
                "pingdom": self.service_health["pingdom"]
            },
            "rate_limits": {
                "comprehensive_speed": getattr(self.api_config, 'COMPREHENSIVE_SPEED_RATE_LIMIT_PER_MINUTE', 30)
            },
            "features": {
                "smart_retry": True,
                "intelligent_caching": True,
                "hybrid_scoring": True,
                "pingdom_integration": True,
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
                "best_practices": sum([r.get("scores", {}).get("best_practices", 0) for r in successful_results]) / total_websites,
                "seo": sum([r.get("scores", {}).get("seo", 0) for r in successful_results]) / total_websites,
                "trust": sum([r.get("scores", {}).get("trust", 0) for r in successful_results]) / total_websites,
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
                        "trust_score": r.get("scores", {}).get("trust", 0)
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
            
            # Trust insights
            trust_scores = [r.get("scores", {}).get("trust", 0) for r in results]
            avg_trust = sum(trust_scores) / len(trust_scores)
            
            if avg_trust < 60:
                insights.append("Low trust scores indicate security/credibility issues")
            elif avg_trust >= 80:
                insights.append("High trust scores show good security practices")
            
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
