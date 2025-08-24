"""
Job Queue Management Service for Batch Processing.
Handles job prioritization, scheduling, and queue management.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import uuid

from src.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class JobPriority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class JobStatus(Enum):
    """Job status values."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class JobQueueEntry:
    """Represents a job in the queue."""
    id: str
    batch_job_id: str
    priority: JobPriority
    scheduled_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.QUEUED
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class JobQueue:
    """Manages job queues with priority-based scheduling."""
    
    def __init__(self, name: str, max_concurrent: int = 5, max_queue_size: int = 100):
        self.name = name
        self.max_concurrent = max_concurrent
        self.max_queue_size = max_queue_size
        self.supabase = get_supabase_client()
        
        # In-memory queue for fast access
        self._queue: List[JobQueueEntry] = []
        self._running_jobs: Dict[str, JobQueueEntry] = {}
        self._completed_jobs: Dict[str, JobQueueEntry] = {}
        
        # Queue statistics
        self.stats = {
            "total_jobs_processed": 0,
            "total_jobs_failed": 0,
            "average_processing_time": 0.0,
            "queue_length": 0,
            "running_jobs": 0
        }
        
        # Event callbacks
        self._callbacks = {
            "job_started": [],
            "job_completed": [],
            "job_failed": [],
            "queue_updated": []
        }
        
        logger.info(f"Initialized JobQueue '{name}' with max_concurrent={max_concurrent}")
    
    async def add_job(
        self, 
        batch_job_id: str, 
        priority: JobPriority = JobPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a job to the queue."""
        try:
            # Check queue size limit
            if len(self._queue) >= self.max_queue_size:
                raise ValueError(f"Queue '{self.name}' is full (max: {self.max_queue_size})")
            
            # Create job entry
            job_id = str(uuid.uuid4())
            job_entry = JobQueueEntry(
                id=job_id,
                batch_job_id=batch_job_id,
                priority=priority,
                scheduled_at=datetime.now(),
                metadata=metadata or {}
            )
            
            # CRITICAL FIX: Add to database first, then memory
            try:
                self._add_job_to_database(job_entry)
                logger.info(f"Successfully added job {job_id} to database for queue '{self.name}'")
            except Exception as db_error:
                logger.error(f"Failed to add job {job_id} to database: {db_error}")
                raise RuntimeError(f"Database operation failed: {db_error}")
            
            # Add to in-memory queue
            self._queue.append(job_entry)
            self._sort_queue()  # Maintain priority order
            
            # Update stats
            self.stats["queue_length"] = len(self._queue)
            
            # Notify callbacks
            await self._notify_callbacks("queue_updated", job_entry)
            
            logger.info(f"Added job {job_id} to queue '{self.name}' with priority {priority.name}")
            return job_id
            
        except Exception as e:
            logger.error(f"Failed to add job to queue '{self.name}': {e}")
            raise
    
    async def get_next_job(self) -> Optional[JobQueueEntry]:
        """Get the next job from the queue based on priority."""
        if not self._queue:
            return None
        
        if len(self._running_jobs) >= self.max_concurrent:
            return None
        
        # Get highest priority job
        job_entry = self._queue.pop(0)
        job_entry.status = JobStatus.RUNNING
        job_entry.started_at = datetime.now()
        
        # Move to running jobs
        self._running_jobs[job_entry.id] = job_entry
        
        # Update database
        self._update_job_status(job_entry)
        
        # Update stats
        self.stats["running_jobs"] = len(self._running_jobs)
        self.stats["queue_length"] = len(self._queue)
        
        # Notify callbacks
        await self._notify_callbacks("job_started", job_entry)
        
        logger.info(f"Started job {job_entry.id} from queue '{self.name}'")
        return job_entry
    
    async def complete_job(self, job_id: str, success: bool = True, result: Optional[Dict[str, Any]] = None):
        """Mark a job as completed."""
        if job_id not in self._running_jobs:
            logger.warning(f"Job {job_id} not found in running jobs")
            return
        
        job_entry = self._running_jobs.pop(job_id)
        job_entry.completed_at = datetime.now()
        job_entry.status = JobStatus.COMPLETED if success else JobStatus.FAILED
        
        # Calculate processing time
        if job_entry.started_at:
            processing_time = (job_entry.completed_at - job_entry.started_at).total_seconds()
            job_entry.metadata["processing_time"] = processing_time
            
            # Update average processing time
            self.stats["total_jobs_processed"] += 1
            if self.stats["total_jobs_processed"] == 1:
                self.stats["average_processing_time"] = processing_time
            else:
                self.stats["average_processing_time"] = (
                    (self.stats["average_processing_time"] * (self.stats["total_jobs_processed"] - 1) + processing_time) /
                    self.stats["total_jobs_processed"]
                )
        
        if not success:
            self.stats["total_jobs_failed"] += 1
        
        # Move to completed jobs
        self._completed_jobs[job_id] = job_entry
        
        # Update database
        self._update_job_status(job_entry)
        
        # Update stats
        self.stats["running_jobs"] = len(self._running_jobs)
        
        # Notify callbacks
        callback_type = "job_completed" if success else "job_failed"
        await self._notify_callbacks(callback_type, job_entry)
        
        logger.info(f"Completed job {job_id} with status: {job_entry.status.name}")
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job if it's still in the queue."""
        # Check if job is in queue
        for i, job in enumerate(self._queue):
            if job.id == job_id:
                job_entry = self._queue.pop(i)
                job_entry.status = JobStatus.CANCELLED
                
                # Update database
                self._update_job_status(job_entry)
                
                # Update stats
                self.stats["queue_length"] = len(self._queue)
                
                logger.info(f"Cancelled job {job_id} from queue '{self.name}'")
                return True
        
        # Check if job is running
        if job_id in self._running_jobs:
            job_entry = self._running_jobs[job_id]
            job_entry.status = JobStatus.CANCELLED
            
            # Update database
            self._update_job_status(job_entry)
            
            logger.info(f"Cancelled running job {job_id} from queue '{self.name}'")
            return True
        
        logger.warning(f"Job {job_id} not found in queue '{self.name}'")
        return False
    
    async def cancel_job_by_batch_id(self, batch_job_id: str) -> bool:
        """Cancel a job by its batch job ID."""
        # Check if job is in queue
        for i, job in enumerate(self._queue):
            if job.batch_job_id == batch_job_id:
                job_entry = self._queue.pop(i)
                job_entry.status = JobStatus.CANCELLED
                
                # Update database
                self._update_job_status(job_entry)
                
                # Update stats
                self.stats["queue_length"] = len(self._queue)
                
                logger.info(f"Cancelled job {job_entry.id} (batch: {batch_job_id}) from queue '{self.name}'")
                return True
        
        # Check if job is running
        for job_id, job_entry in list(self._running_jobs.items()):
            if job_entry.batch_job_id == batch_job_id:
                job_entry.status = JobStatus.CANCELLED
                
                # Update database
                self._update_job_status(job_entry)
                
                # Remove from running jobs
                del self._running_jobs[job_id]
                
                logger.info(f"Cancelled running job {job_id} (batch: {batch_job_id}) from queue '{self.name}'")
                return True
        
        logger.warning(f"Job with batch ID {batch_job_id} not found in queue '{self.name}'")
        return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        # Update stats to reflect current state
        self.stats["queue_length"] = len(self._queue)
        self.stats["running_jobs"] = len(self._running_jobs)
        
        # Debug information
        debug_info = {
            "queue_name": self.name,
            "queue_length": len(self._queue),
            "running_jobs": len(self._running_jobs),
            "completed_jobs": len(self._completed_jobs),
            "max_concurrent": self.max_concurrent,
            "max_queue_size": self.max_queue_size,
            "stats": self.stats.copy(),
            "next_jobs": [
                {
                    "id": job.id,
                    "batch_job_id": job.batch_job_id,
                    "priority": job.priority.name,
                    "scheduled_at": job.scheduled_at.isoformat(),
                    "metadata": job.metadata
                }
                for job in self._queue[:5]  # Show next 5 jobs
            ],
            "debug": {
                "queue_ids": [job.id for job in self._queue],
                "running_ids": list(self._running_jobs.keys()),
                "queue_batch_ids": [job.batch_job_id for job in self._queue],
                "running_batch_ids": [job.batch_job_id for job in self._running_jobs.values()]
            }
        }
        
        logger.debug(f"Queue '{self.name}' status: {debug_info['queue_length']} queued, {debug_info['running_jobs']} running")
        return debug_info
    
    def _reset_queue(self):
        """Reset queue to clean state."""
        self._queue.clear()
        self._running_jobs.clear()
        self._completed_jobs.clear()
        self.stats = {
            "queue_length": 0,
            "running_jobs": 0,
            "completed_jobs": 0,
            "total_processed": 0,
            "total_failed": 0
        }
        logger.info(f"Reset queue '{self.name}' to clean state")
    
    def add_callback(self, event: str, callback: Callable):
        """Add a callback for queue events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
            logger.debug(f"Added callback for event '{event}'")
        else:
            logger.warning(f"Unknown event type: {event}")
    
    def _add_job_to_database(self, job_entry: JobQueueEntry):
        """Add a job entry to the database."""
        try:
            queue_id = self._get_queue_id()
            
            # Insert job queue entry
            result = self.supabase.table("job_queue_entries").insert({
                "id": job_entry.id,
                "queue_id": queue_id,
                "batch_job_id": job_entry.batch_job_id,
                "priority": job_entry.priority.value,
                "scheduled_at": job_entry.scheduled_at.isoformat(),
                "status": job_entry.status.value,
                "metadata": job_entry.metadata or {}
            }).execute()
            
            if not result.data:
                raise RuntimeError("No data returned from database insert")
            
            logger.info(f"Job {job_entry.id} successfully inserted into database queue {queue_id}")
            
        except Exception as e:
            logger.error(f"Failed to add job {job_entry.id} to database: {e}")
            raise RuntimeError(f"Database insert failed: {e}")

    def _update_job_status(self, job_entry: JobQueueEntry):
        """Update job status in the database."""
        try:
            update_data = {
                "status": job_entry.status.value,
                "updated_at": datetime.now().isoformat()
            }
            
            if job_entry.started_at:
                update_data["started_at"] = job_entry.started_at.isoformat()
            
            if job_entry.completed_at:
                update_data["completed_at"] = job_entry.completed_at.isoformat()
            
            result = self.supabase.table("job_queue_entries").update(update_data).eq("id", job_entry.id).execute()
            
            if not result.data:
                logger.warning(f"No rows updated for job {job_entry.id} status update")
            else:
                logger.info(f"Successfully updated job {job_entry.id} status to {job_entry.status.value}")
                
        except Exception as e:
            logger.error(f"Failed to update job status in database: {e}")
            # Don't raise here as this is not critical for job execution
    
    def _get_queue_id(self) -> str:
        """Get the database queue ID for this queue."""
        try:
            result = self.supabase.table("batch_job_queues").select("id").eq("name", self.name).execute()
            if result.data:
                return result.data[0]["id"]
            else:
                # Create queue if it doesn't exist
                result = self.supabase.table("batch_job_queues").insert({
                    "name": self.name,
                    "description": f"Auto-created queue: {self.name}",
                    "max_concurrent_jobs": self.max_concurrent,
                    "max_queue_size": self.max_queue_size
                }).execute()
                return result.data[0]["id"]
        except Exception as e:
            logger.error(f"Failed to get queue ID: {e}")
            raise
    
    def _sort_queue(self):
        """Sort queue by priority (highest first) and then by scheduled time (earliest first)."""
        self._queue.sort(
            key=lambda x: (-x.priority.value, x.scheduled_at),
            reverse=False
        )
    
    async def _notify_callbacks(self, event: str, job_entry: JobQueueEntry):
        """Notify all callbacks for an event."""
        for callback in self._callbacks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(job_entry)
                else:
                    callback(job_entry)
            except Exception as e:
                logger.error(f"Callback error for event '{event}': {e}")
    
    async def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs from memory."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        old_jobs = [
            job_id for job_id, job in self._completed_jobs.items()
            if job.completed_at and job.completed_at < cutoff_time
        ]
        
        for job_id in old_jobs:
            del self._completed_jobs[job_id]
        
        if old_jobs:
            logger.info(f"Cleaned up {len(old_jobs)} old completed jobs from queue '{self.name}'")


class JobQueueManager:
    """Manages multiple job queues with different priorities."""
    
    def __init__(self):
        self.queues: Dict[str, JobQueue] = {}
        self.supabase = get_supabase_client()
        
        # Initialize default queues
        self._initialize_default_queues()
        
        logger.info("Initialized JobQueueManager")
    
    def _initialize_default_queues(self):
        """Initialize default priority queues."""
        self.queues["high_priority"] = JobQueue("high_priority", max_concurrent=2, max_queue_size=50)
        self.queues["normal"] = JobQueue("normal", max_concurrent=5, max_queue_size=100)
        self.queues["low_priority"] = JobQueue("low_priority", max_concurrent=3, max_queue_size=200)
        
        logger.info("Initialized default priority queues")
    
    async def add_job(
        self, 
        batch_job_id: str, 
        priority: JobPriority = JobPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add a job to the appropriate queue based on priority."""
        # Map priority to queue name
        if priority == JobPriority.URGENT or priority == JobPriority.HIGH:
            queue_name = "high_priority"
        elif priority == JobPriority.LOW:
            queue_name = "low_priority"
        else:
            queue_name = "normal"
        
        logger.info(f"Adding job {batch_job_id} to {queue_name} queue with priority {priority.name}")
        
        # Add to the appropriate queue
        job_id = await self.queues[queue_name].add_job(batch_job_id, priority, metadata)
        
        # Verify job was added to the correct queue
        queue = self.queues[queue_name]
        job_found = any(job.batch_job_id == batch_job_id for job in queue._queue)
        if not job_found:
            logger.warning(f"Job {batch_job_id} was not found in {queue_name} queue after addition")
        
        logger.info(f"Successfully added job {job_id} to {queue_name} queue with priority {priority.name}")
        return job_id
    
    async def get_next_job(self, queue_name: Optional[str] = None) -> Optional[JobQueueEntry]:
        """Get the next job from a specific queue or any available queue."""
        if queue_name:
            if queue_name in self.queues:
                return await self.queues[queue_name].get_next_job()
            else:
                logger.warning(f"Queue '{queue_name}' not found")
                return None
        
        # Try high priority first, then normal, then low priority
        for priority_queue in ["high_priority", "normal", "low_priority"]:
            job = await self.queues[priority_queue].get_next_job()
            if job:
                return job
        
        return None
    
    def get_all_queue_statuses(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all queues."""
        return self.get_queue_status_with_jobs()
    
    def _reset_all_queues(self):
        """Reset all queues to clean state."""
        for queue in self.queues.values():
            queue._reset_queue()
    
    async def cleanup_all_queues(self, max_age_hours: int = 24):
        """Clean up old jobs from all queues."""
        for queue in self.queues.values():
            await queue.cleanup_old_jobs(max_age_hours)
    
    def get_queue(self, name: str) -> Optional[JobQueue]:
        """Get a specific queue by name."""
        return self.queues.get(name)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job by its ID across all queues."""
        for queue_name, queue in self.queues.items():
            if await queue.cancel_job(job_id):
                logger.info(f"Cancelled job {job_id} from queue '{queue_name}'")
                return True
        return False
    
    async def cancel_job_by_batch_id(self, batch_job_id: str) -> bool:
        """Cancel a job by its batch job ID across all queues."""
        for queue_name, queue in self.queues.items():
            if await queue.cancel_job_by_batch_id(batch_job_id):
                logger.info(f"Cancelled batch job {batch_job_id} from queue '{queue_name}'")
                return True
        return False
    
    def find_job_in_queues(self, batch_job_id: str) -> Optional[tuple[str, JobQueueEntry]]:
        """Find a job by batch job ID across all queues."""
        for queue_name, queue in self.queues.items():
            # Check if job is in queue
            for job in queue._queue:
                if job.batch_job_id == batch_job_id:
                    return queue_name, job
            
            # Check if job is running
            for job_id, job in queue._running_jobs.items():
                if job.batch_job_id == batch_job_id:
                    return queue_name, job
        
        return None
    
    def get_queue_status_with_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed status of all queues including job information."""
        statuses = {}
        for name, queue in self.queues.items():
            queue_status = queue.get_queue_status()
            
            # Add job details for better tracking (rename to avoid conflict with count fields)
            queue_status["queued_job_details"] = [
                {
                    "id": job.id,
                    "batch_job_id": job.batch_job_id,
                    "priority": job.priority.name,
                    "scheduled_at": job.scheduled_at.isoformat()
                }
                for job in queue._queue
            ]
            
            queue_status["running_job_details"] = [
                {
                    "id": job.id,
                    "batch_job_id": job.batch_job_id,
                    "priority": job.priority.name,
                    "started_at": job.started_at.isoformat() if job.started_at else None
                }
                for job in queue._running_jobs.values()
            ]
            
            statuses[name] = queue_status
        
        return statuses
    
    async def shutdown(self):
        """Shutdown all queues gracefully."""
        logger.info("Shutting down JobQueueManager...")
        
        # Wait for running jobs to complete (with timeout)
        max_wait_time = 30  # seconds
        start_time = time.time()
        
        while any(len(queue._running_jobs) > 0 for queue in self.queues.values()):
            if time.time() - start_time > max_wait_time:
                logger.warning("Force shutdown after timeout")
                break
            
            await asyncio.sleep(1)
        
        logger.info("JobQueueManager shutdown complete")
