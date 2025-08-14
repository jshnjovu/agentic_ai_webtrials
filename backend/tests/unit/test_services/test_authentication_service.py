"""
Unit tests for authentication services.
Tests Google Places and Yelp Fusion authentication services.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.services.google_places_auth_service import GooglePlacesAuthService
from src.services.yelp_fusion_auth_service import YelpFusionAuthService
from src.services.rate_limiter import RateLimiter


class TestGooglePlacesAuthService:
    """Test cases for Google Places authentication service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = GooglePlacesAuthService()
        self.run_id = "test-run-12345"
    
    def test_validate_input(self):
        """Test input validation."""
        # Valid input
        assert self.service.validate_input({"run_id": "test"}) is True
        
        # Invalid input
        assert self.service.validate_input({"invalid": "data"}) is False
        assert self.service.validate_input("string") is False
        assert self.service.validate_input(None) is False
    
    @patch('src.services.google_places_auth_service.httpx.Client')
    def test_authenticate_success(self, mock_client):
        """Test successful authentication."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "OK"}
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            with patch.object(self.service.rate_limiter, 'record_request'):
                result = self.service.authenticate(self.run_id)
                
                assert result["success"] is True
                assert result["api_name"] == "google_places"
                assert "Successfully authenticated" in result["message"]
    
    @patch('src.services.google_places_auth_service.httpx.Client')
    def test_authenticate_rate_limit_exceeded(self, mock_client):
        """Test authentication with rate limit exceeded."""
        # Mock rate limiter failure
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(False, "Rate limit exceeded")):
            result = self.service.authenticate(self.run_id)
            
            assert result["success"] is False
            assert "Rate limit check failed" in result["error"]
    
    @patch('src.services.google_places_auth_service.httpx.Client')
    def test_authenticate_api_error(self, mock_client):
        """Test authentication with API error."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "INVALID_REQUEST", "error_message": "Invalid input"}
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            with patch.object(self.service.rate_limiter, 'record_request'):
                result = self.service.authenticate(self.run_id)
                
                assert result["success"] is False
                assert "API returned status" in result["error"]
    
    @patch('src.services.google_places_auth_service.httpx.Client')
    def test_authenticate_http_error(self, mock_client):
        """Test authentication with HTTP error."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            with patch.object(self.service.rate_limiter, 'record_request'):
                result = self.service.authenticate(self.run_id)
                
                assert result["success"] is False
                assert "HTTP 400" in result["error"]
    
    @patch('src.services.google_places_auth_service.httpx.Client')
    def test_authenticate_timeout(self, mock_client):
        """Test authentication timeout handling."""
        # Mock timeout exception
        mock_client.side_effect = Exception("timeout")
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            result = self.service.authenticate(self.run_id)
            
            assert result["success"] is False
            assert "timeout" in result["error"]
    
    def test_test_connection(self):
        """Test connection testing functionality."""
        # Mock the authenticate method to test connection
        with patch.object(self.service, 'authenticate', return_value={"success": True}):
            result = self.service.test_connection(self.run_id)
            
            assert result["success"] is True
            assert result["api_name"] == "google_places"
    
    def test_get_health_status(self):
        """Test health status retrieval."""
        # Mock the test_connection method
        with patch.object(self.service, 'test_connection', return_value={"success": True}):
            result = self.service.get_health_status(self.run_id)
            
            assert result["success"] is True
            assert result["api_name"] == "google_places"


class TestYelpFusionAuthService:
    """Test cases for Yelp Fusion authentication service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = YelpFusionAuthService()
        self.run_id = "test-run-12345"
    
    def test_validate_input(self):
        """Test input validation."""
        # Valid input
        assert self.service.validate_input({"run_id": "test"}) is True
        
        # Invalid input
        assert self.service.validate_input({"invalid": "data"}) is False
        assert self.service.validate_input("string") is False
        assert self.service.validate_input(None) is False
    
    @patch('src.services.yelp_fusion_auth_service.httpx.Client')
    def test_authenticate_success(self, mock_client):
        """Test successful authentication."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"businesses": [{"id": "test"}]}
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            with patch.object(self.service.rate_limiter, 'record_request'):
                result = self.service.authenticate(self.run_id)
                
                assert result["success"] is True
                assert result["api_name"] == "yelp_fusion"
                assert "Successfully authenticated" in result["message"]
    
    @patch('src.services.yelp_fusion_auth_service.httpx.Client')
    def test_authenticate_unauthorized(self, mock_client):
        """Test authentication with unauthorized error."""
        # Mock unauthorized response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            with patch.object(self.service.rate_limiter, 'record_request'):
                result = self.service.authenticate(self.run_id)
                
                assert result["success"] is False
                assert "Authentication failed" in result["error"]
    
    @patch('src.services.yelp_fusion_auth_service.httpx.Client')
    def test_authenticate_rate_limited(self, mock_client):
        """Test authentication with rate limit error."""
        # Mock rate limited response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            with patch.object(self.service.rate_limiter, 'record_request'):
                result = self.service.authenticate(self.run_id)
                
                assert result["success"] is False
                assert "Rate limit exceeded" in result["error"]
    
    @patch('src.services.yelp_fusion_auth_service.httpx.Client')
    def test_test_connection(self, mock_client):
        """Test connection testing functionality."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"businesses": [{"id": "test"}]}
        mock_response.elapsed.total_seconds.return_value = 0.1
        
        mock_client_instance = Mock()
        mock_client_instance.get.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance
        
        # Mock rate limiter
        with patch.object(self.service.rate_limiter, 'can_make_request', return_value=(True, "OK")):
            with patch.object(self.service.rate_limiter, 'record_request'):
                result = self.service.test_connection(self.run_id)
                
                assert result["success"] is True
                assert result["api_name"] == "yelp_fusion"
    
    def test_get_health_status(self):
        """Test health status retrieval."""
        # Mock the test_connection method
        with patch.object(self.service, 'test_connection', return_value={"success": True}):
            result = self.service.get_health_status(self.run_id)
            
            assert result["success"] is True
            assert result["api_name"] == "yelp_fusion"


