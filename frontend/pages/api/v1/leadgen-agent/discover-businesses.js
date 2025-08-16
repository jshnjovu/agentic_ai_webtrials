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

    // For Vercel deployment, we'll use a simplified approach
    // In production, this would call your backend services
    const businesses = await discoverBusinesses(location, niche);

    const transformedData = {
      results: businesses.map(business => ({
        business_name: business.name,
        website: business.website,
        score_overall: business.score,
        address: business.address,
        phone: business.phone,
        niche: business.niche,
        source: business.source
      })),
      total: businesses.length,
      success: true,
      message: `Found ${businesses.length} businesses in ${location} for ${niche}`,
      source: 'vercel-deployment'
    };

    res.status(200).json(transformedData);

  } catch (error) {
    console.error('API route error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}

// Simplified business discovery function for Vercel
async function discoverBusinesses(location, niche) {
  // This is a placeholder for real business discovery
  // In production, integrate with Google Places API, Yelp Fusion, etc.
  
  const sampleBusinesses = [
    {
      name: "Local Business 1",
      website: "https://example1.com",
      score: Math.floor(Math.random() * 100),
      address: `123 Main St, ${location}`,
      phone: "+1-555-0001",
      niche: niche,
      source: "sample"
    },
    {
      name: "Local Business 2", 
      website: "https://example2.com",
      score: Math.floor(Math.random() * 100),
      address: `456 Oak Ave, ${location}`,
      phone: "+1-555-0002",
      niche: niche,
      source: "sample"
    },
    {
      name: "Local Business 3",
      website: "https://example3.com", 
      score: Math.floor(Math.random() * 100),
      address: `789 Pine St, ${location}`,
      phone: "+1-555-0003",
      niche: niche,
      source: "sample"
    }
  ];

  return sampleBusinesses;
}
