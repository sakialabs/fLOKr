/**
 * Navi services backed by the existing legacy AI API endpoints.
 * Intelligent AI-powered features for fLOKr.
 */
import axios from 'axios'
import { apiClient } from './api'

export interface TagSuggestion {
  tag: string
  confidence: number
}

export interface ImageTagResponse {
  tags: string[]
  category: string
  detailed_tags: TagSuggestion[]
  processing_time?: number
  message?: string
}

export interface RelatedFAQ {
  question: string
  answer: string
  category: string
  score: number
}

export interface QuestionResponse {
  answer: string
  confidence: number
  question_matched: string | null
  category: string | null
  related_faqs: RelatedFAQ[]
  response_time: number
  method: 'semantic' | 'keyword' | 'fallback'
}

export interface FAQEntry {
  id: string
  question: string
  answer: string
  category: string
  keywords?: string[]
  view_count?: number
  helpful_count?: number
}

const createNaviFallbackResponse = (answer: string): QuestionResponse => ({
  answer,
  confidence: 0,
  question_matched: null,
  category: null,
  related_faqs: [],
  response_time: 0,
  method: 'fallback',
})

const isTemporaryNaviFailure = (error: unknown) => {
  if (!axios.isAxiosError(error)) {
    return false
  }

  const status = error.response?.status

  return !error.response || (typeof status === 'number' && status >= 500)
}

const legacyGuideService = {
  /**
   * Get tag and category suggestions for an image
   * @param imageFile - Image file to analyze
   * @returns Tag and category suggestions
   */
  async suggestTagsFromFile(imageFile: File): Promise<ImageTagResponse> {
    const formData = new FormData()
    formData.append('image', imageFile)
    
    const response = await apiClient.post<ImageTagResponse>(
      '/inventory/items/suggest_tags/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    
    return response.data
  },

  /**
   * Get tag and category suggestions from an image URL
   * @param imageUrl - URL of the image to analyze
   * @returns Tag and category suggestions
   */
  async suggestTagsFromUrl(imageUrl: string): Promise<ImageTagResponse> {
    const response = await apiClient.post<ImageTagResponse>(
      '/ori/image-tag/',
      { image_url: imageUrl }
    )
    
    return response.data
  },

  /**
   * Analyze image and get detailed predictions
   * @param imageFile - Image file to analyze
   * @returns Detailed tag predictions with confidence scores
   */
  async analyzeImage(imageFile: File): Promise<ImageTagResponse> {
    const formData = new FormData()
    formData.append('image_file', imageFile)
    
    const response = await apiClient.post<ImageTagResponse>(
      '/ori/image-tag/',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    
    return response.data
  },

  /**
   * Ask Navi a natural language question
   * @param question - The question to ask
   * @param category - Optional category filter
   * @param limit - Maximum number of related FAQs to return
   * @returns Answer with confidence and related FAQs
   */
  async askQuestion(
    question: string,
    category?: string,
    limit: number = 3
  ): Promise<QuestionResponse> {
    try {
      const response = await apiClient.post<QuestionResponse>(
        '/ori/ask/',
        { question, category, limit },
        { skipAuthRedirect: true }
      )

      return response.data
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        return createNaviFallbackResponse(
          "I can answer live questions once you're signed in. For now, you can open the Loop, browse items, find hubs, or register to connect with local support."
        )
      }

      if (isTemporaryNaviFailure(error)) {
        return createNaviFallbackResponse(
          "I can't reach the live help service right now. You can still open the Loop, browse items, find hubs, or contact a Lead; try again in a moment."
        )
      }

      throw error
    }
  },

  /**
   * Get popular FAQ entries
   * @param limit - Maximum number of FAQs to return
   * @returns List of popular FAQs
   */
  async getPopularFAQs(limit: number = 10): Promise<FAQEntry[]> {
    const response = await apiClient.get<FAQEntry[]>(
      `/ori/faqs/popular/?limit=${limit}`
    )
    
    return response.data
  },

  /**
   * Get FAQs by category
   * @param category - Category to filter by
   * @param limit - Maximum number of FAQs to return
   * @returns List of FAQs in the category
   */
  async getFAQsByCategory(
    category: string,
    limit: number = 10
  ): Promise<FAQEntry[]> {
    const response = await apiClient.get<FAQEntry[]>(
      `/ori/faqs/category/?category=${category}&limit=${limit}`
    )
    
    return response.data
  },
}

export const naviAIService = legacyGuideService
