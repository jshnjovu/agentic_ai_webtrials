import { useState, useEffect, useCallback, useRef } from 'react';

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

interface UseWorkflowProgressOptions {
  sessionId: string | null;
  enabled?: boolean;
  pollInterval?: number; // milliseconds
  autoRefresh?: boolean;
}

interface UseWorkflowProgressReturn {
  workflowProgress: WorkflowProgress | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  lastUpdated: Date | null;
  updateProgress: (progress: WorkflowProgress) => void; // Add immediate update method
}

export function useWorkflowProgress({
  sessionId,
  enabled = true,
  pollInterval = 2000, // 2 seconds default
  autoRefresh = true
}: UseWorkflowProgressOptions): UseWorkflowProgressReturn {
  const [workflowProgress, setWorkflowProgress] = useState<WorkflowProgress | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchProgress = useCallback(async () => {
    if (!sessionId || !enabled) return;

    // Cancel previous request if still in flight
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/leadgen-chat/status?session_id=${sessionId}`, {
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.workflow_progress) {
        setWorkflowProgress(data.workflow_progress);
        setLastUpdated(new Date());
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Request was cancelled, ignore
        return;
      }
      
      console.error('Failed to fetch workflow progress:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch progress');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, enabled]);

  // Manual refresh function
  const refresh = useCallback(async () => {
    await fetchProgress();
  }, [fetchProgress]);

  // Immediate update function for instant progress updates
  const updateProgress = useCallback((progress: WorkflowProgress) => {
    setWorkflowProgress(progress);
    setLastUpdated(new Date());
    setError(null);
  }, []);

  // Set up polling
  useEffect(() => {
    if (!enabled || !sessionId || !autoRefresh) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Initial fetch
    fetchProgress();

    // Set up polling interval
    intervalRef.current = setInterval(fetchProgress, pollInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, sessionId, autoRefresh, pollInterval, fetchProgress]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Reset state when session changes
  useEffect(() => {
    setWorkflowProgress(null);
    setError(null);
    setLastUpdated(null);
  }, [sessionId]);

  return {
    workflowProgress,
    isLoading,
    error,
    refresh,
    lastUpdated,
    updateProgress
  };
}
