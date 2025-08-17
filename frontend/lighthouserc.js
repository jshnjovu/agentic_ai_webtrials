module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000'], // Frontend development server
      numberOfRuns: 3, // Multiple runs for more accurate results
      settings: {
        chromeFlags: '--headless --no-sandbox --disable-dev-shm-usage --disable-gpu',
        preset: 'desktop',
        throttling: {
          rttMs: 40,
          throughputKbps: 10240,
          cpuSlowdownMultiplier: 1,
          requestLatencyMs: 0,
          downloadThroughputKbps: 0,
          uploadThroughputKbps: 0
        },
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
        output: 'json',
        quiet: true,
        noEnableErrorReporting: true
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['warn', {minScore: 0.7}],
        'categories:accessibility': ['warn', {minScore: 0.8}],
        'categories:best-practices': ['warn', {minScore: 0.8}],
        'categories:seo': ['warn', {minScore: 0.8}],
        'first-contentful-paint': ['warn', {maxNumericValue: 2000}],
        'largest-contentful-paint': ['warn', {maxNumericValue: 2500}],
        'cumulative-layout-shift': ['warn', {maxNumericValue: 0.1}],
        'total-blocking-time': ['warn', {maxNumericValue: 300}],
        'speed-index': ['warn', {maxNumericValue: 3000}]
      }
    },
    upload: {
      target: 'temporary-public-storage'
    }
  }
};
