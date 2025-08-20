const axios = require('axios');
require('dotenv').config({ path: './env.local' });

/**
 * Domain History and Age Analysis Service
 * Integrates WHOIS and DNS History APIs from WHOISXMLAPIs
 */
class DomainAnalysisService {
    constructor() {
        this.whoisApiKey = process.env.WHOIS_API_KEY;
        this.whoisBaseUrl = process.env.WHOIS_API_BASE_URL;
        this.whoisHistoryBaseUrl = process.env.WHOIS_HISTORY_API_BASE_URL;
        
        if (!this.whoisApiKey) {
            throw new Error('WHOIS_API_KEY is required in env.local file');
        }
    }

    /**
     * Get comprehensive domain information including age and history
     * @param {string} domain - Domain name to analyze
     * @returns {Object} Domain analysis results
     */
    async analyzeDomain(domain) {
        try {
            console.log(`🔍 Analyzing domain: ${domain}`);
            
            // Get WHOIS information
            const whoisData = await this.getWhoisInfo(domain);
            
            // Get WHOIS history for the domain
            const whoisHistory = await this.getWhoisHistory(domain);
            
            // Log raw API responses for debugging
            console.log('\n📊 RAW WHOIS DATA:');
            console.log(JSON.stringify(whoisData, null, 2));
            
            console.log('\n📊 RAW WHOIS HISTORY DATA:');
            console.log(JSON.stringify(whoisHistory, null, 2));
            
            // Calculate domain age
            const domainAge = this.calculateDomainAge(whoisData.createdDate);
            
            // Compile results
            const analysis = {
                domain,
                whois: whoisData,
                whoisHistory,
                domainAge,
                analysis: {
                    isEstablished: domainAge.years >= 2,
                    isVeteran: domainAge.years >= 5,
                    credibility: this.calculateCredibilityScore(whoisData, whoisHistory, domainAge)
                }
            };
            
            console.log(`✅ Analysis complete for ${domain}`);
            return analysis;
            
        } catch (error) {
            console.error(`❌ Error analyzing domain ${domain}:`, error.message);
            throw error;
        }
    }

    /**
     * Get WHOIS information for a domain
     * @param {string} domain - Domain name
     * @returns {Object} WHOIS data
     */
    async getWhoisInfo(domain) {
        const url = `${this.whoisBaseUrl}/whoisserver/WhoisService`;
        const params = {
            domainName: domain,
            outputFormat: 'JSON',
            _hardRefresh: 1,
            apiKey: this.whoisApiKey
        };

        try {
            const response = await axios.get(url, { params, timeout: 10000 });
            
            // Log raw WHOIS API response
            console.log('\n🔍 RAW WHOIS API RESPONSE:');
            console.log(JSON.stringify(response.data, null, 2));
            
            if (response.data && response.data.WhoisRecord) {
                const whois = response.data.WhoisRecord;
                
                // Extract creation date from multiple possible locations
                let createdDate = whois.createdDate;
                let updatedDate = whois.updatedDate;
                let expiresDate = whois.expiresDate;
                let registrar = whois.registrarName;
                let status = whois.status;
                let nameServers = whois.nameServers?.hostNames || [];
                
                // If main data is missing, try to get from registryData
                if (!createdDate && whois.registryData) {
                    createdDate = whois.registryData.createdDate;
                    updatedDate = whois.registryData.updatedDate;
                    expiresDate = whois.registryData.expiresDate;
                    registrar = whois.registryData.registrarName || registrar;
                    status = whois.registryData.status || status;
                    nameServers = whois.registryData.nameServers?.hostNames || nameServers;
                }
                
                return {
                    createdDate,
                    updatedDate,
                    expiresDate,
                    registrar,
                    status,
                    ips: this.extractIPs(whois),
                    nameServers,
                    registrant: whois.registrant?.organization || 'Unknown',
                    country: whois.registrant?.countryCode || 'Unknown'
                };
            } else {
                throw new Error('Invalid WHOIS response format');
            }
        } catch (error) {
            throw new Error(`WHOIS lookup failed: ${error.message}`);
        }
    }

