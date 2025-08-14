"""
Unit tests for RateLimitMonitor service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any

from src.services.rate_limit_monitor import RateLimitMonitor, AlertLevel, RateLimitAlert


class TestRateLimitMonitor:
    """Test cases for RateLimitMonitor."""
    
    @pytest.fixture
    def monitor(self):
        """Create a RateLimitMonitor instance for testing."""
        with patch('src.services.rate_limit_monitor.get_api_config') as mock_config:
            mock_config.return_value = Mock()
            monitor = RateLimitMonitor()
            # Mock the rate_limiter to be a proper Mock object
            monitor.rate_limiter = Mock()
            return monitor
    
    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock rate limiter for testing."""
        mock_limiter = Mock()
        mock_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 100,
            "limit": 5000,
            "remaining": 4900,
            "reset_time": "2024-12-20T00:00:00"
        }
        mock_limiter.can_make_request.return_value = (True, "OK")
        return mock_limiter
    
    @pytest.fixture
    def sample_rate_limit_info(self):
        """Sample rate limit information for testing."""
        return {
            "api_name": "yelp_fusion",
            "current_usage": 3500,
            "limit": 5000,
            "remaining": 1500,
            "reset_time": "2024-12-20T00:00:00"
        }
    
    def test_validate_input_valid(self, monitor):
        """Test input validation with valid API names."""
        assert monitor.validate_input("yelp_fusion") is True
        assert monitor.validate_input("google_places") is True
    
    def test_validate_input_invalid(self, monitor):
        """Test input validation with invalid API names."""
        assert monitor.validate_input("invalid_api") is False
        assert monitor.validate_input(123) is False
        assert monitor.validate_input(None) is False
    
    def test_check_rate_limits_success(self, monitor, mock_rate_limiter):
        """Test successful rate limit checking."""
        monitor.rate_limiter = mock_rate_limiter
        
        result = monitor.check_rate_limits("test_run_123")
        
        assert result["timestamp"]
        assert "status" in result
        assert "yelp_fusion" in result["status"]
        assert result["alerts_generated"] >= 0
        assert "total_alerts" in result
    
    def test_check_rate_limits_error(self, monitor):
        """Test rate limit checking with error."""
        # Mock rate limiter to raise an exception
        monitor.rate_limiter.get_rate_limit_info.side_effect = Exception("Test error")
        
        result = monitor.check_rate_limits("test_run_123")
        
        assert "error" in result
        assert "Failed to check rate limits" in result["error"]
    
    def test_check_api_rate_limit_success(self, monitor, mock_rate_limiter):
        """Test successful API rate limit checking."""
        monitor.rate_limiter = mock_rate_limiter
        
        result = monitor._check_api_rate_limit("yelp_fusion", "test_run_123")
        
        assert result["can_make_request"] is True
        assert result["reason"] == "OK"
        assert result["current_usage"] == 100
        assert result["limit"] == 5000
        assert result["usage_percentage"] == 0.02
        assert result["remaining"] == 4900
        assert "alerts" in result
    
    def test_check_api_rate_limit_error(self, monitor):
        """Test API rate limit checking with error."""
        monitor.rate_limiter.get_rate_limit_info.return_value = None
        
        result = monitor._check_api_rate_limit("yelp_fusion", "test_run_123")
        
        assert "error" in result
        assert "Unable to get rate limit info" in result["error"]
    
    def test_generate_alerts_warning_threshold(self, monitor, mock_rate_limiter):
        """Test alert generation for warning threshold."""
        monitor.rate_limiter = mock_rate_limiter
        
        # Set usage to 75% (above warning threshold of 70%)
        mock_rate_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 3750,  # 75% of 5000
            "limit": 5000,
            "remaining": 1250,
            "reset_time": "2024-12-20T00:00:00"
        }
        
        alerts = monitor._generate_alerts("yelp_fusion", 3750, 5000, 0.75, "test_run_123")
        
        assert len(alerts) >= 1
        warning_alerts = [a for a in alerts if a.level == AlertLevel.WARNING]
        assert len(warning_alerts) >= 1
        assert "75.0%" in warning_alerts[0].message
    
    def test_generate_alerts_critical_threshold(self, monitor, mock_rate_limiter):
        """Test alert generation for critical threshold."""
        monitor.rate_limiter = mock_rate_limiter
        
        # Set usage to 95% (above critical threshold of 90%)
        mock_rate_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 4750,  # 95% of 5000
            "limit": 5000,
            "remaining": 250,
            "reset_time": "2024-12-20T00:00:00"
        }
        
        alerts = monitor._generate_alerts("yelp_fusion", 4750, 5000, 0.95, "test_run_123")
        
        assert len(alerts) >= 2  # Warning + Critical
        critical_alerts = [a for a in alerts if a.level == AlertLevel.CRITICAL]
        assert len(critical_alerts) >= 1
        assert "95.0%" in critical_alerts[0].message
    
    def test_generate_alerts_rate_limit_exceeded(self, monitor, mock_rate_limiter):
        """Test alert generation when rate limit is exceeded."""
        monitor.rate_limiter = mock_rate_limiter
        
        # Set usage to 100% (rate limit exceeded)
        mock_rate_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 5000,  # 100% of 5000
            "limit": 5000,
            "remaining": 0,
            "reset_time": "2024-12-20T00:00:00"
        }
        
        alerts = monitor._generate_alerts("yelp_fusion", 5000, 5000, 1.0, "test_run_123")
        
        assert len(alerts) >= 1
        exceeded_alerts = [a for a in alerts if "exceeded" in a.message.lower()]
        assert len(exceeded_alerts) >= 1
        assert exceeded_alerts[0].level == AlertLevel.CRITICAL
    
    def test_store_alerts(self, monitor):
        """Test storing alerts."""
        initial_count = len(monitor.alerts)
        
        new_alert = RateLimitAlert(
            timestamp=datetime.now(),
            api_name="yelp_fusion",
            level=AlertLevel.WARNING,
            message="Test warning",
            current_usage=100,
            limit=5000,
            usage_percentage=0.02,
            remaining_requests=4900,
            reset_time="2024-12-20T00:00:00",
            run_id="test_run_123"
        )
        
        monitor._store_alerts([new_alert])
        
        assert len(monitor.alerts) == initial_count + 1
        assert monitor.alerts[-1].message == "Test warning"
    
    def test_get_alerts_filtered(self, monitor):
        """Test getting filtered alerts."""
        # Create test alerts with specific timestamps
        now = datetime.now()
        test_alerts = [
            RateLimitAlert(
                timestamp=now - timedelta(hours=1),  # 1 hour ago
                api_name="yelp_fusion",
                level=AlertLevel.WARNING,
                message="Recent warning",
                current_usage=100,
                limit=5000,
                usage_percentage=0.02,
                remaining_requests=4900,
                reset_time="2024-12-20T00:00:00"
            ),
            RateLimitAlert(
                timestamp=now - timedelta(hours=25),  # 25 hours ago
                api_name="yelp_fusion",
                level=AlertLevel.WARNING,
                message="Old warning",
                current_usage=100,
                limit=5000,
                usage_percentage=0.02,
                remaining_requests=4900,
                reset_time="2024-12-20T00:00:00"
            )
        ]
        
        monitor.alerts = test_alerts
        
        # Test filtering by hours (24 hours should only include the recent one)
        recent_alerts = monitor.get_alerts(hours=24)
        assert len(recent_alerts) == 1
        assert recent_alerts[0]["message"] == "Recent warning"
        
        # Test filtering by API (should include both since they're both yelp_fusion, but default hours=24 filter applies)
        yelp_alerts = monitor.get_alerts(api_name="yelp_fusion")
        assert len(yelp_alerts) == 1  # Only the recent one due to default hours=24 filter
        
        # Test filtering by API with longer hours to include both
        yelp_alerts_all = monitor.get_alerts(api_name="yelp_fusion", hours=48)
        assert len(yelp_alerts_all) == 2
        
        # Test filtering by level (should include both since they're both warnings, but default hours=24 filter applies)
        warning_alerts = monitor.get_alerts(level=AlertLevel.WARNING)
        assert len(warning_alerts) == 1  # Only the recent one due to default hours=24 filter
        
        # Test filtering by level with longer hours to include both
        warning_alerts_all = monitor.get_alerts(level=AlertLevel.WARNING, hours=48)
        assert len(warning_alerts_all) == 2
        
        # Test filtering by hours with longer period (should include both)
        all_alerts = monitor.get_alerts(hours=48)
        assert len(all_alerts) == 2
    
    def test_get_rate_limit_summary(self, monitor, mock_rate_limiter):
        """Test getting rate limit summary."""
        monitor.rate_limiter = mock_rate_limiter
        
        summary = monitor.get_rate_limit_summary()
        
        assert "timestamp" in summary
        assert "apis" in summary
        assert "total_alerts" in summary
        assert "critical_alerts" in summary
        assert "warning_alerts" in summary
        assert "yelp_fusion" in summary["apis"]
    
    def test_get_rate_limit_summary_error(self, monitor):
        """Test getting rate limit summary with error."""
        monitor.rate_limiter.get_rate_limit_info.side_effect = Exception("Test error")
        
        summary = monitor.get_rate_limit_summary()
        
        assert "error" in summary
        assert "Failed to get summary" in summary["error"]
    
    def test_reset_alerts_specific_api(self, monitor):
        """Test resetting alerts for a specific API."""
        # Create test alerts for different APIs
        test_alerts = [
            RateLimitAlert(
                timestamp=datetime.now(),
                api_name="yelp_fusion",
                level=AlertLevel.WARNING,
                message="Yelp warning",
                current_usage=100,
                limit=5000,
                usage_percentage=0.02,
                remaining_requests=4900,
                reset_time="2024-12-20T00:00:00"
            ),
            RateLimitAlert(
                timestamp=datetime.now(),
                api_name="google_places",
                level=AlertLevel.WARNING,
                message="Google warning",
                current_usage=50,
                limit=100,
                usage_percentage=0.5,
                remaining_requests=50,
                reset_time="2024-12-20T00:00:00"
            )
        ]
        
        monitor.alerts = test_alerts
        
        # Reset only Yelp alerts
        monitor.reset_alerts("yelp_fusion")
        
        assert len(monitor.alerts) == 1
        assert monitor.alerts[0].api_name == "google_places"
    
    def test_reset_alerts_all(self, monitor):
        """Test resetting all alerts."""
        # Create test alerts
        test_alerts = [
            RateLimitAlert(
                timestamp=datetime.now(),
                api_name="yelp_fusion",
                level=AlertLevel.WARNING,
                message="Test warning",
                current_usage=100,
                limit=5000,
                usage_percentage=0.02,
                remaining_requests=4900,
                reset_time="2024-12-20T00:00:00"
            )
        ]
        
        monitor.alerts = test_alerts
        
        # Reset all alerts
        monitor.reset_alerts()
        
        assert len(monitor.alerts) == 0
    
    def test_cleanup_old_alerts(self, monitor):
        """Test cleanup of old alerts."""
        # Set a low max alerts limit for testing
        monitor.max_alerts_per_api = 2
        
        # Create many test alerts
        test_alerts = []
        for i in range(10):
            alert = RateLimitAlert(
                timestamp=datetime.now() - timedelta(hours=i),
                api_name="yelp_fusion",
                level=AlertLevel.WARNING,
                message=f"Test warning {i}",
                current_usage=100,
                limit=5000,
                usage_percentage=0.02,
                remaining_requests=4900,
                reset_time="2024-12-20T00:00:00"
            )
            test_alerts.append(alert)
        
        monitor.alerts = test_alerts
        
        # Trigger cleanup
        monitor._cleanup_old_alerts()
        
        # Should keep only the most recent alerts
        assert len(monitor.alerts) <= monitor.max_alerts_per_api * len(monitor.alert_thresholds)
    
    def test_alert_level_enum(self):
        """Test AlertLevel enum values."""
        assert AlertLevel.INFO.value == "info"
        assert AlertLevel.WARNING.value == "warning"
        assert AlertLevel.CRITICAL.value == "critical"
    
    def test_rate_limit_alert_dataclass(self):
        """Test RateLimitAlert dataclass structure."""
        alert = RateLimitAlert(
            timestamp=datetime.now(),
            api_name="yelp_fusion",
            level=AlertLevel.WARNING,
            message="Test alert",
            current_usage=100,
            limit=5000,
            usage_percentage=0.02,
            remaining_requests=4900,
            reset_time="2024-12-20T00:00:00",
            run_id="test_run_123"
        )
        
        assert alert.api_name == "yelp_fusion"
        assert alert.level == AlertLevel.WARNING
        assert alert.message == "Test alert"
        assert alert.current_usage == 100
        assert alert.limit == 5000
        assert alert.usage_percentage == 0.02
        assert alert.remaining_requests == 4900
        assert alert.run_id == "test_run_123"
