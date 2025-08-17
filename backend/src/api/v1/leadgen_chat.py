"""
LeadGenBuilder Chat API - Autonomous Agent Interface
Provides a conversational interface to the LeadGenBuilder agent
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.services.leadgen_ai_agent import LeadGenAIAgent
from src.services.leadgen_tool_executor import LeadGenToolExecutor
from src.services.leadgen_context_manager import LeadGenContextManager, WorkflowStep, ConfirmationType
from src.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/leadgen-chat", tags=["leadgen-chat"])

# Global instances (in production, these would be injected dependencies)
ai_agent = LeadGenAIAgent()
tool_executor = LeadGenToolExecutor()
context_manager = LeadGenContextManager()


class ChatMessage(BaseModel):
    """Chat message from user"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")


class ChatResponse(BaseModel):
    """Response from the LeadGenBuilder agent"""
    session_id: str
    agent_message: str
    requires_confirmation: bool = False
    pending_action: Optional[Dict[str, Any]] = None
    workflow_progress: Optional[Dict[str, Any]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class ConfirmationRequest(BaseModel):
    """User confirmation for pending actions"""
    session_id: str = Field(..., description="Session ID")
    confirmed: bool = Field(..., description="Whether user confirmed the action")
    message: Optional[str] = Field(None, description="Optional message from user")


@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatMessage, background_tasks: BackgroundTasks):
    """
    Send a message to the LeadGenBuilder autonomous agent
    
    This endpoint provides a conversational interface where users can:
    - Ask the agent to find businesses
    - Confirm parameters and actions
    - Track workflow progress
    - Get results and next steps
    """
    
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"💬 LeadGen Chat - New message for session {session_id}")
        logger.info(f"📝 User Message: {request.message}")
        
        # Add user message to history
        context_manager.add_message_to_history(session_id, "user", request.message)
        
        # Get current workflow state
        workflow_state = context_manager.get_or_create_workflow_state(session_id)
        
        # Check if there's a pending confirmation
        if workflow_state.pending_confirmation:
            logger.info(f"⏳ Handling pending confirmation for session {session_id}")
            return await _handle_pending_confirmation(session_id, request.message)
        
        # Get message history for context
        message_history = context_manager.get_message_history(session_id)
        
        # Process message through AI agent
        ai_response = await ai_agent.process_message(
            user_message=request.message,
            session_id=session_id,
            message_history=message_history
        )
        
        # Validate AI response
        if not ai_response:
            logger.error("❌ AI agent returned None response")
            raise Exception("AI agent failed to process message")
        
        # Add agent response to history
        if ai_response.get("content"):
            context_manager.add_message_to_history(session_id, "assistant", ai_response["content"])
        
        # Handle any tool calls
        tool_results = []
        if ai_response.get("tool_calls"):
            logger.info(f"🔧 Processing {len(ai_response['tool_calls'])} tool calls")
            
            for tool_call in ai_response["tool_calls"]:
                tool_result = await _execute_tool_with_context(tool_call, session_id)
                logger.info(f"🔧 Tool execution result: {tool_result}")
                tool_results.append(tool_result)
                
                # Update workflow state based on tool results
                await _update_workflow_from_tool_result(tool_result, session_id)
                
                # Update AI agent context so it knows about the progress
                if tool_result.get("success"):
                    tool_name = tool_result.get("tool_name", "unknown")
                    ai_agent.update_context_from_tool_result(session_id, tool_name, tool_result)
        
        # Get updated workflow progress
        workflow_progress = context_manager.get_workflow_progress(session_id)
        
        # Check for next recommended action
        next_action = context_manager.get_next_recommended_action(session_id)
        
        # Prepare response - ensure content is always a string
        response_content = ai_response.get("content") or ""
        if response_content is None:
            response_content = ""
        
        # Add workflow progress information to response
        if tool_results:
            tool_summary = _format_tool_results_summary(tool_results)
            if tool_summary:
                response_content += "\n\n" + tool_summary
        
        # Add next step information
        if next_action and next_action.get("type") != "confirmation_required":
            next_message = next_action.get("message") or ""
            if next_message:
                response_content += f"\n\n🔄 Next: {next_message}"
        
        # Schedule cleanup in background
        background_tasks.add_task(context_manager.cleanup_old_sessions)
        
        return ChatResponse(
            session_id=session_id,
            agent_message=response_content,
            requires_confirmation=ai_response.get("requires_confirmation", False) or bool(workflow_state.pending_confirmation),
            pending_action=workflow_state.pending_action,
            workflow_progress=workflow_progress,
            tool_results=tool_results,
            errors=workflow_state.errors[-5:] if workflow_state.errors else None,  # Last 5 errors
            warnings=workflow_state.warnings[-3:] if workflow_state.warnings else None  # Last 3 warnings
        )
        
    except Exception as e:
        logger.error(f"❌ Chat message processing failed: {e}")
        
        # Handle error gracefully
        session_id = request.session_id or str(uuid.uuid4())
        context_manager.handle_workflow_error(session_id, str(e), recoverable=False)
        
        return ChatResponse(
            session_id=session_id,
            agent_message=f"I apologize, but I encountered an error: {str(e)}. Please try again or start a new session.",
            requires_confirmation=False,
            errors=[str(e)]
        )


