"""
Unit tests for score calculation utilities.
Tests website scoring calculation, normalization, and analysis functions.
"""

import pytest
from src.utils.score_calculation import (
    ScoreCategory, ScoreWeights, calculate_overall_score, normalize_score,
    calculate_score_grade, calculate_performance_trend, validate_score_thresholds,
    get_score_insights
)


class TestScoreCalculation:
    """Test cases for score calculation utilities."""
    
    def test_score_weights_defaults(self):
        """Test default score weights are correct."""
        weights = ScoreWeights.get_weights()
        
        assert weights[ScoreCategory.PERFORMANCE] == 0.40
        assert weights[ScoreCategory.ACCESSIBILITY] == 0.25
        assert weights[ScoreCategory.BEST_PRACTICES] == 0.20
        assert weights[ScoreCategory.SEO] == 0.15
        
        # Verify weights sum to 1.0
        assert sum(weights.values()) == 1.0
    
    def test_calculate_overall_score_valid(self):
        """Test overall score calculation with valid scores."""
        scores = {
            'performance': 85.0,
            'accessibility': 92.0,
            'best_practices': 88.0,
            'seo': 95.0
        }
        
        overall_score = calculate_overall_score(scores)
        
        # Expected: (85*0.4 + 92*0.25 + 88*0.2 + 95*0.15) = 89.5
        expected_score = (85 * 0.4 + 92 * 0.25 + 88 * 0.2 + 95 * 0.15)
        assert abs(overall_score - expected_score) < 0.1
    
    def test_calculate_overall_score_custom_weights(self):
        """Test overall score calculation with custom weights."""
        scores = {
            'performance': 80.0,
            'accessibility': 90.0,
            'best_practices': 85.0,
            'seo': 95.0
        }
        
        custom_weights = {
            'performance': 0.5,
            'accessibility': 0.3,
            'best_practices': 0.1,
            'seo': 0.1
        }
        
        overall_score = calculate_overall_score(scores, custom_weights)
        
        # Expected: (80*0.5 + 90*0.3 + 85*0.1 + 95*0.1) = 84.0
        expected_score = (80 * 0.5 + 90 * 0.3 + 85 * 0.1 + 95 * 0.1)
        assert abs(overall_score - expected_score) < 0.1
    
    def test_calculate_overall_score_empty_scores(self):
        """Test overall score calculation with empty scores."""
        with pytest.raises(ValueError, match="Scores dictionary cannot be empty"):
            calculate_overall_score({})
    
    def test_calculate_overall_score_missing_categories(self):
        """Test overall score calculation with missing categories."""
        scores = {
            'performance': 85.0,
            'accessibility': 92.0
            # Missing best_practices and seo
        }
        
        with pytest.raises(ValueError, match="Missing required score categories"):
            calculate_overall_score(scores)
    
    def test_calculate_overall_score_invalid_score_range(self):
        """Test overall score calculation with invalid score range."""
        scores = {
            'performance': 150.0,  # Invalid: > 100
            'accessibility': 92.0,
            'best_practices': 88.0,
            'seo': 95.0
        }
        
        with pytest.raises(ValueError, match="Invalid score for.*PERFORMANCE.*150\.0.*Must be 0-100"):
            calculate_overall_score(scores)
    
    def test_normalize_score_basic(self):
        """Test basic score normalization."""
        # Normalize from 0-1 scale to 0-100 scale
        normalized = normalize_score(0.75, (0, 1), (0, 100))
        assert normalized == 75.0
    
    def test_normalize_score_reverse_scale(self):
        """Test score normalization with reverse scale."""
        # Normalize from 100-0 scale to 0-100 scale
        normalized = normalize_score(25, (100, 0), (0, 100))
        assert normalized == 75.0
    
    def test_normalize_score_custom_range(self):
        """Test score normalization with custom range."""
        # Normalize from 0-10 scale to 0-100 scale
        normalized = normalize_score(7.5, (0, 10), (0, 100))
        assert normalized == 75.0
    
    def test_normalize_score_zero_range(self):
        """Test score normalization with zero range."""
        with pytest.raises(ValueError, match="Source scale range cannot be zero"):
            normalize_score(5, (0, 0), (0, 100))
    
    def test_calculate_score_grade_default_thresholds(self):
        """Test score grading with default thresholds."""
        assert calculate_score_grade(95) == "A"
        assert calculate_score_grade(87) == "B+"
        assert calculate_score_grade(75) == "C"
        assert calculate_score_grade(65) == "D"
        assert calculate_score_grade(45) == "F"
    
    def test_calculate_score_grade_custom_thresholds(self):
        """Test score grading with custom thresholds."""
        custom_thresholds = {
            'A': 90,
            'B': 80,
            'C': 70,
            'D': 60,
            'F': 0
        }
        
        assert calculate_score_grade(95, custom_thresholds) == "A"
        assert calculate_score_grade(85, custom_thresholds) == "B"
        assert calculate_score_grade(75, custom_thresholds) == "C"
        assert calculate_score_grade(65, custom_thresholds) == "D"
        assert calculate_score_grade(55, custom_thresholds) == "F"
    
    def test_calculate_performance_trend_improving(self):
        """Test performance trend calculation for improving scores."""
        scores = [70, 75, 80, 85, 90]
        trend_data = calculate_performance_trend(scores)
        
        assert trend_data['trend'] == 20.0  # 90 - 70
        assert trend_data['improvement_rate'] == 5.0  # 20 / 4 periods
        assert trend_data['volatility'] > 0
    
    def test_calculate_performance_trend_declining(self):
        """Test performance trend calculation for declining scores."""
        scores = [90, 85, 80, 75, 70]
        trend_data = calculate_performance_trend(scores)
        
        assert trend_data['trend'] == -20.0  # 70 - 90
        assert trend_data['improvement_rate'] == -5.0  # -20 / 4 periods
        assert trend_data['volatility'] > 0
    
    def test_calculate_performance_trend_single_score(self):
        """Test performance trend calculation with single score."""
        scores = [85]
        trend_data = calculate_performance_trend(scores)
        
        assert trend_data['trend'] == 0.0
        assert trend_data['improvement_rate'] == 0.0
        assert trend_data['volatility'] == 0.0
    
    def test_calculate_performance_trend_no_scores(self):
        """Test performance trend calculation with no scores."""
        scores = []
        trend_data = calculate_performance_trend(scores)
        
        assert trend_data['trend'] == 0.0
        assert trend_data['improvement_rate'] == 0.0
        assert trend_data['volatility'] == 0.0
    
    def test_validate_score_thresholds_valid(self):
        """Test threshold validation with valid thresholds."""
        valid_thresholds = {
            'performance': 70.0,
            'accessibility': 80.0,
            'best_practices': 80.0,
            'seo': 80.0,
            'overall': 70.0  # Should not be higher than lowest category (70)
        }
        
        assert validate_score_thresholds(valid_thresholds) is True
    
    def test_validate_score_thresholds_missing_categories(self):
        """Test threshold validation with missing categories."""
        invalid_thresholds = {
            'performance': 70.0,
            'accessibility': 80.0
            # Missing best_practices, seo, and overall
        }
        
        assert validate_score_thresholds(invalid_thresholds) is False
    
    def test_validate_score_thresholds_invalid_range(self):
        """Test threshold validation with invalid range."""
        invalid_thresholds = {
            'performance': 150.0,  # Invalid: > 100
            'accessibility': 80.0,
            'best_practices': 80.0,
            'seo': 80.0,
            'overall': 75.0
        }
        
        assert validate_score_thresholds(invalid_thresholds) is False
    
    def test_validate_score_thresholds_overall_too_high(self):
        """Test threshold validation with overall threshold too high."""
        invalid_thresholds = {
            'performance': 70.0,
            'accessibility': 80.0,
            'best_practices': 80.0,
            'seo': 80.0,
            'overall': 85.0  # Higher than lowest category (70)
        }
        
        assert validate_score_thresholds(invalid_thresholds) is False
    
    def test_get_score_insights_performance_low(self):
        """Test score insights for low performance."""
        scores = {
            'performance': 45.0,  # Critically low
            'accessibility': 85.0,
            'best_practices': 80.0,
            'seo': 90.0
        }
        
        insights = get_score_insights(scores)
        
        assert "critically low" in insights[0].lower()
        assert "immediate optimization needed" in insights[0].lower()
    
    def test_get_score_insights_accessibility_low(self):
        """Test score insights for low accessibility."""
        scores = {
            'performance': 85.0,
            'accessibility': 75.0,  # Below 80 threshold
            'best_practices': 80.0,
            'seo': 90.0
        }
        
        insights = get_score_insights(scores)
        
        assert "accessibility score below recommended threshold" in insights[0].lower()
        assert "wcag compliance" in insights[0].lower()
    
    def test_get_score_insights_excellent_overall(self):
        """Test score insights for excellent overall performance."""
        scores = {
            'performance': 95.0,
            'accessibility': 92.0,
            'best_practices': 90.0,
            'seo': 95.0
        }
        
        insights = get_score_insights(scores)
        
        assert "excellent overall performance" in insights[-1].lower()
        assert "maintain current standards" in insights[-1].lower()
    
    def test_get_score_insights_good_overall(self):
        """Test score insights for good overall performance."""
        scores = {
            'performance': 85.0,
            'accessibility': 88.0,
            'best_practices': 85.0,
            'seo': 90.0
        }
        
        insights = get_score_insights(scores)
        
        assert "good overall performance" in insights[-1].lower()
        assert "minor optimizations may help" in insights[-1].lower()
    
    def test_get_score_insights_acceptable_overall(self):
        """Test score insights for acceptable overall performance."""
        scores = {
            'performance': 75.0,
            'accessibility': 78.0,
            'best_practices': 75.0,
            'seo': 80.0
        }
        
        insights = get_score_insights(scores)
        
        assert "acceptable performance" in insights[-1].lower()
        assert "consider improvements" in insights[-1].lower()
    
    def test_get_score_insights_poor_overall(self):
        """Test score insights for poor overall performance."""
        scores = {
            'performance': 55.0,
            'accessibility': 60.0,
            'best_practices': 58.0,
            'seo': 65.0
        }
        
        insights = get_score_insights(scores)
        
        assert "performance needs significant improvement" in insights[-1].lower()
        assert "prioritize optimization" in insights[-1].lower()
