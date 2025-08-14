"""
Unit tests for YelpFusionRateLimitMiddleware.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse

from src.middleware.rate_limit_middleware import YelpFusionRateLimitMiddleware


class TestYelpFusionRateLimitMiddleware:
    """Test cases for YelpFusionRateLimitMiddleware."""
    
    @pytest.fixture
    def app(self):
        """Create a test FastAPI application."""
        app = FastAPI()
        
        @app.get("/api/v1/business-search/yelp")
        async def yelp_search():
            return {"message": "Yelp search endpoint"}
        
        @app.get("/api/v1/business-search/yelp/")
        async def yelp_search_trailing():
            return {"message": "Yelp search endpoint with trailing slash"}
        
        @app.get("/api/v1/business-search/google")
        async def google_search():
            return {"message": "Google search endpoint"}
        
        @app.get("/other/endpoint")
        async def other_endpoint():
            return {"message": "Other endpoint"}
        
        return app
    
    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock rate limiter for testing."""
        mock_limiter = Mock()
        mock_limiter.can_make_request.return_value = (True, "OK")
        mock_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 100,
            "limit": 5000,
            "remaining": 4900,
            "reset_time": "2024-12-20T00:00:00"
        }
        return mock_limiter
    
    @pytest.fixture
    def client(self, app, mock_rate_limiter):
        """Create a test client with mocked rate limiter."""
        # Create a custom test middleware that uses the mock
        class TestMiddleware(YelpFusionRateLimitMiddleware):
            def __init__(self, app, mock_limiter):
                super().__init__(app)
                self.rate_limiter = mock_limiter
        
        # Add the test middleware to the app
        app.add_middleware(TestMiddleware, mock_limiter=mock_rate_limiter)
        
        return TestClient(app)
    
    def test_middleware_initialization(self, app, mock_rate_limiter):
        """Test middleware initialization."""
        middleware = YelpFusionRateLimitMiddleware(app)
        
        assert middleware.rate_limiter is not None
        assert "/api/v1/business-search/yelp" in middleware.yelp_endpoints
        assert "/api/v1/business-search/yelp/" in middleware.yelp_endpoints
        assert middleware.yelp_endpoints["/api/v1/business-search/yelp"] == "yelp_fusion"
    
    def test_yelp_endpoint_allowed(self, client, mock_rate_limiter):
        """Test that Yelp endpoints work when rate limit allows requests."""
        mock_rate_limiter.can_make_request.return_value = (True, "OK")
        
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Yelp search endpoint"
        
        # Check that rate limit headers are added
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers
    
    def test_yelp_endpoint_trailing_slash(self, client, mock_rate_limiter):
        """Test that Yelp endpoints with trailing slash work."""
        mock_rate_limiter.can_make_request.return_value = (True, "OK")
        
        response = client.get("/api/v1/business-search/yelp/")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Yelp search endpoint with trailing slash"
    
    def test_yelp_endpoint_rate_limited(self, client, mock_rate_limiter):
        """Test that Yelp endpoints return 429 when rate limited."""
        mock_rate_limiter.can_make_request.return_value = (False, "Daily limit exceeded")
        
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 429
        data = response.json()
        assert data["error"] == "Rate limit exceeded"
        assert data["message"] == "Daily limit exceeded"
        assert "rate_limit_info" in data
        assert "retry_after" in data
        assert data["endpoint"] == "/api/v1/business-search/yelp"
    
    def test_non_yelp_endpoint_passes_through(self, client, mock_rate_limiter):
        """Test that non-Yelp endpoints pass through without rate limiting."""
        # Even if rate limiter says no, non-Yelp endpoints should work
        mock_rate_limiter.can_make_request.return_value = (False, "Rate limited")
        
        response = client.get("/api/v1/business-search/google")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Google search endpoint"
        
        # No rate limit headers should be added
        assert "X-RateLimit-Limit" not in response.headers
    
    def test_other_endpoint_passes_through(self, client, mock_rate_limiter):
        """Test that completely unrelated endpoints pass through."""
        response = client.get("/other/endpoint")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Other endpoint"
    
    def test_rate_limit_headers_added(self, client, mock_rate_limiter):
        """Test that rate limit headers are properly added to responses."""
        mock_rate_limiter.can_make_request.return_value = (True, "OK")
        mock_rate_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 100,
            "limit": 5000,
            "remaining": 4900,
            "reset_time": "2024-12-20T00:00:00"
        }
        
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 200
        assert response.headers["X-RateLimit-Limit"] == "5000"
        assert response.headers["X-RateLimit-Remaining"] == "4900"
        assert response.headers["X-RateLimit-Reset"] == "2024-12-20T00:00:00"
        assert "X-RateLimit-Reset-Timestamp" in response.headers
    
    def test_rate_limit_info_in_error_response(self, client, mock_rate_limiter):
        """Test that rate limit info is included in error responses."""
        mock_rate_limiter.can_make_request.return_value = (False, "Daily limit exceeded")
        mock_rate_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 5000,
            "limit": 5000,
            "remaining": 0,
            "reset_time": "2024-12-20T00:00:00"
        }
        
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 429
        data = response.json()
        assert "rate_limit_info" in data
        assert data["rate_limit_info"]["current_usage"] == 5000
        assert data["rate_limit_info"]["limit"] == 5000
        assert data["rate_limit_info"]["remaining"] == 0
    
    def test_retry_after_calculation(self, client, mock_rate_limiter):
        """Test that retry-after is calculated correctly."""
        mock_rate_limiter.can_make_request.return_value = (False, "Daily limit exceeded")
        mock_rate_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 5000,
            "limit": 5000,
            "remaining": 0,
            "reset_time": "2024-12-20T00:00:00"
        }
        
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 429
        data = response.json()
        assert "retry_after" in data
        assert isinstance(data["retry_after"], int)
        assert data["retry_after"] >= 60  # Should be at least 1 minute
    
    def test_retry_after_fallback(self, client, mock_rate_limiter):
        """Test that retry-after falls back to default when reset time is invalid."""
        mock_rate_limiter.can_make_request.return_value = (False, "Daily limit exceeded")
        mock_rate_limiter.get_rate_limit_info.return_value = {
            "api_name": "yelp_fusion",
            "current_usage": 5000,
            "limit": 5000,
            "remaining": 0,
            "reset_time": "invalid-time-format"
        }
        
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 429
        data = response.json()
        assert "retry_after" in data
        assert data["retry_after"] == 3600  # Should fall back to 1 hour
    
    def test_middleware_does_not_affect_request_processing(self, client, mock_rate_limiter):
        """Test that middleware doesn't interfere with normal request processing."""
        mock_rate_limiter.can_make_request.return_value = (True, "OK")
        
        # Test that the response content is unchanged
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Yelp search endpoint"
        
        # Test that headers are preserved
        assert "content-type" in response.headers
    
    def test_multiple_yelp_requests(self, client, mock_rate_limiter):
        """Test that multiple Yelp requests work correctly."""
        mock_rate_limiter.can_make_request.return_value = (True, "OK")
        
        # Make multiple requests
        response1 = client.get("/api/v1/business-search/yelp")
        response2 = client.get("/api/v1/business-search/yelp")
        response3 = client.get("/api/v1/business-search/yelp")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200
        
        # All should have rate limit headers
        for response in [response1, response2, response3]:
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
    
    def test_middleware_error_handling(self, client, mock_rate_limiter):
        """Test that middleware handles errors gracefully."""
        # Mock rate limiter to raise an exception
        mock_rate_limiter.can_make_request.side_effect = Exception("Rate limiter error")
        
        # Should still allow the request to pass through (fail open)
        response = client.get("/api/v1/business-search/yelp")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Yelp search endpoint"