@router.post("/confirm", response_model=ChatResponse)
async def confirm_action(request: ConfirmationRequest):
    """
    Confirm or reject a pending action
    """
    
    try:
        logger.info(f"✅ Confirmation for session {request.session_id}: {request.confirmed}")
        
        # Resolve the pending confirmation
        resolved_action = context_manager.resolve_confirmation(request.session_id, request.confirmed)
        
        if not request.confirmed:
            # User rejected - ask what they'd like to do instead
            return ChatResponse(
                session_id=request.session_id,
                agent_message="No problem! What would you like me to do instead?",
                requires_confirmation=False,
                workflow_progress=context_manager.get_workflow_progress(request.session_id)
            )
        
        if resolved_action:
            # Execute the confirmed action
            if resolved_action.get("type") == "tool_execution":
                tool_result = await tool_executor.execute_tool(
                    resolved_action["tool"],
                    resolved_action.get("arguments", {})
                )
                
                await _update_workflow_from_tool_result(tool_result, request.session_id)
                
                # Update AI agent context so it knows about the progress
                if tool_result.get("success"):
                    tool_name = resolved_action["tool"]
                    ai_agent.update_context_from_tool_result(request.session_id, tool_name, tool_result)
                
                response_message = f"✅ {resolved_action.get('message', 'Action completed')}"
                if tool_result.get("result", {}).get("message"):
                    response_message += f"\n\n{tool_result['result']['message']}"
                
                return ChatResponse(
                    session_id=request.session_id,
                    agent_message=response_message,
                    requires_confirmation=False,
                    workflow_progress=context_manager.get_workflow_progress(request.session_id),
                    tool_results=[tool_result]
                )
            
            elif resolved_action.get("type") == "parameter_confirmation":
                # Update workflow state with confirmed parameters
                location = resolved_action.get("location")
                niche = resolved_action.get("niche")
                
                logger.info(f"✅ Parameter confirmation - location: {location}, niche: {niche}")
                
                context_manager.update_workflow_state(request.session_id, {
                    "location": location,
                    "niche": niche
                })
                context_manager.advance_workflow_step(request.session_id, WorkflowStep.PARAMETERS_CONFIRMED)
                
                # Get updated workflow state for debugging
                updated_state = context_manager.get_or_create_workflow_state(request.session_id)
                logger.info(f"🔄 Updated workflow state - location: {updated_state.location}, niche: {updated_state.niche}, step: {updated_state.current_step}")
                
                # Automatically proceed to business discovery
                try:
                    logger.info(f"🔍 Automatically proceeding to business discovery for {niche} in {location}")
                    
                    # Call the discover_businesses tool directly
                    tool_result = await tool_executor.execute_tool("discover_businesses", {
                        "location": location,
                        "niche": niche,
                        "max_businesses": 10
                    })
                    
                    # Update workflow state with discovery results
                    await _update_workflow_from_tool_result(tool_result, request.session_id)
                    
                    # Prepare response with discovery results
                    if tool_result.get("success"):
                        discovered_count = tool_result.get("result", {}).get("total_found", 0)
                        response_message = f"Perfect! I found {discovered_count} {niche} businesses in {location}. 🔍\n\nNow let me score their websites to identify improvement opportunities..."
                    else:
                        response_message = f"Perfect! I'll search for {niche} businesses in {location}. Let me start discovering businesses now! 🔍\n\nNote: Business discovery encountered some issues, but I'll continue with the workflow."
                    
                    return ChatResponse(
                        session_id=request.session_id,
                        agent_message=response_message,
                        requires_confirmation=False,
                        workflow_progress=context_manager.get_workflow_progress(request.session_id),
                        tool_results=[tool_result] if tool_result.get("success") else []
                    )
                    
                except Exception as e:
                    logger.error(f"❌ Auto business discovery failed: {e}")
                    # Fall back to manual message
                    return ChatResponse(
                        session_id=request.session_id,
                        agent_message=f"Perfect! I'll search for {niche} businesses in {location}. Let me start discovering businesses now! 🔍",
                        requires_confirmation=False,
                        workflow_progress=context_manager.get_workflow_progress(request.session_id)
                    )
        
        return ChatResponse(
            session_id=request.session_id,
            agent_message="Thanks for confirming! How can I help you next?",
            requires_confirmation=False,
            workflow_progress=context_manager.get_workflow_progress(request.session_id)
        )
        
    except Exception as e:
        logger.error(f"❌ Confirmation processing failed: {e}")
        return ChatResponse(
            session_id=request.session_id,
            agent_message=f"Sorry, I had trouble processing your confirmation: {str(e)}",
            requires_confirmation=False,
            errors=[str(e)]
        )


