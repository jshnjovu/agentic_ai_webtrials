import React, { useState } from 'react';
import Head from 'next/head';
import { 
  MapPin, 
  Building2, 
  Search, 
  Target, 
  FileSpreadsheet, 
  CheckCircle,
  ChevronRight,
  X,
  Bot,
  MessageSquare
} from 'lucide-react';
import LeadGenSequentialResults from '../components/LeadGenSequentialResults';
import LeadGenChat from '../components/LeadGenChat';
import { Business } from '../hooks/useBusinessData';

export default function UnifiedLeadGenPage() {
  const [location, setLocation] = useState('');
  const [niche, setNiche] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [processingLogs, setProcessingLogs] = useState<string[]>([]);
  const [isAIAssistantOpen, setIsAIAssistantOpen] = useState(false);

  const steps = [
    { id: 0, name: 'Input Parameters', description: 'Enter location and niche' },
    { id: 1, name: 'Batch Processing', description: 'Discover businesses and score websites' },
    { id: 2, name: 'Processing...', description: 'Analyzing website performance' },
    { id: 3, name: 'Review Results', description: 'Analyze scoring results' },
    { id: 4, name: 'Generate Demos', description: 'Create improved websites (Coming Soon)' },
    { id: 5, name: 'Deploy Sites', description: 'Host demo websites (Coming Soon)' },
    { id: 6, name: 'Create Outreach', description: 'Generate messages (Coming Soon)' }
  ];

  const addLog = (message: string) => {
    setProcessingLogs(prev => [...prev, `${new Date().toLocaleTimeString()}: ${message}`]);
  };

  const handleStart = async () => {
    if (!location.trim() || !niche.trim()) {
      alert('Please enter both location and niche');
      return;
    }

    setIsProcessing(true);
    setCurrentStep(1);
    setProcessingLogs([]);
    setBusinesses([]);

    try {
      addLog(`Starting LeadGenBuilder for ${niche} businesses in ${location}`);
      
      // Use new batch API that combines discovery and scoring
      addLog('🚀 Starting batch discovery and scoring...');
      setCurrentStep(2); // Show processing step
      
      const batchResponse = await fetch('/api/v1/leadgen/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          location, 
          niche, 
          max_businesses: 2,
          enable_scoring: true 
        })
      });
      
      if (!batchResponse.ok) {
        throw new Error('Failed to process batch request');
      }
      
      const batchResult = await batchResponse.json();
      addLog(`✅ Batch processing completed:`);
      addLog(`   - Found ${batchResult.discovery_count} businesses`);
      addLog(`   - Successfully scored ${batchResult.successful_scores} websites`);
      addLog(`   - Failed scores: ${batchResult.failed_scores}`);
      addLog(`   - No websites: ${batchResult.no_websites}`);
      
      setCurrentStep(3); // Set to Review Results step
      setBusinesses(batchResult.businesses);
      addLog('🎯 Website scoring completed - ready for demo site generation');
      addLog('🎉 LeadGenBuilder scoring phase completed successfully!');

    } catch (error) {
      console.error('Error:', error);
      addLog(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text);
    alert(`${type} copied to clipboard!`);
  };

  return (
    <>
      <Head>
        <title>LeadGenBuilder - Autonomous Business Discovery Agent</title>
        <meta name="description" content="Discover local businesses, score websites, and generate outreach" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Main Content Area */}
        <div className={`transition-all duration-300 ${isAIAssistantOpen ? 'mr-96' : 'mr-0'}`}>
          <div className="py-8">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
              
              {/* Header */}
              <div className="text-center mb-8">
                <h1 className="text-4xl font-bold text-gray-900 mb-4">
                  🤖 LeadGenBuilder Agent
                </h1>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                  Autonomous agent that discovers local businesses, scores their websites, 
                  and identifies opportunities for improvement through demo site generation.
                </p>
              </div>

              {/* Progress Steps */}
              <div className="mb-8">
                <div className="flex justify-between items-center">
                  {steps.map((step, index) => (
                    <div key={step.id} className="flex flex-col items-center">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                        currentStep > step.id 
                          ? 'bg-green-500 text-white' 
                          : currentStep === step.id 
                            ? 'bg-blue-500 text-white' 
                            : 'bg-gray-300 text-gray-600'
                      }`}>
                        {currentStep > step.id ? <CheckCircle className="w-5 h-5" /> : step.id + 1}
                      </div>
                      <span className="text-xs mt-2 text-center font-medium">{step.name}</span>
                      <span className="text-xs text-gray-500 text-center">{step.description}</span>
                      {index < steps.length - 1 && (
                        <ChevronRight className="w-4 h-4 text-gray-400 mt-1" />
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Input Form */}
              {currentStep === 0 && (
                <div className="bg-white rounded-lg shadow p-6 mb-8">
                  <h2 className="text-2xl font-semibold mb-6 flex items-center">
                    <Target className="w-6 h-6 mr-2 text-blue-500" />
                    Target Parameters
                  </h2>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <MapPin className="w-4 h-4 inline mr-1" />
                        Location (City, State/Country)
                      </label>
                      <input
                        type="text"
                        value={location}
                        onChange={(e) => setLocation(e.target.value)}
                        placeholder="e.g., London, UK or Austin, TX"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isProcessing}
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <Building2 className="w-4 h-4 inline mr-1" />
                        Business Niche/Industry
                      </label>
                      <input
                        type="text"
                        value={niche}
                        onChange={(e) => setNiche(e.target.value)}
                        placeholder="e.g., restaurants, gyms, dental practices"
                        className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={isProcessing}
                      />
                    </div>
                  </div>

                  <button
                    onClick={handleStart}
                    disabled={isProcessing || !location.trim() || !niche.trim()}
                    className="mt-6 w-full bg-blue-600 text-white py-3 px-6 rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
                  >
                    {isProcessing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Processing...
                      </>
                    ) : (
                      <>
                        <Search className="w-5 h-5 mr-2" />
                        Start LeadGenBuilder Process
                      </>
                    )}
                  </button>
                </div>
              )}

              {/* Processing Logs */}
              {processingLogs.length > 0 && (
                <div className="bg-black text-green-400 rounded-lg p-4 mb-8 font-mono text-sm max-h-60 overflow-y-auto">
                  {processingLogs.map((log, index) => (
                    <div key={index}>{log}</div>
                  ))}
                </div>
              )}

              {/* Sequential Results */}
              {businesses.length > 0 && (
                <LeadGenSequentialResults 
                  businesses={businesses}
                  location={location}
                  niche={niche}
                />
              )}

              {/* Export Data Section */}
              {businesses.length > 0 && (
                <div className="bg-white rounded-lg shadow p-6 text-center mt-8">
                  <h3 className="text-lg font-medium mb-4 flex items-center justify-center">
                    <FileSpreadsheet className="w-5 h-5 mr-2" />
                    Export Scored Business Data
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Download the complete dataset including business information and website scores
                  </p>
                  <button
                    onClick={() => {
                      const csvContent = [
                        ['Business Name', 'Contact Name', 'Email', 'Phone', 'Website', 'Address', 'Overall Score', 'Performance', 'Accessibility', 'SEO', 'Best Practices', 'CRO', 'Top Issues'].join(','),
                        ...businesses.map(b => [
                          b.business_name,
                          b.contact_name || '',
                          b.email || '',
                          b.phone || '',
                          b.website || '',
                          b.address,
                          b.score_overall,
                          b.score_perf,
                          b.score_access,
                          b.score_seo,
                          b.score_best_practices,
                          b.score_cro,
                          (b.top_issues || []).join('; ')
                        ].map(field => `"${field}"`).join(','))
                      ].join('\n');
                      
                      const blob = new Blob([csvContent], { type: 'text/csv' });
                      const url = window.URL.createObjectURL(blob);
                      const link = document.createElement('a');
                      link.href = url;
                      link.download = `leadgen-${location.replace(/\s+/g, '-')}-${niche.replace(/\s+/g, '-')}-${new Date().toISOString().split('T')[0]}.csv`;
                      link.click();
                      window.URL.revokeObjectURL(url);
                    }}
                    className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 flex items-center mx-auto"
                  >
                    <FileSpreadsheet className="w-5 h-5 mr-2" />
                    Download CSV Report
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* AI Assistant Sidebar */}
        <div className={`fixed top-0 right-0 h-full w-96 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out ${
          isAIAssistantOpen ? 'translate-x-0' : 'translate-x-full'
        }`}>
          {/* Sidebar Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-6 py-4 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Bot className="w-6 h-6 mr-3" />
                <h3 className="text-lg font-semibold">AI Assistant</h3>
              </div>
              <button
                onClick={() => setIsAIAssistantOpen(false)}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Chat Interface */}
          <div className="h-full flex flex-col">
            <LeadGenChat
              onSendMessage={(message) => {
                console.log('User message:', message);
                // In a real implementation, this would send the message to the backend
              }}
              onActionRequest={(action, data) => {
                console.log('Action requested:', action, data);
                // Handle actions from the chat to affect the main workflow
                switch (action) {
                  case 'discover_businesses':
                    // Chat can trigger business discovery
                    console.log('Chat requested business discovery');
                    break;
                  case 'analyze_scores':
                    // Chat can trigger website scoring
                    console.log('Chat requested website scoring');
                    break;
                  case 'generate_demos':
                    // Chat can trigger demo generation
                    console.log('Chat requested demo generation');
                    break;
                  case 'check_status':
                    // Chat can check workflow status
                    console.log('Chat requested status check');
                    break;
                  default:
                    console.log('Unknown action:', action);
                }
              }}
            />
          </div>
        </div>

        {/* AI Assistant Toggle Button */}
        <button
          onClick={() => setIsAIAssistantOpen(!isAIAssistantOpen)}
          className={`fixed bottom-32 right-6 z-40 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 ${
            isAIAssistantOpen ? 'right-6' : 'right-6'
          }`}
          title="Toggle AI Assistant"
        >
          <MessageSquare className="w-6 h-6" />
        </button>
      </div>
    </>
  );
}
