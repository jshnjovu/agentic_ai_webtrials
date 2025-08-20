-- LeadGen Makeover Agent Database Schema
-- Run this in your Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Enable Row Level Security (RLS)
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret-here';

-- Processing Runs Table
CREATE TABLE IF NOT EXISTS processing_runs (
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
CREATE TABLE IF NOT EXISTS businesses (
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
CREATE TABLE IF NOT EXISTS website_scores (
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
CREATE TABLE IF NOT EXISTS generated_sites (
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
CREATE TABLE IF NOT EXISTS outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    generated_site_id UUID NOT NULL REFERENCES generated_sites(id) ON DELETE CASCADE,
    campaign_type TEXT NOT NULL CHECK (campaign_type IN ('email', 'linkedin', 'cold_call', 'social_media')),
    status TEXT NOT NULL CHECK (status IN ('draft', 'scheduled', 'sent', 'delivered', 'opened', 'clicked', 'replied', 'failed')),
    subject_line TEXT,
    message_content TEXT,
    recipient_email TEXT,
    recipient_name TEXT,
    scheduled_send_time TIMESTAMPTZ,
    sent_time TIMESTAMPTZ,
    delivery_status TEXT,
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    reply_received BOOLEAN DEFAULT FALSE,
    reply_content TEXT,
    follow_up_scheduled BOOLEAN DEFAULT FALSE,
    follow_up_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_processing_runs_status ON processing_runs(status);
CREATE INDEX IF NOT EXISTS idx_processing_runs_location_niche ON processing_runs(location, niche);
CREATE INDEX IF NOT EXISTS idx_businesses_processing_run_id ON businesses(processing_run_id);
CREATE INDEX IF NOT EXISTS idx_businesses_data_source ON businesses(data_source);
CREATE INDEX IF NOT EXISTS idx_website_scores_business_id ON website_scores(business_id);
CREATE INDEX IF NOT EXISTS idx_website_scores_overall_score ON website_scores(overall_score);
CREATE INDEX IF NOT EXISTS idx_generated_sites_business_id ON generated_sites(business_id);
CREATE INDEX IF NOT EXISTS idx_generated_sites_deployment_status ON generated_sites(deployment_status);
CREATE INDEX IF NOT EXISTS idx_outreach_campaigns_business_id ON outreach_campaigns(business_id);
CREATE INDEX IF NOT EXISTS idx_outreach_campaigns_status ON outreach_campaigns(status);

-- Enable Row Level Security
ALTER TABLE processing_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE website_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_campaigns ENABLE ROW LEVEL SECURITY;

-- Create RLS policies (basic - allow all for now, customize as needed)
CREATE POLICY "Allow all operations on processing_runs" ON processing_runs FOR ALL USING (true);
CREATE POLICY "Allow all operations on businesses" ON businesses FOR ALL USING (true);
CREATE POLICY "Allow all operations on website_scores" ON website_scores FOR ALL USING (true);
CREATE POLICY "Allow all operations on generated_sites" ON generated_sites FOR ALL USING (true);
CREATE POLICY "Allow all operations on outreach_campaigns" ON outreach_campaigns FOR ALL USING (true);

-- Enable realtime for all tables
ALTER PUBLICATION supabase_realtime ADD TABLE processing_runs;
ALTER PUBLICATION supabase_realtime ADD TABLE businesses;
ALTER PUBLICATION supabase_realtime ADD TABLE website_scores;
ALTER PUBLICATION supabase_realtime ADD TABLE generated_sites;
ALTER PUBLICATION supabase_realtime ADD TABLE outreach_campaigns;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_processing_runs_updated_at BEFORE UPDATE ON processing_runs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_businesses_updated_at BEFORE UPDATE ON businesses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_outreach_campaigns_updated_at BEFORE UPDATE ON outreach_campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO processing_runs (location, niche, status, current_step) 
VALUES ('London, UK', 'Gyms', 'initializing', 'start')
ON CONFLICT DO NOTHING;
