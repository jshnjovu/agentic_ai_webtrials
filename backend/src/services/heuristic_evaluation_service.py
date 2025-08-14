"""
Heuristic evaluation service for website analysis.
Analyzes trust signals, CRO elements, mobile usability, content quality, and social proof.
"""

import time
from typing import Dict, Any, Optional
from src.core.base_service import BaseService
from src.core.config import get_api_config
from src.services.rate_limiter import RateLimiter
from src.schemas.website_scoring import (
    HeuristicScore, TrustSignals, CROElements, MobileUsability,
    ContentQuality, SocialProof, ConfidenceLevel
)


class HeuristicEvaluationService(BaseService):
    """Service for heuristic evaluation of websites."""
    
    def __init__(self):
        super().__init__("HeuristicEvaluationService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.timeout = self.api_config.HEURISTICS_EVALUATION_TIMEOUT_SECONDS
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if not isinstance(data, dict):
            return False
        
        required_fields = ['website_url', 'business_id']
        return all(field in data for field in required_fields)
    
    def run_heuristic_evaluation(
        self,
        website_url: str,
        business_id: str,
        run_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run comprehensive heuristic evaluation of a website.
        
        Args:
            website_url: URL of the website to evaluate
            business_id: Business identifier for tracking
            run_id: Run identifier for tracking
            
        Returns:
            Dictionary containing evaluation results and scores
        """
        start_time = time.time()
        
        try:
            self.log_operation(
                "Starting heuristic evaluation",
                run_id=run_id,
                business_id=business_id,
                website_url=website_url
            )
            
            # Check rate limiting
            can_proceed, message = self.rate_limiter.can_make_request("heuristics", run_id)
            if not can_proceed:
                self.log_operation(
                    f"Rate limit exceeded: {message}",
                    run_id=run_id,
                    business_id=business_id
                )
                return {
                    "success": False,
                    "error": f"Rate limit exceeded: {message}",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "context": "rate_limit_check",
                    "run_id": run_id,
                    "business_id": business_id
                }
            
            # For now, return mock evaluation results
            # In a real implementation, this would fetch and analyze the website
            trust_signals = TrustSignals(
                has_https=website_url.startswith('https'),
                has_privacy_policy=True,
                has_contact_info=True,
                has_about_page=False,
                has_terms_of_service=True,
                has_ssl_certificate=website_url.startswith('https'),
                has_business_address=True,
                has_phone_number=True,
                has_email=True
            )
            
            cro_elements = CROElements(
                has_cta_buttons=True,
                has_contact_forms=True,
                has_pricing_tables=False,
                has_testimonials=True,
                has_reviews=True,
                has_social_proof=True,
                has_urgency_elements=False,
                has_trust_badges=True
            )
            
            mobile_usability = MobileUsability(
                has_viewport_meta=True,
                has_touch_targets=True,
                has_responsive_design=True,
                has_mobile_navigation=False,
                has_readable_fonts=True,
                has_adequate_spacing=True
            )
            
            content_quality = ContentQuality(
                has_proper_headings=True,
                has_alt_text=True,
                has_meta_description=True,
                has_meta_keywords=False,
                has_structured_data=True,
                has_internal_links=True,
                has_external_links=False,
                has_blog_content=True
            )
            
            social_proof = SocialProof(
                has_social_media_links=True,
                has_customer_reviews=True,
                has_testimonials=True,
                has_case_studies=False,
                has_awards_certifications=True,
                has_partner_logos=False,
                has_user_generated_content=False
            )
            
            # Calculate scores
            scores = self._calculate_heuristic_scores(
                trust_signals, cro_elements, mobile_usability,
                content_quality, social_proof
            )
            
            # Record successful request
            self.rate_limiter.record_request("heuristics", True, run_id)
            
            evaluation_time = time.time() - start_time
            self.log_operation(
                f"Completed heuristic evaluation in {evaluation_time:.2f}s",
                run_id=run_id,
                business_id=business_id,
                evaluation_time=evaluation_time
            )
            
            return {
                "success": True,
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id,
                "evaluation_timestamp": time.time(),
                "scores": scores,
                "trust_signals": trust_signals.dict(),
                "cro_elements": cro_elements.dict(),
                "mobile_usability": mobile_usability.dict(),
                "content_quality": content_quality.dict(),
                "social_proof": social_proof.dict(),
                "confidence": scores.confidence_level.value,
                "raw_data": {
                    "html_length": 5000,
                    "evaluation_time": evaluation_time
                }
            }
            
        except Exception as e:
            # Record failed request
            self.rate_limiter.record_request("heuristics", False, run_id)
            
            self.log_error(
                e, "heuristic_evaluation", run_id, business_id
            )
            
            return {
                "success": False,
                "error": str(e),
                "error_code": "EVALUATION_FAILED",
                "context": "heuristic_evaluation",
                "run_id": run_id,
                "business_id": business_id
            }
    
    def _calculate_heuristic_scores(
        self,
        trust_signals: TrustSignals,
        cro_elements: CROElements,
        mobile_usability: MobileUsability,
        content_quality: ContentQuality,
        social_proof: SocialProof
    ) -> HeuristicScore:
        """Calculate heuristic scores based on detected elements."""
        try:
            # Trust score (weighted by importance)
            trust_score = self._calculate_trust_score(trust_signals)
            
            # CRO score
            cro_score = self._calculate_cro_score(cro_elements)
            
            # Mobile usability score
            mobile_score = self._calculate_mobile_score(mobile_usability)
            
            # Content quality score
            content_score = self._calculate_content_score(content_quality)
            
            # Social proof score
            social_score = self._calculate_social_score(social_proof)
            
            # Overall heuristic score (weighted average)
            overall_score = self._calculate_overall_score(
                trust_score, cro_score, mobile_score, content_score, social_score
            )
            
            # Determine confidence level
            confidence_level = self._determine_confidence_level(
                trust_signals, cro_elements, mobile_usability, content_quality, social_proof
            )
            
            return HeuristicScore(
                trust_score=trust_score,
                cro_score=cro_score,
                mobile_score=mobile_score,
                content_score=content_score,
                social_score=social_score,
                overall_heuristic_score=overall_score,
                confidence_level=confidence_level
            )
            
        except Exception as e:
            self.log_error(e, "score_calculation")
            # Return default scores on error
            return HeuristicScore(
                trust_score=0.0,
                cro_score=0.0,
                mobile_score=0.0,
                content_score=0.0,
                social_score=0.0,
                overall_heuristic_score=0.0,
                confidence_level=ConfidenceLevel.LOW
            )
    
    def _calculate_trust_score(self, trust_signals: TrustSignals) -> float:
        """Calculate trust score (0-100)."""
        score = 0.0
        total_weight = 0.0
        
        # HTTPS is critical
        if trust_signals.has_https:
            score += 25.0
        total_weight += 25.0
        
        # Privacy and terms are important
        if trust_signals.has_privacy_policy:
            score += 15.0
        if trust_signals.has_terms_of_service:
            score += 10.0
        total_weight += 25.0
        
        # Contact information
        if trust_signals.has_contact_info:
            score += 15.0
        if trust_signals.has_business_address:
            score += 10.0
        if trust_signals.has_phone_number:
            score += 10.0
        if trust_signals.has_email:
            score += 10.0
        total_weight += 45.0
        
        # About page
        if trust_signals.has_about_page:
            score += 5.0
        total_weight += 5.0
        
        return min(100.0, (score / total_weight) * 100) if total_weight > 0 else 0.0
    
    def _calculate_cro_score(self, cro_elements: CROElements) -> float:
        """Calculate CRO score (0-100)."""
        score = 0.0
        total_weight = 0.0
        
        # CTA buttons are critical
        if cro_elements.has_cta_buttons:
            score += 30.0
        total_weight += 30.0
        
        # Contact forms
        if cro_elements.has_contact_forms:
            score += 25.0
        total_weight += 25.0
        
        # Social proof elements
        if cro_elements.has_testimonials:
            score += 15.0
        if cro_elements.has_reviews:
            score += 15.0
        if cro_elements.has_social_proof:
            score += 10.0
        total_weight += 40.0
        
        # Additional elements
        if cro_elements.has_pricing_tables:
            score += 5.0
        total_weight += 5.0
        
        return min(100.0, (score / total_weight) * 100) if total_weight > 0 else 0.0
    
    def _calculate_mobile_score(self, mobile_usability: MobileUsability) -> float:
        """Calculate mobile usability score (0-100)."""
        score = 0.0
        total_weight = 0.0
        
        # Viewport meta is critical
        if mobile_usability.has_viewport_meta:
            score += 30.0
        total_weight += 30.0
        
        # Responsive design
        if mobile_usability.has_responsive_design:
            score += 25.0
        total_weight += 25.0
        
        # Touch targets
        if mobile_usability.has_touch_targets:
            score += 20.0
        total_weight += 20.0
        
        # Mobile navigation
        if mobile_usability.has_mobile_navigation:
            score += 15.0
        total_weight += 15.0
        
        # Readability
        if mobile_usability.has_readable_fonts:
            score += 5.0
        if mobile_usability.has_adequate_spacing:
            score += 5.0
        total_weight += 10.0
        
        return min(100.0, (score / total_weight) * 100) if total_weight > 0 else 0.0
    
    def _calculate_content_score(self, content_quality: ContentQuality) -> float:
        """Calculate content quality score (0-100)."""
        score = 0.0
        total_weight = 0.0
        
        # Heading structure is important
        if content_quality.has_proper_headings:
            score += 20.0
        total_weight += 20.0
        
        # Meta tags
        if content_quality.has_meta_description:
            score += 20.0
        if content_quality.has_meta_keywords:
            score += 10.0
        total_weight += 30.0
        
        # Alt text for images
        if content_quality.has_alt_text:
            score += 15.0
        total_weight += 15.0
        
        # Structured data
        if content_quality.has_structured_data:
            score += 15.0
        total_weight += 15.0
        
        # Links
        if content_quality.has_internal_links:
            score += 10.0
        if content_quality.has_external_links:
            score += 5.0
        total_weight += 15.0
        
        # Blog content
        if content_quality.has_blog_content:
            score += 5.0
        total_weight += 5.0
        
        return min(100.0, (score / total_weight) * 100) if total_weight > 0 else 0.0
    
    def _calculate_social_score(self, social_proof: SocialProof) -> float:
        """Calculate social proof score (0-100)."""
        score = 0.0
        total_weight = 0.0
        
        # Customer reviews are most important
        if social_proof.has_customer_reviews:
            score += 30.0
        total_weight += 30.0
        
        # Testimonials
        if social_proof.has_testimonials:
            score += 25.0
        total_weight += 25.0
        
        # Social media presence
        if social_proof.has_social_media_links:
            score += 20.0
        total_weight += 20.0
        
        # Case studies and awards
        if social_proof.has_case_studies:
            score += 15.0
        if social_proof.has_awards_certifications:
            score += 10.0
        total_weight += 25.0
        
        return min(100.0, (score / total_weight) * 100) if total_weight > 0 else 0.0
    
    def _calculate_overall_score(
        self,
        trust_score: float,
        cro_score: float,
        mobile_score: float,
        content_score: float,
        social_score: float
    ) -> float:
        """Calculate overall heuristic score with business impact weighting."""
        # Weight scores by business impact
        weights = {
            'trust': 0.30,      # Trust is critical for conversions
            'cro': 0.25,        # CRO directly impacts revenue
            'mobile': 0.20,     # Mobile usability is important
            'content': 0.15,    # Content quality supports other areas
            'social': 0.10      # Social proof enhances trust
        }
        
        overall_score = (
            trust_score * weights['trust'] +
            cro_score * weights['cro'] +
            mobile_score * weights['mobile'] +
            content_score * weights['content'] +
            social_score * weights['social']
        )
        
        return round(overall_score, 2)
    
    def _determine_confidence_level(
        self,
        trust_signals: TrustSignals,
        cro_elements: CROElements,
        mobile_usability: MobileUsability,
        content_quality: ContentQuality,
        social_proof: SocialProof
    ) -> ConfidenceLevel:
        """Determine confidence level based on data availability and quality."""
        # Count detected elements
        total_elements = 0
        detected_elements = 0
        
        # Trust signals
        for field in trust_signals.__fields__:
            total_elements += 1
            if getattr(trust_signals, field):
                detected_elements += 1
        
        # CRO elements
        for field in cro_elements.__fields__:
            total_elements += 1
            if getattr(cro_elements, field):
                detected_elements += 1
        
        # Mobile usability
        for field in mobile_usability.__fields__:
            total_elements += 1
            if getattr(mobile_usability, field):
                detected_elements += 1
        
        # Content quality
        for field in content_quality.__fields__:
            total_elements += 1
            if getattr(content_quality, field):
                detected_elements += 1
        
        # Social proof
        for field in social_proof.__fields__:
            total_elements += 1
            if getattr(social_proof, field):
                detected_elements += 1
        
        # Calculate confidence based on detection rate
        detection_rate = detected_elements / total_elements if total_elements > 0 else 0
        
        if detection_rate >= 0.7:
            return ConfidenceLevel.HIGH
        elif detection_rate >= 0.4:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
