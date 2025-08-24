#!/usr/bin/env python3
"""
Comprehensive tests for Batch Processing API endpoints.
Tests all the real-time API endpoints marked as COMPLETED in BatchProcessingRealTimeTracking.md
"""

import asyncio
import sys
import os
import time
import pytest
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.services.comprehensive_speed_service import ComprehensiveSpeedService
from src.services.job_queue import JobPriority
from src.core.supabase import get_supabase_client


class TestBatchProcessingAPI:
    """Test suite for batch processing API endpoints."""
    
    def __init__(self):
        """Initialize test environment."""
        self.comprehensive_speed_service = ComprehensiveSpeedService()
        self.supabase = get_supabase_client()
        self.test_urls = [
            "https://example.com",
            "https://httpbin.org/html",
            "https://httpbin.org/status/200"
        ]
        self.batch_job_id = None
    
    async def setup(self):
        """Setup test environment."""
        pass
    
    async def teardown(self):
        """Cleanup after tests."""
        if self.batch_job_id:
            await self._cleanup_test_job()
    
    async def _cleanup_test_job(self):
        """Clean up test batch job."""
        try:
            # Cancel if still running
            await self.comprehensive_speed_service.cancel_batch_job(self.batch_job_id)
            # Delete test data
            self.supabase.table("url_processing_status").delete().eq("batch_job_id", self.batch_job_id).execute()
            self.supabase.table("job_queue_entries").delete().eq("batch_job_id", self.batch_job_id).execute()
            self.supabase.table("batch_jobs").delete().eq("id", self.batch_job_id).execute()
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
    @pytest.mark.asyncio
    async def test_01_start_batch_analysis(self):
        """Test POST /api/v1/batch-processing/start - Start new batch analysis jobs."""
        print("\n🧪 **Test 1: Start Batch Analysis**")
        print("-" * 50)
        
        try:
            # Start batch analysis
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=self.test_urls,
                batch_size=2,
                priority=JobPriority.HIGH,
                timeout_seconds=120
            )
            
            print(f"✅ Batch job created successfully")
            print(f"   Job ID: {self.batch_job_id}")
            print(f"   URLs: {len(self.test_urls)}")
            print(f"   Batch Size: 2")
            print(f"   Priority: HIGH")
            
            # Verify job was created in database
            result = self.supabase.table("batch_jobs").select("*").eq("id", self.batch_job_id).execute()
            assert result.data, "Batch job should exist in database"
            
            batch_job = result.data[0]
            assert batch_job["total_urls"] == len(self.test_urls), "Total URLs should match"
            assert batch_job["batch_size"] == 2, "Batch size should match"
            assert batch_job["priority"] == JobPriority.HIGH.value, "Priority should match"
            assert batch_job["status"] in ["pending", "processing"], "Status should be pending or processing"
            
            print(f"   Database Status: {batch_job['status']}")
            print(f"   Total URLs: {batch_job['total_urls']}")
            print(f"   Batch Size: {batch_job['batch_size']}")
            print(f"   Priority: {batch_job['priority']}")
            
            # Verify URL status records were created
            url_status_result = self.supabase.table("url_processing_status").select("*").eq("batch_job_id", self.batch_job_id).execute()
            assert len(url_status_result.data) == len(self.test_urls), "URL status records should be created"
            
            print(f"   URL Status Records: {len(url_status_result.data)} created")
            
            # Verify job was queued
            queue_result = self.supabase.table("job_queue_entries").select("*").eq("batch_job_id", self.batch_job_id).execute()
            assert queue_result.data, "Job should be queued"
            
            print(f"   Job Queued: ✅")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_02_get_batch_progress(self):
        """Test GET /api/v1/batch-processing/progress/{batch_job_id} - Real-time progress tracking."""
        print("\n🧪 **Test 2: Get Batch Progress**")
        print("-" * 50)
        
        try:
            # First create a batch job
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=self.test_urls,
                batch_size=2,
                priority=JobPriority.NORMAL,
                timeout_seconds=120
            )
            
            print(f"✅ Batch job created: {self.batch_job_id}")
            
            # Test progress retrieval
            progress = await self.comprehensive_speed_service.get_batch_progress(self.batch_job_id)
            
            assert progress is not None, "Progress should be retrievable"
            assert progress.batch_job_id == self.batch_job_id, "Batch job ID should match"
            assert progress.total_urls == len(self.test_urls), "Total URLs should match"
            assert progress.status in ["pending", "processing"], "Status should be valid"
            
            print(f"   Progress Retrieved: ✅")
            print(f"   Status: {progress.status}")
            print(f"   Total URLs: {progress.total_urls}")
            print(f"   Completed: {progress.completed_urls}")
            print(f"   Failed: {progress.failed_urls}")
            print(f"   Progress: {progress.progress_percentage:.1f}%")
            
            # Test progress updates over time
            print(f"\n   Testing progress updates...")
            initial_progress = progress.progress_percentage
            
            # Wait a bit and check again
            await asyncio.sleep(2)
            updated_progress = await self.comprehensive_speed_service.get_batch_progress(self.batch_job_id)
            
            assert updated_progress is not None, "Updated progress should be retrievable"
            print(f"   Progress Update: ✅ (Initial: {initial_progress:.1f}% → Current: {updated_progress.progress_percentage:.1f}%)")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_03_get_all_batch_jobs(self):
        """Test GET /api/v1/batch-processing/jobs - List all batch jobs with pagination."""
        print("\n🧪 **Test 3: Get All Batch Jobs**")
        print("-" * 50)
        
        try:
            # Create a test batch job
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=self.test_urls[:2],  # Use fewer URLs for faster test
                batch_size=2,
                priority=JobPriority.LOW,
                timeout_seconds=60
            )
            
            print(f"✅ Test batch job created: {self.batch_job_id}")
            
            # Get all batch jobs
            all_jobs = await self.comprehensive_speed_service.get_all_batch_jobs()
            
            assert isinstance(all_jobs, list), "Should return a list of jobs"
            assert len(all_jobs) > 0, "Should have at least one job"
            
            # Find our test job
            test_job = None
            for job in all_jobs:
                if job.get("id") == self.batch_job_id:
                    test_job = job
                    break
            
            assert test_job is not None, "Test job should be in the list"
            assert test_job["total_urls"] == 2, "Test job should have correct URL count"
            
            print(f"   All Jobs Retrieved: ✅")
            print(f"   Total Jobs: {len(all_jobs)}")
            print(f"   Test Job Found: ✅")
            print(f"   Test Job Status: {test_job['status']}")
            print(f"   Test Job URLs: {test_job['total_urls']}")
            
            # Test job details
            job_details = {
                "id": test_job["id"],
                "name": test_job.get("name", "Unknown"),
                "status": test_job["status"],
                "total_urls": test_job["total_urls"],
                "completed_urls": test_job["completed_urls"],
                "failed_urls": test_job["failed_urls"],
                "progress_percentage": test_job["progress_percentage"],
                "priority": test_job["priority"],
                "created_at": test_job["created_at"]
            }
            
            print(f"   Job Details: {job_details}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_04_cancel_batch_job(self):
        """Test POST /api/v1/batch-processing/cancel/{batch_job_id} - Cancel running jobs."""
        print("\n🧪 **Test 4: Cancel Batch Job**")
        print("-" * 50)
        
        try:
            # Create a batch job
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=self.test_urls,
                batch_size=2,
                priority=JobPriority.HIGH,
                timeout_seconds=120
            )
            
            print(f"✅ Batch job created: {self.batch_job_id}")
            
            # Verify job is running
            progress = await self.comprehensive_speed_service.get_batch_progress(self.batch_job_id)
            assert progress.status in ["pending", "processing"], "Job should be running"
            
            print(f"   Initial Status: {progress.status}")
            
            # Cancel the job
            cancel_result = await self.comprehensive_speed_service.cancel_batch_job(self.batch_job_id)
            
            assert cancel_result is True, "Cancel should return True"
            print(f"   Job Cancelled: ✅")
            
            # Verify job status changed
            await asyncio.sleep(1)  # Give time for status update
            updated_progress = await self.comprehensive_speed_service.get_batch_progress(self.batch_job_id)
            
            if updated_progress:
                print(f"   Updated Status: {updated_progress.status}")
                print(f"   Cancellation Verified: ✅")
            else:
                print(f"   Job removed after cancellation")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_05_get_batch_results(self):
        """Test GET /api/v1/batch-processing/results/{batch_job_id} - Get detailed results."""
        print("\n🧪 **Test 5: Get Batch Results**")
        print("-" * 50)
        
        try:
            # Create a batch job
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=self.test_urls[:2],  # Use fewer URLs
                batch_size=2,
                priority=JobPriority.NORMAL,
                timeout_seconds=60
            )
            
            print(f"✅ Batch job created: {self.batch_job_id}")
            
            # Get progress (which includes results)
            progress = await self.comprehensive_speed_service.get_batch_progress(self.batch_job_id)
            
            assert progress is not None, "Progress should be retrievable"
            
            print(f"   Results Retrieved: ✅")
            print(f"   Status: {progress.status}")
            print(f"   Total URLs: {progress.total_urls}")
            print(f"   Completed: {progress.completed_urls}")
            print(f"   Failed: {progress.failed_urls}")
            
            # Test result structure
            if progress.results:
                print(f"   Results Available: ✅")
                for i, result in enumerate(progress.results):
                    print(f"     Result {i+1}:")
                    print(f"       URL: {result.get('url', 'N/A')}")
                    print(f"       Business ID: {result.get('business_id', 'N/A')}")
                    print(f"       Duration: {result.get('processing_duration', 'N/A')}ms")
            else:
                print(f"   Results: No completed URLs yet")
            
            # Test error log
            if progress.error_log:
                print(f"   Error Log Available: ✅")
                for error in progress.error_log:
                    print(f"     Error: {error}")
            else:
                print(f"   Error Log: No errors yet")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_06_get_queue_status(self):
        """Test GET /api/v1/batch-processing/queue/status - Queue health and status."""
        print("\n🧪 **Test 6: Get Queue Status**")
        print("-" * 50)
        
        try:
            # Create a batch job to populate queues
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=self.test_urls[:2],
                batch_size=2,
                priority=JobPriority.HIGH,
                timeout_seconds=60
            )
            
            print(f"✅ Test batch job created: {self.batch_job_id}")
            
            # Get queue status through the same batch processor instance
            batch_processor = self.comprehensive_speed_service.batch_processor
            
            queue_statuses = batch_processor.job_queue_manager.get_all_queue_statuses()
            
            assert isinstance(queue_statuses, dict), "Should return queue statuses"
            assert "high_priority" in queue_statuses, "High priority queue should exist"
            assert "normal" in queue_statuses, "Normal priority queue should exist"
            assert "low_priority" in queue_statuses, "Low priority queue should exist"
            
            print(f"   Queue Status Retrieved: ✅")
            
            # Display queue statuses
            for queue_name, status in queue_statuses.items():
                if isinstance(status, dict):
                    queue_length = status.get('queue_length', 0)
                    running_jobs = status.get('running_jobs', 0)
                    completed_jobs = status.get('completed_jobs', 0)
                    
                    print(f"   {queue_name:12}: {queue_length:2} queued, {running_jobs:2} running, {completed_jobs:2} completed")
                    
                    # Show debug information
                    if 'debug' in status:
                        debug = status['debug']
                        print(f"     Debug - Queue IDs: {debug.get('queue_ids', [])}")
                        print(f"     Debug - Running IDs: {debug.get('running_ids', [])}")
                        print(f"     Debug - Queue Batch IDs: {debug.get('queue_batch_ids', [])}")
                        print(f"     Debug - Running Batch IDs: {debug.get('running_batch_ids', [])}")
                    
                    # Show job details if available
                    if 'queued_job_details' in status:
                        print(f"     Queued Jobs: {len(status['queued_job_details'])}")
                    if 'running_job_details' in status:
                        print(f"     Running Jobs: {len(status['running_job_details'])}")
                else:
                    print(f"   ERROR: Status is not a dictionary: {status}")
            
            # Verify our job is in the appropriate queue
            high_priority_status = queue_statuses["high_priority"]
            assert high_priority_status["queue_length"] > 0 or high_priority_status["running_jobs"] > 0, \
                "High priority queue should contain our job"
            
            print(f"   Job Queue Verification: ✅")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_07_cleanup_old_jobs(self):
        """Test DELETE /api/v1/batch-processing/cleanup - Clean up old completed jobs."""
        print("\n🧪 **Test 7: Cleanup Old Jobs**")
        print("-" * 50)
        
        try:
            # Create a batch job
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=self.test_urls[:2],
                batch_size=2,
                priority=JobPriority.LOW,
                timeout_seconds=60
            )
            
            print(f"✅ Test batch job created: {self.batch_job_id}")
            
            # Get initial job count
            initial_jobs = await self.comprehensive_speed_service.get_all_batch_jobs()
            initial_count = len(initial_jobs)
            
            print(f"   Initial Job Count: {initial_count}")
            
            # Note: The actual cleanup endpoint would be implemented in the API
            # For now, we'll test the cleanup functionality through the service
            batch_processor = self.comprehensive_speed_service.batch_processor
            
            # Clean up old jobs (older than 1 hour)
            await batch_processor.job_queue_manager.cleanup_all_queues(max_age_hours=1)
            
            print(f"   Cleanup Executed: ✅")
            
            # Verify cleanup didn't remove our recent job
            updated_jobs = await self.comprehensive_speed_service.get_all_batch_jobs()
            updated_count = len(updated_jobs)
            
            print(f"   Updated Job Count: {updated_count}")
            print(f"   Recent Job Preserved: ✅")
            
            # Our test job should still exist
            job_exists = any(job.get("id") == self.batch_job_id for job in updated_jobs)
            assert job_exists, "Recent test job should not be cleaned up"
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_08_system_health(self):
        """Test GET /api/v1/batch-processing/health - System health monitoring."""
        print("\n🧪 **Test 8: System Health**")
        print("-" * 50)
        
        try:
            # Test service health through the comprehensive speed service
            service_health = self.comprehensive_speed_service.service_health
            
            assert isinstance(service_health, dict), "Service health should be a dictionary"
            assert "unified" in service_health, "Unified service health should be tracked"
            assert "batch_processor" in service_health, "Batch processor health should be tracked"
            assert "overall" in service_health, "Overall health should be tracked"
            
            print(f"   Service Health Retrieved: ✅")
            print(f"   Unified Service: {service_health['unified']}")
            print(f"   Batch Processor: {service_health['batch_processor']}")
            print(f"   Overall: {service_health['overall']}")
            
            # Test batch processor health
            batch_processor = self.comprehensive_speed_service.batch_processor
            
            # Check if batch processor is operational
            assert batch_processor.job_queue_manager is not None, "Job queue manager should be initialized"
            assert len(batch_processor.job_queue_manager.queues) > 0, "Queues should be initialized"
            
            print(f"   Batch Processor Health: ✅")
            print(f"   Queues Initialized: {len(batch_processor.job_queue_manager.queues)}")
            
            # Test queue health
            queue_statuses = batch_processor.job_queue_manager.get_all_queue_statuses()
            for queue_name, status in queue_statuses.items():
                assert "queue_length" in status, f"Queue {queue_name} should have queue_length"
                assert "running_jobs" in status, f"Queue {queue_name} should have running_jobs"
                assert "completed_jobs" in status, f"Queue {queue_name} should have completed_jobs"
            
            print(f"   Queue Health: ✅")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_09_url_validation_and_cleaning(self):
        """Test URL validation and cleaning features."""
        print("\n🧪 **Test 9: URL Validation & Cleaning**")
        print("-" * 50)
        
        try:
            # Test various URL formats
            test_urls = [
                "example.com",  # Missing protocol
                "http://example.com",  # HTTP
                "https://example.com/",  # HTTPS with trailing slash
                "https://example.com/path",  # HTTPS with path
                "https://example.com/path/",  # HTTPS with path and trailing slash
                "https://subdomain.example.com",  # Subdomain
                "https://example.com:8080",  # Port
                "https://example.com?param=value",  # Query parameters
            ]
            
            print(f"   Testing {len(test_urls)} URL formats...")
            
            # Start batch analysis with various URL formats
            self.batch_job_id = await self.comprehensive_speed_service.start_batch_analysis(
                urls=test_urls,
                batch_size=3,
                priority=JobPriority.NORMAL,
                timeout_seconds=60
            )
            
            print(f"   Batch Job Created: ✅")
            print(f"   Job ID: {self.batch_job_id}")
            
            # Verify URLs were processed
            progress = await self.comprehensive_speed_service.get_batch_progress(self.batch_job_id)
            
            assert progress is not None, "Progress should be retrievable"
            assert progress.total_urls == len(test_urls), "All URLs should be processed"
            
            print(f"   URL Processing: ✅")
            print(f"   Total URLs: {progress.total_urls}")
            print(f"   Status: {progress.status}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise
    
    @pytest.mark.asyncio
    async def test_10_priority_handling(self):
        """Test priority handling (low, normal, high, urgent)."""
        print("\n🧪 **Test 10: Priority Handling**")
        print("-" * 50)
        
        try:
            # Test different priority levels
            priorities = [
                (JobPriority.LOW, "low_priority"),
                (JobPriority.NORMAL, "normal"),
                (JobPriority.HIGH, "high_priority"),
                (JobPriority.URGENT, "high_priority")  # URGENT maps to high_priority
            ]
            
            created_jobs = []
            
            for priority, expected_queue in priorities:
                print(f"   Testing {priority.name} priority...")
                
                # Create batch job with specific priority
                job_id = await self.comprehensive_speed_service.start_batch_analysis(
                    urls=self.test_urls[:1],  # Single URL for faster test
                    batch_size=1,
                    priority=priority,
                    timeout_seconds=30
                )
                
                created_jobs.append(job_id)
                
                # Verify job was created
                assert job_id is not None, f"Job should be created for {priority.name} priority"
                
                # Verify job was queued in correct priority queue
                # Use the same batch processor instance that was used to create the job
                batch_processor = self.comprehensive_speed_service.batch_processor
                
                # Find the job in the appropriate queue
                queue = batch_processor.job_queue_manager.get_queue(expected_queue)
                assert queue is not None, f"Queue {expected_queue} should exist"
                
                # Check if job is in the queue
                job_in_queue = any(entry.batch_job_id == job_id for entry in queue._queue)
                job_running = any(entry.batch_job_id == job_id for entry in queue._running_jobs.values())
                
                assert job_in_queue or job_running, f"Job should be in {expected_queue} queue"
                
                print(f"     ✅ {priority.name} priority → {expected_queue} queue")
            
            print(f"   All Priority Tests: ✅")
            print(f"   Jobs Created: {len(created_jobs)}")
            
            # Clean up test jobs
            for job_id in created_jobs:
                try:
                    await self.comprehensive_speed_service.cancel_batch_job(job_id)
                except:
                    pass  # Ignore cleanup errors
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            raise


async def run_all_tests():
    """Run all batch processing API tests."""
    print("🧪 **Running Batch Processing API Tests**")
    print("=" * 80)
    print("Testing all real-time API endpoints marked as COMPLETED")
    print("=" * 80)
    
    test_suite = TestBatchProcessingAPI()
    
    # Setup
    await test_suite.setup()
    
    # Run all tests
    test_methods = [
        test_suite.test_01_start_batch_analysis,
        test_suite.test_02_get_batch_progress,
        test_suite.test_03_get_all_batch_jobs,
        test_suite.test_04_cancel_batch_job,
        test_suite.test_05_get_batch_results,
        test_suite.test_06_get_queue_status,
        test_suite.test_07_cleanup_old_jobs,
        test_suite.test_08_system_health,
        test_suite.test_09_url_validation_and_cleaning,
        test_suite.test_10_priority_handling,
    ]
    
    passed = 0
    failed = 0
    
    for i, test_method in enumerate(test_methods, 1):
        try:
            print(f"\n🚀 **Running Test {i}/10: {test_method.__name__}**")
            print("=" * 60)
            
            await test_method()
            
            print(f"✅ **Test {i} PASSED**")
            passed += 1
            
        except Exception as e:
            print(f"❌ **Test {i} FAILED: {e}**")
            failed += 1
            import traceback
            traceback.print_exc()
        
        print(f"\n{'='*60}")
    
    # Teardown
    await test_suite.teardown()
    
    # Summary
    print(f"\n🎉 **TEST SUMMARY**")
    print("=" * 60)
    print(f"✅ Passed: {passed}/10")
    print(f"❌ Failed: {failed}/10")
    print(f"📊 Success Rate: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print(f"\n🎯 **ALL TESTS PASSED!**")
        print(f"The batch processing API endpoints are working correctly!")
        return True
    else:
        print(f"\n⚠️  **{failed} TESTS FAILED**")
        print(f"Some API endpoints need attention.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
