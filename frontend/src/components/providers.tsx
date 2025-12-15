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
    return null // or a loading spinner
  }

  return <>{children}</>
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient())

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
