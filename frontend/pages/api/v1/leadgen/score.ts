import type { NextApiRequest, NextApiResponse } from 'next';
import { runPageSpeedAudit } from '../../../../utils/pagespeed';

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

        // Use FRONTEND PageSpeed utility with fallback enabled
        const pagespeedRequest = {
          websiteUrl: business.website,
          businessId: business.place_id,
          runId: `score_${Date.now()}_${business.place_id}`,
          strategy: "desktop" as const, // Default to desktop strategy
          enableFallback: true // Enable heuristic fallback when PageSpeed fails
        };

        console.log(`🚀 Frontend PageSpeed request with fallback:`, pagespeedRequest);

        // Run PageSpeed audit directly in frontend (with fallback)
        const scoreData = await runPageSpeedAudit(pagespeedRequest);
        
        if (!scoreData.success) {
          console.error(`❌ PageSpeed scoring failed for ${business.business_name}:`, scoreData.error);
          
          scoredBusinesses.push({
            ...business,
            website_score: null,
            scoring_status: 'failed',
            scoring_error: `PageSpeed audit failed: ${scoreData.error}`
          });
          continue;
        }

        console.log(`✅ Website scoring successful for ${business.business_name}:`, {
          overall: scoreData.overallScore,
          performance: scoreData.scores.performance,
          accessibility: scoreData.scores.accessibility,
          bestPractices: scoreData.scores.bestPractices,
          seo: scoreData.scores.seo,
          fallbackUsed: scoreData.fallbackUsed || false
        });

        // Extract relevant scoring data from frontend results
        const websiteScore = {
          overall_score: scoreData.overallScore || 0,
          performance_score: scoreData.scores.performance || 0,
          accessibility_score: scoreData.scores.accessibility || 0,
          best_practices_score: scoreData.scores.bestPractices || 0,
          seo_score: scoreData.scores.seo || 0,
          first_contentful_paint: scoreData.coreWebVitals.firstContentfulPaint || null,
          largest_contentful_paint: scoreData.coreWebVitals.largestContentfulPaint || null,
          cumulative_layout_shift: scoreData.coreWebVitals.cumulativeLayoutShift || null,
          total_blocking_time: scoreData.coreWebVitals.totalBlockingTime || null,
          speed_index: scoreData.coreWebVitals.speedIndex || null,
          scoring_method: scoreData.fallbackUsed ? 'heuristic_fallback' : 'pagespeed',
          confidence: scoreData.confidence
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