@router.get("/status/{session_id}")
async def get_session_status(session_id: str):
    """
    Get current status and progress for a session
    """
    
    try:
        workflow_progress = context_manager.get_workflow_progress(session_id)
        next_action = context_manager.get_next_recommended_action(session_id)
        
        return {
            "session_id": session_id,
            "workflow_progress": workflow_progress,
            "next_recommended_action": next_action,
            "message_count": len(context_manager.get_message_history(session_id))
        }
        
    except Exception as e:
        logger.error(f"❌ Status check failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/{session_id}")
async def export_session_data(session_id: str):
    """
    Export complete session data for debugging or analysis
    """
    
    try:
        exported_data = context_manager.export_workflow_state(session_id)
        return exported_data
        
    except Exception as e:
        logger.error(f"❌ Export failed for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/businesses/{session_id}")
async def get_discovered_businesses(session_id: str):
    """
    Get discovered businesses for a session
    """
    try:
        workflow_state = context_manager.get_or_create_workflow_state(session_id)
        
        businesses = workflow_state.discovered_businesses or []
        
        return {
            "success": True,
            "session_id": session_id,
            "businesses": businesses,
            "total_count": len(businesses),
            "location": workflow_state.location,
            "niche": workflow_state.niche,
            "discovered_at": workflow_state.last_updated.isoformat() if workflow_state.last_updated else None
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get discovered businesses for session {session_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "session_id": session_id
        }


async def _handle_pending_confirmation(session_id: str, user_message: str) -> ChatResponse:
    """Handle user response to pending confirmation"""
    
    workflow_state = context_manager.get_or_create_workflow_state(session_id)
    
    # Simple confirmation detection
    user_message_lower = user_message.lower().strip()
    
    if any(word in user_message_lower for word in ["yes", "y", "ok", "okay", "correct", "right", "confirm", "proceed"]):
        # User confirmed
        request = ConfirmationRequest(session_id=session_id, confirmed=True, message=user_message)
        return await confirm_action(request)
    
    elif any(word in user_message_lower for word in ["no", "n", "wrong", "incorrect", "cancel", "stop"]):
        # User rejected
        request = ConfirmationRequest(session_id=session_id, confirmed=False, message=user_message)
        return await confirm_action(request)
    
    else:
        # Ambiguous response - ask for clarification
        return ChatResponse(
            session_id=session_id,
            agent_message=f"I'm not sure if that's a yes or no. {workflow_state.confirmation_message}\n\nPlease respond with 'yes' to confirm or 'no' to cancel.",
            requires_confirmation=True,
            pending_action=workflow_state.pending_action,
            workflow_progress=context_manager.get_workflow_progress(session_id)
        )


async def _execute_tool_with_context(tool_call: Dict[str, Any], session_id: str) -> Dict[str, Any]:
    """Execute a tool call with workflow context"""
    
    try:
        logger.info(f"🔧 Full tool_call received: {tool_call}")
        
        # Handle both tool call formats (AI agent format vs expected format)
        if "function" in tool_call and "name" in tool_call["function"]:
            # AI agent format: {"function": {"name": "tool_name", "arguments": "json_string"}}
            function_name = tool_call["function"]["name"]
            arguments_str = tool_call["function"]["arguments"]
            
            # Parse JSON arguments
            try:
                import json
                arguments = json.loads(arguments_str)
                logger.info(f"🔧 Parsed JSON arguments: {arguments}")
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"❌ Failed to parse arguments JSON: {e}")
                arguments = {}
                
        elif "function_name" in tool_call:
            # Expected format: {"function_name": "tool_name", "arguments": {...}}
            function_name = tool_call["function_name"]
            arguments = tool_call.get("arguments", {})
        else:
            raise ValueError(f"Invalid tool call format: {tool_call}")
        
        logger.info(f"🔧 Tool call: {function_name}")
        logger.info(f"📋 Original arguments: {arguments}")
        logger.info(f"📋 Arguments type: {type(arguments)}")
        
        # Add session context to tool arguments if needed
        workflow_state = context_manager.get_or_create_workflow_state(session_id)
        logger.info(f"📍 Workflow state - location: {workflow_state.location}, niche: {workflow_state.niche}")
        
        # Ensure location and niche are available for tools that need them
        if function_name in ["discover_businesses", "generate_demo_sites"]:
            if "location" not in arguments and workflow_state.location:
                arguments["location"] = workflow_state.location
                logger.info(f"📍 Added location from workflow state: {workflow_state.location}")
            if "niche" not in arguments and workflow_state.niche:
                arguments["niche"] = workflow_state.niche
                logger.info(f"📍 Added niche from workflow state: {workflow_state.niche}")
        
        logger.info(f"📋 Final arguments: {arguments}")
        
        # Execute the tool
        result = await tool_executor.execute_tool(function_name, arguments)
        
        # Add session context to result
        result["session_id"] = session_id
        result["executed_at"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Tool execution with context failed: {e}")
        logger.error(f"❌ Tool call that failed: {tool_call}")
        return {
            "success": False,
            "error": str(e),
            "tool_name": tool_call.get("function_name", tool_call.get("function", {}).get("name", "unknown")),
            "session_id": session_id
        }


async def _update_workflow_from_tool_result(tool_result: Dict[str, Any], session_id: str):
    """Update workflow state based on tool execution results"""
    
    logger.info(f"🔄 Updating workflow from tool result: {tool_result.get('tool_name')} - success: {tool_result.get('success')}")
    
    if not tool_result.get("success"):
        context_manager.handle_workflow_error(
            session_id, 
            f"Tool {tool_result.get('tool_name')} failed: {tool_result.get('error')}",
            recoverable=True
        )
        return
    
    tool_name = tool_result.get("tool_name")
    result_data = tool_result.get("result", {})
    
    logger.info(f"📋 Tool result data: {result_data}")
    
    # Update workflow state based on tool type
    if tool_name == "discover_businesses":
        logger.info(f"🔍 Updating workflow with discovered businesses: {len(result_data.get('businesses', []))} found")
        context_manager.update_workflow_state(session_id, {
            "discovered_businesses": result_data.get("businesses", [])
        })
        context_manager.advance_workflow_step(session_id, WorkflowStep.BUSINESSES_DISCOVERED)
        
    elif tool_name == "score_websites":
        logger.info(f"📊 Updating workflow with scored businesses: {len(result_data.get('businesses', []))} scored")
        context_manager.update_workflow_state(session_id, {
            "scored_businesses": result_data.get("businesses", [])
        })
        context_manager.advance_workflow_step(session_id, WorkflowStep.WEBSITES_SCORED)
        
    elif tool_name == "generate_demo_sites":
        logger.info(f"🏗️ Updating workflow with demo businesses: {len(result_data.get('businesses', []))} demos generated")
        context_manager.update_workflow_state(session_id, {
            "demo_businesses": result_data.get("businesses", [])
        })
        context_manager.advance_workflow_step(session_id, WorkflowStep.DEMOS_GENERATED)
        
    elif tool_name == "export_data":
        logger.info(f"📋 Updating workflow with exported data")
        context_manager.update_workflow_state(session_id, {
            "exported_data": result_data
        })
        context_manager.advance_workflow_step(session_id, WorkflowStep.DATA_EXPORTED)
        
    elif tool_name == "generate_outreach":
        logger.info(f"💬 Updating workflow with outreach businesses: {len(result_data.get('businesses', []))} outreach generated")
        context_manager.update_workflow_state(session_id, {
            "outreach_businesses": result_data.get("businesses", [])
        })
        context_manager.advance_workflow_step(session_id, WorkflowStep.OUTREACH_GENERATED)
        
    elif tool_name == "confirm_parameters":
        logger.info(f"✅ Updating workflow with parameter confirmation")
        logger.info(f"🔍 Tool result for confirm_parameters: {tool_result}")
        logger.info(f"🔍 Result data: {result_data}")
        logger.info(f"🔍 Requires confirmation: {tool_result.get('requires_confirmation')}")
        
        if tool_result.get("requires_confirmation"):
            logger.info(f"✅ Setting pending confirmation for parameters")
            context_manager.set_pending_confirmation(
                session_id,
                ConfirmationType.PARAMETERS,
                result_data.get("confirmation_message", "Please confirm parameters"),
                {
                    "type": "parameter_confirmation",
                    "location": result_data.get("location"),
                    "niche": result_data.get("niche")
                }
            )
        else:
            logger.warning(f"⚠️ confirm_parameters tool did not set requires_confirmation")
    
    # Log final workflow state
    final_state = context_manager.get_or_create_workflow_state(session_id)
    logger.info(f"🔄 Final workflow state - step: {final_state.current_step}, businesses: {len(final_state.discovered_businesses)}")


def _format_tool_results_summary(tool_results: List[Dict[str, Any]]) -> str:
    """Format tool results into a user-friendly summary"""
    
    summary_parts = []
    
    for result in tool_results:
        if not result.get("success"):
            continue
            
        tool_name = result.get("tool_name")
        result_data = result.get("result", {})
        
        if tool_name == "discover_businesses":
            summary_parts.append(f"🔍 Found {result_data.get('total_found', 0)} businesses")
            
        elif tool_name == "score_websites":
            avg_score = result_data.get('average_score', 0)
            low_scorers = result_data.get('low_scorers', 0)
            summary_parts.append(f"📊 Scored websites (avg: {avg_score:.1f}/100, {low_scorers} need improvement)")
            
        elif tool_name == "generate_demo_sites":
            demo_count = result_data.get('demo_sites_created', 0)
            summary_parts.append(f"🏗️ Generated {demo_count} demo websites")
            
        elif tool_name == "export_data":
            business_count = result_data.get('business_count', 0)
            summary_parts.append(f"📊 Exported data for {business_count} businesses")
            
        elif tool_name == "generate_outreach":
            outreach_count = result_data.get('outreach_generated', 0)
            summary_parts.append(f"💬 Generated outreach for {outreach_count} businesses")
    
    return "\n".join(summary_parts) if summary_parts else ""


@router.get("/agent-status")
async def get_agent_status():
    """Get the current status of the LeadGenBuilder agent"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "capabilities": [
            "autonomous_business_discovery",
            "website_scoring_analysis", 
            "demo_site_generation",
            "data_export",
            "personalized_outreach_creation",
            "conversational_interface",
            "workflow_management",
            "confirmation_flows"
        ],
        "active_sessions": len(context_manager.workflow_states),
        "supported_tools": [
            "discover_businesses",
            "score_websites", 
            "generate_demo_sites",
            "export_data",
            "generate_outreach",
            "confirm_parameters"
        ]
    }
