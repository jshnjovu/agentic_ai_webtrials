"""
Batch Processing Service for concurrent website analysis.
Orchestrates multiple URL processing with real-time progress tracking.
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from dataclasses import dataclass

from src.core.supabase import get_supabase_client
from src.services.job_queue import JobQueueManager, JobPriority, JobQueueEntry
from src.services.unified import UnifiedAnalyzer
from src.services.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


@dataclass
class BatchJobConfig:
    """Configuration for batch processing jobs."""
    name: str
    description: Optional[str] = None
    batch_size: int = 5  # Concurrent processing limit
    priority: JobPriority = JobPriority.NORMAL
    max_retries: int = 3
    timeout_seconds: int = 300  # 5 minutes per URL
    enable_fallback: bool = True
    strategy: str = "mobile"  # PageSpeed strategy


@dataclass
class BatchJobResult:
    """Result of a batch processing job."""
    job_id: str
    batch_job_id: str
    total_urls: int
    completed_urls: int
    failed_urls: int
    progress_percentage: float
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    results: List[Dict[str, Any]] = None
    error_log: List[str] = None
    performance_metrics: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
        if self.error_log is None:
            self.error_log = []
        if self.performance_metrics is None:
            self.performance_metrics = {}


class BatchProcessor:
    """Main batch processing service for concurrent website analysis."""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.job_queue_manager = JobQueueManager()
        self.unified_analyzer = UnifiedAnalyzer()
        self.rate_limiter = RateLimiter()
        
        # Batch processing configuration
        self.default_config = BatchJobConfig(
            name="default_batch",
            batch_size=5,
            priority=JobPriority.NORMAL,
            max_retries=3,
            timeout_seconds=300
        )
        
        # Active batch jobs
        self.active_batches: Dict[str, Dict[str, Any]] = {}
        
        # Progress tracking callbacks
        self.progress_callbacks: List[Callable] = []
        
        logger.info("Initialized BatchProcessor")
    
    async def start_batch_analysis(
        self,
        urls: List[str],
        config: Optional[BatchJobConfig] = None,
        run_id: Optional[str] = None,
        business_ids: Optional[List[str]] = None
    ) -> str:
        """
        Start a new batch analysis job.
        
        Args:
            urls: List of URLs to analyze
            config: Batch processing configuration
            run_id: Optional processing run ID for tracking
            business_ids: Optional list of business IDs corresponding to URLs
            
        Returns:
            Batch job ID for tracking progress
        """
        try:
            # Use default config if none provided
            if config is None:
                config = self.default_config
            
            # Validate inputs
            if not urls:
                raise ValueError("URLs list cannot be empty")
            
            if business_ids and len(business_ids) != len(urls):
                raise ValueError("Business IDs list must match URLs list length")
            
            # Generate batch job ID
            batch_job_id = str(uuid.uuid4())
            
            # Create batch job record in database
            await self._create_batch_job_record(
                batch_job_id=batch_job_id,
                run_id=run_id,
                config=config,
                total_urls=len(urls)
            )
            
            # Create URL processing status records
            await self._create_url_status_records(
                batch_job_id=batch_job_id,
                urls=urls,
                business_ids=business_ids or [None] * len(urls)
            )
            
            # Add to job queue - CRITICAL FIX: Ensure this succeeds
            try:
                job_id = await self.job_queue_manager.add_job(
                    batch_job_id=batch_job_id,
                    priority=config.priority,
                    metadata={
                        "config": {
                            "batch_size": config.batch_size,
                            "max_retries": config.max_retries,
                            "timeout_seconds": config.timeout_seconds,
                            "enable_fallback": config.enable_fallback,
                            "strategy": config.strategy
                        },
                        "urls": urls,
                        "business_ids": business_ids
                    }
                )
                logger.info(f"Successfully added job {job_id} to queue with priority {config.priority.name}")
            except Exception as queue_error:
                logger.error(f"Failed to add job to queue: {queue_error}")
                # Update batch job status to failed
                await self._update_batch_job_status(batch_job_id, "failed", f"Queue error: {queue_error}")
                raise RuntimeError(f"Failed to queue batch job: {queue_error}")
            
            # Store active batch info
            self.active_batches[batch_job_id] = {
                "config": config,
                "urls": urls,
                "business_ids": business_ids,
                "job_id": job_id,
                "start_time": datetime.now(),
                "status": "queued"
            }
            
            logger.info(f"Started batch analysis job {batch_job_id} with {len(urls)} URLs")
            
            # CRITICAL FIX: Start processing in background and ensure it's properly awaited
            processing_task = asyncio.create_task(self._process_batch_job(batch_job_id))
            
            # Store the task reference for potential cancellation
            self.active_batches[batch_job_id]["processing_task"] = processing_task
            
            return batch_job_id
            
        except Exception as e:
            logger.error(f"Failed to start batch analysis: {e}")
            raise
    
    async def get_batch_progress(self, batch_job_id: str) -> Optional[BatchJobResult]:
        """Get real-time progress for a batch job."""
        try:
            # Get batch job from database
            result = self.supabase.table("batch_jobs").select("*").eq("id", batch_job_id).execute()
            
            if not result.data:
                return None
            
            batch_job = result.data[0]
            
            # Get URL processing status
            url_status_result = self.supabase.table("url_processing_status").select("*").eq("batch_job_id", batch_job_id).execute()
            
            # Calculate progress
            total_urls = batch_job["total_urls"]
            completed_urls = batch_job["completed_urls"]
            failed_urls = batch_job["failed_urls"]
            progress_percentage = batch_job["progress_percentage"]
            
            # Get results for completed URLs
            results = []
            for url_status in url_status_result.data:
                if url_status["status"] == "completed" and url_status["result_data"]:
                    results.append({
                        "url": url_status["url"],
                        "business_id": url_status["business_id"],
                        "result": url_status["result_data"],
                        "processing_duration": url_status["processing_duration"]
                    })
            
            # Get error log
            error_log = []
            for url_status in url_status_result.data:
                if url_status["status"] == "failed" and url_status["error_message"]:
                    error_log.append(f"URL {url_status['url']}: {url_status['error_message']}")
            
            return BatchJobResult(
                job_id=batch_job_id,
                batch_job_id=batch_job_id,
                total_urls=total_urls,
                completed_urls=completed_urls,
                failed_urls=failed_urls,
                progress_percentage=progress_percentage,
                status=batch_job["status"],
                start_time=datetime.fromisoformat(batch_job["created_at"]),
                end_time=datetime.fromisoformat(batch_job["completed_at"]) if batch_job["completed_at"] else None,
                results=results,
                error_log=error_log,
                performance_metrics=batch_job.get("performance_metrics", {})
            )
            
        except Exception as e:
            logger.error(f"Failed to get batch progress for {batch_job_id}: {e}")
            return None
    
    async def cancel_batch_job(self, batch_job_id: str) -> bool:
        """Cancel a running batch job."""
        try:
            if batch_job_id not in self.active_batches:
                logger.warning(f"Batch job {batch_job_id} not found in active batches")
                return False
            
            batch_info = self.active_batches[batch_job_id]
            
            # Cancel the job in the queue using batch job ID
            queue_cancelled = await self.job_queue_manager.cancel_job_by_batch_id(batch_job_id)
            if queue_cancelled:
                logger.info(f"Successfully cancelled job {batch_job_id} from queue")
            else:
                logger.warning(f"Job {batch_job_id} was not found in any queue")
            
            # Update database status
            self.supabase.table("batch_jobs").update({
                "status": "cancelled",
                "updated_at": datetime.now().isoformat()
            }).eq("id", batch_job_id).execute()
            
            # Update URL statuses to cancelled
            self.supabase.table("url_processing_status").update({
                "status": "cancelled",
                "updated_at": datetime.now().isoformat()
            }).eq("batch_job_id", batch_job_id).eq("status", "pending").execute()
            
            # Remove from active batches
            del self.active_batches[batch_job_id]
            
            logger.info(f"Cancelled batch job {batch_job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel batch job {batch_job_id}: {e}")
            return False
    
    async def get_all_batch_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all batch jobs with pagination."""
        try:
            result = self.supabase.table("batch_jobs").select("*").order("created_at", desc=True).limit(limit).execute()
            return result.data or []
        except Exception as e:
            logger.error(f"Failed to get batch jobs: {e}")
            return []
    
    def add_progress_callback(self, callback: Callable):
        """Add a callback for progress updates."""
        self.progress_callbacks.append(callback)
        logger.debug(f"Added progress callback: {callback}")
    
    async def _process_batch_job(self, batch_job_id: str):
        """Process a batch job with concurrent URL processing."""
        try:
            if batch_job_id not in self.active_batches:
                logger.error(f"Batch job {batch_job_id} not found in active batches")
                return
            
            batch_info = self.active_batches[batch_job_id]
            config = batch_info["config"]
            urls = batch_info["urls"]
            business_ids = batch_info["business_ids"]
            
            logger.info(f"Starting batch processing for {batch_job_id} with {len(urls)} URLs")
            
            # Update batch status to processing
            await self._update_batch_status(batch_job_id, "processing")
            batch_info["status"] = "processing"
            
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(config.batch_size)
            
            # Process URLs concurrently
            tasks = []
            for i, url in enumerate(urls):
                business_id = business_ids[i] if business_ids else None
                task = asyncio.create_task(
                    self._process_single_url(
                        batch_job_id=batch_job_id,
                        url=url,
                        business_id=business_id,
                        config=config,
                        semaphore=semaphore
                    )
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and update final status
            successful_results = [r for r in results if not isinstance(r, Exception)]
            failed_results = [r for r in results if isinstance(r, Exception)]
            
            # Update batch status
            final_status = "completed" if not failed_results else "completed_with_errors"
            await self._update_batch_status(batch_job_id, final_status)
            
            # Update performance metrics
            await self._update_performance_metrics(batch_job_id, {
                "total_processing_time": time.time() - batch_info["start_time"].timestamp(),
                "successful_urls": len(successful_results),
                "failed_urls": len(failed_results),
                "concurrency_level": config.batch_size
            })
            
            batch_info["status"] = final_status
            batch_info["end_time"] = datetime.now()
            
            logger.info(f"Completed batch job {batch_job_id}: {len(successful_results)} successful, {len(failed_results)} failed")
            
            # Notify progress callbacks
            await self._notify_progress_callbacks(batch_job_id, final_status)
            
        except Exception as e:
            logger.error(f"Batch processing failed for {batch_job_id}: {e}")
            await self._update_batch_status(batch_job_id, "failed")
            
            if batch_job_id in self.active_batches:
                self.active_batches[batch_job_id]["status"] = "failed"
    
    async def _process_single_url(
        self,
        batch_job_id: str,
        url: str,
        business_id: Optional[str],
        config: BatchJobConfig,
        semaphore: asyncio.Semaphore
    ) -> Dict[str, Any]:
        """Process a single URL with comprehensive analysis."""
        start_time = time.time()  # Track start time for duration calculation
        
        async with semaphore:
            try:
                # Update URL status to processing
                await self._update_url_status(
                    batch_job_id, 
                    url, 
                    "processing", 
                    "analysis"
                )
                
                # Create analysis task with timeout
                analysis_task = asyncio.create_task(
                    self.unified_analyzer.analyze_url(url, business_id)
                )
                
                try:
                    # Wait for analysis to complete with timeout
                    result = await asyncio.wait_for(analysis_task, timeout=config.timeout_seconds)
                    
                    # Calculate actual processing duration in milliseconds
                    processing_duration = int((time.time() - start_time) * 1000)
                    
                    # Update URL status to completed
                    await self._update_url_status(
                        batch_job_id, 
                        url, 
                        "completed", 
                        "analysis_complete",
                        result_data=result,
                        processing_duration=processing_duration
                    )
                    
                    logger.info(f"Completed analysis for {url} in batch {batch_job_id}")
                    return result
                    
                except asyncio.TimeoutError:
                    # Cancel the analysis task
                    analysis_task.cancel()
                    
                    # Update URL status to failed
                    await self._update_url_status(
                        batch_job_id, 
                        url, 
                        "failed", 
                        "timeout",
                        error_message=f"Analysis timed out after {config.timeout_seconds} seconds"
                    )
                    
                    logger.warning(f"Analysis timed out for {url} in batch {batch_job_id}")
                    raise TimeoutError(f"Analysis timed out for {url}")
                
            except Exception as e:
                # Update URL status to failed
                await self._update_url_status(
                    batch_job_id, 
                    url, 
                    "failed", 
                    "error",
                    error_message=str(e)
                )
                
                logger.error(f"Failed to process {url} in batch {batch_job_id}: {e}")
                raise
    
    async def _create_batch_job_record(
        self,
        batch_job_id: str,
        run_id: Optional[str],
        config: BatchJobConfig,
        total_urls: int
    ):
        """Create a new batch job record in the database."""
        try:
            self.supabase.table("batch_jobs").insert({
                "id": batch_job_id,
                "processing_run_id": run_id,
                "name": config.name,
                "description": config.description,
                "status": "pending",
                "total_urls": total_urls,
                "completed_urls": 0,
                "failed_urls": 0,
                "progress_percentage": 0,
                "batch_size": config.batch_size,
                "priority": config.priority.value,
                "estimated_duration": config.timeout_seconds * total_urls // config.batch_size
            }).execute()
            
        except Exception as e:
            logger.error(f"Failed to create batch job record: {e}")
            raise
    
    async def _create_url_status_records(
        self,
        batch_job_id: str,
        urls: List[str],
        business_ids: List[Optional[str]]
    ):
        """Create URL processing status records for all URLs in the batch."""
        try:
            url_status_records = []
            for url, business_id in zip(urls, business_ids):
                url_status_records.append({
                    "batch_job_id": batch_job_id,
                    "url": url,
                    "business_id": business_id,
                    "status": "pending",
                    "current_step": "analysis",
                    "retry_count": 0,
                    "max_retries": 3
                })
            
            self.supabase.table("url_processing_status").insert(url_status_records).execute()
            
        except Exception as e:
            logger.error(f"Failed to create URL status records: {e}")
            raise
    
    async def _update_batch_status(self, batch_job_id: str, status: str):
        """Update batch job status in the database."""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if status in ["completed", "completed_with_errors", "failed"]:
                update_data["completed_at"] = datetime.now().isoformat()
            elif status == "processing":
                update_data["started_at"] = datetime.now().isoformat()
            
            self.supabase.table("batch_jobs").update(update_data).eq("id", batch_job_id).execute()
            
        except Exception as e:
            logger.error(f"Failed to update batch status: {e}")
    
    async def _update_url_status(
        self,
        batch_job_id: str,
        url: str,
        status: str,
        current_step: str,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        processing_duration: Optional[int] = None
    ):
        """Update URL processing status in the database."""
        try:
            update_data = {
                "status": status,
                "current_step": current_step,
                "updated_at": datetime.now().isoformat()
            }
            
            if status == "processing":
                update_data["started_at"] = datetime.now().isoformat()
            elif status in ["completed", "failed"]:
                update_data["completed_at"] = datetime.now().isoformat()
                if processing_duration:
                    update_data["processing_duration"] = processing_duration
            
            if result_data:
                update_data["result_data"] = result_data
            
            if error_message:
                update_data["error_message"] = error_message
            
            self.supabase.table("url_processing_status").update(update_data).eq("batch_job_id", batch_job_id).eq("url", url).execute()
            
        except Exception as e:
            logger.error(f"Failed to update URL status: {e}")
    
    async def _update_performance_metrics(self, batch_job_id: str, metrics: Dict[str, Any]):
        """Update performance metrics for a batch job."""
        try:
            self.supabase.table("batch_jobs").update({
                "performance_metrics": metrics,
                "updated_at": datetime.now().isoformat()
            }).eq("id", batch_job_id).execute()
            
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
    
    async def _notify_progress_callbacks(self, batch_job_id: str, status: str):
        """Notify all progress callbacks about batch completion."""
        for callback in self.progress_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(batch_job_id, status)
                else:
                    callback(batch_job_id, status)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    async def _update_batch_job_status(self, batch_job_id: str, status: str, error_message: Optional[str] = None):
        """Update batch job status in database."""
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.now().isoformat()
            }
            
            if error_message:
                update_data["error_message"] = error_message
            
            if status in ["completed", "failed", "cancelled"]:
                update_data["completed_at"] = datetime.now().isoformat()
            
            self.supabase.table("batch_jobs").update(update_data).eq("id", batch_job_id).execute()
            logger.info(f"Updated batch job {batch_job_id} status to {status}")
            
        except Exception as e:
            logger.error(f"Failed to update batch job status for {batch_job_id}: {e}")

    async def shutdown(self):
        """Shutdown the batch processor gracefully."""
        logger.info("Shutting down BatchProcessor...")
        
        # Cancel all active batch jobs
        for batch_job_id in list(self.active_batches.keys()):
            await self.cancel_batch_job(batch_job_id)
        
        # Shutdown job queue manager
        await self.job_queue_manager.shutdown()
        
        logger.info("BatchProcessor shutdown complete")
