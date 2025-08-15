"""
LeadGenBuilder AI Agent
Handles AI-powered message processing and tool calling for the lead generation system
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LeadGenAIAgent:
    """
    AI agent that processes user messages and determines appropriate tool calls
    
    This agent handles:
    - Natural language understanding of user requests
    - Tool selection and parameter extraction
    - Context management across conversations
    - Response generation
    """
    
    def __init__(self):
        self.conversation_contexts = {}
        self.tool_definitions = {
            "discover_businesses": {
                "description": "Search for businesses in a specific location and niche",
                "parameters": ["location", "niche", "max_businesses"]
            },
            "score_websites": {
                "description": "Evaluate website quality using Lighthouse and heuristic analysis",
                "parameters": ["businesses", "scoring_method"]
            },
            "generate_demo_sites": {
                "description": "Create demo websites for businesses",
                "parameters": ["businesses", "template_style"]
            },
            "export_data": {
                "description": "Export business and scoring data",
                "parameters": ["businesses", "format"]
            },
            "generate_outreach": {
                "description": "Generate personalized outreach messages",
                "parameters": ["businesses", "outreach_type"]
            },
            "confirm_parameters": {
                "description": "Confirm location and niche parameters with user",
                "parameters": ["location", "niche"]
            }
        }
    
    async def process_message(
        self, 
        user_message: str, 
        session_id: str, 
        message_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Process a user message and determine appropriate response and tool calls
        
        Args:
            user_message: The user's input message
            session_id: Unique session identifier
            message_history: Previous conversation messages
            
        Returns:
            Dictionary containing response content and tool calls
        """
        
        try:
            logger.info(f"🤖 AI Agent processing message for session {session_id}")
            logger.info(f"📝 User message: {user_message}")
            
            # Update conversation context
            self._update_context(session_id, user_message, message_history)
            
            # Analyze user intent
            intent = self._analyze_intent(user_message)
            logger.info(f"🎯 Detected intent: {intent}")
            
            # Generate response and tool calls based on intent
            if intent["type"] == "business_discovery":
                return await self._handle_business_discovery(intent, session_id)
            elif intent["type"] == "website_scoring":
                return await self._handle_website_scoring(intent, session_id)
            elif intent["type"] == "demo_generation":
                return await self._handle_demo_generation(intent, session_id)
            elif intent["type"] == "data_export":
                return await self._handle_data_export(intent, session_id)
            elif intent["type"] == "outreach_generation":
                return await self._handle_outreach_generation(intent, session_id)
            elif intent["type"] == "parameter_confirmation":
                return await self._handle_parameter_confirmation(intent, session_id)
            elif intent["type"] == "general_help":
                return await self._handle_general_help(intent, session_id)
            else:
                return await self._handle_unknown_intent(intent, session_id)
                
        except Exception as e:
            logger.error(f"❌ AI Agent processing failed: {e}")
            return {
                "content": f"I apologize, but I encountered an error processing your message: {str(e)}. Please try again.",
                "tool_calls": [],
                "requires_confirmation": False
            }
    
    def _update_context(self, session_id: str, user_message: str, message_history: List[Dict[str, str]]):
        """Update conversation context for the session"""
        
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = {
                "last_updated": datetime.now(),
                "message_count": 0,
                "extracted_parameters": {},
                "conversation_flow": []
            }
        
        context = self.conversation_contexts[session_id]
        context["last_updated"] = datetime.now()
        context["message_count"] += 1
        
        # Extract and store any parameters mentioned in the message
        extracted = self._extract_parameters(user_message)
        context["extracted_parameters"].update(extracted)
        
        # Track conversation flow
        context["conversation_flow"].append({
            "timestamp": datetime.now(),
            "message": user_message,
            "intent": "user_input"
        })
    
    def _analyze_intent(self, user_message: str) -> Dict[str, Any]:
        """Analyze user message to determine intent and extract parameters"""
        
        message_lower = user_message.lower().strip()
        
        # Check for business discovery intent
        if any(word in message_lower for word in ["find", "search", "discover", "look for", "businesses", "companies"]):
            return {
                "type": "business_discovery",
                "confidence": 0.9,
                "parameters": self._extract_parameters(user_message)
            }
        
        # Check for website scoring intent
        elif any(word in message_lower for word in ["score", "evaluate", "analyze", "website", "quality", "performance"]):
            return {
                "type": "website_scoring",
                "confidence": 0.8,
                "parameters": self._extract_parameters(user_message)
            }
        
        # Check for demo generation intent
        elif any(word in message_lower for word in ["demo", "create", "build", "website", "template"]):
            return {
                "type": "demo_generation",
                "confidence": 0.8,
                "parameters": self._extract_parameters(user_message)
            }
        
        # Check for data export intent
        elif any(word in message_lower for word in ["export", "download", "save", "data", "report"]):
            return {
                "type": "data_export",
                "confidence": 0.7,
                "parameters": self._extract_parameters(user_message)
            }
        
        # Check for outreach generation intent
        elif any(word in message_lower for word in ["outreach", "email", "message", "contact", "follow up"]):
            return {
                "type": "outreach_generation",
                "confidence": 0.7,
                "parameters": self._extract_parameters(user_message)
            }
        
        # Check for parameter confirmation
        elif any(word in message_lower for word in ["yes", "no", "confirm", "correct", "right", "wrong"]):
            return {
                "type": "parameter_confirmation",
                "confidence": 0.6,
                "parameters": self._extract_parameters(user_message)
            }
        
        # Check for general help
        elif any(word in message_lower for word in ["help", "what can you do", "how does this work", "explain"]):
            return {
                "type": "general_help",
                "confidence": 0.9,
                "parameters": {}
            }
        
        # Default to general conversation
        else:
            return {
                "type": "general_conversation",
                "confidence": 0.3,
                "parameters": self._extract_parameters(user_message)
            }
    
    def _extract_parameters(self, user_message: str) -> Dict[str, Any]:
        """Extract location, niche, and other parameters from user message"""
        
        parameters = {}
        message_lower = user_message.lower()
        
        # Extract location (common city names, states, etc.)
        location_keywords = ["in", "at", "near", "around", "from"]
        for keyword in location_keywords:
            if keyword in message_lower:
                # Simple extraction - in production, use NLP libraries
                parts = message_lower.split(keyword)
                if len(parts) > 1:
                    potential_location = parts[1].strip().split()[0:3]  # Take up to 3 words
                    if potential_location:
                        parameters["location"] = " ".join(potential_location).title()
                        break
        
        # Extract niche/business type
        niche_keywords = ["restaurants", "dentists", "lawyers", "plumbers", "electricians", "doctors", "shops", "services"]
        for niche in niche_keywords:
            if niche in message_lower:
                parameters["niche"] = niche
                break
        
        # Extract number of businesses
        import re
        number_match = re.search(r'(\d+)\s*(businesses?|companies?)', message_lower)
        if number_match:
            parameters["max_businesses"] = int(number_match.group(1))
        
        return parameters
    
    async def _handle_business_discovery(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle business discovery requests"""
        
        parameters = intent.get("parameters", {})
        location = parameters.get("location", "your area")
        niche = parameters.get("niche", "businesses")
        
        if not parameters.get("location") or not parameters.get("niche"):
            return {
                "content": f"I'd be happy to help you find {niche}! To get started, I need to know the location. Where would you like me to search?",
                "tool_calls": [],
                "requires_confirmation": False
            }
        
        return {
            "content": f"Great! I'll search for {niche} in {location}. Let me discover the businesses in that area for you.",
            "tool_calls": [{
                "function": {
                    "name": "discover_businesses",
                    "arguments": json.dumps({
                        "location": location,
                        "niche": niche,
                        "max_businesses": parameters.get("max_businesses", 10)
                    })
                }
            }],
            "requires_confirmation": False
        }
    
    async def _handle_website_scoring(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle website scoring requests"""
        
        return {
            "content": "I'll analyze the website quality for the discovered businesses using Lighthouse and heuristic evaluation.",
            "tool_calls": [{
                "function": {
                    "name": "score_websites",
                    "arguments": json.dumps({
                        "scoring_method": "comprehensive"
                    })
                }
            }],
            "requires_confirmation": False
        }
    
    async def _handle_demo_generation(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle demo website generation requests"""
        
        return {
            "content": "I'll create demo websites for the businesses to showcase improvement opportunities.",
            "tool_calls": [{
                "function": {
                    "name": "generate_demo_sites",
                    "arguments": json.dumps({
                        "template_style": "modern"
                    })
                }
            }],
            "requires_confirmation": False
        }
    
    async def _handle_data_export(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle data export requests"""
        
        return {
            "content": "I'll export the business and scoring data for you.",
            "tool_calls": [{
                "function": {
                    "name": "export_data",
                    "arguments": json.dumps({
                        "format": "csv"
                    })
                }
            }],
            "requires_confirmation": False
        }
    
    async def _handle_outreach_generation(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle outreach message generation requests"""
        
        return {
            "content": "I'll generate personalized outreach messages for the businesses.",
            "tool_calls": [{
                "function": {
                    "name": "generate_outreach",
                    "arguments": json.dumps({
                        "outreach_type": "email"
                    })
                }
            }],
            "requires_confirmation": False
        }
    
    async def _handle_parameter_confirmation(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle parameter confirmation requests"""
        
        return {
            "content": "I'll confirm the parameters and proceed with the workflow.",
            "tool_calls": [{
                "function": {
                    "name": "confirm_parameters",
                    "arguments": json.dumps({})
                }
            }],
            "requires_confirmation": True
        }
    
    async def _handle_general_help(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle general help requests"""
        
        help_text = """
I'm the LeadGenBuilder AI agent! I can help you with:

🔍 **Business Discovery**: Find businesses in specific locations and niches
📊 **Website Scoring**: Evaluate website quality and performance
🏗️ **Demo Generation**: Create demo websites to showcase improvements
📋 **Data Export**: Export business and scoring data
💬 **Outreach Generation**: Create personalized outreach messages

To get started, just tell me what you'd like to do! For example:
- "Find restaurants in New York"
- "Score websites for dentists in Chicago"
- "Create demo sites for local businesses"

What would you like me to help you with?
        """.strip()
        
        return {
            "content": help_text,
            "tool_calls": [],
            "requires_confirmation": False
        }
    
    async def _handle_unknown_intent(self, intent: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Handle unknown or unclear intents"""
        
        return {
            "content": "I'm not quite sure what you'd like me to do. Could you please be more specific? I can help you discover businesses, score websites, generate demos, and more. Just let me know what you need!",
            "tool_calls": [],
            "requires_confirmation": False
        }
    
    def update_context_from_tool_result(self, session_id: str, tool_name: str, tool_result: Dict[str, Any]):
        """Update AI agent context based on tool execution results"""
        
        if session_id not in self.conversation_contexts:
            return
        
        context = self.conversation_contexts[session_id]
        
        # Store tool execution results
        if "tool_results" not in context:
            context["tool_results"] = []
        
        context["tool_results"].append({
            "tool_name": tool_name,
            "result": tool_result,
            "timestamp": datetime.now()
        })
        
        # Update extracted parameters if tool provided new information
        if tool_result.get("success") and tool_result.get("result"):
            result_data = tool_result["result"]
            
            if "location" in result_data:
                context["extracted_parameters"]["location"] = result_data["location"]
            
            if "niche" in result_data:
                context["extracted_parameters"]["niche"] = result_data["niche"]
            
            if "businesses" in result_data:
                context["extracted_parameters"]["business_count"] = len(result_data["businesses"])
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get the current context for a session"""
        
        return self.conversation_contexts.get(session_id, {})
    
    def clear_session_context(self, session_id: str):
        """Clear context for a session"""
        
        if session_id in self.conversation_contexts:
            del self.conversation_contexts[session_id]
