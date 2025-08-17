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

    // Transform frontend request to backend business search format
    const backendRequest = {
      query: niche,
      location: location,
      location_type: 'city', // Default to city search
      category: niche,
      max_results: max_businesses || 10,
      radius: 5000 // Default 5km radius
    };

    console.log('🔍 Frontend discover request:', req.body);
    console.log('🔍 Backend business search request:', backendRequest);

    // Call backend business search API
    const response = await fetch(`${BACKEND_URL}/api/v1/business-search/google-places/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(backendRequest),
    });

    if (!response.ok) {
      const errorData = await response.text();
      console.error('Backend business search error:', response.status, errorData);
      return res.status(response.status).json({ 
        error: 'Failed to discover businesses',
        details: errorData
      });
    }

    const backendData = await response.json();
    console.log('✅ Backend business search response:', backendData);

    // Transform backend response to frontend expected format
    const frontendResponse = {
      businesses: backendData.results.map((business: any) => ({
        business_name: business.name,
        niche: niche,
        location: location,
        place_id: business.place_id,
        rating: business.rating,
        user_ratings_total: business.user_ratings_total,
        address: business.address || business.formatted_address,
        phone: business.phone,
        website: business.website,
        categories: business.types || business.categories || [],
        confidence_level: business.confidence_level || 'medium'
      })),
      total_results: backendData.total_results,
      query: backendData.query,
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
