const https = require('https');
const fs = require('fs');
const path = require('path');

// Load environment variables
require('dotenv').config({ path: './env.local' });

// Use Google API key instead of service account
const GOOGLE_API_KEY = process.env.GOOGLE_GENERAL_API;

if (!GOOGLE_API_KEY) {
  throw new Error('GOOGLE_GENERAL_API key not found in env.local file');
}

class PageSpeedInsightsAPI {
  constructor() {
    this.baseUrl = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
  }

  // Initialize API using API key
  async initialize() {
    try {
      console.log('✅ PageSpeed Insights API initialized with API key');
    } catch (error) {
      console.error('❌ Error initializing API:', error.message);
      throw error;
    }
  }

  // Run PageSpeed Insights analysis
  async runPageSpeedAnalysis(url, strategy = 'mobile') {
    try {
      console.log(`\n🔍 Analyzing: ${url} (${strategy})`);
      
      const apiUrl = `${this.baseUrl}?url=${encodeURIComponent(url)}&strategy=${strategy}&category=performance&category=accessibility&category=best-practices&category=seo&prettyPrint=true&key=${GOOGLE_API_KEY}`;
      
      const results = await this.makeRequest(apiUrl);
      return this.formatResults(results, url, strategy);
    } catch (error) {
      console.error(`❌ Error analyzing ${url}:`, error.message);
      throw error;
    }
  }

  // Make HTTP request to the API
  makeRequest(url) {
    return new Promise((resolve, reject) => {
      const requestOptions = new URL(url);
      requestOptions.headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'identity'
      };

      https.get(requestOptions, (res) => {
        let data = '';

        res.on('data', (chunk) => {
          data += chunk;
        });

        res.on('end', () => {
          try {
            const jsonData = JSON.parse(data);
            if (jsonData.error) {
              reject(new Error(jsonData.error.message || 'API Error'));
            } else {
              resolve(jsonData);
            }
          } catch (error) {
            reject(new Error('Failed to parse API response'));
          }
        });
      }).on('error', (error) => {
        reject(error);
      });
    });
  }

  // Format the results in a readable way
  formatResults(data, url, strategy) {
    const scores = data.lighthouseResult?.categories || {};
    const metrics = data.lighthouseResult?.audits || {};
    
    const results = {
      url: url,
      strategy: strategy,
      timestamp: new Date().toISOString(),
      scores: {
        performance: Math.round(scores.performance?.score * 100) || 'N/A',
        accessibility: Math.round(scores.accessibility?.score * 100) || 'N/A',
        bestPractices: Math.round(scores['best-practices']?.score * 100) || 'N/A',
        seo: Math.round(scores.seo?.score * 100) || 'N/A'
      },
      metrics: {
        firstContentfulPaint: this.extractMetric(metrics['first-contentful-paint']),
        largestContentfulPaint: this.extractMetric(metrics['largest-contentful-paint']),
        firstInputDelay: this.extractMetric(metrics['max-potential-fid']),
        cumulativeLayoutShift: this.extractMetric(metrics['cumulative-layout-shift']),
        speedIndex: this.extractMetric(metrics['speed-index'])
      },
      opportunities: this.extractOpportunities(metrics),
      diagnostics: this.extractDiagnostics(metrics)
    };

    return results;
  }

  // Extract metric values
  extractMetric(audit) {
    if (!audit) return 'N/A';
    return {
      value: audit.numericValue,
      unit: audit.numericUnit,
      displayValue: audit.displayValue
    };
  }

  // Extract optimization opportunities
  extractOpportunities(metrics) {
    const opportunities = [];
    Object.keys(metrics).forEach(key => {
      if (metrics[key].details && metrics[key].details.type === 'opportunity') {
        opportunities.push({
          title: metrics[key].title,
          description: metrics[key].description,
          score: metrics[key].score,
          numericValue: metrics[key].numericValue,
          numericUnit: metrics[key].numericUnit
        });
      }
    });
    return opportunities.slice(0, 5); // Return top 5 opportunities
  }

  // Extract diagnostic information
  extractDiagnostics(metrics) {
    const diagnostics = [];
    Object.keys(metrics).forEach(key => {
      if (metrics[key].details && metrics[key].details.type === 'diagnostic') {
        diagnostics.push({
          title: metrics[key].title,
          description: metrics[key].description,
          details: metrics[key].details
        });
      }
    });
    return diagnostics.slice(0, 3); // Return top 3 diagnostics
  }

  // Print results in a formatted way
  printResults(results) {
    console.log('\n' + '='.repeat(60));
    console.log(`📊 PageSpeed Insights Results for ${results.url}`);
    console.log(`📱 Strategy: ${results.strategy}`);
    console.log(`⏰ Timestamp: ${results.timestamp}`);
    console.log('='.repeat(60));
    
    console.log('\n🏆 SCORES:');
    console.log(`  Performance: ${results.scores.performance}/100`);
    console.log(`  Accessibility: ${results.scores.accessibility}/100`);
    console.log(`  Best Practices: ${results.scores.bestPractices}/100`);
    console.log(`  SEO: ${results.scores.seo}/100`);
    
    console.log('\n📈 CORE WEB VITALS:');
    Object.entries(results.metrics).forEach(([key, metric]) => {
      if (metric !== 'N/A') {
        console.log(`  ${key}: ${metric.displayValue || metric.value} ${metric.unit || ''}`);
      }
    });
    
    if (results.opportunities.length > 0) {
      console.log('\n💡 TOP OPTIMIZATION OPPORTUNITIES:');
      results.opportunities.forEach((opp, index) => {
        console.log(`  ${index + 1}. ${opp.title}`);
        console.log(`     Potential savings: ${opp.numericValue} ${opp.numericUnit}`);
      });
    }
    
    console.log('\n' + '='.repeat(60));
  }
}

// Main execution function
async function main() {
  const api = new PageSpeedInsightsAPI();
  
  try {
    // Initialize the API
    await api.initialize();
    
    // Test URLs to analyze
    const testUrls = [
      'https://www.google.com',
      'https://www.github.com',
      'https://www.stackoverflow.com'
    ];
    
    // Analyze each URL with both mobile and desktop strategies
    for (const url of testUrls) {
      try {
        // Mobile analysis
        const mobileResults = await api.runPageSpeedAnalysis(url, 'mobile');
        api.printResults(mobileResults);
        
        // Desktop analysis
        const desktopResults = await api.runPageSpeedAnalysis(url, 'desktop');
        api.printResults(desktopResults);
        
        // Save results to file
        const filename = `pagespeed-results-${new Date().toISOString().split('T')[0]}.json`;
        const allResults = {
          mobile: mobileResults,
          desktop: desktopResults
        };
        
        fs.writeFileSync(filename, JSON.stringify(allResults, null, 2));
        console.log(`💾 Results saved to ${filename}`);
        
      } catch (error) {
        console.error(`Failed to analyze ${url}:`, error.message);
      }
    }
    
  } catch (error) {
    console.error('❌ Application failed:', error.message);
    process.exit(1);
  }
}

// Run the application if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = PageSpeedInsightsAPI;
