'use client'

import { Provider } from 'react-redux'
import { ThemeProvider } from 'next-themes'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { store } from '@/store'
import { useState, useEffect } from 'react'
import { setCredentials, setLoading } from '@/store/slices/authSlice'
import { tokenManager, authService } from '@/lib/auth'

function AuthHydration({ children }: { children: React.ReactNode }) {
  const [isHydrated, setIsHydrated] = useState(false)

  useEffect(() => {
    const hydrateAuth = async () => {
      store.dispatch(setLoading(true))
      const accessToken = tokenManager.getAccessToken()
      const refreshToken = tokenManager.getRefreshToken()

      if (accessToken && refreshToken) {
        try {
          // Fetch user profile to restore auth state
          const user = await authService.getProfile()
          store.dispatch(
            setCredentials({
              user,
              accessToken,
              refreshToken,
            })
          )
        } catch (error) {
          // Token invalid, clear them
          tokenManager.clearTokens()
          store.dispatch(setLoading(false))
        }
      } else {
        store.dispatch(setLoading(false))
      }
      setIsHydrated(true)
    }

    hydrateAuth()
  }, [])

  if (!isHydrated) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
          <p className="text-sm text-muted-foreground">Loading fLOKr...</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 60 * 1000,
        retry: 1,
      },
    },
  }))
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-gray-600"></div>
      </div>
    )
  }

  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          <AuthHydration>{children}</AuthHydration>
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>
  )
}
