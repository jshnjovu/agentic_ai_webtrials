"""
LeadGenBuilder AI Agent
Handles the conversational AI logic and workflow progression
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.services.leadgen_tool_executor import LeadGenToolExecutor
from src.services.leadgen_context_manager import LeadGenContextManager, WorkflowStep, ConfirmationType

logger = logging.getLogger(__name__)


class LeadGenAIAgent:
    """
    AI Agent that manages the lead generation workflow
    
    This agent handles:
    - User message processing
    - Workflow state management
    - Tool execution coordination
    - Progress tracking and updates
    """
    
    def __init__(self):
        self.tool_executor = LeadGenToolExecutor()
        self.context_manager = LeadGenContextManager()
        
    async def process_message(
        self, 
        user_message: str, 
        session_id: str,
        message_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process a user message and determine the appropriate response
        
        Args:
            user_message: The user's input message
            session_id: Session identifier
            message_history: Previous conversation messages
            
        Returns:
            Dict containing the agent's response and any required actions
        """
        try:
            logger.info(f"🤖 AI Agent processing message: {user_message[:100]}...")
            
            # Get current workflow state
            workflow_state = self.context_manager.get_or_create_workflow_state(session_id)
            
            # Check if there's a pending confirmation
            if workflow_state.pending_confirmation:
                return await self._handle_pending_confirmation(user_message, session_id, workflow_state)
            
            # Determine the current workflow step and appropriate action
            if workflow_state.current_step == WorkflowStep.INITIALIZED:
                return await self._handle_initial_message(user_message, session_id, workflow_state)
            
            elif workflow_state.current_step == WorkflowStep.PARAMETERS_CONFIRMED:
                return await self._handle_business_discovery(user_message, session_id, workflow_state)
            
            elif workflow_state.current_step == WorkflowStep.BUSINESSES_DISCOVERED:
                return await self._handle_website_scoring(user_message, session_id, workflow_state)
            
            elif workflow_state.current_step == WorkflowStep.WEBSITES_SCORED:
                return await self._handle_demo_generation(user_message, session_id, workflow_state)
            
            elif workflow_state.current_step == WorkflowStep.DEMOS_GENERATED:
                return await self._handle_data_export(user_message, session_id, workflow_state)
            
            elif workflow_state.current_step == WorkflowStep.DATA_EXPORTED:
                return await self._handle_outreach_generation(user_message, session_id, workflow_state)
            
            else:
                return await self._handle_completed_workflow(user_message, session_id, workflow_state)
                
        except Exception as e:
            logger.error(f"❌ AI Agent error: {str(e)}")
            return {
                "success": False,
                "content": f"I encountered an error: {str(e)}. Please try again.",
                "requires_confirmation": False,
                "workflow_progress": None
            }
    
    async def _handle_initial_message(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle the initial user message to extract location and niche"""
        
        # Extract location and niche from user message
        location, niche = self._extract_location_and_niche(user_message)
        
        if not location or not niche:
            return {
                "success": True,
                "content": "I need to know both the location and business type to help you. Please provide both, for example: 'Find restaurants in Austin, TX' or 'I want to find gyms in London, UK'",
                "requires_confirmation": False,
                "workflow_progress": None
            }
        
        # Update workflow state with extracted parameters
        self.context_manager.update_workflow_state(session_id, {
            "location": location,
            "niche": niche
        })
        
        # Request confirmation
        confirmation_message = f"I'll help you find {niche} businesses in {location}. Should I proceed with this search?"
        
        self.context_manager.set_pending_confirmation(
            session_id,
            ConfirmationType.PARAMETERS,
            confirmation_message,
            {
                "type": "parameter_confirmation",
                "location": location,
                "niche": niche
            }
        )
        
        return {
            "success": True,
            "content": confirmation_message,
            "requires_confirmation": True,
            "pending_action": {
                "type": "confirm_parameters",
                "location": location,
                "niche": niche
            },
            "workflow_progress": workflow_state.get_frontend_workflow_progress()
        }
    
    async def _handle_pending_confirmation(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle user response to pending confirmation"""
        
        # Check if user confirmed
        if self._is_confirmation_positive(user_message):
            # Clear pending confirmation
            self.context_manager.clear_pending_confirmation(session_id)
            
            # Advance to next step based on current state
            if workflow_state.current_step == WorkflowStep.INITIALIZED:
                self.context_manager.advance_workflow_step(session_id, WorkflowStep.PARAMETERS_CONFIRMED)
                return await self._handle_business_discovery(user_message, session_id, workflow_state)
            
            elif workflow_state.current_step == WorkflowStep.PARAMETERS_CONFIRMED:
                return await self._handle_business_discovery(user_message, session_id, workflow_state)
            
            else:
                # Continue with current step
                return await self._continue_current_step(user_message, session_id, workflow_state)
        
        else:
            # User rejected - reset workflow
            self.context_manager.clear_pending_confirmation(session_id)
            self.context_manager.reset_session(session_id)
            
            return {
                "success": True,
                "content": "No problem! Let's start over. What location and business type would you like to target?",
                "requires_confirmation": False,
                "workflow_progress": None
            }
    
    async def _handle_business_discovery(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle business discovery step"""
        
        try:
            logger.info(f"🔍 Starting business discovery for {workflow_state.niche} in {workflow_state.location}")
            
            # Execute business discovery tool
            tool_result = await self.tool_executor.execute_tool("discover_businesses", {
                "location": workflow_state.location,
                "niche": workflow_state.niche,
                "max_businesses": 10,
                "session_id": session_id
            })
            
            if tool_result.get("success"):
                businesses = tool_result.get("result", {}).get("businesses", [])
                discovered_count = len(businesses)
                
                # Update workflow state
                self.context_manager.update_workflow_state(session_id, {
                    "discovered_businesses": businesses
                })
                self.context_manager.advance_workflow_step(session_id, WorkflowStep.BUSINESSES_DISCOVERED)
                
                response_message = f"Perfect! I found {discovered_count} {workflow_state.niche} businesses in {workflow_state.location}. 🔍\n\nNow let me score their websites to identify improvement opportunities..."
                
                return {
                    "success": True,
                    "content": response_message,
                    "requires_confirmation": False,
                    "workflow_progress": self.context_manager.get_workflow_progress(session_id),
                    "tool_results": [tool_result]
                }
            
            else:
                error_msg = tool_result.get("error", "Unknown error occurred")
                return {
                    "success": False,
                    "content": f"Business discovery failed: {error_msg}. Please try again.",
                    "requires_confirmation": False,
                    "workflow_progress": workflow_state.get_frontend_workflow_progress()
                }
                
        except Exception as e:
            logger.error(f"❌ Business discovery error: {str(e)}")
            return {
                "success": False,
                "content": f"Business discovery encountered an error: {str(e)}. Please try again.",
                "requires_confirmation": False,
                "workflow_progress": workflow_state.get_frontend_workflow_progress()
            }
    
    async def _handle_website_scoring(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle website scoring step"""
        
        try:
            logger.info(f"📊 Starting website scoring for {len(workflow_state.discovered_businesses)} businesses")
            
            # Execute website scoring tool
            tool_result = await self.tool_executor.execute_tool("score_websites", {
                "businesses": workflow_state.discovered_businesses,
                "session_id": session_id
            })
            
            if tool_result.get("success"):
                scored_businesses = tool_result.get("result", {}).get("businesses", [])
                
                # Update workflow state
                self.context_manager.update_workflow_state(session_id, {
                    "scored_businesses": scored_businesses
                })
                self.context_manager.advance_workflow_step(session_id, WorkflowStep.WEBSITES_SCORED)
                
                response_message = f"Great! I've scored {len(scored_businesses)} websites. Now I'll generate demo sites to showcase improvement opportunities..."
                
                return {
                    "success": True,
                    "content": response_message,
                    "requires_confirmation": False,
                    "workflow_progress": self.context_manager.get_workflow_progress(session_id),
                    "tool_results": [tool_result]
                }
            
            else:
                error_msg = tool_result.get("error", "Unknown error occurred")
                return {
                    "success": False,
                    "content": f"Website scoring failed: {error_msg}. Please try again.",
                    "requires_confirmation": False,
                    "workflow_progress": workflow_state.get_frontend_workflow_progress()
                }
                
        except Exception as e:
            logger.error(f"❌ Website scoring error: {str(e)}")
            return {
                "success": False,
                "content": f"Website scoring encountered an error: {str(e)}. Please try again.",
                "requires_confirmation": False,
                "workflow_progress": workflow_state.get_frontend_workflow_progress()
            }
    
    async def _handle_demo_generation(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle demo site generation step"""
        
        try:
            logger.info(f"🏗️ Starting demo site generation for {len(workflow_state.scored_businesses)} businesses")
            
            # Execute demo generation tool
            tool_result = await self.tool_executor.execute_tool("generate_demo_sites", {
                "businesses": workflow_state.scored_businesses,
                "session_id": session_id
            })
            
            if tool_result.get("success"):
                demo_businesses = tool_result.get("result", {}).get("businesses", [])
                
                # Update workflow state
                self.context_manager.update_workflow_state(session_id, {
                    "demo_businesses": demo_businesses
                })
                self.context_manager.advance_workflow_step(session_id, WorkflowStep.DEMOS_GENERATED)
                
                response_message = f"Excellent! I've generated {len(demo_businesses)} demo sites. Now I'll export all the data for your records..."
                
                return {
                    "success": True,
                    "content": response_message,
                    "requires_confirmation": False,
                    "workflow_progress": self.context_manager.get_workflow_progress(session_id),
                    "tool_results": [tool_result]
                }
            
            else:
                error_msg = tool_result.get("error", "Unknown error occurred")
                return {
                    "success": False,
                    "content": f"Demo generation failed: {error_msg}. Please try again.",
                    "requires_confirmation": False,
                    "workflow_progress": workflow_state.get_frontend_workflow_progress()
                }
                
        except Exception as e:
            logger.error(f"❌ Demo generation error: {str(e)}")
            return {
                "success": False,
                "content": f"Demo generation encountered an error: {str(e)}. Please try again.",
                "requires_confirmation": False,
                "workflow_progress": workflow_state.get_frontend_workflow_progress()
            }
    
    async def _handle_data_export(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle data export step"""
        
        try:
            logger.info(f"📋 Starting data export for {len(workflow_state.discovered_businesses)} businesses")
            
            # Execute data export tool
            tool_result = await self.tool_executor.execute_tool("export_data", {
                "businesses": workflow_state.discovered_businesses,
                "scored_businesses": workflow_state.scored_businesses,
                "demo_businesses": workflow_state.demo_businesses,
                "session_id": session_id
            })
            
            if tool_result.get("success"):
                exported_data = tool_result.get("result", {})
                
                # Update workflow state
                self.context_manager.update_workflow_state(session_id, {
                    "exported_data": exported_data
                })
                self.context_manager.advance_workflow_step(session_id, WorkflowStep.DATA_EXPORTED)
                
                response_message = f"Perfect! Data exported successfully. Now I'll generate personalized outreach messages for the businesses..."
                
                return {
                    "success": True,
                    "content": response_message,
                    "requires_confirmation": False,
                    "workflow_progress": self.context_manager.get_workflow_progress(session_id),
                    "tool_results": [tool_result]
                }
            
            else:
                error_msg = tool_result.get("error", "Unknown error occurred")
                return {
                    "success": False,
                    "content": f"Data export failed: {error_msg}. Please try again.",
                    "requires_confirmation": False,
                    "workflow_progress": workflow_state.get_frontend_workflow_progress()
                }
                
        except Exception as e:
            logger.error(f"❌ Data export error: {str(e)}")
            return {
                "success": False,
                "content": f"Data export encountered an error: {str(e)}. Please try again.",
                "requires_confirmation": False,
                "workflow_progress": workflow_state.get_frontend_workflow_progress()
            }
    
    async def _handle_outreach_generation(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle outreach message generation step"""
        
        try:
            logger.info(f"💬 Starting outreach generation for {len(workflow_state.discovered_businesses)} businesses")
            
            # Execute outreach generation tool
            tool_result = await self.tool_executor.execute_tool("generate_outreach", {
                "businesses": workflow_state.discovered_businesses,
                "session_id": session_id
            })
            
            if tool_result.get("success"):
                outreach_businesses = tool_result.get("result", {}).get("businesses", [])
                
                # Update workflow state
                self.context_manager.update_workflow_state(session_id, {
                    "outreach_businesses": outreach_businesses
                })
                self.context_manager.advance_workflow_step(session_id, WorkflowStep.OUTREACH_GENERATED)
                
                response_message = f"Fantastic! I've generated outreach messages for {len(outreach_businesses)} businesses. Your workflow is now complete! 🎉"
                
                return {
                    "success": True,
                    "content": response_message,
                    "requires_confirmation": False,
                    "workflow_progress": self.context_manager.get_workflow_progress(session_id),
                    "tool_results": [tool_result]
                }
            
            else:
                error_msg = tool_result.get("error", "Unknown error occurred")
                return {
                    "success": False,
                    "content": f"Outreach generation failed: {error_msg}. Please try again.",
                    "requires_confirmation": False,
                    "workflow_progress": workflow_state.get_frontend_workflow_progress()
                }
                
        except Exception as e:
            logger.error(f"❌ Outreach generation error: {str(e)}")
            return {
                "success": False,
                "content": f"Outreach generation encountered an error: {str(e)}. Please try again.",
                "requires_confirmation": False,
                "workflow_progress": workflow_state.get_frontend_workflow_progress()
            }
    
    async def _handle_completed_workflow(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Handle messages after workflow completion"""
        
        return {
            "success": True,
            "content": "Your workflow is complete! All businesses have been discovered, websites scored, demo sites generated, data exported, and outreach messages created. Is there anything else you'd like me to help you with?",
            "requires_confirmation": False,
            "workflow_progress": workflow_state.get_frontend_workflow_progress()
        }
    
    async def _continue_current_step(
        self, 
        user_message: str, 
        session_id: str, 
        workflow_state: Any
    ) -> Dict[str, Any]:
        """Continue with the current workflow step"""
        
        # Route back to appropriate handler based on current step
        if workflow_state.current_step == WorkflowStep.BUSINESSES_DISCOVERED:
            return await self._handle_website_scoring(user_message, session_id, workflow_state)
        elif workflow_state.current_step == WorkflowStep.WEBSITES_SCORED:
            return await self._handle_demo_generation(user_message, session_id, workflow_state)
        elif workflow_state.current_step == WorkflowStep.DEMOS_GENERATED:
            return await self._handle_data_export(user_message, session_id, workflow_state)
        elif workflow_state.current_step == WorkflowStep.DATA_EXPORTED:
            return await self._handle_outreach_generation(user_message, session_id, workflow_state)
        else:
            return await self._handle_completed_workflow(user_message, session_id, workflow_state)
    
    def _extract_location_and_niche(self, message: str) -> tuple[Optional[str], Optional[str]]:
        """Extract location and business niche from user message"""
        
        message_lower = message.lower().strip()
        
        # Common business types
        business_types = [
            "gym", "restaurant", "cafe", "bar", "salon", "spa", "dentist", "doctor",
            "lawyer", "accountant", "plumber", "electrician", "real estate", "car dealer",
            "pet store", "veterinarian", "pharmacy", "bakery", "butcher", "florist"
        ]
        
        # Extract business type
        niche = None
        for business_type in business_types:
            if business_type in message_lower:
                niche = business_type
                break
        
        # Extract location (look for common location patterns)
        location = None
        
        # Look for "in [location]" pattern
        if " in " in message_lower:
            parts = message_lower.split(" in ")
            if len(parts) > 1:
                location = parts[1].strip()
        
        # Look for city, state patterns
        if not location:
            import re
            # Match patterns like "Austin, TX", "London, UK", "New York"
            location_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)(?:\s*,\s*([A-Z]{2,3}))?', message)
            if location_match:
                location = location_match.group(0)
        
        return location, niche
    
    def _is_confirmation_positive(self, message: str) -> bool:
        """Check if user message indicates positive confirmation"""
        
        message_lower = message.lower().strip()
        positive_words = ["yes", "y", "ok", "okay", "correct", "right", "confirm", "proceed", "sure", "absolutely"]
        
        return any(word in message_lower for word in positive_words)
