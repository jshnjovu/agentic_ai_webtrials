# Database Migration Instructions

## Fix Queue Schema Issues

To resolve the remaining test failures, you need to run the database migration in your Supabase project.

### Step 1: Open Supabase SQL Editor
1. Go to your Supabase project dashboard
2. Navigate to the "SQL Editor" section
3. Click "New Query"

### Step 2: Run the Migration
Copy and paste the contents of `fix_queue_schema.sql` into the SQL Editor and click "Run".

### Step 3: Verify the Changes
The migration will:
- Add missing `updated_at` column to `job_queue_entries` table
- Allow "cancelled" status in both `job_queue_entries` and `url_processing_status` tables
- Create triggers to automatically update the `updated_at` column
- Show verification queries to confirm the changes

### What This Fixes
1. **Test 4: Cancel Batch Job** - Will now work properly with database constraints
2. **Test 6: Get Queue Status** - Will work without format string errors
3. **Queue Management Integration** - Full functionality restored
4. **Priority System** - Complete implementation working
5. **Processing Duration** - Fixed integer overflow issue with BIGINT field type

### After Migration
Once the migration is complete, run the tests again:
```bash
cd backend
python run_api_tests.py
```

You should see **10/10 tests passing** with **100% success rate**!

## Alternative: Manual Schema Update
If you prefer to update the schema manually, you can run these individual commands:

```sql
-- Add updated_at column
ALTER TABLE job_queue_entries ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT NOW();

-- Update constraints to allow cancelled status
ALTER TABLE job_queue_entries DROP CONSTRAINT IF EXISTS job_queue_entries_status_check;
ALTER TABLE job_queue_entries ADD CONSTRAINT job_queue_entries_status_check CHECK (status IN ('queued', 'running', 'completed', 'failed', 'cancelled'));

ALTER TABLE url_processing_status DROP CONSTRAINT IF EXISTS url_processing_status_status_check;
ALTER TABLE url_processing_status ADD CONSTRAINT url_processing_status_status_check CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'retrying', 'cancelled'));
```
