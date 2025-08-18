const PageSpeedInsightsAPI = require('./index.js');

async function testSingleURL() {
  const api = new PageSpeedInsightsAPI();
  
  try {
    console.log('🚀 Starting PageSpeed Insights API test...\n');
    
    // Initialize the API
    await api.initialize();
    
    // Test with a single URL
    const testUrl = 'https://www.google.com';
    console.log(`Testing URL: ${testUrl}\n`);
    
    // Run mobile analysis
    const mobileResults = await api.runPageSpeedAnalysis(testUrl, 'mobile');
    api.printResults(mobileResults);
    
    // Run desktop analysis
    const desktopResults = await api.runPageSpeedAnalysis(testUrl, 'desktop');
    api.printResults(desktopResults);
    
    console.log('✅ Test completed successfully!');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  }
}

// Run the test
testSingleURL();