    /**
     * Get WHOIS history for a domain
     * @param {string} domain - Domain name
     * @returns {Object} WHOIS history data
     */
    async getWhoisHistory(domain) {
        const url = `${this.whoisHistoryBaseUrl}/api/v1`;
        const params = {
            domainName: domain,
            outputFormat: 'JSON',
            apiKey: this.whoisApiKey
        };

        try {
            const response = await axios.get(url, { params, timeout: 10000 });
            
            // Log raw WHOIS History API response
            console.log('\n🔍 RAW WHOIS HISTORY API RESPONSE:');
            console.log(JSON.stringify(response.data, null, 2));
            
            if (response.data && response.data.recordsCount !== undefined) {
                return {
                    totalRecords: response.data.recordsCount,
                    firstSeen: null, // API doesn't provide this
                    lastVisit: null, // API doesn't provide this
                    records: [], // API doesn't provide individual records
                    note: 'API returns only count, not individual records'
                };
            } else {
                return null;
            }
        } catch (error) {
            console.warn(`WHOIS History lookup failed for domain ${domain}: ${error.message}`);
            return null;
        }
    }

    /**
     * Calculate domain age from creation date
     * @param {string} createdDate - ISO date string
     * @returns {Object} Age breakdown
     */
    calculateDomainAge(createdDate) {
        if (!createdDate) {
            return { 
                years: 0, 
                months: 0, 
                days: 0, 
                totalDays: 0, 
                createdDate: null,
                ageDescription: 'Unknown'
            };
        }

        try {
            const created = new Date(createdDate);
            
            // Check if date is valid
            if (isNaN(created.getTime())) {
                return { 
                    years: 0, 
                    months: 0, 
                    days: 0, 
                    totalDays: 0, 
                    createdDate: null,
                    ageDescription: 'Invalid Date'
                };
            }
            
            const now = new Date();
            const diffTime = Math.abs(now - created);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            const years = Math.floor(diffDays / 365);
            const months = Math.floor((diffDays % 365) / 30);
            const days = diffDays % 30;

            return {
                years,
                months,
                days,
                totalDays: diffDays,
                createdDate: created.toISOString(),
                ageDescription: this.getAgeDescription(years, months)
            };
        } catch (error) {
            console.warn(`Error calculating domain age for date: ${createdDate}`, error.message);
            return { 
                years: 0, 
                months: 0, 
                days: 0, 
                totalDays: 0, 
                createdDate: null,
                ageDescription: 'Error'
            };
        }
    }

    /**
     * Get age description based on years and months
     * @param {number} years - Number of years
     * @param {number} months - Number of months
     * @returns {string} Age description
     */
    getAgeDescription(years, months) {
        if (years >= 10) return 'Veteran';
        if (years >= 5) return 'Established';
        if (years >= 2) return 'Mature';
        if (years >= 1) return 'Young';
        if (months >= 6) return 'Recent';
        if (months >= 1) return 'New';
        return 'Very New';
    }

    /**
     * Calculate credibility score based on domain analysis
     * @param {Object} whoisData - WHOIS information
     * @param {Object} whoisHistory - WHOIS history data
     * @param {Object} domainAge - Domain age information
     * @returns {number} Credibility score (0-100)
     */
    calculateCredibilityScore(whoisData, whoisHistory, domainAge) {
        let score = 0;
        
        // Domain age score (40 points max)
        if (domainAge.years >= 5) score += 40;
        else if (domainAge.years >= 2) score += 30;
        else if (domainAge.years >= 1) score += 20;
        else if (domainAge.months >= 6) score += 10;
        
        // Registration status score (20 points max)
        if (whoisData.status && !whoisData.status.includes('expired')) {
            score += 20;
        }
        
        // Name servers score (15 points max)
        if (whoisData.nameServers && whoisData.nameServers.length >= 2) {
            score += 15;
        }
        
        // WHOIS history score (15 points max)
        if (whoisHistory && whoisHistory.totalRecords > 0) {
            score += Math.min(15, Math.floor(whoisHistory.totalRecords / 10));
        }
        
        // Registrar reputation score (10 points max)
        if (whoisData.registrar && !whoisData.registrar.includes('Unknown')) {
            score += 10;
        }
        
        return Math.min(100, score);
    }

    /**
     * Extract IP addresses from WHOIS data
     * @param {Object} whois - WHOIS record
     * @returns {Array} Array of IP addresses
     */
    extractIPs(whois) {
        const ips = [];
        
        // Check nameServers.ips array
        if (whois.nameServers && whois.nameServers.ips) {
            ips.push(...whois.nameServers.ips);
        }
        
        // Check registryData nameServers.ips array
        if (whois.registryData && whois.registryData.nameServers && whois.registryData.nameServers.ips) {
            ips.push(...whois.registryData.nameServers.ips);
        }
        
        return ips;
    }
}

module.exports = DomainAnalysisService;
