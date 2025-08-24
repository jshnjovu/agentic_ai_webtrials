"""
Batch Processing API endpoints for concurrent website analysis.
Provides REST API for managing batch processing jobs with real-time progress tracking.
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

from src.services.batch_processor import BatchProcessor, BatchJobConfig, JobPriority
from src.services.comprehensive_speed_service import ComprehensiveSpeedService
from src.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/batch-processing", tags=["batch-processing"])

# Initialize services
batch_processor = BatchProcessor()
comprehensive_speed_service = ComprehensiveSpeedService()


# Request/Response Models
class BatchJobRequest(BaseModel):
    """Request model for starting a batch analysis job."""
    urls: List[str] = Field(..., min_items=1, max_items=100, description="List of URLs to analyze")
    business_ids: Optional[List[str]] = Field(None, description="Optional business IDs corresponding to URLs")
    run_id: Optional[str] = Field(None, description="Optional processing run ID for tracking")
    batch_size: int = Field(5, ge=1, le=20, description="Number of URLs to process concurrently")
    priority: str = Field("normal", description="Job priority: low, normal, high, urgent")
    timeout_seconds: int = Field(300, ge=60, le=1800, description="Timeout per URL in seconds")
    strategy: str = Field("mobile", description="PageSpeed analysis strategy: mobile or desktop")
    name: Optional[str] = Field(None, description="Optional custom name for the batch job")
    description: Optional[str] = Field(None, description="Optional description for the batch job")


class BatchJobResponse(BaseModel):
    """Response model for batch job creation."""
    success: bool = Field(..., description="Whether the batch job was created successfully")
    batch_job_id: str = Field(..., description="Unique identifier for the batch job")
    message: str = Field(..., description="Status message")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in seconds")
    total_urls: int = Field(..., description="Total number of URLs to process")
    batch_size: int = Field(..., description="Concurrent processing batch size")
    priority: str = Field(..., description="Job priority level")
    created_at: datetime = Field(..., description="When the job was created")


class BatchJobProgress(BaseModel):
    """Response model for batch job progress."""
    batch_job_id: str = Field(..., description="Unique identifier for the batch job")
    name: str = Field(..., description="Batch job name")
    status: str = Field(..., description="Current job status")
    total_urls: int = Field(..., description="Total number of URLs")
    completed_urls: int = Field(..., description="Number of completed URLs")
    failed_urls: int = Field(..., description="Number of failed URLs")
    progress_percentage: float = Field(..., description="Progress percentage (0-100)")
    estimated_remaining_time: Optional[int] = Field(None, description="Estimated remaining time in seconds")
    started_at: Optional[datetime] = Field(None, description="When processing started")
    completed_at: Optional[datetime] = Field(None, description="When processing completed")
    current_step: str = Field(..., description="Current processing step")
    error_log: List[str] = Field(default_factory=list, description="List of error messages")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")


class BatchJobListResponse(BaseModel):
    """Response model for listing batch jobs."""
    success: bool = Field(..., description="Whether the request was successful")
    total_jobs: int = Field(..., description="Total number of batch jobs")
    jobs: List[Dict[str, Any]] = Field(..., description="List of batch jobs")
    pagination: Dict[str, Any] = Field(..., description="Pagination information")


class CancelBatchJobResponse(BaseModel):
    """Response model for cancelling a batch job."""
    success: bool = Field(..., description="Whether the job was cancelled successfully")
    batch_job_id: str = Field(..., description="ID of the cancelled batch job")
    message: str = Field(..., description="Status message")
    cancelled_at: datetime = Field(..., description="When the job was cancelled")


class BatchJobResults(BaseModel):
    """Response model for batch job results."""
    success: bool = Field(..., description="Whether the request was successful")
    batch_job_id: str = Field(..., description="ID of the batch job")
    total_urls: int = Field(..., description="Total number of URLs processed")
    successful_analyses: int = Field(..., description="Number of successful analyses")
    failed_analyses: int = Field(..., description="Number of failed analyses")
    success_rate: float = Field(..., description="Success rate percentage")
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    average_time_per_url: float = Field(..., description="Average time per URL in seconds")
    results: List[Dict[str, Any]] = Field(..., description="Analysis results for each URL")
    summary: Dict[str, Any] = Field(..., description="Summary statistics")


# Helper Functions
def _get_priority_enum(priority_str: str) -> JobPriority:
    """Convert priority string to JobPriority enum."""
    priority_map = {
        "low": JobPriority.LOW,
        "normal": JobPriority.NORMAL,
        "high": JobPriority.HIGH,
        "urgent": JobPriority.URGENT
    }
    
    if priority_str.lower() not in priority_map:
        raise HTTPException(status_code=400, detail=f"Invalid priority: {priority_str}. Must be one of: {list(priority_map.keys())}")
    
    return priority_map[priority_str.lower()]


def _validate_urls(urls: List[str]) -> List[str]:
    """Validate and clean URLs."""
    validated_urls = []
    for url in urls:
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Remove trailing slashes for consistency
        url = url.rstrip('/')
        validated_urls.append(url)
    
    return validated_urls


# API Endpoints
@router.post("/start", response_model=BatchJobResponse)
async def start_batch_analysis(
    request: BatchJobRequest,
    background_tasks: BackgroundTasks
) -> BatchJobResponse:
    """
    Start a new batch analysis job for multiple URLs.
    
    This endpoint creates a new batch job and starts processing URLs concurrently.
    Progress can be tracked using the returned batch_job_id.
    """
    try:
        # Validate and clean URLs
        validated_urls = _validate_urls(request.urls)
        
        # Validate business IDs if provided
        if request.business_ids and len(request.business_ids) != len(validated_urls):
            raise HTTPException(
                status_code=400, 
                detail="Number of business IDs must match number of URLs"
            )
        
        # Convert priority string to enum
        priority = _get_priority_enum(request.priority)
        
        # Create batch job configuration
        config = BatchJobConfig(
            name=request.name or f"batch_analysis_{int(datetime.now().timestamp())}",
            description=request.description or f"Batch analysis of {len(validated_urls)} URLs",
            batch_size=request.batch_size,
            priority=priority,
            timeout_seconds=request.timeout_seconds,
            enable_fallback=True,
            strategy=request.strategy
        )
        
        # Start batch analysis
        batch_job_id = await comprehensive_speed_service.start_batch_analysis(
            urls=validated_urls,
            business_ids=request.business_ids,
            run_id=request.run_id,
            batch_size=request.batch_size,
            priority=priority,
            timeout_seconds=request.timeout_seconds
        )
        
        # Calculate estimated duration
        estimated_duration = (request.timeout_seconds * len(validated_urls)) // request.batch_size
        
        logger.info(f"Started batch analysis job {batch_job_id} with {len(validated_urls)} URLs")
        
        return BatchJobResponse(
            success=True,
            batch_job_id=batch_job_id,
            message=f"Batch analysis job started successfully with {len(validated_urls)} URLs",
            estimated_duration=estimated_duration,
            total_urls=len(validated_urls),
            batch_size=request.batch_size,
            priority=request.priority,
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Failed to start batch analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start batch analysis: {str(e)}")


@router.get("/progress/{batch_job_id}", response_model=BatchJobProgress)
async def get_batch_progress(batch_job_id: str) -> BatchJobProgress:
    """
    Get real-time progress for a batch analysis job.
    
    This endpoint returns the current status and progress of a batch job,
    including completed URLs, failed URLs, and estimated completion time.
    """
    try:
        # Get progress from batch processor
        progress = await comprehensive_speed_service.get_batch_progress(batch_job_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail=f"Batch job {batch_job_id} not found")
        
        # Get additional details from database
        supabase = get_supabase_client()
        batch_job_result = supabase.table("batch_jobs").select("*").eq("id", batch_job_id).execute()
        
        if not batch_job_result.data:
            raise HTTPException(status_code=404, detail=f"Batch job {batch_job_id} not found in database")
        
        batch_job = batch_job_result.data[0]
        
        # Get URL processing status for current step
        url_status_result = supabase.table("url_processing_status").select("current_step").eq("batch_job_id", batch_job_id).eq("status", "processing").limit(1).execute()
        
        current_step = "processing"
        if url_status_result.data:
            current_step = url_status_result.data[0].get("current_step", "processing")
        
        return BatchJobProgress(
            batch_job_id=batch_job_id,
            name=batch_job.get("name", "Unknown"),
            status=progress.status,
            total_urls=progress.total_urls,
            completed_urls=progress.completed_urls,
            failed_urls=progress.failed_urls,
            progress_percentage=progress.progress_percentage,
            estimated_remaining_time=progress.performance_metrics.get("estimated_remaining_time"),
            started_at=progress.start_time,
            completed_at=progress.end_time,
            current_step=current_step,
            error_log=progress.error_log,
            performance_metrics=progress.performance_metrics
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get batch progress for {batch_job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get batch progress: {str(e)}")


@router.get("/jobs", response_model=BatchJobListResponse)
async def list_batch_jobs(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> BatchJobListResponse:
    """
    List all batch processing jobs with optional filtering and pagination.
    
    This endpoint returns a paginated list of batch jobs with their current status,
    progress, and metadata.
    """
    try:
        # Get jobs from batch processor
        jobs = await comprehensive_speed_service.get_all_batch_jobs(limit=limit + offset)
        
        # Apply filters
        if status:
            jobs = [job for job in jobs if job.get("status") == status]
        
        if priority:
            jobs = [job for job in jobs if job.get("priority") == priority]
        
        # Apply pagination
        total_jobs = len(jobs)
        paginated_jobs = jobs[offset:offset + limit]
        
        # Calculate pagination info
        pagination = {
            "limit": limit,
            "offset": offset,
            "total": total_jobs,
            "has_more": offset + limit < total_jobs,
            "next_offset": offset + limit if offset + limit < total_jobs else None
        }
        
        return BatchJobListResponse(
            success=True,
            total_jobs=total_jobs,
            jobs=paginated_jobs,
            pagination=pagination
        )
        
    except Exception as e:
        logger.error(f"Failed to list batch jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list batch jobs: {str(e)}")


@router.post("/cancel/{batch_job_id}", response_model=CancelBatchJobResponse)
async def cancel_batch_job(batch_job_id: str) -> CancelBatchJobResponse:
    """
    Cancel a running batch analysis job.
    
    This endpoint cancels a batch job if it's still running or queued.
    Completed jobs cannot be cancelled.
    """
    try:
        # Cancel the batch job
        success = await comprehensive_speed_service.cancel_batch_job(batch_job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Batch job {batch_job_id} not found or cannot be cancelled")
        
        logger.info(f"Cancelled batch job {batch_job_id}")
        
        return CancelBatchJobResponse(
            success=True,
            batch_job_id=batch_job_id,
            message="Batch job cancelled successfully",
            cancelled_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel batch job {batch_job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel batch job: {str(e)}")


@router.get("/results/{batch_job_id}", response_model=BatchJobResults)
async def get_batch_results(batch_job_id: str) -> BatchJobResults:
    """
    Get detailed results for a completed batch analysis job.
    
    This endpoint returns the complete analysis results for all URLs in a batch job,
    including scores, performance metrics, and error details.
    """
    try:
        # Get progress and results
        progress = await comprehensive_speed_service.get_batch_progress(batch_job_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail=f"Batch job {batch_job_id} not found")
        
        # Check if job is completed
        if progress.status not in ["completed", "completed_with_errors"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Batch job {batch_job_id} is not completed yet. Current status: {progress.status}"
            )
        
        # Calculate success rate
        total_urls = progress.total_urls
        successful_analyses = progress.completed_urls
        failed_analyses = progress.failed_urls
        success_rate = (successful_analyses / total_urls * 100) if total_urls > 0 else 0
        
        # Calculate timing metrics
        total_processing_time = 0
        if progress.start_time and progress.end_time:
            total_processing_time = (progress.end_time - progress.start_time).total_seconds()
        
        average_time_per_url = total_processing_time / total_urls if total_urls > 0 else 0
        
        # Prepare results summary
        summary = {
            "total_errors": progress.failed_urls,
            "services_completed": progress.completed_urls,
            "analysis_duration": int(total_processing_time * 1000),  # Convert to milliseconds
            "success_rate": round(success_rate, 2),
            "concurrency_level": progress.performance_metrics.get("concurrency_level", 5),
            "batch_size": progress.performance_metrics.get("batch_size", 5)
        }
        
        return BatchJobResults(
            success=True,
            batch_job_id=batch_job_id,
            total_urls=total_urls,
            successful_analyses=successful_analyses,
            failed_analyses=failed_analyses,
            success_rate=round(success_rate, 2),
            total_processing_time=round(total_processing_time, 2),
            average_time_per_url=round(average_time_per_url, 2),
            results=progress.results,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get batch results for {batch_job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get batch results: {str(e)}")


@router.get("/queue/status")
async def get_queue_status():
    """
    Get the current status of all job queues.
    
    This endpoint returns the status of high, normal, and low priority queues,
    including queue lengths, running jobs, and performance statistics.
    """
    try:
        # Get queue statuses from job queue manager
        queue_statuses = batch_processor.job_queue_manager.get_all_queue_statuses()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "queues": queue_statuses,
            "active_batches": len(batch_processor.active_batches),
            "total_queued_jobs": sum(
                queue["queue_length"] for queue in queue_statuses.values()
            ),
            "total_running_jobs": sum(
                queue["running_jobs"] for queue in queue_statuses.values()
            )
        }
        
    except Exception as e:
        logger.error(f"Failed to get queue status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")


@router.delete("/cleanup")
async def cleanup_completed_jobs(
    max_age_hours: int = 24
):
    """
    Clean up old completed batch jobs.
    
    This endpoint removes old completed jobs to free up database space.
    Only jobs older than the specified age will be cleaned up.
    """
    try:
        # Clean up old jobs from all queues
        await batch_processor.job_queue_manager.cleanup_all_queues(max_age_hours)
        
        logger.info(f"Cleaned up batch jobs older than {max_age_hours} hours")
        
        return {
            "success": True,
            "message": f"Cleaned up batch jobs older than {max_age_hours} hours",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup batch jobs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup batch jobs: {str(e)}")


@router.get("/health")
async def get_batch_processing_health():
    """
    Get the health status of the batch processing system.
    
    This endpoint returns the health status of all batch processing services,
    including the batch processor, job queues, and database connections.
    """
    try:
        # Get service health
        comprehensive_health = comprehensive_speed_service.get_service_health()
        
        # Get queue health
        queue_statuses = batch_processor.job_queue_manager.get_all_queue_statuses()
        
        # Check database connection
        supabase = get_supabase_client()
        try:
            supabase.table("batch_jobs").select("id").limit(1).execute()
            database_status = "healthy"
        except Exception:
            database_status = "unhealthy"
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "overall_status": comprehensive_health["status"],
            "services": {
                "comprehensive_speed": comprehensive_health["status"],
                "batch_processor": comprehensive_health["services"]["batch_processor"],
                "job_queues": "healthy" if all(q["stats"]["running_jobs"] >= 0 for q in queue_statuses.values()) else "degraded",
                "database": database_status
            },
            "queue_statuses": queue_statuses,
            "active_batches": len(batch_processor.active_batches),
            "features": comprehensive_health["features"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get batch processing health: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get health status: {str(e)}")
