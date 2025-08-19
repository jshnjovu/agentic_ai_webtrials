from typing import Dict, List, Optional, Tuple, Any
import statistics
import time
from dataclasses import dataclass
from enum import Enum

from ..core.base_service import BaseService
from ..models.website_scoring import WebsiteScore
from ..schemas.website_scoring import ScoreValidationResult, ValidationMetrics, IssuePriority, IssuePriorityDetails, IssueCategory, FinalScore


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IssueCategory(str, Enum):
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    SEO = "seo"
    BEST_PRACTICES = "best_practices"
    TECHNICAL = "technical"


@dataclass
class ScoreData:
    lighthouse_score: float
    comprehensive_score: float
    category: str
    weight: float = 1.0


class ScoreValidationService(BaseService):
    """
    Service for validating website scores and calculating confidence levels.
    Extends BaseService for consistent logging and error handling.
    """
    
    def __init__(self):
        super().__init__("ScoreValidationService")
        # Default weights: Lighthouse 80%, Comprehensive 20%
        self.lighthouse_weight = 0.8
        self.comprehensive_weight = 0.2
        self.confidence_thresholds = {
            "high": 0.8,
            "medium": 0.6,
            "low": 0.0
        }
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        try:
            if not isinstance(data, dict):
                return False
            
            required_fields = ['business_id', 'run_id', 'lighthouse_scores', 'comprehensive_scores']
            for field in required_fields:
                if field not in data:
                    return False
            
            # Validate business_id and run_id are strings
            if not isinstance(data['business_id'], str) or not isinstance(data['run_id'], str):
                return False
            
            # Validate scores are lists
            if not isinstance(data['lighthouse_scores'], list) or not isinstance(data['comprehensive_scores'], list):
                return False
            
            return True
            
        except Exception:
            return False
    
    async def validate_scores(
        self,
        lighthouse_scores: List[WebsiteScore],
        comprehensive_scores: List[dict],
        business_id: str,
        run_id: str
    ) -> ScoreValidationResult:
        """
        Main validation method that orchestrates the entire validation process.
        
        Args:
            lighthouse_scores: List of Lighthouse scoring results
            comprehensive_scores: List of comprehensive scoring results
            business_id: Business identifier
            run_id: Processing run identifier
            
        Returns:
            ScoreValidationResult with validation outcomes and confidence metrics
        """
        try:
            self.log_operation("Starting score validation", run_id, business_id)
            
            # Step 1: Score consistency checking
            consistency_result = self._check_score_consistency(lighthouse_scores, comprehensive_scores)
            
            # Step 2: Calculate confidence level
            confidence_level = self._calculate_confidence_level(consistency_result)
            
            # Step 3: Detect discrepancies
            discrepancies = self._detect_discrepancies(lighthouse_scores, comprehensive_scores)
            
            # Step 4: Calculate weighted final score
            final_score = self._calculate_weighted_final_score(lighthouse_scores, comprehensive_scores)
            
            # Step 5: Create issue prioritization
            issue_priorities = self._create_issue_priorities(discrepancies, consistency_result)
            
            # Create validation metrics
            validation_metrics = ValidationMetrics(
                correlation_coefficient=consistency_result["correlation"],
                statistical_significance=consistency_result["significance"],
                variance_analysis=consistency_result["variance"],
                reliability_indicator=consistency_result["reliability"],
                sample_size=max(len(lighthouse_scores), 1),  # Ensure minimum sample size of 1
                confidence_interval=(0.95, 0.99)  # 95% confidence interval
            )
            
            # Create final score
            final_score_model = FinalScore(
                business_id=business_id,
                run_id=run_id,
                weighted_final_score=final_score,
                confidence_level=confidence_level,
                lighthouse_weight=0.8,
                comprehensive_weight=0.2,
                discrepancy_flags=[],
                issue_priorities=issue_priorities,
                validation_status="completed",
                calculation_timestamp=time.time()
            )
            
            result = ScoreValidationResult(
                business_id=business_id,
                run_id=run_id,
                validation_timestamp=time.time(),
                confidence_level=confidence_level,
                score_correlation=consistency_result["correlation"],
                discrepancy_count=len(discrepancies),
                validation_metrics=validation_metrics,
                issue_priorities=issue_priorities,
                final_weighted_score=final_score,
                validation_status="completed"
            )
            
            self.log_operation("Score validation completed", run_id, business_id, confidence_level=confidence_level)
            return result
            
        except Exception as e:
            self.log_error(e, "score validation", run_id, business_id)
            raise
    
    def _check_score_consistency(
        self,
        lighthouse_scores: List[WebsiteScore],
        comprehensive_scores: List[dict]
    ) -> Dict:
        """
        Check consistency between Lighthouse and comprehensive scores.
        
        Returns:
            Dictionary with correlation, significance, variance, and reliability metrics
        """
        try:
            # Extract scores for correlation analysis
            lighthouse_values = [score.overall_score if hasattr(score, 'overall_score') else score.overall for score in lighthouse_scores]
            comprehensive_values = [score.get('overall_score', 0.0) for score in comprehensive_scores]
            
            if not lighthouse_values or not comprehensive_values:
                return {
                    "correlation": 0.0,
                    "significance": 0.0,
                    "variance": 0.0,
                    "reliability": 0.0
                }
            
            # Calculate Pearson correlation coefficient
            correlation = self._calculate_pearson_correlation(lighthouse_values, comprehensive_values)
            
            # Calculate statistical significance (simplified approach)
            significance = self._calculate_statistical_significance(correlation, len(lighthouse_values))
            
            # Calculate variance analysis
            variance = self._calculate_variance_analysis(lighthouse_values, comprehensive_values)
            
            # Calculate reliability indicator
            reliability = self._calculate_reliability_indicator(correlation, significance, variance)
            
            return {
                "correlation": correlation,
                "significance": significance,
                "variance": variance,
                "reliability": reliability
            }
            
        except Exception as e:
            self.log_error(e, "score consistency check")
            return {
                "correlation": 0.0,
                "significance": 0.0,
                "variance": 0.0,
                "reliability": 0.0
            }
    
    def _calculate_pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient between two lists of scores."""
        try:
            if len(x) != len(y) or len(x) < 2:
                return 0.0
            
            n = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xy = sum(x[i] * y[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            sum_y2 = sum(y[i] ** 2 for i in range(n))
            
            numerator = n * sum_xy - sum_x * sum_y
            denominator = ((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2)) ** 0.5
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return max(-1.0, min(1.0, correlation))  # Clamp between -1 and 1
            
        except Exception as e:
            self.log_error(e, "Pearson correlation calculation")
            return 0.0
    
    def _calculate_statistical_significance(self, correlation: float, sample_size: int) -> float:
        """Calculate statistical significance of correlation coefficient."""
        try:
            if sample_size < 3:
                return 0.0
            
            # Simplified t-test for correlation significance
            t_stat = correlation * ((sample_size - 2) / (1 - correlation ** 2)) ** 0.5
            
            # Convert to significance level (simplified)
            if abs(t_stat) > 2.0:
                return 0.95  # High significance
            elif abs(t_stat) > 1.5:
                return 0.80  # Medium significance
            else:
                return 0.50  # Low significance
                
        except Exception as e:
            self.log_error(e, "statistical significance calculation")
            return 0.0
    
    def _calculate_variance_analysis(self, x: List[float], y: List[float]) -> float:
        """Calculate variance analysis between two score sets."""
        try:
            if not x or not y:
                return 0.0
            
            # Calculate coefficient of variation for both sets
            x_cv = statistics.stdev(x) / statistics.mean(x) if statistics.mean(x) != 0 else 0
            y_cv = statistics.stdev(y) / statistics.mean(y) if statistics.mean(y) != 0 else 0
            
            # Return average coefficient of variation
            return (x_cv + y_cv) / 2
            
        except Exception as e:
            self.log_error(e, "variance analysis calculation")
            return 0.0
    
    def _calculate_reliability_indicator(self, correlation: float, significance: float, variance: float) -> float:
        """Calculate overall reliability indicator based on multiple metrics."""
        try:
            # Normalize correlation to 0-1 range
            correlation_norm = (correlation + 1) / 2
            
            # Combine metrics with weights
            reliability = (
                correlation_norm * 0.4 +
                significance * 0.3 +
                (1 - min(variance, 1.0)) * 0.3  # Lower variance = higher reliability
            )
            
            return max(0.0, min(1.0, reliability))
            
        except Exception as e:
            self.log_error(e, "reliability indicator calculation")
            return 0.0
    
    def _calculate_confidence_level(self, consistency_result: Dict) -> ConfidenceLevel:
        """Calculate confidence level based on consistency metrics."""
        try:
            reliability = consistency_result.get("reliability", 0.0)
            
            if reliability >= self.confidence_thresholds["high"]:
                return ConfidenceLevel.HIGH
            elif reliability >= self.confidence_thresholds["medium"]:
                return ConfidenceLevel.MEDIUM
            else:
                return ConfidenceLevel.LOW
                
        except Exception as e:
            self.log_error(e, "confidence level calculation")
            return ConfidenceLevel.LOW
    
    def _detect_discrepancies(
        self,
        lighthouse_scores: List[WebsiteScore],
        comprehensive_scores: List[dict]
    ) -> List[Dict]:
        """Detect discrepancies between Lighthouse and comprehensive scores."""
        try:
            discrepancies = []
            
            # Create lookup dictionaries for easy comparison
            # Handle both database models and schema classes
            lighthouse_lookup = {}
            for score in lighthouse_scores:
                if hasattr(score, 'website_url'):
                    key = score.website_url
                else:
                    key = "default"  # Use default key for schema classes
                lighthouse_lookup[key] = score.overall_score if hasattr(score, 'overall_score') else score.overall
            
            comprehensive_lookup = {}
            for score in comprehensive_scores:
                if hasattr(score, 'website_url'):
                    key = score.website_url
                else:
                    key = "default"  # Use default key for schema classes
                comprehensive_lookup[key] = score.get('overall_score', 0.0)
            
            # Check for score differences
            for key in set(lighthouse_lookup.keys()) | set(comprehensive_lookup.keys()):
                lighthouse_score = lighthouse_lookup.get(key, 0.0)
                comprehensive_score = comprehensive_lookup.get(key, 0.0)
                
                # Calculate difference
                difference = abs(lighthouse_score - comprehensive_score)
                
                # Flag as discrepancy if difference > 20 points
                if difference > 20.0:
                    discrepancies.append({
                        "category": "overall",
                        "lighthouse_score": lighthouse_score,
                        "comprehensive_score": comprehensive_score,
                        "difference": difference,
                        "severity": "high" if difference > 40.0 else "medium"
                    })
            
            return discrepancies
            
        except Exception as e:
            self.log_error(e, "discrepancy detection")
            return []
    
    def _calculate_weighted_final_score(
        self,
        lighthouse_scores: List[WebsiteScore],
        comprehensive_scores: List[dict]
    ) -> float:
        """Calculate weighted final score combining both scoring methods."""
        try:
            if not lighthouse_scores and not comprehensive_scores:
                return 0.0
            
            # Calculate average scores
            lighthouse_avg = (
                statistics.mean([score.overall_score if hasattr(score, 'overall_score') else score.overall for score in lighthouse_scores])
                if lighthouse_scores else 0.0
            )
            comprehensive_avg = (
                statistics.mean([score.get('overall_score', 0.0) for score in comprehensive_scores])
                if comprehensive_scores else 0.0
            )
            
            # Apply weights
            weighted_score = (
                lighthouse_avg * self.lighthouse_weight +
                comprehensive_avg * self.comprehensive_weight
            )
            
            return max(0.0, min(100.0, weighted_score))
            
        except Exception as e:
            self.log_error(e, "weighted final score calculation")
            return 0.0
    
    def _create_issue_priorities(
        self,
        discrepancies: List[Dict],
        consistency_result: Dict
    ) -> List[IssuePriorityDetails]:
        """Create prioritized list of issues based on discrepancies and consistency."""
        try:
            priorities = []
            
            # Add discrepancy-based issues
            for discrepancy in discrepancies:
                priority_level = self._determine_priority_level(discrepancy["severity"])
                
                priority = IssuePriorityDetails(
                    priority=IssuePriority(priority_level),
                    category=IssueCategory(discrepancy["category"]),
                    business_impact_score=self._calculate_business_impact(discrepancy),
                    recommended_action=self._get_recommended_action(discrepancy),
                    estimated_effort="medium",
                    dependencies=[]
                )
                priorities.append(priority)
            
            # Add consistency-based issues if confidence is low
            if consistency_result.get("reliability", 1.0) < 0.5:
                priority = IssuePriorityDetails(
                    priority=IssuePriority.HIGH,
                    category=IssueCategory.TECHNICAL,
                    business_impact_score=0.8,
                    recommended_action="Manual review required due to low confidence",
                    estimated_effort="high",
                    dependencies=[]
                )
                priorities.append(priority)
            
            # Sort by priority level
            priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            priorities.sort(key=lambda x: priority_order.get(x.priority.value, 4))
            
            return priorities
            
        except Exception as e:
            self.log_error(e, "issue priorities creation")
            return []
    
    def _determine_priority_level(self, severity: str) -> str:
        """Determine priority level based on severity."""
        if severity == "high":
            return "high"
        elif severity == "medium":
            return "medium"
        else:
            return "low"
    
    def _calculate_business_impact(self, discrepancy: Dict) -> float:
        """Calculate business impact score for a discrepancy."""
        try:
            # Base impact on difference magnitude
            difference = discrepancy.get("difference", 0.0)
            
            if difference > 40.0:
                return 0.9  # High impact
            elif difference > 20.0:
                return 0.6  # Medium impact
            else:
                return 0.3  # Low impact
                
        except Exception as e:
            self.log_error(e, "business impact calculation")
            return 0.5
    
    def _get_recommended_action(self, discrepancy: Dict) -> str:
        """Get recommended action for a discrepancy."""
        difference = discrepancy.get("difference", 0.0)
        
        if difference > 40.0:
            return "Immediate investigation required"
        elif difference > 20.0:
            return "Review and validate scoring methodology"
        else:
            return "Monitor for trends"
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()
