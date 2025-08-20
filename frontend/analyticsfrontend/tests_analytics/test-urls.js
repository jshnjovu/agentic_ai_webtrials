const fs = require('fs');
const path = require('path');
const DomainAnalysisService = require('../domain-analysis');

/**
 * Test script that analyzes domains from urls.json file
 * Tests real business domains for domain history and age analysis
 */
class UrlsTestRunner {
    constructor() {
        this.urlsFile = path.join(__dirname, 'urls.json');
        this.domainService = null;
        this.results = [];
    }

    /**
     * Load URLs from urls.json file
     * @returns {Array} Array of URLs
     */
    loadUrls() {
        try {
            if (!fs.existsSync(this.urlsFile)) {
                throw new Error(`URLs file not found: ${this.urlsFile}`);
            }

            const urlsData = fs.readFileSync(this.urlsFile, 'utf8');
            const urls = JSON.parse(urlsData);

            if (!Array.isArray(urls) || urls.length === 0) {
                throw new Error('URLs file is empty or invalid format');
            }

            console.log(`📋 Loaded ${urls.length} URLs from urls.json`);
            return urls;
        } catch (error) {
            console.error('❌ Error loading URLs:', error.message);
            throw error;
        }
    }

    /**
     * Extract domain from URL
     * @param {string} url - Full URL
     * @returns {string} Domain name
     */
    extractDomain(url) {
        try {
            // Remove protocol and get domain
            const domain = url.replace(/^https?:\/\//, '').replace(/^www\./, '');
            return domain;
        } catch (error) {
            console.error(`❌ Error extracting domain from ${url}:`, error.message);
            return url;
        }
    }

    /**
     * Run analysis on a single domain
     * @param {string} domain - Domain name to analyze
     * @returns {Object} Analysis result
     */
    async analyzeSingleDomain(domain) {
        try {
            console.log(`\n${'='.repeat(60)}`);
            console.log(`🔍 ANALYZING: ${domain}`);
            console.log(`${'='.repeat(60)}`);

            const startTime = Date.now();
            const analysis = await this.domainService.analyzeDomain(domain);
            const duration = Date.now() - startTime;

            // Add timing information
            analysis.analysisTime = duration;
            analysis.timestamp = new Date().toISOString();

            // Display results
            this.displayAnalysisResults(analysis, duration);

            return analysis;
        } catch (error) {
            console.error(`❌ Failed to analyze ${domain}:`, error.message);
            return {
                domain,
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * Display formatted analysis results
     * @param {Object} analysis - Analysis results
     * @param {number} duration - Analysis duration in milliseconds
     */
    displayAnalysisResults(analysis, duration) {
        if (analysis.error) {
            console.log(`❌ Analysis failed: ${analysis.error}`);
            return;
        }

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
            if (history.note) {
                console.log(`   Note: ${history.note}`);
            }
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
     * Generate summary report
     */
    generateSummaryReport() {
        console.log('\n' + '='.repeat(80));
        console.log('📊 COMPREHENSIVE ANALYSIS SUMMARY REPORT');
        console.log('='.repeat(80));

        const successful = this.results.filter(r => !r.error);
        const failed = this.results.filter(r => r.error);
        const total = this.results.length;

        console.log(`\n📈 OVERALL STATISTICS:`);
        console.log(`   Total Domains Analyzed: ${total}`);
        console.log(`   Successful: ${successful.length} ✅`);
        console.log(`   Failed: ${failed.length} ❌`);
        console.log(`   Success Rate: ${((successful.length / total) * 100).toFixed(1)}%`);

        if (successful.length > 0) {
            console.log(`\n🏆 CREDIBILITY SCORE BREAKDOWN:`);
            const scores = successful.map(r => r.analysis?.credibility).filter(s => s !== undefined);
            if (scores.length > 0) {
                const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
                const maxScore = Math.max(...scores);
                const minScore = Math.min(...scores);
                
                console.log(`   Average Score: ${avgScore.toFixed(1)}/100`);
                console.log(`   Highest Score: ${maxScore}/100`);
                console.log(`   Lowest Score: ${minScore}/100`);
            }

            console.log(`\n📅 DOMAIN AGE BREAKDOWN:`);
            const ages = successful.map(r => r.domainAge?.years).filter(a => a !== undefined);
            if (ages.length > 0) {
                const avgAge = ages.reduce((a, b) => a + b, 0) / ages.length;
                const maxAge = Math.max(...ages);
                const minAge = Math.min(...ages);
                
                console.log(`   Average Age: ${avgAge.toFixed(1)} years`);
                console.log(`   Oldest Domain: ${maxAge} years`);
                console.log(`   Newest Domain: ${minAge} years`);
            }

            console.log(`\n🏷️  DOMAIN CATEGORIES:`);
            const categories = successful.map(r => r.domainAge?.ageDescription).filter(c => c);
            const categoryCount = {};
            categories.forEach(cat => {
                categoryCount[cat] = (categoryCount[cat] || 0) + 1;
            });
            
            Object.entries(categoryCount).forEach(([cat, count]) => {
                console.log(`   ${cat}: ${count} domains`);
            });
        }

        if (failed.length > 0) {
            console.log(`\n❌ FAILED ANALYSES:`);
            failed.forEach(result => {
                console.log(`   ${result.domain}: ${result.error}`);
            });
        }

        console.log(`\n⏱️  PERFORMANCE:`);
        const times = successful.map(r => r.analysisTime).filter(t => t !== undefined);
        if (times.length > 0) {
            const avgTime = times.reduce((a, b) => a + b, 0) / times.length;
            const totalTime = times.reduce((a, b) => a + b, 0);
            console.log(`   Average Analysis Time: ${avgTime.toFixed(0)}ms`);
            console.log(`   Total Analysis Time: ${(totalTime / 1000).toFixed(1)}s`);
        }

        console.log('\n🎯 RECOMMENDATIONS:');
        if (successful.length > 0) {
            const highCredibility = successful.filter(r => r.analysis?.credibility >= 80);
            const established = successful.filter(r => r.analysis?.isEstablished);
            
            if (highCredibility.length > 0) {
                console.log(`   🏆 High Credibility Domains (${highCredibility.length}): Consider for premium leads`);
            }
            if (established.length > 0) {
                console.log(`   ✅ Established Domains (${established.length}): Good for reliable business relationships`);
            }
        }
    }

    /**
     * Save results to JSON file
     */
    saveResults() {
        const outputFile = path.join(__dirname, 'analysis-results.json');
        try {
            fs.writeFileSync(outputFile, JSON.stringify(this.results, null, 2));
            console.log(`\n💾 Results saved to: ${outputFile}`);
        } catch (error) {
            console.error('❌ Error saving results:', error.message);
        }
    }

    /**
     * Run analysis on all URLs
     */
    async runAnalysis() {
        try {
            console.log('🚀 URLS ANALYSIS TEST RUNNER');
            console.log('='.repeat(60));

            // Initialize service
            this.domainService = new DomainAnalysisService();
            console.log('✅ Domain Analysis Service initialized');

            // Load URLs
            const urls = this.loadUrls();
            console.log('📋 URLs loaded successfully\n');

            // Analyze each domain
            for (let i = 0; i < urls.length; i++) {
                const url = urls[i];
                const domain = this.extractDomain(url);
                
                console.log(`\n🔄 Progress: ${i + 1}/${urls.length}`);
                
                // Analyze domain
                const result = await this.analyzeSingleDomain(domain);
                this.results.push(result);

                // Add delay between requests to respect rate limits
                if (i < urls.length - 1) {
                    console.log('\n⏳ Waiting 3 seconds before next request...');
                    await new Promise(resolve => setTimeout(resolve, 3000));
                }
            }

            // Generate summary and save results
            this.generateSummaryReport();
            this.saveResults();

            console.log('\n🎉 URL Analysis Complete!');
            
        } catch (error) {
            console.error('❌ Analysis failed:', error.message);
            process.exit(1);
        }
    }
}

// Run if called directly
if (require.main === module) {
    const runner = new UrlsTestRunner();
    runner.runAnalysis().catch(console.error);
}

module.exports = UrlsTestRunner;
