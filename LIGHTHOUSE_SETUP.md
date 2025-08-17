# Lighthouse CLI Integration Guide

This document explains how to set up and use Lighthouse CLI for website performance auditing in the LeadGen Makeover Agent project.

## Overview

We've migrated from Google PageSpeed Insights API to **Lighthouse CLI** for the following reasons:

- **Better Performance**: Direct CLI execution is faster than API calls
- **More Control**: Full control over audit parameters and Chrome flags
- **Cost Effective**: No API rate limits or costs
- **Local Testing**: Can test local development sites
- **CI/CD Integration**: Better integration with automated workflows

## Prerequisites

- **Node.js 18+** installed on your system
- **npm** package manager
- **Chrome/Chromium** browser (for Lighthouse to work)

## Installation

### Option 1: Automated Setup (Recommended)

#### Backend Setup
```bash
# Navigate to backend directory
cd backend

# Run setup script (Linux/macOS)
chmod +x scripts/setup-lighthouse.sh
./scripts/setup-lighthouse.sh

# Or run PowerShell script (Windows)
.\scripts\setup-lighthouse.ps1
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Run setup script (Linux/macOS)
chmod +x scripts/setup-lighthouse.sh
./scripts/setup-lighthouse.sh

# Or run PowerShell script (Windows)
.\scripts\setup-lighthouse.ps1
```

### Option 2: Manual Installation

```bash
# Install Lighthouse CLI globally
npm install -g lighthouse@latest

# Install Lighthouse CI
npm install -g @lhci/cli@latest

# Install project dependencies
npm install
```

## Configuration

### Environment Variables

Update your `.env` file with the following Lighthouse-specific settings:

```bash
# Lighthouse CLI Configuration
LIGHTHOUSE_CLI_PATH=lighthouse  # or 'npx lighthouse' if not installed globally
LIGHTHOUSE_CHROME_PATH=  # Optional: path to Chrome/Chromium executable

# Rate Limiting (reduced for CLI-based audits)
LIGHTHOUSE_RATE_LIMIT_PER_DAY=100
LIGHTHOUSE_RATE_LIMIT_PER_MINUTE=2

# Timeout Settings (increased for CLI audits)
LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS=120
LIGHTHOUSE_FALLBACK_TIMEOUT_SECONDS=60
```

### Lighthouse CI Configuration

Both `backend/lighthouserc.js` and `frontend/lighthouserc.js` are configured with:

- **Performance thresholds**: 70+ for warnings
- **Accessibility thresholds**: 80+ for warnings
- **Best Practices thresholds**: 80+ for warnings
- **SEO thresholds**: 80+ for warnings
- **Core Web Vitals**: Specific timing thresholds

## Usage

### Command Line

#### Basic Audit
```bash
# Test Lighthouse CLI
npm run lighthouse:test

# Run single audit
npm run lighthouse:audit

# Run CI workflow
npm run lighthouse:ci
```

#### Custom Audit
```bash
# Desktop audit
lighthouse https://example.com --output=json --output-path=./report.json --only-categories=performance,accessibility,best-practices,seo

# Mobile audit
lighthouse https://example.com --form-factor=mobile --output=json --output-path=./report.json

# Performance-only audit
lighthouse https://example.com --only-categories=performance --output=json --output-path=./report.json
```

### Programmatic Usage

#### Backend (Python)
```python
from src.services.lighthouse_service import LighthouseService

service = LighthouseService()
result = service.run_lighthouse_audit(
    website_url="https://example.com",
    business_id="business-123",
    run_id="run-456",
    strategy="desktop"
)

if result["success"]:
    print(f"Performance Score: {result['scores']['performance']}/100")
    print(f"Overall Score: {result['overall_score']}/100")
```

#### Frontend (TypeScript)
```typescript
import { runLighthouseAudit } from '../utils/lighthouse';

const result = await runLighthouseAudit({
  websiteUrl: 'https://example.com',
  businessId: 'business-123',
  strategy: 'desktop'
});

if (result.success) {
  console.log(`Performance Score: ${result.scores.performance}/100`);
  console.log(`Overall Score: ${result.overallScore}/100`);
}
```

