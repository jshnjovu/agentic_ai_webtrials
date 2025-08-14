# API Specification

## Core API Endpoints

**Base URL:** `/api/v1`

### Processing Runs API

**POST `/processing-runs`** - Initiate Processing Workflow
```typescript
// Request
interface ProcessingRunRequest {
  location: string;           // "New York, NY"
  niche: string;             // "Italian restaurants"
  max_businesses?: number;   // Default: 10, Max: 50
  scoring_enabled?: boolean; // Default: true
  generation_enabled?: boolean; // Default: true
  outreach_enabled?: boolean; // Default: true
}

// Response
interface ProcessingRunResponse {
  id: string;
  status: 'initializing';
  websocket_url: string;     // Real-time progress updates
  estimated_duration: number; // seconds
  created_at: string;
}
```

**GET `/processing-runs/{id}`** - Get Processing Run Status
```typescript
interface ProcessingRunDetailResponse {
  id: string;
  location: string;
  niche: string;
  status: ProcessingStatus;
  progress: {
    current_step: string;
    completion_percentage: number;
    businesses_discovered: number;
    businesses_scored: number;
    sites_generated: number;
    campaigns_created: number;
  };
  businesses: Business[];
  performance_metrics: {
    total_duration: number;
    discovery_time: number;
    scoring_time: number;
    generation_time: number;
    outreach_time: number;
  };
  export_links: {
    csv_url: string | null;
    google_sheet_url: string | null;
  };
}
```

### Business Management API

**GET `/processing-runs/{runId}/businesses`** - List Discovered Businesses
```typescript
interface BusinessListResponse {
  businesses: Business[];
  total_count: number;
  completion_stats: {
    with_websites: number;
    with_emails: number;
    with_phones: number;
    confidence_high: number;
  };
}
```

**GET `/businesses/{id}/website-score`** - Get Website Score Details
```typescript
interface WebsiteScoreResponse {
  score: WebsiteScore;
  recommendations: {
    category: 'performance' | 'accessibility' | 'seo' | 'best_practices' | 'trust' | 'cro';
    priority: 'high' | 'medium' | 'low';
    issue: string;
    solution: string;
    estimated_impact: number; // 1-10 scale
  }[];
  lighthouse_report_url?: string;
}
```

### Outreach Campaign API

**GET `/businesses/{id}/outreach-campaigns`** - Get Campaign Details
```typescript
interface OutreachCampaignResponse {
  campaign: OutreachCampaign;
  delivery_tracking: {
    email: {
      sent_at: string | null;
      delivered_at: string | null;
      opened_at: string | null;
      clicked_at: string | null;
      bounced_at: string | null;
      status: 'pending' | 'sent' | 'delivered' | 'opened' | 'clicked' | 'bounced' | 'failed';
      provider_id: string | null; // Bravo message ID
      error_message: string | null;
    };
    whatsapp: {
      sent_at: string | null;
      delivered_at: string | null;
      read_at: string | null;
      replied_at: string | null;
      status: 'pending' | 'sent' | 'delivered' | 'read' | 'replied' | 'failed';
      provider_id: string | null; // TextBee message ID
      error_message: string | null;
    };
    sms: {
      sent_at: string | null;
      delivered_at: string | null;
      status: 'pending' | 'sent' | 'delivered' | 'failed';
      provider_id: string | null; // TextBee message ID
      error_message: string | null;
    };
  };
}
```

**POST `/outreach-campaigns/{id}/send`** - Send Campaign Messages
```typescript
// Request
interface SendCampaignRequest {
  channels: ('email' | 'whatsapp' | 'sms')[];
  schedule_at?: string; // ISO timestamp for delayed sending
  test_mode?: boolean;  // Send to test recipients only
}

// Response
interface SendCampaignResponse {
  campaign_id: string;
  scheduled_sends: {
    channel: 'email' | 'whatsapp' | 'sms';
    status: 'queued' | 'sending' | 'sent' | 'failed';
    provider_id: string | null;
    scheduled_for: string;
    error_message?: string;
  }[];
}
```

### Delivery Webhook Endpoints

**POST `/webhooks/email-delivery`** - Bravo Email Delivery Webhook
```typescript
interface BravoWebhookPayload {
  message_id: string;
  event_type: 'sent' | 'delivered' | 'opened' | 'clicked' | 'bounced';
  timestamp: string;
  recipient_email: string;
  campaign_metadata: {
    business_id: string;
    outreach_campaign_id: string;
  };
  bounce_reason?: string;
  user_agent?: string; // for open/click events
}
```

**POST `/webhooks/sms-whatsapp-delivery`** - TextBee Delivery Webhook
```typescript
interface TextBeeWebhookPayload {
  message_id: string;
  channel: 'sms' | 'whatsapp';
  status: 'sent' | 'delivered' | 'read' | 'replied' | 'failed';
  timestamp: string;
  recipient: string; // phone number
  campaign_metadata: {
    business_id: string;
    outreach_campaign_id: string;
  };
  error_code?: string;
  reply_message?: string; // for replied events
}
```

### Export and Reporting API

**POST `/processing-runs/{id}/export`** - Export Processing Results
```typescript
// Request
interface ExportRequest {
  format: 'csv' | 'google_sheets';
  include_fields: {
    businesses: boolean;
    website_scores: boolean;
    generated_sites: boolean;
    outreach_campaigns: boolean;
    delivery_tracking: boolean;
  };
  google_sheet_config?: {
    sheet_name: string;
    share_with_emails: string[];
  };
}

// Response
interface ExportResponse {
  export_id: string;
  format: 'csv' | 'google_sheets';
  status: 'processing' | 'completed' | 'failed';
  download_url?: string; // For CSV exports
  google_sheet_url?: string; // For Google Sheets exports
  expires_at: string;
}
```

### Real-time Progress WebSocket API

**WebSocket `/processing-runs/{id}/progress`**
```typescript
// Outbound Message Types
interface ProgressUpdateMessage {
  type: 'progress_update';
  data: {
    run_id: string;
    status: ProcessingStatus;
    current_step: string;
    completion_percentage: number;
    agent_status: Record<string, 'pending' | 'running' | 'completed' | 'failed'>;
    last_completed_business?: {
      name: string;
      website_score?: number;
      demo_generated: boolean;
    };
    estimated_time_remaining: number; // seconds
  };
}

interface ErrorNotificationMessage {
  type: 'error';
  data: {
    run_id: string;
    error_code: string;
    message: string;
    recoverable: boolean;
    retry_in?: number; // seconds until retry
    affected_businesses: string[]; // business IDs
  };
}

interface DeliveryStatusMessage {
  type: 'delivery_update';
  data: {
    business_id: string;
    campaign_id: string;
    channel: 'email' | 'whatsapp' | 'sms';
    status: string;
    timestamp: string;
  };
}
```

---
