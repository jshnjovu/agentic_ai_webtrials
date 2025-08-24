-- Run this directly in your Supabase SQL Editor
-- This will fix the missing columns for batch processing

-- Step 1: Add missing columns
ALTER TABLE job_queue_entries 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

ALTER TABLE batch_jobs 
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Step 2: Update existing rows with default values
UPDATE job_queue_entries 
SET metadata = '{}'::jsonb 
WHERE metadata IS NULL;

-- Step 3: Verify the changes
SELECT 
    'job_queue_entries' as table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'job_queue_entries'
AND column_name = 'metadata'

UNION ALL

SELECT 
    'batch_jobs' as table_name,
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'batch_jobs'
AND column_name = 'error_message'

ORDER BY table_name, column_name;

-- Step 4: Test inserting a sample record
INSERT INTO job_queue_entries (
    queue_id, 
    batch_job_id, 
    priority, 
    status, 
    metadata
) VALUES (
    (SELECT id FROM batch_job_queues WHERE name = 'high_priority' LIMIT 1),
    (SELECT id FROM batch_jobs LIMIT 1),
    3,
    'queued',
    '{"test": "metadata"}'::jsonb
) ON CONFLICT DO NOTHING;

-- Step 5: Clean up test record
DELETE FROM job_queue_entries WHERE metadata = '{"test": "metadata"}'::jsonb;

-- Step 6: Show final table structure
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('job_queue_entries', 'batch_jobs')
AND column_name IN ('metadata', 'error_message')
ORDER BY table_name, column_name;
