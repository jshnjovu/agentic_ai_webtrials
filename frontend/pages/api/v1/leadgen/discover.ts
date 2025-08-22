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
    const { location, niche, max_businesses } = req.body;

    // Validate required fields
    if (!location || !niche) {
      return res.status(400).json({ 
        error: 'Missing required fields: location and niche are required' 
      });
    }

    // Transform frontend request to Yelp Fusion business search format
    const backendRequest = {
      term: niche,
      location: location,
      location_type: 'city', // Default to city search
      categories: [niche], // Yelp uses categories array
      limit: max_businesses || 2,
      radius: 5000 // Default 5km radius
    };

    console.log('🔍 Frontend discover request:', req.body);
    console.log('🔍 Backend Yelp Fusion request:', backendRequest);

    // Call backend Yelp Fusion business search API
    const response = await fetch(`${BACKEND_URL}/api/v1/business-search/yelp-fusion/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendRequest),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Backend Yelp Fusion search error:', response.status, errorData);
      return res.status(response.status).json({ 
        error: 'Failed to discover businesses via Yelp Fusion',
        details: errorData
      });
    }

    const backendData = await response.json();
    console.log('✅ Backend Yelp Fusion response:', backendData);

    // Transform Yelp Fusion response to frontend expected format
    const frontendResponse = {
      businesses: backendData.businesses.map((business: any) => {
        // Contact name logic: use "about_this_biz_bio_first_name" + "about_this_biz_bio_last_name" if available, otherwise use "alias"
        let contactName = business.alias;
        if (business.attributes && business.attributes.about_this_biz_bio_first_name && business.attributes.about_this_biz_bio_last_name) {
          contactName = `${business.attributes.about_this_biz_bio_first_name} ${business.attributes.about_this_biz_bio_last_name}`;
        } else if (business.attributes && business.attributes.about_this_biz_bio_first_name) {
          contactName = business.attributes.about_this_biz_bio_first_name;
        }

        // Extract postcode from location object
        const postcode = business.location?.zip_code || '';

        // Build full address
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
          place_id: business.id, // Yelp uses 'id' instead of 'place_id'
          rating: business.rating,
          user_ratings_total: business.review_count, // Yelp uses 'review_count'
          address: fullAddress,
          postcode: postcode, // Extract postcode separately
          phone: business.phone,
          website: business.attributes?.business_url || business.url, // Yelp business URL or Yelp page URL
          categories: business.categories?.map((cat: any) => cat.title) || [],
          confidence_level: 'high', // Yelp data is generally high quality
          source: 'yelp_fusion'
        };
      }),
      total_results: backendData.total,
      query: backendData.term, // Yelp uses 'term' instead of 'query'
      location: backendData.location
    };

    console.log('✅ Transformed frontend response:', frontendResponse);
    return res.status(200).json(frontendResponse);

  } catch (error) {
    console.error('API route error:', error);
    return res.status(500).json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}
