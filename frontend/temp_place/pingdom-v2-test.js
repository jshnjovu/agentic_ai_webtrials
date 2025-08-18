const axios = require('axios');
require('dotenv').config({ path: './env.local' });

class PingdomV2Test {
  constructor() {
    this.apiKey = process.env.PINGDOM_API_KEY;
    this.baseUrl = 'https://api.pingdom.com/api/2.1';
    this.headers = {
      'Authorization': `Bearer ${this.apiKey}`,
      'Content-Type': 'application/json'
    };
  }

  async testV2API() {
    try {
      console.log('🚀 Testing Pingdom API v2.1...\n');
      console.log(`API Key: ${this.apiKey.substring(0, 10)}...`);
      console.log(`Base URL: ${this.baseUrl}\n`);

      // Test 1: Create a check
      console.log('📝 Test 1: Creating a check...');
      const checkResponse = await axios.post(`${this.baseUrl}/checks`, {
        name: 'V2 Test Check',
        host: 'google.com',
        type: 'http'
      }, { headers: this.headers });

      console.log('✅ Check created successfully!');
      console.log('Check details:', JSON.stringify(checkResponse.data, null, 2));

      const checkId = checkResponse.data.check.id;

      // Test 2: Get check details
      console.log('\n📊 Test 2: Getting check details...');
      try {
        const checkDetails = await axios.get(`${this.baseUrl}/checks/${checkId}`, {
          headers: this.headers
        });
        console.log('✅ Check details retrieved!');
        console.log('Details:', JSON.stringify(checkDetails.data, null, 2));
      } catch (error) {
        console.log('❌ Could not get check details:', error.response?.data || error.message);
      }

      // Test 3: List all checks
      console.log('\n📋 Test 3: Listing all checks...');
      try {
        const allChecks = await axios.get(`${this.baseUrl}/checks`, {
          headers: this.headers
        });
        console.log('✅ All checks retrieved!');
        console.log('Total checks:', allChecks.data.checks?.length || 0);
        if (allChecks.data.checks) {
          allChecks.data.checks.forEach((check, index) => {
            console.log(`  ${index + 1}. ${check.name} (${check.hostname}) - ID: ${check.id}`);
          });
        }
      } catch (error) {
        console.log('❌ Could not list checks:', error.response?.data || error.message);
      }

      // Test 4: Delete the test check
      console.log('\n🗑️ Test 4: Deleting test check...');
      try {
        await axios.delete(`${this.baseUrl}/checks/${checkId}`, {
          headers: this.headers
        });
        console.log('✅ Test check deleted successfully!');
      } catch (error) {
        console.log('❌ Could not delete check:', error.response?.data || error.message);
      }

      console.log('\n✅ V2 API test completed!');

    } catch (error) {
      console.error('❌ Test failed:', error.response?.data || error.message);
    }
  }
}

// Run the test
const test = new PingdomV2Test();
test.testV2API().catch(console.error);
