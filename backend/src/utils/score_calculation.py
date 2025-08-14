"""
Score calculation and normalization utilities for website scoring.
Provides functions for calculating overall scores and normalizing audit results.
"""

from typing import Dict, List, Tuple, Optional
from enum import Enum


class ScoreCategory(str, Enum):
    """Score categories for website performance."""
    PERFORMANCE = "performance"
    ACCESSIBILITY = "accessibility"
    BEST_PRACTICES = "best_practices"
    SEO = "seo"


class ScoreWeights:
    """Default weights for calculating overall website scores."""
    
    # Performance has highest weight as it's most critical for user experience
    PERFORMANCE = 0.40      # 40%
    ACCESSIBILITY = 0.25    # 25%
    BEST_PRACTICES = 0.20   # 20%
    SEO = 0.15             # 15%
    
    @classmethod
    def get_weights(cls) -> Dict[str, float]:
        """Get all score weights as a dictionary."""
        return {
            ScoreCategory.PERFORMANCE: cls.PERFORMANCE,
            ScoreCategory.ACCESSIBILITY: cls.ACCESSIBILITY,
            ScoreCategory.BEST_PRACTICES: cls.BEST_PRACTICES,
            ScoreCategory.SEO: cls.SEO
        }


def calculate_overall_score(scores: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
    """
    Calculate overall website score as weighted average of category scores.
    
    Args:
        scores: Dictionary of category scores (0-100 scale)
        weights: Optional custom weights dictionary, uses defaults if not provided
        
    Returns:
        Overall weighted score (0-100 scale)
        
    Raises:
        ValueError: If scores or weights are invalid
    """
    if not scores:
        raise ValueError("Scores dictionary cannot be empty")
    
    if weights is None:
        weights = ScoreWeights.get_weights()
    
    # Validate that all required categories are present
    required_categories = list(weights.keys())
    missing_categories = [cat for cat in required_categories if cat not in scores]
    
    if missing_categories:
        raise ValueError(f"Missing required score categories: {missing_categories}")
    
    # Calculate weighted average
    total_score = 0.0
    total_weight = 0.0
    
    for category, weight in weights.items():
        score = scores.get(category, 0.0)
        
        # Validate score range
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            raise ValueError(f"Invalid score for {category}: {score}. Must be 0-100.")
        
        total_score += score * weight
        total_weight += weight
    
    if total_weight == 0:
        raise ValueError("Total weight cannot be zero")
    
    return round(total_score / total_weight, 1)


def normalize_score(score: float, from_scale: Tuple[float, float] = (0, 1), 
                   to_scale: Tuple[float, float] = (0, 100)) -> float:
    """
    Normalize a score from one scale to another.
    
    Args:
        score: Original score value
        from_scale: Tuple of (min, max) for original scale
        to_scale: Tuple of (min, max) for target scale
        
    Returns:
        Normalized score in target scale
        
    Example:
        normalize_score(0.75, (0, 1), (0, 100)) -> 75.0
    """
    min_from, max_from = from_scale
    min_to, max_to = to_scale
    
    if max_from == min_from:
        raise ValueError("Source scale range cannot be zero")
    
    # Normalize to 0-1 range first
    normalized = (score - min_from) / (max_from - min_from)
    
    # Scale to target range
    result = normalized * (max_to - min_to) + min_to
    
    return round(result, 1)


def calculate_score_grade(score: float, thresholds: Optional[Dict[str, float]] = None) -> str:
    """
    Calculate letter grade based on score.
    
    Args:
        score: Score value (0-100 scale)
        thresholds: Optional custom grade thresholds
        
    Returns:
        Letter grade (A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F)
    """
    if thresholds is None:
        thresholds = {
            'A+': 97, 'A': 93, 'A-': 90,
            'B+': 87, 'B': 83, 'B-': 80,
            'C+': 77, 'C': 73, 'C-': 70,
            'D+': 67, 'D': 63, 'D-': 60,
            'F': 0
        }
    
    # Sort thresholds by score (descending)
    sorted_thresholds = sorted(thresholds.items(), key=lambda x: x[1], reverse=True)
    
    for grade, threshold in sorted_thresholds:
        if score >= threshold:
            return grade
    
    return 'F'


def calculate_performance_trend(scores: List[float]) -> Dict[str, float]:
    """
    Calculate performance trend from historical scores.
    
    Args:
        scores: List of historical scores (most recent last)
        
    Returns:
        Dictionary with trend metrics
    """
    if len(scores) < 2:
        return {
            'trend': 0.0,
            'improvement_rate': 0.0,
            'volatility': 0.0
        }
    
    # Calculate trend (positive = improving, negative = declining)
    trend = scores[-1] - scores[0]
    
    # Calculate improvement rate per period
    periods = len(scores) - 1
    improvement_rate = trend / periods if periods > 0 else 0
    
    # Calculate volatility (standard deviation)
    mean_score = sum(scores) / len(scores)
    variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
    volatility = variance ** 0.5
    
    return {
        'trend': round(trend, 2),
        'improvement_rate': round(improvement_rate, 2),
        'volatility': round(volatility, 2)
    }


def validate_score_thresholds(thresholds: Dict[str, float]) -> bool:
    """
    Validate that score thresholds are reasonable.
    
    Args:
        thresholds: Dictionary of category thresholds
        
    Returns:
        True if thresholds are valid, False otherwise
    """
    required_categories = ['performance', 'accessibility', 'best_practices', 'seo', 'overall']
    
    # Check that all required categories are present
    for category in required_categories:
        if category not in thresholds:
            return False
    
    # Check that thresholds are within valid range
    for category, threshold in thresholds.items():
        if not isinstance(threshold, (int, float)) or threshold < 0 or threshold > 100:
            return False
    
    # Check that overall threshold is reasonable given category thresholds
    category_thresholds = [
        thresholds.get('performance', 0),
        thresholds.get('accessibility', 0),
        thresholds.get('best_practices', 0),
        thresholds.get('seo', 0)
    ]
    
    min_category = min(category_thresholds)
    overall_threshold = thresholds.get('overall', 0)
    
    # Overall threshold should not be higher than the lowest category threshold
    if overall_threshold > min_category:
        return False
    
    return True


def get_score_insights(scores: Dict[str, float]) -> List[str]:
    """
    Generate insights based on website scores.
    
    Args:
        scores: Dictionary of category scores
        
    Returns:
        List of insight messages
    """
    insights = []
    
    # Calculate overall score if not provided
    if 'overall' not in scores:
        try:
            scores['overall'] = calculate_overall_score(scores)
        except (ValueError, KeyError):
            scores['overall'] = 0.0
    
    # Performance insights
    if scores.get('performance', 0) < 50:
        insights.append("Performance score is critically low - immediate optimization needed")
    elif scores.get('performance', 0) < 70:
        insights.append("Performance score needs improvement - consider optimization")
    
    # Accessibility insights
    if scores.get('accessibility', 0) < 80:
        insights.append("Accessibility score below recommended threshold - review WCAG compliance")
    
    # Best practices insights
    if scores.get('best_practices', 0) < 80:
        insights.append("Best practices score indicates room for improvement")
    
    # SEO insights
    if scores.get('seo', 0) < 80:
        insights.append("SEO score suggests optimization opportunities")
    
    # Overall insights
    overall = scores.get('overall', 0)
    if overall >= 90:
        insights.append("Excellent overall performance - maintain current standards")
    elif overall >= 80:
        insights.append("Good overall performance - minor optimizations may help")
    elif overall >= 70:
        insights.append("Acceptable performance - consider improvements for better user experience")
    else:
        insights.append("Performance needs significant improvement - prioritize optimization")
    
    return insights
