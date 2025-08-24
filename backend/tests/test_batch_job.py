#!/usr/bin/env python3
"""
Test script for starting a batch analysis job.
"""

import asyncio
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_batch_job():
    """Test starting a batch analysis job."""
    try:
        print("Testing batch job creation...")
        
        # Import services
        from src.services.comprehensive_speed_service import ComprehensiveSpeedService
        from src.services.job_queue import JobPriority
        
        comprehensive_speed_service = ComprehensiveSpeedService()
        print("✅ Comprehensive speed service initialized")
        
        # Test URLs
        test_urls = [
            "https://example.com",
            "https://google.com",
            "https://github.com"
        ]
        
        print(f"Starting batch analysis for {len(test_urls)} URLs...")
        
        # Start batch analysis
        batch_job_id = await comprehensive_speed_service.start_batch_analysis(
            urls=test_urls,
            batch_size=2,
            priority=JobPriority.NORMAL,
            timeout_seconds=300
        )
        
        print(f"✅ Batch job started with ID: {batch_job_id}")
        
        # Get progress
        progress = await comprehensive_speed_service.get_batch_progress(batch_job_id)
        if progress:
            print(f"✅ Progress retrieved: {progress.status}")
            print(f"   Total URLs: {progress.total_urls}")
            print(f"   Completed: {progress.completed_urls}")
            print(f"   Failed: {progress.failed_urls}")
            print(f"   Progress: {progress.progress_percentage:.1f}%")
        else:
            print("❌ Could not retrieve progress")
        
        # Get all batch jobs
        all_jobs = await comprehensive_speed_service.get_all_batch_jobs()
        print(f"✅ Total batch jobs: {len(all_jobs)}")
        
        print("\n🎉 Batch job test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_batch_job())
    sys.exit(0 if success else 1)
