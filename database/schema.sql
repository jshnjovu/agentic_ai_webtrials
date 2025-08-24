-- LeadGen Makeover Agent + Batch Processing Database Schema
-- Run this in your Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For fuzzy text search

-- Processing Runs Table (LeadGen core)
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

-- Businesses Table (LeadGen core)
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

-- Batch Jobs Table (Enhanced for LeadGen batch processing)
CREATE TABLE IF NOT EXISTS batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    processing_run_id UUID REFERENCES processing_runs(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'cancelled')) DEFAULT 'pending',
    total_urls INTEGER NOT NULL,
    completed_urls INTEGER DEFAULT 0,
    failed_urls INTEGER DEFAULT 0,
    progress_percentage NUMERIC(5,2) DEFAULT 0,
    batch_size INTEGER DEFAULT 5,
    priority INTEGER DEFAULT 1,
    estimated_duration INTEGER,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    error_log JSONB DEFAULT '[]'::jsonb,
    performance_metrics JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- URL Processing Status Table (Enhanced for LeadGen URLs)
CREATE TABLE IF NOT EXISTS url_processing_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    batch_job_id UUID NOT NULL REFERENCES batch_jobs(id) ON DELETE CASCADE,
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'retrying', 'cancelled')) DEFAULT 'pending',
    current_step TEXT CHECK (current_step IN ('pagespeed', 'whois', 'trust_cro', 'analysis', 'discovery', 'scoring')),
    progress_data JSONB DEFAULT '{}'::jsonb,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    processing_duration BIGINT,
    result_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Website Scores Table (LeadGen specific)
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
    scan_duration INTEGER,
    scored_at TIMESTAMPTZ DEFAULT NOW()
);

-- Generated Sites Table (LeadGen specific)
CREATE TABLE IF NOT EXISTS generated_sites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    website_score_id UUID NOT NULL REFERENCES website_scores(id) ON DELETE CASCADE,
    site_url TEXT NOT NULL,
    template_used TEXT NOT NULL,
    generation_prompt TEXT,
    vercel_deployment_id TEXT,
    generation_time NUMERIC(8,2),
    site_content JSONB DEFAULT '{}'::jsonb,
    deployment_status TEXT NOT NULL CHECK (deployment_status IN ('pending', 'deployed', 'failed', 'expired')),
    expires_at TIMESTAMPTZ,
    page_views INTEGER DEFAULT 0,
    mobile_score NUMERIC(5,2),
    generation_cost NUMERIC(10,4),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach Campaigns Table (LeadGen specific)
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

-- Batch Job Queues Table (Retained for background processing)
CREATE TABLE IF NOT EXISTS batch_job_queues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    max_concurrent_jobs INTEGER DEFAULT 3,
    max_queue_size INTEGER DEFAULT 100,
    priority_weight INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Job Queue Entries Table
