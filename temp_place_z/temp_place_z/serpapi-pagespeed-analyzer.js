const https = require('https');
const fs = require('fs');
require('dotenv').config({ path: './env.local' });

class SerpApiPageSpeedAnalyzer {
  constructor() {
    this.baseUrl = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
    this.googleApiKey = process.env.GOOGLE_GENERAL_API;
    this.serpApiResultsFile = './serpapi_test_results.json';
    this.results = [];
    
    if (!this.googleApiKey) {
      throw new Error('GOOGLE_GENERAL_API key not found in env.local file');
    }
  }

  // Load and parse SERP API results
  loadSerpApiResults() {
    try {
      if (!fs.existsSync(this.serpApiResultsFile)) {
        throw new Error(`SERP API results file not found: ${this.serpApiResultsFile}`);
      }
      
      const data = fs.readFileSync(this.serpApiResultsFile, 'utf8');
      const results = JSON.parse(data);
      
      if (!results.success || !results.results || !Array.isArray(results.results)) {
        throw new Error('Invalid SERP API results format');
      }
      
      console.log(`📊 Loaded ${results.results.length} results from SERP API`);
      console.log(`🔍 Query: "${results.query}" in ${results.location}`);
      console.log('='.repeat(60));
      
      return results;
    } catch (error) {
      console.error('❌ Error loading SERP API results:', error.message);
      throw error;
    }
  }

  // Extract websites from SERP API results
  extractWebsites(serpResults) {
    const websites = [];
    
    serpResults.results.forEach((result, index) => {
      if (result.website && result.website.startsWith('http')) {
        websites.push({
          index: index + 1,
          name: result.name,
          address: result.address,
          rating: result.rating,
          reviews: result.reviews,
          website: result.website,
          place_id: result.place_id
        });
      } else {
        console.log(`⚠️ Skipping ${result.name} - no valid website found`);
      }
    });
    
    console.log(`🌐 Found ${websites.length} valid websites to analyze`);
    return websites;
  }

  // Run PageSpeed Insights analysis on a website
  async runPageSpeedAnalysis(website, strategy = 'mobile') {
    try {
      console.log(`\n🔍 Analyzing: ${website.name} (${strategy})`);
      console.log(`🌐 Website: ${website.website}`);
      
      const apiUrl = `${this.baseUrl}?url=${encodeURIComponent(website.website)}&strategy=${strategy}&category=performance&category=accessibility&category=best-practices&category=seo&prettyPrint=true&key=${this.googleApiKey}`;
      
      const results = await this.makeRequest(apiUrl);
      return this.formatResults(results, website, strategy);
    } catch (error) {
      console.error(`❌ Error analyzing ${website.name}:`, error.message);
      throw error;
    }
  }

  // Make HTTP request to the PageSpeed API
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

  // Format the PageSpeed results
  formatResults(data, website, strategy) {
    const scores = data.lighthouseResult?.categories || {};
    const metrics = data.lighthouseResult?.audits || {};
    
    const results = {
      website: website,
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
      opportunities: this.extractOpportunities(metrics)
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

  // Print results in a formatted way
  printResults(results) {
    const website = results.website;
    
    console.log('\n' + '='.repeat(60));
    console.log(`📊 PageSpeed Results for ${website.name}`);
    console.log(`🌐 Website: ${website.website}`);
    console.log(`📍 Address: ${website.address}`);
    console.log(`⭐ Rating: ${website.rating}/5 (${website.reviews} reviews)`);
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
        if (opp.numericValue) {
          console.log(`     Potential savings: ${opp.numericValue} ${opp.numericUnit}`);
        }
      });
    }
    
    console.log('\n' + '='.repeat(60));
  }

  // Analyze all websites from SERP API results
  async analyzeAllWebsites() {
    try {
      console.log('🚀 Starting SERP API PageSpeed Analysis...\n');
      
      // Load SERP API results
      const serpResults = this.loadSerpApiResults();
      
      // Extract websites
      const websites = this.extractWebsites(serpResults);
      
      if (websites.length === 0) {
        console.log('❌ No valid websites found to analyze');
        return;
      }
      
      // Analyze each website with both mobile and desktop strategies
      for (const website of websites) {
        try {
          // Mobile analysis
          const mobileResults = await this.runPageSpeedAnalysis(website, 'mobile');
          this.printResults(mobileResults);
          this.results.push(mobileResults);
          
          // Desktop analysis
          const desktopResults = await this.runPageSpeedAnalysis(website, 'desktop');
          this.printResults(desktopResults);
          this.results.push(desktopResults);
          
        } catch (error) {
          console.error(`Failed to analyze ${website.name}:`, error.message);
        }
      }
      
      // Save results to file
      await this.saveResults(serpResults);
      
    } catch (error) {
      console.error('❌ Application failed:', error.message);
      process.exit(1);
    }
  }

  // Save results to file
  async saveResults(serpResults) {
    try {
      const filename = `serpapi-pagespeed-results-${new Date().toISOString().split('T')[0]}.json`;
      
      const allResults = {
        serpApiQuery: {
          query: serpResults.query,
          location: serpResults.location,
          totalResults: serpResults.total_results
        },
        analysisTimestamp: new Date().toISOString(),
        results: this.results
      };
      
      fs.writeFileSync(filename, JSON.stringify(allResults, null, 2));
      console.log(`\n💾 Results saved to ${filename}`);
      
      return filename;
    } catch (error) {
      console.error('❌ Error saving results:', error.message);
      return null;
    }
  }
}

// Main execution function
async function main() {
  const analyzer = new SerpApiPageSpeedAnalyzer();
  
  try {
    await analyzer.analyzeAllWebsites();
  } catch (error) {
    console.error('❌ Application failed:', error.message);
    process.exit(1);
  }
}

// Run the application if this file is executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = SerpApiPageSpeedAnalyzer;
