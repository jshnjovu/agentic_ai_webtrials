import React from 'react';
import { 
  MapPin, 
  Building2, 
  CheckCircle, 
  AlertCircle, 
  Clock,
  Download,
  ExternalLink,
  Bot,
  RefreshCw,
  Play,
  Pause
} from 'lucide-react';

// Import the WorkflowProgress type from the hook
interface WorkflowProgress {
  current_step: string;
  progress_percentage: number;
  location?: string;
  niche?: string;
  businesses_discovered: number;
  businesses_scored: number;
  demo_sites_generated: number;
  has_exported_data: boolean;
  has_outreach: boolean;
  pending_confirmation?: string;
  confirmation_message?: string;
  started_at?: string;
  last_updated?: string;
  total_time_seconds?: number;
  errors?: string[];
  warnings?: string[];
}

interface WorkflowProgressProps {
  workflowProgress: WorkflowProgress | null;
  lastUpdated: Date | null;
  isLoading: boolean;
  error: string | null;
  onRefresh: () => void;
  isAutoRefreshEnabled: boolean;
  onToggleAutoRefresh: () => void;
}

const WORKFLOW_STEPS = [
  { key: 'INITIAL', label: 'Getting Started', icon: '🚀', description: 'Initializing workflow' },
  { key: 'PARAMETERS_CONFIRMED', label: 'Parameters Confirmed', icon: '✅', description: 'Location and niche confirmed' },
  { key: 'BUSINESSES_DISCOVERED', label: 'Businesses Discovered', icon: '🔍', description: 'Finding local businesses' },
  { key: 'WEBSITES_SCORED', label: 'Websites Scored', icon: '📊', description: 'Analyzing website performance' },
  { key: 'DEMOS_GENERATED', label: 'Demo Sites Generated', icon: '🏗️', description: 'Creating improvement demos' },
  { key: 'DATA_EXPORTED', label: 'Data Exported', icon: '📋', description: 'Exporting business data' },
  { key: 'OUTREACH_GENERATED', label: 'Outreach Created', icon: '💬', description: 'Generating outreach messages' },
  { key: 'COMPLETED', label: 'Workflow Complete', icon: '🎉', description: 'All tasks completed' }
];

