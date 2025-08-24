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
    const { location, niche, max_businesses, enable_scoring = true } = req.body;

    // Validate required fields
    if (!location || !niche) {
      return res.status(400).json({ 
        error: 'Missing required fields: location and niche are required' 
      });
    }

    console.log('🚀 Frontend batch request:', req.body);

    // Step 1: Discover businesses using Yelp Fusion
    console.log('🔍 Step 1: Discovering businesses...');
    const backendRequest = {
      term: niche,
      location: location,
      location_type: 'city',
      categories: [niche],
      limit: max_businesses || 2,
      radius: 5000
    };

    const discoverResponse = await fetch(`${BACKEND_URL}/api/v1/business-search/yelp-fusion/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendRequest),
    });

          if (!discoverResponse.ok) {
        const errorData = await discoverResponse.text();
        console.error('Backend Yelp Fusion search error:', discoverResponse.status, errorData);
        return res.status(discoverResponse.status).json({ 
          error: 'Failed to discover businesses via Yelp Fusion',
          details: errorData
        });
      }

    const backendData = await discoverResponse.json();
    console.log('✅ Business discovery completed:', backendData.businesses.length, 'businesses found');

    // Transform Yelp Fusion response to frontend expected format
    const discoveredBusinesses = backendData.businesses.map((business: any) => {
      let contactName = business.alias;
      if (business.attributes && business.attributes.about_this_biz_bio_first_name && business.attributes.about_this_biz_bio_last_name) {
        contactName = `${business.attributes.about_this_biz_bio_first_name} ${business.attributes.about_this_biz_bio_last_name}`;
      } else if (business.attributes && business.attributes.about_this_biz_bio_first_name) {
        contactName = business.attributes.about_this_biz_bio_first_name;
      }

      const postcode = business.location?.zip_code || '';
      const addressParts = [
        business.location?.address1,
        business.location?.address2
      ].filter(Boolean);
      const fullAddress = addressParts.join(', ');

      return {
        business_name: business.name,
        contact_name: contactName,
        niche: niche,
        location: location,
        place_id: business.id,
        rating: business.rating,
        user_ratings_total: business.review_count,
        address: fullAddress,
        postcode: postcode,
        phone: business.phone,
        website: business.attributes?.business_url || business.url,
        categories: business.categories?.map((cat: any) => cat.title) || [],
        confidence_level: 'high',
        source: 'yelp_fusion'
      };
    });

    // Step 2: Score websites using backend batch scoring (if enabled)
    let scoredBusinesses = discoveredBusinesses;
    
    if (enable_scoring && discoveredBusinesses.length > 0) {
      console.log('📊 Step 2: Scoring websites using backend batch API...');
      
      // Extract URLs for batch scoring
      const urls = discoveredBusinesses
        .filter((business: any) => business.website)
        .map((business: any) => business.website);

      if (urls.length > 0) {
        try {
          // Use backend batch scoring API
          const batchScoreRequest = {
            urls: urls,
            type: "comprehensive", // Use comprehensive analysis
            strategy: "mobile",
            max_concurrent: 3
          };

          console.log('🚀 Calling backend batch scoring API:', batchScoreRequest);

          const scoreResponse = await fetch(`${BACKEND_URL}/api/v1/website-scoring/batch`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(batchScoreRequest),
          });

          if (scoreResponse.ok) {
            const scoreData = await scoreResponse.json();
            console.log('✅ Backend batch scoring completed:', scoreData.results.length, 'websites scored');

            // Merge scoring results with business data
            scoredBusinesses = discoveredBusinesses.map((business: any, index: number) => {
              const scoreResult = scoreData.results.find((result: any) => 
                result.url === business.website || result.domain === business.website?.replace(/^https?:\/\//, '')
              );

              if (scoreResult && scoreResult.pageSpeed) {
                // Extract scores from backend results
                const mobile = scoreResult.pageSpeed.mobile;
                const desktop = scoreResult.pageSpeed.desktop;
                
                // Prefer mobile scores, fallback to desktop
                const scores = mobile?.scores || desktop?.scores || {};
                
                // Calculate overall score (average of available scores)
                const availableScores = [
                  scores.performance,
                  scores.accessibility,
                  scores.seo,
                  scoreResult.trustAndCRO?.trust?.parsed?.score || 0,
                  scoreResult.trustAndCRO?.cro?.parsed?.score || 0
                ].filter(score => score !== null && score !== undefined);
                
                const overallScore = availableScores.length > 0 
                  ? Math.round(availableScores.reduce((sum, score) => sum + score, 0) / availableScores.length)
                  : 0;

                // Extract opportunities
                const opportunities = scoreResult.pageSpeed.mobile?.opportunities || 
                                   scoreResult.pageSpeed.desktop?.opportunities || [];

                return {
                  ...business,
                  // Direct score fields for frontend components
                  score_overall: overallScore,
                  score_perf: scores.performance || 0,
                  score_access: scores.accessibility || 0,
                  score_seo: scores.seo || 0,
                  score_trust: scoreResult.trustAndCRO?.trust?.parsed?.score || 0,
                  score_cro: scoreResult.trustAndCRO?.cro?.parsed?.score || 0,
                  scoring_status: 'completed',
                  scoring_error: null,
                  last_scored: new Date().toISOString(),
                  // Website score details
                  website_score: {
                    overall_score: overallScore,
                    performance_score: scores.performance || 0,
                    accessibility_score: scores.accessibility || 0,
                    seo_score: scores.seo || 0,
                    trust_score: scoreResult.trustAndCRO?.trust?.parsed?.score || 0,
                    cro_score: scoreResult.trustAndCRO?.cro?.parsed?.score || 0,
                    opportunities: opportunities.map((opp: any) => ({
                      title: opp.title || 'Performance Improvement',
                      description: opp.description || 'Website optimization opportunity',
                      potentialSavings: opp.potentialSavings || 0,
                      unit: opp.unit || 'ms'
                    }))
                  },
                  // Top issues for UI display
                  top_issues: opportunities.slice(0, 3).map((opp: any) => opp.title || 'Performance Issue')
                };
              } else {
                // No scoring result available
                return {
                  ...business,
                  score_overall: 0,
                  score_perf: 0,
                  score_access: 0,
                  score_seo: 0,
                  score_trust: 0,
                  score_cro: 0,
                  scoring_status: 'no_website',
                  scoring_error: business.website ? 'Scoring failed' : 'No website',
                  last_scored: new Date().toISOString(),
                  website_score: null,
                  top_issues: []
                };
              }
            });
          } else {
            console.warn('⚠️ Backend batch scoring failed, using discovered businesses without scores');
            // Fallback: add default scores
            scoredBusinesses = discoveredBusinesses.map((business: any) => ({
              ...business,
              score_overall: 0,
              score_perf: 0,
              score_access: 0,
              score_seo: 0,
              score_trust: 0,
              score_cro: 0,
              scoring_status: 'failed',
              scoring_error: 'Backend scoring failed',
              last_scored: new Date().toISOString(),
              website_score: null,
              top_issues: []
            }));
          }
        } catch (scoringError) {
          console.error('❌ Backend batch scoring error:', scoringError);
          // Fallback: add default scores
          scoredBusinesses = discoveredBusinesses.map((business: any) => ({
            ...business,
            score_overall: 0,
            score_perf: 0,
            score_access: 0,
            score_seo: 0,
            score_trust: 0,
            score_cro: 0,
            scoring_status: 'error',
            scoring_error: 'Scoring error occurred',
            last_scored: new Date().toISOString(),
            website_score: null,
            top_issues: []
          }));
        }
      } else {
        console.log('⚠️ No websites found for scoring');
        // No websites to score
        scoredBusinesses = discoveredBusinesses.map((business: any) => ({
          ...business,
          score_overall: 0,
          score_perf: 0,
          score_access: 0,
          score_seo: 0,
          score_trust: 0,
          score_cro: 0,
          scoring_status: 'no_website',
          scoring_error: 'No website URL provided',
          last_scored: new Date().toISOString(),
          website_score: null,
          top_issues: []
        }));
      }
    }

    // Return combined results
    const response = {
      success: true,
      businesses: scoredBusinesses,
      total_results: scoredBusinesses.length,
      query: niche,
      location: location,
      discovery_count: discoveredBusinesses.length,
      scoring_enabled: enable_scoring,
      successful_scores: scoredBusinesses.filter((b: any) => b.scoring_status === 'completed').length,
      failed_scores: scoredBusinesses.filter((b: any) => b.scoring_status === 'failed' || b.scoring_status === 'error').length,
      no_websites: scoredBusinesses.filter((b: any) => b.scoring_status === 'no_website').length
    };

    console.log('✅ Batch API completed successfully:', response);
    return res.status(200).json(response);

  } catch (error) {
    console.error('❌ Batch API error:', error);
    return res.status(500).json({ 
      error: 'Internal server error during batch processing',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
