"""
Fallback scoring service for when Lighthouse API fails.
Provides comprehensive speed analysis scoring with automatic fallback detection and retry logic.
"""

import time
import asyncio
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core.base_service import BaseService
from src.core.config import get_api_config
from src.services.rate_limiter import RateLimiter
from src.services.comprehensive_speed_service import ComprehensiveSpeedService
from src.schemas.website_scoring import (
    FallbackScore, FallbackReason, FallbackReasonDetails, FallbackMetrics, FallbackHistory, FallbackQuality, FallbackQualityDetails,
    ConfidenceLevel, FallbackScoringRequest, FallbackScoringResponse, FallbackScoringError
)


class FailureSeverity(str, Enum):
    """Severity levels for Lighthouse failures."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FallbackDecision(str, Enum):
    """Fallback decision types."""
    IMMEDIATE_FALLBACK = "immediate_fallback"
    RETRY_THEN_FALLBACK = "retry_then_fallback"
    NO_FALLBACK = "no_fallback"


class FallbackScoringService(BaseService):
    """Service for fallback scoring when Lighthouse fails."""
    
    def __init__(self):
        super().__init__("FallbackScoringService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.comprehensive_service = ComprehensiveSpeedService()
        
        # Fallback configuration
        self.max_retry_attempts = 3
        self.retry_delay_base = 1.0
        self.fallback_timeout = 10  # seconds
        self.quality_threshold = 70.0  # minimum quality score for fallback
        
        # Failure pattern recognition
        self.failure_patterns = {
            "TIMEOUT": {
                "severity": FailureSeverity.MEDIUM,
                "decision": FallbackDecision.RETRY_THEN_FALLBACK,
                "retry_count": 2
            },
            "RATE_LIMIT_EXCEEDED": {
                "severity": FailureSeverity.HIGH,
                "decision": FallbackDecision.IMMEDIATE_FALLBACK,
                "retry_count": 0
            },
            "API_ERROR": {
                "severity": FailureSeverity.MEDIUM,
                "decision": FallbackDecision.RETRY_THEN_FALLBACK,
                "retry_count": 2
            },
            "NETWORK_ERROR": {
                "severity": FailureSeverity.LOW,
                "decision": FallbackDecision.RETRY_THEN_FALLBACK,
                "retry_count": 3
            },
            "INVALID_URL": {
                "severity": FailureSeverity.CRITICAL,
                "decision": FallbackDecision.NO_FALLBACK,
                "retry_count": 0
            },
            "UNKNOWN_ERROR": {
                "severity": FailureSeverity.MEDIUM,
                "decision": FallbackDecision.RETRY_THEN_FALLBACK,
                "retry_count": 1
            }
        }
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if not isinstance(data, dict):
            return False
        
        # Accept either pagespeed_failure_reason or lighthouse_failure_reason
        required_fields = ['website_url', 'business_id']
        if not all(field in data for field in required_fields):
            return False
        
        # Must have at least one failure reason
        failure_reasons = ['pagespeed_failure_reason', 'lighthouse_failure_reason']
        return any(reason in data for reason in failure_reasons)
    
    async def run_fallback_scoring(
        self,
        website_url: str,
        business_id: str,
        pagespeed_failure_reason: str,
        run_id: Optional[str] = None,
        fallback_parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run fallback scoring when PageSpeed fails.
        
        Args:
            website_url: URL of the website to score
            business_id: Business identifier for tracking
            pagespeed_failure_reason: Reason why PageSpeed failed
            run_id: Run identifier for tracking
            fallback_parameters: Additional fallback parameters
            
        Returns:
            Dictionary containing fallback scoring results
        """
        start_time = time.time()
        
        try:
            self.log_operation(
                "Starting fallback scoring",
                run_id=run_id,
                business_id=business_id,
                website_url=website_url,
                failure_reason=pagespeed_failure_reason
            )
            
            # Check rate limiting
            can_proceed, message = self.rate_limiter.can_make_request("fallback", run_id)
            if not can_proceed:
                return self._create_error_response(
                    f"Rate limit exceeded: {message}",
                    "rate_limit_check",
                    website_url,
                    business_id,
                    run_id
                )
            
            # Analyze failure and determine fallback strategy
            failure_analysis = self._analyze_failure(pagespeed_failure_reason)
            
            # Execute fallback strategy
            if failure_analysis["decision"] == FallbackDecision.NO_FALLBACK:
                return self._create_error_response(
                    f"Fallback not recommended for {failure_analysis['severity']} severity failure",
                    "fallback_strategy",
                    website_url,
                    business_id,
                    run_id
                )
            
            # Execute retry logic if needed
            retry_attempts = 0
            if failure_analysis["decision"] == FallbackDecision.RETRY_THEN_FALLBACK:
                retry_attempts = self._execute_retry_logic(
                    website_url, business_id, run_id, failure_analysis
                )
            
            # Run comprehensive speed analysis for fallback scoring
            comprehensive_result = await self._run_comprehensive_analysis(
                website_url, business_id, run_id
            )
            
            if not comprehensive_result["success"]:
                return self._create_error_response(
                    f"Comprehensive speed analysis failed: {comprehensive_result.get('error', 'Unknown error')}",
                    "comprehensive_analysis",
                    website_url,
                    business_id,
                    run_id
                )
            
            # Create fallback score with reduced confidence
            fallback_score = self._create_fallback_score(
                comprehensive_result, pagespeed_failure_reason, run_id, business_id, website_url
            )
            
            # Create fallback reason tracking
            fallback_reason = self._create_fallback_reason(
                pagespeed_failure_reason, failure_analysis, retry_attempts, True
            )
            
            # Assess fallback quality
            fallback_quality = self._assess_fallback_quality(
                fallback_score, comprehensive_result, failure_analysis
            )
            
            # Record successful request
            self.rate_limiter.record_request("fallback", True, run_id)
            
            execution_time = time.time() - start_time
            self.log_operation(
                f"Completed fallback scoring in {execution_time:.2f}s",
                run_id=run_id,
                business_id=business_id,
                execution_time=execution_time,
                fallback_quality=fallback_quality.reliability_score
            )
            
            return {
                "success": True,
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id,
                "fallback_timestamp": time.time(),
                "fallback_score": fallback_score,
                "fallback_reason": fallback_reason,
                "fallback_quality": fallback_quality,
                "retry_attempts": retry_attempts,
                "execution_time": execution_time
            }
            
        except Exception as e:
            # Record failed request
            self.rate_limiter.record_request("fallback", False, run_id)
            
            self.log_error(e, "fallback_scoring", run_id, business_id)
            
            return self._create_error_response(
                str(e),
                "fallback_scoring",
                website_url,
                business_id,
                run_id
            )
    
    def _analyze_failure(self, failure_reason: str) -> Dict[str, Any]:
        """Analyze Lighthouse failure and determine fallback strategy."""
        try:
            # Extract failure type from reason
            failure_type = self._extract_failure_type(failure_reason)
            
            # Get pattern for this failure type
            pattern = self.failure_patterns.get(failure_type, self.failure_patterns["UNKNOWN_ERROR"])
            
            return {
                "failure_type": failure_type,
                "severity": pattern["severity"],
                "decision": pattern["decision"],
                "retry_count": pattern["retry_count"],
                "original_reason": failure_reason
            }
            
        except Exception as e:
            self.log_error(e, "failure_analysis")
            return self.failure_patterns["UNKNOWN_ERROR"]
    
    def _extract_failure_type(self, failure_reason: str) -> str:
        """Extract failure type from failure reason string."""
        failure_reason_lower = failure_reason.lower()
        
        if "timeout" in failure_reason_lower or "timed out" in failure_reason_lower:
            return "TIMEOUT"
        elif "rate limit" in failure_reason_lower or "quota" in failure_reason_lower:
            return "RATE_LIMIT_EXCEEDED"
        elif "api" in failure_reason_lower and "error" in failure_reason_lower:
            return "API_ERROR"
        elif "network" in failure_reason_lower or "connection" in failure_reason_lower:
            return "NETWORK_ERROR"
        elif "invalid" in failure_reason_lower and "url" in failure_reason_lower:
            return "INVALID_URL"
        else:
            return "UNKNOWN_ERROR"
    
    def _execute_retry_logic(
        self,
        website_url: str,
        business_id: str,
        run_id: Optional[str],
        failure_analysis: Dict[str, Any]
    ) -> int:
        """Execute retry logic for temporary failures."""
        max_retries = failure_analysis["retry_count"]
        retry_attempts = 0
        
        self.log_operation(
            f"Executing retry logic for {max_retries} attempts",
            run_id=run_id,
            business_id=business_id,
            failure_type=failure_analysis["failure_type"]
        )
        
        for attempt in range(max_retries):
            try:
                retry_attempts += 1
                
                # Calculate delay with exponential backoff
                delay = self.retry_delay_base * (2 ** attempt)
                
                self.log_operation(
                    f"Retry attempt {retry_attempts}/{max_retries} with {delay}s delay",
                    run_id=run_id,
                    business_id=business_id,
                    attempt=retry_attempts
                )
                
                # Wait before retry
                time.sleep(delay)
                
                # Attempt to recover (this would typically try Lighthouse again)
                # For now, we'll simulate a recovery attempt
                recovery_successful = self._attempt_lighthouse_recovery(
                    website_url, business_id, run_id
                )
                
                if recovery_successful:
                    self.log_operation(
                        f"Recovery successful on attempt {retry_attempts}",
                        run_id=run_id,
                        business_id=business_id
                    )
                    return retry_attempts
                
            except Exception as e:
                self.log_error(e, f"retry_attempt_{retry_attempts}", run_id, business_id)
                continue
        
        self.log_operation(
            f"All {max_retries} retry attempts failed, proceeding with fallback",
            run_id=run_id,
            business_id=business_id
        )
        
        return retry_attempts
    
    def _attempt_lighthouse_recovery(
        self,
        website_url: str,
        business_id: str,
        run_id: Optional[str]
    ) -> bool:
        """Attempt to recover Lighthouse functionality."""
        try:
            # This would typically attempt a lightweight Lighthouse check
            # For now, we'll simulate a recovery attempt that usually fails
            # In a real implementation, this might try a different Lighthouse endpoint
            # or check if the service is back online
            
            # Simulate recovery attempt (usually fails in fallback scenarios)
            recovery_successful = False
            
            self.log_operation(
                f"Lighthouse recovery attempt {'successful' if recovery_successful else 'failed'}",
                run_id=run_id,
                business_id=business_id
            )
            
            return recovery_successful
            
        except Exception as e:
            self.log_error(e, "lighthouse_recovery_attempt", run_id, business_id)
            return False
    
    async def _run_comprehensive_analysis(
        self,
        website_url: str,
        business_id: str,
        run_id: Optional[str]
    ) -> Dict[str, Any]:
        """Run comprehensive speed analysis for fallback scoring."""
        try:
            self.log_operation(
                "Running comprehensive speed analysis for fallback scoring",
                run_id=run_id,
                business_id=business_id,
                website_url=website_url
            )
            
            # Use the comprehensive speed service
            result = await self.comprehensive_service.run_comprehensive_analysis(
                website_url, business_id, run_id
            )
            
            return result
            
        except Exception as e:
            self.log_error(e, "comprehensive_analysis", run_id, business_id)
            return {
                "success": False,
                "error": str(e),
                "context": "comprehensive_analysis"
            }
    
    def _create_fallback_score(
        self,
        comprehensive_result: Dict[str, Any],
        fallback_reason: str,
        run_id: Optional[str],
        business_id: str = "unknown",
        website_url: str = "unknown"
    ) -> FallbackScore:
        """Create fallback score with reduced confidence."""
        try:
            scores = comprehensive_result.get("scores", {})
            
            # Create fallback scores dictionary
            fallback_scores = {
                "pingdom_trust": scores.get("pingdom_trust", 0.0),
                "pingdom_cro": scores.get("pingdom_cro", 0.0),
                "pagespeed_performance": scores.get("pagespeed_performance", 0.0),
                "pagespeed_accessibility": scores.get("pagespeed_accessibility", 0.0),
                "pagespeed_best_practices": scores.get("pagespeed_best_practices", 0.0),
                "pagespeed_seo": scores.get("pagespeed_seo", 0.0),
                "overall_score": scores.get("overall_score", 0.0)
            }
            
            # Create quality metrics
            quality_metrics = FallbackMetrics(
                # Quality assessment fields
                data_completeness=self._calculate_data_completeness(comprehensive_result),
                source_reliability=0.7,  # Reduced reliability for fallback
                confidence_score=0.6,    # Reduced confidence for fallback
                fallback_reason=FallbackReason.TIMEOUT,  # Default to timeout
                quality_rating=FallbackQuality.FAIR,
                # Performance tracking fields
                fallback_success_rate=75.0,  # Default fallback success rate
                average_fallback_score_quality=70.0,  # Default quality
                failure_pattern_analysis={"TIMEOUT": 1},  # Default pattern
                performance_metrics={"execution_time": 2.5},  # Default metrics
                total_fallbacks=1,  # Default count
                successful_fallbacks=1  # Default count
            )
    
            # Create fallback score with proper schema structure
            fallback_score = FallbackScore(
                business_id=business_id,
                run_id=run_id or "unknown",
                website_url=website_url,
                fallback_timestamp=time.time(),
                fallback_reason=FallbackReason.TIMEOUT,  # Convert string to enum
                fallback_scores=fallback_scores,
                quality_metrics=quality_metrics,
                confidence_level=ConfidenceLevel.LOW,  # Reduced confidence for fallback
                notes=f"Fallback scoring due to: {fallback_reason}",
                fallback_history=[]
            )
    
            return fallback_score
            
        except Exception as e:
            self.log_error(e, "fallback_score_creation", run_id)
            # Return default fallback score on error
            return FallbackScore(
                business_id=business_id,
                run_id=run_id or "unknown",
                website_url=website_url,
                fallback_timestamp=time.time(),
                fallback_reason=FallbackReason.UNKNOWN_ERROR,
                fallback_scores={"overall_score": 0.0},
                quality_metrics=FallbackMetrics(
                    # Quality assessment fields
                    data_completeness=0.0,
                    source_reliability=0.0,
                    confidence_score=0.0,
                    fallback_reason=FallbackReason.UNKNOWN_ERROR,
                    quality_rating=FallbackQuality.UNRELIABLE,
                    # Performance tracking fields
                    fallback_success_rate=0.0,
                    average_fallback_score_quality=0.0,
                    failure_pattern_analysis={},
                    performance_metrics={},
                    total_fallbacks=0,
                    successful_fallbacks=0
                ),
                confidence_level=ConfidenceLevel.LOW,
                notes=f"Fallback scoring failed due to: {fallback_reason}",
                fallback_history=[]
            )
    
    def _create_fallback_reason(
        self,
        pagespeed_failure_reason: str,
        failure_analysis: Dict[str, Any],
        retry_attempts: int,
        success_status: bool
    ) -> FallbackReasonDetails:
        """Create fallback reason tracking."""
        try:
            fallback_reason = FallbackReasonDetails(
                failure_type=failure_analysis["failure_type"],
                error_message=pagespeed_failure_reason,
                severity_level=failure_analysis["severity"].value,
                fallback_decision=failure_analysis["decision"].value,
                retry_attempts=retry_attempts,
                success_status=success_status,
                fallback_timestamp=time.time()
            )
            
            return fallback_reason
            
        except Exception as e:
            self.log_error(e, "fallback_reason_creation")
            # Return default fallback reason on error
            return FallbackReasonDetails(
                failure_type="UNKNOWN_ERROR",
                error_message=pagespeed_failure_reason,
                severity_level="medium",
                fallback_decision="immediate_fallback",
                retry_attempts=retry_attempts,
                success_status=success_status,
                fallback_timestamp=time.time()
            )
    
    def _assess_fallback_quality(
        self,
        fallback_score: FallbackScore,
        comprehensive_result: Dict[str, Any],
        failure_analysis: Dict[str, Any]
    ) -> FallbackQualityDetails:
        """Assess the quality of fallback scoring results."""
        try:
            # Calculate reliability score based on data completeness
            data_completeness = self._calculate_data_completeness(comprehensive_result)
            
            # Calculate reliability score based on failure severity and data quality
            reliability_score = self._calculate_reliability_score(
                failure_analysis["severity"], data_completeness
            )
            
            # Calculate confidence adjustment factor
            confidence_adjustment = self._calculate_confidence_adjustment(
                failure_analysis["severity"], data_completeness
            )
            
            # Determine quality indicators
            quality_indicators = self._determine_quality_indicators(
                fallback_score, comprehensive_result, failure_analysis
            )
            
            # Generate recommendation
            recommendation = self._generate_quality_recommendation(
                reliability_score, data_completeness, failure_analysis
            )
            
            fallback_quality = FallbackQualityDetails(
                reliability_score=reliability_score,
                data_completeness=data_completeness,
                confidence_adjustment=confidence_adjustment,
                quality_indicators=quality_indicators,
                recommendation=recommendation
            )
            
            return fallback_quality
            
        except Exception as e:
            self.log_error(e, "fallback_quality_assessment")
            # Return default quality assessment on error
            return FallbackQualityDetails(
                reliability_score=0.0,
                data_completeness=0.0,
                confidence_adjustment=0.0,
                quality_indicators={},
                recommendation="Unable to assess quality due to error"
            )
    
    def _calculate_data_completeness(self, comprehensive_result: Dict[str, Any]) -> float:
        """Calculate completeness of comprehensive speed analysis data."""
        try:
            # Count available data points
            total_points = 0
            available_points = 0
            
            # Check PageSpeed data (4 main scores + core web vitals)
            pagespeed_data = comprehensive_result.get("pagespeed_data", {})
            pagespeed_fields = [
                "performance_score", "accessibility_score", "best_practices_score", "seo_score",
                "first_contentful_paint", "largest_contentful_paint", "cumulative_layout_shift",
                "total_blocking_time", "speed_index"
            ]
            for field in pagespeed_fields:
                total_points += 1
                if pagespeed_data.get(field) is not None:
                    available_points += 1
            
            # Check Pingdom data (6 fields)
            pingdom_data = comprehensive_result.get("pingdom_data", {})
            pingdom_fields = [
                "trust_score", "cro_score", "ssl_status", "response_time", "uptime", "security_headers"
            ]
            for field in pingdom_fields:
                total_points += 1
                if pingdom_data.get(field) is not None:
                    available_points += 1
            
            # Check overall scores (7 fields)
            scores = comprehensive_result.get("scores", {})
            score_fields = [
                "pagespeed_performance", "pagespeed_accessibility", "pagespeed_best_practices",
                "pagespeed_seo", "pingdom_trust", "pingdom_cro", "overall_score"
            ]
            for field in score_fields:
                total_points += 1
                if scores.get(field) is not None:
                    available_points += 1
            

            
            # Calculate completeness percentage
            if total_points > 0:
                return available_points / total_points
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    def _calculate_reliability_score(
        self,
        severity: FailureSeverity,
        data_completeness: float
    ) -> float:
        """Calculate reliability score based on failure severity and data completeness."""
        try:
            # Base reliability score
            base_score = 100.0
            
            # Severity penalties
            severity_penalties = {
                FailureSeverity.LOW: 10.0,
                FailureSeverity.MEDIUM: 25.0,
                FailureSeverity.HIGH: 40.0,
                FailureSeverity.CRITICAL: 60.0
            }
            
            # Data completeness penalties
            completeness_penalty = max(0, (100 - data_completeness) * 0.3)
            
            # Calculate final reliability score
            reliability_score = base_score - severity_penalties.get(severity, 25.0) - completeness_penalty
            
            return max(0.0, min(100.0, reliability_score))
            
        except Exception:
            return 50.0
    
    def _calculate_confidence_adjustment(
        self,
        severity: FailureSeverity,
        data_completeness: float
    ) -> float:
        """Calculate confidence adjustment factor."""
        try:
            # Base confidence adjustment
            base_adjustment = 1.0
            
            # Severity adjustments
            severity_adjustments = {
                FailureSeverity.LOW: 0.9,
                FailureSeverity.MEDIUM: 0.7,
                FailureSeverity.HIGH: 0.5,
                FailureSeverity.CRITICAL: 0.3
            }
            
            # Data completeness adjustments
            completeness_factor = data_completeness / 100.0
            
            # Calculate final adjustment
            adjustment = base_adjustment * severity_adjustments.get(severity, 0.7) * completeness_factor
            
            return max(0.1, min(1.0, adjustment))
            
        except Exception:
            return 0.5
    
    def _determine_quality_indicators(
        self,
        fallback_score: FallbackScore,
        comprehensive_result: Dict[str, Any],
        failure_analysis: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Determine quality indicators for fallback results."""
        try:
            indicators = {}
            
            # Check if scores are reasonable
            fallback_scores = fallback_score.fallback_scores
            indicators["scores_reasonable"] = (
                0 <= fallback_scores.get("overall_score", 0) <= 100 and
                all(0 <= score <= 100 for score in [
                    fallback_scores.get("pingdom_trust", 0),
                    fallback_scores.get("pingdom_cro", 0),
                    fallback_scores.get("pagespeed_performance", 0),
                    fallback_scores.get("pagespeed_accessibility", 0),
                    fallback_scores.get("pagespeed_best_practices", 0),
                    fallback_scores.get("pagespeed_seo", 0)
                ])
            )
            
            # Check if data is available
            indicators["data_available"] = bool(comprehensive_result.get("scores"))
            
            # Check if failure analysis is complete
            indicators["failure_analysis_complete"] = all(
                key in failure_analysis for key in ["severity", "decision", "retry_count"]
            )
            
            # Check if confidence level is appropriate
            indicators["confidence_appropriate"] = fallback_score.confidence_level == ConfidenceLevel.LOW
            
            return indicators
            
        except Exception:
            return {
                "scores_reasonable": False,
                "data_available": False,
                "failure_analysis_complete": False,
                "confidence_appropriate": False
            }
    
    def _generate_quality_recommendation(
        self,
        reliability_score: float,
        data_completeness: float,
        failure_analysis: Dict[str, Any]
    ) -> str:
        """Generate quality recommendation for fallback results."""
        try:
            if reliability_score >= 80:
                recommendation = "Fallback results are highly reliable and can be used with confidence."
            elif reliability_score >= 60:
                recommendation = "Fallback results are moderately reliable but should be used with caution."
            elif reliability_score >= 40:
                recommendation = "Fallback results have limited reliability and should be verified when possible."
            else:
                recommendation = "Fallback results have low reliability and should not be used for critical decisions."
            
            # Add data completeness note
            if data_completeness < 50:
                recommendation += " Limited data availability may affect result accuracy."
            
            # Add severity note
            if failure_analysis["severity"] in [FailureSeverity.HIGH, FailureSeverity.CRITICAL]:
                recommendation += " High severity failure suggests potential systemic issues."
            
            return recommendation
            
        except Exception:
            return "Unable to generate quality recommendation due to error."
    
    def _create_error_response(
        self,
        error: str,
        context: str,
        website_url: str,
        business_id: str,
        run_id: Optional[str]
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "success": False,
            "error": error,
            "context": context,
            "website_url": website_url,
            "business_id": business_id,
            "run_id": run_id,
            "fallback_timestamp": time.time(),
            "fallback_score": None,
            "fallback_reason": None,
            "fallback_quality": None,
            "retry_attempts": 0
        }
    
    def get_fallback_metrics(self) -> FallbackMetrics:
        """Get fallback performance metrics."""
        try:
            # This would typically query the database for metrics
            # For now, return placeholder metrics
            metrics = FallbackMetrics(
                # Quality assessment fields
                data_completeness=0.85,
                source_reliability=0.72,
                confidence_score=0.68,
                fallback_reason=FallbackReason.TIMEOUT,
                quality_rating=FallbackQuality.GOOD,
                # Performance tracking fields
                fallback_success_rate=85.0,
                average_fallback_score_quality=72.0,
                failure_pattern_analysis={
                    "TIMEOUT": 45,
                    "RATE_LIMIT_EXCEEDED": 25,
                    "API_ERROR": 20,
                    "NETWORK_ERROR": 10
                },
                performance_metrics={
                    "average_execution_time": 3.2,
                    "success_rate_trend": 2.1
                },
                total_fallbacks=120,
                successful_fallbacks=102
            )
            
            return metrics
            
        except Exception as e:
            self.log_error(e, "get_fallback_metrics")
            # Return default metrics on error
            return FallbackMetrics(
                # Quality assessment fields
                data_completeness=0.0,
                source_reliability=0.0,
                confidence_score=0.0,
                fallback_reason=FallbackReason.UNKNOWN_ERROR,
                quality_rating=FallbackQuality.UNRELIABLE,
                # Performance tracking fields
                fallback_success_rate=0.0,
                average_fallback_score_quality=0.0,
                failure_pattern_analysis={},
                performance_metrics={},
                total_fallbacks=0,
                successful_fallbacks=0
            )
