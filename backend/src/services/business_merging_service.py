"""
Business merging service for combining business data from multiple sources.
Implements contact information prioritization, data completeness scoring, and merge strategies.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid

from ..core.base_service import BaseService
from ..schemas.business_matching import BusinessSourceData, BusinessLocation, BusinessContactInfo, ConfidenceLevel
from ..schemas.business_merging import (
    DataCompletenessScore,
    MergedBusinessData,
    MergeConflict,
    BusinessMergeRequest,
    BusinessMergeResponse
)
from ..services.confidence_scoring_service import ConfidenceScoringService
from ..services.review_management_service import ReviewManagementService


class BusinessMergingService(BaseService):
    """Service for merging business data from multiple sources."""
    
    def __init__(self):
        super().__init__("BusinessMergingService")
        self.logger.info("BusinessMergingService initialized")
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if isinstance(data, BusinessMergeRequest):
            return len(data.businesses) >= 2
        return False
    
    def merge_businesses(self, request: BusinessMergeRequest) -> BusinessMergeResponse:
        """
        Merge business data from multiple sources using prioritization and conflict resolution.
        
        Args:
            request: BusinessMergeRequest containing businesses to merge
            
        Returns:
            BusinessMergeResponse with merged business data and conflict resolution details
        """
        try:
            if not self.validate_input(request):
                raise ValueError("Invalid input: must have at least 2 businesses to merge")
            
            self.log_operation("merge_businesses", request.run_id)
            
            # Calculate data completeness scores for each source
            completeness_scores = self._calculate_completeness_scores(request.businesses)
            
            # Determine primary business based on completeness and prioritization
            primary_business = self._determine_primary_business(
                request.businesses, 
                completeness_scores, 
                request.prioritize_source
            )
            
            # Merge business data
            merged_data, conflicts_resolved = self._merge_business_data(
                request.businesses,
                primary_business,
                completeness_scores,
                request.merge_strategy
            )
            
            # Create merged business record
            merged_business = MergedBusinessData(
                business_id=str(uuid.uuid4()),
                name=merged_data["name"],
                location=merged_data["location"],
                contact_info=merged_data["contact_info"],
                rating=merged_data["rating"],
                review_count=merged_data["review_count"],
                categories=merged_data["categories"],
                price_level=merged_data["price_level"],
                hours=merged_data["hours"],
                photos=merged_data["photos"],
                confidence_level=self._determine_merged_confidence(conflicts_resolved),
                source_contributions=[b.source for b in request.businesses],
                merge_metadata={
                    "merge_strategy": request.merge_strategy,
                    "prioritize_source": request.prioritize_source,
                    "completeness_scores": {score.source: score.overall_score for score in completeness_scores},
                    "conflicts_count": len(conflicts_resolved),
                    "merge_timestamp": datetime.utcnow().isoformat()
                },
                last_updated=datetime.utcnow().isoformat(),
                needs_review=self._determine_if_review_needed(merged_business, conflicts_resolved, completeness_scores)
            )
            
            response = BusinessMergeResponse(
                success=True,
                merged_business=merged_business,
                conflicts_resolved=conflicts_resolved,
                merge_metadata={
                    "total_sources": len(request.businesses),
                    "merge_strategy": request.merge_strategy,
                    "conflicts_resolved": len(conflicts_resolved),
                    "processing_timestamp": datetime.utcnow().isoformat()
                },
                run_id=request.run_id
            )
            
            self.log_operation("merge_businesses_completed", request.run_id,
                             total_sources=len(request.businesses),
                             conflicts_resolved=len(conflicts_resolved))
            
            return response
            
        except Exception as e:
            self.log_error(e, "merge_businesses", request.run_id)
            raise
    
    def _calculate_completeness_scores(self, businesses: List[BusinessSourceData]) -> List[DataCompletenessScore]:
        """Calculate data completeness scores for each business source."""
        scores = []
        
        for business in businesses:
            # Name completeness
            name_score = 1.0 if business.name and business.name.strip() else 0.0
            
            # Location completeness
            location_score = self._calculate_location_completeness(business.location)
            
            # Contact information completeness
            contact_score = self._calculate_contact_completeness(business.contact_info)
            
            # Rating and review completeness
            rating_score = self._calculate_rating_completeness(business.rating, business.review_count)
            
            # Category completeness
            category_score = self._calculate_category_completeness(business.categories)
            
            # Calculate overall score (weighted average)
            overall_score = (
                name_score * 0.2 +
                location_score * 0.3 +
                contact_score * 0.25 +
                rating_score * 0.15 +
                category_score * 0.1
            )
            
            score = DataCompletenessScore(
                source=business.source,
                overall_score=overall_score,
                name_score=name_score,
                location_score=location_score,
                contact_score=contact_score,
                rating_score=rating_score,
                category_score=category_score,
                details={
                    "name": name_score,
                    "location": location_score,
                    "contact": contact_score,
                    "rating": rating_score,
                    "category": category_score
                }
            )
            
            scores.append(score)
        
        return scores
    
    def _calculate_location_completeness(self, location: BusinessLocation) -> float:
        """Calculate completeness score for location data."""
        if not location:
            return 0.0
        
        score = 0.0
        total_fields = 0
        
        # Required fields
        if location.latitude and location.longitude:
            score += 1.0
        total_fields += 1
        
        if location.address:
            score += 1.0
        total_fields += 1
        
        # Optional fields
        if location.city:
            score += 0.5
        total_fields += 0.5
        
        if location.state:
            score += 0.5
        total_fields += 0.5
        
        if location.zip_code:
            score += 0.5
        total_fields += 0.5
        
        if location.country:
            score += 0.5
        total_fields += 0.5
        
        return score / total_fields if total_fields > 0 else 0.0
    
    def _calculate_contact_completeness(self, contact_info: Optional[BusinessContactInfo]) -> float:
        """Calculate completeness score for contact information."""
        if not contact_info:
            return 0.0
        
        score = 0.0
        total_fields = 0
        
        if contact_info.phone:
            score += 1.0
        total_fields += 1
        
        if contact_info.website:
            score += 1.0
        total_fields += 1
        
        if contact_info.email:
            score += 1.0
        total_fields += 1
        
        if contact_info.social_media:
            score += 0.5
        total_fields += 0.5
        
        return score / total_fields if total_fields > 0 else 0.0
    
    def _calculate_rating_completeness(self, rating: Optional[float], review_count: Optional[int]) -> float:
        """Calculate completeness score for rating and review data."""
        score = 0.0
        total_fields = 0
        
        if rating is not None:
            score += 1.0
        total_fields += 1
        
        if review_count is not None:
            score += 1.0
        total_fields += 1
        
        return score / total_fields if total_fields > 0 else 0.0
    
    def _calculate_category_completeness(self, categories: Optional[List[str]]) -> float:
        """Calculate completeness score for category data."""
        if not categories:
            return 0.0
        
        # Score based on number of categories (more categories = higher score)
        if len(categories) >= 3:
            return 1.0
        elif len(categories) == 2:
            return 0.7
        elif len(categories) == 1:
            return 0.4
        else:
            return 0.0
    
    def _determine_primary_business(self, businesses: List[BusinessSourceData], 
                                   completeness_scores: List[DataCompletenessScore],
                                   prioritize_source: Optional[str]) -> BusinessSourceData:
        """Determine the primary business based on completeness and prioritization."""
        if prioritize_source:
            # Find business from prioritized source
            for business in businesses:
                if business.source == prioritize_source:
                    return business
        
        # Find business with highest completeness score
        best_score = max(completeness_scores, key=lambda x: x.overall_score)
        for business in businesses:
            if business.source == best_score.source:
                return business
        
        # Fallback to first business
        return businesses[0]
    
    def _merge_business_data(self, businesses: List[BusinessSourceData],
                            primary_business: BusinessSourceData,
                            completeness_scores: List[DataCompletenessScore],
                            merge_strategy: str) -> Tuple[Dict[str, Any], List[MergeConflict]]:
        """Merge business data using the specified strategy."""
        merged_data = {
            "name": primary_business.name,
            "location": primary_business.location,
            "contact_info": primary_business.contact_info,
            "rating": primary_business.rating,
            "review_count": primary_business.review_count,
            "categories": primary_business.categories or [],
            "price_level": primary_business.price_level,
            "hours": primary_business.hours,
            "photos": primary_business.photos or []
        }
        
        conflicts_resolved = []
        
        # Merge data from other sources
        for business in businesses:
            if business.source == primary_business.source:
                continue
            
            # Merge categories
            if business.categories:
                merged_data["categories"] = list(set(merged_data["categories"] + business.categories))
            
            # Merge photos
            if business.photos:
                merged_data["photos"].extend(business.photos)
            
            # Resolve conflicts for other fields
            conflicts = self._resolve_field_conflicts(
                merged_data, business, primary_business, merge_strategy
            )
            conflicts_resolved.extend(conflicts)
            
            # Update merged data with resolved conflicts
            for conflict in conflicts:
                if conflict.field_name in merged_data:
                    merged_data[conflict.field_name] = conflict.resolved_value
        
        return merged_data, conflicts_resolved
    
    def _resolve_field_conflicts(self, merged_data: Dict[str, Any],
                               business: BusinessSourceData,
                               primary_business: BusinessSourceData,
                               merge_strategy: str) -> List[MergeConflict]:
        """Resolve conflicts between merged data and new business data."""
        conflicts = []
        
        # Contact information conflicts
        if business.contact_info and merged_data["contact_info"]:
            conflicts.extend(self._resolve_contact_conflicts(
                merged_data["contact_info"], business.contact_info, merge_strategy
            ))
        
        # Rating conflicts
        if business.rating is not None and merged_data["rating"] is not None:
            if business.rating != merged_data["rating"]:
                conflict = self._resolve_rating_conflict(
                    merged_data["rating"], business.rating, merge_strategy
                )
                conflicts.append(conflict)
        
        # Price level conflicts
        if business.price_level is not None and merged_data["price_level"] is not None:
            if business.price_level != merged_data["price_level"]:
                conflict = self._resolve_price_conflict(
                    merged_data["price_level"], business.price_level, merge_strategy
                )
                conflicts.append(conflict)
        
        return conflicts
    
    def _resolve_contact_conflicts(self, primary_contact: BusinessContactInfo,
                                 business_contact: BusinessContactInfo,
                                 merge_strategy: str) -> List[MergeConflict]:
        """Resolve conflicts in contact information."""
        conflicts = []
        
        # Phone conflict
        if primary_contact.phone and business_contact.phone and primary_contact.phone != business_contact.phone:
            conflict = MergeConflict(
                field_name="phone",
                source_values={
                    "primary": primary_contact.phone,
                    "business": business_contact.phone
                },
                resolution_strategy=merge_strategy,
                resolved_value=primary_contact.phone,  # Keep primary
                confidence=0.8
            )
            conflicts.append(conflict)
        
        # Website conflict
        if primary_contact.website and business_contact.website and primary_contact.website != business_contact.website:
            conflict = MergeConflict(
                field_name="website",
                source_values={
                    "primary": primary_contact.website,
                    "business": business_contact.website
                },
                resolution_strategy=merge_strategy,
                resolved_value=primary_contact.website,  # Keep primary
                confidence=0.8
            )
            conflicts.append(conflict)
        
        # Email conflict
        if primary_contact.email and business_contact.email and primary_contact.email != business_contact.email:
            conflict = MergeConflict(
                field_name="email",
                source_values={
                    "primary": primary_contact.email,
                    "business": business_contact.email
                },
                resolution_strategy=merge_strategy,
                resolved_value=primary_contact.email,  # Keep primary
                confidence=0.8
            )
            conflicts.append(conflict)
        
        return conflicts
    
    def _resolve_rating_conflict(self, primary_rating: float, business_rating: float,
                                merge_strategy: str) -> MergeConflict:
        """Resolve rating conflicts."""
        if merge_strategy == "completeness":
            # Keep the rating with more reviews (assume primary has more)
            resolved_value = primary_rating
            confidence = 0.7
        else:
            # Keep primary rating
            resolved_value = primary_rating
            confidence = 0.8
        
        return MergeConflict(
            field_name="rating",
            source_values={
                "primary": primary_rating,
                "business": business_rating
            },
            resolution_strategy=merge_strategy,
            resolved_value=resolved_value,
            confidence=confidence
        )
    
    def _resolve_price_conflict(self, primary_price: int, business_price: int,
                               merge_strategy: str) -> MergeConflict:
        """Resolve price level conflicts."""
        # Keep primary price level
        return MergeConflict(
            field_name="price_level",
            source_values={
                "primary": primary_price,
                "business": business_price
            },
            resolution_strategy=merge_strategy,
            resolved_value=primary_price,
            confidence=0.8
        )
    
    def _determine_merged_confidence(self, conflicts_resolved: List[MergeConflict]) -> ConfidenceLevel:
        """Determine confidence level for merged data based on conflicts."""
        if not conflicts_resolved:
            return ConfidenceLevel.HIGH
        
        # Calculate average confidence
        avg_confidence = sum(conflict.confidence for conflict in conflicts_resolved) / len(conflicts_resolved)
        
        # Use confidence scoring service for more sophisticated confidence assessment
        confidence_service = ConfidenceScoringService()
        return confidence_service.assign_confidence_level(avg_confidence)
    
    def _determine_if_review_needed(self, 
                                   merged_business: MergedBusinessData,
                                   conflicts_resolved: List[MergeConflict],
                                   completeness_scores: List[DataCompletenessScore]) -> bool:
        """Determine if the merged business needs manual review."""
        try:
            # Use review management service to determine if review is needed
            review_service = ReviewManagementService()
            
            # Create a temporary merged business object for review assessment
            temp_merged = MergedBusinessData(
                business_id=merged_business.business_id,
                name=merged_business.name,
                location=merged_business.location,
                contact_info=merged_business.contact_info,
                rating=merged_business.rating,
                review_count=merged_business.review_count,
                categories=merged_business.categories,
                price_level=merged_business.price_level,
                hours=merged_business.hours,
                photos=merged_business.photos,
                confidence_level=merged_business.confidence_level,
                source_contributions=merged_business.source_contributions,
                merge_metadata=merged_business.merge_metadata,
                last_updated=merged_business.last_updated,
                needs_review=False  # Temporary value
            )
            
            # Check if review is needed using the review service
            review_flag = review_service.flag_uncertain_matches(
                temp_merged, 
                conflicts_resolved, 
                []  # Placeholder for source data
            )
            
            return review_flag is not None
            
        except Exception as e:
            self.logger.error(f"Error determining if review needed: {str(e)}")
            # Fallback to basic logic
            return (len(conflicts_resolved) > 0 and 
                   any(c.confidence < 0.7 for c in conflicts_resolved))