class TestRateLimiter:
    """Test cases for rate limiter service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.rate_limiter = RateLimiter()
    
    def test_validate_input(self):
        """Test input validation."""
        # Valid inputs
        assert self.rate_limiter.validate_input("google_places") is True
        assert self.rate_limiter.validate_input("yelp_fusion") is True
        
        # Invalid inputs
        assert self.rate_limiter.validate_input("unknown_api") is False
        assert self.rate_limiter.validate_input(123) is False
        assert self.rate_limiter.validate_input(None) is False
    
    def test_can_make_request(self):
        """Test rate limit checking."""
        # Should be able to make request initially
        can_request, reason = self.rate_limiter.can_make_request("google_places")
        assert can_request is True
        assert reason == "OK"
    
    def test_rate_limit_exceeded(self):
        """Test rate limit exceeded scenario."""
        # Make many requests to exceed rate limit
        for i in range(101):  # Exceed 100 per minute limit
            self.rate_limiter.record_request("google_places", True)
        
        # Should not be able to make more requests
        can_request, reason = self.rate_limiter.can_make_request("google_places")
        assert can_request is False
        assert "Rate limit exceeded" in reason
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        # Record multiple failures
        for i in range(6):  # Exceed failure threshold
            self.rate_limiter.record_request("google_places", False)
        
        # Circuit breaker should be open
        can_request, reason = self.rate_limiter.can_make_request("google_places")
        assert can_request is False
        assert "Circuit breaker is OPEN" in reason
    
    def test_get_rate_limit_info(self):
        """Test rate limit information retrieval."""
        info = self.rate_limiter.get_rate_limit_info("google_places")
        
        assert info is not None
        assert info["api_name"] == "google_places"
        assert "current_usage" in info
        assert "limit" in info
        assert "remaining" in info
        assert "reset_time" in info
    
    def test_reset_circuit_breaker(self):
        """Test manual circuit breaker reset."""
        # Open circuit breaker first
        for i in range(6):
            self.rate_limiter.record_request("google_places", False)
        
        # Reset circuit breaker
        self.rate_limiter.reset_circuit_breaker("google_places")
        
        # Should be able to make requests again
        can_request, reason = self.rate_limiter.can_make_request("google_places")
        assert can_request is True
        assert reason == "OK"
