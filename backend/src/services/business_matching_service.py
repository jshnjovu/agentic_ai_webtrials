"""
Business matching service for identifying similar businesses across different data sources.
Implements fuzzy string matching, address similarity scoring, and coordinate proximity calculations.
"""

import math
import re
from typing import List, Any, Tuple
from datetime import datetime

from fuzzywuzzy import fuzz
from geopy.distance import geodesic

from ..core.base_service import BaseService
from ..schemas.business_matching import (
    BusinessSourceData,
    BusinessLocation,
    BusinessMatchScore,
    BusinessMatchCandidate,
    BusinessMatchingRequest,
    BusinessMatchingResponse,
    ConfidenceLevel,
)


class BusinessMatchingService(BaseService):
    """Service for matching businesses across different data sources."""

    def __init__(self):
        super().__init__("BusinessMatchingService")
        self.logger.info("BusinessMatchingService initialized")

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if isinstance(data, BusinessMatchingRequest):
            return len(data.businesses) >= 2
        return False

    def match_businesses(
        self, request: BusinessMatchingRequest
    ) -> BusinessMatchingResponse:
        """
        Match businesses using name similarity, address similarity, and coordinate proximity.

        Args:
            request: BusinessMatchingRequest containing businesses to match

        Returns:
            BusinessMatchingResponse with matched groups and unmatched businesses
        """
        try:
            if not self.validate_input(request):
                raise ValueError(
                    "Invalid input: must have at least 2 businesses to match"
                )

            self.log_operation("match_businesses", request.run_id)

            # Normalize business data
            normalized_businesses = self._normalize_businesses(request.businesses)

            # Find matches
            matched_groups, unmatched_businesses = self._find_matches(
                normalized_businesses,
                request.similarity_threshold,
                request.name_weight,
                request.address_weight,
                request.coordinate_weight,
            )

            # Create response
            response = BusinessMatchingResponse(
                success=True,
                total_businesses=len(request.businesses),
                matched_groups=matched_groups,
                unmatched_businesses=unmatched_businesses,
                matching_metadata={
                    "similarity_threshold": request.similarity_threshold,
                    "name_weight": request.name_weight,
                    "address_weight": request.address_weight,
                    "coordinate_weight": request.coordinate_weight,
                    "total_matches": len(matched_groups),
                    "total_unmatched": len(unmatched_businesses),
                    "processing_timestamp": datetime.utcnow().isoformat(),
                },
                run_id=request.run_id,
            )

            self.log_operation(
                "match_businesses_completed",
                request.run_id,
                total_matches=len(matched_groups),
                total_unmatched=len(unmatched_businesses),
            )

            return response

        except Exception as e:
            run_id = request.run_id if request else None
            self.log_error(e, "match_businesses", run_id)
            raise

    def _normalize_businesses(
        self, businesses: List[BusinessSourceData]
    ) -> List[BusinessSourceData]:
        """Normalize business data for consistent comparison."""
        normalized = []

        for business in businesses:
            # Create a copy to avoid modifying original
            normalized_business = business.model_copy()

            # Normalize name
            if normalized_business.name:
                normalized_business.name = self._normalize_business_name(
                    normalized_business.name
                )

            # Normalize address
            if normalized_business.location and normalized_business.location.address:
                normalized_business.location.address = self._normalize_address(
                    normalized_business.location.address
                )

            normalized.append(normalized_business)

        return normalized

    def _normalize_business_name(self, name: str) -> str:
        """Normalize business name for comparison."""
        if not name:
            return ""

        # Convert to lowercase
        normalized = name.lower()

        # Remove common business suffixes
        suffixes = [
            " inc",
            " llc",
            " ltd",
            " corp",
            " corporation",
            " company",
            " co",
            " & co",
            " & company",
            " & sons",
            " & daughters",
            " & associates",
        ]

        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[: -len(suffix)]

        # Remove punctuation and extra whitespace
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

        # Remove punctuation and extra whitespace
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _normalize_address(self, address: str) -> str:
        """Normalize address for comparison."""
        if not address:
            return ""

        # Convert to lowercase
        normalized = address.lower()

        # Remove common address abbreviations
        abbreviations = {
            "street": "st",
            "avenue": "ave",
            "road": "rd",
            "boulevard": "blvd",
            "drive": "dr",
            "lane": "ln",
            "court": "ct",
            "place": "pl",
            "north": "n",
            "south": "s",
            "east": "e",
            "west": "w",
            "northeast": "ne",
            "northwest": "nw",
            "southeast": "se",
            "southwest": "sw",
        }

        for full, abbr in abbreviations.items():
            normalized = re.sub(rf"\b{full}\b", abbr, normalized)

        # Remove punctuation and extra whitespace
        normalized = re.sub(r"[^\w\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()

        return normalized

    def _find_matches(
        self,
        businesses: List[BusinessSourceData],
        threshold: float,
        name_weight: float,
        address_weight: float,
        coordinate_weight: float,
    ) -> Tuple[List[List[BusinessMatchCandidate]], List[BusinessSourceData]]:
        """Find matches among businesses using similarity scoring."""
        matched_groups = []
        processed = set()

        for i, business in enumerate(businesses):
            if i in processed:
                continue

            # Find matches for current business
            matches = [business]
            processed.add(i)

            for j, other_business in enumerate(businesses[i + 1 :], i + 1):
                if j in processed:
                    continue

                # Calculate similarity score
                score = self._calculate_similarity_score(
                    business,
                    other_business,
                    name_weight,
                    address_weight,
                    coordinate_weight,
                )

                if score.combined_score >= threshold:
                    matches.append(other_business)
                    processed.add(j)

            # Create match group if we have multiple matches
            if len(matches) > 1:
                candidates = []
                for match in matches:
                    candidate = BusinessMatchCandidate(
                        source_data=match,
                        match_score=self._calculate_similarity_score(
                            business,
                            match,
                            name_weight,
                            address_weight,
                            coordinate_weight,
                        ),
                        is_duplicate=True,
                        needs_review=False,
                    )
                    candidates.append(candidate)

                matched_groups.append(candidates)
            else:
                # Single business, no matches
                pass

        # Find unmatched businesses
        unmatched = [
            businesses[i] for i in range(len(businesses)) if i not in processed
        ]

        return matched_groups, unmatched

    def _calculate_similarity_score(
        self,
        business1: BusinessSourceData,
        business2: BusinessSourceData,
        name_weight: float,
        address_weight: float,
        coordinate_weight: float,
    ) -> BusinessMatchScore:
        """Calculate similarity score between two businesses."""

        # Name similarity
        name_similarity = self._calculate_name_similarity(
            business1.name, business2.name
        )

        # Address similarity
        address_similarity = self._calculate_address_similarity(
            business1.location, business2.location
        )

        # Coordinate proximity
        coordinate_proximity = self._calculate_coordinate_proximity(
            business1.location, business2.location
        )

        # Combined weighted score
        combined_score = (
            name_similarity * name_weight
            + address_similarity * address_weight
            + coordinate_proximity * coordinate_weight
        )

        # Determine confidence level
        confidence_level = self._determine_confidence_level(combined_score)

        return BusinessMatchScore(
            name_similarity=name_similarity,
            address_similarity=address_similarity,
            coordinate_proximity=coordinate_proximity,
            combined_score=combined_score,
            confidence_level=confidence_level,
        )

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two business names."""
        if not name1 or not name2:
            return 0.0

        # Use fuzzy string matching
        ratio = fuzz.ratio(name1, name2) / 100.0
        partial_ratio = fuzz.partial_ratio(name1, name2) / 100.0
        token_sort_ratio = fuzz.token_sort_ratio(name1, name2) / 100.0
        token_set_ratio = fuzz.token_set_ratio(name1, name2) / 100.0

        # Take the highest ratio
        return max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)

    def _calculate_address_similarity(
        self, location1: BusinessLocation, location2: BusinessLocation
    ) -> float:
        """Calculate similarity between two addresses."""
        if not location1.address or not location2.address:
            return 0.0

        # Use fuzzy string matching for address comparison
        return fuzz.ratio(location1.address, location2.address) / 100.0

    def _calculate_coordinate_proximity(
        self, location1: BusinessLocation, location2: BusinessLocation
    ) -> float:
        """Calculate proximity between two coordinate pairs."""
        if (
            not location1.latitude
            or not location1.longitude
            or not location2.latitude
            or not location2.longitude
        ):
            return 0.0

        try:
            # Calculate distance in meters
            point1 = (location1.latitude, location1.longitude)
            point2 = (location2.latitude, location2.longitude)

            distance_meters = geodesic(point1, point2).meters

            # Convert distance to similarity score (closer = higher score)
            # Use exponential decay: score = e^(-distance/1000)
            # This gives high scores for nearby businesses and low scores for distant ones
            similarity = math.exp(-distance_meters / 1000.0)

            return max(0.0, min(1.0, similarity))

        except Exception as e:
            self.logger.warning(f"Error calculating coordinate proximity: {e}")
            return 0.0

    def _determine_confidence_level(self, score: float) -> ConfidenceLevel:
        """Determine confidence level based on similarity score."""
        if score >= 0.8:
            return ConfidenceLevel.HIGH
        elif score >= 0.6:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
