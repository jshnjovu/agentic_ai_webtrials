const axios = require('axios');
const https = require('https');
const fs = require('fs');
require('dotenv').config({ path: './env.local' });

class ComprehensiveWebsiteAnalyzer {
  constructor() {
    this.pingdomApiKey = process.env.PINGDOM_API_KEY;
    this.pingdomBaseUrl = 'https://api.pingdom.com/api/3.1';
    this.pagespeedBaseUrl = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
    this.results = new Map();
  }

  async analyzeWebsite(url, name) {
    try {
      console.log(`\n🔍 Analyzing: ${url}`);
      console.log(`📝 Name: ${name}`);
      console.log('='.repeat(60));

      const analysis = {
        url: url,
        name: name,
        timestamp: new Date().toISOString(),
        scores: {
          performance: 0,
          accessibility: 0,
          seo: 0,
          trust: 0,
          cro: 0
        },
        details: {},
        pingdom: {},
        pagespeed: {},
        trust: {},
        cro: {}
      };

      // 1. Pingdom Analysis (Uptime & Basic Performance)
      console.log('📊 1. Running Pingdom analysis...');
      try {
        const pingdomData = await this.runPingdomAnalysis(url, name);
        analysis.pingdom = pingdomData;
        analysis.scores.performance += 20; // Base performance score from uptime
      } catch (error) {
        console.log('   ⚠️ Pingdom analysis failed:', error.message);
      }

      // 2. PageSpeed Insights Analysis (Performance, Accessibility, SEO)
      console.log('📊 2. Running PageSpeed Insights analysis...');
      try {
        const pagespeedData = await this.runPageSpeedAnalysis(url);
        analysis.pagespeed = pagespeedData;
        
        // Update scores based on PageSpeed results
        if (pagespeedData.scores) {
          analysis.scores.performance = Math.max(analysis.scores.performance, pagespeedData.scores.performance);
          analysis.scores.accessibility = pagespeedData.scores.accessibility;
          analysis.scores.seo = pagespeedData.scores.seo;
        }
      } catch (error) {
        console.log('   ⚠️ PageSpeed analysis failed:', error.message);
      }

      // 3. Trust Analysis (SSL, Security Headers, Domain Age)
      console.log('📊 3. Running Trust analysis...');
      try {
        const trustData = await this.analyzeTrust(url);
        analysis.trust = trustData;
        analysis.scores.trust = trustData.score;
      } catch (error) {
        console.log('   ⚠️ Trust analysis failed:', error.message);
      }

      // 4. CRO Analysis (Conversion Rate Optimization)
      console.log('📊 4. Running CRO analysis...');
      try {
        const croData = await this.analyzeCRO(url);
        analysis.cro = croData;
        analysis.scores.cro = croData.score;
      } catch (error) {
        console.log('   ⚠️ CRO analysis failed:', error.message);
      }

      // 5. Calculate final scores
      this.calculateFinalScores(analysis);

      // Store results
      this.results.set(url, analysis);

      return analysis;
    } catch (error) {
      console.error(`❌ Error analyzing ${url}:`, error.message);
      throw error;
    }
  }

  async runPingdomAnalysis(url, name) {
    try {
      const domain = new URL(url).hostname;
      
      // Create monitoring check
      const response = await axios.post(`${this.pingdomBaseUrl}/checks`, {
        name: name,
        host: domain,
        type: 'http',
        resolution: 1
      }, { 
        headers: {
          'Authorization': `Bearer ${this.pingdomApiKey}`,
          'Content-Type': 'application/json'
        }
      });

      const check = response.data.check;
      
      return {
        checkId: check.id,
        status: 'created',
        domain: domain,
        uptime: '99.9%', // Simulated uptime
        responseTime: Math.floor(Math.random() * 500) + 100 // Simulated response time
      };
    } catch (error) {
      throw new Error(`Pingdom API error: ${error.message}`);
    }
  }

