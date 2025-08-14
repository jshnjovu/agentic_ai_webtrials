"""
Unit tests for HeuristicEvaluationService.
Tests heuristic evaluation functionality including trust signals, CRO elements, mobile usability, content quality, and social proof.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
import requests

from src.services.heuristic_evaluation_service import HeuristicEvaluationService
from src.schemas.website_scoring import (
    TrustSignals, CROElements, MobileUsability, ContentQuality, SocialProof,
    HeuristicScore, ConfidenceLevel
)


class TestHeuristicEvaluationService:
    """Test cases for HeuristicEvaluationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        with patch('src.services.heuristic_evaluation_service.get_api_config'):
            with patch('src.services.heuristic_evaluation_service.RateLimiter'):
                self.service = HeuristicEvaluationService()
                self.service.api_config.HEURISTICS_EVALUATION_TIMEOUT_SECONDS = 15
                self.service.rate_limiter = Mock()
                self.service.rate_limiter.can_make_request.return_value = (True, "OK")
                self.service.rate_limiter.record_request.return_value = None
        
        self.run_id = "test-run-12345"
        self.business_id = "test-business-123"
        self.website_url = "https://example.com"
    
    def test_validate_input_valid(self):
        """Test input validation with valid data."""
        valid_data = {
            'website_url': 'https://example.com',
            'business_id': 'test-business-123'
        }
        assert self.service.validate_input(valid_data) is True
    
    def test_validate_input_invalid(self):
        """Test input validation with invalid data."""
        invalid_data = [
            None,
            "not a dict",
            {'website_url': 'https://example.com'},  # missing business_id
            {'business_id': 'test-business-123'},   # missing website_url
            {}
        ]
        
        for data in invalid_data:
            assert self.service.validate_input(data) is False
    
    @patch('src.services.heuristic_evaluation_service.requests.get')
    def test_fetch_website_success(self, mock_get):
        """Test successful website fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><head><title>Test</title></head><body>Test content</body></html>'
        mock_response.content = b'<html><head><title>Test</title></head><body>Test content</body></html>'
        mock_get.return_value = mock_response
        
        html_content, soup = self.service._fetch_website(
            self.website_url
        )
        
        assert html_content is not None
        assert soup is not None
        assert isinstance(soup, BeautifulSoup)
        assert soup.title.string == 'Test'
    
    @patch('src.services.heuristic_evaluation_service.requests.get')
    def test_fetch_website_timeout(self, mock_get):
        """Test website fetching timeout handling."""
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        html_content, soup = self.service._fetch_website(self.website_url)
        assert html_content is None
        assert soup is None
    
    @patch('src.services.heuristic_evaluation_service.requests.get')
    def test_fetch_website_request_exception(self, mock_get):
        """Test website fetching request exception handling."""
        mock_get.side_effect = requests.RequestException("Request failed")
        
        html_content, soup = self.service._fetch_website(self.website_url)
        assert html_content is None
        assert soup is None
    
    def test_evaluate_trust_signals_https(self):
        """Test trust signal evaluation with HTTPS."""
        html = '<html><body><a href="/privacy">Privacy</a><a href="/contact">Contact</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        trust_signals = self.service._evaluate_trust_signals(
            "https://example.com", soup
        )
        
        assert trust_signals.has_https is True
        assert trust_signals.has_privacy_policy is True
        assert trust_signals.has_contact_info is True
    
    def test_evaluate_trust_signals_http(self):
        """Test trust signal evaluation with HTTP."""
        html = '<html><body><a href="/privacy">Privacy</a></body></html>'
        soup = BeautifulSoup(html, 'html.parser')
        
        trust_signals = self.service._evaluate_trust_signals(
            "http://example.com", soup
        )
        
        assert trust_signals.has_https is False
        assert trust_signals.has_privacy_policy is True
    
    def test_evaluate_trust_signals_with_contact_info(self):
        """Test trust signal evaluation with contact information."""
        html = '''
        <html>
        <body>
            <p>Contact us at 123-456-7890</p>
            <p>Email: test@example.com</p>
            <p>Address: 123 Main St, City, State</p>
        </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        trust_signals = self.service._evaluate_trust_signals(
            self.website_url, soup
        )
        
        assert trust_signals.has_phone_number is True
        assert trust_signals.has_email is True
        assert trust_signals.has_business_address is True
    
    def test_evaluate_cro_elements(self):
        """Test CRO elements evaluation."""
        html = '''
        <html>
        <body>
            <button>Get Started</button>
            <form action="/contact">
                <input type="text" placeholder="Name">
            </form>
            <p>Starting at $99/month</p>
            <div class="testimonial">Great service!</div>
        </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        cro_elements = self.service._evaluate_cro_elements(soup)
        
        assert cro_elements.has_cta_buttons is True
        assert cro_elements.has_contact_forms is True
        assert cro_elements.has_pricing_tables is True
        assert cro_elements.has_testimonials is True
    
    def test_evaluate_mobile_usability(self):
        """Test mobile usability evaluation."""
        html = '''
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <button>Click me</button>
            <a href="/link">Link</a>
            <link rel="stylesheet" media="(max-width: 768px)" href="/mobile.css">
        </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        mobile_usability = self.service._evaluate_mobile_usability(soup)
        
        assert mobile_usability.has_viewport_meta is True
        assert mobile_usability.has_touch_targets is True
        assert mobile_usability.has_responsive_design is True
    
    def test_evaluate_content_quality(self):
        """Test content quality evaluation."""
        html = '''
        <html>
        <head>
            <meta name="description" content="Test description">
            <meta name="keywords" content="test, keywords">
        </head>
        <body>
            <h1>Main Title</h1>
            <h2>Subtitle</h2>
            <img src="test.jpg" alt="Test image">
            <a href="/internal">Internal link</a>
            <a href="https://external.com">External link</a>
            <script type="application/ld+json">{"@type": "Organization"}</script>
        </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        content_quality = self.service._evaluate_content_quality(soup)
        
        assert content_quality.has_proper_headings is True
        assert content_quality.has_alt_text is True
        assert content_quality.has_meta_description is True
        assert content_quality.has_meta_keywords is True
        assert content_quality.has_structured_data is True
        assert content_quality.has_internal_links is True
        assert content_quality.has_external_links is True
    
    def test_evaluate_social_proof(self):
        """Test social proof evaluation."""
        html = '''
        <html>
        <body>
            <a href="https://facebook.com/company">Facebook</a>
            <a href="https://twitter.com/company">Twitter</a>
            <div class="review">Great product!</div>
            <div class="testimonial">Amazing service!</div>
            <div class="case-study">Success story here</div>
            <img alt="Partner logo" src="partner.jpg">
        </body>
        </html>
        '''
        soup = BeautifulSoup(html, 'html.parser')
        
        social_proof = self.service._evaluate_social_proof(soup)
        
        assert social_proof.has_social_media_links is True
        assert social_proof.has_customer_reviews is True
        assert social_proof.has_testimonials is True
        assert social_proof.has_case_studies is True
        assert social_proof.has_partner_logos is True
    
    def test_calculate_trust_score(self):
        """Test trust score calculation."""
        trust_signals = TrustSignals(
            has_https=True,
            has_privacy_policy=True,
            has_contact_info=True,
            has_about_page=True,
            has_terms_of_service=True,
            has_ssl_certificate=True,
            has_business_address=True,
            has_phone_number=True,
            has_email=True
        )
        
        score = self.service._calculate_trust_score(trust_signals)
        assert 0 <= score <= 100
        assert score > 0  # Should have a positive score with all signals
    
    def test_calculate_cro_score(self):
        """Test CRO score calculation."""
        cro_elements = CROElements(
            has_cta_buttons=True,
            has_contact_forms=True,
            has_pricing_tables=True,
            has_testimonials=True,
            has_reviews=True,
            has_social_proof=True,
            has_urgency_elements=True,
            has_trust_badges=True
        )
        
        score = self.service._calculate_cro_score(cro_elements)
        assert 0 <= score <= 100
        assert score > 0  # Should have a positive score with all elements
    
    def test_calculate_mobile_score(self):
        """Test mobile usability score calculation."""
        mobile_usability = MobileUsability(
            has_viewport_meta=True,
            has_touch_targets=True,
            has_responsive_design=True,
            has_mobile_navigation=True,
            has_readable_fonts=True,
            has_adequate_spacing=True
        )
        
        score = self.service._calculate_mobile_score(mobile_usability)
        assert 0 <= score <= 100
        assert score > 0  # Should have a positive score with all features
    
    def test_calculate_content_score(self):
        """Test content quality score calculation."""
        content_quality = ContentQuality(
            has_proper_headings=True,
            has_alt_text=True,
            has_meta_description=True,
            has_meta_keywords=True,
            has_structured_data=True,
            has_internal_links=True,
            has_external_links=True,
            has_blog_content=True
        )
        
        score = self.service._calculate_content_score(content_quality)
        assert 0 <= score <= 100
        assert score > 0  # Should have a positive score with all features
    
    def test_calculate_social_score(self):
        """Test social proof score calculation."""
        social_proof = SocialProof(
            has_social_media_links=True,
            has_customer_reviews=True,
            has_testimonials=True,
            has_case_studies=True,
            has_awards_certifications=True,
            has_partner_logos=True,
            has_user_generated_content=True
        )
        
        score = self.service._calculate_social_score(social_proof)
        assert 0 <= score <= 100
        assert score > 0  # Should have a positive score with all elements
    
    def test_calculate_overall_score(self):
        """Test overall heuristic score calculation."""
        overall_score = self.service._calculate_overall_score(
            trust_score=80.0,
            cro_score=75.0,
            mobile_score=90.0,
            content_score=85.0,
            social_score=70.0
        )
        
        assert 0 <= overall_score <= 100
        assert overall_score > 0
        # Should be weighted average of individual scores
        assert 70 <= overall_score <= 90
    
    def test_determine_confidence_level_high(self):
        """Test confidence level determination for high confidence."""
        trust_signals = TrustSignals(
            has_https=True, has_privacy_policy=True, has_contact_info=True,
            has_about_page=True, has_terms_of_service=True, has_ssl_certificate=True,
            has_business_address=True, has_phone_number=True, has_email=True
        )

        cro_elements = CROElements(
            has_cta_buttons=True, has_contact_forms=True, has_pricing_tables=True,
            has_testimonials=True, has_reviews=True, has_social_proof=True,
            has_urgency_elements=True, has_trust_badges=True
        )
        
        mobile_usability = MobileUsability(
            has_viewport_meta=True, has_touch_targets=True, has_responsive_design=True,
            has_mobile_navigation=True, has_readable_fonts=True, has_adequate_spacing=True
        )

        content_quality = ContentQuality(
            has_proper_headings=True, has_alt_text=True, has_meta_description=True,
            has_meta_keywords=True, has_structured_data=True, has_internal_links=True,
            has_external_links=True, has_blog_content=True
        )

        social_proof = SocialProof(
            has_social_media_links=True, has_customer_reviews=True, has_testimonials=True,
            has_case_studies=True, has_awards_certifications=True, has_partner_logos=True,
            has_user_generated_content=True
        )
        
        confidence = self.service._determine_confidence_level(
            trust_signals, cro_elements, mobile_usability, content_quality, social_proof
        )
        
        assert confidence == ConfidenceLevel.HIGH
    
    def test_determine_confidence_level_medium(self):
        """Test confidence level determination for medium confidence."""
        trust_signals = TrustSignals(
            has_https=True, has_privacy_policy=True, has_contact_info=True,
            has_about_page=True, has_terms_of_service=True
        )
        cro_elements = CROElements(
            has_cta_buttons=True, has_contact_forms=True, has_testimonials=True
        )
        mobile_usability = MobileUsability(
            has_viewport_meta=True, has_touch_targets=True, has_responsive_design=True
        )
        content_quality = ContentQuality(
            has_proper_headings=True, has_alt_text=True, has_meta_description=True
        )
        social_proof = SocialProof(
            has_social_media_links=True, has_customer_reviews=True, has_testimonials=True
        )
        
        confidence = self.service._determine_confidence_level(
            trust_signals, cro_elements, mobile_usability, content_quality, social_proof
        )
        
        assert confidence == ConfidenceLevel.MEDIUM
    
    def test_determine_confidence_level_low(self):
        """Test confidence level determination for low confidence."""
        trust_signals = TrustSignals()
        cro_elements = CROElements()
        mobile_usability = MobileUsability()
        content_quality = ContentQuality()
        social_proof = SocialProof()
        
        confidence = self.service._determine_confidence_level(
            trust_signals, cro_elements, mobile_usability, content_quality, social_proof
        )
        
        assert confidence == ConfidenceLevel.LOW
    
    def test_calculate_heuristic_scores_success(self):
        """Test successful heuristic score calculation."""
        trust_signals = TrustSignals(has_https=True, has_privacy_policy=True)
        cro_elements = CROElements(has_cta_buttons=True, has_contact_forms=True)
        mobile_usability = MobileUsability(has_viewport_meta=True)
        content_quality = ContentQuality(has_proper_headings=True)
        social_proof = SocialProof(has_social_media_links=True)
        
        scores = self.service._calculate_heuristic_scores(
            trust_signals, cro_elements, mobile_usability, content_quality, social_proof
        )
        
        assert isinstance(scores, HeuristicScore)
        assert 0 <= scores.trust_score <= 100
        assert 0 <= scores.cro_score <= 100
        assert 0 <= scores.mobile_score <= 100
        assert 0 <= scores.content_score <= 100
        assert 0 <= scores.social_score <= 100
        assert 0 <= scores.overall_heuristic_score <= 100
        assert scores.confidence_level in [ConfidenceLevel.HIGH, ConfidenceLevel.MEDIUM, ConfidenceLevel.LOW]
    
    def test_calculate_heuristic_scores_error(self):
        """Test heuristic score calculation with error handling."""
        with patch.object(self.service, '_calculate_trust_score', side_effect=Exception("Test error")):
            scores = self.service._calculate_heuristic_scores(
                TrustSignals(), CROElements(), MobileUsability(), ContentQuality(), SocialProof()
            )
            
            # Should return default scores on error
            assert scores.trust_score == 0.0
            assert scores.cro_score == 0.0
            assert scores.mobile_score == 0.0
            assert scores.content_score == 0.0
            assert scores.social_score == 0.0
            assert scores.overall_heuristic_score == 0.0
            assert scores.confidence_level == ConfidenceLevel.LOW
    
    @patch('src.services.heuristic_evaluation_service.requests.get')
    def test_run_heuristic_evaluation_success(self, mock_get):
        """Test successful heuristic evaluation run."""
        # Mock successful website fetch
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><button>Get Started</button><form></form></body></html>'
        mock_response.content = b'<html><body><button>Get Started</button><form></form></body></html>'
        mock_get.return_value = mock_response
        
        result = self.service.run_heuristic_evaluation(
            self.website_url, self.business_id, self.run_id
        )
        
        assert result["success"] is True
        assert result["website_url"] == self.website_url
        assert result["business_id"] == self.business_id
        assert result["run_id"] == self.run_id
        assert "scores" in result
        assert "trust_signals" in result
        assert "cro_elements" in result
        assert "mobile_usability" in result
        assert "content_quality" in result
        assert "social_proof" in result
    
    def test_run_heuristic_evaluation_rate_limit_exceeded(self):
        """Test heuristic evaluation with rate limit exceeded."""
        self.service.rate_limiter.can_make_request.return_value = (False, "Rate limit exceeded")
        
        result = self.service.run_heuristic_evaluation(
            self.website_url, self.business_id, self.run_id
        )
        
        assert result["success"] is False
        assert "Rate limit exceeded" in result["error"]
        assert result["error_code"] == "RATE_LIMIT_EXCEEDED"
    
    @patch('src.services.heuristic_evaluation_service.requests.get')
    def test_run_heuristic_evaluation_fetch_failed(self, mock_get):
        """Test heuristic evaluation with website fetch failure."""
        mock_get.side_effect = requests.RequestException("Fetch failed")
        
        result = self.service.run_heuristic_evaluation(
            self.website_url, self.business_id, self.run_id
        )
        
        assert result["success"] is False
        assert "Failed to fetch website content" in result["error"]
        assert result["error_code"] == "FETCH_FAILED"
    
    def test_helper_methods(self):
        """Test helper methods for pattern matching."""
        # These methods are not implemented in the current service
        # They were part of an earlier design that was simplified
        pass
    
    def test_pattern_methods(self):
        """Test pattern matching methods."""
        # These methods are not implemented in the current service
        # They were part of an earlier design that was simplified
        pass
