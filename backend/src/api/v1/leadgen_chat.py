"""
LeadGen Chat API Endpoint
Handles AI-powered chat interactions for lead generation workflow
"""

import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from src.services.leadgen_ai_agent import LeadGenAIAgent
from src.services.leadgen_context_manager import LeadGenContextManager

logger = logging.getLogger(__name__)

# Initialize services
ai_agent = LeadGenAIAgent()
context_manager = LeadGenContextManager()

router = APIRouter(prefix="/leadgen-chat", tags=["LeadGen Chat"])


class ChatMessage(BaseModel):
    """Chat message model"""
    
    message: str = Field(..., description="User's message")
    session_id: Optional[str] = Field(None, description="Session identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ChatResponse(BaseModel):
    """Chat response model"""
    
    session_id: str = Field(..., description="Session identifier")
    content: str = Field(..., description="AI agent response content")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool calls to execute")
    requires_confirmation: bool = Field(False, description="Whether user confirmation is required")
    workflow_progress: Optional[Dict[str, Any]] = Field(None, description="Current workflow progress")
    timestamp: str = Field(..., description="Response timestamp")


class SessionInfo(BaseModel):
    """Session information model"""
    
    session_id: str = Field(..., description="Session identifier")
    created_at: str = Field(..., description="Session creation timestamp")
    last_updated: str = Field(..., description="Last activity timestamp")
    message_count: int = Field(..., description="Number of messages in session")
    current_step: str = Field(..., description="Current workflow step")
    business_count: int = Field(..., description="Number of discovered businesses")
    error_count: int = Field(..., description="Number of errors encountered")
    warning_count: int = Field(..., description="Number of warnings")


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_message: ChatMessage,
    background_tasks: BackgroundTasks
) -> ChatResponse:
    """
    Chat with the LeadGen AI agent
    
    This endpoint processes user messages and returns AI responses with tool calls
    """
    
    try:
        # Generate or use existing session ID
        session_id = chat_message.session_id or str(uuid.uuid4())
        
        logger.info(f"🤖 Processing chat message for session {session_id}")
        logger.info(f"📝 User message: {chat_message.message}")
        
        # Get or create workflow state
        workflow_state = context_manager.get_or_create_workflow_state(session_id)
        
        # Add user message to history
        context_manager.add_message_to_history(
            session_id=session_id,
            role="user",
            content=chat_message.message,
            metadata=chat_message.metadata
        )
        
        # Process message with AI agent
        ai_response = await ai_agent.process_message(
            user_message=chat_message.message,
            session_id=session_id,
            message_history=context_manager.get_message_history(session_id)
        )
        
        # Add AI response to history
        context_manager.add_message_to_history(
            session_id=session_id,
            role="assistant",
            content=ai_response["content"],
            metadata={"tool_calls": ai_response.get("tool_calls", [])}
        )
        
        # Update workflow state if parameters were extracted
        if "parameters" in ai_response:
            context_manager.update_workflow_state(session_id, ai_response["parameters"])
        
        # Get current workflow progress
        workflow_progress = context_manager.get_workflow_progress(session_id)
        
        # Create response
        response = ChatResponse(
            session_id=session_id,
            content=ai_response["content"],
            tool_calls=ai_response.get("tool_calls", []),
            requires_confirmation=ai_response.get("requires_confirmation", False),
            workflow_progress=workflow_progress,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Chat response generated for session {session_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Chat processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat message: {str(e)}"
        )


@router.get("/sessions", response_model=List[SessionInfo])
async def get_active_sessions() -> List[SessionInfo]:
    """Get list of active chat sessions"""
    
    try:
        active_sessions = context_manager.get_active_sessions()
        session_infos = []
        
        for session_id in active_sessions:
            summary = context_manager.get_session_summary(session_id)
            if "error" not in summary:
                session_infos.append(SessionInfo(**summary))
        
        logger.info(f"📋 Retrieved {len(session_infos)} active sessions")
        return session_infos
        
    except Exception as e:
        logger.error(f"❌ Failed to get active sessions: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve active sessions: {str(e)}"
        )


@router.get("/sessions/{session_id}/progress", response_model=Dict[str, Any])
async def get_session_progress(session_id: str) -> Dict[str, Any]:
    """Get workflow progress for a specific session"""
    
    try:
        progress = context_manager.get_workflow_progress(session_id)
        
        if "error" in progress:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"📊 Retrieved progress for session {session_id}")
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get session progress: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session progress: {str(e)}"
        )


@router.post("/sessions/{session_id}/confirm")
async def confirm_action(
    session_id: str,
    confirmed: bool = True
) -> Dict[str, Any]:
    """Confirm a pending action for a session"""
    
    try:
        result = context_manager.resolve_confirmation(session_id, confirmed)
        
        if result is None:
            raise HTTPException(
                status_code=400,
                detail="No pending confirmation for this session"
            )
        
        logger.info(f"✅ Confirmation resolved for session {session_id}: {confirmed}")
        return {
            "session_id": session_id,
            "confirmed": confirmed,
            "action": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to resolve confirmation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resolve confirmation: {str(e)}"
        )


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> Dict[str, Any]:
    """Delete a chat session and clear all associated data"""
    
    try:
        context_manager.reset_session(session_id)
        ai_agent.clear_session_context(session_id)
        
        logger.info(f"🗑️ Session {session_id} deleted")
        return {
            "session_id": session_id,
            "deleted": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to delete session {session_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    
    return {
        "status": "healthy",
        "service": "LeadGen Chat API",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": context_manager.get_session_count()
    }