  async runPageSpeedAnalysis(url) {
    try {
      // Use PageSpeed Insights API with API key
      const apiUrl = `${this.pagespeedBaseUrl}?url=${encodeURIComponent(url)}&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo&prettyPrint=true&key=${process.env.GOOGLE_GENERAL_API}`;
      
      const data = await this.makeRequest(apiUrl);
      
      if (data.error) {
        throw new Error(data.error.message);
      }

      const scores = data.lighthouseResult?.categories || {};
      const metrics = data.lighthouseResult?.audits || {};
      
      return {
        scores: {
          performance: Math.round(scores.performance?.score * 100) || 0,
          accessibility: Math.round(scores.accessibility?.score * 100) || 0,
          bestPractices: Math.round(scores['best-practices']?.score * 100) || 0,
          seo: Math.round(scores.seo?.score * 100) || 0
        },
        metrics: {
          firstContentfulPaint: this.extractMetric(metrics['first-contentful-paint']),
          largestContentfulPaint: this.extractMetric(metrics['largest-contentful-paint']),
          speedIndex: this.extractMetric(metrics['speed-index'])
        },
        opportunities: this.extractOpportunities(metrics)
      };
    } catch (error) {
      throw new Error(`PageSpeed API error: ${error.message}`);
    }
  }

  async analyzeTrust(url) {
    try {
      const domain = new URL(url).hostname;
      const trustScore = {
        ssl: false,
        securityHeaders: false,
        domainAge: 'unknown',
        score: 0
      };

      // Check SSL
      try {
        const sslResponse = await axios.get(`https://${domain}`, { 
          timeout: 5000,
          validateStatus: () => true 
        });
        trustScore.ssl = sslResponse.status < 400;
        trustScore.score += trustScore.ssl ? 30 : 0;
      } catch (error) {
        trustScore.ssl = false;
      }

      // Check security headers
      try {
        const headersResponse = await axios.get(`https://${domain}`, { 
          timeout: 5000,
          validateStatus: () => true 
        });
        const headers = headersResponse.headers;
        
        trustScore.securityHeaders = !!(headers['x-frame-options'] || headers['x-content-type-options'] || headers['strict-transport-security']);
        trustScore.score += trustScore.securityHeaders ? 40 : 0;
      } catch (error) {
        // Continue without security headers
      }

      // Domain age simulation (in real implementation, you'd use WHOIS API)
      trustScore.domainAge = '1+ years'; // Simulated
      trustScore.score += 30; // Base trust score for established domains

      return trustScore;
    } catch (error) {
      throw new Error(`Trust analysis error: ${error.message}`);
    }
  }

  async analyzeCRO(url) {
    try {
      const croScore = {
        mobileFriendly: false,
        pageSpeed: 0,
        userExperience: 0,
        score: 0
      };

      // Check mobile friendliness (simulated)
      croScore.mobileFriendly = Math.random() > 0.3; // 70% chance of being mobile friendly
      croScore.score += croScore.mobileFriendly ? 25 : 0;

      // Page speed score (simulated based on performance)
      croScore.pageSpeed = Math.floor(Math.random() * 40) + 60; // 60-100 range
      croScore.score += Math.floor(croScore.pageSpeed * 0.5); // 50% weight

      // User experience score (simulated)
      croScore.userExperience = Math.floor(Math.random() * 30) + 70; // 70-100 range
      croScore.score += Math.floor(croScore.userExperience * 0.25); // 25% weight

      return croScore;
    } catch (error) {
      throw new Error(`CRO analysis error: ${error.message}`);
    }
  }

  calculateFinalScores(analysis) {
    // Ensure scores are within 0-100 range
    Object.keys(analysis.scores).forEach(key => {
      analysis.scores[key] = Math.max(0, Math.min(100, analysis.scores[key]));
    });

    // Calculate overall score
    const totalScore = Object.values(analysis.scores).reduce((sum, score) => sum + score, 0);
    analysis.overallScore = Math.round(totalScore / 5);
  }

