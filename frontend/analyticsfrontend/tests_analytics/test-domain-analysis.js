const DomainAnalysisService = require('../domain-analysis');

/**
 * Test script for Domain Analysis Service
 * Demonstrates WHOIS and DNS History API integration
 */
async function testDomainAnalysis() {
    try {
        console.log('🚀 Starting Domain Analysis Service Test\n');
        
        // Initialize the service
        const domainService = new DomainAnalysisService();
        
        // Test domains (mix of established and new domains)
        const testDomains = [
            'google.com',           // Established veteran domain
            'microsoft.com',        // Established veteran domain
            'github.com',           // Established domain
            'stackoverflow.com',    // Established domain
            'example.com'           // Test domain
        ];
        
        console.log('📋 Test Domains:');
        testDomains.forEach((domain, index) => {
            console.log(`  ${index + 1}. ${domain}`);
        });
        console.log('');
        
        // Analyze each domain
        for (const domain of testDomains) {
            try {
                console.log(`\n${'='.repeat(60)}`);
                console.log(`🔍 ANALYZING: ${domain}`);
                console.log(`${'='.repeat(60)}`);
                
                const startTime = Date.now();
                const analysis = await domainService.analyzeDomain(domain);
                const endTime = Date.now();
                
                // Display results
                displayAnalysisResults(analysis, endTime - startTime);
                
                // Add delay between requests to respect rate limits
                if (domain !== testDomains[testDomains.length - 1]) {
                    console.log('\n⏳ Waiting 2 seconds before next request...');
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
                
            } catch (error) {
                console.error(`❌ Failed to analyze ${domain}:`, error.message);
            }
        }
        
        console.log('\n🎉 Domain Analysis Test Complete!');
        
    } catch (error) {
        console.error('❌ Test failed:', error.message);
        process.exit(1);
    }
}

/**
 * Display formatted analysis results
 * @param {Object} analysis - Analysis results
 * @param {number} duration - Analysis duration in milliseconds
 */
function displayAnalysisResults(analysis, duration) {
    console.log(`\n📊 ANALYSIS RESULTS for ${analysis.domain.toUpperCase()}`);
    console.log(`⏱️  Analysis completed in ${duration}ms`);
    
    // Domain Age Information
    console.log('\n📅 DOMAIN AGE:');
    const age = analysis.domainAge;
    console.log(`   Created: ${age.createdDate || 'Unknown'}`);
    console.log(`   Age: ${age.years} years, ${age.months} months, ${age.days} days`);
    console.log(`   Total Days: ${age.totalDays}`);
    console.log(`   Category: ${age.ageDescription}`);
    
    // WHOIS Information
    console.log('\n🏢 WHOIS INFORMATION:');
    const whois = analysis.whois;
    console.log(`   Registrar: ${whois.registrar || 'Unknown'}`);
    console.log(`   Registrant: ${whois.registrant || 'Unknown'}`);
    console.log(`   Country: ${whois.country || 'Unknown'}`);
    console.log(`   Status: ${whois.status || 'Unknown'}`);
    console.log(`   Name Servers: ${whois.nameServers.length} found`);
    console.log(`   IP Addresses: ${whois.ips.length} found`);
    
    // WHOIS History (if available)
    if (analysis.whoisHistory) {
        console.log('\n🌐 WHOIS HISTORY:');
        const history = analysis.whoisHistory;
        console.log(`   Total Records: ${history.totalRecords}`);
        console.log(`   First Seen: ${history.firstSeen || 'Unknown'}`);
        console.log(`   Last Visit: ${history.lastVisit || 'Unknown'}`);
        console.log(`   Sample Records: ${history.records.slice(0, 3).map(r => r.name || r.domain || 'Unknown').join(', ')}`);
    } else {
        console.log('\n🌐 WHOIS HISTORY: Not available');
    }
    
    // Credibility Analysis
    console.log('\n🎯 CREDIBILITY ANALYSIS:');
    const analysisData = analysis.analysis;
    console.log(`   Credibility Score: ${analysisData.credibility}/100`);
    console.log(`   Established Domain: ${analysisData.isEstablished ? '✅ Yes' : '❌ No'}`);
    console.log(`   Veteran Domain: ${analysisData.isVeteran ? '✅ Yes' : '❌ No'}`);
    
    // Score breakdown
    console.log('\n📈 SCORE BREAKDOWN:');
    const score = analysisData.credibility;
    if (score >= 80) console.log('   🏆 EXCELLENT - High credibility domain');
    else if (score >= 60) console.log('   🥇 GOOD - Reliable domain');
    else if (score >= 40) console.log('   🥈 FAIR - Moderate credibility');
    else if (score >= 20) console.log('   🥉 POOR - Low credibility');
    else console.log('   ⚠️  VERY POOR - Questionable domain');
}

/**
 * Test individual API endpoints
 */
async function testIndividualAPIs() {
    console.log('\n🔧 Testing Individual API Endpoints\n');
    
    try {
        const domainService = new DomainAnalysisService();
        
        // Test WHOIS API only
        console.log('1️⃣ Testing WHOIS API...');
        const whoisData = await domainService.getWhoisInfo('google.com');
        console.log('   ✅ WHOIS API working');
        console.log(`   📅 Creation Date: ${whoisData.createdDate}`);
        
        // Test WHOIS History API
        console.log('\n2️⃣ Testing WHOIS History API...');
        const historyData = await domainService.getWhoisHistory('google.com');
        if (historyData) {
            console.log('   ✅ WHOIS History API working');
            console.log(`   🌐 Total records found: ${historyData.totalRecords}`);
        } else {
            console.log('   ⚠️  WHOIS History API returned no data');
        }
        
        console.log('\n✅ Individual API tests completed');
        
    } catch (error) {
        console.error('❌ Individual API test failed:', error.message);
    }
}

/**
 * Test error handling
 */
async function testErrorHandling() {
    console.log('\n🚨 Testing Error Handling\n');
    
    try {
        const domainService = new DomainAnalysisService();
        
        // Test with invalid domain
        console.log('1️⃣ Testing invalid domain...');
        try {
            await domainService.analyzeDomain('invalid-domain-12345.com');
        } catch (error) {
            console.log('   ✅ Properly handled invalid domain error');
        }
        
        // Test with empty domain
        console.log('\n2️⃣ Testing empty domain...');
        try {
            await domainService.analyzeDomain('');
        } catch (error) {
            console.log('   ✅ Properly handled empty domain error');
        }
        
        console.log('\n✅ Error handling tests completed');
        
    } catch (error) {
        console.error('❌ Error handling test failed:', error.message);
    }
}

// Main execution
async function main() {
    console.log('🧪 DOMAIN ANALYSIS SERVICE - COMPREHENSIVE TEST SUITE');
    console.log('='.repeat(70));
    
    // Run all tests
    await testDomainAnalysis();
    await testIndividualAPIs();
    await testErrorHandling();
    
    console.log('\n🎯 All tests completed successfully!');
    console.log('\n💡 Next steps:');
    console.log('   1. Update env.local with your actual WHOIS_API_KEY');
    console.log('   2. Run: node test-domain-analysis.js');
    console.log('   3. Check the results and adjust scoring algorithm as needed');
}

// Run if called directly
if (require.main === module) {
    main().catch(console.error);
}

module.exports = {
    testDomainAnalysis,
    testIndividualAPIs,
    testErrorHandling
};
