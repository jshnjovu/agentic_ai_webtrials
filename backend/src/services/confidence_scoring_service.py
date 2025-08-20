"""
Confidence scoring service for business data quality assessment.
Implements data confidence scoring algorithms and confidence level assignment.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import math

from ..core.base_service import BaseService
from ..schemas.business_matching import BusinessSourceData, BusinessLocation, BusinessContactInfo, ConfidenceLevel
from ..schemas.business_merging import DataCompletenessScore, MergedBusinessData, MergeConflict


class ConfidenceScoringService(BaseService):
    """Service for calculating data confidence scores and assigning confidence levels."""
    
    def __init__(self):
        super().__init__("ConfidenceScoringService")
        self.logger.info("ConfidenceScoringService initialized")
        
        # Confidence thresholds
        self.HIGH_CONFIDENCE_THRESHOLD = 0.8
        self.MEDIUM_CONFIDENCE_THRESHOLD = 0.6
        
        # Field weights for confidence calculation
        self.FIELD_WEIGHTS = {
            "name": 0.25,
            "location": 0.25,
            "contact_info": 0.20,
            "rating": 0.15,
            "categories": 0.10,
            "hours": 0.05
        }
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return data is not None
    
    def calculate_data_confidence(self, business_data: BusinessSourceData) -> float:
        """
        Calculate overall confidence score for business data from a single source.
        
        Args:
            business_data: Business data from a source
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            if not self.validate_input(business_data):
                return 0.0
            
            self.log_operation("calculate_data_confidence", getattr(business_data, 'run_id', None))
            
            # Calculate confidence for each field
            field_confidences = {
                "name": self._calculate_name_confidence(business_data.name),
                "location": self._calculate_location_confidence(business_data.location),
                "contact_info": self._calculate_contact_confidence(business_data.contact_info),
                "rating": self._calculate_rating_confidence(business_data.rating),
                "categories": self._calculate_categories_confidence(business_data.categories),
                "hours": self._calculate_hours_confidence(business_data.hours)
            }
            
            # Calculate weighted average confidence
            total_confidence = 0.0
            total_weight = 0.0
            
            for field, weight in self.FIELD_WEIGHTS.items():
                if field in field_confidences:
                    total_confidence += field_confidences[field] * weight
                    total_weight += weight
            
            overall_confidence = total_confidence / total_weight if total_weight > 0 else 0.0
            
            self.logger.debug(f"Calculated confidence for {business_data.source}: {overall_confidence:.3f}")
            return round(overall_confidence, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating data confidence: {str(e)}")
            return 0.0
    
    def assign_confidence_level(self, confidence_score: float) -> ConfidenceLevel:
        """
        Assign confidence level based on confidence score.
        
        Args:
            confidence_score: Confidence score between 0.0 and 1.0
            
        Returns:
            ConfidenceLevel enum value
        """
        try:
            if confidence_score >= self.HIGH_CONFIDENCE_THRESHOLD:
                return ConfidenceLevel.HIGH
            elif confidence_score >= self.MEDIUM_CONFIDENCE_THRESHOLD:
                return ConfidenceLevel.MEDIUM
            else:
                return ConfidenceLevel.LOW
                
        except Exception as e:
            self.logger.error(f"Error assigning confidence level: {str(e)}")
            return ConfidenceLevel.LOW
    
    def calculate_merged_confidence(self, 
                                  completeness_scores: List[DataCompletenessScore],
                                  conflicts_resolved: List[MergeConflict]) -> float:
        """
        Calculate confidence score for merged business data.
        
        Args:
            completeness_scores: Data completeness scores from all sources
            conflicts_resolved: List of resolved conflicts during merging
            
        Returns:
            Merged confidence score between 0.0 and 1.0
        """
        try:
            if not completeness_scores:
                return 0.0
            
            self.log_operation("calculate_merged_confidence", None)
            
            # Base confidence from source completeness
            source_confidence = self._calculate_source_confidence(completeness_scores)
            
            # Conflict resolution confidence
            conflict_confidence = self._calculate_conflict_resolution_confidence(conflicts_resolved)
            
            # Data consistency confidence
            consistency_confidence = self._calculate_data_consistency_confidence(completeness_scores)
            
            # Weighted combination
            weights = {
                "source": 0.5,
                "conflict": 0.3,
                "consistency": 0.2
            }
            
            merged_confidence = (
                source_confidence * weights["source"] +
                conflict_confidence * weights["conflict"] +
                consistency_confidence * weights["consistency"]
            )
            
            self.logger.debug(f"Calculated merged confidence: {merged_confidence:.3f}")
            return round(merged_confidence, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating merged confidence: {str(e)}")
            return 0.0
    
    def add_confidence_indicators(self, merged_business: MergedBusinessData) -> Dict[str, Any]:
        """
        Add confidence indicators to merged business record.
        
        Args:
            merged_business: Merged business data
            
        Returns:
            Dictionary with confidence indicators
        """
        try:
            if not self.validate_input(merged_business):
                return {}
            
            self.log_operation("add_confidence_indicators", getattr(merged_business, 'run_id', None))
            
            confidence_indicators = {
                "overall_confidence": merged_business.confidence_level.value,
                "confidence_score": self._confidence_level_to_score(merged_business.confidence_level),
                "review_required": merged_business.needs_review,
                "data_quality": self._assess_data_quality(merged_business),
                "source_reliability": self._assess_source_reliability(merged_business),
                "last_assessment": datetime.now().isoformat()
            }
            
            self.logger.debug(f"Added confidence indicators for business {merged_business.business_id}")
            return confidence_indicators
            
        except Exception as e:
            self.logger.error(f"Error adding confidence indicators: {str(e)}")
            return {}
    
    def calculate_enhanced_confidence(self, website_url: str, business_data: Dict[str, Any], run_id: Optional[str] = None) -> float:
        """
        Calculate enhanced confidence score using UnifiedAnalyzer technical metrics combined with business confidence logic.
        
        Args:
            website_url: URL of the website to analyze
            business_data: Business data for confidence calculation
            run_id: Optional run identifier for tracking
            
        Returns:
            Enhanced confidence score between 0.0 and 1.0
        """
        try:
            if not self.validate_input(business_data):
                return 0.0
            
            self.log_operation("calculate_enhanced_confidence", run_id)
            
            # Calculate base business confidence
            business_confidence = self.calculate_data_confidence(business_data)
            
            # Note: UnifiedAnalyzer integration would be async, so this is a placeholder
            # In a real implementation, you would call:
            # unified_result = await self.unified_analyzer.run_comprehensive_analysis(website_url)
            # technical_score = unified_result.get("scores", {}).get("overall", 0) / 100.0
            
            # For now, use a simplified technical score based on business data
            technical_score = self._estimate_technical_score(business_data)
            
            # Weighted combination: 60% business confidence, 40% technical confidence
            enhanced_confidence = (business_confidence * 0.6) + (technical_score * 0.4)
            
            self.logger.debug(f"Enhanced confidence calculation: business={business_confidence:.3f}, technical={technical_score:.3f}, final={enhanced_confidence:.3f}")
            return round(enhanced_confidence, 3)
            
        except Exception as e:
            self.logger.error(f"Error calculating enhanced confidence: {str(e)}")
            return 0.0
    
    def _estimate_technical_score(self, business_data: Dict[str, Any]) -> float:
        """
        Estimate technical score based on business data quality indicators.
        This is a simplified approach - in production, use UnifiedAnalyzer for real technical analysis.
        """
        try:
            score = 0.0
            total_indicators = 0
            
            # Website presence
            if business_data.get("website"):
                score += 0.8
                total_indicators += 1
                
                # Basic website quality indicators
                website = business_data["website"]
                if website.startswith("https://"):
                    score += 0.1
                if "www." in website:
                    score += 0.05
                if len(website) > 10:  # Reasonable length
                    score += 0.05
                total_indicators += 3
            
            # Contact information quality
            contact_info = business_data.get("contact_info", {})
            if contact_info:
                if contact_info.get("phone"):
                    score += 0.7
                    total_indicators += 1
                if contact_info.get("email"):
                    score += 0.6
                    total_indicators += 1
                if contact_info.get("website"):
                    score += 0.5
                    total_indicators += 1
            
            # Location data quality
            location = business_data.get("location", {})
            if location:
                if location.get("address"):
                    score += 0.6
                    total_indicators += 1
                if location.get("latitude") and location.get("longitude"):
                    score += 0.8
                    total_indicators += 1
                if location.get("city") and location.get("state"):
                    score += 0.5
                    total_indicators += 1
            
            # Business information quality
            if business_data.get("name"):
                score += 0.7
                total_indicators += 1
            if business_data.get("categories"):
                score += 0.5
                total_indicators += 1
            if business_data.get("rating") is not None:
                score += 0.6
                total_indicators += 1
            
            # Calculate average score
            if total_indicators > 0:
                return min(1.0, score / total_indicators)
            else:
                return 0.0
                
        except Exception as e:
            self.logger.error(f"Error estimating technical score: {str(e)}")
            return 0.0
    
    async def calculate_unified_confidence(self, website_url: str, business_data: Dict[str, Any], run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate confidence score using UnifiedAnalyzer for comprehensive technical analysis.
        This method requires UnifiedAnalyzer to be available and properly configured.
        
        Args:
            website_url: URL of the website to analyze
            business_data: Business data for confidence calculation
            run_id: Optional run identifier for tracking
            
        Returns:
            Dictionary with comprehensive confidence metrics
        """
        try:
            if not self.validate_input(business_data):
                return {"error": "Invalid business data"}
            
            self.log_operation("calculate_unified_confidence", run_id)
            
            # Calculate base business confidence
            business_confidence = self.calculate_data_confidence(business_data)
            
            # Note: This is a placeholder for the UnifiedAnalyzer integration
            # In production, you would:
            # 1. Import UnifiedAnalyzer
            # 2. Run comprehensive analysis
            # 3. Extract technical metrics
            # 4. Combine with business confidence
            
            # Placeholder technical analysis result
            technical_analysis = {
                "performance_score": 0.0,
                "accessibility_score": 0.0,
                "seo_score": 0.0,
                "trust_score": 0.0,
                "overall_technical_score": 0.0,
                "analysis_available": False,
                "note": "UnifiedAnalyzer integration required for real technical analysis"
            }
            
            # Calculate enhanced confidence (placeholder)
            enhanced_confidence = business_confidence * 0.8  # 80% business, 20% technical (placeholder)
            
            # Determine confidence level
            confidence_level = self.assign_confidence_level(enhanced_confidence)
            
            result = {
                "business_confidence": business_confidence,
                "technical_analysis": technical_analysis,
                "enhanced_confidence": enhanced_confidence,
                "confidence_level": confidence_level.value,
                "calculation_method": "unified_analysis_placeholder",
                "recommendations": self._generate_confidence_recommendations(enhanced_confidence, business_confidence),
                "run_id": run_id
            }
            
            self.logger.info(f"Unified confidence calculation completed: {enhanced_confidence:.3f} ({confidence_level.value})")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating unified confidence: {str(e)}")
            return {"error": f"Confidence calculation failed: {str(e)}"}
    
    def _generate_confidence_recommendations(self, enhanced_confidence: float, business_confidence: float) -> List[str]:
        """Generate recommendations for improving confidence scores."""
        recommendations = []
        
        if enhanced_confidence < 0.6:
            recommendations.append("Consider manual review of business data quality")
            if business_confidence < 0.5:
                recommendations.append("Improve business data completeness (contact info, location, categories)")
            if enhanced_confidence < 0.4:
                recommendations.append("Website analysis recommended for technical confidence assessment")
        
        if business_confidence < 0.7:
            recommendations.append("Verify business information accuracy and completeness")
        
        if enhanced_confidence >= 0.8:
            recommendations.append("High confidence achieved - data quality is excellent")
        
        return recommendations
    
    def _calculate_name_confidence(self, name: str) -> float:
        """Calculate confidence score for business name."""
        if not name or not name.strip():
            return 0.0
        
        name = name.strip()
        
        # Length confidence (longer names are more specific)
        length_confidence = min(len(name) / 50.0, 1.0)
        
        # Format confidence (proper capitalization, no excessive spaces)
        format_confidence = 1.0
        if name != name.title() and name != name.upper():
            format_confidence = 0.8
        
        # Special characters confidence (fewer special chars = higher confidence)
        special_chars = sum(1 for c in name if not c.isalnum() and not c.isspace())
        char_confidence = max(1.0 - (special_chars / len(name)), 0.5)
        
        return (length_confidence + format_confidence + char_confidence) / 3.0
    
    def _calculate_location_confidence(self, location: BusinessLocation) -> float:
        """Calculate confidence score for business location."""
        if not location:
            return 0.0
        
        confidence_factors = []
        
        # Coordinate confidence
        if location.latitude is not None and location.longitude is not None:
            # Check if coordinates are within valid ranges
            if -90 <= location.latitude <= 90 and -180 <= location.longitude <= 180:
                confidence_factors.append(1.0)
            else:
                confidence_factors.append(0.0)
        else:
            confidence_factors.append(0.0)
        
        # Address completeness
        address_fields = [location.address, location.city, location.state, location.zip_code]
        address_completeness = sum(1 for field in address_fields if field and field.strip()) / len(address_fields)
        confidence_factors.append(address_completeness)
        
        return sum(confidence_factors) / len(confidence_factors)
    
    def _calculate_contact_confidence(self, contact_info: Optional[BusinessContactInfo]) -> float:
        """Calculate confidence score for contact information."""
        if not contact_info:
            return 0.0
        
        contact_fields = [
            contact_info.phone,
            contact_info.website,
            contact_info.email
        ]
        
        # Count non-empty fields
        filled_fields = sum(1 for field in contact_fields if field and field.strip())
        
        # Basic validation for filled fields
        valid_fields = 0
        for field in contact_fields:
            if field and field.strip():
                if self._validate_contact_field(field):
                    valid_fields += 1
        
        return valid_fields / len(contact_fields) if contact_fields else 0.0
    
    def _calculate_rating_confidence(self, rating: Optional[float]) -> float:
        """Calculate confidence score for business rating."""
        if rating is None:
            return 0.0
        
        # Rating should be between 0.0 and 5.0
        if 0.0 <= rating <= 5.0:
            return 1.0
        else:
            return 0.0
    
    def _calculate_categories_confidence(self, categories: Optional[List[str]]) -> float:
        """Calculate confidence score for business categories."""
        if not categories:
            return 0.0
        
        # More categories generally indicate better data
        category_count = len(categories)
        if category_count == 0:
            return 0.0
        elif category_count == 1:
            return 0.7
        elif category_count <= 3:
            return 0.9
        else:
            return 1.0
    
    def _calculate_hours_confidence(self, hours: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence score for business hours."""
        if not hours:
            return 0.0
        
        # Check if hours have proper structure
        if isinstance(hours, dict) and len(hours) > 0:
            return 0.8
        else:
            return 0.0
    
    def _calculate_source_confidence(self, completeness_scores: List[DataCompletenessScore]) -> float:
        """Calculate confidence based on source data completeness."""
        if not completeness_scores:
            return 0.0
        
        # Average completeness across all sources
        total_completeness = sum(score.overall_score for score in completeness_scores)
        return total_completeness / len(completeness_scores)
    
    def _calculate_conflict_resolution_confidence(self, conflicts_resolved: List[MergeConflict]) -> float:
        """Calculate confidence based on conflict resolution quality."""
        if not conflicts_resolved:
            return 1.0  # No conflicts = high confidence
        
        # Average confidence in conflict resolutions
        total_confidence = sum(conflict.confidence for conflict in conflicts_resolved)
        return total_confidence / len(conflicts_resolved)
    
    def _calculate_data_consistency_confidence(self, completeness_scores: List[DataCompletenessScore]) -> float:
        """Calculate confidence based on data consistency across sources."""
        if len(completeness_scores) < 2:
            return 1.0  # Single source = no consistency issues
        
        # Check variance in completeness scores
        scores = [score.overall_score for score in completeness_scores]
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # Lower variance = higher consistency confidence
        consistency_confidence = max(1.0 - math.sqrt(variance), 0.5)
        return consistency_confidence
    
    def _confidence_level_to_score(self, confidence_level: ConfidenceLevel) -> float:
        """Convert confidence level to numeric score."""
        level_scores = {
            ConfidenceLevel.HIGH: 0.9,
            ConfidenceLevel.MEDIUM: 0.7,
            ConfidenceLevel.LOW: 0.4
        }
        return level_scores.get(confidence_level, 0.5)
    
    def _assess_data_quality(self, merged_business: MergedBusinessData) -> str:
        """Assess overall data quality."""
        if merged_business.confidence_level == ConfidenceLevel.HIGH:
            return "excellent"
        elif merged_business.confidence_level == ConfidenceLevel.MEDIUM:
            return "good"
        else:
            return "fair"
    
    def _assess_source_reliability(self, merged_business: MergedBusinessData) -> str:
        """Assess source reliability based on number of sources."""
        source_count = len(merged_business.source_contributions)
        if source_count >= 3:
            return "high"
        elif source_count == 2:
            return "medium"
        else:
            return "low"
    
    def _validate_contact_field(self, field_value: str) -> bool:
        """Basic validation for contact field values."""
        field_value = field_value.strip()
        
        # Phone number validation (basic)
        if field_value.startswith('+') or field_value.replace('-', '').replace('(', '').replace(')', '').replace(' ', '').isdigit():
            return True
        
        # Email validation (basic)
        if '@' in field_value and '.' in field_value.split('@')[1]:
            return True
        
        # Website validation (basic)
        if field_value.startswith(('http://', 'https://', 'www.')):
            # Check if there's a domain after the protocol
            if field_value.startswith('http://') and len(field_value) > 7:
                domain_part = field_value[7:]
                if '.' in domain_part and len(domain_part.split('.')[0]) > 0:
                    return True
            elif field_value.startswith('https://') and len(field_value) > 8:
                domain_part = field_value[8:]
                if '.' in domain_part and len(domain_part.split('.')[0]) > 0:
                    return True
            elif field_value.startswith('www.') and len(field_value) > 4:
                domain_part = field_value[4:]
                if '.' in domain_part and len(domain_part.split('.')[0]) > 0:
                    return True
            return False
        
        return False
