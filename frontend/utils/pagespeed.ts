/**
 * PageSpeed utility for frontend website scoring
 * Updated to use comprehensive analysis for Trust and CRO scores
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
  seo: number;
  trust: number;
  cro: number;
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
  opportunities?: Array<{
    title: string;
    description: string;
    potentialSavings: number;
    unit: string;
  }>;
}

/**
 * Run comprehensive website analysis using the backend API
 * This includes PageSpeed scores PLUS Trust and CRO scores
 */
export async function runPageSpeedAudit(request: PageSpeedRequest): Promise<PageSpeedResult> {
  try {
    console.log('🚀 Running comprehensive website analysis for:', request.websiteUrl);

    // Get backend URL from environment or use default
    const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://127.0.0.1:8000';

    // Call the backend comprehensive analysis API to get ALL scores including Trust and CRO
    const response = await fetch(`${BACKEND_URL}/api/v1/website-scoring/comprehensive`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_url: request.websiteUrl,
        strategy: request.strategy,
      }),
    });

    if (!response.ok) {
      throw new Error(`Comprehensive analysis API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    // Debug: Log the actual response structure
    console.log('🔍 Backend comprehensive analysis response:', {
      success: data.success !== false,
      pageSpeed: data.pageSpeed,
      trustAndCRO: data.trustAndCRO,
      raw_data: data
    });

    // Extract scores from the comprehensive analysis result
    let performance = 0, accessibility = 0, seo = 0, trust = 0, cro = 0;
    let opportunities: Array<{title: string; description: string; potentialSavings: number; unit: string}> = [];
    
    // Extract PageSpeed scores (mobile preferred, fallback to desktop)
    if (data.pageSpeed) {
      const mobile = data.pageSpeed.mobile;
      const desktop = data.pageSpeed.desktop;
      const scores = mobile?.scores || desktop?.scores || {};
      
      performance = scores.performance || 0;
      accessibility = scores.accessibility || 0;
      seo = scores.seo || 0;
      
      // Extract opportunities from the opportunities field (includes both specific and generic)
      if (data.opportunities && data.opportunities.length > 0) {
        opportunities = data.opportunities;
      } else if (mobile?.opportunities) {
        opportunities = mobile.opportunities;
      } else if (desktop?.opportunities) {
        opportunities = desktop.opportunities;
      }
    }
    
    // Extract Trust and CRO scores from the comprehensive analysis
    if (data.trustAndCRO) {
      trust = data.trustAndCRO.trust?.parsed?.score || 0;
      cro = data.trustAndCRO.cro?.parsed?.score || 0;
    }
    
    // Use the backend's calculated Overall score from unified.py
    // This ensures zeros are properly counted: (96 + 82 + 91 + 0 + 90) / 5 = 71.8
    const overallScore = data.overall_score !== undefined ? Math.round(data.overall_score) : 
      Math.round((performance + accessibility + seo + trust + cro) / 5);

    // Convert backend response to frontend format
    const result: PageSpeedResult = {
      success: true,
      overallScore: overallScore,
      scores: {
        performance: Math.round(performance),
        accessibility: Math.round(accessibility),
        seo: Math.round(seo),
        trust: Math.round(trust),
        cro: Math.round(cro),
      },
      coreWebVitals: {
        firstContentfulPaint: null, // Will be populated if available
        largestContentfulPaint: null,
        cumulativeLayoutShift: null,
        totalBlockingTime: null,
        speedIndex: null,
      },
      fallbackUsed: false, // Comprehensive analysis is the primary method
      confidence: 'high',
      opportunities: opportunities,
    };

    console.log('✅ Comprehensive analysis completed:', result);
    console.log('🔍 Score breakdown:', {
      performance, accessibility, seo, trust, cro,
      sum: performance + accessibility + seo + trust + cro,
      count: 5,
      average: (performance + accessibility + seo + trust + cro) / 5,
      backendOverall: data.overall_score,
      finalOverall: overallScore
    });
    return result;

  } catch (error) {
    console.error('❌ Comprehensive analysis failed:', error);

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

    // If fallback is enabled and comprehensive analysis fails, return simplified fallback
    if (request.enableFallback) {
      console.log('🔄 Comprehensive analysis failed, using simplified fallback scoring...');
      
      // Return simplified fallback scores based on basic heuristics
      return {
        success: true,
        overallScore: 50, // Neutral fallback score
        scores: {
          performance: 50,
          accessibility: 50,
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
        error: `Comprehensive analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}. Using fallback scores.`
      };
    }

    // Return error result
    return {
      success: false,
      overallScore: 0,
      scores: {
        performance: 0,
        accessibility: 0,
        seo: 0,
        trust: 0,
        cro: 0,
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
