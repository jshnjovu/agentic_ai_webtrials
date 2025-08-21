/**
 * PageSpeed utility for frontend website scoring
 * Replaces the previous Lighthouse utility
 */

export interface PageSpeedRequest {
  websiteUrl: string;
  businessId: string;
  runId: string;
  strategy: 'desktop' | 'mobile';
  enableFallback?: boolean;
}

export interface PageSpeedScores {
  performance: number;
  accessibility: number;
  bestPractices: number;
  seo: number;
  trust?: number;
  cro?: number;
}

export interface CoreWebVitals {
  firstContentfulPaint: number | null;
  largestContentfulPaint: number | null;
  cumulativeLayoutShift: number | null;
  totalBlockingTime: number | null;
  speedIndex: number | null;
}

export interface PageSpeedResult {
  success: boolean;
  overallScore: number;
  scores: PageSpeedScores;
  coreWebVitals: CoreWebVitals;
  fallbackUsed: boolean;
  confidence: 'high' | 'medium' | 'low';
  error?: string;
}

/**
 * Run PageSpeed audit using the backend API
 */
export async function runPageSpeedAudit(request: PageSpeedRequest): Promise<PageSpeedResult> {
  try {
    console.log('🚀 Running PageSpeed audit for:', request.websiteUrl);

    // Get backend URL from environment or use default
    const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

    // Call the backend PageSpeed API directly
    const response = await fetch(`${BACKEND_URL}/api/v1/website-scoring/pagespeed`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_url: request.websiteUrl,
        business_id: request.businessId,
        run_id: request.runId,
        strategy: request.strategy,
        categories: ['performance', 'accessibility', 'best-practices', 'seo']
      }),
    });

    if (!response.ok) {
      throw new Error(`PageSpeed API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'PageSpeed audit failed');
    }

    // Debug: Log the actual response structure
    console.log('🔍 Backend PageSpeed response:', {
      success: data.success,
      scores: data.scores,
      core_web_vitals: data.core_web_vitals,
      raw_data: data
    });

    // Convert backend response to frontend format
    const result: PageSpeedResult = {
      success: true,
      overallScore: Math.round(data.scores.overall || 0), // Backend already provides 0-100 scores
      scores: {
        performance: Math.round(data.scores.performance || 0),
        accessibility: Math.round(data.scores.accessibility || 0),
        bestPractices: Math.round(data.scores.best_practices || 0), // Note: backend uses snake_case
        seo: Math.round(data.scores.seo || 0),
        trust: 0, // PageSpeed doesn't provide trust score
        cro: 0,   // PageSpeed doesn't provide CRO score
      },
      coreWebVitals: {
        firstContentfulPaint: data.core_web_vitals?.first_contentful_paint || null,
        largestContentfulPaint: data.core_web_vitals?.largest_contentful_paint || null,
        cumulativeLayoutShift: data.core_web_vitals?.cumulative_layout_shift || null,
        totalBlockingTime: data.core_web_vitals?.total_blocking_time || null,
        speedIndex: data.core_web_vitals?.speed_index || null,
      },
      fallbackUsed: false, // PageSpeed is the primary method
      confidence: 'high',
    };

    console.log('✅ PageSpeed audit completed:', result);
    return result;

  } catch (error) {
    console.error('❌ PageSpeed audit failed:', error);

    // Enhanced error logging
    const errorDetails = {
      websiteUrl: request.websiteUrl,
      businessId: request.businessId,
      runId: request.runId,
      strategy: request.strategy,
      error: error instanceof Error ? error.message : 'Unknown error',
      timestamp: new Date().toISOString(),
      backendUrl: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000'
    };
    
    console.error('🔍 Detailed error context:', errorDetails);

    // If fallback is enabled and PageSpeed fails, return simplified fallback
    if (request.enableFallback) {
      console.log('🔄 PageSpeed failed, using simplified fallback scoring...');
      
      // Return simplified fallback scores based on basic heuristics
      return {
        success: true,
        overallScore: 50, // Neutral fallback score
        scores: {
          performance: 50,
          accessibility: 50,
          bestPractices: 50,
          seo: 50,
          trust: 50,
          cro: 50,
        },
        coreWebVitals: {
          firstContentfulPaint: null,
          largestContentfulPaint: null,
          cumulativeLayoutShift: null,
          totalBlockingTime: null,
          speedIndex: null,
        },
        fallbackUsed: true,
        confidence: 'low',
        error: `PageSpeed API failed: ${error instanceof Error ? error.message : 'Unknown error'}. Using fallback scores.`
      };
    }

    // Return error result
    return {
      success: false,
      overallScore: 0,
      scores: {
        performance: 0,
        accessibility: 0,
        bestPractices: 0,
        seo: 0,
      },
      coreWebVitals: {
        firstContentfulPaint: null,
        largestContentfulPaint: null,
        cumulativeLayoutShift: null,
        totalBlockingTime: null,
        speedIndex: null,
      },
      fallbackUsed: false,
      confidence: 'low',
      error: error instanceof Error ? error.message : 'Unknown error',
    };
  }
}

/**
 * Legacy function name for backward compatibility
 * @deprecated Use runPageSpeedAudit instead
 */
export const runLighthouseAudit = runPageSpeedAudit;
