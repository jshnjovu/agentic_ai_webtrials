/**
 * Frontend Lighthouse utility for website performance auditing
 * Integrates with backend Lighthouse CLI service and provides client-side functionality
 */

export interface LighthouseScores {
  performance: number;
  accessibility: number;
  bestPractices: number;
  seo: number;
}

export interface CoreWebVitals {
  firstContentfulPaint?: number;
  largestContentfulPaint?: number;
  cumulativeLayoutShift?: number;
  totalBlockingTime?: number;
  speedIndex?: number;
}

export interface LighthouseResult {
  success: boolean;
  websiteUrl: string;
  businessId: string;
  runId?: string;
  auditTimestamp: number;
  strategy: 'desktop' | 'mobile';
  scores: LighthouseScores;
  overallScore: number;
  coreWebVitals: CoreWebVitals;
  confidence: 'low' | 'medium' | 'high';
  error?: string;
  errorCode?: string;
  context?: string;
}

export interface LighthouseAuditRequest {
  websiteUrl: string;
  businessId: string;
  runId?: string;
  strategy?: 'desktop' | 'mobile';
}

/**
 * Run Lighthouse audit via backend service
 */
export async function runLighthouseAudit(
  request: LighthouseAuditRequest,
  backendUrl: string = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
): Promise<LighthouseResult> {
  try {
    const response = await fetch(`${backendUrl}/api/v1/website-scoring/lighthouse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_url: request.websiteUrl,
        business_id: request.businessId,
        run_id: request.runId,
        strategy: request.strategy || 'desktop'
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Lighthouse audit failed: ${response.status} - ${errorText}`);
    }

    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Lighthouse audit error:', error);
    return {
      success: false,
      websiteUrl: request.websiteUrl,
      businessId: request.businessId,
      runId: request.runId,
      auditTimestamp: Date.now(),
      strategy: request.strategy || 'desktop',
      scores: { performance: 0, accessibility: 0, bestPractices: 0, seo: 0 },
      overallScore: 0,
      coreWebVitals: {},
      confidence: 'low',
      error: error instanceof Error ? error.message : 'Unknown error',
      errorCode: 'REQUEST_FAILED',
      context: 'frontend_audit_request'
    };
  }
}

/**
 * Calculate overall score from individual category scores
 */
export function calculateOverallScore(scores: LighthouseScores): number {
  const weights = {
    performance: 0.4,
    accessibility: 0.25,
    bestPractices: 0.2,
    seo: 0.15
  };

  return Math.round(
    scores.performance * weights.performance +
    scores.accessibility * weights.accessibility +
    scores.bestPractices * weights.bestPractices +
    scores.seo * weights.seo
  );
}

/**
 * Get performance rating based on score
 */
export function getPerformanceRating(score: number): 'poor' | 'needs-improvement' | 'good' | 'excellent' {
  if (score >= 90) return 'excellent';
  if (score >= 80) return 'good';
  if (score >= 50) return 'needs-improvement';
  return 'poor';
}

/**
 * Format Core Web Vitals for display
 */
export function formatCoreWebVitals(coreWebVitals: CoreWebVitals): Record<string, string> {
  const formatted: Record<string, string> = {};
  
  if (coreWebVitals.firstContentfulPaint) {
    formatted.firstContentfulPaint = `${coreWebVitals.firstContentfulPaint.toFixed(0)}ms`;
  }
  
  if (coreWebVitals.largestContentfulPaint) {
    formatted.largestContentfulPaint = `${coreWebVitals.largestContentfulPaint.toFixed(0)}ms`;
  }
  
  if (coreWebVitals.cumulativeLayoutShift) {
    formatted.cumulativeLayoutShift = coreWebVitals.cumulativeLayoutShift.toFixed(3);
  }
  
  if (coreWebVitals.totalBlockingTime) {
    formatted.totalBlockingTime = `${coreWebVitals.totalBlockingTime.toFixed(0)}ms`;
  }
  
  if (coreWebVitals.speedIndex) {
    formatted.speedIndex = `${coreWebVitals.speedIndex.toFixed(0)}ms`;
  }
  
  return formatted;
}

/**
 * Get color class for score display
 */
export function getScoreColorClass(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 80) return 'text-blue-600';
  if (score >= 50) return 'text-yellow-600';
  return 'text-red-600';
}

/**
 * Get background color class for score display
 */
export function getScoreBgColorClass(score: number): string {
  if (score >= 90) return 'bg-green-100';
  if (score >= 80) return 'bg-blue-100';
  if (score >= 50) return 'bg-yellow-100';
  return 'bg-red-100';
}
