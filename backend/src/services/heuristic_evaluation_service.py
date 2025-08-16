"""
Heuristic evaluation service for website analysis.
Analyzes trust signals, CRO elements, mobile usability, content quality, and social proof.
"""

import time
import re
import requests
from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from src.core.base_service import BaseService
from src.core.config import get_api_config
from src.services.rate_limiter import RateLimiter
from src.schemas.website_scoring import (
    HeuristicScore,
    TrustSignals,
    CROElements,
    MobileUsability,
    ContentQuality,
    SocialProof,
    ConfidenceLevel,
)


class HeuristicEvaluationService(BaseService):
    """Service for heuristic evaluation of websites."""

    def __init__(self):
        super().__init__("HeuristicEvaluationService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.timeout = self.api_config.HEURISTICS_EVALUATION_TIMEOUT_SECONDS

        # User agent rotation for reliable scraping
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        ]

        # Trust signal patterns
        self.trust_patterns = {
            "privacy_policy": [
                r"privacy\s*policy",
                r"privacy\s*notice",
                r"privacy\s*statement",
                r"data\s*protection",
                r"gdpr",
                r"ccpa",
                r"\bprivacy\b",
            ],
            "terms_of_service": [
                r"terms\s*of\s*service",
                r"terms\s*and\s*conditions",
                r"user\s*agreement",
                r"legal\s*terms",
                r"conditions\s*of\s*use",
            ],
            "about_page": [
                r"about\s*us",
                r"about\s*company",
                r"company\s*information",
                r"our\s*story",
                r"who\s*we\s*are",
            ],
            "contact_info": [
                r"contact\s*us",
                r"get\s*in\s*touch",
                r"contact\s*information",
                r"phone",
                r"email",
                r"address",
                r"\bcontact\b",
            ],
        }

        # CRO element patterns
        self.cro_patterns = {
            "cta_buttons": [
                r"get\s*started",
                r"start\s*now",
                r"get\s*quote",
                r"request\s*demo",
                r"book\s*now",
                r"order\s*now",
                r"buy\s*now",
                r"sign\s*up",
                r"free\s*trial",
                r"learn\s*more",
                r"contact\s*sales",
            ],
            "pricing_tables": [
                r"pricing",
                r"plans",
                r"packages",
                r"cost",
                r"price",
                r"monthly",
                r"annually",
                r"yearly",
                r"per\s*month",
                r"\$\d+",
            ],
            "testimonials": [
                r"testimonial",
                r"review",
                r"customer\s*story",
                r"client\s*feedback",
                r"what\s*customers\s*say",
                r"customer\s*experience",
            ],
            "urgency_elements": [
                r"limited\s*time",
                r"offer\s*expires",
                r"act\s*now",
                r"while\s*supplies\s*last",
                r"only\s*\d+\s*left",
            ],
        }

        # Social proof patterns
        self.social_patterns = {
            "testimonials": [
                r"testimonial",
                r"review",
                r"customer\s*story",
                r"client\s*feedback",
                r"what\s*customers\s*say",
                r"customer\s*experience",
            ],
            "case_studies": [
                r"case\s*study",
                r"success\s*story",
                r"customer\s*success",
                r"results",
                r"outcomes",
                r"before\s*and\s*after",
            ],
            "awards_certifications": [
                r"award",
                r"certification",
                r"accreditation",
                r"badge",
                r"recognition",
                r"honor",
                r"achievement",
            ],
        }

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if not isinstance(data, dict):
            return False

        required_fields = ["website_url", "business_id"]
        return all(field in data for field in required_fields)

    def run_heuristic_evaluation(
        self, website_url: str, business_id: str, run_id: Optional[str] = None
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
                website_url=website_url,
            )

            # Check rate limiting
            can_proceed, message = self.rate_limiter.can_make_request(
                "heuristics", run_id
            )
            if not can_proceed:
                self.log_operation(
                    f"Rate limit exceeded: {message}",
                    run_id=run_id,
                    business_id=business_id,
                )
                return {
                    "success": False,
                    "error": f"Rate limit exceeded: {message}",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "context": "rate_limit_check",
                    "run_id": run_id,
                    "business_id": business_id,
                }

            # Fetch and parse the website
            html_content, soup = self._fetch_website(website_url)
            if not html_content:
                return {
                    "success": False,
                    "error": "Failed to fetch website content",
                    "error_code": "FETCH_FAILED",
                    "context": "website_fetching",
                    "run_id": run_id,
                    "business_id": business_id,
                }

            # Evaluate all heuristic categories
            trust_signals = self._evaluate_trust_signals(website_url, soup)
            cro_elements = self._evaluate_cro_elements(soup)
            mobile_usability = self._evaluate_mobile_usability(soup)
            content_quality = self._evaluate_content_quality(soup)
            social_proof = self._evaluate_social_proof(soup)

            # Calculate scores
            scores = self._calculate_heuristic_scores(
                trust_signals,
                cro_elements,
                mobile_usability,
                content_quality,
                social_proof,
            )

            # Record successful request
            self.rate_limiter.record_request("heuristics", True, run_id)

            evaluation_time = time.time() - start_time
            self.log_operation(
                f"Completed heuristic evaluation in {evaluation_time:.2f}s",
                run_id=run_id,
                business_id=business_id,
                evaluation_time=evaluation_time,
            )

            return {
                "success": True,
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id,
                "evaluation_timestamp": time.time(),
                "scores": scores,
                "trust_signals": trust_signals.model_dump(),
                "cro_elements": cro_elements.model_dump(),
                "mobile_usability": mobile_usability.model_dump(),
                "content_quality": content_quality.model_dump(),
                "social_proof": social_proof.model_dump(),
                "confidence": scores.confidence_level.value,
                "raw_data": {
                    "html_length": len(html_content),
                    "evaluation_time": evaluation_time,
                },
            }

        except Exception as e:
            # Record failed request
            self.rate_limiter.record_request("heuristics", False, run_id)

            self.log_error(e, "heuristic_evaluation", run_id, business_id)

            return {
                "success": False,
                "error": str(e),
                "error_code": "EVALUATION_FAILED",
                "context": "heuristic_evaluation",
                "run_id": run_id,
                "business_id": business_id,
            }

    def _fetch_website(
        self, website_url: str
    ) -> Tuple[Optional[str], Optional[BeautifulSoup]]:
        """Fetch website content and parse HTML."""
        try:
            # Select a user agent
            user_agent = self.user_agents[hash(website_url) % len(self.user_agents)]

            headers = {
                "User-Agent": user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }

            response = requests.get(
                website_url, headers=headers, timeout=self.timeout, allow_redirects=True
            )
            response.raise_for_status()

            # Parse HTML content
            soup = BeautifulSoup(response.content, "html.parser")
            return response.text, soup

        except requests.exceptions.Timeout:
            self.log_error(Exception("Website fetch timeout"), "website_fetching")
            return None, None
        except requests.exceptions.RequestException as e:
            self.log_error(e, "website_fetching")
            return None, None
        except Exception as e:
            self.log_error(e, "website_fetching")
            return None, None

    def _evaluate_trust_signals(
        self, website_url: str, soup: BeautifulSoup
    ) -> TrustSignals:
        """Evaluate trust signals on the website."""
        try:
            # Check HTTPS
            has_https = website_url.startswith("https://")

            # Check SSL certificate (basic check)
            has_ssl_certificate = has_https

            # Check for privacy policy
            has_privacy_policy = self._check_text_patterns(
                soup, self.trust_patterns["privacy_policy"]
            )

            # Check for terms of service
            has_terms_of_service = self._check_text_patterns(
                soup, self.trust_patterns["terms_of_service"]
            )

            # Check for about page
            has_about_page = self._check_text_patterns(
                soup, self.trust_patterns["about_page"]
            )

            # Check for contact information
            has_contact_info = self._check_text_patterns(
                soup, self.trust_patterns["contact_info"]
            )

            # Check for business address
            has_business_address = self._check_address_elements(soup)

            # Check for phone number
            has_phone_number = self._check_phone_elements(soup)

            # Check for email
            has_email = self._check_email_elements(soup)

            return TrustSignals(
                has_https=has_https,
                has_privacy_policy=has_privacy_policy,
                has_contact_info=has_contact_info,
                has_about_page=has_about_page,
                has_terms_of_service=has_terms_of_service,
                has_ssl_certificate=has_ssl_certificate,
                has_business_address=has_business_address,
                has_phone_number=has_phone_number,
                has_email=has_email,
            )

        except Exception as e:
            self.log_error(e, "trust_signals_evaluation")
            return TrustSignals()

    def _evaluate_cro_elements(self, soup: BeautifulSoup) -> CROElements:
        """Evaluate conversion rate optimization elements."""
        try:
            # Check for CTA buttons
            has_cta_buttons = self._check_cta_elements(soup)

            # Check for contact forms
            has_contact_forms = self._check_contact_forms(soup)

            # Check for pricing tables
            has_pricing_tables = self._check_text_patterns(
                soup, self.cro_patterns["pricing_tables"]
            )

            # Check for testimonials
            has_testimonials = self._check_text_patterns(
                soup, self.cro_patterns["testimonials"]
            )

            # Check for reviews
            has_reviews = self._check_review_elements(soup)

            # Check for social proof
            has_social_proof = has_testimonials or has_reviews

            # Check for urgency elements
            has_urgency_elements = self._check_text_patterns(
                soup, self.cro_patterns["urgency_elements"]
            )

            # Check for trust badges
            has_trust_badges = self._check_trust_badges(soup)

            return CROElements(
                has_cta_buttons=has_cta_buttons,
                has_contact_forms=has_contact_forms,
                has_pricing_tables=has_pricing_tables,
                has_testimonials=has_testimonials,
                has_reviews=has_reviews,
                has_social_proof=has_social_proof,
                has_urgency_elements=has_urgency_elements,
                has_trust_badges=has_trust_badges,
            )

        except Exception as e:
            self.log_error(e, "cro_elements_evaluation")
            return CROElements()

    def _evaluate_mobile_usability(self, soup: BeautifulSoup) -> MobileUsability:
        """Evaluate mobile usability heuristics."""
        try:
            # Check for viewport meta tag
            has_viewport_meta = self._check_viewport_meta(soup)

            # Check for touch targets
            has_touch_targets = self._check_touch_targets(soup)

            # Check for responsive design
            has_responsive_design = self._check_responsive_design(soup)

            # Check for mobile navigation
            has_mobile_navigation = self._check_mobile_navigation(soup)

            # Check for readable fonts
            has_readable_fonts = self._check_readable_fonts(soup)

            # Check for adequate spacing
            has_adequate_spacing = self._check_adequate_spacing(soup)

            return MobileUsability(
                has_viewport_meta=has_viewport_meta,
                has_touch_targets=has_touch_targets,
                has_responsive_design=has_responsive_design,
                has_mobile_navigation=has_mobile_navigation,
                has_readable_fonts=has_readable_fonts,
                has_adequate_spacing=has_adequate_spacing,
            )

        except Exception as e:
            self.log_error(e, "mobile_usability_evaluation")
            return MobileUsability()

    def _evaluate_content_quality(self, soup: BeautifulSoup) -> ContentQuality:
        """Evaluate content quality and structure."""
        try:
            # Check for proper heading structure
            has_proper_headings = self._check_heading_structure(soup)

            # Check for alt text on images
            has_alt_text = self._check_alt_text(soup)

            # Check for meta description
            has_meta_description = self._check_meta_description(soup)

            # Check for meta keywords
            has_meta_keywords = self._check_meta_keywords(soup)

            # Check for structured data
            has_structured_data = self._check_structured_data(soup)

            # Check for internal links
            has_internal_links = self._check_internal_links(soup)

            # Check for external links
            has_external_links = self._check_external_links(soup)

            # Check for blog content
            has_blog_content = self._check_blog_content(soup)

            return ContentQuality(
                has_proper_headings=has_proper_headings,
                has_alt_text=has_alt_text,
                has_meta_description=has_meta_description,
                has_meta_keywords=has_meta_keywords,
                has_structured_data=has_structured_data,
                has_internal_links=has_internal_links,
                has_external_links=has_external_links,
                has_blog_content=has_blog_content,
            )

        except Exception as e:
            self.log_error(e, "content_quality_evaluation")
            return ContentQuality()

    def _evaluate_social_proof(self, soup: BeautifulSoup) -> SocialProof:
        """Evaluate social proof elements."""
        try:
            # Check for social media links
            has_social_media_links = self._check_social_media_links(soup)

            # Check for customer reviews
            has_customer_reviews = self._check_review_elements(soup)

            # Check for testimonials
            has_testimonials = self._check_text_patterns(
                soup, self.social_patterns["testimonials"]
            )

            # Check for case studies
            has_case_studies = self._check_text_patterns(
                soup, self.social_patterns["case_studies"]
            )

            # Check for awards and certifications
            has_awards_certifications = self._check_text_patterns(
                soup, self.social_patterns["awards_certifications"]
            )

            # Check for partner logos
            has_partner_logos = self._check_partner_logos(soup)

            # Check for user-generated content
            has_user_generated_content = self._check_user_generated_content(soup)

            return SocialProof(
                has_social_media_links=has_social_media_links,
                has_customer_reviews=has_customer_reviews,
                has_testimonials=has_testimonials,
                has_case_studies=has_case_studies,
                has_awards_certifications=has_awards_certifications,
                has_partner_logos=has_partner_logos,
                has_user_generated_content=has_user_generated_content,
            )

        except Exception as e:
            self.log_error(e, "social_proof_evaluation")
            return SocialProof()

    def _check_text_patterns(self, soup: BeautifulSoup, patterns: list) -> bool:
        """Check if any text patterns are found in the HTML."""
        try:
            # Check text content
            text_content = soup.get_text().lower()
            if any(
                re.search(pattern, text_content, re.IGNORECASE) for pattern in patterns
            ):
                return True

            # Check link text and href attributes
            links = soup.find_all("a", href=True)
            for link in links:
                link_text = link.get_text().lower()
                href = link.get("href", "").lower()

                # Check if link text or href contains any of the patterns
                if any(
                    re.search(pattern, link_text, re.IGNORECASE) for pattern in patterns
                ):
                    return True
                if any(re.search(pattern, href, re.IGNORECASE) for pattern in patterns):
                    return True

            # Check HTML attributes (class, id, etc.)
            for tag in soup.find_all():
                for attr_name, attr_value in tag.attrs.items():
                    if isinstance(attr_value, str):
                        if any(
                            re.search(pattern, attr_value.lower(), re.IGNORECASE)
                            for pattern in patterns
                        ):
                            return True
                    elif isinstance(attr_value, list):
                        for value in attr_value:
                            if isinstance(value, str):
                                if any(
                                    re.search(pattern, value.lower(), re.IGNORECASE)
                                    for pattern in patterns
                                ):
                                    return True

            return False
        except Exception:
            return False

    def _check_address_elements(self, soup: BeautifulSoup) -> bool:
        """Check for business address elements."""
        try:
            # Look for address-related text
            address_patterns = [
                r"\d+\s+[a-zA-Z\s]+(?:street|st|avenue|ave|road|rd|lane|ln|drive|dr)",
                r"[a-zA-Z\s]+,\s*[A-Z]{2}\s*\d{5}",
                r"p\.?o\.?\s*box\s*\d+",
            ]

            text_content = soup.get_text()
            return any(
                re.search(pattern, text_content, re.IGNORECASE)
                for pattern in address_patterns
            )
        except Exception:
            return False

    def _check_phone_elements(self, soup: BeautifulSoup) -> bool:
        """Check for phone number elements."""
        try:
            # Look for phone number patterns
            phone_patterns = [
                r"\(\d{3}\)\s*\d{3}-\d{4}",
                r"\d{3}-\d{3}-\d{4}",
                r"\d{3}\.\d{3}\.\d{4}",
                r"\+1\s*\d{3}\s*\d{3}\s*\d{4}",
            ]

            text_content = soup.get_text()
            return any(re.search(pattern, text_content) for pattern in phone_patterns)
        except Exception:
            return False

    def _check_email_elements(self, soup: BeautifulSoup) -> bool:
        """Check for email address elements."""
        try:
            # Look for email patterns
            email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            text_content = soup.get_text()
            return bool(re.search(email_pattern, text_content))
        except Exception:
            return False

    def _check_cta_elements(self, soup: BeautifulSoup) -> bool:
        """Check for call-to-action buttons."""
        try:
            # Look for CTA buttons and links
            cta_elements = soup.find_all(
                ["button", "a", "input"],
                string=re.compile(
                    "|".join(self.cro_patterns["cta_buttons"]), re.IGNORECASE
                ),
            )

            # Also check for buttons with CTA-like classes
            cta_buttons = soup.find_all(
                "button",
                class_=re.compile(r"cta|call-to-action|primary|action", re.IGNORECASE),
            )

            return len(cta_elements) > 0 or len(cta_buttons) > 0
        except Exception:
            return False

    def _check_contact_forms(self, soup: BeautifulSoup) -> bool:
        """Check for contact forms."""
        try:
            # Look for form elements
            forms = soup.find_all("form")

            # Check if any form has contact-related fields
            for form in forms:
                # Check form action attribute
                form_action = form.get("action", "").lower()
                if any(
                    keyword in form_action
                    for keyword in ["contact", "message", "inquiry", "request"]
                ):
                    return True

                # Check form text content
                form_text = form.get_text().lower()
                if any(
                    keyword in form_text
                    for keyword in ["contact", "message", "inquiry", "request"]
                ):
                    return True

                # Check for common contact form fields
                inputs = form.find_all("input")
                for input_elem in inputs:
                    input_type = input_elem.get("type", "").lower()
                    input_name = input_elem.get("name", "").lower()
                    if input_type in ["email", "text"] and any(
                        keyword in input_name
                        for keyword in ["name", "email", "message"]
                    ):
                        return True

            return False
        except Exception:
            return False

    def _check_review_elements(self, soup: BeautifulSoup) -> bool:
        """Check for review elements."""
        try:
            # Look for review-related elements
            review_patterns = [
                r"review",
                r"rating",
                r"star",
                r"feedback",
                r"opinion",
                r"\d+\s*out\s*of\s*\d+",
                r"\d+\s*stars?",
            ]

            # Check text content
            text_content = soup.get_text().lower()
            if any(
                re.search(pattern, text_content, re.IGNORECASE)
                for pattern in review_patterns
            ):
                return True

            # Check HTML attributes (class, id, etc.)
            for tag in soup.find_all():
                for attr_name, attr_value in tag.attrs.items():
                    if isinstance(attr_value, str):
                        if any(
                            re.search(pattern, attr_value.lower(), re.IGNORECASE)
                            for pattern in review_patterns
                        ):
                            return True
                    elif isinstance(attr_value, list):
                        for value in attr_value:
                            if isinstance(value, str):
                                if any(
                                    re.search(pattern, value.lower(), re.IGNORECASE)
                                    for pattern in review_patterns
                                ):
                                    return True

            return False
        except Exception:
            return False

    def _check_trust_badges(self, soup: BeautifulSoup) -> bool:
        """Check for trust badges and certifications."""
        try:
            # Look for trust-related images and text
            trust_patterns = [
                r"trust\s*badge",
                r"certified",
                r"verified",
                r"secure",
                r"bbb",
                r"better\s*business\s*bureau",
                r"guarantee",
            ]

            text_content = soup.get_text().lower()
            return any(
                re.search(pattern, text_content, re.IGNORECASE)
                for pattern in trust_patterns
            )
        except Exception:
            return False

    def _check_viewport_meta(self, soup: BeautifulSoup) -> bool:
        """Check for viewport meta tag."""
        try:
            viewport_meta = soup.find("meta", attrs={"name": "viewport"})
            return viewport_meta is not None
        except Exception:
            return False

    def _check_touch_targets(self, soup: BeautifulSoup) -> bool:
        """Check for adequate touch target sizes."""
        try:
            # Look for buttons and links that might be touch targets
            touch_elements = soup.find_all(["button", "a", "input"])

            # This is a simplified check - in a real implementation, you'd analyze CSS
            # For now, we'll assume the presence of mobile-friendly elements suggests good touch targets
            return len(touch_elements) > 0
        except Exception:
            return False

    def _check_responsive_design(self, soup: BeautifulSoup) -> bool:
        """Check for responsive design indicators."""
        try:
            # Look for responsive design indicators
            responsive_indicators = [
                soup.find("meta", attrs={"name": "viewport"}),
                soup.find(
                    "link",
                    attrs={"media": re.compile(r"max-width|min-width", re.IGNORECASE)},
                ),
                soup.find("style", string=re.compile(r"@media", re.IGNORECASE)),
            ]

            return any(indicator is not None for indicator in responsive_indicators)
        except Exception:
            return False

    def _check_mobile_navigation(self, soup: BeautifulSoup) -> bool:
        """Check for mobile navigation elements."""
        try:
            # Look for mobile navigation indicators
            mobile_nav_patterns = [
                r"mobile\s*nav",
                r"hamburger",
                r"menu\s*toggle",
                r"mobile\s*menu",
                r"responsive\s*nav",
            ]

            text_content = soup.get_text().lower()
            return any(
                re.search(pattern, text_content, re.IGNORECASE)
                for pattern in mobile_nav_patterns
            )
        except Exception:
            return False

    def _check_readable_fonts(self, soup: BeautifulSoup) -> bool:
        """Check for readable font sizes."""
        try:
            # This is a simplified check - in a real implementation, you'd analyze CSS
            # For now, we'll assume the presence of text content suggests readable fonts
            text_content = soup.get_text()
            return (
                len(text_content.strip()) > 100
            )  # Assume readable if there's substantial text
        except Exception:
            return False

    def _check_adequate_spacing(self, soup: BeautifulSoup) -> bool:
        """Check for adequate spacing between elements."""
        try:
            # This is a simplified check - in a real implementation, you'd analyze CSS
            # For now, we'll assume the presence of structured content suggests good spacing
            paragraphs = soup.find_all("p")
            divs = soup.find_all("div")
            return len(paragraphs) > 0 or len(divs) > 0
        except Exception:
            return False

    def _check_heading_structure(self, soup: BeautifulSoup) -> bool:
        """Check for proper heading structure."""
        try:
            headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

            if len(headings) == 0:
                return False

            # Check if there's at least one H1
            h1_count = len(soup.find_all("h1"))

            # Check for logical heading hierarchy
            [int(h.name[1]) for h in headings]

            return h1_count > 0 and len(headings) >= 2
        except Exception:
            return False

    def _check_alt_text(self, soup: BeautifulSoup) -> bool:
        """Check for alt text on images."""
        try:
            images = soup.find_all("img")
            if len(images) == 0:
                return True  # No images means no alt text needed

            images_with_alt = [
                img for img in images if img.get("alt") and img.get("alt").strip()
            ]
            return len(images_with_alt) > 0
        except Exception:
            return False

    def _check_meta_description(self, soup: BeautifulSoup) -> bool:
        """Check for meta description."""
        try:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            return meta_desc is not None and meta_desc.get("content", "").strip() != ""
        except Exception:
            return False

    def _check_meta_keywords(self, soup: BeautifulSoup) -> bool:
        """Check for meta keywords."""
        try:
            meta_keywords = soup.find("meta", attrs={"name": "keywords"})
            return (
                meta_keywords is not None
                and meta_keywords.get("content", "").strip() != ""
            )
        except Exception:
            return False

    def _check_structured_data(self, soup: BeautifulSoup) -> bool:
        """Check for structured data markup."""
        try:
            # Look for JSON-LD structured data
            json_ld_scripts = soup.find_all("script", type="application/ld+json")

            # Look for microdata attributes
            microdata_elements = soup.find_all(attrs={"itemtype": True})

            # Look for RDFa attributes
            rdfa_elements = soup.find_all(attrs={"property": True})

            return (
                len(json_ld_scripts) > 0
                or len(microdata_elements) > 0
                or len(rdfa_elements) > 0
            )
        except Exception:
            return False

    def _check_internal_links(self, soup: BeautifulSoup) -> bool:
        """Check for internal linking structure."""
        try:
            links = soup.find_all("a", href=True)
            internal_links = [
                link
                for link in links
                if link["href"].startswith("#") or not link["href"].startswith("http")
            ]
            return len(internal_links) > 0
        except Exception:
            return False

    def _check_external_links(self, soup: BeautifulSoup) -> bool:
        """Check for external links."""
        try:
            links = soup.find_all("a", href=True)
            external_links = [
                link
                for link in links
                if link["href"].startswith("http")
                and not link["href"].startswith("http://localhost")
            ]
            return len(external_links) > 0
        except Exception:
            return False

    def _check_blog_content(self, soup: BeautifulSoup) -> bool:
        """Check for blog or content section."""
        try:
            # Look for blog-related indicators
            blog_patterns = [
                r"blog",
                r"article",
                r"post",
                r"news",
                r"updates",
                r"latest",
                r"recent",
                r"archive",
            ]

            text_content = soup.get_text().lower()
            return any(
                re.search(pattern, text_content, re.IGNORECASE)
                for pattern in blog_patterns
            )
        except Exception:
            return False

    def _check_social_media_links(self, soup: BeautifulSoup) -> bool:
        """Check for social media links."""
        try:
            # Look for social media platforms
            social_platforms = [
                "facebook",
                "twitter",
                "instagram",
                "linkedin",
                "youtube",
                "tiktok",
                "snapchat",
                "pinterest",
                "reddit",
            ]

            links = soup.find_all("a", href=True)
            social_links = [
                link
                for link in links
                if any(
                    platform in link["href"].lower() for platform in social_platforms
                )
            ]

            return len(social_links) > 0
        except Exception:
            return False

    def _check_partner_logos(self, soup: BeautifulSoup) -> bool:
        """Check for partner or client logos."""
        try:
            # Look for partner-related text
            partner_patterns = [
                r"partners?",
                r"clients?",
                r"customers?",
                r"logos?",
                r"who\s*trusts\s*us",
                r"our\s*clients",
            ]

            # Check text content
            text_content = soup.get_text().lower()
            if any(
                re.search(pattern, text_content, re.IGNORECASE)
                for pattern in partner_patterns
            ):
                return True

            # Check HTML attributes (class, id, alt, etc.)
            for tag in soup.find_all():
                for attr_name, attr_value in tag.attrs.items():
                    if isinstance(attr_value, str):
                        if any(
                            re.search(pattern, attr_value.lower(), re.IGNORECASE)
                            for pattern in partner_patterns
                        ):
                            return True
                    elif isinstance(attr_value, list):
                        for value in attr_value:
                            if isinstance(value, str):
                                if any(
                                    re.search(pattern, value.lower(), re.IGNORECASE)
                                    for pattern in partner_patterns
                                ):
                                    return True

            return False
        except Exception:
            return False

    def _check_user_generated_content(self, soup: BeautifulSoup) -> bool:
        """Check for user-generated content."""
        try:
            # Look for user-generated content indicators
            ugc_patterns = [
                r"user\s*reviews",
                r"customer\s*photos",
                r"guest\s*posts",
                r"community",
                r"forum",
                r"comments",
            ]

            text_content = soup.get_text().lower()
            return any(
                re.search(pattern, text_content, re.IGNORECASE)
                for pattern in ugc_patterns
            )
        except Exception:
            return False

    def _calculate_heuristic_scores(
        self,
        trust_signals: TrustSignals,
        cro_elements: CROElements,
        mobile_usability: MobileUsability,
        content_quality: ContentQuality,
        social_proof: SocialProof,
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
                trust_signals,
                cro_elements,
                mobile_usability,
                content_quality,
                social_proof,
            )

            return HeuristicScore(
                trust_score=trust_score,
                cro_score=cro_score,
                mobile_score=mobile_score,
                content_score=content_score,
                social_score=social_score,
                overall_heuristic_score=overall_score,
                confidence_level=confidence_level,
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
                confidence_level=ConfidenceLevel.LOW,
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
        social_score: float,
    ) -> float:
        """Calculate overall heuristic score with business impact weighting."""
        # Weight scores by business impact
        weights = {
            "trust": 0.30,  # Trust is critical for conversions
            "cro": 0.25,  # CRO directly impacts revenue
            "mobile": 0.20,  # Mobile usability is important
            "content": 0.15,  # Content quality supports other areas
            "social": 0.10,  # Social proof enhances trust
        }

        overall_score = (
            trust_score * weights["trust"]
            + cro_score * weights["cro"]
            + mobile_score * weights["mobile"]
            + content_score * weights["content"]
            + social_score * weights["social"]
        )

        return round(overall_score, 2)

    def _determine_confidence_level(
        self,
        trust_signals: TrustSignals,
        cro_elements: CROElements,
        mobile_usability: MobileUsability,
        content_quality: ContentQuality,
        social_proof: SocialProof,
    ) -> ConfidenceLevel:
        """Determine confidence level based on data availability and quality."""
        # Count detected elements
        total_elements = 0
        detected_elements = 0

        # Trust signals
        for field in TrustSignals.model_fields:
            total_elements += 1
            if getattr(trust_signals, field):
                detected_elements += 1

        # CRO elements
        for field in CROElements.model_fields:
            total_elements += 1
            if getattr(cro_elements, field):
                detected_elements += 1

        # Mobile usability
        for field in MobileUsability.model_fields:
            total_elements += 1
            if getattr(mobile_usability, field):
                detected_elements += 1

        # Content quality
        for field in ContentQuality.model_fields:
            total_elements += 1
            if getattr(content_quality, field):
                detected_elements += 1

        # Social proof
        for field in SocialProof.model_fields:
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
