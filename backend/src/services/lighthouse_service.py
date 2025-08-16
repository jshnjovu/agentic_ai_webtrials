"""
Lighthouse API integration service for website performance auditing.
Handles website audits using Google PageSpeed Insights API with timeout and retry logic.
"""

import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.core import BaseService, get_api_config
from src.services import RateLimiter
from src.utils.score_calculation import calculate_overall_score


class LighthouseService(BaseService):
    """Lighthouse API integration service for website performance auditing."""

    def __init__(self):
        super().__init__("LighthouseService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.api_key = self.api_config.LIGHTHOUSE_API_KEY
        self.timeout = self.api_config.LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS
        self.connect_timeout = self.api_config.LIGHTHOUSE_CONNECT_TIMEOUT_SECONDS
        self.read_timeout = self.api_config.LIGHTHOUSE_READ_TIMEOUT_SECONDS
        self.fallback_timeout = self.api_config.LIGHTHOUSE_FALLBACK_TIMEOUT_SECONDS

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if isinstance(data, dict):
            required_fields = ["website_url", "business_id"]
            return all(field in data for field in required_fields)
        return False

    def run_lighthouse_audit(
        self,
        website_url: str,
        business_id: str,
        run_id: Optional[str] = None,
        strategy: str = "desktop",
    ) -> Dict[str, Any]:
        """
        Run a Lighthouse audit for a website using Google PageSpeed Insights API.

        Args:
            website_url: URL of the website to audit
            business_id: Business identifier for logging and tracking
            run_id: Run identifier for logging and tracking
            strategy: Audit strategy ('desktop' or 'mobile')

        Returns:
            Dictionary containing audit results or error information
        """
        try:
            self.log_operation(
                f"Starting Lighthouse audit for {website_url} using {strategy} strategy",
                run_id=run_id,
                business_id=business_id,
            )

            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request(
                "lighthouse", run_id
            )
            if not can_request:
                return self._create_error_response(
                    f"Rate limit exceeded: {reason}",
                    "rate_limit_check",
                    website_url,
                    business_id,
                    run_id,
                )

            # Validate URL format
            if not self._validate_url(website_url):
                return self._create_error_response(
                    "Invalid website URL format",
                    "url_validation",
                    website_url,
                    business_id,
                    run_id,
                )

            # Build API request parameters
            params = self._build_audit_params(website_url, strategy)

            # Execute audit with timeout and retry logic
            audit_result = self._execute_audit_with_retry(params, run_id, business_id)

            # Record the request in rate limiter
            self.rate_limiter.record_request(
                "lighthouse", audit_result["success"], run_id
            )

            # If primary audit fails, attempt fallback audit
            if (
                not audit_result["success"]
                and audit_result.get("error_code") == "TIMEOUT"
            ):
                self.log_operation(
                    f"Primary audit failed with timeout, attempting fallback audit for {website_url}",
                    run_id=run_id,
                    business_id=business_id,
                    context="fallback_attempt",
                )

                # Attempt fallback audit with reduced scope
                fallback_result = self._execute_fallback_audit(
                    website_url, business_id, run_id, strategy
                )

                if fallback_result["success"]:
                    self.log_operation(
                        f"Fallback audit successful for {website_url}",
                        run_id=run_id,
                        business_id=business_id,
                        context="fallback_success",
                    )
                    return fallback_result
                else:
                    self.log_operation(
                        f"Fallback audit also failed for {website_url}",
                        run_id=run_id,
                        business_id=business_id,
                        context="fallback_failure",
                    )
                    # Return fallback result instead of original audit result
                    return fallback_result

            if not audit_result["success"]:
                return audit_result

            # Process and normalize audit results
            processed_results = self._process_audit_results(
                audit_result["data"], website_url, business_id, run_id
            )

            self.log_operation(
                f"Successfully completed Lighthouse audit for {website_url}",
                run_id=run_id,
                business_id=business_id,
                scores=processed_results.get("scores", {}),
            )

            return processed_results

        except Exception as e:
            self.log_error(e, "lighthouse_audit_execution", run_id, business_id)
            return self._create_error_response(
                str(e), "audit_execution", website_url, business_id, run_id
            )

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            if not url.startswith(("http://", "https://")):
                return False
            # Basic URL validation - could be enhanced with more sophisticated checks
            return True
        except Exception:
            return False

    def _build_audit_params(self, website_url: str, strategy: str) -> Dict[str, str]:
        """Build API request parameters for PageSpeed Insights."""
        return {
            "url": website_url,
            "key": self.api_key,
            "strategy": strategy,
            "category": "performance,accessibility,best-practices,seo",
            "prettyPrint": "false",
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, requests.Timeout)),
    )
    def _execute_audit_with_retry(
        self, params: Dict[str, str], run_id: Optional[str], business_id: str
    ) -> Dict[str, Any]:
        """Execute audit with retry logic and timeout handling."""
        try:
            # Build full URL with parameters
            full_url = f"{self.base_url}?{urlencode(params)}"

            self.log_operation(
                "Executing Lighthouse audit request",
                run_id=run_id,
                business_id=business_id,
                url=params.get("url"),
            )

            # Make request with enhanced timeout handling
            timeout_tuple = (self.connect_timeout, self.read_timeout)
            response = requests.get(
                full_url,
                timeout=timeout_tuple,
                headers={"User-Agent": "LeadGen-Makeover-Agent/1.0"},
            )

            response.raise_for_status()

            # Parse response
            audit_data = response.json()

            return {
                "success": True,
                "data": audit_data,
                "status_code": response.status_code,
            }

        except requests.Timeout:
            self.log_error(
                Exception("Lighthouse audit request timed out"),
                "audit_timeout",
                run_id,
                business_id,
            )
            return {
                "success": False,
                "error": "Audit request timed out",
                "error_code": "TIMEOUT",
                "context": "audit_execution",
            }

        except requests.RequestException as e:
            self.log_error(e, "audit_request_failed", run_id, business_id)
            return {
                "success": False,
                "error": f"Audit request failed: {str(e)}",
                "error_code": "REQUEST_FAILED",
                "context": "audit_execution",
            }

    def _process_audit_results(
        self,
        audit_data: Dict[str, Any],
        website_url: str,
        business_id: str,
        run_id: Optional[str],
    ) -> Dict[str, Any]:
        """Process and normalize audit results."""
        try:
            # Extract category scores
            categories = audit_data.get("lighthouseResult", {}).get("categories", {})

            scores = {
                "performance": self._extract_score(categories, "performance"),
                "accessibility": self._extract_score(categories, "accessibility"),
                "best_practices": self._extract_score(categories, "best-practices"),
                "seo": self._extract_score(categories, "seo"),
            }

            # Calculate overall score using utility function
            overall_score = calculate_overall_score(scores)

            # Extract Core Web Vitals
            core_web_vitals = self._extract_core_web_vitals(audit_data)

            # Determine confidence level
            confidence = self._determine_confidence(audit_data)

            return {
                "success": True,
                "website_url": website_url,
                "business_id": business_id,
                "run_id": run_id,
                "audit_timestamp": time.time(),
                "strategy": audit_data.get("lighthouseResult", {})
                .get("configSettings", {})
                .get("formFactor", "desktop"),
                "scores": scores,
                "overall_score": overall_score,
                "core_web_vitals": core_web_vitals,
                "confidence": confidence,
                "raw_data": audit_data,
            }

        except Exception as e:
            self.log_error(e, "audit_results_processing", run_id, business_id)
            return self._create_error_response(
                f"Failed to process audit results: {str(e)}",
                "results_processing",
                website_url,
                business_id,
                run_id,
            )

    def _extract_score(self, categories: Dict[str, Any], category_name: str) -> float:
        """Extract score from a specific category."""
        category = categories.get(category_name, {})
        score = category.get("score", 0)
        # Convert from 0-1 scale to 0-100 scale
        return round(score * 100, 1) if score is not None else 0.0

    def _extract_core_web_vitals(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Core Web Vitals metrics from audit data."""
        try:
            audits = audit_data.get("lighthouseResult", {}).get("audits", {})

            return {
                "first_contentful_paint": self._extract_metric(
                    audits, "first-contentful-paint"
                ),
                "largest_contentful_paint": self._extract_metric(
                    audits, "largest-contentful-paint"
                ),
                "cumulative_layout_shift": self._extract_metric(
                    audits, "cumulative-layout-shift"
                ),
                "total_blocking_time": self._extract_metric(
                    audits, "total-blocking-time"
                ),
                "speed_index": self._extract_metric(audits, "speed-index"),
            }
        except Exception:
            return {}

    def _extract_metric(
        self, audits: Dict[str, Any], metric_name: str
    ) -> Optional[float]:
        """Extract a specific metric value from audits."""
        try:
            metric = audits.get(metric_name, {})
            value = metric.get("numericValue")
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None

    def _determine_confidence(self, audit_data: Dict[str, Any]) -> str:
        """Determine confidence level based on audit completion status."""
        try:
            # Check if audit completed successfully
            if audit_data.get("lighthouseResult", {}).get("runtimeError"):
                return "low"

            # Check if all categories have scores
            categories = audit_data.get("lighthouseResult", {}).get("categories", {})
            required_categories = [
                "performance",
                "accessibility",
                "best-practices",
                "seo",
            ]

            for category in required_categories:
                if (
                    category not in categories
                    or categories[category].get("score") is None
                ):
                    return "medium"

            return "high"

        except Exception:
            return "low"

    def _create_error_response(
        self,
        error: str,
        context: str,
        website_url: str,
        business_id: str,
        run_id: Optional[str],
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        return {
            "success": False,
            "error": error,
            "context": context,
            "website_url": website_url,
            "business_id": business_id,
            "run_id": run_id,
            "audit_timestamp": time.time(),
            "scores": {
                "performance": 0.0,
                "accessibility": 0.0,
                "best_practices": 0.0,
                "seo": 0.0,
            },
            "overall_score": 0.0,
            "confidence": "low",
        }

    def _execute_fallback_audit(
        self, website_url: str, business_id: str, run_id: Optional[str], strategy: str
    ) -> Dict[str, Any]:
        """
        Execute fallback audit with reduced parameters when primary audit fails.
        Uses faster strategy and reduced categories for quicker completion.
        """
        try:
            self.log_operation(
                f"Executing fallback audit for {website_url}",
                run_id=run_id,
                business_id=business_id,
                context="fallback_audit",
            )

            # Build fallback parameters with reduced scope
            fallback_params = {
                "url": website_url,
                "key": self.api_key,
                "strategy": strategy,
                "category": "performance",  # Only performance for faster results
                "prettyPrint": "false",
            }

            # Execute with shorter timeout
            timeout_tuple = (self.connect_timeout, self.fallback_timeout)

            response = requests.get(
                f"{self.base_url}?{urlencode(fallback_params)}",
                timeout=timeout_tuple,
                headers={"User-Agent": "LeadGen-Makeover-Agent/1.0"},
            )

            response.raise_for_status()
            audit_data = response.json()

            # Process with limited data
            scores = {
                "performance": self._extract_score(
                    audit_data.get("lighthouseResult", {}).get("categories", {}),
                    "performance",
                ),
                "accessibility": 0.0,  # Not available in fallback
                "best_practices": 0.0,  # Not available in fallback
                "seo": 0.0,  # Not available in fallback
            }

            overall_score = scores["performance"]  # Only performance score available

            return {
                "success": True,
                "data": audit_data,
                "status_code": response.status_code,
                "fallback_used": True,
                "scores": scores,
                "overall_score": overall_score,
                "confidence": "medium",  # Lower confidence due to limited data
            }

        except Exception as e:
            self.log_error(e, "fallback_audit_failed", run_id, business_id)
            return {
                "success": False,
                "error": f"Fallback audit failed: {str(e)}",
                "error_code": "FALLBACK_FAILED",
                "context": "fallback_audit",
                "fallback_used": True,
            }
