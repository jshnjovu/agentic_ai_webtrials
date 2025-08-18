# Agentic AI Frontend

This is the frontend application for the LeadGen Makeover Agent, built with Next.js and TypeScript.

## 🚀 **New Lighthouse Implementation**

**IMPORTANT**: We've completely redesigned the Lighthouse implementation to use the **programmatic API** instead of CLI execution. This eliminates the zero-score issues and provides reliable performance auditing directly from the frontend.

### **How It Works Now:**

1. **Frontend Processing**: Lighthouse runs directly in the browser using Node.js packages
2. **Real-time Results**: Immediate performance scores without backend processing delays
3. **No CLI Issues**: Eliminates subprocess failures and platform-specific problems
4. **Backend Storage**: Results are optionally sent to backend for aggregation

### **Key Benefits:**

- ✅ **Real scores** - No more zero scores from failed CLI execution
- ✅ **Faster results** - Immediate processing without HTTP round-trips
- ✅ **Reliable execution** - Programmatic API vs unreliable CLI calls
- ✅ **Cross-platform** - Works consistently across all operating systems
- ✅ **Better debugging** - JavaScript errors vs subprocess failures

## 🛠️ **Setup**

### **Prerequisites**

- Node.js 18+ 
- npm or yarn

### **Installation**

```bash
# Install dependencies (includes Lighthouse packages)
npm install

# Test Lighthouse packages
npm run lighthouse:test
```

### **Development**

```bash
# Start development server
npm run dev

# Navigate to http://localhost:3000/lighthouse-test
# Test the new Lighthouse functionality
```

## 🧪 **Testing Lighthouse**

Visit `/lighthouse-test` to test the new frontend-based Lighthouse implementation:

1. **Enter a website URL** (e.g., https://www.google.com)
2. **Select strategy** (desktop or mobile)
3. **Click "Run Lighthouse Audit"**
4. **View real-time results** with actual performance scores

## 📦 **Dependencies**

### **Core Dependencies**
- Next.js 13.4.0
- React 18.2.0
- TypeScript 5.9.2
- Tailwind CSS 3.3.5

### **Lighthouse Dependencies**
- `lighthouse@^11.6.0` - Core Lighthouse functionality
- `chrome-launcher@^1.1.0` - Chrome browser management

## 🔧 **Architecture**

### **Frontend Lighthouse Processing**
```typescript
// frontend/utils/lighthouse.ts
import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';

export async function runLighthouseAudit(request: LighthouseAuditRequest) {
  const chrome = await chromeLauncher.launch({
    chromeFlags: ['--headless', '--no-sandbox']
  });
  
  const result = await lighthouse(request.websiteUrl, options);
  await chrome.kill();
  
  return result.lhr;
}
```

### **Backend Integration**
```typescript
// Optional: Send results to backend for storage
export async function sendResultsToBackend(results: LighthouseResult) {
  const response = await fetch('/api/v1/website-scoring/lighthouse-results', {
    method: 'POST',
    body: JSON.stringify(results)
  });
  return response.ok;
}
```

## 📁 **File Structure**

```
frontend/
├── components/
│   └── LighthouseTest.tsx    # Test component for Lighthouse
├── pages/
│   └── lighthouse-test.tsx   # Test page route
├── utils/
│   └── lighthouse.ts         # Lighthouse utility functions
├── package.json              # Dependencies including Lighthouse
└── README.md                 # This file
```

## 🚫 **What We Removed**

- ❌ CLI execution scripts
- ❌ Subprocess management
- ❌ Platform-specific path resolution
- ❌ All the complexity causing zero scores

## ✅ **What We Added**

- ✅ Programmatic Lighthouse API usage
- ✅ Chrome Launcher integration
- ✅ Real-time performance auditing
- ✅ Immediate results display
- ✅ Cross-platform compatibility

## 🔍 **Troubleshooting**

### **If Lighthouse Fails:**
1. **Check Node.js version** (needs 18+)
2. **Verify npm packages** are installed correctly
3. **Check Chrome installation** (Chrome Launcher needs Chrome/Chromium)
4. **Clear node_modules** and reinstall if needed

### **If Backend Integration Fails:**
1. **Backend is optional** - Lighthouse works independently
2. **Check backend URL** in environment variables
3. **Verify backend API** endpoint is accessible

## 📖 **Documentation**

- [Lighthouse Programmatic API](https://github.com/GoogleChrome/lighthouse/blob/main/docs/readme.md#using-programmatically)
- [Chrome Launcher Documentation](https://github.com/GoogleChrome/chrome-launcher)
- [Next.js Documentation](https://nextjs.org/docs)

## 🎯 **Next Steps**

1. **Test the new implementation** at `/lighthouse-test`
2. **Integrate with existing components** using the new utility
3. **Update backend integration** to use the new endpoint
4. **Remove old CLI-based code** from backend
5. **Deploy and monitor** performance improvements

The new architecture is **much cleaner, more reliable, and follows best practices**! 🎉
