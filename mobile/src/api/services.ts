import apiClient from './client'

// Auth Types & Service
export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: 'newcomer' | 'community_member' | 'steward' | 'admin' | 'partner'
  phone?: string
  preferred_language: string
  is_mentor: boolean
  reputation_score: number
}

export interface LoginResponse {
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/login/', { email, password })
    return response.data
  },

  async register(data: {
    email: string
    password: string
    password_confirm: string
    first_name: string
    last_name: string
    role?: string
  }): Promise<LoginResponse> {
    const response = await apiClient.post('/auth/register/', data)
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
}


// Hub Types & Service
export interface Hub {
  id: string
  name: string
  address: string
  location: any
  operating_hours: Record<string, any>
  status: string
  current_inventory_count: number
  capacity: number
  distance?: number
}

export const hubService = {
  async getAll(): Promise<Hub[]> {
    const response = await apiClient.get('/hubs/')
    return response.data
  },

  async getNearby(lat: number, lng: number): Promise<Hub[]> {
    const response = await apiClient.get(`/hubs/nearby/?lat=${lat}&lng=${lng}`)
    return response.data
  },

  async getById(id: string): Promise<Hub> {
    const response = await apiClient.get(`/hubs/${id}/`)
    return response.data
  },
}

// Inventory Types & Service
export interface InventoryItem {
  id: string
  name: string
  description: string
  category: string
  condition: string
  quantity_available: number
  quantity_total: number
  images: string[]
  hub_name?: string
  status: string
  created_at: string
}

export const inventoryService = {
  async getAll(params?: Record<string, any>): Promise<InventoryItem[]> {
    const response = await apiClient.get('/inventory/items/', { params })
    return response.data
  },

  async search(query: string, hubId?: string): Promise<InventoryItem[]> {
    const params: Record<string, any> = { q: query }
    if (hubId) params.hub_id = hubId
    const response = await apiClient.get('/inventory/items/search/', { params })
    return response.data
  },

  async getById(id: string): Promise<InventoryItem> {
    const response = await apiClient.get(`/inventory/items/${id}/`)
    return response.data
  },

  async create(data: Partial<InventoryItem>): Promise<InventoryItem> {
    const response = await apiClient.post('/inventory/items/', data)
    return response.data
  },
}


// Reservation Types & Service
export interface Reservation {
  id: string
  item_name: string
  hub_name: string
  quantity: number
  status: string
  pickup_date: string
  expected_return_date: string
  actual_return_date?: string
  extension_requested: boolean
  extension_approved: boolean
  created_at: string
}

export const reservationService = {
  async getAll(): Promise<Reservation[]> {
    const response = await apiClient.get('/reservations/')
    return response.data
  },

  async create(data: {
    item: string
    hub: string
    quantity: number
    pickup_date: string
    expected_return_date: string
  }): Promise<Reservation> {
    const response = await apiClient.post('/reservations/', data)
    return response.data
  },

  async cancel(id: string): Promise<Reservation> {
    const response = await apiClient.post(`/reservations/${id}/cancel/`)
    return response.data
  },

  async pickup(id: string): Promise<Reservation> {
    const response = await apiClient.post(`/reservations/${id}/pickup/`)
    return response.data
  },

  async return(id: string): Promise<Reservation> {
    const response = await apiClient.post(`/reservations/${id}/return/`)
    return response.data
  },

  async requestExtension(id: string): Promise<Reservation> {
    const response = await apiClient.post(`/reservations/${id}/request_extension/`)
    return response.data
  },

  async approveExtension(id: string, newDate: string): Promise<Reservation> {
    const response = await apiClient.post(`/reservations/${id}/approve_extension/`, {
      new_return_date: newDate,
    })
    return response.data
  },
}


// Notification Types & Service
export interface Notification {
  id: string
  type: 'reservation' | 'reminder' | 'message' | 'community' | 'system' | 'incident'
  title: string
  body: string
  data: Record<string, any>
  read: boolean
  read_at?: string
  push_sent: boolean
  created_at: string
}

export interface NotificationPreference {
  push_enabled: boolean
  push_reservations: boolean
  push_reminders: boolean
  push_messages: boolean
  push_community: boolean
  quiet_hours_enabled: boolean
  quiet_hours_start?: string
  quiet_hours_end?: string
}

export interface DeviceToken {
  id: string
  token: string
  platform: 'ios' | 'android' | 'web'
  device_name: string
  is_active: boolean
  created_at: string
}

export const notificationService = {
  async getAll(): Promise<Notification[]> {
    const response = await apiClient.get('/users/notifications/')
    return response.data
  },

  async getUnread(): Promise<Notification[]> {
    const response = await apiClient.get('/users/notifications/unread/')
    return response.data
  },

  async getUnreadCount(): Promise<number> {
    const response = await apiClient.get('/users/notifications/unread_count/')
    return response.data.count
  },

  async markAsRead(id: string): Promise<void> {
    await apiClient.post(`/users/notifications/${id}/mark_read/`)
  },

  async markAllAsRead(): Promise<void> {
    await apiClient.post('/users/notifications/mark_all_read/')
  },

  async getPreferences(): Promise<NotificationPreference> {
    const response = await apiClient.get('/users/notification-preferences/')
    return response.data
  },

  async updatePreferences(data: Partial<NotificationPreference>): Promise<NotificationPreference> {
    const response = await apiClient.post('/users/notification-preferences/', data)
    return response.data
  },

  async registerDevice(data: {
    token: string
    platform: 'ios' | 'android' | 'web'
    device_name?: string
  }): Promise<DeviceToken> {
    const response = await apiClient.post('/users/devices/', data)
    return response.data
  },

  async unregisterDevice(token: string): Promise<void> {
    await apiClient.post('/users/devices/unregister/', { token })
  },

  async getDevices(): Promise<DeviceToken[]> {
    const response = await apiClient.get('/users/devices/')
    return response.data
  },
}
