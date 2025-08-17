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
}

module.exports = nextConfig
