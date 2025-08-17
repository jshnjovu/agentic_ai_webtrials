"""
Unit tests for website scoring API endpoints.
Tests both Lighthouse and Heuristic evaluation endpoints.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException

from src.main import app
from src.schemas.website_scoring import (
    WebsiteScore, ConfidenceLevel, HeuristicScore
)


class TestWebsiteScoringAPI:
    """Test cases for website scoring API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.business_id = "test-business-123"
        self.run_id = "test-run-12345"
        self.website_url = "https://example.com"
    
    def test_lighthouse_health_check(self):
        """Test health check endpoint for website scoring services."""
        response = self.client.get("/api/v1/website-scoring/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Website Scoring API"
        assert "lighthouse_auditing" in data["features"]
        assert "heuristic_evaluation" in data["features"]
        assert "trust_signal_detection" in data["features"]
        assert "cro_element_identification" in data["features"]
    
    def test_lighthouse_audit_success(self):
        """Test successful Lighthouse audit endpoint."""
        with patch('src.services.lighthouse_service.LighthouseService.run_lighthouse_audit') as mock_run_audit, \
             patch('src.services.lighthouse_service.LighthouseService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_audit.return_value = {
                "success": True,
                "website_url": self.website_url + "/",  # Match the actual response format
                "business_id": self.business_id,
                "run_id": self.run_id,
                "audit_timestamp": 1234567890.0,
                "strategy": "desktop",
                "scores": {
                    "performance": 85.0,
                    "accessibility": 90.0,
                    "best_practices": 88.0,
                    "seo": 92.0,
                    "overall_score": 88.75
                },
                "core_web_vitals": {
                    "first_contentful_paint": 1200.0,
                    "largest_contentful_paint": 2500.0,
                    "cumulative_layout_shift": 0.1,
                    "total_blocking_time": 150.0,
                    "speed_index": 1800.0
                },
                "confidence": "high",
                "raw_data": {"test": "data"}
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id,
                "strategy": "desktop"
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/lighthouse",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["website_url"] == self.website_url + "/"  # Match the actual response format
            assert data["business_id"] == self.business_id
            assert data["run_id"] == self.run_id
            assert data["scores"]["performance"] == 85.0
            assert data["scores"]["accessibility"] == 90.0
            assert data["scores"]["best_practices"] == 88.0
            assert data["scores"]["seo"] == 92.0
            assert data["scores"]["overall"] == 88.75
            assert data["confidence"] == "high"
    
    def test_lighthouse_audit_validation_error(self):
        """Test Lighthouse audit endpoint with validation error."""
        with patch('src.services.lighthouse_service.LighthouseService.validate_input') as mock_validate:
            # Set up the mock
            mock_validate.return_value = False
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id,
                "strategy": "desktop"
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/lighthouse",
                json=request_data
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid Lighthouse audit request" in data["detail"]
    
    def test_lighthouse_audit_timeout_error(self):
        """Test Lighthouse audit endpoint with timeout error."""
        with patch('src.services.lighthouse_service.LighthouseService.run_lighthouse_audit') as mock_run_audit, \
             patch('src.services.lighthouse_service.LighthouseService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_audit.return_value = {
                "success": False,
                "error": "Audit timed out",
                "error_code": "TIMEOUT",
                "context": "audit_execution",
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id,
                "strategy": "desktop"
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/lighthouse",
                json=request_data
            )
            
            assert response.status_code == 408
            data = response.json()
            assert "Lighthouse audit timed out" in data["detail"]["error"]
            assert data["detail"]["error_code"] == "TIMEOUT"
    
    def test_lighthouse_audit_rate_limit_error(self):
        """Test Lighthouse audit endpoint with rate limit error."""
        with patch('src.services.lighthouse_service.LighthouseService.run_lighthouse_audit') as mock_run_audit, \
             patch('src.services.lighthouse_service.LighthouseService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_audit.return_value = {
                "success": False,
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "context": "rate_limit_check",
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id,
                "strategy": "desktop"
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/lighthouse",
                json=request_data
            )
            
            assert response.status_code == 429
            data = response.json()
            assert "Rate limit exceeded for Lighthouse API" in data["detail"]["error"]
            assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"
    
    def test_heuristic_evaluation_success(self):
        """Test successful heuristic evaluation endpoint."""
        with patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.run_heuristic_evaluation') as mock_run_eval, \
             patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_eval.return_value = {
                "success": True,
                "website_url": self.website_url + "/",  # Match the actual response format
                "business_id": self.business_id,
                "run_id": self.run_id,
                "evaluation_timestamp": 1234567890.0,
                "scores": {
                    "trust_score": 85.0,
                    "cro_score": 78.0,
                    "mobile_score": 92.0,
                    "content_score": 88.0,
                    "social_score": 75.0,
                    "overall_heuristic_score": 83.6,
                    "confidence_level": "high"
                },
                "trust_signals": {
                    "has_https": True,
                    "has_privacy_policy": True,
                    "has_contact_info": True,
                    "has_about_page": False,
                    "has_terms_of_service": True,
                    "has_ssl_certificate": True,
                    "has_business_address": True,
                    "has_phone_number": True,
                    "has_email": True
                },
                "cro_elements": {
                    "has_cta_buttons": True,
                    "has_contact_forms": True,
                    "has_pricing_tables": False,
                    "has_testimonials": True,
                    "has_reviews": True,
                    "has_social_proof": True,
                    "has_urgency_elements": False,
                    "has_trust_badges": True
                },
                "mobile_usability": {
                    "has_viewport_meta": True,
                    "has_touch_targets": True,
                    "has_responsive_design": True,
                    "has_mobile_navigation": False,
                    "has_readable_fonts": True,
                    "has_adequate_spacing": True
                },
                "content_quality": {
                    "has_proper_headings": True,
                    "has_alt_text": True,
                    "has_meta_description": True,
                    "has_meta_keywords": False,
                    "has_structured_data": True,
                    "has_internal_links": True,
                    "has_external_links": False,
                    "has_blog_content": True
                },
                "social_proof": {
                    "has_social_media_links": True,
                    "has_customer_reviews": True,
                    "has_testimonials": True,
                    "has_case_studies": False,
                    "has_awards_certifications": True,
                    "has_partner_logos": False,
                    "has_user_generated_content": False
                },
                "confidence": "high",
                "raw_data": {"html_length": 5000, "evaluation_time": 2.5}
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/heuristics",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["website_url"] == self.website_url + "/"  # Match the actual response format
            assert data["business_id"] == self.business_id
            assert data["run_id"] == self.run_id
            assert data["scores"]["trust_score"] == 85.0
            assert data["scores"]["cro_score"] == 78.0
            assert data["scores"]["mobile_score"] == 92.0
            assert data["scores"]["content_score"] == 88.0
            assert data["scores"]["social_score"] == 75.0
            assert data["scores"]["overall_heuristic_score"] == 83.6
            assert data["confidence"] == "high"
            assert data["trust_signals"]["has_https"] is True
            assert data["cro_elements"]["has_cta_buttons"] is True
            assert data["mobile_usability"]["has_viewport_meta"] is True
            assert data["content_quality"]["has_proper_headings"] is True
            assert data["social_proof"]["has_social_media_links"] is True

    def test_heuristic_evaluation_validation_error(self):
        """Test heuristic evaluation endpoint with validation error."""
        with patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.validate_input') as mock_validate:
            # Set up the mock
            mock_validate.return_value = False
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/heuristics",
                json=request_data
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "Invalid heuristic evaluation request" in data["detail"]
    
    def test_heuristic_evaluation_timeout_error(self):
        """Test heuristic evaluation endpoint with timeout error."""
        with patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.run_heuristic_evaluation') as mock_run_eval, \
             patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_eval.return_value = {
                "success": False,
                "error": "Evaluation timed out",
                "error_code": "TIMEOUT",
                "context": "evaluation_execution",
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/heuristics",
                json=request_data
            )
            
            assert response.status_code == 408
            data = response.json()
            assert "Heuristic evaluation timed out" in data["detail"]["error"]
            assert data["detail"]["error_code"] == "TIMEOUT"
    
    def test_heuristic_evaluation_rate_limit_error(self):
        """Test heuristic evaluation endpoint with rate limit error."""
        with patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.run_heuristic_evaluation') as mock_run_eval, \
             patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_eval.return_value = {
                "success": False,
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "context": "rate_limit_check",
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/heuristics",
                json=request_data
            )
            
            assert response.status_code == 429
            data = response.json()
            assert "Rate limit exceeded for heuristic evaluation" in data["detail"]["error"]
            assert data["detail"]["error_code"] == "RATE_LIMIT_EXCEEDED"
    
    def test_heuristic_evaluation_general_error(self):
        """Test heuristic evaluation endpoint with general error."""
        with patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.run_heuristic_evaluation') as mock_run_eval, \
             patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_eval.return_value = {
                "success": False,
                "error": "General evaluation error",
                "error_code": "EVALUATION_FAILED",
                "context": "evaluation_execution",
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/heuristics",
                json=request_data
            )
            
            assert response.status_code == 400
            data = response.json()
            assert "General evaluation error" in data["detail"]["error"]
            assert data["detail"]["error_code"] == "EVALUATION_FAILED"
    
    def test_website_scoring_summary(self):
        """Test website scoring summary endpoint."""
        response = self.client.get(f"/api/v1/website-scoring/lighthouse/{self.business_id}/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["business_id"] == self.business_id
        assert "total_audits" in data
        assert "successful_audits" in data
        assert "failed_audits" in data
        assert "average_scores" in data
    
    def test_website_scoring_summary_with_limit(self):
        """Test website scoring summary endpoint with limit parameter."""
        response = self.client.get(
            f"/api/v1/website-scoring/lighthouse/{self.business_id}/summary?limit=5"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["business_id"] == self.business_id
    
    def test_invalid_website_url(self):
        """Test API endpoints with invalid website URL."""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "javascript:alert('xss')",
            ""
        ]
        
        for invalid_url in invalid_urls:
            # Test Lighthouse endpoint
            request_data = {
                "website_url": invalid_url,
                "business_id": self.business_id,
                "run_id": self.run_id,
                "strategy": "desktop"
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/lighthouse",
                json=request_data
            )
            
            assert response.status_code == 422  # Validation error
            
            # Test Heuristic endpoint
            request_data = {
                "website_url": invalid_url,
                "business_id": self.business_id,
                "run_id": self.run_id
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/heuristics",
                json=request_data
            )
            
            assert response.status_code == 422  # Validation error
    
    def test_missing_required_fields(self):
        """Test API endpoints with missing required fields."""
        # Test Lighthouse endpoint
        incomplete_data = {
            "website_url": self.website_url
            # Missing business_id
        }
        
        response = self.client.post(
            "/api/v1/website-scoring/lighthouse",
            json=incomplete_data
        )
        
        assert response.status_code == 422  # Validation error
        
        # Test Heuristic endpoint
        response = self.client.post(
            "/api/v1/website-scoring/heuristics",
            json=incomplete_data
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_auto_generated_run_id(self):
        """Test that run_id is auto-generated when not provided."""
        with patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.run_heuristic_evaluation') as mock_run_eval, \
             patch('src.services.heuristic_evaluation_service.HeuristicEvaluationService.validate_input') as mock_validate:
            
            # Set up the mocks
            mock_validate.return_value = True
            mock_run_eval.return_value = {
                "success": True,
                "website_url": self.website_url,
                "business_id": self.business_id,
                "run_id": None,  # Service will generate one
                "evaluation_timestamp": 1234567890.0,
                "scores": {
                    "trust_score": 85.0,
                    "cro_score": 78.0,
                    "mobile_score": 92.0,
                    "content_score": 88.0,
                    "social_score": 75.0,
                    "overall_heuristic_score": 83.6,
                    "confidence_level": "high"
                },
                "trust_signals": {},
                "cro_elements": {},
                "mobile_usability": {},
                "content_quality": {},
                "social_proof": {},
                "confidence": "high",
                "raw_data": {}
            }
            
            request_data = {
                "website_url": self.website_url,
                "business_id": self.business_id
                # No run_id provided
            }
            
            response = self.client.post(
                "/api/v1/website-scoring/heuristics",
                json=request_data
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "run_id" in data
            assert data["run_id"] is not None
            assert data["run_id"] != ""