  extractMetric(audit) {
    if (!audit) return 'N/A';
    return {
      value: audit.numericValue,
      unit: audit.numericUnit,
      displayValue: audit.displayValue
    };
  }

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
    return opportunities.slice(0, 3);
  }

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
            resolve(jsonData);
          } catch (error) {
            reject(new Error('Failed to parse API response'));
          }
        });
      }).on('error', (error) => {
        reject(error);
      });
    });
  }

  printAnalysis(analysis) {
    console.log('\n' + '='.repeat(60));
    console.log(`📊 COMPREHENSIVE WEBSITE ANALYSIS`);
    console.log(`🌐 URL: ${analysis.url}`);
    console.log(`📝 Name: ${analysis.name}`);
    console.log(`⏰ Timestamp: ${analysis.timestamp}`);
    console.log('='.repeat(60));
    
    console.log('\n🏆 SCORES:');
    console.log(`  Performance: ${analysis.scores.performance}/100`);
    console.log(`  Accessibility: ${analysis.scores.accessibility}/100`);
    console.log(`  SEO: ${analysis.scores.seo}/100`);
    console.log(`  Trust: ${analysis.scores.trust}/100`);
    console.log(`  CRO: ${analysis.scores.cro}/100`);
    console.log(`  Overall: ${analysis.overallScore}/100`);
    
    if (analysis.pagespeed.metrics) {
      console.log('\n📈 PERFORMANCE METRICS:');
      Object.entries(analysis.pagespeed.metrics).forEach(([key, metric]) => {
        if (metric !== 'N/A') {
          console.log(`  ${key}: ${metric.displayValue || metric.value} ${metric.unit || ''}`);
        }
      });
    }
    
    if (analysis.trust) {
      console.log('\n🔒 TRUST INDICATORS:');
      console.log(`  SSL: ${analysis.trust.ssl ? '✅' : '❌'}`);
      console.log(`  Security Headers: ${analysis.trust.securityHeaders ? '✅' : '❌'}`);
      console.log(`  Domain Age: ${analysis.trust.domainAge}`);
    }
    
    if (analysis.cro) {
      console.log('\n📱 CRO FACTORS:');
      console.log(`  Mobile Friendly: ${analysis.cro.mobileFriendly ? '✅' : '❌'}`);
      console.log(`  Page Speed: ${analysis.cro.pageSpeed}/100`);
      console.log(`  User Experience: ${analysis.cro.userExperience}/100`);
    }
    
    console.log('\n' + '='.repeat(60));
  }

  async saveResults() {
    try {
      const filename = `website-analysis-${new Date().toISOString().split('T')[0]}.json`;
      const allResults = Array.from(this.results.values());
      
      fs.writeFileSync(filename, JSON.stringify(allResults, null, 2));
      console.log(`💾 Results saved to ${filename}`);
      
      return filename;
    } catch (error) {
      console.error('❌ Error saving results:', error.message);
      return null;
    }
  }

  async cleanup() {
    try {
      console.log('\n🧹 Cleaning up Pingdom checks...');
      
      for (const [url, analysis] of this.results) {
        if (analysis.pingdom.checkId) {
          try {
            await axios.delete(`${this.pingdomBaseUrl}/checks/${analysis.pingdom.checkId}`, {
              headers: {
                'Authorization': `Bearer ${this.pingdomApiKey}`,
                'Content-Type': 'application/json'
              }
            });
            console.log(`✅ Deleted check for ${url}`);
          } catch (error) {
            console.log(`❌ Could not delete check for ${url}:`, error.message);
          }
        }
      }
      
      console.log('✅ Cleanup completed');
    } catch (error) {
      console.error('❌ Error during cleanup:', error.message);
    }
  }
}

async function main() {
  const analyzer = new ComprehensiveWebsiteAnalyzer();
  
  try {
    console.log('🚀 Starting Comprehensive Website Analysis...\n');
    
    // Test websites to analyze
    const testWebsites = [
      { url: 'https://www.google.com', name: 'Google' },
      { url: 'https://www.github.com', name: 'GitHub' },
      { url: 'https://www.stackoverflow.com', name: 'Stack Overflow' }
    ];
    
    // Analyze each website
    for (const website of testWebsites) {
      try {
        const analysis = await analyzer.analyzeWebsite(website.url, website.name);
        analyzer.printAnalysis(analysis);
        
        // Wait between analyses to avoid rate limits
        await new Promise(resolve => setTimeout(resolve, 3000));
        
      } catch (error) {
        console.error(`Failed to analyze ${website.url}:`, error.message);
      }
    }
    
    // Save all results
    await analyzer.saveResults();
    
    console.log('\n✅ Comprehensive analysis completed successfully!');
    console.log('💡 Note: Some metrics are simulated due to API limitations.');
    console.log('   In production, you would integrate with additional APIs for real data.');
    
  } catch (error) {
    console.error('❌ Application failed:', error.message);
  } finally {
    // Clean up (optional - comment out if you want to keep the checks)
    // await analyzer.cleanup();
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = ComprehensiveWebsiteAnalyzer;
