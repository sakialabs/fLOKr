'use client'

import { ReactNode } from 'react'
import { Providers } from '@/components/providers'
import { Toaster } from '@/components/ui/sonner'
import { ErrorBoundary } from '@/components/error-boundary'

export function ClientLayout({ children }: { children: ReactNode }) {
  return (
    <ErrorBoundary>
      <Providers>
        {children}
        <Toaster />
      </Providers>
    </ErrorBoundary>
  )
}
