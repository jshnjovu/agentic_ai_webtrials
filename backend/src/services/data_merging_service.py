"""
Data merging and deduplication service.
"""

from __future__ import annotations

import math
import uuid
from typing import Any, Dict, List, Optional, Tuple

from src.core import BaseService
from src.schemas import (
    BusinessInput,
    DataSource,
    MatchDetails,
    MergedBusiness,
    MergeRequest,
    MergeResponse,
)


def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().lower().split())


def _levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)
    v0 = list(range(len(b) + 1))
    v1 = [0] * (len(b) + 1)
    for i in range(len(a)):
        v1[0] = i + 1
        for j in range(len(b)):
            cost = 0 if a[i] == b[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0, v1 = v1, v0
    return v0[len(b)]


def _string_similarity(a: str, b: str) -> float:
    a_norm = _normalize_text(a)
    b_norm = _normalize_text(b)
    if not a_norm and not b_norm:
        return 1.0
    if not a_norm or not b_norm:
        return 0.0
    distance = _levenshtein_distance(a_norm, b_norm)
    max_len = max(len(a_norm), len(b_norm))
    if max_len == 0:
        return 1.0
    return max(0.0, 1.0 - distance / max_len)


def _haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def _proximity_score(a: BusinessInput, b: BusinessInput, threshold_meters: float) -> float:
    if a.latitude is None or a.longitude is None or b.latitude is None or b.longitude is None:
        return 0.0
    d = _haversine_distance_meters(a.latitude, a.longitude, b.latitude, b.longitude)
    if d >= threshold_meters:
        return 0.0
    # Score decays linearly with distance up to threshold
    return max(0.0, 1.0 - (d / threshold_meters))


class DataMergingService(BaseService):
    """Service responsible for merging and deduplicating business data from multiple sources."""

    def __init__(self):
        super().__init__("DataMergingService")

    def validate_input(self, data: Any) -> bool:
        return isinstance(data, MergeRequest)

    def _score_match(self, a: BusinessInput, b: BusinessInput, req: MergeRequest) -> MatchDetails:
        name_sim = _string_similarity(a.name, b.name)
        addr_sim = _string_similarity(a.address or "", b.address or "")
        prox = _proximity_score(a, b, req.distance_threshold_meters)
        combined = (name_sim * req.name_weight) + (max(addr_sim, prox) * req.address_weight)
        matched = combined >= req.match_threshold
        return MatchDetails(
            name_similarity=name_sim,
            address_similarity=addr_sim,
            proximity_score=prox,
            combined_score=combined,
            matched=matched,
            threshold=req.match_threshold,
        )

    def _choose_best(self, a: BusinessInput, b: BusinessInput) -> Tuple[str, Optional[str], Optional[float], Optional[float], Optional[str], Optional[str], List[str]]:
        review_reasons: List[str] = []
        # Name: prefer longer non-empty (more complete)
        name_candidates = [a.name or "", b.name or ""]
        name = max(name_candidates, key=lambda x: len(x or ""))

        # Address: prefer presence then longer
        addr_candidates = [a.address or "", b.address or ""]
        address = max(addr_candidates, key=lambda x: (len(x) > 0, len(x))) or None

        # Coordinates: prefer presence; if both present but far, mark review
        lat = a.latitude if a.latitude is not None else b.latitude
        lon = a.longitude if a.longitude is not None else b.longitude
        if a.latitude is not None and b.latitude is not None and a.longitude is not None and b.longitude is not None:
            dist = _haversine_distance_meters(a.latitude, a.longitude, b.latitude, b.longitude)
            if dist > 100.0:
                review_reasons.append("coordinate_discrepancy")

        # Phone: prefer E.164-like or longer
        phone_candidates = [a.phone or "", b.phone or ""]
        phone = max(phone_candidates, key=lambda x: (x.startswith("+") and x[1:].isdigit(), len(x))) or None

        # Website: prefer https and longer
        website_candidates = [a.website or "", b.website or ""]
        website = max(website_candidates, key=lambda x: (x.startswith("https"), len(x))) or None

        return name, address, lat, lon, phone, website, review_reasons

    def _confidence_level(self, score: float) -> str:
        if score >= 0.9:
            return "high"
        if score >= 0.75:
            return "medium"
        return "low"

    def merge_and_deduplicate(self, request: MergeRequest) -> MergeResponse:
        try:
            self.log_operation("Starting merge and deduplication", run_id=request.run_id)

            merged: List[MergedBusiness] = []
            duplicates_removed = 0
            manual_review_count = 0

            yelp_pool = list(request.yelp_data)
            for g in request.google_data:
                # Attempt to find best match in Yelp pool
                best_match: Optional[Tuple[int, MatchDetails]] = None
                for idx, y in enumerate(yelp_pool):
                    details = self._score_match(g, y, request)
                    if best_match is None or details.combined_score > best_match[1].combined_score:
                        best_match = (idx, details)
                if best_match and best_match[1].matched:
                    y = yelp_pool.pop(best_match[0])
                    name, address, lat, lon, phone, website, review_reasons = self._choose_best(g, y)
                    confidence = best_match[1].combined_score
                    confidence_level = self._confidence_level(confidence)
                    manual_review_required = confidence_level == "low" or len(review_reasons) > 0
                    if manual_review_required:
                        manual_review_count += 1
                    merged.append(
                        MergedBusiness(
                            id=str(uuid.uuid4()),
                            name=name,
                            address=address,
                            latitude=lat,
                            longitude=lon,
                            phone=phone,
                            website=website,
                            google_place_id=g.google_place_id or g.id,
                            yelp_business_id=y.yelp_business_id or y.id,
                            data_source=DataSource.MERGED,
                            confidence_score=confidence,
                            confidence_level=self._confidence_level(confidence),
                            manual_review_required=manual_review_required,
                            review_reasons=review_reasons,
                            match_details=best_match[1],
                        )
                    )
                    duplicates_removed += 1
                else:
                    # No match found; include Google record as-is (normalized)
                    merged.append(
                        MergedBusiness(
                            id=str(uuid.uuid4()),
                            name=g.name,
                            address=g.address,
                            latitude=g.latitude,
                            longitude=g.longitude,
                            phone=g.phone,
                            website=g.website,
                            google_place_id=g.google_place_id or g.id,
                            yelp_business_id=None,
                            data_source=DataSource.GOOGLE,
                            confidence_score=0.6,
                            confidence_level=self._confidence_level(0.6),
                            manual_review_required=False,
                            review_reasons=[],
                            match_details=None,
                        )
                    )

            # Any remaining Yelp entries not matched become standalone
            for y in yelp_pool:
                merged.append(
                    MergedBusiness(
                        id=str(uuid.uuid4()),
                        name=y.name,
                        address=y.address,
                        latitude=y.latitude,
                        longitude=y.longitude,
                        phone=y.phone,
                        website=y.website,
                        google_place_id=None,
                        yelp_business_id=y.yelp_business_id or y.id,
                        data_source=DataSource.YELP,
                        confidence_score=0.6,
                        confidence_level=self._confidence_level(0.6),
                        manual_review_required=False,
                        review_reasons=[],
                        match_details=None,
                    )
                )

            response = MergeResponse(
                success=True,
                total_input=len(request.google_data) + len(request.yelp_data),
                total_output=len(merged),
                duplicates_removed=duplicates_removed,
                manual_review_count=manual_review_count,
                merged=merged,
                run_id=request.run_id,
                details={
                    "algorithm": {
                        "name_weight": request.name_weight,
                        "address_weight": request.address_weight,
                        "match_threshold": request.match_threshold,
                        "distance_threshold_meters": request.distance_threshold_meters,
                    }
                },
            )

            self.log_operation(
                f"Merge completed: in={response.total_input} out={response.total_output} dupes_removed={duplicates_removed}",
                run_id=request.run_id,
            )
            return response
        except Exception as e:
            self.log_error(e, "merge_and_deduplicate", run_id=request.run_id)
            raise