-- Database Migration: Fix Queue Schema Issues
-- Run this in Supabase SQL Editor to fix the remaining test failures

-- 1. Add missing updated_at column to job_queue_entries
ALTER TABLE job_queue_entries 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- 2. Update the check constraint for job_queue_entries to allow 'cancelled' status
ALTER TABLE job_queue_entries 
DROP CONSTRAINT IF EXISTS job_queue_entries_status_check;

ALTER TABLE job_queue_entries 
ADD CONSTRAINT job_queue_entries_status_check 
CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled'));

-- 3. Update the check constraint for url_processing_status to allow 'cancelled' status
ALTER TABLE url_processing_status 
DROP CONSTRAINT IF EXISTS url_processing_status_status_check;

ALTER TABLE url_processing_status 
ADD CONSTRAINT url_processing_status_status_check 
CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'retrying', 'cancelled'));

-- 4. Fix the processing_duration field type issue
-- Change from INTEGER to BIGINT to handle larger duration values
ALTER TABLE url_processing_status 
ALTER COLUMN processing_duration TYPE BIGINT;

-- 5. Create a trigger to automatically update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 6. Create trigger for job_queue_entries
DROP TRIGGER IF EXISTS update_job_queue_entries_updated_at ON job_queue_entries;
CREATE TRIGGER update_job_queue_entries_updated_at
    BEFORE UPDATE ON job_queue_entries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 7. Create trigger for url_processing_status (if not already exists)
DROP TRIGGER IF EXISTS update_url_processing_status_updated_at ON url_processing_status;
CREATE TRIGGER update_url_processing_status_updated_at
    BEFORE UPDATE ON url_processing_status
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 8. Verify the changes
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('job_queue_entries', 'url_processing_status')
AND column_name IN ('updated_at', 'processing_duration')
ORDER BY table_name, column_name;

-- 9. Show the updated constraints
SELECT 
    tc.table_name, 
    tc.constraint_name, 
    tc.constraint_type,
    cc.check_clause
FROM information_schema.table_constraints tc
JOIN information_schema.check_constraints cc ON tc.constraint_name = cc.constraint_name
WHERE tc.table_name IN ('job_queue_entries', 'url_processing_status')
AND tc.constraint_type = 'CHECK';
