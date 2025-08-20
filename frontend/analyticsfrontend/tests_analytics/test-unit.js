const DomainAnalysisService = require('../domain-analysis');

/**
 * Unit Tests for Domain Analysis Service
 * Tests individual methods without making actual API calls
 */
class DomainAnalysisServiceTest {
    constructor() {
        this.passedTests = 0;
        this.failedTests = 0;
        this.totalTests = 0;
    }

    /**
     * Run all unit tests
     */
    async runAllTests() {
        console.log('🧪 UNIT TESTS FOR DOMAIN ANALYSIS SERVICE');
        console.log('='.repeat(60));
        
        // Test domain age calculations
        this.testDomainAgeCalculations();
        
        // Test credibility scoring
        this.testCredibilityScoring();
        
        // Test utility methods
        this.testUtilityMethods();
        
        // Test error handling
        this.testErrorHandling();
        
        // Display results
        this.displayResults();
    }

    /**
     * Test domain age calculation methods
     */
    testDomainAgeCalculations() {
        console.log('\n📅 Testing Domain Age Calculations...');
        
        // Create a mock service instance for testing
        const service = new DomainAnalysisService();
        
        // Test 1: Recent domain (6 months old)
        this.runTest('Recent domain age calculation', () => {
            const age = service.calculateDomainAge('2023-07-01T00:00:00Z');
            return age.months >= 6 && age.years === 0;
        });
        
        // Test 2: Established domain (2 years old)
        this.runTest('Established domain age calculation', () => {
            const age = service.calculateDomainAge('2021-12-01T00:00:00Z');
            return age.years === 2 && age.months >= 0;
        });
        
        // Test 3: Veteran domain (10 years old)
        this.runTest('Veteran domain age calculation', () => {
            const age = service.calculateDomainAge('2013-01-01T00:00:00Z');
            return age.years === 10 && age.months >= 0;
        });
        
        // Test 4: Invalid date handling
        this.runTest('Invalid date handling', () => {
            const age = service.calculateDomainAge(null);
            return age.years === 0 && age.months === 0 && age.days === 0;
        });
        
        // Test 5: Age description categorization
        this.runTest('Age description categorization', () => {
            const newDesc = service.getAgeDescription(0, 3);
            const growingDesc = service.getAgeDescription(0, 8);
            const matureDesc = service.getAgeDescription(1, 0);
            const establishedDesc = service.getAgeDescription(3, 0);
            const veteranDesc = service.getAgeDescription(7, 0);
            
            return newDesc === 'New' &&
                   growingDesc === 'Growing' &&
                   matureDesc === 'Mature' &&
                   establishedDesc === 'Established' &&
                   veteranDesc === 'Veteran';
        });
    }

    /**
     * Test credibility scoring algorithm
     */
    testCredibilityScoring() {
        console.log('\n🎯 Testing Credibility Scoring...');
        
        const service = new DomainAnalysisService();
        
        // Test 1: High credibility domain (veteran, good status, multiple NS)
        this.runTest('High credibility scoring', () => {
            const mockWhois = {
                status: 'active',
                nameServers: ['ns1.example.com', 'ns2.example.com'],
                registrar: 'GoDaddy',
                ips: ['192.168.1.1']
            };
            const mockWhoisHistory = { totalRecords: 25 };
            const mockAge = { years: 8, months: 0 };
            
            const score = service.calculateCredibilityScore(mockWhois, mockWhoisHistory, mockAge);
            return score >= 80; // Should be excellent
        });
        
        // Test 2: Medium credibility domain
        this.runTest('Medium credibility scoring', () => {
            const mockWhois = {
                status: 'active',
                nameServers: ['ns1.example.com'],
                registrar: 'Unknown',
                ips: ['192.168.1.1']
            };
            const mockWhoisHistory = { totalRecords: 5 };
            const mockAge = { years: 1, months: 6 };
            
            const score = service.calculateCredibilityScore(mockWhois, mockWhoisHistory, mockAge);
            return score >= 40 && score < 70; // Should be fair to good
        });
        
        // Test 3: Low credibility domain
        this.runTest('Low credibility scoring', () => {
            const mockWhois = {
                status: 'expired',
                nameServers: [],
                registrar: 'Unknown',
                ips: []
            };
            const mockWhoisHistory = null;
            const mockAge = { years: 0, months: 2 };
            
            const score = service.calculateCredibilityScore(mockWhois, mockWhoisHistory, mockAge);
            return score < 30; // Should be poor
        });
    }

