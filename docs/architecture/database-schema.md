# Database Schema

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Processing Runs Table
CREATE TABLE processing_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location TEXT NOT NULL,
    niche TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN (
        'initializing', 'discovering', 'scoring', 'generating', 
        'outreach', 'exporting', 'completed', 'failed'
    )),
    total_businesses INTEGER DEFAULT 0,
    completed_businesses INTEGER DEFAULT 0,
    failed_businesses INTEGER DEFAULT 0,
    current_step TEXT,
    start_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    estimated_completion TIMESTAMPTZ,
    error_log JSONB DEFAULT '[]'::jsonb,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    export_csv_path TEXT,
    google_sheet_id TEXT,
    agent_status JSONB DEFAULT '{
        "discovery_agent": "pending",
        "scoring_agent": "pending", 
        "generation_agent": "pending",
        "outreach_agent": "pending"
    }'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Businesses Table
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    processing_run_id UUID NOT NULL REFERENCES processing_runs(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    niche TEXT NOT NULL,
    location TEXT NOT NULL,
    website TEXT,
    email TEXT,
    phone TEXT,
    address TEXT NOT NULL,
    postcode TEXT NOT NULL,
    contact_name TEXT,
    google_place_id TEXT,
    yelp_business_id TEXT,
    data_source TEXT NOT NULL CHECK (data_source IN ('google', 'yelp', 'merged')),
    confidence_score NUMERIC(5,2) CHECK (confidence_score >= 0 AND confidence_score <= 100),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Website Scores Table
CREATE TABLE website_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    overall_score NUMERIC(5,2) CHECK (overall_score >= 0 AND overall_score <= 100),
    performance_score NUMERIC(4,2) CHECK (performance_score >= 0 AND performance_score <= 20),
    accessibility_score NUMERIC(4,2) CHECK (accessibility_score >= 0 AND accessibility_score <= 15),
    seo_score NUMERIC(4,2) CHECK (seo_score >= 0 AND seo_score <= 15),
    best_practices_score NUMERIC(4,2) CHECK (best_practices_score >= 0 AND best_practices_score <= 15),
    trust_score NUMERIC(4,2) CHECK (trust_score >= 0 AND trust_score <= 15),
    cro_score NUMERIC(4,2) CHECK (cro_score >= 0 AND cro_score <= 20),
    scoring_method TEXT NOT NULL CHECK (scoring_method IN ('lighthouse', 'heuristic', 'hybrid', 'fallback')),
    confidence_level TEXT NOT NULL CHECK (confidence_level IN ('high', 'medium', 'low')),
    lighthouse_data JSONB,
    heuristic_data JSONB DEFAULT '{}'::jsonb,
    top_issues TEXT[] DEFAULT '{}',
    scan_duration INTEGER, -- seconds
    scored_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated Sites Table
CREATE TABLE generated_sites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    website_score_id UUID NOT NULL REFERENCES website_scores(id) ON DELETE CASCADE,
    site_url TEXT NOT NULL,
    template_used TEXT NOT NULL,
    generation_prompt TEXT,
    vercel_deployment_id TEXT,
    generation_time NUMERIC(8,2), -- seconds with decimals
    site_content JSONB DEFAULT '{}'::jsonb,
    deployment_status TEXT NOT NULL CHECK (deployment_status IN ('pending', 'deployed', 'failed', 'expired')),
    expires_at TIMESTAMPTZ,
    page_views INTEGER DEFAULT 0,
    mobile_score NUMERIC(5,2),
    generation_cost NUMERIC(10,4), -- USD with 4 decimal precision
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach Campaigns Table
CREATE TABLE outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    generated_site_id UUID REFERENCES generated_sites(id) ON DELETE SET NULL,
    email_subject TEXT NOT NULL,
    email_body TEXT NOT NULL,
    whatsapp_message TEXT NOT NULL,
    sms_message TEXT NOT NULL,
    delivery_status JSONB DEFAULT '{
        "email_sent": false,
        "email_delivered": false,
        "email_callback_data": null,
        "whatsapp_sent": false,
        "whatsapp_delivered": false,
        "whatsapp_callback_data": null,
        "sms_sent": false,
        "sms_delivered": false,
        "sms_callback_data": null,
        "last_updated": null
    }'::jsonb,
    personalization_data JSONB DEFAULT '{}'::jsonb,
    generation_model TEXT,
    campaign_tone TEXT CHECK (campaign_tone IN ('professional', 'casual', 'friendly', 'urgent')),
    call_to_action TEXT,
    variables_used TEXT[] DEFAULT '{}',
    content_length JSONB DEFAULT '{
        "email_chars": 0,
        "whatsapp_chars": 0,
        "sms_chars": 0
    }'::jsonb,
    generation_cost NUMERIC(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance Indexes
CREATE INDEX idx_processing_runs_status ON processing_runs(status);
CREATE INDEX idx_processing_runs_created_at ON processing_runs(created_at DESC);
CREATE INDEX idx_businesses_run_id ON businesses(processing_run_id);
CREATE INDEX idx_businesses_niche_location ON businesses(niche, location);
CREATE INDEX idx_businesses_website ON businesses(website) WHERE website IS NOT NULL;
CREATE INDEX idx_businesses_confidence ON businesses(confidence_score DESC);
CREATE INDEX idx_website_scores_business_id ON website_scores(business_id);
CREATE INDEX idx_website_scores_overall_score ON website_scores(overall_score DESC);
CREATE INDEX idx_website_scores_scored_at ON website_scores(scored_at DESC);
CREATE INDEX idx_generated_sites_business_id ON generated_sites(business_id);
CREATE INDEX idx_generated_sites_status ON generated_sites(deployment_status);
CREATE INDEX idx_generated_sites_expires_at ON generated_sites(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_outreach_campaigns_business_id ON outreach_campaigns(business_id);
```

---
