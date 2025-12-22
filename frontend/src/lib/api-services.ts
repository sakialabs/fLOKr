import { apiClient } from './api'

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
    const response = await apiClient.get('/hubs/hubs/')
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
  async getAll(params?: Record<string, unknown>): Promise<InventoryItem[]> {
    const response = await apiClient.get('/inventory/items/', { params })
    return response.data
  },

  async search(query: string, hubId?: string): Promise<InventoryItem[]> {
    const params: Record<string, string> = { q: query }
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

  async requestExtension(id: string): Promise<Reservation> {
    const response = await apiClient.post(`/reservations/${id}/request_extension/`)
    return response.data
  },
}

// Notification Types & Service
export interface Notification {
  id: string
  type: 'reservation' | 'reminder' | 'message' | 'community' | 'system' | 'incident'
  title: string
  body: string
  data: Record<string, unknown>
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

// Community Types & Service
export interface Badge {
  id: string
  name: string
  slug: string
  description: string
  icon: string
  color: string
  category: string
  criteria: Record<string, unknown>
  unlocks_feature?: string
  created_at: string
}

export interface UserBadge {
  id: string
  user: string
  badge: Badge
  awarded_at: string
  awarded_reason: string
  viewed_at?: string
}

export interface Feedback {
  id: string
  user: string
  item?: string
  reservation?: string
  type: 'positive' | 'negative' | 'incident'
  rating?: number
  comment: string
  status: 'pending' | 'reviewed' | 'resolved'
  created_at: string
}

export interface MentorshipConnection {
  id: string
  mentor: UserProfile
  mentee: UserProfile
  status: 'requested' | 'active' | 'completed' | 'declined'
  start_date?: string
  end_date?: string
  created_at: string
}

export interface Message {
  id: string
  connection: string
  sender: string
  content: string
  read: boolean
  created_at: string
}

export interface UserProfile {
  id: string
  full_name: string
  role: string
  bio?: string
  skills?: string[] | string
  languages_spoken?: string[] | string
  is_mentor: boolean
  badges_earned: UserBadge[]
  contribution_stats: {
    items_contributed: number
    successful_reservations: number
    active_mentorships: number
    positive_feedback_count: number
  }
  reputation_score: number
  member_since: string
  preferred_language: string
  profile_picture?: string
}

export const communityService = {
  // Badges
  async getBadges(): Promise<Badge[]> {
    const response = await apiClient.get('/community/badges/')
    return response.data
  },

  async getUserBadges(userId?: string): Promise<UserBadge[]> {
    const params = userId ? { user: userId } : {}
    const response = await apiClient.get('/community/user-badges/', { params })
    return response.data
  },

  async getRecentBadges(): Promise<UserBadge[]> {
    const response = await apiClient.get('/community/user-badges/', { 
      params: { recent: 'true' } 
    })
    return response.data
  },

  // Feedback
  async submitFeedback(data: Partial<Feedback>): Promise<Feedback> {
    const response = await apiClient.post('/community/feedback/', data)
    return response.data
  },

  async getFeedback(type?: string): Promise<Feedback[]> {
    const params = type ? { type } : {}
    const response = await apiClient.get('/community/feedback/', { params })
    return response.data
  },

  async getPositiveFeedback(): Promise<Feedback[]> {
    const response = await apiClient.get('/community/feedback/', {
      params: { positive_only: 'true' }
    })
    return response.data
  },

  // Mentorship
  async findMentors(languages?: string[], interests?: string[]): Promise<UserProfile[]> {
    const response = await apiClient.get('/community/mentorships/find_mentors/', {
      params: { languages, interests }
    })
    return response.data
  },

  async requestMentorship(mentorId: string): Promise<MentorshipConnection> {
    const response = await apiClient.post('/community/mentorships/request_mentor/', {
      mentor_id: mentorId
    })
    return response.data
  },

  async getMentorships(): Promise<MentorshipConnection[]> {
    const response = await apiClient.get('/community/mentorships/')
    return response.data
  },

  async acceptMentorship(id: string): Promise<MentorshipConnection> {
    const response = await apiClient.post(`/community/mentorships/${id}/accept/`)
    return response.data
  },

  async declineMentorship(id: string): Promise<MentorshipConnection> {
    const response = await apiClient.post(`/community/mentorships/${id}/decline/`)
    return response.data
  },

  // Messages
  async getMessages(connectionId: string): Promise<Message[]> {
    const response = await apiClient.get(`/community/mentorships/${connectionId}/messages/`)
    return response.data
  },

  async sendMessage(connectionId: string, content: string): Promise<Message> {
    const response = await apiClient.post(`/community/mentorships/${connectionId}/messages/`, {
      content
    })
    return response.data
  },

  // Leaderboard (dignity-first)
  async getLeaderboard(): Promise<Array<Record<string, unknown>>> {
    const response = await apiClient.get('/community/leaderboard/')
    return response.data
  },

  // User Profile
  async getUserProfile(userId: string): Promise<UserProfile> {
    const response = await apiClient.get(`/users/profile/${userId}/`)
    return response.data
  },

  async uploadProfilePicture(file: File): Promise<{ message: string; profile_picture_url: string }> {
    const formData = new FormData()
    formData.append('profile_picture', file)
    const response = await apiClient.post('/users/profile/picture/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async deleteProfilePicture(): Promise<{ message: string }> {
    const response = await apiClient.delete('/users/profile/picture/')
    return response.data
  },
}
