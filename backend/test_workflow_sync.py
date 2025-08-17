#!/usr/bin/env python3
"""
Test script to verify workflow synchronization between backend and frontend
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.leadgen_context_manager import LeadGenContextManager, WorkflowStep

async def test_workflow_sync():
    """Test workflow state synchronization"""
    
    print("🧪 Testing Workflow Synchronization")
    print("=" * 50)
    
    # Initialize services
    context_manager = LeadGenContextManager()
    
    # Create a test session
    session_id = "test-session-123"
    
    print(f"📝 Creating test session: {session_id}")
    
    # Test initial state
    workflow_state = context_manager.get_or_create_workflow_state(session_id)
    print(f"🔍 Initial workflow state: {workflow_state.current_step.value}")
    
    # Test parameter confirmation
    print("\n✅ Testing parameter confirmation...")
    context_manager.update_workflow_state(session_id, {
        "location": "London, UK",
        "niche": "gyms"
    })
    context_manager.advance_workflow_step(session_id, WorkflowStep.PARAMETERS_CONFIRMED)
    
    workflow_state = context_manager.get_or_create_workflow_state(session_id)
    print(f"🔍 After parameter confirmation: {workflow_state.current_step.value}")
    
    # Test business discovery
    print("\n🔍 Testing business discovery...")
    mock_businesses = [
        {"business_name": "Test Gym 1", "address": "123 Test St"},
        {"business_name": "Test Gym 2", "address": "456 Test Ave"}
    ]
    
    context_manager.update_workflow_state(session_id, {
        "discovered_businesses": mock_businesses
    })
    context_manager.advance_workflow_step(session_id, WorkflowStep.BUSINESSES_DISCOVERED)
    
    workflow_state = context_manager.get_or_create_workflow_state(session_id)
    print(f"🔍 After business discovery: {workflow_state.current_step.value}")
    print(f"📊 Businesses found: {len(workflow_state.discovered_businesses)}")
    
    # Test frontend workflow progress format
    print("\n🖥️ Testing frontend workflow progress format...")
    frontend_progress = workflow_state.get_frontend_workflow_progress()
    
    print("Frontend Progress Data:")
    for key, value in frontend_progress.items():
        print(f"  {key}: {value}")
    
    # Test workflow progress method
    print("\n📊 Testing workflow progress method...")
    progress_data = context_manager.get_workflow_progress(session_id)
    
    print("Workflow Progress Data:")
    for key, value in progress_data.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Workflow synchronization test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_workflow_sync())
