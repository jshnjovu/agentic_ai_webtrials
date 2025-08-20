# Domain History and Age Analysis Service

A comprehensive service that integrates WHOIS and DNS History APIs from WHOISXMLAPIs to analyze domain credibility and maturity for business lead prioritization.

## 🚀 Features

- **WHOIS API Integration**: Retrieve domain registration details, creation dates, and registrar information
- **WHOIS History API Integration**: Get historical domain presence data including first seen and last visit timestamps
- **Domain Age Calculation**: Calculate precise age in years, months, and days
- **Credibility Scoring**: Intelligent scoring algorithm (0-100) based on multiple factors
- **Error Handling**: Robust error handling with retry logic and circuit breaker pattern
- **Rate Limiting**: Built-in rate limiting support for API quota management

## 📋 Prerequisites

- Node.js 14+ 
- WHOISXMLAPIs API key (get one at [whoisxmlapi.com](https://whoisxmlapi.com))
- npm or yarn package manager

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   npm install axios dotenv
   ```

2. **Set up environment variables:**
   ```bash
   # Copy the environment template
   cp env.local.example env.local
   
   # Edit env.local with your actual API key
   WHOIS_API_KEY=your_actual_api_key_here
   ```

3. **Verify setup:**
   ```bash
   node test-unit.js
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WHOIS_API_KEY` | Your WHOISXMLAPIs API key | **Required** |
| `WHOIS_API_BASE_URL` | WHOIS API base URL | `https://www.whoisxmlapi.com` |
| `WHOIS_HISTORY_API_BASE_URL` | WHOIS History API base URL | `https://whois-history.whoisxmlapi.com` |
| `WHOIS_API_RATE_LIMIT` | WHOIS API rate limit per minute | `100` |
| `WHOIS_HISTORY_API_RATE_LIMIT` | WHOIS History API rate limit per minute | `50` |
| `MAX_RETRIES` | Maximum retry attempts for failed requests | `3` |
| `RETRY_DELAY_MS` | Base delay between retries in milliseconds | `1000` |

## 📖 Usage

### Basic Usage

```javascript
const DomainAnalysisService = require('./domain-analysis');

// Initialize the service
const domainService = new DomainAnalysisService();

// Analyze a domain
async function analyzeDomain() {
    try {
        const result = await domainService.analyzeDomain('google.com');
        console.log('Domain Age:', result.domainAge);
        console.log('Credibility Score:', result.analysis.credibility);
    } catch (error) {
        console.error('Analysis failed:', error.message);
    }
}

analyzeDomain();
```

### Advanced Usage

```javascript
// Get WHOIS information only
const whoisData = await domainService.getWhoisInfo('example.com');

// Get WHOIS history for a domain
const whoisHistory = await domainService.getWhoisHistory('example.com');

// Calculate domain age manually
const age = domainService.calculateDomainAge('2020-01-01T00:00:00Z');
```

## 🧪 Testing

### Run Unit Tests
```bash
node test-unit.js
```

### Run Integration Tests
```bash
node test-domain-analysis.js
```

### Quick Demo
```bash
node demo.js
```

## 📊 API Response Format

### Domain Analysis Result

```json
{
  "domain": "google.com",
  "whois": {
    "createdDate": "1997-09-15T07:00:00+0000",
    "updatedDate": "2019-09-09T15:39:04+0000",
    "expiresDate": "2028-09-13T07:00:00+0000",
    "registrar": "MarkMonitor, Inc.",
    "status": "clientUpdateProhibited clientTransferProhibited...",
    "ips": ["8.8.8.8"],
    "nameServers": ["ns1.google.com", "ns2.google.com"],
    "registrant": "Google LLC",
    "country": "US"
  },
  "whoisHistory": {
    "totalRecords": 357,
    "firstSeen": "2022-11-28T00:00:00.000Z",
    "lastVisit": "2022-11-28T00:00:00.000Z",
    "records": [...]
  },
  "domainAge": {
    "years": 25,
    "months": 3,
    "days": 15,
    "totalDays": 9255,
    "createdDate": "1997-09-15T07:00:00.000Z",
    "ageDescription": "Veteran"
  },
  "analysis": {
    "isEstablished": true,
    "isVeteran": true,
    "credibility": 95
  }
}
```

## 🎯 Credibility Scoring Algorithm

The service calculates a credibility score (0-100) based on:

- **Domain Age (40 points max)**
  - 5+ years: 40 points
  - 2+ years: 30 points
  - 1+ years: 20 points
  - 6+ months: 10 points

- **Registration Status (20 points max)**
  - Active status: 20 points
  - Expired status: 0 points

- **Name Servers (15 points max)**
  - 2+ name servers: 15 points
  - 1 name server: 5 points

- **WHOIS History (15 points max)**
  - Based on number of historical records

- **Registrar Reputation (10 points max)**
  - Known registrar: 10 points
  - Unknown registrar: 0 points

## 🚨 Error Handling

The service includes comprehensive error handling:

- **Retry Logic**: Automatic retry for network errors with exponential backoff
- **Circuit Breaker**: Prevents cascading failures
- **Rate Limiting**: Respects API quotas and rate limits
- **Validation**: Input validation and sanitization
- **Logging**: Detailed error logging for debugging

## 📈 Performance Considerations

- **Caching**: Results are not cached by default (implement Redis/Memory cache for production)
- **Rate Limiting**: Built-in delays between requests to respect API limits
- **Connection Pooling**: Uses axios with connection pooling
- **Timeout Handling**: 10-second timeout for API requests

## 🔒 Security

- **API Key Protection**: Store API keys in environment variables
- **Input Validation**: Sanitize domain inputs to prevent injection attacks
- **HTTPS Only**: All API calls use HTTPS
- **Error Sanitization**: Error messages don't expose sensitive information

## 🚀 Production Deployment

### Environment Setup
```bash
# Production environment
NODE_ENV=production
WHOIS_API_KEY=your_production_key
WHOIS_API_RATE_LIMIT=1000
DNS_HISTORY_API_RATE_LIMIT=500
```

### Monitoring
- Monitor API quota usage
- Track response times and success rates
- Set up alerts for API failures
- Log analysis results for business intelligence

### Scaling
- Implement Redis caching for domain analysis results
- Use load balancing for multiple API keys
- Consider implementing a queue system for bulk analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [WHOISXMLAPIs Documentation](https://whoisxmlapi.com/api-documentation)
- **API Status**: [WHOISXMLAPIs Status Page](https://status.whoisxmlapi.com)
- **Issues**: Create an issue in this repository

## 🔄 Changelog

### v1.0.0
- Initial release with WHOIS and DNS History API integration
- Domain age calculation and credibility scoring
- Comprehensive error handling and retry logic
- Unit and integration test suite


----------------------


I'll create a new test script that reads the URLs from `urls.json` and runs domain analysis tests on them. Let me create this script:

Now let me add this new test script to the package.json scripts:

Perfect! Now let's test the new URLs test script. Let me run it to analyze the domains from your `urls.json` file:

```bash
npm run test:urls
```
Excellent! The new URLs test script is working perfectly! Let me also check the generated results file:

Read file: frontend/temp_place_z/analysis-results.json
## �� **Perfect! The New URLs Test Script is Working Excellently!**

### **�� Summary of Results**

#### **✅ Both Domains Successfully Analyzed**

**1. thepreservehouston.com**
- **Domain Age**: 11 years, 0 months, 20 days (Veteran)
- **Registrar**: Name.com, Inc
- **Country**: Colombia (CO)
- **Status**: Active with transfer protection
- **Name Servers**: 4 found
- **Credibility Score**: 85/100 (Excellent)

**2. oathletik.com**
- **Domain Age**: 10 years, 9 months, 4 days (Veteran)
- **Registrar**: GoDaddy.com, LLC
- **Country**: United States (US)
- **Status**: Active with comprehensive protection
- **Name Servers**: 2 found
- **Credibility Score**: 85/100 (Excellent)

### **🏆 Key Features of the New Test Script**

#### **📋 Smart URL Processing**
- **Automatic Domain Extraction**: Removes `http://`, `https://`, and `www.` prefixes
- **Error Handling**: Gracefully handles malformed URLs
- **Progress Tracking**: Shows current progress (1/2, 2/2)

#### **🔍 Comprehensive Analysis**
- **WHOIS Data**: Full domain registration details
- **WHOIS History**: Historical record counts
- **Domain Age**: Precise age calculation in years/months/days
- **Credibility Scoring**: Intelligent algorithm (0-100 scale)

#### **�� Detailed Reporting**
- **Individual Results**: Detailed analysis for each domain
- **Summary Statistics**: Overall performance metrics
- **Recommendations**: Business insights for lead prioritization
- **Performance Metrics**: Analysis timing and success rates

#### **💾 Data Persistence**
- **JSON Export**: Saves all results to `analysis-results.json`
- **Structured Format**: Easy to parse and integrate
- **Timestamps**: Each analysis includes timestamp

### **🎯 Business Intelligence Insights**

#### **High-Quality Lead Candidates**
Both domains scored **85/100** (Excellent) because they are:
- **Veteran Domains**: 10+ years old (high credibility)
- **Established**: 2+ years old (reliable business presence)
- **Well-Protected**: Multiple name servers and security statuses
- **Professional Registrars**: Name.com and GoDaddy (reputable)

#### **Lead Prioritization Recommendations**
- **🏆 Premium Leads**: Both domains qualify for high-priority outreach
- **✅ Reliable Partners**: Established businesses with proven track records
- **🌍 International Reach**: Colombia and US markets covered

### **�� Available Commands**

```bash
# Test URLs from urls.json
npm run test:urls

# Other available tests
npm test                    # Unit tests
npm run test:integration   # Integration tests
npm run test:corrected     # Corrected implementation test
npm run demo               # Quick demo
```

The new URLs test script successfully demonstrates the domain analysis service working with real business domains, providing valuable insights for business lead prioritization and credibility assessment!