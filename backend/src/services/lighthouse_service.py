"""
Lighthouse CLI integration service for website performance auditing.
Handles website audits using actual Lighthouse CLI tool with proper configuration.
"""

import json
import time
import subprocess
import tempfile
import os
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.core import BaseService, get_api_config
from src.services import RateLimiter
from src.utils.score_calculation import calculate_overall_score


class LighthouseService(BaseService):
    """Lighthouse CLI integration service for website performance auditing."""
    
    def __init__(self):
        super().__init__("LighthouseService")
        self.api_config = get_api_config()
        self.rate_limiter = RateLimiter()
        self.lighthouse_path = self._get_lighthouse_path()
        self.timeout = self.api_config.LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS
        self.connect_timeout = self.api_config.LIGHTHOUSE_CONNECT_TIMEOUT_SECONDS
        self.read_timeout = self.api_config.LIGHTHOUSE_READ_TIMEOUT_SECONDS
        self.fallback_timeout = self.api_config.LIGHTHOUSE_FALLBACK_TIMEOUT_SECONDS
        
    def _get_lighthouse_path(self) -> str:
        """Get the path to Lighthouse CLI executable."""
        # Try to find lighthouse in PATH
        try:
            result = subprocess.run(['which', 'lighthouse'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try npx lighthouse
        try:
            result = subprocess.run(['npx', 'lighthouse', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return 'npx lighthouse'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback to global lighthouse
        return 'lighthouse'
        
    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        if isinstance(data, dict):
            required_fields = ['website_url', 'business_id']
            return all(field in data for field in required_fields)
        return False
    
    def run_lighthouse_audit(self, website_url: str, business_id: str, 
                           run_id: Optional[str] = None, 
                           strategy: str = "desktop") -> Dict[str, Any]:
        """
        Run a Lighthouse audit for a website using Lighthouse CLI.
        
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
                f"Starting Lighthouse CLI audit for {website_url} using {strategy} strategy",
                run_id=run_id,
                business_id=business_id
            )
            
            # Check rate limiting
            can_request, reason = self.rate_limiter.can_make_request("lighthouse", run_id)
            if not can_request:
                return self._create_error_response(
                    f"Rate limit exceeded: {reason}",
                    "rate_limit_check",
                    website_url,
                    business_id,
                    run_id
                )
            
            # Validate URL format
            if not self._validate_url(website_url):
                return self._create_error_response(
                    "Invalid website URL format",
                    "url_validation",
                    website_url,
                    business_id,
                    run_id
                )
            
            # Execute Lighthouse CLI audit
            audit_result = self._execute_lighthouse_cli(website_url, strategy, run_id, business_id)
            
            # Record the request in rate limiter
            self.rate_limiter.record_request("lighthouse", audit_result["success"], run_id)
            
            # If primary audit fails, attempt fallback audit
            if not audit_result["success"] and audit_result.get("error_code") == "TIMEOUT":
                self.log_operation(
                    f"Primary audit failed with timeout, attempting fallback audit for {website_url}",
                    run_id=run_id,
                    business_id=business_id,
                    context="fallback_attempt"
                )
                
                # Attempt fallback audit with reduced scope
                fallback_result = self._execute_fallback_audit(website_url, business_id, run_id, strategy)
                
                if fallback_result["success"]:
                    self.log_operation(
                        f"Fallback audit successful for {website_url}",
                        run_id=run_id,
                        business_id=business_id,
                        context="fallback_success"
                    )
                    return fallback_result
                else:
                    self.log_operation(
                        f"Fallback audit also failed for {website_url}",
                        run_id=run_id,
                        business_id=business_id,
                        context="fallback_failure"
                    )
                    return fallback_result
            
            if not audit_result["success"]:
                return audit_result
            
            # Process and normalize audit results
            processed_results = self._process_audit_results(audit_result["data"], website_url, business_id, run_id)
            
            self.log_operation(
                f"Successfully completed Lighthouse CLI audit for {website_url}",
                run_id=run_id,
                business_id=business_id,
                scores=processed_results.get("scores", {})
            )
            
            return processed_results
            
        except Exception as e:
            self.log_error(e, "lighthouse_audit_execution", run_id, business_id)
            return self._create_error_response(
                str(e),
                "audit_execution",
                website_url,
                business_id,
                run_id
            )
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            if not url.startswith(('http://', 'https://')):
                return False
            # Basic URL validation - could be enhanced with more sophisticated checks
            return True
        except Exception:
            return False
    
    def _execute_lighthouse_cli(self, website_url: str, strategy: str, 
                               run_id: Optional[str], business_id: str) -> Dict[str, Any]:
        """Execute Lighthouse CLI audit."""
        try:
            # Create temporary file for output
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                temp_file_path = temp_file.name
            
            try:
                # Build Lighthouse CLI command
                cmd = [
                    self.lighthouse_path,
                    website_url,
                    '--output=json',
                    f'--output-path={temp_file_path}',
                    f'--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage',
                    '--only-categories=performance,accessibility,best-practices,seo',
                    '--quiet',
                    '--no-enable-error-reporting'
                ]
                
                # Add strategy-specific flags
                if strategy == "mobile":
                    cmd.extend(['--form-factor=mobile', '--screenEmulation.mobile=true'])
                else:
                    cmd.extend(['--form-factor=desktop', '--screenEmulation.mobile=false'])
                
                self.log_operation(
                    f"Executing Lighthouse CLI command: {' '.join(cmd)}",
                    run_id=run_id,
                    business_id=business_id,
                    url=website_url
                )
                
                # Execute command with timeout
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                if result.returncode != 0:
                    return {
                        "success": False,
                        "error": f"Lighthouse CLI failed: {result.stderr}",
                        "error_code": "CLI_FAILED",
                        "context": "lighthouse_cli_execution"
                    }
                
                # Read and parse the output file
                if os.path.exists(temp_file_path):
                    with open(temp_file_path, 'r') as f:
                        audit_data = json.load(f)
                    
                    return {
                        "success": True,
                        "data": audit_data,
                        "status_code": 200
                    }
                else:
                    return {
                        "success": False,
                        "error": "Lighthouse output file not found",
                        "error_code": "OUTPUT_MISSING",
                        "context": "lighthouse_cli_execution"
                    }
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except subprocess.TimeoutExpired:
            self.log_error(
                Exception("Lighthouse CLI audit timed out"),
                "audit_timeout",
                run_id,
                business_id
            )
            return {
                "success": False,
                "error": "Lighthouse CLI audit timed out",
                "error_code": "TIMEOUT",
                "context": "lighthouse_cli_execution"
            }
            
        except Exception as e:
            self.log_error(e, "lighthouse_cli_execution", run_id, business_id)
            return {
                "success": False,
                "error": f"Lighthouse CLI execution failed: {str(e)}",
                "error_code": "EXECUTION_FAILED",
                "context": "lighthouse_cli_execution"
            }
    
    def _process_audit_results(self, audit_data: Dict[str, Any], website_url: str,
                              business_id: str, run_id: Optional[str]) -> Dict[str, Any]:
        """Process and normalize audit results."""
        try:
            # Extract category scores
            categories = audit_data.get('categories', {})
            
            scores = {
                'performance': self._extract_score(categories, 'performance'),
                'accessibility': self._extract_score(categories, 'accessibility'),
                'best_practices': self._extract_score(categories, 'best-practices'),
                'seo': self._extract_score(categories, 'seo')
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
                "strategy": audit_data.get('configSettings', {}).get('formFactor', 'desktop'),
                "scores": scores,
                "overall_score": overall_score,
                "core_web_vitals": core_web_vitals,
                "confidence": confidence,
                "raw_data": audit_data
            }
            
        except Exception as e:
            self.log_error(e, "audit_results_processing", run_id, business_id)
            return self._create_error_response(
                f"Failed to process audit results: {str(e)}",
                "results_processing",
                website_url,
                business_id,
                run_id
            )
    
    def _extract_score(self, categories: Dict[str, Any], category_name: str) -> float:
        """Extract score from a specific category."""
        category = categories.get(category_name, {})
        score = category.get('score', 0)
        # Convert from 0-1 scale to 0-100 scale
        return round(score * 100, 1) if score is not None else 0.0
    
    def _extract_core_web_vitals(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Core Web Vitals metrics from audit data."""
        try:
            audits = audit_data.get('audits', {})
            
            return {
                'first_contentful_paint': self._extract_metric(audits, 'first-contentful-paint'),
                'largest_contentful_paint': self._extract_metric(audits, 'largest-contentful-paint'),
                'cumulative_layout_shift': self._extract_metric(audits, 'cumulative-layout-shift'),
                'total_blocking_time': self._extract_metric(audits, 'total-blocking-time'),
                'speed_index': self._extract_metric(audits, 'speed-index')
            }
        except Exception:
            return {}
    
    def _extract_metric(self, audits: Dict[str, Any], metric_name: str) -> Optional[float]:
        """Extract a specific metric value from audits."""
        try:
            metric = audits.get(metric_name, {})
            value = metric.get('numericValue')
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def _determine_confidence(self, audit_data: Dict[str, Any]) -> str:
        """Determine confidence level based on audit completion status."""
        try:
            # Check if audit completed successfully
            if audit_data.get('runtimeError'):
                return "low"
            
            # Check if all categories have scores
            categories = audit_data.get('categories', {})
            required_categories = ['performance', 'accessibility', 'best-practices', 'seo']
            
            for category in required_categories:
                if category not in categories or categories[category].get('score') is None:
                    return "medium"
            
            return "high"
            
        except Exception:
            return "low"
    
    def _create_error_response(self, error: str, context: str, website_url: str,
                             business_id: str, run_id: Optional[str]) -> Dict[str, Any]:
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
                'performance': 0.0,
                'accessibility': 0.0,
                'best_practices': 0.0,
                'seo': 0.0
            },
            'overall_score': 0.0,
            'confidence': 'low'
        }
    
    def _execute_fallback_audit(self, website_url: str, business_id: str, 
                               run_id: Optional[str], strategy: str) -> Dict[str, Any]:
        """
        Execute fallback audit with reduced parameters when primary audit fails.
        Uses faster strategy and reduced categories for quicker completion.
        """
        try:
            self.log_operation(
                f"Executing fallback audit for {website_url}",
                run_id=run_id,
                business_id=business_id,
                context="fallback_audit"
            )
            
            # Build fallback command with reduced scope
            cmd = [
                self.lighthouse_path,
                website_url,
                '--output=json',
                '--only-categories=performance',  # Only performance for faster results
                '--chrome-flags=--headless --no-sandbox --disable-dev-shm-usage',
                '--quiet',
                '--no-enable-error-reporting'
            ]
            
            # Add strategy-specific flags
            if strategy == "mobile":
                cmd.extend(['--form-factor=mobile', '--screenEmulation.mobile=true'])
            else:
                cmd.extend(['--form-factor=desktop', '--screenEmulation.mobile=false'])
            
            # Execute with shorter timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.fallback_timeout
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Fallback audit failed: {result.stderr}",
                    "error_code": "FALLBACK_FAILED",
                    "context": "fallback_audit",
                    "fallback_used": True
                }
            
            # Parse output from stdout for fallback
            try:
                audit_data = json.loads(result.stdout)
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Failed to parse fallback audit output",
                    "error_code": "PARSE_FAILED",
                    "context": "fallback_audit",
                    "fallback_used": True
                }
            
            # Process with limited data
            scores = {
                'performance': self._extract_score(audit_data.get('categories', {}), 'performance'),
                'accessibility': 0.0,  # Not available in fallback
                'best_practices': 0.0,  # Not available in fallback
                'seo': 0.0  # Not available in fallback
            }
            
            overall_score = scores['performance']  # Only performance score available
            
            return {
                "success": True,
                "data": audit_data,
                "status_code": 200,
                "fallback_used": True,
                "scores": scores,
                "overall_score": overall_score,
                "confidence": "medium"  # Lower confidence due to limited data
            }
            
        except Exception as e:
            self.log_error(e, "fallback_audit_failed", run_id, business_id)
            return {
                "success": False,
                "error": f"Fallback audit failed: {str(e)}",
                "error_code": "FALLBACK_FAILED",
                "context": "fallback_audit",
                "fallback_used": True
            }
