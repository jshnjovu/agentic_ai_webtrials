/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
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
}

module.exports = nextConfig
