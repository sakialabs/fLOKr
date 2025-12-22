import { apiClient } from './api'

export interface RegisterData {
  email: string
  password: string
  password_confirm: string
  first_name: string
  last_name: string
  phone?: string
  role?: 'newcomer' | 'community_member' | 'steward' | 'admin' | 'partner'
  preferred_language?: string
  address?: string
  arrival_date?: string
}

export interface LoginData {
  email: string
  password: string
}

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  phone: string
  role: string
  preferred_language: string
  address: string
  location: any
  assigned_hub: string | null
  arrival_date: string | null
  preferences: Record<string, unknown>
  reputation_score: number
  is_mentor: boolean
  late_return_count: number
  borrowing_restricted_until: string | null
  created_at: string
  profile_picture?: string
  avatar_choice?: string
}

export interface AuthResponse {
  message: string
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

export const authService = {
  async register(data: RegisterData): Promise<AuthResponse> {
    try {
      console.log('📤 Registration request:', JSON.stringify(data, null, 2))
      const response = await apiClient.post('/auth/register/', data)
      console.log('✅ Registration success:', response.data)
      return response.data
    } catch (error) {
      const err = error as { response?: { status?: number; statusText?: string; data?: unknown; headers?: unknown }; message?: string }
      console.error('❌ Registration failed:', {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        headers: err.response?.headers,
        message: err.message
      })
      throw error
    }
  },

  async login(data: LoginData): Promise<AuthResponse> {
    const response = await apiClient.post('/auth/login/', data)
    return response.data
  },

  async logout(refreshToken: string): Promise<void> {
    await apiClient.post('/auth/logout/', { refresh: refreshToken })
  },

  async getProfile(): Promise<User> {
    const response = await apiClient.get('/auth/profile/')
    return response.data
  },

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await apiClient.put('/auth/profile/', data)
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<{ access: string }> {
    const response = await apiClient.post('/auth/token/refresh/', {
      refresh: refreshToken,
    })
    return response.data
  },

  async requestPasswordReset(email: string): Promise<void> {
    await apiClient.post('/auth/password-reset/request/', { email })
  },

  async confirmPasswordReset(
    uid: string,
    token: string,
    password: string,
    password_confirm: string
  ): Promise<void> {
    await apiClient.post('/auth/password-reset/confirm/', {
      uid,
      token,
      password,
      password_confirm,
    })
  },

  async saveOnboardingPreferences(preferences: OnboardingPreferences): Promise<User> {
    const response = await apiClient.post('/auth/onboarding/', preferences)
    return response.data.user
  },

  async getOnboardingPreferences(): Promise<OnboardingPreferences> {
    const response = await apiClient.get('/auth/onboarding/')
    return response.data
  },
}

export interface OnboardingPreferences {
  clothing_sizes?: {
    shirt?: string
    pants?: string
    shoes?: string
  }
  dietary_restrictions?: string[]
  skill_interests?: string[]
  preferred_language?: string
  languages_spoken?: string[]
  address?: string
  phone?: string
  address_country?: string
  address_province?: string
  address_street?: string
  address_city?: string
  address_postal_code?: string
  arrival_date?: string
  immediate_needs?: string[]
  interests?: string[]
  seeking_mentor?: boolean
  mentor_preferences?: Record<string, unknown>
}

// Token management helpers
export const tokenManager = {
  getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  },

  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('refresh_token')
  },

  setTokens(access: string, refresh: string): void {
    if (typeof window === 'undefined') return
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  },

  clearTokens(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}
