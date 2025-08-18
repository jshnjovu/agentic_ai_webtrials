/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/templates/:path*',
        destination: '/api/templates/:path*',
      },
    ]
  },
  // Handle ES modules in API routes
  experimental: {
    esmExternals: 'loose'
  },
  // Transpile Lighthouse packages for Node.js compatibility
  transpilePackages: ['lighthouse', 'chrome-launcher'],
  // Ensure proper module resolution
  webpack: (config, { isServer }) => {
    if (isServer) {
      // Handle ES modules on the server side
      config.externals = config.externals || [];
      config.externals.push({
        'lighthouse': 'commonjs lighthouse',
        'chrome-launcher': 'commonjs chrome-launcher'
      });
    }
    return config;
  }
}

module.exports = nextConfig
