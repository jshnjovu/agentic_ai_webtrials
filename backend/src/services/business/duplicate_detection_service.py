"""
Duplicate detection service for identifying and removing duplicate business records.
Implements business fingerprinting, duplicate detection algorithms, and removal strategies.
"""

import logging
import hashlib
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from ...core.base_service import BaseService
from ...schemas.business_matching import BusinessSourceData, BusinessLocation, BusinessContactInfo, ConfidenceLevel
from ...schemas.duplicate_detection import (
    BusinessFingerprint,
    DuplicateType,
    DuplicateGroup,
    DuplicateDetectionRequest,
    DuplicateDetectionResponse,
    DuplicateRemovalRequest,
    DuplicateRemovalResponse
)


class DuplicateDetectionService(BaseService):
    """Service for detecting and removing duplicate business records."""
    
    def __init__(self):
        super().__init__("DuplicateDetectionService")
        self.logger.info("DuplicateDetectionService initialized")
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if isinstance(data, (DuplicateDetectionRequest, DuplicateRemovalRequest)):
            return len(data.businesses) >= 1 if hasattr(data, 'businesses') else len(data.duplicate_groups) >= 1
        return False
    
    def detect_duplicates(self, request: DuplicateDetectionRequest) -> DuplicateDetectionResponse:
        """
        Detect duplicate businesses using fingerprinting and similarity algorithms.
        
        Args:
            request: DuplicateDetectionRequest containing businesses to check
            
        Returns:
            DuplicateDetectionResponse with duplicate groups and unique businesses
        """
        try:
            if not self.validate_input(request):
                raise ValueError("Invalid input: must have at least 1 business to check")
            
            self.log_operation("detect_duplicates", request.run_id)
            
            # Generate fingerprints for all businesses
            fingerprints = self._generate_fingerprints(request.businesses)
            
            # Detect duplicate groups
            duplicate_groups = self._detect_duplicate_groups(
                request.businesses, 
                fingerprints, 
                request.detection_threshold
            )
            
            # Identify unique businesses (not in any duplicate group)
            unique_businesses = self._identify_unique_businesses(
                request.businesses, duplicate_groups
            )
            
            # Handle automatic removal for high-confidence duplicates
            removed_duplicates = []
            if request.auto_remove_high_confidence:
                removed_duplicates = self._auto_remove_high_confidence_duplicates(
                    duplicate_groups, request.detection_threshold
                )
            
            response = DuplicateDetectionResponse(
                success=True,
                total_businesses=len(request.businesses),
                duplicate_groups=duplicate_groups,
                unique_businesses=unique_businesses,
                removed_duplicates=removed_duplicates,
                detection_metadata={
                    "detection_threshold": request.detection_threshold,
                    "auto_remove_enabled": request.auto_remove_high_confidence,
                    "total_duplicate_groups": len(duplicate_groups),
                    "total_unique_businesses": len(unique_businesses),
                    "total_removed_duplicates": len(removed_duplicates),
                    "processing_timestamp": datetime.utcnow().isoformat()
                },
                run_id=request.run_id
            )
            
            self.log_operation("detect_duplicates_completed", request.run_id,
                             total_duplicates=len(duplicate_groups),
                             total_unique=len(unique_businesses),
                             total_removed=len(removed_duplicates))
            
            return response
            
        except Exception as e:
            self.log_error(e, "detect_duplicates", request.run_id)
            raise
    
    def remove_duplicates(self, request: DuplicateRemovalRequest) -> DuplicateRemovalResponse:
        """
        Remove duplicate businesses based on specified strategy.
        
        Args:
            request: DuplicateRemovalRequest containing duplicate groups to process
            
        Returns:
            DuplicateRemovalResponse with removal results and review requirements
        """
        try:
            if not self.validate_input(request):
                raise ValueError("Invalid input: must have at least 1 duplicate group to process")
            
            self.log_operation("remove_duplicates", request.run_id)
            
            duplicates_removed = []
            businesses_kept = []
            review_required = []
            
            for group in request.duplicate_groups:
                if group.confidence_score >= request.review_threshold:
                    # High confidence - remove duplicates, keep primary
                    duplicates_removed.extend(group.duplicate_businesses)
                    businesses_kept.append(group.primary_business)
                else:
                    # Low confidence - flag for manual review
                    group.needs_review = True
                    review_required.append(group)
            
            response = DuplicateRemovalResponse(
                success=True,
                total_groups_processed=len(request.duplicate_groups),
                duplicates_removed=duplicates_removed,
                businesses_kept=businesses_kept,
                review_required=review_required,
                removal_metadata={
                    "removal_strategy": request.removal_strategy,
                    "review_threshold": request.review_threshold,
                    "total_removed": len(duplicates_removed),
                    "total_kept": len(businesses_kept),
                    "total_review_required": len(review_required),
                    "processing_timestamp": datetime.utcnow().isoformat()
                },
                run_id=request.run_id
            )
            
            self.log_operation("remove_duplicates_completed", request.run_id,
                             total_removed=len(duplicates_removed),
                             total_kept=len(businesses_kept),
                             total_review=len(review_required))
            
            return response
            
        except Exception as e:
            self.log_error(e, "remove_duplicates", request.run_id)
            raise
    
    def _generate_fingerprints(self, businesses: List[BusinessSourceData]) -> List[BusinessFingerprint]:
        """Generate fingerprints for all businesses."""
        fingerprints = []
        
        for business in businesses:
            fingerprint = BusinessFingerprint(
                business_id=business.source_id,
                name_normalized=self._normalize_business_name(business.name),
                address_normalized=self._normalize_address(business.location.address) if business.location and business.location.address else "",
                phone_normalized=self._normalize_phone(business.contact_info.phone) if business.contact_info and business.contact_info.phone else None,
                website_normalized=self._normalize_website(business.contact_info.website) if business.contact_info and business.contact_info.website else None,
                coordinate_hash=self._generate_coordinate_hash(business.location) if business.location else "",
                category_signature=self._generate_category_signature(business.categories),
                fingerprint_hash="",  # Will be calculated below
                created_at=datetime.utcnow().isoformat()
            )
            
            # Generate overall fingerprint hash
            fingerprint.fingerprint_hash = self._generate_fingerprint_hash(fingerprint)
            fingerprints.append(fingerprint)
        
        return fingerprints
    
    def _normalize_business_name(self, name: str) -> str:
        """Normalize business name for fingerprinting."""
        if not name:
            return ""
        
        # Convert to lowercase and remove common business suffixes
        normalized = name.lower()
        suffixes = [
            ' inc', ' llc', ' ltd', ' corp', ' corporation', ' company', ' co',
            ' & co', ' & company', ' & sons', ' & daughters', ' & associates'
        ]
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        # Remove punctuation and extra whitespace
        import re
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _normalize_address(self, address: str) -> str:
        """Normalize address for fingerprinting."""
        if not address:
            return ""
        
        # Convert to lowercase
        normalized = address.lower()
        
        # Remove common address abbreviations
        abbreviations = {
            'street': 'st',
            'avenue': 'ave',
            'road': 'rd',
            'boulevard': 'blvd',
            'drive': 'dr',
            'lane': 'ln',
            'court': 'ct',
            'place': 'pl',
            'north': 'n',
            'south': 's',
            'east': 'e',
            'west': 'w',
            'northeast': 'ne',
            'northwest': 'nw',
            'southeast': 'se',
            'southwest': 'sw'
        }
        
        import re
        for full, abbr in abbreviations.items():
            normalized = re.sub(rf'\b{full}\b', abbr, normalized)
        
        # Remove punctuation and extra whitespace
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for fingerprinting."""
        if not phone:
            return None
        
        # Remove all non-digit characters
        import re
        normalized = re.sub(r'[^\d]', '', phone)
        
        # Handle international numbers (remove country code if present)
        if len(normalized) > 10:
            normalized = normalized[-10:]  # Keep last 10 digits
        
        return normalized if normalized else None
    
    def _normalize_website(self, website: str) -> str:
        """Normalize website for fingerprinting."""
        if not website:
            return None
        
        # Convert to lowercase and remove protocol
        normalized = website.lower()
        if normalized.startswith(('http://', 'https://')):
            normalized = normalized.split('://', 1)[1]
        
        # Remove www prefix
        if normalized.startswith('www.'):
            normalized = normalized[4:]
        
        # Remove trailing slash
        normalized = normalized.rstrip('/')
        
        return normalized
    
    def _generate_coordinate_hash(self, location: BusinessLocation) -> str:
        """Generate hash for coordinates."""
        if not location or not location.latitude or not location.longitude:
            return ""
        
        # Round coordinates to reduce precision for proximity matching
        lat_rounded = round(location.latitude, 4)  # ~11 meters precision
        lon_rounded = round(location.longitude, 4)
        
        coordinate_string = f"{lat_rounded:.4f},{lon_rounded:.4f}"
        return hashlib.md5(coordinate_string.encode()).hexdigest()
    
    def _generate_category_signature(self, categories: Optional[List[str]]) -> str:
        """Generate signature for business categories."""
        if not categories:
            return ""
        
        # Sort categories for consistent signature
        sorted_categories = sorted([cat.lower().strip() for cat in categories if cat])
        categories_string = "|".join(sorted_categories)
        
        return hashlib.md5(categories_string.encode()).hexdigest()
    
    def _generate_fingerprint_hash(self, fingerprint: BusinessFingerprint) -> str:
        """Generate overall fingerprint hash."""
        # Combine all fingerprint components
        components = [
            fingerprint.name_normalized,
            fingerprint.address_normalized,
            fingerprint.phone_normalized or "",
            fingerprint.website_normalized or "",
            fingerprint.coordinate_hash,
            fingerprint.category_signature
        ]
        
        fingerprint_string = "|".join(components)
        return hashlib.md5(fingerprint_string.encode()).hexdigest()
    
    def _detect_duplicate_groups(self, businesses: List[BusinessSourceData],
                                fingerprints: List[BusinessFingerprint],
                                threshold: float) -> List[DuplicateGroup]:
        """Detect duplicate groups based on fingerprint similarity."""
        duplicate_groups = []
        processed = set()
        
        for i, fingerprint in enumerate(fingerprints):
            if i in processed:
                continue
            
            # Find matches for current fingerprint
            matches = [businesses[i]]
            processed.add(i)
            
            for j, other_fingerprint in enumerate(fingerprints[i+1:], i+1):
                if j in processed:
                    continue
                
                # Calculate similarity score
                similarity = self._calculate_fingerprint_similarity(fingerprint, other_fingerprint)
                
                if similarity >= threshold:
                    matches.append(businesses[j])
                    processed.add(j)
            
            # Create duplicate group if we have multiple matches
            if len(matches) > 1:
                # Determine primary business (first one)
                primary_business = matches[0]
                duplicate_businesses = matches[1:]
                
                # Calculate confidence score
                confidence_score = self._calculate_group_confidence(matches, fingerprints)
                
                # Determine duplicate type
                duplicate_type = self._determine_duplicate_type(confidence_score)
                
                group = DuplicateGroup(
                    group_id=str(uuid.uuid4()),
                    primary_business=primary_business,
                    duplicate_businesses=duplicate_businesses,
                    duplicate_type=duplicate_type,
                    confidence_score=confidence_score,
                    detection_method="fingerprint_similarity",
                    detection_metadata={
                        "similarity_threshold": threshold,
                        "total_matches": len(matches),
                        "fingerprint_hashes": [f.fingerprint_hash for f in fingerprints if f.business_id in [b.source_id for b in matches]]
                    },
                    created_at=datetime.utcnow().isoformat(),
                    needs_review=confidence_score < threshold + 0.1  # Flag for review if close to threshold
                )
                
                duplicate_groups.append(group)
        
        return duplicate_groups
    
    def _calculate_fingerprint_similarity(self, fp1: BusinessFingerprint, fp2: BusinessFingerprint) -> float:
        """Calculate similarity between two fingerprints."""
        similarities = []
        
        # Name similarity
        if fp1.name_normalized and fp2.name_normalized:
            name_sim = self._calculate_string_similarity(fp1.name_normalized, fp2.name_normalized)
            similarities.append(name_sim * 0.3)  # 30% weight
        
        # Address similarity
        if fp1.address_normalized and fp2.address_normalized:
            addr_sim = self._calculate_string_similarity(fp1.address_normalized, fp2.address_normalized)
            similarities.append(addr_sim * 0.25)  # 25% weight
        
        # Phone similarity
        if fp1.phone_normalized and fp2.phone_normalized:
            phone_sim = 1.0 if fp1.phone_normalized == fp2.phone_normalized else 0.0
            similarities.append(phone_sim * 0.2)  # 20% weight
        
        # Website similarity
        if fp1.website_normalized and fp2.website_normalized:
            website_sim = 1.0 if fp1.website_normalized == fp2.website_normalized else 0.0
            similarities.append(website_sim * 0.15)  # 15% weight
        
        # Coordinate similarity
        if fp1.coordinate_hash and fp2.coordinate_hash:
            coord_sim = 1.0 if fp1.coordinate_hash == fp2.coordinate_hash else 0.0
            similarities.append(coord_sim * 0.1)  # 10% weight
        
        # Return average similarity
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using fuzzy matching."""
        from fuzzywuzzy import fuzz
        
        # Use multiple fuzzy matching algorithms
        ratio = fuzz.ratio(str1, str2) / 100.0
        partial_ratio = fuzz.partial_ratio(str1, str2) / 100.0
        token_sort_ratio = fuzz.token_sort_ratio(str1, str2) / 100.0
        token_set_ratio = fuzz.token_set_ratio(str1, str2) / 100.0
        
        # Return the highest similarity score
        return max(ratio, partial_ratio, token_sort_ratio, token_set_ratio)
    
    def _calculate_group_confidence(self, businesses: List[BusinessSourceData],
                                   fingerprints: List[BusinessFingerprint]) -> float:
        """Calculate confidence score for a duplicate group."""
        if len(businesses) < 2:
            return 0.0
        
        # Calculate average similarity between all pairs in the group
        similarities = []
        
        for i in range(len(businesses)):
            for j in range(i + 1, len(businesses)):
                fp1 = next(f for f in fingerprints if f.business_id == businesses[i].source_id)
                fp2 = next(f for f in fingerprints if f.business_id == businesses[j].source_id)
                similarity = self._calculate_fingerprint_similarity(fp1, fp2)
                similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _determine_duplicate_type(self, confidence_score: float) -> DuplicateType:
        """Determine duplicate type based on confidence score."""
        if confidence_score >= 0.95:
            return DuplicateType.EXACT_MATCH
        elif confidence_score >= 0.85:
            return DuplicateType.HIGH_SIMILARITY
        elif confidence_score >= 0.75:
            return DuplicateType.MEDIUM_SIMILARITY
        elif confidence_score >= 0.65:
            return DuplicateType.LOW_SIMILARITY
        else:
            return DuplicateType.POTENTIAL_DUPLICATE
    
    def _identify_unique_businesses(self, businesses: List[BusinessSourceData],
                                   duplicate_groups: List[DuplicateGroup]) -> List[BusinessSourceData]:
        """Identify businesses that are not part of any duplicate group."""
        # Get all business IDs that are in duplicate groups
        duplicate_ids = set()
        for group in duplicate_groups:
            duplicate_ids.add(group.primary_business.source_id)
            for duplicate in group.duplicate_businesses:
                duplicate_ids.add(duplicate.source_id)
        
        # Return businesses not in duplicate groups
        return [b for b in businesses if b.source_id not in duplicate_ids]
    
    def _auto_remove_high_confidence_duplicates(self, duplicate_groups: List[DuplicateGroup],
                                               threshold: float) -> List[BusinessSourceData]:
        """Automatically remove high-confidence duplicates."""
        removed = []
        
        for group in duplicate_groups:
            if group.confidence_score >= threshold + 0.1:  # Higher threshold for auto-removal
                removed.extend(group.duplicate_businesses)
        
        return removed
