"""
Rate limit monitoring service for tracking API usage and generating alerts.
Provides monitoring, alerting, and reporting capabilities for rate limits.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from src.core.base_service import BaseService
from src.services import RateLimiter
from src.core.config import get_api_config


class AlertLevel(Enum):
    """Alert levels for rate limit monitoring."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class RateLimitAlert:
    """Rate limit alert data structure."""

    timestamp: datetime
    api_name: str
    level: AlertLevel
    message: str
    current_usage: int
    limit: int
    usage_percentage: float
    remaining_requests: int
    reset_time: str
    run_id: Optional[str] = None


class RateLimitMonitor(BaseService):
    """Rate limit monitoring service with alerting capabilities."""

    def __init__(self):
        super().__init__("RateLimitMonitor")
        self.rate_limiter = RateLimiter()
        self.api_config = get_api_config()
        self.alerts: List[RateLimitAlert] = []
        self.alert_thresholds = {
            "yelp_fusion": {
                "warning": 0.7,  # 70% of daily limit
                "critical": 0.9,  # 90% of daily limit
            },
            "google_places": {
                "warning": 0.8,  # 80% of per-minute limit
                "critical": 0.95,  # 95% of per-minute limit
            },
        }
        self.max_alerts_per_api = 100  # Prevent memory issues

    def validate_input(self, data: Any) -> bool:
        """Validate input data for the service."""
        return isinstance(data, str) and data in self.alert_thresholds

    def check_rate_limits(self, run_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check current rate limits for all APIs and generate alerts if needed.

        Args:
            run_id: Optional run identifier for logging

        Returns:
            Dictionary with rate limit status and any generated alerts
        """
        try:
            self.log_operation("Checking rate limits for all APIs", run_id=run_id)

            status = {}
            new_alerts = []

            for api_name in self.alert_thresholds:
                api_status = self._check_api_rate_limit(api_name, run_id)
                status[api_name] = api_status

                # Generate alerts if thresholds are exceeded
                if api_status["alerts"]:
                    new_alerts.extend(api_status["alerts"])

            # Store new alerts
            self._store_alerts(new_alerts)

            # Clean up old alerts
            self._cleanup_old_alerts()

            return {
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "alerts_generated": len(new_alerts),
                "total_alerts": len(self.alerts),
            }

        except Exception as e:
            self.log_error(e, "rate_limit_check", run_id)
            return {
                "error": f"Failed to check rate limits: {str(e)}",
                "timestamp": datetime.now().isoformat(),
            }

    def _check_api_rate_limit(
        self, api_name: str, run_id: Optional[str]
    ) -> Dict[str, Any]:
        """
        Check rate limit for a specific API and generate alerts if needed.

        Args:
            api_name: Name of the API to check
            run_id: Optional run identifier for logging

        Returns:
            Dictionary with API status and any generated alerts
        """
        try:
            rate_limit_info = self.rate_limiter.get_rate_limit_info(api_name)
            if not rate_limit_info:
                return {"error": "Unable to get rate limit info"}

            current_usage = rate_limit_info["current_usage"]
            limit = rate_limit_info["limit"]
            usage_percentage = current_usage / limit if limit > 0 else 0

            # Check if we can make requests
            can_request, reason = self.rate_limiter.can_make_request(api_name)

            # Generate alerts based on thresholds
            alerts = self._generate_alerts(
                api_name, current_usage, limit, usage_percentage, run_id
            )

            return {
                "can_make_request": can_request,
                "reason": reason,
                "current_usage": current_usage,
                "limit": limit,
                "usage_percentage": usage_percentage,
                "remaining": rate_limit_info["remaining"],
                "reset_time": rate_limit_info["reset_time"],
                "alerts": alerts,
            }

        except Exception as e:
            self.log_error(e, f"check_api_rate_limit_{api_name}", run_id)
            return {"error": f"Failed to check {api_name}: {str(e)}"}

    def _generate_alerts(
        self,
        api_name: str,
        current_usage: int,
        limit: int,
        usage_percentage: float,
        run_id: Optional[str],
    ) -> List[RateLimitAlert]:
        """
        Generate alerts based on usage thresholds.

        Args:
            api_name: Name of the API
            current_usage: Current number of requests used
            limit: Total request limit
            usage_percentage: Percentage of limit used
            run_id: Optional run identifier for logging

        Returns:
            List of generated alerts
        """
        alerts = []
        thresholds = self.alert_thresholds.get(api_name, {})

        # Check warning threshold
        if usage_percentage >= thresholds.get("warning", 0.7):
            alert = RateLimitAlert(
                timestamp=datetime.now(),
                api_name=api_name,
                level=AlertLevel.WARNING,
                message=f"API usage approaching limit: {usage_percentage:.1%}",
                current_usage=current_usage,
                limit=limit,
                usage_percentage=usage_percentage,
                remaining_requests=limit - current_usage,
                reset_time=self.rate_limiter.get_rate_limit_info(api_name)[
                    "reset_time"
                ],
                run_id=run_id,
            )
            alerts.append(alert)

        # Check critical threshold
        if usage_percentage >= thresholds.get("critical", 0.9):
            alert = RateLimitAlert(
                timestamp=datetime.now(),
                api_name=api_name,
                level=AlertLevel.CRITICAL,
                message=f"API usage critical: {usage_percentage:.1%}",
                current_usage=current_usage,
                limit=limit,
                usage_percentage=usage_percentage,
                remaining_requests=limit - current_usage,
                reset_time=self.rate_limiter.get_rate_limit_info(api_name)[
                    "reset_time"
                ],
                run_id=run_id,
            )
            alerts.append(alert)

        # Check if rate limit is exceeded
        if current_usage >= limit:
            alert = RateLimitAlert(
                timestamp=datetime.now(),
                api_name=api_name,
                level=AlertLevel.CRITICAL,
                message="Rate limit exceeded - no more requests allowed",
                current_usage=current_usage,
                limit=limit,
                usage_percentage=usage_percentage,
                remaining_requests=0,
                reset_time=self.rate_limiter.get_rate_limit_info(api_name)[
                    "reset_time"
                ],
                run_id=run_id,
            )
            alerts.append(alert)

        return alerts

    def _store_alerts(self, new_alerts: List[RateLimitAlert]):
        """Store new alerts in the alerts list."""
        self.alerts.extend(new_alerts)

        # Log new alerts
        for alert in new_alerts:
            if alert.level == AlertLevel.CRITICAL:
                self.logger.error(
                    f"CRITICAL ALERT: {alert.message} for {alert.api_name}"
                )
            elif alert.level == AlertLevel.WARNING:
                self.logger.warning(f"WARNING: {alert.message} for {alert.api_name}")
            else:
                self.logger.info(f"INFO: {alert.message} for {alert.api_name}")

    def _cleanup_old_alerts(self):
        """Remove old alerts to prevent memory issues."""
        if len(self.alerts) > self.max_alerts_per_api * len(self.alert_thresholds):
            # Keep only the most recent alerts
            self.alerts.sort(key=lambda x: x.timestamp, reverse=True)
            self.alerts = self.alerts[
                : self.max_alerts_per_api * len(self.alert_thresholds)
            ]

    def get_alerts(
        self,
        api_name: Optional[str] = None,
        level: Optional[AlertLevel] = None,
        hours: Optional[int] = 24,
    ) -> List[Dict[str, Any]]:
        """
        Get alerts with optional filtering.

        Args:
            api_name: Filter by specific API
            level: Filter by alert level
            hours: Only return alerts from the last N hours

        Returns:
            List of filtered alerts as dictionaries
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)

            filtered_alerts = [
                alert
                for alert in self.alerts
                if alert.timestamp >= cutoff_time
                and (api_name is None or alert.api_name == api_name)
                and (level is None or alert.level == level)
            ]

            # Convert to dictionaries and sort by timestamp
            alert_dicts = [asdict(alert) for alert in filtered_alerts]
            alert_dicts.sort(key=lambda x: x["timestamp"], reverse=True)

            return alert_dicts

        except Exception as e:
            self.log_error(e, "get_alerts")
            return []

    def get_rate_limit_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current rate limit status for all APIs.

        Returns:
            Dictionary with rate limit summary
        """
        try:
            summary = {
                "timestamp": datetime.now().isoformat(),
                "apis": {},
                "total_alerts": len(self.alerts),
                "critical_alerts": len(
                    [a for a in self.alerts if a.level == AlertLevel.CRITICAL]
                ),
                "warning_alerts": len(
                    [a for a in self.alerts if a.level == AlertLevel.WARNING]
                ),
            }

            for api_name in self.alert_thresholds:
                rate_limit_info = self.rate_limiter.get_rate_limit_info(api_name)
                if rate_limit_info:
                    summary["apis"][api_name] = {
                        "current_usage": rate_limit_info["current_usage"],
                        "limit": rate_limit_info["limit"],
                        "usage_percentage": rate_limit_info["current_usage"]
                        / rate_limit_info["limit"],
                        "remaining": rate_limit_info["remaining"],
                        "reset_time": rate_limit_info["reset_time"],
                    }

            return summary

        except Exception as e:
            self.log_error(e, "get_rate_limit_summary")
            return {"error": f"Failed to get summary: {str(e)}"}

    def reset_alerts(self, api_name: Optional[str] = None):
        """
        Reset alerts for a specific API or all APIs.

        Args:
            api_name: Specific API to reset, or None for all
        """
        if api_name:
            self.alerts = [alert for alert in self.alerts if alert.api_name != api_name]
            self.log_operation(f"Reset alerts for {api_name}")
        else:
            self.alerts.clear()
            self.log_operation("Reset all alerts")
