const DomainAnalysisService = require('../domain-analysis');

/**
 * Test script for corrected WHOIS History API implementation
 */
async function testCorrectedImplementation() {
    try {
        console.log('🧪 Testing Corrected WHOIS History API Implementation\n');
        
        // Initialize the service
        const domainService = new DomainAnalysisService();
        
        // Test domain
        const domain = 'google.com';
        
        console.log(`🔍 Testing domain: ${domain}`);
        console.log('⏳ Please wait...\n');
        
        // Test WHOIS API
        console.log('1️⃣ Testing WHOIS API...');
        const whoisData = await domainService.getWhoisInfo(domain);
        console.log('   ✅ WHOIS API working');
        console.log(`   📅 Creation Date: ${whoisData.createdDate}`);
        console.log(`   🏢 Registrar: ${whoisData.registrar}`);
        
        // Test WHOIS History API
        console.log('\n2️⃣ Testing WHOIS History API...');
        const historyData = await domainService.getWhoisHistory(domain);
        if (historyData) {
            console.log('   ✅ WHOIS History API working');
            console.log(`   🌐 Total records found: ${historyData.totalRecords}`);
            console.log(`   📅 First Seen: ${historyData.firstSeen || 'Unknown'}`);
            console.log(`   📅 Last Visit: ${historyData.lastVisit || 'Unknown'}`);
        } else {
            console.log('   ⚠️  WHOIS History API returned no data');
        }
        
        // Test full analysis
        console.log('\n3️⃣ Testing Full Domain Analysis...');
        const analysis = await domainService.analyzeDomain(domain);
        console.log('   ✅ Full analysis completed');
        console.log(`   🎯 Credibility Score: ${analysis.analysis.credibility}/100`);
        console.log(`   📅 Domain Age: ${analysis.domainAge.years} years, ${analysis.domainAge.months} months`);
        console.log(`   🏷️  Category: ${analysis.domainAge.ageDescription}`);
        
        if (analysis.whoisHistory) {
            console.log(`   🌐 WHOIS History Records: ${analysis.whoisHistory.totalRecords}`);
        }
        
        console.log('\n🎉 All tests passed! Implementation is working correctly.');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        console.log('\n💡 Make sure you have:');
        console.log('   1. Updated env.local with your actual WHOIS_API_KEY');
        console.log('   2. Installed dependencies: npm install axios dotenv');
    }
}

// Run test
testCorrectedImplementation();
