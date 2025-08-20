import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_API_KEY!

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  realtime: {
    params: {
      eventsPerSecond: 10
    }
  }
})

// Database table names
export const TABLES = {
  PROCESSING_RUNS: 'processing_runs',
  BUSINESSES: 'businesses',
  WEBSITE_SCORES: 'website_scores',
  GENERATED_SITES: 'generated_sites',
  OUTREACH_CAMPAIGNS: 'outreach_campaigns'
} as const

// Real-time channels
export const CHANNELS = {
  WORKFLOW_PROGRESS: 'workflow-progress',
  BUSINESS_DISCOVERY: 'business-discovery',
  WEBSITE_SCORING: 'website-scoring',
  DEMO_GENERATION: 'demo-generation'
} as const

// Database types for TypeScript
export interface ProcessingRun {
  id: string
  location: string
  niche: string
  status: 'initializing' | 'discovering' | 'scoring' | 'generating' | 'outreach' | 'exporting' | 'completed' | 'failed'
  total_businesses: number
  completed_businesses: number
  failed_businesses: number
  current_step: string
  start_time: string
  end_time?: string
  estimated_completion?: string
  error_log: any[]
  performance_metrics: any
  export_csv_path?: string
  google_sheet_id?: string
  agent_status: {
    discovery_agent: string
    scoring_agent: string
    generation_agent: string
    outreach_agent: string
  }
  created_at: string
  updated_at: string
}

export interface Business {
  id: string
  processing_run_id: string
  name: string
  niche: string
  location: string
  website?: string
  email?: string
  phone?: string
  address: string
  postcode: string
  contact_name?: string
  google_place_id?: string
  yelp_business_id?: string
  data_source: 'google' | 'yelp' | 'merged'
  confidence_score?: number
  created_at: string
  updated_at: string
}

export interface WebsiteScore {
  id: string
  business_id: string
  overall_score: number
  performance_score: number
  accessibility_score: number
  seo_score: number
  best_practices_score: number
  trust_score?: number
  cro_score?: number
  scoring_method: 'lighthouse' | 'heuristic' | 'hybrid' | 'fallback'
  confidence_level: 'high' | 'medium' | 'low'
  lighthouse_data?: any
  heuristic_data?: any
  top_issues: string[]
  scan_duration?: number
  scored_at: string
}
