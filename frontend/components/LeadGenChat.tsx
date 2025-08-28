import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  User, 
  Bot, 
  Building2, 
  Search, 
  Target, 
  CheckCircle,
  Clock,
  AlertCircle
} from 'lucide-react';

interface ChatMessage {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  metadata?: {
    action?: string;
    businessesFound?: number;
    location?: string;
    niche?: string;
    score?: number;
  };
}

interface LeadGenChatProps {
  onSendMessage?: (message: string) => void;
  onActionRequest?: (action: string, data?: any) => void;
}

export default function LeadGenChat({ 
  onSendMessage,
  onActionRequest
}: LeadGenChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Simulate AI responses based on user input - completely independent
  const simulateAIResponse = (userMessage: string) => {
    setIsTyping(true);
    
    setTimeout(() => {
      let aiResponse = '';
      let metadata = {};

      if (userMessage.toLowerCase().includes('discover') || userMessage.toLowerCase().includes('find') || userMessage.toLowerCase().includes('search')) {
        aiResponse = `I'll help you discover businesses. Please specify the location and business niche you'd like to target. For example: "Find restaurants in Austin, TX" or "Discover gyms in London, UK".`;
        metadata = { action: 'discovery_requested' };
      } else if (userMessage.toLowerCase().includes('score') || userMessage.toLowerCase().includes('analyze') || userMessage.toLowerCase().includes('website')) {
        aiResponse = `I can help you analyze website performance. First, we'll need to discover some businesses to analyze. Would you like to start with business discovery?`;
        metadata = { action: 'scoring_requested' };
      } else if (userMessage.toLowerCase().includes('demo') || userMessage.toLowerCase().includes('generate') || userMessage.toLowerCase().includes('site')) {
        aiResponse = `I can help you generate demo websites for businesses that need improvement. We'll need to discover and score businesses first. Shall we start with business discovery?`;
        metadata = { action: 'demo_generation_requested' };
      } else if (userMessage.toLowerCase().includes('status') || userMessage.toLowerCase().includes('progress') || userMessage.toLowerCase().includes('update')) {
        aiResponse = `I can check the current status of your LeadGen workflow. Let me know what you'd like to check or if you'd like to start a new discovery process.`;
        metadata = { action: 'status_requested' };
      } else {
        aiResponse = `I'm your LeadGen AI assistant! I can help you with business discovery, website scoring, demo site generation, and outreach campaigns. What would you like to start with?`;
      }

      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'ai',
        content: aiResponse,
        timestamp: new Date(),
        status: 'sent',
        metadata
      };

      setMessages(prev => [...prev, newMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date(),
      status: 'sent'
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    
    // Call parent callback if provided
    if (onSendMessage) {
      onSendMessage(inputMessage);
    }

    // Simulate AI response
    simulateAIResponse(inputMessage);
  };

  const handleQuickAction = (action: string) => {
    const actionMessage = `Quick action: ${action}`;
    setInputMessage(actionMessage);
    
    // Trigger the action through callback
    if (onActionRequest) {
      onActionRequest(action);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'user':
        return <User className="w-6 h-6 text-blue-600" />;
      case 'ai':
        return <Bot className="w-6 h-6 text-green-600" />;
      case 'system':
        return <Building2 className="w-6 h-6 text-gray-600" />;
      default:
        return <User className="w-6 h-6 text-gray-600" />;
    }
  };

  const getMessageBubbleClass = (type: string) => {
    switch (type) {
      case 'user':
        return 'bg-blue-600 text-white ml-auto';
      case 'ai':
        return 'bg-gray-100 text-gray-900';
      case 'system':
        return 'bg-yellow-100 text-yellow-800 mx-auto';
      default:
        return 'bg-gray-100 text-gray-900';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex items-start space-x-3 max-w-xs lg:max-w-md ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              <div className="flex-shrink-0">
                {getMessageIcon(message.type)}
              </div>
              <div className={`rounded-lg px-4 py-2 ${getMessageBubbleClass(message.type)}`}>
                <p className="text-sm">{message.content}</p>
                {message.metadata && (
                  <div className="mt-2 pt-2 border-t border-opacity-20 border-current">
                    {message.metadata.action === 'discovery_requested' && (
                      <div className="flex items-center space-x-2 text-xs opacity-80">
                        <Search className="w-3 h-3" />
                        <span>Ready to start business discovery</span>
                      </div>
                    )}
                    {message.metadata.action === 'scoring_requested' && (
                      <div className="flex items-center space-x-2 text-xs opacity-80">
                        <Target className="w-3 h-3" />
                        <span>Ready to analyze websites</span>
                      </div>
                    )}
                    {message.metadata.action === 'demo_generation_requested' && (
                      <div className="flex items-center space-x-2 text-xs opacity-80">
                        <Building2 className="w-3 h-3" />
                        <span>Ready to generate demo sites</span>
                      </div>
                    )}
                    {message.metadata.action === 'status_requested' && (
                      <div className="flex items-center space-x-2 text-xs opacity-80">
                        <CheckCircle className="w-3 h-3" />
                        <span>Ready to check status</span>
                      </div>
                    )}
                  </div>
                )}
                <div className={`text-xs mt-1 ${message.type === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-3 max-w-xs lg:max-w-md">
              <div className="flex-shrink-0">
                <Bot className="w-6 h-6 text-green-600" />
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex items-center space-x-1">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-xs text-gray-500 ml-2">AI is typing...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 p-4 pb-10 bg-white">
        <div className="flex items-center space-x-3">
          <div className="flex-1">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              rows={2}
            />
          </div>
          <button
            onClick={handleSendMessage}
            disabled={!inputMessage.trim() || isTyping}
            className="w-10 h-10 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
            </svg>
          </button>
        </div>
        
        {/* Quick Actions */}
        <div className="mt-3 flex flex-wrap gap-1.5">
          <button
            onClick={() => handleQuickAction('discover_businesses')}
            className="px-2.5 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors whitespace-nowrap"
          >
            🔍 Discover
          </button>
          <button
            onClick={() => handleQuickAction('analyze_scores')}
            className="px-2.5 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200 transition-colors whitespace-nowrap"
          >
            📊 Analyze
          </button>
          <button
            onClick={() => handleQuickAction('generate_demos')}
            className="px-2.5 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors whitespace-nowrap"
          >
            🚀 Generate
          </button>
          <button
            onClick={() => handleQuickAction('check_status')}
            className="px-2.5 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors whitespace-nowrap"
          >
            📈 Status
          </button>
        </div>
      </div>
    </div>
  );
} 