    /**
     * Test utility methods
     */
    testUtilityMethods() {
        console.log('\n🔧 Testing Utility Methods...');
        
        const service = new DomainAnalysisService();
        
        // Test 1: IP extraction from WHOIS data
        this.runTest('IP extraction from WHOIS data', () => {
            const mockWhois = {
                nameServers: {
                    ips: ['192.168.1.1', '192.168.1.2', '']
                }
            };
            const ips = service.extractIPs(mockWhois);
            return ips.length === 2 && ips.includes('192.168.1.1') && ips.includes('192.168.1.2');
        });
        
        // Test 2: Timestamp finding methods
        this.runTest('Timestamp finding methods', () => {
            const mockDomains = [
                { first_seen: 1628985600, last_visit: 1665100800 },
                { first_seen: 1657238400, last_visit: 1664668800 },
                { first_seen: 1658966400, last_visit: 1667001600 }
            ];
            
            const earliest = service.findEarliestFirstSeen(mockDomains);
            const latest = service.findLatestLastVisit(mockDomains);
            
            return earliest && latest;
        });
        
        // Test 3: Retryable error detection
        this.runTest('Retryable error detection', () => {
            const networkError = { code: 'ECONNRESET' };
            const timeoutError = { code: 'ETIMEDOUT' };
            const serverError = { response: { status: 500 } };
            const clientError = { response: { status: 400 } };
            
            return service.isRetryableError(networkError) &&
                   service.isRetryableError(timeoutError) &&
                   service.isRetryableError(serverError) &&
                   !service.isRetryableError(clientError);
        });
    }

    /**
     * Test error handling
     */
    testErrorHandling() {
        console.log('\n🚨 Testing Error Handling...');
        
        // Test 1: Missing API key
        this.runTest('Missing API key handling', () => {
            try {
                // Temporarily modify environment
                const originalKey = process.env.WHOIS_API_KEY;
                delete process.env.WHOIS_API_KEY;
                
                new DomainAnalysisService();
                return false; // Should not reach here
            } catch (error) {
                return error.message.includes('WHOIS_API_KEY is required');
            }
        });
        
        // Test 2: Invalid domain input
        this.runTest('Invalid domain input handling', () => {
            const service = new DomainAnalysisService();
            const age = service.calculateDomainAge('invalid-date');
            return age.years === 0 && age.months === 0;
        });
    }

    /**
     * Run a single test
     * @param {string} testName - Name of the test
     * @param {Function} testFunction - Test function that returns boolean
     */
    runTest(testName, testFunction) {
        this.totalTests++;
        
        try {
            const result = testFunction();
            if (result) {
                console.log(`   ✅ ${testName}`);
                this.passedTests++;
            } else {
                console.log(`   ❌ ${testName} - Test returned false`);
                this.failedTests++;
            }
        } catch (error) {
            console.log(`   ❌ ${testName} - Error: ${error.message}`);
            this.failedTests++;
        }
    }

    /**
     * Display test results
     */
    displayResults() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 TEST RESULTS SUMMARY');
        console.log('='.repeat(60));
        console.log(`Total Tests: ${this.totalTests}`);
        console.log(`Passed: ${this.passedTests} ✅`);
        console.log(`Failed: ${this.failedTests} ❌`);
        console.log(`Success Rate: ${((this.passedTests / this.totalTests) * 100).toFixed(1)}%`);
        
        if (this.failedTests === 0) {
            console.log('\n🎉 All tests passed! The service is working correctly.');
        } else {
            console.log('\n⚠️  Some tests failed. Please review the implementation.');
        }
    }
}

// Run tests if called directly
if (require.main === module) {
    const tester = new DomainAnalysisServiceTest();
    tester.runAllTests().catch(console.error);
}

module.exports = DomainAnalysisServiceTest;
