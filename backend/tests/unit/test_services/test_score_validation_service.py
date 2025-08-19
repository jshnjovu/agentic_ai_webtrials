"""
Unit tests for ScoreValidationService.
Tests score validation, confidence calculation, and discrepancy detection.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.score_validation_service import (
    ScoreValidationService,
    ConfidenceLevel,
    IssueCategory,
    ScoreData
)
from src.schemas.website_scoring import (
    ScoreValidationResult,
    IssuePriority,
    IssuePriorityDetails
)
from src.schemas.website_scoring import (
    WebsiteScore,
    ScoreValidationResult,
    ValidationMetrics,
    IssuePriority,
    FinalScore
)


class TestScoreValidationService:
    """Test cases for ScoreValidationService."""
    
    @pytest.fixture
    def service(self):
        """Create a ScoreValidationService instance for testing."""
        return ScoreValidationService()
    
    @pytest.fixture
    def sample_lighthouse_scores(self):
        """Create sample Lighthouse scores for testing."""
        return [
            WebsiteScore(
                performance=85.0,
                accessibility=90.0,
                best_practices=88.0,
                seo=92.0,
                overall=88.75
            ),
            WebsiteScore( 
                performance=78.0,
                accessibility=85.0,
                best_practices=82.0,
                seo=88.0,
                overall=83.25
            )
        ]
    
    @pytest.fixture
    def sample_comprehensive_scores(self):
        """Create sample comprehensive speed scores for testing."""
        return [
            {
                "pagespeed_performance": 88.0,
                "pagespeed_accessibility": 85.0,
                "pagespeed_best_practices": 90.0,
                "pagespeed_seo": 87.0,
                "pingdom_trust": 89.0,
                "pingdom_cro": 87.8,
                "overall_score": 87.8,
                "confidence_level": ConfidenceLevel.HIGH
            },
            {
                "pagespeed_performance": 80.0,
                "pagespeed_accessibility": 82.0,
                "pagespeed_best_practices": 85.0,
                "pagespeed_seo": 83.0,
                "pingdom_trust": 86.0,
                "pingdom_cro": 83.2,
                "overall_score": 83.2,
                "confidence_level": ConfidenceLevel.HIGH
            }
        ]
    
    def test_service_initialization(self, service):
        """Test that the service initializes with correct default values."""
        assert service.lighthouse_weight == 0.8
        assert service.comprehensive_weight == 0.2
        assert service.confidence_thresholds["high"] == 0.8
        assert service.confidence_thresholds["medium"] == 0.6
        assert service.confidence_thresholds["low"] == 0.0
    
    @pytest.mark.asyncio
    async def test_validate_scores_success(self, service, sample_lighthouse_scores, sample_comprehensive_scores):
        """Test successful score validation with complete data."""
        result = await service.validate_scores(
            lighthouse_scores=sample_lighthouse_scores,
            comprehensive_scores=sample_comprehensive_scores,
            business_id="test_business",
            run_id="test_run"
        )
        
        assert isinstance(result, ScoreValidationResult)
        assert result.business_id == "test_business"
        assert result.run_id == "test_run"
        assert result.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
        assert result.correlation_coefficient >= -1.0 and result.correlation_coefficient <= 1.0
        assert result.discrepancy_count >= 0
        assert result.final_score is not None
        assert result.validation_metrics is not None
        assert len(result.issue_priorities) >= 0
    
    @pytest.mark.asyncio
    async def test_validate_scores_empty_data(self, service):
        """Test score validation with empty data sets."""
        result = await service.validate_scores(
            lighthouse_scores=[],
            comprehensive_scores=[],
            business_id="test_business",
            run_id="test_run"
        )
        
        assert result.confidence_level == ConfidenceLevel.LOW
        assert result.correlation_coefficient == 0.0
        assert result.discrepancy_count == 0
        assert result.final_weighted_score == 0.0
    
    def test_pearson_correlation_perfect_correlation(self, service):
        """Test Pearson correlation calculation with perfectly correlated data."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 4.0, 6.0, 8.0, 10.0]
        
        correlation = service._calculate_pearson_correlation(x, y)
        assert abs(correlation - 1.0) < 0.001
    
    def test_pearson_correlation_negative_correlation(self, service):
        """Test Pearson correlation calculation with negatively correlated data."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [10.0, 8.0, 6.0, 4.0, 2.0]
        
        correlation = service._calculate_pearson_correlation(x, y)
        assert abs(correlation - (-1.0)) < 0.001
    
    def test_pearson_correlation_no_correlation(self, service):
        """Test Pearson correlation calculation with uncorrelated data."""
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [1.0, 1.0, 1.0, 1.0, 1.0]
        
        correlation = service._calculate_pearson_correlation(x, y)
        assert correlation == 0.0
    
    def test_pearson_correlation_insufficient_data(self, service):
        """Test Pearson correlation with insufficient data points."""
        x = [1.0]
        y = [2.0]
        
        correlation = service._calculate_pearson_correlation(x, y)
        assert correlation == 0.0
    
    def test_statistical_significance_high(self, service):
        """Test statistical significance calculation for high significance."""
        # High correlation with sufficient sample size should give high significance
        significance = service._calculate_statistical_significance(0.9, 10)
        assert significance >= 0.8
    
    def test_statistical_significance_low(self, service):
        """Test statistical significance calculation for low significance."""
        # Low correlation should give low significance
        significance = service._calculate_statistical_significance(0.1, 5)
        assert significance <= 0.6
    
    def test_variance_analysis(self, service):
        """Test variance analysis calculation."""
        x = [80.0, 85.0, 90.0, 95.0, 100.0]
        y = [75.0, 80.0, 85.0, 90.0, 95.0]
        
        variance = service._calculate_variance_analysis(x, y)
        assert variance >= 0.0
        assert isinstance(variance, float)
    
    def test_variance_analysis_empty_data(self, service):
        """Test variance analysis with empty data."""
        variance = service._calculate_variance_analysis([], [])
        assert variance == 0.0
    
    def test_reliability_indicator_calculation(self, service):
        """Test reliability indicator calculation."""
        correlation = 0.8
        significance = 0.9
        variance = 0.2
        
        reliability = service._calculate_reliability_indicator(correlation, significance, variance)
        assert reliability >= 0.0 and reliability <= 1.0
        assert reliability > 0.5  # Should be reasonably high with good inputs
    
    def test_confidence_level_high(self, service):
        """Test confidence level calculation for high reliability."""
        consistency_result = {"reliability": 0.9}
        confidence = service._calculate_confidence_level(consistency_result)
        assert confidence == ConfidenceLevel.HIGH
    
    def test_confidence_level_medium(self, service):
        """Test confidence level calculation for medium reliability."""
        consistency_result = {"reliability": 0.7}
        confidence = service._calculate_confidence_level(consistency_result)
        assert confidence == ConfidenceLevel.MEDIUM
    
    def test_confidence_level_low(self, service):
        """Test confidence level calculation for low reliability."""
        consistency_result = {"reliability": 0.3}
        confidence = service._calculate_confidence_level(consistency_result)
        assert confidence == ConfidenceLevel.LOW
    
    def test_discrepancy_detection(self, service, sample_lighthouse_scores, sample_comprehensive_scores):
        """Test discrepancy detection between scoring methods."""
        discrepancies = service._detect_discrepancies(sample_lighthouse_scores, sample_comprehensive_scores)
        
        assert isinstance(discrepancies, list)
        # Should detect some discrepancies if scores differ significantly
        for discrepancy in discrepancies:
            assert "category" in discrepancy
            assert "lighthouse_score" in discrepancy
            assert "comprehensive_score" in discrepancy
            assert "difference" in discrepancy
            assert "severity" in discrepancy
            assert discrepancy["severity"] in ["high", "medium"]
    
    def test_weighted_final_score_calculation(self, service, sample_lighthouse_scores, sample_comprehensive_scores):
        """Test weighted final score calculation."""
        final_score = service._calculate_weighted_final_score(sample_lighthouse_scores, sample_comprehensive_scores)
        
        assert isinstance(final_score, float)
        assert final_score >= 0.0 and final_score <= 100.0
        
        # Should be weighted average: 80% lighthouse + 20% comprehensive
        expected_lighthouse_avg = (88.75 + 83.25) / 2
        expected_comprehensive_avg = (87.8 + 83.2) / 2
        expected_weighted = expected_lighthouse_avg * 0.8 + expected_comprehensive_avg * 0.2
        
        assert abs(final_score - expected_weighted) < 1.0
    
    def test_weighted_final_score_empty_data(self, service):
        """Test weighted final score calculation with empty data."""
        final_score = service._calculate_weighted_final_score([], [])
        assert final_score == 0.0
    
    def test_issue_priorities_creation(self, service):
        """Test issue priorities creation."""
        discrepancies = [
            {
                "category": "performance",
                "severity": "high",
                "difference": 45.0
            },
            {
                "category": "accessibility",
                "severity": "medium",
                "difference": 25.0
            }
        ]
        
        consistency_result = {"reliability": 0.6}
        
        priorities = service._create_issue_priorities(discrepancies, consistency_result)
        
        assert len(priorities) >= 2
        assert all(isinstance(priority, IssuePriorityDetails) for priority in priorities)
        
        # Check that high severity gets high priority
        high_priority = next((p for p in priorities if p.category == IssueCategory.PERFORMANCE), None)
        if high_priority:
            assert high_priority.priority == IssuePriority.HIGH
            assert high_priority.business_impact_score > 0.5
    
    def test_business_impact_calculation(self, service):
        """Test business impact score calculation."""
        high_discrepancy = {"difference": 45.0}
        medium_discrepancy = {"difference": 25.0}
        low_discrepancy = {"difference": 15.0}
        
        high_impact = service._calculate_business_impact(high_discrepancy)
        medium_impact = service._calculate_business_impact(medium_discrepancy)
        low_impact = service._calculate_business_impact(low_discrepancy)
        
        assert high_impact > medium_impact > low_impact
        assert all(0.0 <= impact <= 1.0 for impact in [high_impact, medium_impact, low_impact])
    
    def test_recommended_action_generation(self, service):
        """Test recommended action generation based on discrepancy severity."""
        high_discrepancy = {"difference": 45.0}
        medium_discrepancy = {"difference": 25.0}
        low_discrepancy = {"difference": 15.0}
        
        high_action = service._get_recommended_action(high_discrepancy)
        medium_action = service._get_recommended_action(medium_discrepancy)
        low_action = service._get_recommended_action(low_discrepancy)
        
        assert "immediate" in high_action.lower()
        assert "review" in medium_action.lower()
        assert "monitor" in low_action.lower()
    
    def test_error_handling_in_consistency_check(self, service):
        """Test error handling in score consistency check."""
        with patch.object(service, '_calculate_pearson_correlation', side_effect=Exception("Test error")):
            result = service._check_score_consistency([], [])
            
            assert result["correlation"] == 0.0
            assert result["significance"] == 0.0
            assert result["variance"] == 0.0
            assert result["reliability"] == 0.0
    
    def test_error_handling_in_discrepancy_detection(self, service):
        """Test error handling in discrepancy detection."""
        with patch.object(service, 'log_error') as mock_log:
            result = service._detect_discrepancies(None, None)
            
            assert result == []
            mock_log.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_scores_exception_handling(self, service):
        """Test exception handling during score validation."""
        with patch.object(service, '_check_score_consistency', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as exc_info:
                await service.validate_scores([], [], "test_business", "test_run")
            
            assert "Test error" in str(exc_info.value)
    
    def test_timestamp_generation(self, service):
        """Test timestamp generation for validation results."""
        timestamp = service._get_current_timestamp()
        
        assert isinstance(timestamp, str)
        # Should be ISO format
        assert "T" in timestamp or " " in timestamp  # ISO format or space-separated
    
    def test_priority_level_determination(self, service):
        """Test priority level determination based on severity."""
        assert service._determine_priority_level("high") == "high"
        assert service._determine_priority_level("medium") == "medium"
        assert service._determine_priority_level("low") == "low"
        assert service._determine_priority_level("unknown") == "low"  # Default case
