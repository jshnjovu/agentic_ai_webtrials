/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    appDir: false,
  },
  // Ensure proper static export if needed
  trailingSlash: false,
  // Optimize for Vercel
  poweredByHeader: false,
  compress: true,
}

module.exports = nextConfig
