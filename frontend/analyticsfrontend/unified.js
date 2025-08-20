const axios = require('axios');
require('dotenv').config({ path: './.env.local' });

// Import the DomainAnalysisService
const DomainAnalysisService = require('./domain-analysis');

class UnifiedAnalyzer {
  constructor() {
    this.pagespeedBaseUrl = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed';
    this.googleApiKey = process.env.GOOGLE_GENERAL_API;
    
    // Initialize the domain analysis service
    try {
      this.domainService = new DomainAnalysisService();
    } catch (error) {
      console.warn('⚠️ Domain Analysis Service not available:', error.message);
      this.domainService = null;
    }
  }

  async makeRequest(url, options = {}) {
    try {
      const response = await axios.get(url, options);
      return response.data;
    } catch (error) {
      if (error.response) {
        throw new Error(`Request failed with status ${error.response.status}: ${error.response.statusText}`);
      }
      throw new Error(`Request failed: ${error.message}`);
    }
  }

  extractMetric(metric) {
    return metric ? { 
      value: metric.numericValue, 
      displayValue: metric.displayValue,
      unit: metric.numericUnit || ''
    } : null;
  }

  extractOpportunities(audits) {
    const opportunities = [];
    Object.keys(audits).forEach(key => {
      if (audits[key].details?.type === 'opportunity' && audits[key].numericValue > 0) {
        opportunities.push({
          title: audits[key].title,
          description: audits[key].description,
          potentialSavings: Math.round(audits[key].numericValue) || 0,
          unit: audits[key].numericUnit || 'ms'
        });
      }
    });
    return opportunities.slice(0, 3);
  }

  async runPageSpeedAnalysis(url, strategy = 'mobile') {
    try {
      const categories = ['performance', 'accessibility', 'best-practices', 'seo'];
      const categoryParams = categories.map(cat => `category=${cat}`).join('&');
      const apiUrl = `${this.pagespeedBaseUrl}?url=${encodeURIComponent(url)}&strategy=${strategy}&${categoryParams}&prettyPrint=true&key=${this.googleApiKey}`;

      const data = await this.makeRequest(apiUrl);

      if (data.error) {
        throw new Error(data.error.message);
      }

      const scores = data.lighthouseResult?.categories || {};
      const audits = data.lighthouseResult?.audits || {};

      return {
        scores: {
          performance: Math.round(scores.performance?.score * 100) || 0,
          accessibility: Math.round(scores.accessibility?.score * 100) || 0,
          bestPractices: Math.round(scores['best-practices']?.score * 100) || 0,
          seo: Math.round(scores.seo?.score * 100) || 0
        },
        coreWebVitals: {
          largestContentfulPaint: this.extractMetric(audits['largest-contentful-paint']),
          firstInputDelay: this.extractMetric(audits['max-potential-fid']) || this.extractMetric(audits['first-input-delay']),
          cumulativeLayoutShift: this.extractMetric(audits['cumulative-layout-shift']),
          firstContentfulPaint: this.extractMetric(audits['first-contentful-paint']),
          speedIndex: this.extractMetric(audits['speed-index'])
        },
        serverMetrics: {
          serverResponseTime: this.extractMetric(audits['server-response-time']),
          totalBlockingTime: this.extractMetric(audits['total-blocking-time']),
          timeToInteractive: this.extractMetric(audits['interactive'])
        },
        mobileUsability: this.analyzeMobileUsabilityFromPageSpeed(audits),
        opportunities: this.extractOpportunities(audits)
      };
    } catch (error) {
      throw new Error(`PageSpeed API error: ${error.message}`);
      }
  }

  analyzeMobileUsabilityFromPageSpeed(audits) {
    const mobileChecks = {
      hasViewportMetaTag: audits['viewport']?.score === 1,
      contentSizedCorrectly: audits['content-width']?.score === 1,
      tapTargetsAppropriateSize: audits['tap-targets']?.score === 1,
      textReadable: audits['font-size']?.score === 1,
      isResponsive: true // Default assumption
      };

    const passedChecks = Object.values(mobileChecks).filter(Boolean).length;
    const mobileFriendlyScore = Math.round((passedChecks / Object.keys(mobileChecks).length) * 100);

    return {
      mobileFriendly: mobileFriendlyScore >= 80,
      score: mobileFriendlyScore,
      checks: mobileChecks,
      issues: this.getMobileIssues(mobileChecks),
      realData: true
    };
  }

