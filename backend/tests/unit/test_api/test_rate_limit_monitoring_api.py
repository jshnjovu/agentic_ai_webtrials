"""
Unit tests for rate limit monitoring API endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from src.main import app
from src.services.rate_limit_monitor import AlertLevel


class TestRateLimitMonitoringAPI:
    """Test cases for rate limit monitoring API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_monitor(self):
        """Mock rate limit monitor for testing."""
        mock_monitor = Mock()
        mock_monitor.check_rate_limits.return_value = {
            "timestamp": "2024-12-19T12:00:00",
            "status": {
                "yelp_fusion": {
                    "can_make_request": True,
                    "reason": "OK",
                    "current_usage": 100,
                    "limit": 5000,
                    "usage_percentage": 0.02,
                    "remaining": 4900,
                    "reset_time": "2024-12-20T00:00:00",
                    "alerts": []
                }
            },
            "alerts_generated": 0,
            "total_alerts": 0
        }
        mock_monitor.get_rate_limit_summary.return_value = {
            "timestamp": "2024-12-19T12:00:00",
            "apis": {
                "yelp_fusion": {
                    "current_usage": 100,
                    "limit": 5000,
                    "usage_percentage": 0.02,
                    "remaining": 4900,
                    "reset_time": "2024-12-20T00:00:00"
                }
            },
            "total_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0
        }
        mock_monitor.get_alerts.return_value = []
        mock_monitor.validate_input.return_value = True
        return mock_monitor
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_rate_limit_status_success(self, mock_monitor_class, client, mock_monitor):
        """Test successful rate limit status retrieval."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/status")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "status" in data
        assert "yelp_fusion" in data["status"]
        assert data["alerts_generated"] == 0
        assert data["total_alerts"] == 0
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_rate_limit_status_error(self, mock_monitor_class, client):
        """Test rate limit status retrieval with error."""
        mock_monitor = Mock()
        mock_monitor.check_rate_limits.side_effect = Exception("Test error")
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/status")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to get rate limit status" in data["detail"]
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_rate_limit_summary_success(self, mock_monitor_class, client, mock_monitor):
        """Test successful rate limit summary retrieval."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "apis" in data
        assert "yelp_fusion" in data["apis"]
        assert data["total_alerts"] == 0
        assert data["critical_alerts"] == 0
        assert data["warning_alerts"] == 0
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_rate_limit_summary_error(self, mock_monitor_class, client):
        """Test rate limit summary retrieval with error."""
        mock_monitor = Mock()
        mock_monitor.get_rate_limit_summary.side_effect = Exception("Test error")
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/summary")
        
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "Failed to get rate limit summary" in data["detail"]
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_alerts_no_filters(self, mock_monitor_class, client, mock_monitor):
        """Test getting alerts without filters."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts")
        
        assert response.status_code == 200
        assert response.json() == []
        
        # Verify the monitor was called with default parameters
        mock_monitor.get_alerts.assert_called_once_with(
            api_name=None, level=None, hours=24
        )
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_alerts_with_api_filter(self, mock_monitor_class, client, mock_monitor):
        """Test getting alerts filtered by API name."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts?api_name=yelp_fusion")
        
        assert response.status_code == 200
        
        # Verify the monitor was called with API filter
        mock_monitor.get_alerts.assert_called_once_with(
            api_name="yelp_fusion", level=None, hours=24
        )
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_alerts_with_level_filter(self, mock_monitor_class, client, mock_monitor):
        """Test getting alerts filtered by level."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts?level=warning")
        
        assert response.status_code == 200
        
        # Verify the monitor was called with level filter
        mock_monitor.get_alerts.assert_called_once_with(
            api_name=None, level=AlertLevel.WARNING, hours=24
        )
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_alerts_with_hours_filter(self, mock_monitor_class, client, mock_monitor):
        """Test getting alerts filtered by hours."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts?hours=48")
        
        assert response.status_code == 200
        
        # Verify the monitor was called with hours filter
        mock_monitor.get_alerts.assert_called_once_with(
            api_name=None, level=None, hours=48
        )
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_alerts_invalid_level(self, mock_monitor_class, client, mock_monitor):
        """Test getting alerts with invalid level parameter."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts?level=invalid")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid alert level" in data["detail"]
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_api_alerts_success(self, mock_monitor_class, client, mock_monitor):
        """Test getting alerts for a specific API."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts/yelp_fusion")
        
        assert response.status_code == 200
        assert response.json() == []
        
        # Verify the monitor was called with API filter
        mock_monitor.get_alerts.assert_called_once_with(
            api_name="yelp_fusion", level=None, hours=24
        )
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_api_alerts_invalid_api(self, mock_monitor_class, client, mock_monitor):
        """Test getting alerts for an invalid API name."""
        mock_monitor_class.return_value = mock_monitor
        mock_monitor.validate_input.return_value = False
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts/invalid_api")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid API name" in data["detail"]
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_api_alerts_with_filters(self, mock_monitor_class, client, mock_monitor):
        """Test getting API alerts with additional filters."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/alerts/yelp_fusion?level=critical&hours=12")
        
        assert response.status_code == 200
        
        # Verify the monitor was called with all filters
        mock_monitor.get_alerts.assert_called_once_with(
            api_name="yelp_fusion", level=AlertLevel.CRITICAL, hours=12
        )
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_reset_alerts_all(self, mock_monitor_class, client, mock_monitor):
        """Test resetting all alerts."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.post("/api/v1/rate-limit-monitoring/alerts/reset")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "All alerts reset"
        
        # Verify the monitor was called
        mock_monitor.reset_alerts.assert_called_once_with(None)
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_reset_alerts_specific_api(self, mock_monitor_class, client, mock_monitor):
        """Test resetting alerts for a specific API."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.post("/api/v1/rate-limit-monitoring/alerts/reset?api_name=yelp_fusion")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Alerts reset for yelp_fusion"
        
        # Verify the monitor was called
        mock_monitor.reset_alerts.assert_called_once_with("yelp_fusion")
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_reset_alerts_invalid_api(self, mock_monitor_class, client, mock_monitor):
        """Test resetting alerts for an invalid API."""
        mock_monitor_class.return_value = mock_monitor
        mock_monitor.validate_input.return_value = False
        
        response = client.post("/api/v1/rate-limit-monitoring/alerts/reset?api_name=invalid_api")
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Invalid API name" in data["detail"]
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_monitoring_health_success(self, mock_monitor_class, client, mock_monitor):
        """Test successful monitoring health check."""
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["system_operational"] is True
        assert "apis_monitored" in data
        assert "total_alerts" in data
    
    @patch('src.api.v1.rate_limit_monitoring.RateLimitMonitor')
    def test_get_monitoring_health_error(self, mock_monitor_class, client):
        """Test monitoring health check with error."""
        mock_monitor = Mock()
        mock_monitor.get_rate_limit_summary.side_effect = Exception("Test error")
        mock_monitor_class.return_value = mock_monitor
        
        response = client.get("/api/v1/rate-limit-monitoring/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert data["system_operational"] is False
        assert "error" in data
    
    def test_router_prefix_and_tags(self):
        """Test that the router has the correct prefix and tags."""
        # Check that the rate limit monitoring routes are included
        rate_limit_routes = [
            route for route in app.routes 
            if hasattr(route, 'path') and 'rate-limit-monitoring' in route.path
        ]
        
        assert len(rate_limit_routes) > 0
        
        # Check that the router has the correct tags
        for route in app.routes:
            if hasattr(route, 'tags') and "Rate Limit Monitoring" in route.tags:
                assert route.tags == ["Rate Limit Monitoring"]
                break
        else:
            pytest.fail("Router should have 'Rate Limit Monitoring' tags")
    
    def test_endpoint_urls(self, client):
        """Test that all expected endpoints are accessible."""
        endpoints = [
            "/api/v1/rate-limit-monitoring/status",
            "/api/v1/rate-limit-monitoring/summary",
            "/api/v1/rate-limit-monitoring/alerts",
            "/api/v1/rate-limit-monitoring/health"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (endpoint exists)
            assert response.status_code != 404
