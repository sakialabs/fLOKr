import axios from 'axios'

declare module 'axios' {
  interface AxiosRequestConfig {
    _retry?: boolean
    skipAuthRedirect?: boolean
  }
}

export const normalizeApiBaseUrl = (url: string) => {
  const trimmedUrl = url.trim().replace(/\/+$/, '')

  if (!trimmedUrl) {
    return '/api'
  }

  return trimmedUrl.endsWith('/api') ? trimmedUrl : `${trimmedUrl}/api`
}

export const API_BASE_URL = normalizeApiBaseUrl(
  process.env.NEXT_PUBLIC_API_URL || '/api'
)

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Export as 'api' for convenience
export const api = apiClient

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // If 401 and we haven't retried yet, try to refresh token
    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.skipAuthRedirect
    ) {
      originalRequest._retry = true

      if (typeof window !== 'undefined') {
        const refreshToken = localStorage.getItem('refresh_token')
        
        if (refreshToken) {
          try {
            const response = await apiClient.post('/auth/token/refresh/', {
              refresh: refreshToken,
            })
            const { access } = response.data
            localStorage.setItem('access_token', access)
            originalRequest.headers.Authorization = `Bearer ${access}`
            return apiClient(originalRequest)
          } catch (refreshError) {
            // Refresh failed, clear tokens and redirect to login
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        } else {
          // No refresh token, redirect to login
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)