export default function WorkflowProgress({
  workflowProgress,
  lastUpdated,
  isLoading,
  error,
  onRefresh,
  isAutoRefreshEnabled,
  onToggleAutoRefresh
}: WorkflowProgressProps) {
  if (!workflowProgress) {
    return (
      <div className="p-4 text-center text-gray-500">
        <Bot className="w-8 h-8 mx-auto mb-2 text-gray-400" />
        <p>No workflow in progress</p>
        <p className="text-sm">Start a conversation to see progress</p>
      </div>
    );
  }

  const currentStepIndex = WORKFLOW_STEPS.findIndex(step => step.key === workflowProgress.current_step);
  const progressPercentage = workflowProgress.progress_percentage || 0;

  // Intelligent step determination based on actual data
  const getIntelligentCurrentStep = () => {
    // If businesses are discovered but not scored, move to scoring step
    if (workflowProgress.businesses_discovered > 0 && workflowProgress.businesses_scored === 0) {
      return 'WEBSITES_SCORED';
    }
    
    // If businesses are scored but no demos generated, move to demo generation step
    if (workflowProgress.businesses_scored > 0 && workflowProgress.demo_sites_generated === 0) {
      return 'DEMOS_GENERATED';
    }
    
    // If demos are generated but no export, move to export step
    if (workflowProgress.demo_sites_generated > 0 && !workflowProgress.has_exported_data) {
      return 'DATA_EXPORTED';
    }
    
    // If export is done but no outreach, move to outreach step
    if (workflowProgress.has_exported_data && !workflowProgress.has_outreach) {
      return 'OUTREACH_GENERATED';
    }
    
    // If everything is done, mark as completed
    if (workflowProgress.has_exported_data && workflowProgress.has_outreach) {
      return 'COMPLETED';
    }
    
    // Default to the backend-provided step
    return workflowProgress.current_step;
  };

  const intelligentCurrentStep = getIntelligentCurrentStep();
  const intelligentCurrentStepIndex = WORKFLOW_STEPS.findIndex(step => step.key === intelligentCurrentStep);
  
  // Calculate intelligent progress percentage
  const getIntelligentProgressPercentage = () => {
    if (intelligentCurrentStepIndex === -1) return 0;
    
    // Calculate progress based on completed steps
    const totalSteps = WORKFLOW_STEPS.length;
    const completedSteps = intelligentCurrentStepIndex;
    
    // Add partial progress for current step
    let currentStepProgress = 0;
    if (intelligentCurrentStep === 'WEBSITES_SCORED' && workflowProgress.businesses_discovered > 0) {
      // If we have businesses discovered, we're ready to start scoring
      currentStepProgress = 0.5;
    } else if (intelligentCurrentStep === 'DEMOS_GENERATED' && workflowProgress.businesses_scored > 0) {
      // If we have businesses scored, we're ready to start demo generation
      currentStepProgress = 0.5;
    }
    
    return Math.round(((completedSteps + currentStepProgress) / totalSteps) * 100);
  };

  const intelligentProgressPercentage = getIntelligentProgressPercentage();

  const getStepIcon = (stepKey: string) => {
    const step = WORKFLOW_STEPS.find(s => s.key === stepKey);
    return step?.icon || '⏳';
  };

  const getStepLabel = (stepKey: string) => {
    const step = WORKFLOW_STEPS.find(s => s.key === stepKey);
    return step?.label || stepKey.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getStepDescription = (stepKey: string) => {
    const step = WORKFLOW_STEPS.find(s => s.key === stepKey);
    return step?.description || 'Processing...';
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500';
    if (percentage >= 50) return 'bg-blue-500';
    if (percentage >= 25) return 'bg-yellow-500';
    return 'bg-gray-300';
  };

  return (
    <div className="p-4 flex-1 space-y-6">
      {/* Header with refresh controls */}
      <div className="flex items-center justify-between">
        <h3 className="font-medium text-gray-900">Workflow Progress</h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={onToggleAutoRefresh}
            className={`p-1 rounded ${isAutoRefreshEnabled ? 'text-blue-600' : 'text-gray-400'}`}
            title={isAutoRefreshEnabled ? 'Disable auto-refresh' : 'Enable auto-refresh'}
          >
            {isAutoRefreshEnabled ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className={`p-1 rounded text-gray-500 hover:text-gray-700 disabled:opacity-50 ${
              isLoading ? 'animate-spin' : ''
            }`}
            title="Refresh progress"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div className="bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ease-out ${getProgressColor(intelligentProgressPercentage)}`}
            style={{ width: `${intelligentProgressPercentage}%` }}
          ></div>
        </div>
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">
            {intelligentProgressPercentage.toFixed(0)}% Complete
          </span>
          {lastUpdated && (
            <span className="text-gray-500">
              Updated {lastUpdated.toLocaleTimeString()}
            </span>
          )}
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <span className="text-sm text-red-700">Error: {error}</span>
          </div>
        </div>
      )}

      {/* Target Parameters */}
      {workflowProgress.location && workflowProgress.niche && (
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Target Parameters</h4>
          <div className="space-y-2 text-sm">
            <div className="flex items-center p-2 bg-blue-50 rounded-lg">
              <MapPin className="w-4 h-4 mr-2 text-blue-500" />
              <span className="font-medium">{workflowProgress.location}</span>
            </div>
            <div className="flex items-center p-2 bg-green-50 rounded-lg">
              <Building2 className="w-4 h-4 mr-2 text-green-500" />
              <span className="font-medium">{workflowProgress.niche}</span>
            </div>
          </div>
        </div>
      )}

      {/* Step-by-Step Progress */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900">Workflow Steps</h4>
        <div className="space-y-2">
          {WORKFLOW_STEPS.map((step, index) => {
            const isCompleted = index < intelligentCurrentStepIndex;
            const isCurrent = index === intelligentCurrentStepIndex;
            const isPending = index > intelligentCurrentStepIndex;
            
            return (
              <div
                key={step.key}
                className={`flex items-center p-3 rounded-lg border transition-all duration-200 ${
                  isCompleted 
                    ? 'bg-green-50 border-green-200' 
                    : isCurrent 
                    ? 'bg-blue-50 border-blue-200 shadow-sm' 
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-3 ${
                  isCompleted 
                    ? 'bg-green-500 text-white' 
                    : isCurrent 
                    ? 'bg-blue-500 text-white' 
                    : 'bg-gray-300 text-gray-600'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="w-4 h-4" />
                  ) : isCurrent ? (
                    <span className="text-sm font-medium">
                      {intelligentCurrentStep === workflowProgress.current_step ? step.icon : '🎯'}
                    </span>
                  ) : (
                    <span className="text-sm font-medium">{index + 1}</span>
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className={`font-medium ${
                      isCurrent ? 'text-blue-900' : isCompleted ? 'text-green-900' : 'text-gray-700'
                    }`}>
                      {step.label}
                    </span>
                    {isCurrent && intelligentCurrentStep !== workflowProgress.current_step && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        🎯 Auto-detected
                      </span>
                    )}
                  </div>
                  <p className={`text-sm ${
                    isCurrent ? 'text-blue-700' : isCompleted ? 'text-green-700' : 'text-gray-500'
                  }`}>
                    {step.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Results Summary */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900">Results Summary</h4>
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Businesses Found</span>
              <span className="font-semibold text-gray-900">{workflowProgress.businesses_discovered}</span>
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Websites Scored</span>
              <span className="font-semibold text-gray-900">{workflowProgress.businesses_scored}</span>
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Demo Sites</span>
              <span className="font-semibold text-gray-900">{workflowProgress.demo_sites_generated}</span>
            </div>
          </div>
          <div className="bg-gray-50 p-3 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Data Exported</span>
              <span className="font-semibold text-gray-900">
                {workflowProgress.has_exported_data ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-50 p-3 rounded-lg">
          <div className="flex items-center justify-between">
            <span className="text-gray-600">Outreach Ready</span>
            <span className="font-semibold text-gray-900">
              {workflowProgress.has_outreach ? 'Yes' : 'No'}
            </span>
          </div>
        </div>
      </div>

      {/* Timing Information */}
      {workflowProgress.started_at && (
        <div className="space-y-2 text-sm text-gray-600">
          <div className="flex items-center justify-between">
            <span>Started</span>
            <span>{new Date(workflowProgress.started_at).toLocaleTimeString()}</span>
          </div>
          {workflowProgress.total_time_seconds && (
            <div className="flex items-center justify-between">
              <span>Total Time</span>
              <span className="flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                {formatDuration(workflowProgress.total_time_seconds)}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Warnings */}
      {workflowProgress.warnings && workflowProgress.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-4 h-4 text-yellow-600" />
            <span className="text-sm font-medium text-yellow-800">Warnings</span>
          </div>
          <div className="space-y-1">
            {workflowProgress.warnings.slice(-3).map((warning: string, index: number) => (
              <div key={index} className="text-xs text-yellow-700">
                {warning}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
