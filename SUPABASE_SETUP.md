# Supabase Setup Guide for LeadGen Makeover Agent

## 🚀 **Quick Start**

### **1. Environment Variables Setup**

**Backend (Create `backend/.env`):**
```bash
SUPABASE_URL=https://kcktnvyzksckkkbgnzal.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtja3Rudnl6a3Nja2trYmduemFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0MDk2NjUsImV4cCI6MjA3MDk4NTY2NX0.PPJt4zMHiS8q4UjOjn5Is1QWSEIbM5gtUgDA0hefViY
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
SUPABASE_DB_NAME=supabase-amber-island
```

**Frontend (Create `frontend/.env.local`):**
```bash
NEXT_PUBLIC_SUPABASE_URL=https://kcktnvyzksckkkbgnzal.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtja3Rudnl6a3Nja2trYmduemFsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU0MDk2NjUsImV4cCI6MjA3MDk4NTY2NX0.PPJt4zMHiS8q4UjOjn5Is1QWSEIbM5gtUgDA0hefViY
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

### **2. Install Dependencies**

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### **3. Database Setup**

1. **Go to your Supabase Dashboard:**
   - URL: https://supabase.com/dashboard/project/kcktnvyzksckkkbgnzal
   - Navigate to SQL Editor

2. **Run the schema:**
   - Copy the contents of `database/schema.sql`
   - Paste into SQL Editor
   - Click "Run" to execute

3. **Verify tables created:**
   - Go to Table Editor
   - You should see: `processing_runs`, `businesses`, `website_scores`, `generated_sites`, `outreach_campaigns`

### **4. Enable Realtime**

1. **In Supabase Dashboard:**
   - Go to Database → Replication
   - Ensure "Realtime" is enabled for all tables
   - Tables should show "Realtime enabled"

2. **Verify Realtime Status:**
   - Check that `supabase_realtime` publication includes all tables
   - Status should show "Active" for realtime

## 🔧 **Configuration Details**

### **Backend Supabase Integration**

The backend now includes:
- `src/core/supabase.py` - Supabase client configuration
- Database connection management
- Service role access for admin operations

### **Frontend Real-time Hooks**

New real-time capabilities:
- `hooks/useSupabaseRealtime.ts` - Generic real-time hook
- `hooks/useWorkflowProgress.ts` - Workflow-specific updates
- `hooks/useBusinessDiscovery.ts` - Business discovery updates
- `hooks/useWebsiteScoring.ts` - Website scoring updates

### **Database Schema Features**

- **Real-time enabled** for all tables
- **Row Level Security (RLS)** configured
- **Proper indexing** for performance
- **Triggers** for automatic timestamp updates
- **Foreign key relationships** maintained

## 🧪 **Testing the Setup**

### **1. Test Backend Connection**

```bash
cd backend
python -c "
from src.core.supabase import is_supabase_configured
print(f'Supabase configured: {is_supabase_configured()}')
"
```

### **2. Test Frontend Connection**

```bash
cd frontend
npm run dev
```

Navigate to `http://localhost:3000` and check browser console for Supabase connection status.

### **3. Test Real-time Updates**

1. **Start a workflow** in the LeadGen interface
2. **Open browser console** to see real-time subscription messages
3. **Verify updates** appear without page refresh

## 🚨 **Troubleshooting**

### **Common Issues**

1. **"Missing Supabase environment variables"**
   - Ensure `.env` files are created in correct locations
   - Check environment variable names match exactly

2. **"Failed to subscribe to real-time updates"**
   - Verify Supabase project is active
   - Check realtime is enabled in dashboard
   - Ensure tables exist and have proper permissions

3. **"Database connection failed"**
   - Verify `SUPABASE_URL` format
   - Check service role key permissions
   - Ensure database is not paused

### **Debug Commands**

**Check Supabase Status:**
```bash
# Backend
python -c "from src.core.supabase import supabase_config; print(supabase_config.__dict__)"

# Frontend (browser console)
console.log('Supabase URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
```

## 📊 **Real-time Features Now Available**

### **Business Discovery Phase**
- ✅ Real-time business count updates
- ✅ Live progress indicators
- ✅ Immediate UI feedback

### **Website Scoring Phase**
- ✅ Live scoring progress
- ✅ Real-time score updates
- ✅ Instant result display

### **Workflow Management**
- ✅ Live status updates
- ✅ Progress tracking
- ✅ Error notifications

## 🔄 **Next Steps**

1. **Test real-time updates** with sample data
2. **Integrate with existing LeadGen workflow**
3. **Add authentication** if needed
4. **Monitor performance** and optimize queries
5. **Set up backup and monitoring**

## 📞 **Support**

If you encounter issues:
1. Check Supabase dashboard status
2. Verify environment variables
3. Review browser console for errors
4. Check Supabase logs in dashboard

---

**🎉 Congratulations!** Your LeadGen Makeover Agent now has real-time database capabilities with Supabase!
