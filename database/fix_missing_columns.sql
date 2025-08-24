-- Fix Missing Columns Migration
-- Run this in your Supabase SQL Editor to add missing columns
-- Based on analysis of existing schema.sql

-- Add missing error_message column to batch_jobs table
-- (error_log JSONB already exists, but error_message TEXT is missing)
ALTER TABLE batch_jobs 
ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Add missing metadata column to job_queue_entries table
-- (This column is completely missing from the schema)
ALTER TABLE job_queue_entries 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Verify the changes
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name IN ('job_queue_entries', 'batch_jobs')
AND column_name IN ('metadata', 'error_message')
ORDER BY table_name, column_name;

-- Update existing rows to have default values
UPDATE job_queue_entries 
SET metadata = '{}'::jsonb 
WHERE metadata IS NULL;

-- Add comments for documentation
COMMENT ON COLUMN job_queue_entries.metadata IS 'Additional metadata for job processing (JSON format)';
COMMENT ON COLUMN batch_jobs.error_message IS 'Error message if batch job failed';
