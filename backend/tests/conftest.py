"""
Test configuration and fixtures for the LeadGen Makeover Agent API.
"""

import pytest
import os
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load real environment variables from .env file for integration testing
# Only set test values if the real ones are not available
if not os.getenv("GOOGLE_PLACES_API_KEY"):
    os.environ["GOOGLE_PLACES_API_KEY"] = "test_google_places_key"
if not os.getenv("YELP_FUSION_API_KEY"):
    os.environ["YELP_FUSION_API_KEY"] = "test_yelp_fusion_key"
if not os.getenv("GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE"):
    os.environ["GOOGLE_PLACES_RATE_LIMIT_PER_MINUTE"] = "100"
if not os.getenv("YELP_FUSION_RATE_LIMIT_PER_DAY"):
    os.environ["YELP_FUSION_RATE_LIMIT_PER_DAY"] = "5000"


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application."""
    from src.main import app
    return TestClient(app)


@pytest.fixture
def mock_google_places_response():
    """Mock Google Places API response."""
    return {
        "status": "OK",
        "candidates": [
            {
                "place_id": "test_place_id",
                "formatted_address": "Test Address",
                "name": "Test Business"
            }
        ]
    }


@pytest.fixture
def mock_yelp_fusion_response():
    """Mock Yelp Fusion API response."""
    return {
        "businesses": [
            {
                "id": "test_business_id",
                "name": "Test Business",
                "location": {
                    "address1": "Test Address",
                    "city": "Test City"
                }
            }
        ],
        "total": 1
    }


@pytest.fixture
def mock_rate_limiter():
    """Mock rate limiter service."""
    mock = Mock()
    mock.can_make_request.return_value = (True, "OK")
    mock.record_request.return_value = None
    mock.get_rate_limit_info.return_value = {
        "api_name": "test_api",
        "current_usage": 0,
        "limit": 100,
        "remaining": 100,
        "reset_time": "2024-12-19T12:00:00"
    }
    return mock


@pytest.fixture
def sample_run_id():
    """Sample run ID for testing."""
    return "test-run-12345"