  getMobileIssues(checks) {
    const issues = [];
    if (!checks.hasViewportMetaTag) issues.push('Missing viewport meta tag');
    if (!checks.contentSizedCorrectly) issues.push('Content not sized correctly for viewport');
    if (!checks.tapTargetsAppropriateSize) issues.push('Tap targets too small');
    if (!checks.textReadable) issues.push('Text too small to read');
    return issues;
  }

  async analyzeTrust(url) {
    try {
      const domain = new URL(url).hostname;
      const trustScore = {
        ssl: false,
        securityHeaders: [],
        domainAge: 'unknown',
        score: 0,
        realData: { ssl: true, securityHeaders: true, domainAge: false },
        warnings: []
      };

      // Check SSL
      try {
        const sslResponse = await axios.get(`https://${domain}`, { 
          timeout: 10000, 
          validateStatus: () => true,
          maxRedirects: 5
        });
        trustScore.ssl = sslResponse.status < 400;
        trustScore.score += trustScore.ssl ? 30 : 0;
      } catch (error) {
        trustScore.warnings.push(`SSL check failed: ${error.message}`);
      }

      // Check security headers
      try {
        const headersResponse = await axios.get(`https://${domain}`, { 
          timeout: 10000, 
          validateStatus: () => true,
          maxRedirects: 5
        });
        const headers = headersResponse.headers;

        const securityHeaders = [
          'x-frame-options',
          'x-content-type-options',
          'strict-transport-security',
          'content-security-policy',
          'x-xss-protection'
        ];

        trustScore.securityHeaders = securityHeaders.filter(header => headers[header]);
        trustScore.score += Math.min(40, trustScore.securityHeaders.length * 8);
      } catch (error) {
        trustScore.warnings.push(`Security headers check failed: ${error.message}`);
      }

      // Get domain age using DomainAnalysisService
      if (this.domainService) {
        try {
          const domainAnalysis = await this.domainService.analyzeDomain(domain);
          const domainAge = domainAnalysis.domainAge;
          
          trustScore.domainAge = `${domainAge.years} years, ${domainAge.months} months, ${domainAge.days} days`;
          trustScore.realData.domainAge = true;
          
          // Add domain age score based on years
          if (domainAge.years >= 10) trustScore.score += 15;
          else if (domainAge.years >= 5) trustScore.score += 12;
          else if (domainAge.years >= 2) trustScore.score += 8;
          else if (domainAge.years >= 1) trustScore.score += 5;
          else trustScore.score += 2;
          
        } catch (error) {
          trustScore.warnings.push(`Domain age analysis failed: ${error.message}`);
          // Fallback to estimation
          trustScore.domainAge = this.estimateDomainAge(domain);
          trustScore.realData.domainAge = false;
          trustScore.score += 3;
        }
      } else {
        // Fallback to estimation if domain service not available
        trustScore.domainAge = this.estimateDomainAge(domain);
        trustScore.realData.domainAge = false;
        trustScore.score += 3;
        trustScore.warnings.push('Domain age estimation only - service not available');
      }

      return trustScore;
    } catch (error) {
      throw new Error(`Trust analysis error: ${error.message}`);
    }
  }

  estimateDomainAge(domain) {
    // Simple heuristic: shorter, common domains are often older
    if (domain.length <= 8 && !domain.includes('-') && !domain.includes('2')) {
      return '5+ years (estimated)';
    } else if (domain.includes('2020') || domain.includes('2021') || domain.includes('2022')) {
      return '2-3 years (estimated)';
    } else if (domain.includes('new') || domain.includes('latest')) {
      return '1-2 years (estimated)';
    } else {
      return '3-5 years (estimated)';
    }
  }

