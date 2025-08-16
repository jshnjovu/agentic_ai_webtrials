export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight request
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    const { location, niche } = req.query;
    
    // Validate required parameters
    if (!location || !niche) {
      return res.status(400).json({
        error: 'Missing required parameters',
        required: ['location', 'niche'],
        received: { location, niche }
      });
    }

    // Get backend URL from environment variable
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'https://agentic-ai-webtrials-47bn3kr9a-healthy-entrepreneursnl.vercel.app';
    
    // Proxy request to backend
    const backendResponse = await fetch(`${backendUrl}/discover_businesses?location=${encodeURIComponent(location)}&niche=${encodeURIComponent(niche)}`);
    
    if (!backendResponse.ok) {
      throw new Error(`Backend responded with status: ${backendResponse.status}`);
    }

    const backendData = await backendResponse.json();
    
    // Return backend response
    res.status(200).json(backendData);

  } catch (error) {
    console.error('API route error:', error);
    
    // Fallback to sample data if backend is unavailable
    const { location, niche } = req.query;
    const fallbackData = {
      results: [
        {
          business_name: "Local Business 1 (Fallback)",
          website: "https://example1.com",
          score_overall: Math.floor(Math.random() * 100),
          address: `123 Main St, ${location}`,
          phone: "+1-555-0001",
          niche: niche,
          source: 'fallback'
        }
      ],
      total: 1,
      success: false,
      message: `Backend unavailable, showing fallback data for ${location} ${niche}`,
      error: error.message,
      source: 'fallback'
    };
    
    res.status(200).json(fallbackData);
  }
}