## API Endpoints

### Backend API
```
POST /api/v1/website-scoring/lighthouse
```

**Request Body:**
```json
{
  "website_url": "https://example.com",
  "business_id": "business-123",
  "run_id": "run-456",
  "strategy": "desktop"
}
```

**Response:**
```json
{
  "success": true,
  "website_url": "https://example.com",
  "business_id": "business-123",
  "run_id": "run-456",
  "audit_timestamp": 1703123456.789,
  "strategy": "desktop",
  "scores": {
    "performance": 85.2,
    "accessibility": 92.1,
    "best_practices": 88.7,
    "seo": 95.3
  },
  "overall_score": 90.3,
  "core_web_vitals": {
    "first_contentful_paint": 1200,
    "largest_contentful_paint": 2100,
    "cumulative_layout_shift": 0.05,
    "total_blocking_time": 150,
    "speed_index": 1800
  },
  "confidence": "high"
}
```

## Troubleshooting

### Common Issues

#### 1. Lighthouse Command Not Found
```bash
# Install globally
npm install -g lighthouse@latest

# Or use npx
npx lighthouse --version
```

#### 2. Chrome/Chromium Not Found
```bash
# Install Chrome
# Linux: sudo apt-get install google-chrome-stable
# macOS: brew install --cask google-chrome
# Windows: Download from https://www.google.com/chrome/

# Or specify Chrome path in .env
LIGHTHOUSE_CHROME_PATH=/usr/bin/google-chrome
```

#### 3. Permission Denied (Linux/macOS)
```bash
# Make scripts executable
chmod +x scripts/setup-lighthouse.sh

# Or run with sudo (not recommended)
sudo npm install -g lighthouse@latest
```

#### 4. Timeout Issues
```bash
# Increase timeout in .env
LIGHTHOUSE_AUDIT_TIMEOUT_SECONDS=180
LIGHTHOUSE_FALLBACK_TIMEOUT_SECONDS=90
```

### Debug Mode

Enable debug logging by setting in `.env`:
```bash
DEBUG=True
```

### Performance Optimization

For faster audits:
```bash
# Use performance-only category
lighthouse https://example.com --only-categories=performance

# Reduce throttling
lighthouse https://example.com --throttling.cpuSlowdownMultiplier=1

# Disable unnecessary audits
lighthouse https://example.com --skip-audits=uses-http2,uses-long-cache-ttl
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Lighthouse CI
on: [push, pull_request]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run lighthouse:ci
```

### Local CI Testing

```bash
# Test CI configuration
lhci autorun

# Collect data only
lhci collect

# Assert against thresholds
lhci assert

# Upload to temporary storage
lhci upload
```

## Migration from PageSpeed Insights

### What Changed

1. **API Endpoint**: No more Google PageSpeed Insights API calls
2. **Authentication**: No API key required
3. **Rate Limits**: Reduced from 25,000/day to 100/day (CLI-based)
4. **Timeout**: Increased from 30s to 120s for CLI execution
5. **Data Structure**: Direct Lighthouse output instead of wrapped API response

### Code Changes Required

1. **Remove API key references** from environment files
2. **Update timeout configurations** for CLI-based execution
3. **Adjust rate limiting** for reduced CLI usage
4. **Update error handling** for CLI-specific error codes

## Best Practices

1. **Run audits during off-peak hours** to avoid impacting development
2. **Use fallback audits** for timeout scenarios
3. **Cache results** when possible to reduce repeated audits
4. **Monitor performance** of the CLI execution itself
5. **Keep Chrome/Chromium updated** for best compatibility

## Support

- **Lighthouse Documentation**: https://developer.chrome.com/docs/lighthouse/overview
- **Lighthouse CI**: https://github.com/GoogleChrome/lighthouse-ci
- **Project Issues**: Check the project's GitHub repository

## License

This integration follows the same license as the main project.
