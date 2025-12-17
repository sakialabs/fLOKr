import type { NextConfig } from 'next'
import path from 'path'

const nextConfig: NextConfig = {
  reactStrictMode: true,
  outputFileTracingRoot: path.join(__dirname, '../'),
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  // Optimize chunk loading
  experimental: {
    optimizePackageImports: ['@/components', '@/lib'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_API_URL + '/:path*',
      },
    ]
  },
  webpack: (config, { isServer }) => {
    // Fix for framer-motion and other client-side only packages
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
      
      // Improve chunk loading reliability
      config.output = {
        ...config.output,
        crossOriginLoading: 'anonymous',
      }
    }
    return config
  },
}

export default nextConfig
