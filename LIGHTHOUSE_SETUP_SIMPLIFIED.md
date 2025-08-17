# Lighthouse CLI Setup - Simplified Architecture

## 🎯 **Architecture Overview**

We've simplified the Lighthouse setup to follow the **correct separation of concerns**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                      │
│              (NO Lighthouse CLI needed)                    │
│                                                             │
│  • lighthouse.ts utility (HTTP client only)               │
│  • Makes API calls to backend                             │
│  • Formats and displays results                            │
│  • Pure client-side functionality                          │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP API calls
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                       │
│              (ONLY place that needs CLI)                   │
│                                                             │
│  • LighthouseService (executes CLI)                        │
│  • CLI installation & execution                            │
│  • Real performance auditing                               │
│  • API endpoints for frontend                              │
└─────────────────────────────────────────────────────────────┘
```

## 🚫 **What We Removed (Frontend):**

- ❌ Lighthouse CLI installation
- ❌ Lighthouse CI configuration  
- ❌ Setup scripts
- ❌ CLI dependencies
- ❌ Unnecessary npm scripts

## ✅ **What We Kept (Backend):**

- ✅ Lighthouse CLI installation
- ✅ Lighthouse CI configuration
- ✅ Setup scripts (Windows & Linux)
- ✅ CLI dependencies
- ✅ All necessary npm scripts

## 🚀 **Setup Process (Backend Only):**

### **Step 1: Backend Setup**
```bash
# Navigate to backend directory
cd backend

# Run setup script (Windows)
.\scripts\setup-lighthouse.ps1

# Or run setup script (Linux/macOS)
chmod +x scripts/setup-lighthouse.sh
./scripts/setup-lighthouse.sh
```

### **Step 2: Frontend Setup**
```bash
# Navigate to frontend directory
cd frontend

# Just install regular dependencies (no Lighthouse CLI needed!)
npm install
```

## 🔍 **Why This Architecture Makes Sense:**

### **Backend (Python) - NEEDS CLI:**
- **Executes actual Lighthouse audits** via subprocess
- **Handles real performance testing** of websites
- **Manages CLI installation** and execution
- **Provides API endpoints** for frontend to consume

### **Frontend (TypeScript) - NO CLI NEEDED:**
- **Just makes HTTP requests** to backend API
- **Displays results** and formats data
- **No performance auditing** - that's backend's job
- **Pure client-side utility** functions

## 📋 **What Each Part Does:**

### **Backend LighthouseService:**
```python
# This is where the real work happens
def _execute_lighthouse_cli(self, website_url: str, strategy: str, ...):
    cmd = [
        self.lighthouse_path,  # CLI executable
        website_url,
        '--output=json',
        '--only-categories=performance,accessibility,best-practices,seo'
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=self.timeout)
```

### **Frontend lighthouse.ts:**
```typescript
// This is just an HTTP client - no CLI needed!
export async function runLighthouseAudit(request: LighthouseAuditRequest): Promise<LighthouseResult> {
  const response = await fetch(`${backendUrl}/api/v1/website-scoring/lighthouse`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request)
  });
  return response.json();
}
```

## 🧪 **Testing the Setup:**

### **Backend Testing:**
```bash
cd backend

# Test Lighthouse CLI
npm run lighthouse:test

# Run single audit
npm run lighthouse:audit

# Run CI workflow
npm run lighthouse:ci
```

### **Frontend Testing:**
```bash
cd frontend

# Just regular frontend tests
npm test

# No Lighthouse CLI needed!
```

## 🔧 **Troubleshooting:**

### **If Backend Setup Fails:**
1. **Check Node.js version** (needs 18+)
2. **Verify npm installation**
3. **Run PowerShell as Administrator** if needed
4. **Check Chrome/Chromium installation**

### **If Frontend Has Issues:**
1. **Frontend doesn't need Lighthouse CLI** - it's just a client
2. **Check backend API** is running and accessible
3. **Verify environment variables** for backend URL

## 🎉 **Benefits of This Architecture:**

1. **Cleaner separation** of concerns
2. **Easier maintenance** - only one place to manage CLI
3. **Reduced complexity** - frontend stays lightweight
4. **Better security** - CLI execution only on backend
5. **Simplified deployment** - no CLI needed in frontend containers
6. **Clear API boundaries** - frontend consumes, backend provides

## 📚 **Files Structure After Cleanup:**

```
backend/
├── package.json              # ✅ Has Lighthouse CLI dependencies
├── lighthouserc.js          # ✅ Has Lighthouse CI config
├── scripts/
│   ├── setup-lighthouse.sh  # ✅ Linux/macOS setup
│   └── setup-lighthouse.ps1 # ✅ Windows setup
└── src/services/
    └── lighthouse_service.py # ✅ Executes CLI commands

frontend/
├── package.json              # ❌ No Lighthouse CLI dependencies
├── utils/
│   └── lighthouse.ts         # ✅ HTTP client utility only
└── scripts/                  # ❌ No setup scripts needed
```

## 🚀 **Next Steps:**

1. **Run backend setup** to install Lighthouse CLI
2. **Test backend functionality** with npm scripts
3. **Verify frontend can connect** to backend API
4. **Run end-to-end tests** to ensure everything works

The architecture is now clean, logical, and follows best practices! 🎯
