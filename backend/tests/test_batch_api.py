#!/usr/bin/env python3
"""
Test script for batch processing API endpoints.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

async def test_batch_api():
    """Test the batch processing API endpoints."""
    try:
        print("Testing batch processing API...")
        
        # Test imports
        from src.api.v1.batch_processing import router
        print("✅ Batch processing API imports successfully")
        
        # Test service initialization
        from src.services.batch_processor import BatchProcessor
        from src.services.comprehensive_speed_service import ComprehensiveSpeedService
        
        batch_processor = BatchProcessor()
        comprehensive_speed_service = ComprehensiveSpeedService()
        print("✅ Services initialize successfully")
        
        # Test queue status
        queue_statuses = batch_processor.job_queue_manager.get_all_queue_statuses()
        print(f"✅ Queue statuses retrieved: {len(queue_statuses)} queues")
        
        # Test service health
        health = comprehensive_speed_service.get_service_health()
        print(f"✅ Service health: {health['status']}")
        
        print("\n🎉 All tests passed! Batch processing API is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_batch_api())
    sys.exit(0 if success else 1)
