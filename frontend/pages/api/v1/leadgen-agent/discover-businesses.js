export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Backend endpoint: /api/v1/leadgen-agent/discover-businesses
  // This matches the FastAPI router configuration in backend/src/main.py

  // Handle preflight request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  // Enhanced method validation with detailed logging
  if (req.method !== 'GET' && req.method !== 'POST') {
    console.error('Method not allowed:', req.method);
    console.error('Allowed methods: GET, POST');
    console.error('Request headers:', req.headers);
    return res.status(405).json({ 
      error: 'Method not allowed',
      method: req.method,
      allowed: ['GET', 'POST'],
      headers: req.headers
    });
  }

  // Comprehensive request logging for debugging
  console.log('=== REQUEST DEBUG INFO ===');
  console.log('Method:', req.method);
  console.log('URL:', req.url);
  console.log('Headers:', req.headers);
  console.log('Query:', req.query);
  console.log('Body:', req.body);
  console.log('========================');

  // Simple test response to verify route is working
  if (req.method === 'GET' && req.query.test === 'true') {
    return res.status(200).json({ 
      message: 'API route is working correctly',
      method: req.method,
      timestamp: new Date().toISOString()
    });
  }

  try {
    // Extract parameters from query (GET) or body (POST)
    const { location, niche } = req.method === 'GET' ? req.query : req.body;
    
    // Debug logging (only in development)
    if (process.env.NODE_ENV === 'development') {
      console.log('Request method:', req.method);
      console.log('Request query:', req.query);
      console.log('Request body:', req.body);
      console.log('Extracted params:', { location, niche });
    }
    
    // Validate required parameters
    if (!location || !niche) {
      return res.status(400).json({
        error: 'Missing required parameters',
        required: ['location', 'niche'],
        received: { location, niche },
        method: req.method,
        query: req.query,
        body: req.body
      });
    }

    // Get backend URL from environment variable
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://agentic-ai-webtrials-47bn3kr9a-healthy-entrepreneursnl.vercel.app';
    
    if (process.env.NODE_ENV === 'development') {
      console.log('Attempting to connect to backend:', backendUrl);
    }
    
    try {
      // Proxy request to backend - use the correct endpoint path
      const backendResponse = await fetch(`${backendUrl}/api/v1/leadgen-agent/discover-businesses?location=${encodeURIComponent(location)}&niche=${encodeURIComponent(niche)}`);
      
      if (!backendResponse.ok) {
        throw new Error(`Backend responded with status: ${backendResponse.status}`);
      }

      const backendData = await backendResponse.json();
      if (process.env.NODE_ENV === 'development') {
        console.log('Backend response received:', backendData);
      }
      
      // Return backend response
      res.status(200).json(backendData);
      return;
    } catch (backendError) {
      if (process.env.NODE_ENV === 'development') {
        console.log('Backend connection failed, using fallback data:', backendError.message);
        console.log('Backend URL attempted:', `${backendUrl}/api/v1/leadgen-agent/discover-businesses`);
      }
      // Continue to fallback data
    }

    // If we reach here, backend failed, so return fallback data
    const fallbackData = {
      results: [
        {
          business_name: `${niche} Business 1 (${location})`,
          website: "https://example1.com",
          score_overall: Math.floor(Math.random() * 40) + 30, // Scores between 30-70
          address: `123 Main St, ${location}`,
          phone: "+1-555-0001",
          niche: niche,
          source: 'fallback',
          score_perf: Math.floor(Math.random() * 60) + 20,
          score_access: Math.floor(Math.random() * 60) + 20,
          score_seo: Math.floor(Math.random() * 60) + 20,
          score_trust: Math.floor(Math.random() * 60) + 20,
          score_cro: Math.floor(Math.random() * 60) + 20,
          top_issues: ['Mobile responsiveness', 'Page load speed', 'SEO optimization']
        },
        {
          business_name: `${niche} Business 2 (${location})`,
          website: "https://example2.com",
          score_overall: Math.floor(Math.random() * 60) + 30,
          address: `456 Oak Ave, ${location}`,
          phone: "+1-555-0002",
          niche: niche,
          source: 'fallback',
          score_perf: Math.floor(Math.random() * 60) + 20,
          score_access: Math.floor(Math.random() * 60) + 20,
          score_seo: Math.floor(Math.random() * 60) + 20,
          score_trust: Math.floor(Math.random() * 60) + 20,
          score_cro: Math.floor(Math.random() * 60) + 20,
          top_issues: ['Content quality', 'User experience', 'Conversion optimization']
        }
      ],
      total: 2,
      success: true,
      message: `Backend unavailable, showing fallback data for ${location} ${niche}`,
      source: 'fallback'
    };
    
    if (process.env.NODE_ENV === 'development') {
      console.log('Sending fallback data:', fallbackData);
    }
    res.status(200).json(fallbackData);
    return;

  } catch (error) {
    console.error('API route error:', error);
    
    // Return error response for unexpected errors
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      timestamp: new Date().toISOString()
    });
  }
}
