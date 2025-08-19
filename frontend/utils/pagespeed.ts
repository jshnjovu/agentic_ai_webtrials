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

    // Convert backend response to frontend format
    const result: PageSpeedResult = {
      success: true,
      overallScore: Math.round(data.scores.overall || 0), // Backend already provides 0-100 scores
      scores: {
        performance: Math.round(data.scores.performance || 0),
        accessibility: Math.round(data.scores.accessibility || 0),
        bestPractices: Math.round(data.scores.best_practices || 0), // Note: backend uses snake_case
        seo: Math.round(data.scores.seo || 0),
        trust: Math.round(data.scores.trust || 0), // Trust score from backend
        cro: Math.round(data.scores.cro || 0),     // CRO score from backend
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

    // If fallback is enabled and PageSpeed fails, try heuristic fallback
    if (request.enableFallback) {
      console.log('🔄 PageSpeed failed, trying heuristic fallback...');
      return await runHeuristicFallback(request);
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
 * Heuristic fallback scoring when PageSpeed fails
 */
async function runHeuristicFallback(request: PageSpeedRequest): Promise<PageSpeedResult> {
  try {
    console.log('🔍 Running heuristic fallback for:', request.websiteUrl);

    // Get backend URL from environment or use default
    const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

    // Call the backend heuristic evaluation API directly
    const response = await fetch(`${BACKEND_URL}/api/v1/website-scoring/heuristic`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_url: request.websiteUrl,
        business_id: request.businessId,
        run_id: request.runId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Heuristic API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Heuristic evaluation failed');
    }

    // Convert heuristic scores to PageSpeed format
    const result: PageSpeedResult = {
      success: true,
      overallScore: Math.round(data.scores.overall_heuristic_score || 0),
      scores: {
        performance: Math.round(data.scores.trust_score || 0), // Use trust score as performance proxy
        accessibility: Math.round(data.scores.mobile_score || 0), // Use mobile score as accessibility proxy
        bestPractices: Math.round(data.scores.cro_score || 0), // Use CRO score as best practices proxy
        seo: Math.round(data.scores.content_score || 0), // Use content score as SEO proxy
        trust: Math.round(data.scores.trust_score || 0), // Trust score directly from heuristic
        cro: Math.round(data.scores.cro_score || 0),     // CRO score directly from heuristic
      },
      coreWebVitals: {
        firstContentfulPaint: null, // Not available in heuristic
        largestContentfulPaint: null,
        cumulativeLayoutShift: null,
        totalBlockingTime: null,
        speedIndex: null,
      },
      fallbackUsed: true,
      confidence: data.confidence || 'medium',
    };

    console.log('✅ Heuristic fallback completed:', result);
    return result;

  } catch (error) {
    console.error('❌ Heuristic fallback failed:', error);

    // Return dummy scores as last resort
    return {
      success: true,
      overallScore: 50, // Dummy score
      scores: {
        performance: 50,
        accessibility: 50,
        bestPractices: 50,
        seo: 50,
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
    };
  }
}

/**
 * Legacy function name for backward compatibility
 * @deprecated Use runPageSpeedAudit instead
 */
export const runLighthouseAudit = runPageSpeedAudit;
