const fs = require('fs');
const UnifiedAnalyzer = require('../unified');

function loadUrls() {
  try {
    const data = fs.readFileSync('./urls.json', 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('❌ Error loading URLs:', error.message);
    return [];
  }
}

async function runTests() {
  const analyzer = new UnifiedAnalyzer();
  const urls = loadUrls();

  if (urls.length === 0) {
    console.log('⚠️ No URLs found in urls.json');
    return;
  }

  console.log(`🚀 Starting comprehensive analysis for ${urls.length} URLs...\n`);

  for (const url of urls) {
    console.log(`🌐 Analyzing: ${url}`);
    console.log('='.repeat(60));

    try {
      // PageSpeed Analysis (Mobile & Desktop)
      console.log('📊 Running PageSpeed Analysis...');
      const mobileResults = await analyzer.runPageSpeedAnalysis(url, 'mobile');
      const desktopResults = await analyzer.runPageSpeedAnalysis(url, 'desktop');
      
      console.log('\n📱 Mobile Scores:');
      console.log(`Performance: ${mobileResults.scores.performance}/100`);
      console.log(`Accessibility: ${mobileResults.scores.accessibility}/100`);
      console.log(`Best Practices: ${mobileResults.scores.bestPractices}/100`);
      console.log(`SEO: ${mobileResults.scores.seo}/100`);

      console.log('\n💻 Desktop Scores:');
      console.log(`Performance: ${desktopResults.scores.performance}/100`);
      console.log(`Accessibility: ${desktopResults.scores.accessibility}/100`);
      console.log(`Best Practices: ${desktopResults.scores.bestPractices}/100`);
      console.log(`SEO: ${desktopResults.scores.seo}/100`);

      // Core Web Vitals
      console.log('\n📈 Core Web Vitals (Mobile):');
      console.log(`LCP: ${mobileResults.coreWebVitals.largestContentfulPaint?.displayValue || 'N/A'}`);
      console.log(`FID: ${mobileResults.coreWebVitals.firstInputDelay?.displayValue || 'N/A'}`);
      console.log(`CLS: ${mobileResults.coreWebVitals.cumulativeLayoutShift?.displayValue || 'N/A'}`);

      // Server Metrics
      console.log('\n⚡ Server Metrics:');
      console.log(`Server Response Time: ${mobileResults.serverMetrics.serverResponseTime?.displayValue || 'N/A'}`);
      console.log(`Total Blocking Time: ${mobileResults.serverMetrics.totalBlockingTime?.displayValue || 'N/A'}`);

      // Mobile Usability (extracted from PageSpeed)
      console.log('\n📱 Mobile Usability:');
      console.log(`Mobile Friendly: ${mobileResults.mobileUsability.mobileFriendly ? '✅' : '❌'}`);
      console.log(`Usability Score: ${mobileResults.mobileUsability.score}/100`);
      if (mobileResults.mobileUsability.issues.length > 0) {
        console.log(`Issues: ${mobileResults.mobileUsability.issues.join(', ')}`);
      }

      // Trust Analysis
      console.log('\n🔒 Trust Analysis...');
      const trustResults = await analyzer.analyzeTrust(url);
      console.log(`Trust Score: ${trustResults.score}/100`);
      console.log(`SSL: ${trustResults.ssl ? '✅' : '❌'}`);
      console.log(`Security Headers: ${trustResults.securityHeaders.length > 0 ? '✅ ' + trustResults.securityHeaders.join(', ') : '❌ None'}`);
      console.log(`Domain Age: ${trustResults.domainAge}`);

      // CRO Analysis
      console.log('\n💰 CRO Analysis...');
      const croResults = await analyzer.analyzeCRO(url);
      console.log(`CRO Score: ${croResults.score}/100`);
      console.log(`Mobile Friendly: ${croResults.mobileFriendly ? '✅' : '❌'}`);
      console.log(`Performance (Mobile/Desktop): ${croResults.pageSpeed.mobile}/${croResults.pageSpeed.desktop}`);
      console.log(`UX Loading Score: ${croResults.userExperience.loadingTime}/100`);

      // Uptime Analysis (replaces Pingdom)
      console.log('\n📡 Uptime Analysis...');
      const uptimeResults = await analyzer.analyzeUptime(url);
      console.log(`Uptime Score: ${uptimeResults.score}/100`);
      console.log(`Availability: ${uptimeResults.uptime}`);
      console.log(`Avg Response Time: ${uptimeResults.averageResponseTime}ms`);
      console.log(`Status: ${uptimeResults.status}`);

      // Optimization Opportunities
      console.log('\n💡 Top Optimization Opportunities:');
      mobileResults.opportunities.forEach((opportunity, index) => {
        console.log(`${index + 1}. ${opportunity.title}`);
        console.log(`   Potential Savings: ${opportunity.potentialSavings}${opportunity.unit}`);
      });

      console.log('\n' + '='.repeat(60));
    } catch (error) {
      console.error(`❌ Failed to analyze ${url}:`, error.message);
      console.log('='.repeat(60));
    }
  }

  console.log(`✅ Comprehensive analysis completed for ${urls.length} URLs.`);
}

runTests().catch(console.error);