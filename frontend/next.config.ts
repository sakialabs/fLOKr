import type { NextConfig } from 'next'
import { PHASE_DEVELOPMENT_SERVER } from 'next/constants'
import path from 'path'

const normalizeApiBaseUrl = (url: string) => {
  const trimmedUrl = url.trim().replace(/\/+$/, '')

  if (!trimmedUrl) {
    return 'http://localhost:8000/api'
  }

  return trimmedUrl.endsWith('/api') ? trimmedUrl : `${trimmedUrl}/api`
}

const createNextConfig = (phase: string): NextConfig => ({
  reactStrictMode: true,
  distDir: phase === PHASE_DEVELOPMENT_SERVER ? '.next-dev' : '.next',
  outputFileTracingRoot: path.join(__dirname, '../'),
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  async redirects() {
    return [
      {
        source: '/ori',
        destination: '/navi',
        permanent: false,
      },
    ]
  },
  async rewrites() {
    const apiUrl = normalizeApiBaseUrl(
      process.env.NEXT_PRIVATE_API_URL ||
        process.env.API_PROXY_TARGET ||
        'http://localhost:8000'
    )
    return [
      {
        source: '/api/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ]
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }
    return config
  },
})

export default createNextConfig
