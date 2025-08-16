# 🚀 Vercel Deployment Guide for Agentic AI WebTrials

## 📋 **Prerequisites**
- ✅ Git repository connected to Vercel
- ✅ Vercel account and CLI installed
- ✅ Environment variables configured

## 🎯 **Deployment Strategy: Separate Projects**

### **Frontend (Next.js) - Project 1**
- **Framework**: Next.js 13.4.0
- **Deployment**: Automatic via Git push
- **Domain**: `your-project.vercel.app`

### **Backend (FastAPI) - Project 2**
- **Framework**: FastAPI → Vercel Serverless Functions
- **Deployment**: Manual via Vercel CLI
- **Domain**: `your-backend.vercel.app`

---

## 🚀 **Step 1: Deploy Frontend**

Your frontend is already configured! Just push to deploy:

```bash
cd frontend
git add .
git commit -m "Ready for Vercel deployment"
git push origin main
```

**Frontend will auto-deploy to**: `https://your-project.vercel.app`

---

## 🐍 **Step 2: Deploy Backend**

### **2.1 Install Vercel CLI**
```bash
npm i -g vercel
```

### **2.2 Login to Vercel**
```bash
vercel login
```

### **2.3 Deploy Backend**
```bash
cd backend
vercel --prod
```

**Follow the prompts:**
- Set up and deploy: `Y`
- Which scope: Select your account
- Link to existing project: `N`
- Project name: `agentic-ai-backend`
- Directory: `./` (current directory)
- Override settings: `N`

**Backend will deploy to**: `https://your-backend.vercel.app`

---

## 🔧 **Step 3: Configure Environment Variables**

### **Frontend Environment Variables**
In Vercel Dashboard → Frontend Project → Settings → Environment Variables:

```bash
NEXT_PUBLIC_BACKEND_URL=https://your-backend.vercel.app
NEXT_PUBLIC_API_VERSION=v1
```

### **Backend Environment Variables**
In Vercel Dashboard → Backend Project → Settings → Environment Variables:

```bash
# Copy from env.template and fill in real values
GOOGLE_PLACES_API_KEY=your_actual_key
YELP_FUSION_API_KEY=your_actual_key
LIGHTHOUSE_API_KEY=your_actual_key
# ... (all other required variables)
```

---

## 🔗 **Step 4: Update Frontend API Calls**

Update your frontend to use the new backend URL:

```javascript
// In your API calls, replace localhost:8000 with:
const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://your-backend.vercel.app';

// Example API call:
const response = await fetch(`${BACKEND_URL}/discover_businesses?location=${location}&niche=${niche}`);
```

---

## 🧪 **Step 5: Test Deployment**

### **Test Frontend**
```bash
# Frontend should be accessible at:
https://your-project.vercel.app
```

### **Test Backend**
```bash
# Backend health check:
https://your-backend.vercel.app/health

# API endpoint test:
https://your-backend.vercel.app/discover_businesses?location=London&niche=gym
```

---

## 🔄 **Step 6: Set Up Auto-Deployment**

### **Frontend (Automatic)**
- ✅ Already configured via Git integration
- Every push to `main` branch triggers deployment

### **Backend (Manual or Auto)**
For automatic backend deployment, add to your CI/CD:

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend to Vercel
on:
  push:
    branches: [main]
    paths: ['backend/**']
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./backend
```

---

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **CORS Errors**
   - Ensure backend CORS allows frontend domain
   - Check environment variables are set correctly

2. **API Timeouts**
   - Vercel functions have 30s timeout limit
   - Optimize long-running operations

3. **Environment Variables**
   - Verify all required variables are set in Vercel
   - Check variable names match exactly

4. **Import Errors**
   - Ensure `PYTHONPATH` is set correctly
   - Check file structure matches imports

### **Debug Commands:**
```bash
# Check Vercel deployment status
vercel ls

# View deployment logs
vercel logs your-backend.vercel.app

# Redeploy backend
vercel --prod
```

---

## 🎉 **Success Indicators**

✅ Frontend accessible at `https://your-project.vercel.app`
✅ Backend health check returns success
✅ API endpoints respond correctly
✅ CORS working between frontend and backend
✅ Environment variables loaded properly

---

## 📚 **Next Steps**

1. **Monitor Performance**: Use Vercel Analytics
2. **Set Up Monitoring**: Configure error tracking
3. **Scale Up**: Add more serverless functions as needed
4. **Custom Domain**: Configure your own domain
5. **SSL**: HTTPS is automatically handled by Vercel

---

## 🆘 **Need Help?**

- **Vercel Docs**: https://vercel.com/docs
- **FastAPI on Vercel**: https://vercel.com/guides/deploying-fastapi
- **Next.js on Vercel**: https://vercel.com/guides/deploying-nextjs