CREATE TABLE IF NOT EXISTS job_queue_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    queue_id UUID NOT NULL REFERENCES batch_job_queues(id) ON DELETE CASCADE,
    batch_job_id UUID NOT NULL REFERENCES batch_jobs(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 1,
    scheduled_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    status TEXT NOT NULL CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled')) DEFAULT 'queued',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Batch Processing Metrics Table (Enhanced for both systems)
CREATE TABLE IF NOT EXISTS batch_processing_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    processing_run_id UUID REFERENCES processing_runs(id) ON DELETE CASCADE,
    batch_job_id UUID REFERENCES batch_jobs(id) ON DELETE CASCADE,
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC(10,4),
    metric_unit TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
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

CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_processing_run_id ON batch_jobs(processing_run_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_priority ON batch_jobs(priority);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_created_at ON batch_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_url_processing_status_batch_job_id ON url_processing_status(batch_job_id);
CREATE INDEX IF NOT EXISTS idx_url_processing_status_business_id ON url_processing_status(business_id);
CREATE INDEX IF NOT EXISTS idx_url_processing_status_status ON url_processing_status(status);
CREATE INDEX IF NOT EXISTS idx_url_processing_status_url ON url_processing_status(url);
CREATE INDEX IF NOT EXISTS idx_job_queue_entries_queue_id ON job_queue_entries(queue_id);
CREATE INDEX IF NOT EXISTS idx_job_queue_entries_priority ON job_queue_entries(priority);
CREATE INDEX IF NOT EXISTS idx_batch_processing_metrics_composite ON batch_processing_metrics(processing_run_id, batch_job_id, business_id);

-- Enable Row Level Security
ALTER TABLE processing_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE businesses ENABLE ROW LEVEL SECURITY;
ALTER TABLE website_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_campaigns ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE url_processing_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_job_queues ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_queue_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_processing_metrics ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (to avoid conflicts)
DROP POLICY IF EXISTS "Allow all operations on processing_runs" ON processing_runs;
DROP POLICY IF EXISTS "Allow all operations on businesses" ON businesses;
DROP POLICY IF EXISTS "Allow all operations on website_scores" ON website_scores;
DROP POLICY IF EXISTS "Allow all operations on generated_sites" ON generated_sites;
DROP POLICY IF EXISTS "Allow all operations on outreach_campaigns" ON outreach_campaigns;
DROP POLICY IF EXISTS "Allow all operations on batch_jobs" ON batch_jobs;
DROP POLICY IF EXISTS "Allow all operations on url_processing_status" ON url_processing_status;
DROP POLICY IF EXISTS "Allow all operations on batch_job_queues" ON batch_job_queues;
DROP POLICY IF EXISTS "Allow all operations on job_queue_entries" ON job_queue_entries;
DROP POLICY IF EXISTS "Allow all operations on batch_processing_metrics" ON batch_processing_metrics;

-- Create RLS policies (without IF NOT EXISTS)
CREATE POLICY "Allow all operations on processing_runs" ON processing_runs FOR ALL USING (true);
CREATE POLICY "Allow all operations on businesses" ON businesses FOR ALL USING (true);
CREATE POLICY "Allow all operations on website_scores" ON website_scores FOR ALL USING (true);
CREATE POLICY "Allow all operations on generated_sites" ON generated_sites FOR ALL USING (true);
CREATE POLICY "Allow all operations on outreach_campaigns" ON outreach_campaigns FOR ALL USING (true);
CREATE POLICY "Allow all operations on batch_jobs" ON batch_jobs FOR ALL USING (true);
CREATE POLICY "Allow all operations on url_processing_status" ON url_processing_status FOR ALL USING (true);
CREATE POLICY "Allow all operations on batch_job_queues" ON batch_job_queues FOR ALL USING (true);
CREATE POLICY "Allow all operations on job_queue_entries" ON job_queue_entries FOR ALL USING (true);
CREATE POLICY "Allow all operations on batch_processing_metrics" ON batch_processing_metrics FOR ALL USING (true);

-- Helper function to safely add tables to realtime publication
CREATE OR REPLACE FUNCTION add_table_to_realtime_if_not_exists(table_name TEXT)
RETURNS VOID AS $$
BEGIN
    -- Check if the table is already in the publication
    IF NOT EXISTS (
        SELECT 1 
        FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
        AND tablename = table_name
    ) THEN
        -- Add the table to the publication
        EXECUTE format('ALTER PUBLICATION supabase_realtime ADD TABLE %I', table_name);
    END IF;
EXCEPTION
    WHEN others THEN
        -- Log the error but don't fail the entire script
        RAISE NOTICE 'Could not add table % to realtime publication: %', table_name, SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- Enable realtime for all tables (safely)
SELECT add_table_to_realtime_if_not_exists('processing_runs');
SELECT add_table_to_realtime_if_not_exists('businesses');
SELECT add_table_to_realtime_if_not_exists('website_scores');
SELECT add_table_to_realtime_if_not_exists('generated_sites');
SELECT add_table_to_realtime_if_not_exists('outreach_campaigns');
SELECT add_table_to_realtime_if_not_exists('batch_jobs');
SELECT add_table_to_realtime_if_not_exists('url_processing_status');
SELECT add_table_to_realtime_if_not_exists('batch_job_queues');
SELECT add_table_to_realtime_if_not_exists('job_queue_entries');
SELECT add_table_to_realtime_if_not_exists('batch_processing_metrics');

-- Clean up the helper function
DROP FUNCTION IF EXISTS add_table_to_realtime_if_not_exists(TEXT);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing triggers if they exist to avoid conflicts
DROP TRIGGER IF EXISTS update_processing_runs_updated_at ON processing_runs;
DROP TRIGGER IF EXISTS update_businesses_updated_at ON businesses;
DROP TRIGGER IF EXISTS update_outreach_campaigns_updated_at ON outreach_campaigns;
DROP TRIGGER IF EXISTS update_batch_jobs_updated_at ON batch_jobs;
DROP TRIGGER IF EXISTS update_url_processing_status_updated_at ON url_processing_status;
DROP TRIGGER IF EXISTS update_job_queue_entries_updated_at ON job_queue_entries;

-- Create triggers
CREATE TRIGGER update_processing_runs_updated_at BEFORE UPDATE ON processing_runs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_businesses_updated_at BEFORE UPDATE ON businesses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_outreach_campaigns_updated_at BEFORE UPDATE ON outreach_campaigns FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_batch_jobs_updated_at BEFORE UPDATE ON batch_jobs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_url_processing_status_updated_at BEFORE UPDATE ON url_processing_status FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_job_queue_entries_updated_at BEFORE UPDATE ON job_queue_entries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to update batch progress (enhanced for LeadGen)
CREATE OR REPLACE FUNCTION update_batch_progress()
RETURNS TRIGGER AS $$
BEGIN
    -- Update progress percentage when URL status changes
    IF TG_OP = 'UPDATE' THEN
        UPDATE batch_jobs 
        SET 
            completed_urls = (
                SELECT COUNT(*) 
                FROM url_processing_status 
                WHERE batch_job_id = NEW.batch_job_id 
                AND status = 'completed'
            ),
            failed_urls = (
                SELECT COUNT(*) 
                FROM url_processing_status 
                WHERE batch_job_id = NEW.batch_job_id 
                AND status = 'failed'
            ),
            progress_percentage = (
                SELECT ROUND(
                    (COUNT(CASE WHEN status IN ('completed', 'failed') THEN 1 END)::NUMERIC / 
                     COUNT(*)::NUMERIC) * 100, 2
                )
                FROM url_processing_status 
                WHERE batch_job_id = NEW.batch_job_id
            ),
            updated_at = NOW()
        WHERE id = NEW.batch_job_id;
        
        -- Update batch job status based on progress
        UPDATE batch_jobs 
        SET 
            status = CASE 
                WHEN progress_percentage = 100 THEN 'completed'
                WHEN progress_percentage > 0 THEN 'processing'
                ELSE status
            END,
            completed_at = CASE 
                WHEN progress_percentage = 100 THEN NOW()
                ELSE completed_at
            END
        WHERE id = NEW.batch_job_id;
        
        -- Update processing run metrics if this URL is linked to a business
        IF NEW.business_id IS NOT NULL THEN
            UPDATE processing_runs 
            SET 
                completed_businesses = (
                    SELECT COUNT(DISTINCT business_id)
                    FROM url_processing_status ups
                    JOIN batch_jobs bj ON ups.batch_job_id = bj.id
                    WHERE bj.processing_run_id = (
                        SELECT processing_run_id 
                        FROM batch_jobs 
                        WHERE id = NEW.batch_job_id
                    )
                    AND ups.status = 'completed'
                ),
                updated_at = NOW()
            WHERE id = (
                SELECT processing_run_id 
                FROM batch_jobs 
                WHERE id = NEW.batch_job_id
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop existing trigger to avoid conflicts
DROP TRIGGER IF EXISTS update_batch_progress_trigger ON url_processing_status;

-- Create trigger to automatically update batch progress
CREATE TRIGGER update_batch_progress_trigger 
    AFTER UPDATE ON url_processing_status 
    FOR EACH ROW EXECUTE FUNCTION update_batch_progress();

-- Create function to get batch job summary (enhanced)
CREATE OR REPLACE FUNCTION get_batch_job_summary(job_id UUID)
RETURNS TABLE(
    total_urls INTEGER,
    completed_urls INTEGER,
    failed_urls INTEGER,
    progress_percentage NUMERIC,
    estimated_remaining_time INTEGER,
    status TEXT,
    processing_run_id UUID
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        bj.total_urls,
        bj.completed_urls,
        bj.failed_urls,
        bj.progress_percentage,
        CASE 
            WHEN bj.progress_percentage > 0 THEN
                ROUND(
                    (EXTRACT(EPOCH FROM (NOW() - bj.started_at)) / 
                     (bj.progress_percentage / 100)) * 
                    (1 - bj.progress_percentage / 100)
                )
            ELSE NULL
        END::INTEGER as estimated_remaining_time,
        bj.status,
        bj.processing_run_id
    FROM batch_jobs bj
    WHERE bj.id = job_id;
END;
$$ language 'plpgsql';

-- Create function to get processing run summary
CREATE OR REPLACE FUNCTION get_processing_run_summary(run_id UUID)
RETURNS TABLE(
    total_businesses INTEGER,
    completed_businesses INTEGER,
    failed_businesses INTEGER,
    current_status TEXT,
    completion_percentage NUMERIC,
    estimated_completion TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pr.total_businesses,
        pr.completed_businesses,
        pr.failed_businesses,
        pr.status,
        CASE 
            WHEN pr.total_businesses > 0 THEN
                ROUND((pr.completed_businesses::NUMERIC / pr.total_businesses::NUMERIC) * 100, 2)
            ELSE 0
        END as completion_percentage,
        pr.estimated_completion
    FROM processing_runs pr
    WHERE pr.id = run_id;
END;
$$ language 'plpgsql';

-- Insert default queue configurations
INSERT INTO batch_job_queues (name, description, max_concurrent_jobs, priority_weight) 
VALUES 
    ('high_priority', 'High priority jobs for immediate processing', 2, 3),
    ('normal', 'Standard priority jobs', 5, 1),
    ('low_priority', 'Low priority background jobs', 3, 0.5)
ON CONFLICT (name) DO NOTHING;

-- Insert sample data for testing
INSERT INTO processing_runs (location, niche, status, current_step) 
VALUES ('London, UK', 'Gyms', 'initializing', 'start')
ON CONFLICT DO NOTHING;