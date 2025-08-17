import React, { useState, useEffect, useRef } from 'react';
import Head from 'next/head';
import { 
  MessageSquare, 
  Send, 
  MapPin, 
  Building2, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Download,
  ExternalLink,
  Bot,
  User,
  Loader
} from 'lucide-react';
import { useWorkflowProgress } from '../hooks/useWorkflowProgress';
import WorkflowProgress from '../components/WorkflowProgress';
import WorkflowNotification from '../components/WorkflowNotification';
import DiscoveredBusinessesTable from '../components/DiscoveredBusinessesTable';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  requires_confirmation?: boolean;
  pending_action?: any;
  workflow_progress?: any;
  tool_results?: any[];
}



export default function LeadGenChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pendingConfirmation, setPendingConfirmation] = useState<{
    type: string;
    confirmation_message?: string;
    [key: string]: any;
  } | null>(null);
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(true);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Use the new reactive workflow progress hook
  const {
    workflowProgress,
    isLoading: progressLoading,
    error: progressError,
    refresh: refreshProgress,
    lastUpdated,
    updateProgress: updateWorkflowProgress
  } = useWorkflowProgress({
    sessionId,
    enabled: !!sessionId,
    pollInterval: 2000, // 2 seconds
    autoRefresh: isAutoRefreshEnabled
  });
  
  // Debug confirmation state changes
  useEffect(() => {
    console.log('🔍 pendingConfirmation state changed:', pendingConfirmation);
  }, [pendingConfirmation]);
  
  // Sync confirmation state with workflow progress
  useEffect(() => {
    if (workflowProgress && workflowProgress.pending_confirmation && !pendingConfirmation) {
      console.log('🔍 Syncing confirmation state from workflow progress:', workflowProgress.pending_confirmation);
      setPendingConfirmation({
        type: workflowProgress.pending_confirmation,
        confirmation_message: workflowProgress.confirmation_message
      });
    }
    
    // Clear confirmation if workflow no longer requires it
    if (pendingConfirmation && workflowProgress && !workflowProgress.pending_confirmation) {
      console.log('🔍 Clearing confirmation state - no longer required');
      setPendingConfirmation(null);
    }
  }, [workflowProgress?.pending_confirmation, pendingConfirmation, workflowProgress]);
  
  useEffect(() => {
    // Initial greeting message
    const initialMessage: ChatMessage = {
      id: '1',
      role: 'assistant',
      content: `Hello! I'm LeadGenBuilder, your autonomous business discovery agent. 🤖

I can help you:
• 🔍 Find local businesses in any niche and location
• 📊 Score their websites using professional criteria
• 🏗️ Generate improved demo websites for low performers
• 💬 Create personalized outreach messages (Email, WhatsApp, SMS)
• 📋 Export everything to CSV for your records

To get started, just tell me what location and business niche you'd like to target!

For example: "Find restaurants in Austin, TX" or "I want to find gyms in London, UK"`,
      timestamp: new Date().toISOString()
    };
    
    setMessages([initialMessage]);
  }, []);
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/v1/leadgen-chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          session_id: sessionId
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send message');
      }
      
      const data = await response.json();
      
      console.log('🔍 Backend response received:', {
        requires_confirmation: data.requires_confirmation,
        pending_action: data.pending_action,
        agent_message: data.agent_message?.substring(0, 100) + '...',
        session_id: data.session_id
      });
      
      // Update session ID if new
      if (!sessionId) {
        setSessionId(data.session_id);
      }
      
      // Add agent response
      const agentMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.agent_message,
        timestamp: new Date().toISOString(),
        requires_confirmation: data.requires_confirmation || false,
        pending_action: data.pending_action || null,
        workflow_progress: data.workflow_progress,
        tool_results: data.tool_results
      };
      
      console.log('🔍 Agent message created:', {
        requires_confirmation: agentMessage.requires_confirmation,
        pending_action: agentMessage.pending_action,
        content: agentMessage.content.substring(0, 100) + '...'
      });
      
      setMessages(prev => [...prev, agentMessage]);
      
      // Note: Workflow progress is now handled by the useWorkflowProgress hook
      // which automatically polls for updates
      
      // Handle pending confirmation - check multiple possible formats
      if (data.requires_confirmation || data.pending_action) {
        const confirmationData = data.pending_action || { type: 'confirmation_required' };
        setPendingConfirmation(confirmationData);
        console.log('🔍 Confirmation required:', { 
          requires_confirmation: data.requires_confirmation, 
          pending_action: data.pending_action,
          confirmationData
        });
      } else {
        console.log('🔍 No confirmation required, clearing pendingConfirmation');
        setPendingConfirmation(null);
      }
      
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleConfirmation = async (confirmed: boolean) => {
    if (!sessionId) return;
    
    setIsLoading(true);
    
    try {
      const response = await fetch('/api/v1/leadgen-chat/confirm', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          confirmed: confirmed
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to send confirmation');
      }
      
      const data = await response.json();
      
      // Find and update the specific message that had confirmation buttons
      setMessages(prev => prev.map(msg => {
        if (msg.requires_confirmation) {
          return {
            ...msg,
            requires_confirmation: false, // Remove confirmation from this specific message
            pending_action: null
          };
        }
        return msg;
      }));
      
      // Add confirmation response
      const confirmationMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: data.agent_message,
        timestamp: new Date().toISOString(),
        requires_confirmation: false, // Confirmation resolved
        pending_action: null,
        workflow_progress: data.workflow_progress,
        tool_results: data.tool_results
      };
      
      console.log('🔍 Confirmation message created:', {
        content: confirmationMessage.content.substring(0, 100) + '...',
        tool_results: confirmationMessage.tool_results?.length || 0
      });
      
      setMessages(prev => [...prev, confirmationMessage]);
      
      // Clear pending confirmation immediately for better UX
      setPendingConfirmation(null);
      
      // Force immediate workflow progress refresh
      if (data.workflow_progress) {
        // Update local workflow progress immediately
        // This will be reflected in the UI before the next poll
        console.log('🔍 Immediate workflow progress update:', data.workflow_progress);
        updateWorkflowProgress(data.workflow_progress);
      }
      
    } catch (error) {
      console.error('Error sending confirmation:', error);
      
      // Clear pending confirmation even on error to prevent UI getting stuck
      setPendingConfirmation(null);
      
      // Also remove confirmation buttons from messages that had them on error
      setMessages(prev => prev.map(msg => {
        if (msg.requires_confirmation) {
          return {
            ...msg,
            requires_confirmation: false,
            pending_action: null
          };
        }
        return msg;
      }));
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  const toggleAutoRefresh = () => {
    setIsAutoRefreshEnabled(!isAutoRefreshEnabled);
  };
  
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // Extract businesses from tool results
  const extractBusinessesFromResults = (toolResults: any[]): any[] => {
    const businesses: any[] = [];
    
    toolResults.forEach(result => {
      if (result.success && result.tool_name === 'discover_businesses' && result.result?.businesses) {
        businesses.push(...result.result.businesses);
      }
    });
    
    return businesses;
  };

  // Check if a message contains business discovery results
  const hasBusinessDiscovery = (message: ChatMessage): boolean => {
    return message.tool_results?.some(result => 
      result.success && 
      result.tool_name === 'discover_businesses' && 
      result.result?.businesses?.length > 0
    ) || false;
  };

  // Get business data from a message
  const getBusinessesFromMessage = (message: ChatMessage): any[] => {
    if (!message.tool_results) return [];
    return extractBusinessesFromResults(message.tool_results);
  };
  


  return (
    <>
      <Head>
        <title>LeadGenBuilder Chat - Autonomous Business Discovery</title>
        <meta name="description" content="Chat with the LeadGenBuilder AI agent" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      
      {/* Real-time Workflow Notifications */}
      <WorkflowNotification
        workflowProgress={workflowProgress}
        lastUpdated={lastUpdated}
        previousProgress={null}
      />
      
      {/* Debug information removed for cleaner UI */}

      <div className="min-h-screen bg-gray-50 flex">
        
        {/* Sidebar - Workflow Progress */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="p-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Bot className="w-5 h-5 mr-2 text-blue-500" />
              LeadGenBuilder
            </h2>
            <p className="text-sm text-gray-600 mt-1">Autonomous Agent</p>
          </div>
          
          <WorkflowProgress
            workflowProgress={workflowProgress}
            lastUpdated={lastUpdated}
            isLoading={progressLoading}
            error={progressError}
            onRefresh={refreshProgress}
            isAutoRefreshEnabled={isAutoRefreshEnabled}
            onToggleAutoRefresh={toggleAutoRefresh}
          />
        </div>
        
        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          
          {/* Chat Header */}
          <div className="bg-white border-b border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-xl font-semibold text-gray-900">Chat with LeadGenBuilder</h1>
                <p className="text-sm text-gray-600">
                  Tell me a location and business niche to get started
                </p>
                {workflowProgress && (
                  <div className="flex items-center space-x-2 mt-2">
                    <div className="flex items-center space-x-1 text-xs text-gray-500">
                      <span>Current Step:</span>
                      <span className="font-medium text-blue-600">
                        {workflowProgress.current_step.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                    {workflowProgress.progress_percentage > 0 && (
                      <div className="flex items-center space-x-1 text-xs text-gray-500">
                        <span>•</span>
                        <span>{workflowProgress.progress_percentage.toFixed(0)}% Complete</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="flex items-center space-x-3">
                {workflowProgress && (
                  <div className="flex items-center space-x-2 text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                      <span>🔍</span>
                      <span>{workflowProgress.businesses_discovered}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span>📊</span>
                      <span>{workflowProgress.businesses_scored}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <span>🏗️</span>
                      <span>{workflowProgress.demo_sites_generated}</span>
                    </div>
                  </div>
                )}
                {sessionId && (
                  <div className="text-sm text-gray-500">
                    Session: {sessionId.slice(0, 8)}...
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-2xl rounded-lg px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-white border border-gray-200 shadow-sm'
                  }`}
                >
                  <div className="flex items-start space-x-2">
                    {message.role === 'assistant' && (
                      <Bot className="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                    )}
                    {message.role === 'user' && (
                      <User className="w-5 h-5 text-blue-100 mt-0.5 flex-shrink-0" />
                    )}
                    <div className="flex-1">
                      <div className="whitespace-pre-line text-sm leading-relaxed">
                        {message.content}
                      </div>
                      
                      {/* Tool Results */}
                      {message.tool_results && message.tool_results.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {message.tool_results.map((result, index) => (
                            <div key={index} className="bg-gray-50 rounded p-2 text-xs">
                              <div className="flex items-center justify-between">
                                <span className="font-medium">
                                  {result.success ? '✅' : '❌'} {result.tool_name}
                                </span>
                                {result.result?.processing_time && (
                                  <span className="text-gray-500">
                                    {result.result.processing_time}s
                                  </span>
                                )}
                              </div>
                              {result.result?.message && (
                                <p className="mt-1 text-gray-600">{result.result.message}</p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Confirmation Buttons - Show for this message if it requires confirmation */}
                      {message.requires_confirmation && (
                        <div className="mt-3 flex space-x-2">
                          <button
                            onClick={() => handleConfirmation(true)}
                            disabled={isLoading}
                            className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium shadow-sm transition-all duration-200 flex items-center space-x-2"
                          >
                            {isLoading ? (
                              <>
                                <Loader className="w-4 h-4 animate-spin" />
                                <span>Processing...</span>
                              </>
                            ) : (
                              <>
                                <span>✅</span>
                                <span>Yes, Confirm</span>
                              </>
                            )}
                          </button>
                          <button
                            onClick={() => handleConfirmation(false)}
                            disabled={isLoading}
                            className="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 disabled:opacity-50 font-medium shadow-sm transition-all duration-200 flex items-center space-x-2"
                          >
                            {isLoading ? (
                              <>
                                <Loader className="w-4 h-4 animate-spin" />
                                <span>Processing...</span>
                              </>
                            ) : (
                              <>
                                <span>❌</span>
                                <span>No, Cancel</span>
                              </>
                            )}
                          </button>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-gray-500">
                          {formatTimestamp(message.timestamp)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <Bot className="w-5 h-5 text-blue-500" />
                    <Loader className="w-4 h-4 animate-spin text-gray-500" />
                    <span className="text-sm text-gray-600">LeadGenBuilder is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* Business Discovery Table - Single Location */}
          {sessionId && workflowProgress && workflowProgress.businesses_discovered > 0 && (
            <div className="px-4 pb-4">
              <DiscoveredBusinessesTable
                sessionId={sessionId}
                onBusinessSelect={(business) => {
                  console.log('Selected business:', business);
                  // You can add logic here to handle business selection
                }}
              />
            </div>
          )}
          
          {/* Global Confirmation Area - Removed duplicate confirmation buttons */}
          {/* Confirmation now only appears in the chat message */}
          
          {/* Input Area */}
          <div className="bg-white border-t border-gray-200 p-4">
            <div className="flex space-x-4">
              <div className="flex-1">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                  placeholder="Type your message... (e.g., 'Find restaurants in Austin, TX')"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  rows={3}
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputValue.trim() || isLoading}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Send className="w-4 h-4" />
                <span>Send</span>
              </button>
            </div>
            
            <div className="mt-2 text-xs text-gray-500">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