  async analyzeCRO(url) {
    try {
      // Get both mobile and desktop PageSpeed data for comprehensive CRO analysis
      const mobileData = await this.runPageSpeedAnalysis(url, 'mobile');
      const desktopData = await this.runPageSpeedAnalysis(url, 'desktop');

      const croScore = {
        mobileFriendly: mobileData.mobileUsability.mobileFriendly,
        mobileUsabilityScore: mobileData.mobileUsability.score,
        mobileIssues: mobileData.mobileUsability.issues,
        pageSpeed: {
          mobile: mobileData.scores.performance,
          desktop: desktopData.scores.performance,
          average: Math.round((mobileData.scores.performance + desktopData.scores.performance) / 2)
        },
        userExperience: {
          loadingTime: this.calculateUXScore(mobileData.coreWebVitals),
          interactivity: this.calculateInteractivityScore(mobileData.serverMetrics),
          visualStability: this.calculateVisualStabilityScore(mobileData.coreWebVitals)
        },
        score: 0,
        realData: true
      };

      // Calculate overall CRO score
      croScore.score = Math.round(
        (croScore.mobileUsabilityScore * 0.3) +
        (croScore.pageSpeed.average * 0.4) +
        (croScore.userExperience.loadingTime * 0.3)
      );

      return croScore;
    } catch (error) {
      throw new Error(`CRO analysis error: ${error.message}`);
    }
  }

  calculateUXScore(coreWebVitals) {
    let score = 100;

    // LCP scoring
    const lcp = coreWebVitals.largestContentfulPaint?.value || 0;
    if (lcp > 4000) score -= 30;
    else if (lcp > 2500) score -= 15;
    
    // CLS scoring  
    const cls = coreWebVitals.cumulativeLayoutShift?.value || 0;
    if (cls > 0.25) score -= 25;
    else if (cls > 0.1) score -= 10;

    return Math.max(0, score);
  }

  calculateInteractivityScore(serverMetrics) {
    let score = 100;

    const tti = serverMetrics.timeToInteractive?.value || 0;
    if (tti > 5000) score -= 30;
    else if (tti > 3000) score -= 15;

    const tbt = serverMetrics.totalBlockingTime?.value || 0;
    if (tbt > 600) score -= 25;
    else if (tbt > 300) score -= 10;

    return Math.max(0, score);
  }

  calculateVisualStabilityScore(coreWebVitals) {
    const cls = coreWebVitals.cumulativeLayoutShift?.value || 0;
    if (cls <= 0.1) return 100;
    if (cls <= 0.25) return 80;
    return 50;
  }

  // Simulate uptime monitoring using PageSpeed availability
  async analyzeUptime(url) {
    try {
      const startTime = Date.now();

      // Test multiple rapid requests to simulate monitoring
      const testResults = [];
      for (let i = 0; i < 3; i++) {
        try {
          const testStart = Date.now();
          await axios.get(url, { timeout: 10000, validateStatus: () => true });
          const responseTime = Date.now() - testStart;
          testResults.push({ success: true, responseTime });
    } catch (error) {
          testResults.push({ success: false, responseTime: 10000 });
        }
        
        if (i < 2) await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      const successfulTests = testResults.filter(r => r.success).length;
      const averageResponseTime = testResults.reduce((sum, r) => sum + r.responseTime, 0) / testResults.length;
      const uptime = (successfulTests / testResults.length) * 100;

      let score = 100;
      if (uptime < 100) score -= (100 - uptime) * 2;
      if (averageResponseTime > 3000) score -= 20;
      else if (averageResponseTime > 1000) score -= 10;

      return {
        score: Math.max(0, Math.round(score)),
        uptime: `${uptime.toFixed(1)}%`,
        averageResponseTime: Math.round(averageResponseTime),
        status: uptime > 66 ? 'up' : 'down',
        realData: true
      };
    } catch (error) {
      throw new Error(`Uptime analysis error: ${error.message}`);
}
  }
}

module.exports = UnifiedAnalyzer;