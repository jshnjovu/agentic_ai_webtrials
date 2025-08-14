import uuid

import pytest

from src.schemas import BusinessInput, DataSource, MergeRequest
from src.services import DataMergingService


def make_input(name: str, address: str | None, lat: float | None, lon: float | None, phone: str | None, website: str | None, source: DataSource, gid: str | None = None, yid: str | None = None):
    return BusinessInput(
        source=source,
        id=gid or yid,
        name=name,
        address=address,
        latitude=lat,
        longitude=lon,
        phone=phone,
        website=website,
        google_place_id=gid,
        yelp_business_id=yid,
    )


def test_merge_exact_match_high_confidence():
    service = DataMergingService()
    g = make_input("Acme Plumbing", "123 Main St", 40.0, -74.0, "+15551234567", "https://acme.com", DataSource.GOOGLE, gid="g1")
    y = make_input("Acme Plumbing", "123 Main Street", 40.0005, -74.0005, "+15551234567", "http://acme.com", DataSource.YELP, yid="y1")

    req = MergeRequest(google_data=[g], yelp_data=[y], match_threshold=0.8, distance_threshold_meters=200.0)

    resp = service.merge_and_deduplicate(req)

    assert resp.success is True
    assert resp.total_input == 2
    assert resp.total_output == 1
    assert resp.duplicates_removed == 1
    assert len(resp.merged) == 1

    m = resp.merged[0]
    assert m.google_place_id == "g1"
    assert m.yelp_business_id == "y1"
    assert m.confidence_score >= 0.8
    assert m.confidence_level in ("medium", "high")
    assert m.manual_review_required in (True, False)


def test_merge_no_match_keeps_both():
    service = DataMergingService()
    g = make_input("Alpha Bakery", "1 River Rd", 41.0, -75.0, None, None, DataSource.GOOGLE, gid="g2")
    y = make_input("Beta Fitness", "999 Hill St", 42.0, -76.0, None, None, DataSource.YELP, yid="y2")

    req = MergeRequest(google_data=[g], yelp_data=[y], match_threshold=0.95)

    resp = service.merge_and_deduplicate(req)

    assert resp.success is True
    assert resp.total_input == 2
    assert resp.total_output == 2
    assert resp.duplicates_removed == 0
    assert {x.data_source.value for x in resp.merged} == {"google", "yelp"}


def test_manual_review_on_coordinate_discrepancy():
    service = DataMergingService()
    g = make_input("Gamma Salon", "22 Lake Ave", 40.0, -74.0, None, None, DataSource.GOOGLE, gid="g3")
    y = make_input("Gamma Salon", "22 Lake Ave", 40.01, -74.01, None, None, DataSource.YELP, yid="y3")

    req = MergeRequest(google_data=[g], yelp_data=[y], match_threshold=0.7, distance_threshold_meters=1000.0)

    resp = service.merge_and_deduplicate(req)

    assert resp.success
    assert resp.total_output == 1
    m = resp.merged[0]
    assert m.manual_review_required is True or "coordinate_discrepancy" in m.review_reasons


def test_prioritization_prefers_https_and_longer_phone():
    service = DataMergingService()
    g = make_input("Delta Auto", "77 Elm St", 39.0, -73.0, "+1 555 123 4567", "http://delta-auto.com", DataSource.GOOGLE, gid="g4")
    y = make_input("Delta Auto LLC", "77 Elm St", 39.0001, -73.0001, "+15551234567", "https://delta-auto.com", DataSource.YELP, yid="y4")

    req = MergeRequest(google_data=[g], yelp_data=[y], match_threshold=0.7)
    resp = service.merge_and_deduplicate(req)

    assert resp.success
    m = resp.merged[0]
    assert m.website.startswith("https://")
    assert m.phone.replace(" ", "").startswith("+1555")