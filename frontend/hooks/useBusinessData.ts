import { useState, useEffect, useCallback, useRef } from 'react';

export interface Business {
  business_name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  website?: string;
  address: string;
  postcode?: string;
  rating?: number;
  review_count?: number;
  categories?: string[];
  price_level?: number;
  place_id?: string;
  source?: string;
  // Website scoring properties
  score_overall?: number;
  score_perf?: number;
  score_access?: number;
  score_seo?: number;
  score_trust?: number;
  score_cro?: number;
  score_category?: string;
  demo_eligible?: boolean;
  demo_priority?: string;
  top_issues?: string[];
  // Demo generation properties
  demo_status?: string;
  demo_generated_at?: string;
  demo_skip_reason?: string;
  demo_error?: string;
  generated_site_url?: string;
  // Website score details including opportunities
  website_score?: {
    opportunities?: Array<{
      title: string;
      description: string;
      potentialSavings: number;
      unit: string;
    }>;
  };
}

interface BusinessDataResponse {
  success: boolean;
  session_id: string;
  businesses: Business[];
  total_count: number;
  location?: string;
  niche?: string;
  discovered_at?: string;
  error?: string;
}

interface UseBusinessDataOptions {
  sessionId: string | null;
  enabled?: boolean;
  pollInterval?: number;
  autoRefresh?: boolean;
}

interface UseBusinessDataReturn {
  businesses: Business[];
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  lastUpdated: Date | null;
  totalCount: number;
  location?: string;
  niche?: string;
  workflowProgress?: any; // Add workflow progress for discovery logs
}

export function useBusinessData({
  sessionId,
  enabled = true,
  pollInterval = 5000, // 5 seconds default
  autoRefresh = true
}: UseBusinessDataOptions): UseBusinessDataReturn {
  
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [location, setLocation] = useState<string | undefined>();
  const [niche, setNiche] = useState<string | undefined>();
  const [workflowProgress, setWorkflowProgress] = useState<any>(null);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const fetchBusinessData = useCallback(async () => {
    if (!sessionId || !enabled) return;

    // Cancel previous request if still in flight
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    abortControllerRef.current = new AbortController();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/v1/leadgen-chat/businesses?session_id=${sessionId}`, {
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: BusinessDataResponse = await response.json();
      
      if (data.success) {
        setBusinesses(data.businesses);
        setTotalCount(data.total_count);
        setLocation(data.location);
        setNiche(data.niche);
        setLastUpdated(new Date());
        
        // Also fetch workflow progress for discovery logs
        try {
          const progressResponse = await fetch(`/api/v1/leadgen-chat/status/${sessionId}`);
          if (progressResponse.ok) {
            const progressData = await progressResponse.json();
            setWorkflowProgress(progressData.workflow_progress);
          }
        } catch (progressErr) {
          // Ignore progress fetch errors
          console.warn('Failed to fetch workflow progress:', progressErr);
        }
      } else {
        throw new Error(data.error || 'Failed to fetch business data');
      }
    } catch (err) {
      if (err instanceof Error && err.name === 'AbortError') {
        // Request was cancelled, ignore
        return;
      }
      
      console.error('Failed to fetch business data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch business data');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, enabled]);

  // Manual refresh function
  const refresh = useCallback(async () => {
    await fetchBusinessData();
  }, [fetchBusinessData]);

  // Set up polling
  useEffect(() => {
    if (!enabled || !sessionId) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    // Initial fetch
    fetchBusinessData();

    // Set up polling interval
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchBusinessData, pollInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [sessionId, enabled, autoRefresh, pollInterval, fetchBusinessData]);

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
    setBusinesses([]);
    setError(null);
    setLastUpdated(null);
    setTotalCount(0);
    setLocation(undefined);
    setNiche(undefined);
    setWorkflowProgress(null);
  }, [sessionId]);

  return {
    businesses,
    isLoading,
    error,
    refresh,
    lastUpdated,
    totalCount,
    location,
    niche,
    workflowProgress
  };
}
