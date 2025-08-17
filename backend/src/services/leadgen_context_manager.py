"""
LeadGenBuilder Context Manager
Manages workflow state, session context, and conversation history for the lead generation system
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


class WorkflowStep(Enum):
    """Workflow steps for the lead generation process"""
    INITIALIZED = "INITIAL"
    PARAMETERS_CONFIRMED = "PARAMETERS_CONFIRMED"
    BUSINESSES_DISCOVERED = "BUSINESSES_DISCOVERED"
    WEBSITES_SCORED = "WEBSITES_SCORED"
    DEMOS_GENERATED = "DEMOS_GENERATED"
    DATA_EXPORTED = "DATA_EXPORTED"
    OUTREACH_GENERATED = "OUTREACH_GENERATED"
    COMPLETED = "COMPLETED"


class ConfirmationType(Enum):
    """Types of confirmations that can be requested"""
    PARAMETERS = "parameters"
    TOOL_EXECUTION = "tool_execution"
    DATA_EXPORT = "data_export"
    OUTREACH_GENERATION = "outreach_generation"


@dataclass
class WorkflowState:
    """Represents the current state of a workflow session"""
    
    session_id: str
    current_step: WorkflowStep = WorkflowStep.INITIALIZED
    location: Optional[str] = None
    niche: Optional[str] = None
    discovered_businesses: List[Dict[str, Any]] = None
    scored_businesses: List[Dict[str, Any]] = None
    demo_businesses: List[Dict[str, Any]] = None
    exported_data: Optional[Dict[str, Any]] = None
    outreach_businesses: List[Dict[str, Any]] = None
    pending_confirmation: bool = False
    confirmation_type: Optional[ConfirmationType] = None
    confirmation_message: Optional[str] = None
    pending_action: Optional[Dict[str, Any]] = None
    errors: List[str] = None
    warnings: List[str] = None
    created_at: datetime = None
    last_updated: datetime = None
    started_at: Optional[datetime] = None
    total_time_seconds: Optional[int] = None
    
    def __post_init__(self):
        if self.discovered_businesses is None:
            self.discovered_businesses = []
        if self.scored_businesses is None:
            self.scored_businesses = []
        if self.demo_businesses is None:
            self.demo_businesses = []
        if self.outreach_businesses is None:
            self.outreach_businesses = []
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
        if self.started_at is None:
            self.started_at = datetime.now()
    
    def get_progress_percentage(self) -> int:
        """Calculate progress percentage based on completed steps"""
        total_steps = len(WorkflowStep)
        current_step_index = list(WorkflowStep).index(self.current_step)
        return min(100, int((current_step_index / (total_steps - 1)) * 100))
    
    def get_frontend_workflow_progress(self) -> Dict[str, Any]:
        """Convert to frontend-compatible workflow progress format"""
        return {
            "current_step": self.current_step.value,
            "progress_percentage": self.get_progress_percentage(),
            "location": self.location,
            "niche": self.niche,
            "businesses_discovered": len(self.discovered_businesses),
            "businesses_scored": len(self.scored_businesses),
            "demo_sites_generated": len(self.demo_businesses),
            "has_exported_data": self.exported_data is not None,
            "has_outreach": len(self.outreach_businesses) > 0,
            "pending_confirmation": self.confirmation_type.value if self.confirmation_type else None,
            "confirmation_message": self.confirmation_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "total_time_seconds": self.total_time_seconds or (
                int((datetime.now() - self.started_at).total_seconds()) if self.started_at else 0
            ),
            "errors": self.errors,
            "warnings": self.warnings
        }


@dataclass
class MessageHistory:
    """Represents a message in the conversation history"""
    
    timestamp: datetime
    role: str  # "user" or "assistant"
    content: str
    metadata: Optional[Dict[str, Any]] = None


class LeadGenContextManager:
    """
    Manages workflow state and context for lead generation sessions
    
    This class handles:
    - Session creation and management
    - Workflow state tracking
    - Message history storage
    - Confirmation flows
    - Error handling and recovery
    """
    
    def __init__(self):
        self.workflow_states: Dict[str, WorkflowState] = {}
        self.message_histories: Dict[str, List[MessageHistory]] = {}
        self.session_timeout = timedelta(hours=24)  # 24 hour timeout
    
    def get_or_create_workflow_state(self, session_id: str) -> WorkflowState:
        """Get existing workflow state or create a new one"""
        
        if session_id not in self.workflow_states:
            logger.info(f"🆕 Creating new workflow state for session {session_id}")
            self.workflow_states[session_id] = WorkflowState(session_id=session_id)
        
        return self.workflow_states[session_id]
    
    def get_workflow_state(self, session_id: str) -> Optional[WorkflowState]:
        """Get existing workflow state if it exists"""
        return self.workflow_states.get(session_id)
    
    def update_workflow_state(self, session_id: str, updates: Dict[str, Any]):
        """Update workflow state with new data"""
        
        if session_id not in self.workflow_states:
            logger.warning(f"⚠️ Attempted to update non-existent session {session_id}")
            return
        
        workflow_state = self.workflow_states[session_id]
        
        # Update fields that exist in the WorkflowState
        for key, value in updates.items():
            if hasattr(workflow_state, key):
                setattr(workflow_state, key, value)
            else:
                logger.warning(f"⚠️ Unknown field {key} for workflow state")
        
        # Update timestamp
        workflow_state.last_updated = datetime.now()
    
    def advance_workflow_step(self, session_id: str, new_step: WorkflowStep):
        """Advance the workflow to a new step"""
        
        if session_id not in self.workflow_states:
            logger.warning(f"⚠️ Attempted to advance non-existent session {session_id}")
            return
        
        workflow_state = self.workflow_states[session_id]
        old_step = workflow_state.current_step
        
        workflow_state.current_step = new_step
        workflow_state.last_updated = datetime.now()
        
        logger.info(f"🔄 Workflow step advanced for session {session_id}: {old_step.value} → {new_step.value}")
    
    def add_message_to_history(self, session_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation history"""
        
        if session_id not in self.message_histories:
            self.message_histories[session_id] = []
        
        message = MessageHistory(
            timestamp=datetime.now(),
            role=role,
            content=content,
            metadata=metadata
        )
        
        self.message_histories[session_id].append(message)
        logger.info(f"💬 Added {role} message to session {session_id}")
    
    def get_message_history(self, session_id: str) -> List[Dict[str, str]]:
        """Get message history for a session in a simplified format"""
        
        if session_id not in self.message_histories:
            return []
        
        # Convert to simple dict format for AI agent consumption
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in self.message_histories[session_id]
        ]
    
    def set_pending_confirmation(
        self, 
        session_id: str, 
        confirmation_type: ConfirmationType, 
        message: str, 
        pending_action: Dict[str, Any]
    ):
        """Set a pending confirmation for the user"""
        
        if session_id not in self.workflow_states:
            logger.warning(f"⚠️ Attempted to set confirmation for non-existent session {session_id}")
            return
        
        workflow_state = self.workflow_states[session_id]
        
        workflow_state.pending_confirmation = True
        workflow_state.confirmation_type = confirmation_type
        workflow_state.confirmation_message = message
        workflow_state.pending_action = pending_action
        workflow_state.last_updated = datetime.now()
        
        logger.info(f"⏳ Set pending confirmation for session {session_id}: {confirmation_type.value}")
    
    def clear_pending_confirmation(self, session_id: str):
        """Clear a pending confirmation without resolving it"""
        
        if session_id not in self.workflow_states:
            logger.warning(f"⚠️ Attempted to clear confirmation for non-existent session {session_id}")
            return
        
        workflow_state = self.workflow_states[session_id]
        
        if not workflow_state.pending_confirmation:
            logger.warning(f"⚠️ No pending confirmation for session {session_id}")
            return
        
        # Clear confirmation state
        workflow_state.pending_confirmation = False
        workflow_state.confirmation_type = None
        workflow_state.confirmation_message = None
        workflow_state.pending_action = None
        workflow_state.last_updated = datetime.now()
        
        logger.info(f"🧹 Cleared pending confirmation for session {session_id}")
    
    def resolve_confirmation(self, session_id: str, confirmed: bool) -> Optional[Dict[str, Any]]:
        """Resolve a pending confirmation"""
        
        if session_id not in self.workflow_states:
            logger.warning(f"⚠️ Attempted to resolve confirmation for non-existent session {session_id}")
            return None
        
        workflow_state = self.workflow_states[session_id]
        
        if not workflow_state.pending_confirmation:
            logger.warning(f"⚠️ No pending confirmation for session {session_id}")
            return None
        
        # Clear confirmation state
        resolved_action = workflow_state.pending_action
        workflow_state.pending_confirmation = False
        workflow_state.confirmation_type = None
        workflow_state.confirmation_message = None
        workflow_state.pending_action = None
        workflow_state.last_updated = datetime.now()
        
        logger.info(f"✅ Resolved confirmation for session {session_id}: confirmed={confirmed}")
        
        if confirmed:
            return resolved_action
        else:
            return None
    
    def handle_workflow_error(self, session_id: str, error_message: str, recoverable: bool = True):
        """Handle workflow errors and store them in the session state"""
        
        if session_id not in self.workflow_states:
            logger.warning(f"⚠️ Attempted to handle error for non-existent session {session_id}")
            return
        
        workflow_state = self.workflow_states[session_id]
        
        # Add error to the list
        workflow_state.errors.append(error_message)
        workflow_state.last_updated = datetime.now()
        
        # Add warning if recoverable
        if recoverable:
            warning_msg = f"Recoverable error: {error_message}"
            workflow_state.warnings.append(warning_msg)
        
        logger.error(f"❌ Workflow error for session {session_id}: {error_message} (recoverable: {recoverable})")
    
    def add_warning(self, session_id: str, warning_message: str):
        """Add a warning to the session state"""
        
        if session_id not in self.workflow_states:
            logger.warning(f"⚠️ Attempted to add warning for non-existent session {session_id}")
            return
        
        workflow_state = self.workflow_states[session_id]
        workflow_state.warnings.append(warning_message)
        workflow_state.last_updated = datetime.now()
        
        logger.warning(f"⚠️ Warning for session {session_id}: {warning_message}")
    
    def get_workflow_progress(self, session_id: str) -> Dict[str, Any]:
        """Get current workflow progress for a session"""
        
        if session_id not in self.workflow_states:
            return {"error": "Session not found"}
        
        workflow_state = self.workflow_states[session_id]
        
        # Use the new frontend-compatible format
        return workflow_state.get_frontend_workflow_progress()
    
    def get_next_recommended_action(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get the next recommended action based on current workflow state"""
        
        if session_id not in self.workflow_states:
            return None
        
        workflow_state = self.workflow_states[session_id]
        
        if workflow_state.pending_confirmation:
            return {
                "type": "confirmation_required",
                "message": workflow_state.confirmation_message,
                "confirmation_type": workflow_state.confirmation_type.value
            }
        
        # Determine next action based on current step
        if workflow_state.current_step == WorkflowStep.INITIALIZED:
            if not workflow_state.location or not workflow_state.niche:
                return {
                    "type": "parameter_input",
                    "message": "Please provide location and business niche to get started"
                }
            else:
                return {
                    "type": "parameter_confirmation",
                    "message": f"Ready to search for {workflow_state.niche} in {workflow_state.location}. Should I proceed?"
                }
        
        elif workflow_state.current_step == WorkflowStep.PARAMETERS_CONFIRMED:
            return {
                "type": "business_discovery",
                "message": f"Searching for {workflow_state.niche} businesses in {workflow_state.location}"
            }
        
        elif workflow_state.current_step == WorkflowStep.BUSINESSES_DISCOVERED:
            if workflow_state.discovered_businesses:
                return {
                    "type": "website_scoring",
                    "message": f"Evaluating website quality for {len(workflow_state.discovered_businesses)} discovered businesses"
                }
            else:
                return {
                    "type": "error_recovery",
                    "message": "No businesses were discovered. Please try different parameters."
                }
        
        elif workflow_state.current_step == WorkflowStep.WEBSITES_SCORED:
            return {
                "type": "demo_generation",
                "message": "Creating demo websites to showcase improvement opportunities"
            }
        
        elif workflow_state.current_step == WorkflowStep.DEMOS_GENERATED:
            return {
                "type": "data_export",
                "message": "Exporting business and scoring data for analysis"
            }
        
        elif workflow_state.current_step == WorkflowStep.DATA_EXPORTED:
            return {
                "type": "outreach_generation",
                "message": "Generating personalized outreach messages for businesses"
            }
        
        elif workflow_state.current_step == WorkflowStep.OUTREACH_GENERATED:
            return {
                "type": "workflow_completion",
                "message": "All tasks completed successfully!"
            }
        
        return None
    
    def export_workflow_state(self, session_id: str) -> Dict[str, Any]:
        """Export complete workflow state for debugging or analysis"""
        
        if session_id not in self.workflow_states:
            return {"error": "Session not found"}
        
        workflow_state = self.workflow_states[session_id]
        message_history = self.message_histories.get(session_id, [])
        
        return {
            "session_id": session_id,
            "workflow_state": asdict(workflow_state),
            "message_history": [
                {
                    "timestamp": msg.timestamp.isoformat(),
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.metadata
                }
                for msg in message_history
            ],
            "exported_at": datetime.now().isoformat()
        }
    
    def cleanup_old_sessions(self):
        """Clean up expired sessions to prevent memory leaks"""
        
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, workflow_state in self.workflow_states.items():
            if current_time - workflow_state.last_updated > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            logger.info(f"🧹 Cleaning up expired session {session_id}")
            del self.workflow_states[session_id]
            if session_id in self.message_histories:
                del self.message_histories[session_id]
        
        if expired_sessions:
            logger.info(f"🧹 Cleaned up {len(expired_sessions)} expired sessions")
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        
        return list(self.workflow_states.keys())
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        
        return len(self.workflow_states)
    
    def reset_session(self, session_id: str):
        """Reset a session to initial state"""
        
        if session_id in self.workflow_states:
            logger.info(f"🔄 Resetting session {session_id}")
            del self.workflow_states[session_id]
        
        if session_id in self.message_histories:
            del self.message_histories[session_id]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of session activity"""
        
        if session_id not in self.workflow_states:
            return {"error": "Session not found"}
        
        workflow_state = self.workflow_states[session_id]
        message_history = self.message_histories.get(session_id, [])
        
        return {
            "session_id": session_id,
            "current_step": workflow_state.current_step.value,
            "progress_percentage": workflow_state.get_progress_percentage(),
            "message_count": len(message_history),
            "created_at": workflow_state.created_at.isoformat(),
            "last_updated": workflow_state.last_updated.isoformat(),
            "total_time_seconds": workflow_state.total_time_seconds or 0
        }
