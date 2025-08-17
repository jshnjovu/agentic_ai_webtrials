import type { NextApiRequest, NextApiResponse } from 'next';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { businesses } = req.body;

    // Validate required fields
    if (!businesses || !Array.isArray(businesses) || businesses.length === 0) {
      return res.status(400).json({
        error: 'Missing required fields: businesses array is required'
      });
    }

    console.log('📊 Frontend score request:', { businessCount: businesses.length });
    console.log('📊 First business sample:', businesses[0]);

    // Process each business to score their website
    const scoredBusinesses = [];
    
    for (const business of businesses) {
      try {
        // Check if business has a website
        if (!business.website) {
          console.log(`⚠️ Business ${business.business_name} has no website, skipping scoring`);
          scoredBusinesses.push({
            ...business,
            website_score: null,
            scoring_status: 'no_website',
            scoring_error: 'No website URL provided'
          });
          continue;
        }

        console.log(`🔍 Scoring website for: ${business.business_name} (${business.website})`);

        // Call backend Lighthouse audit endpoint
        const lighthouseRequest = {
          website_url: business.website,
          business_id: business.place_id,
          run_id: `score_${Date.now()}_${business.place_id}`,
          strategy: "desktop", // Default to desktop strategy
          categories: ["performance", "accessibility", "best-practices", "seo"],
          throttling: "simulated",
          max_wait: 30
        };

        console.log(`🔍 Backend Lighthouse request:`, lighthouseRequest);

        const scoreResponse = await fetch(`${BACKEND_URL}/api/v1/website-scoring/lighthouse`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(lighthouseRequest),
        });

        if (!scoreResponse.ok) {
          const errorData = await scoreResponse.text();
          console.error(`❌ Lighthouse scoring failed for ${business.business_name}:`, scoreResponse.status, errorData);
          
          scoredBusinesses.push({
            ...business,
            website_score: null,
            scoring_status: 'failed',
            scoring_error: `Lighthouse API failed: ${scoreResponse.status} - ${errorData}`
          });
          continue;
        }

        const scoreData = await scoreResponse.json();
        console.log(`✅ Lighthouse scoring successful for ${business.business_name}:`, scoreData);

        // Extract relevant scoring data
        const websiteScore = {
          overall_score: scoreData.overall_score || 0,
          performance_score: scoreData.performance_score || 0,
          accessibility_score: scoreData.accessibility_score || 0,
          best_practices_score: scoreData.best_practices_score || 0,
          seo_score: scoreData.seo_score || 0,
          first_contentful_paint: scoreData.first_contentful_paint || null,
          largest_contentful_paint: scoreData.largest_contentful_paint || null,
          cumulative_layout_shift: scoreData.cumulative_layout_shift || null,
          total_blocking_time: scoreData.total_blocking_time || null,
          speed_index: scoreData.speed_index || null
        };

        scoredBusinesses.push({
          ...business,
          website_score: websiteScore,
          scoring_status: 'completed',
          scoring_error: null,
          last_scored: new Date().toISOString()
        });

      } catch (businessError) {
        console.error(`❌ Error scoring business ${business.business_name}:`, businessError);
        
        scoredBusinesses.push({
          ...business,
          website_score: null,
          scoring_status: 'error',
          scoring_error: `Scoring error: ${businessError instanceof Error ? businessError.message : 'Unknown error'}`
        });
      }
    }

    console.log(`✅ Website scoring completed: ${scoredBusinesses.length} businesses processed`);

    // Return scored businesses
    const response = {
      success: true,
      businesses: scoredBusinesses,
      total_scored: scoredBusinesses.length,
      successful_scores: scoredBusinesses.filter(b => b.scoring_status === 'completed').length,
      failed_scores: scoredBusinesses.filter(b => b.scoring_status === 'failed' || b.scoring_status === 'error').length,
      no_websites: scoredBusinesses.filter(b => b.scoring_status === 'no_website').length
    };

    console.log('✅ Frontend score response:', response);
    return res.status(200).json(response);

  } catch (error) {
    console.error('API route error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
