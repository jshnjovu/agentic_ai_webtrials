"""
Rate limit monitoring API endpoints.
Provides endpoints for checking rate limit status and retrieving alerts.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from src.services import RateLimitMonitor
from src.services.rate_limit_monitor import AlertLevel

router = APIRouter(prefix="/rate-limit-monitoring", tags=["Rate Limit Monitoring"])


@router.get("/status")
async def get_rate_limit_status():
    """
    Get current rate limit status for all APIs.

    Returns:
        Current rate limit status and any active alerts
    """
    try:
        monitor = RateLimitMonitor()
        return monitor.check_rate_limits()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get rate limit status: {str(e)}"
        )


@router.get("/summary")
async def get_rate_limit_summary():
    """
    Get a summary of rate limit status for all APIs.

    Returns:
        Summary of rate limit usage and alert counts
    """
    try:
        monitor = RateLimitMonitor()
        return monitor.get_rate_limit_summary()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get rate limit summary: {str(e)}"
        )


@router.get("/alerts")
async def get_alerts(
    api_name: Optional[str] = Query(None, description="Filter by specific API"),
    level: Optional[str] = Query(
        None, description="Filter by alert level (info, warning, critical)"
    ),
    hours: Optional[int] = Query(
        24, description="Only return alerts from the last N hours"
    ),
):
    """
    Get rate limit alerts with optional filtering.

    Args:
        api_name: Filter by specific API (yelp_fusion, google_places)
        level: Filter by alert level
        hours: Only return alerts from the last N hours

    Returns:
        List of filtered alerts
    """
    try:
        monitor = RateLimitMonitor()

        # Convert level string to enum if provided
        alert_level = None
        if level:
            try:
                alert_level = AlertLevel(level.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid alert level: {level}. Must be one of: info, warning, critical",
                )

        return monitor.get_alerts(api_name=api_name, level=alert_level, hours=hours)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.get("/alerts/{api_name}")
async def get_api_alerts(
    api_name: str,
    level: Optional[str] = Query(None, description="Filter by alert level"),
    hours: Optional[int] = Query(
        24, description="Only return alerts from the last N hours"
    ),
):
    """
    Get rate limit alerts for a specific API.

    Args:
        api_name: Name of the API (yelp_fusion, google_places)
        level: Filter by alert level
        hours: Only return alerts from the last N hours

    Returns:
        List of alerts for the specified API
    """
    try:
        monitor = RateLimitMonitor()

        # Validate API name
        if not monitor.validate_input(api_name):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid API name: {api_name}. Must be one of: yelp_fusion, google_places",
            )

        # Convert level string to enum if provided
        alert_level = None
        if level:
            try:
                alert_level = AlertLevel(level.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid alert level: {level}. Must be one of: info, warning, critical",
                )

        return monitor.get_alerts(api_name=api_name, level=alert_level, hours=hours)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get API alerts: {str(e)}"
        )


@router.post("/alerts/reset")
async def reset_alerts(api_name: Optional[str] = None):
    """
    Reset rate limit alerts.

    Args:
        api_name: Specific API to reset alerts for, or None for all APIs

    Returns:
        Confirmation message
    """
    try:
        monitor = RateLimitMonitor()

        if api_name and not monitor.validate_input(api_name):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid API name: {api_name}. Must be one of: yelp_fusion, google_places",
            )

        monitor.reset_alerts(api_name)

        if api_name:
            return {"message": f"Alerts reset for {api_name}"}
        else:
            return {"message": "All alerts reset"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset alerts: {str(e)}")


@router.get("/health")
async def get_monitoring_health():
    """
    Get health status of the rate limit monitoring system.

    Returns:
        Health status information
    """
    try:
        monitor = RateLimitMonitor()

        # Test basic functionality
        summary = monitor.get_rate_limit_summary()

        return {
            "status": "healthy",
            "timestamp": summary.get("timestamp"),
            "apis_monitored": len(summary.get("apis", {})),
            "total_alerts": summary.get("total_alerts", 0),
            "system_operational": True,
        }

    except Exception as e:
        return {"status": "unhealthy", "error": str(e), "system_operational": False}
