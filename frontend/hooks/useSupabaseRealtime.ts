import { useEffect, useState, useCallback, useRef } from 'react'
import { supabase, TABLES, CHANNELS } from '../lib/supabase'
import type { ProcessingRun, Business, WebsiteScore } from '../lib/supabase'

interface UseRealtimeOptions {
  table: keyof typeof TABLES
  filter?: string
  event?: 'INSERT' | 'UPDATE' | 'DELETE' | '*'
}

interface RealtimeData<T> {
  data: T[]
  loading: boolean
  error: string | null
  lastUpdated: Date | null
  refresh: () => Promise<void>
  subscribe: () => Promise<void>
  unsubscribe: () => Promise<void>
}

export function useSupabaseRealtime<T>(
  options: UseRealtimeOptions,
  initialData: T[] = []
): RealtimeData<T> {
  const [data, setData] = useState<T[]>(initialData)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  
  const channelRef = useRef<any>(null)
  const isSubscribed = useRef(false)

  const handleRealtimeUpdate = useCallback((payload: any) => {
    console.log(`🔄 Real-time update received for ${options.table}:`, payload)
    
    if (payload.eventType === 'INSERT') {
      setData(prev => [...prev, payload.new])
    } else if (payload.eventType === 'UPDATE') {
      setData(prev => prev.map(item => 
        (item as any).id === payload.new.id ? payload.new : item
      ))
    } else if (payload.eventType === 'DELETE') {
      setData(prev => prev.filter(item => (item as any).id !== payload.old.id)
      )
    }
    
    setLastUpdated(new Date())
  }, [options.table])

  const subscribe = useCallback(async () => {
    if (isSubscribed.current) return

    try {
      setLoading(true)
      setError(null)

      const channel = supabase
        .channel(`${CHANNELS.WORKFLOW_PROGRESS}-${options.table}`)
        .on(
          'postgres_changes' as any,
          {
            event: options.event || '*',
            schema: 'public',
            table: TABLES[options.table],
            filter: options.filter
          },
          handleRealtimeUpdate
        )
        .subscribe((status) => {
          console.log(`📡 Subscription status for ${options.table}:`, status)
          
          if (status === 'SUBSCRIBED') {
            isSubscribed.current = true
            setLoading(false)
          } else if (status === 'CHANNEL_ERROR') {
            setError('Failed to subscribe to real-time updates')
            setLoading(false)
          }
        })

      channelRef.current = channel
      
    } catch (err) {
      console.error('Error subscribing to real-time updates:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
      setLoading(false)
    }
  }, [options.table, options.event, options.filter, handleRealtimeUpdate])

  const unsubscribe = useCallback(async () => {
    if (channelRef.current && isSubscribed.current) {
      try {
        await supabase.removeChannel(channelRef.current)
        isSubscribed.current = false
        channelRef.current = null
        console.log(`🔌 Unsubscribed from ${options.table} real-time updates`)
      } catch (err) {
        console.error('Error unsubscribing:', err)
      }
    }
  }, [options.table])

  useEffect(() => {
    subscribe()
    
    return () => {
      unsubscribe()
    }
  }, [subscribe, unsubscribe])

  const refresh = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      
      // Fetch fresh data from the table
      const { data: freshData, error: fetchError } = await supabase
        .from(TABLES[options.table])
        .select('*')
        .order('created_at', { ascending: false })
      
      if (fetchError) throw fetchError
      
      setData(freshData || [])
      setLastUpdated(new Date())
      
    } catch (err) {
      console.error('Error refreshing data:', err)
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [options.table])

  return {
    data,
    loading,
    error,
    lastUpdated,
    refresh,
    subscribe,
    unsubscribe
  }
}

// Specialized hooks for specific use cases
export function useWorkflowProgress(runId?: string) {
  const options: UseRealtimeOptions = {
    table: 'PROCESSING_RUNS',
    event: 'UPDATE',
    filter: runId ? `id=eq.${runId}` : undefined
  }
  
  return useSupabaseRealtime<ProcessingRun>(options)
}

export function useBusinessDiscovery(runId?: string) {
  const options: UseRealtimeOptions = {
    table: 'BUSINESSES',
    event: 'INSERT',
    filter: runId ? `processing_run_id=eq.${runId}` : undefined
  }
  
  return useSupabaseRealtime<Business>(options)
}

export function useWebsiteScoring(businessId?: string) {
  const options: UseRealtimeOptions = {
    table: 'WEBSITE_SCORES',
    event: 'INSERT',
    filter: businessId ? `business_id=eq.${businessId}` : undefined
  }
  
  return useSupabaseRealtime<WebsiteScore>(options)
}

export function useProcessingRunStatus(runId: string) {
  const [status, setStatus] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!runId) return

    const fetchStatus = async () => {
      try {
        setLoading(true)
        const { data, error: fetchError } = await supabase
          .from(TABLES.PROCESSING_RUNS)
          .select('status, current_step, total_businesses, completed_businesses')
          .eq('id', runId)
          .single()

        if (fetchError) throw fetchError
        setStatus(data?.status || null)
      } catch (err) {
        console.error('Error fetching run status:', err)
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchStatus()

    // Subscribe to real-time updates for this specific run
    const channel = supabase
      .channel(`run-status-${runId}`)
              .on(
          'postgres_changes' as any,
          {
            event: 'UPDATE',
            schema: 'public',
            table: TABLES.PROCESSING_RUNS,
            filter: `id=eq.${runId}`
          },
          (payload) => {
            console.log('🔄 Run status update:', payload)
            setStatus(payload.new.status)
          }
        )
      .subscribe()

    return () => {
      supabase.removeChannel(channel)
    }
  }, [runId])

  return { status, loading, error }
}
