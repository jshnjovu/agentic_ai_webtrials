import json

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_merge_endpoint_success():
    payload = {
        "google_data": [
            {"source": "google", "name": "Acme Plumbing", "address": "123 Main St", "latitude": 40.0, "longitude": -74.0, "google_place_id": "g1"}
        ],
        "yelp_data": [
            {"source": "yelp", "name": "Acme Plumbing", "address": "123 Main Street", "latitude": 40.0005, "longitude": -74.0005, "yelp_business_id": "y1"}
        ],
        "match_threshold": 0.7,
        "distance_threshold_meters": 200.0,
    }

    resp = client.post("/api/v1/business-management/merge", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["success"] is True
    assert data["total_input"] == 2
    assert data["total_output"] == 1
    assert data["duplicates_removed"] == 1
    assert len(data["merged"]) == 1


def test_merge_health():
    resp = client.get("/api/v1/business-management/merge/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("healthy", "unhealthy")
    assert data["service"] == "DataMergingService"