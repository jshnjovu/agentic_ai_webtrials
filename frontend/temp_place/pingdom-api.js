const axios = require('axios');
const fs = require('fs');
require('dotenv').config({ path: './env.local' });

class PingdomAPI {
  constructor() {
    this.apiKey = process.env.PINGDOM_API_KEY;
    this.baseUrl = 'https://api.pingdom.com/api/3.1';
    this.headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  async createCheck(url, name, type = 'http') {
    try {
      console.log(`🔍 Creating check for: ${url}`);
      
      // Extract domain from URL
      const domain = new URL(url).hostname;
      
      const response = await axios.post(`${this.baseUrl}/checks`, {
        name: name,
        host: domain,
        type: type,
        resolution: 1 // Check every minute
      }, { headers: this.headers });

      console.log(`✅ Check created successfully: ${response.data.check.id}`);
      return response.data.check;
    } catch (error) {
      console.error(`❌ Error creating check:`, error.response?.data || error.message);
      throw error;
    }
  }

  async getCheckResults(checkId) {
    try {
      console.log(`📊 Getting results for check: ${checkId}`);
      
      const response = await axios.get(`${this.baseUrl}/results/${checkId}`, {
        headers: this.headers
      });

      console.log('📋 Results response:', JSON.stringify(response.data, null, 2));
      return response.data.results || [];
    } catch (error) {
      console.error(`❌ Error getting results:`, error.response?.data || error.message);
      return [];
    }
  }

  async getChecks() {
    try {
      console.log('📋 Getting all checks...');
      
      const response = await axios.get(`${this.baseUrl}/checks`, {
        headers: this.headers
      });

      console.log('📋 Checks response:', JSON.stringify(response.data, null, 2));
      return response.data.checks || [];
    } catch (error) {
      console.error(`❌ Error getting checks:`, error.response?.data || error.message);
      return [];
    }
  }

  async deleteCheck(checkId) {
    try {
      console.log(`🗑️ Deleting check: ${checkId}`);
      
      await axios.delete(`${this.baseUrl}/checks/${checkId}`, {
        headers: this.headers
      });

      console.log(`✅ Check deleted successfully`);
    } catch (error) {
      console.error(`❌ Error deleting check:`, error.response?.data || error.message);
      throw error;
    }
  }

  formatResults(results) {
    return results.map(result => ({
      timestamp: new Date(result.time * 1000).toISOString(),
      responseTime: result.responsetime,
      status: result.status,
      statusDesc: result.statusdesc
    }));
  }

  printResults(check, results) {
    console.log('\n' + '='.repeat(60));
    console.log(`📊 Pingdom Results for ${check.hostname}`);
    console.log(`📝 Name: ${check.name}`);
    console.log(`🆔 Check ID: ${check.id}`);
    console.log(`📱 Status: ${check.status}`);
    console.log('='.repeat(60));
    
    if (results && results.length > 0) {
      console.log('\n📈 RECENT RESULTS:');
      results.forEach((result, index) => {
        console.log(`  ${index + 1}. ${result.timestamp}`);
        console.log(`     Response Time: ${result.responseTime}ms`);
        console.log(`     Status: ${result.status} (${result.statusDesc})`);
      });
    }
    
    console.log('\n' + '='.repeat(60));
  }
}

async function main() {
  const api = new PingdomAPI();
  
  try {
    console.log('🚀 Starting Pingdom API test...\n');
    
    // Test URLs to monitor
    const testUrls = [
      { url: 'https://www.google.com', name: 'Google Test' },
      { url: 'https://www.github.com', name: 'GitHub Test' }
    ];
    
    const createdChecks = [];
    
    // Create checks for each URL
    for (const test of testUrls) {
      try {
        const check = await api.createCheck(test.url, test.name);
        createdChecks.push(check);
        
        // Wait a bit for the check to run
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Get results
        const results = await api.getCheckResults(check.id);
        api.printResults(check, api.formatResults(results));
        
      } catch (error) {
        console.error(`Failed to process ${test.url}:`, error.message);
      }
    }
    
    // Get all checks
    console.log('\n📋 All available checks:');
    const allChecks = await api.getChecks();
    allChecks.forEach(check => {
      console.log(`  - ${check.name} (${check.hostname}) - Status: ${check.status}`);
    });
    
    // Clean up test checks
    console.log('\n🧹 Cleaning up test checks...');
    for (const check of createdChecks) {
      try {
        await api.deleteCheck(check.id);
      } catch (error) {
        console.error(`Failed to delete check ${check.id}:`, error.message);
      }
    }
    
    console.log('✅ Test completed successfully!');
    
  } catch (error) {
    console.error('❌ Application failed:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = PingdomAPI;
