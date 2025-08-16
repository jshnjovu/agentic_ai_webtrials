// Environment Configuration for LeadGen Frontend
const config = {
  development: {
    backendUrl: 'http://localhost:8000',
    environment: 'development'
  },
  production: {
    backendUrl: 'https://agentic-ai-webtrials.vercel.app',
    environment: 'production'
  }
};

// Get current environment
const env = process.env.NODE_ENV || 'development';

// Export configuration
module.exports = {
  ...config[env],
  // Allow override via environment variable
  backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || config[env].backendUrl
};
