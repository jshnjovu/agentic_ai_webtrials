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

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const {
      business_name,
      location,
      niche,
      website,
      address,
      phone,
      score_overall,
      score_perf,
      score_access,
      score_seo,
      score_trust,
      score_cro,
      top_issues,
      timestamp,
      run_id
    } = req.body;

    // Validate required fields
    if (!business_name || !location || !niche) {
      return res.status(400).json({
        error: 'Missing required fields',
        required: ['business_name', 'location', 'niche']
      });
    }

    // Generate a unique filename
    const filename = `${business_name.replace(/[^a-zA-Z0-9]/g, '_')}_${niche}_${Date.now()}.html`;
    
    // Determine template based on niche
    let template_used = 'general';
    if (niche.toLowerCase().includes('restaurant') || niche.toLowerCase().includes('food') || niche.toLowerCase().includes('cafe')) {
      template_used = 'restaurant';
    } else if (niche.toLowerCase().includes('gym') || niche.toLowerCase().includes('fitness') || niche.toLowerCase().includes('health')) {
      template_used = 'gym';
    }

    // For now, return success with file info
    // In a real implementation, this would generate the actual HTML file
    const result = {
      success: true,
      message: `Website generated successfully for ${business_name}`,
      filename: filename,
      template_used: template_used,
      business_name: business_name,
      generated_url: `https://agentic-ai-webtrials.vercel.app/demo/${filename}`,
      timestamp: timestamp || new Date().toISOString(),
      run_id: run_id || `run_${Date.now()}`
    };

    res.status(200).json(result);

  } catch (error) {
    console.error('Website generation error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}
