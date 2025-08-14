# Data Models

## Business

**Purpose:** Represents a discovered local business with complete contact information and enrichment data from Google Places and Yelp Fusion APIs.

**TypeScript Interface:**
```typescript
export interface Business {
  id: string;
  name: string;
  niche: string;
  location: string;
  website: string | null;
  email: string | null;
  phone: string | null;
  address: string;
  postcode: string;
  contact_name: string | null;
  google_place_id: string | null;
  yelp_business_id: string | null;
  data_source: 'google' | 'yelp' | 'merged';
  confidence_score: number;
  created_at: string;
  updated_at: string;
}
```

## WebsiteScore

**Purpose:** Comprehensive website evaluation results from hybrid Lighthouse + heuristic analysis, providing detailed scoring breakdown and improvement recommendations.

**TypeScript Interface:**
```typescript
export interface WebsiteScore {
  id: string;
  business_id: string;
  overall_score: number;
  performance_score: number;
  accessibility_score: number;
  seo_score: number;
  best_practices_score: number;
  trust_score: number;
  cro_score: number;
  scoring_method: 'lighthouse' | 'heuristic' | 'hybrid' | 'fallback';
  confidence_level: 'high' | 'medium' | 'low';
  lighthouse_data: Record<string, any> | null;
  heuristic_data: Record<string, any>;
  top_issues: string[];
  scan_duration: number;
  scored_at: string;
}
```

## GeneratedSite

**Purpose:** AI-generated demo website created for businesses with low website scores, including deployment details and performance tracking.

**TypeScript Interface:**
```typescript
export interface GeneratedSite {
  id: string;
  business_id: string;
  website_score_id: string;
  site_url: string;
  template_used: string;
  generation_prompt: string;
  vercel_deployment_id: string;
  generation_time: number;
  site_content: {
    hero: {
      headline: string;
      subheadline: string;
      cta_text: string;
    };
    services: Array<{
      title: string;
      description: string;
      icon: string;
    }>;
    about: string;
    contact: {
      form_fields: string[];
      map_embed: string;
    };
  };
  deployment_status: 'pending' | 'deployed' | 'failed' | 'expired';
  expires_at: string;
  page_views: number;
  mobile_score: number;
  generation_cost: number;
  created_at: string;
}
```

## OutreachCampaign

**Purpose:** Multi-channel personalized outreach messages (Email, WhatsApp, SMS) generated using AI with business-specific context and demo site integration, including delivery tracking.

**TypeScript Interface:**
```typescript
export interface OutreachCampaign {
  id: string;
  business_id: string;
  generated_site_id: string | null;
  email_subject: string;
  email_body: string;
  whatsapp_message: string;
  sms_message: string;
  delivery_status: {
    email_sent: boolean;
    email_delivered: boolean;
    email_callback_data: Record<string, any> | null;
    whatsapp_sent: boolean;
    whatsapp_delivered: boolean;
    whatsapp_callback_data: Record<string, any> | null;
    sms_sent: boolean;
    sms_delivered: boolean;
    sms_callback_data: Record<string, any> | null;
    last_updated: string;
  };
  personalization_data: {
    business_name: string;
    contact_name: string | null;
    location: string;
    top_issues: string[];
    demo_url: string | null;
    niche_keywords: string[];
  };
  generation_model: string;
  campaign_tone: 'professional' | 'casual' | 'friendly' | 'urgent';
  call_to_action: string;
  variables_used: string[];
  content_length: {
    email_chars: number;
    whatsapp_chars: number;
    sms_chars: number;
  };
  generation_cost: number;
  created_at: string;
}
```

## ProcessingRun

**Purpose:** Tracking and orchestration data for each agentic AI processing session, managing the complete workflow from business discovery through outreach generation.

**TypeScript Interface:**
```typescript
export interface ProcessingRun {
  id: string;
  location: string;
  niche: string;
  status: 'initializing' | 'discovering' | 'scoring' | 'generating' | 'outreach' | 'exporting' | 'completed' | 'failed';
  total_businesses: number;
  completed_businesses: number;
  failed_businesses: number;
  current_step: string;
  start_time: string;
  end_time: string | null;
  estimated_completion: string | null;
  error_log: Array<{
    timestamp: string;
    error_type: string;
    message: string;
    business_id: string | null;
    retry_count: number;
  }>;
  performance_metrics: {
    discovery_time: number;
    scoring_time: number;
    generation_time: number;
    outreach_time: number;
    total_api_calls: number;
    total_cost: number;
  };
  export_csv_path: string | null;
  google_sheet_id: string | null;
  agent_status: {
    discovery_agent: 'pending' | 'running' | 'completed' | 'failed';
    scoring_agent: 'pending' | 'running' | 'completed' | 'failed';
    generation_agent: 'pending' | 'running' | 'completed' | 'failed';
    outreach_agent: 'pending' | 'running' | 'completed' | 'failed';
  };
  created_at: string;
  updated_at: string;
}
```

---
