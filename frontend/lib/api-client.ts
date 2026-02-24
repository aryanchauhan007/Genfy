// lib/api-client.ts
// API Client for Backend Integration
// Handles all communication with FastAPI backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

// ============================================================================
// Types matching backend models
// ============================================================================

export interface Session {
  session_id: string
  current_step: string
  user_idea: string
  selected_category: string | null
  selected_llm: string
  answers_json: Record<string, any>
  messages: ChatMessage[]
  conversation_step: number
  selected_chips: string[]
  created_at: string
  final_prompt?: string
  // Visual Settings
  selected_aspect_ratio?: string
  selected_color_palette?: string
  selected_camera_settings?: string
  selected_image_purpose?: string
}

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  timestamp: string
}

export interface Category {
  name: string
  key: string
  emoji: string
  description: string
  image_path: string
  color: string
  question_count: number
}

export interface VisualSettings {
  color_palette?: string
  aspect_ratio?: string
  camera_settings?: string
  image_purpose?: string
}

export interface PromptHistory {
  id: number
  timestamp: string
  category: string
  user_idea: string
  llm_used: string
  final_prompt: string
  generated_image_url?: string
}

export interface User {
  id: string
  email: string
}

// ============================================================================
// API Client Class
// ============================================================================

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  /**
   * Get user_id from localStorage
   */
  private getUserId(): string | null {
    if (typeof window === 'undefined') return null

    const userStr = localStorage.getItem('user')
    if (!userStr) return null

    try {
      const user = JSON.parse(userStr)
      return user.id
    } catch {
      return null
    }
  }

  /**
   * Make authenticated HTTP request
   */
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const userId = this.getUserId()

    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...options?.headers as Record<string, string>,
      }

      // ✅ Add Authorization header if user is logged in
      if (userId) {
        headers["Authorization"] = `Bearer ${userId}`
      }

      const response = await fetch(url, {
        ...options,
        headers,
      })

      // ✅ Handle authentication errors
      if (response.status === 401) {
        console.warn("❌ Unauthorized - redirecting to login")
        if (typeof window !== 'undefined') {
          localStorage.removeItem('user')
          localStorage.removeItem('session_id')
          window.location.href = '/login'
        }
        throw new Error("Unauthorized")
      }

      if (response.status === 403) {
        console.warn("❌ Access denied")
        throw new Error("Access denied: You don't have permission to access this resource")
      }

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Unknown error" }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return response.json()
    } catch (error) {
      // Silently log API errors instead of throwing
      console.warn(`⚠️ API request failed for ${endpoint}:`, error instanceof Error ? error.message : error)
      throw error
    }
  }

  // ============================================================================
  // Auth Management
  // ============================================================================

  async signup(email: string, password: string): Promise<{ id: string; email: string }> {
    return this.request("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
  }

  async login(email: string, password: string): Promise<{ user: { id: string; email: string }; session: any }> {
    return this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
  }

  async logout(): Promise<{ success: boolean }> {
    return this.request("/api/auth/logout", {
      method: "POST",
    })
  }

  // ============================================================================
  // Session Management
  // ============================================================================

  async createSession(llmProvider: string = "Claude", userId?: string): Promise<{ session_id: string; llm_provider: string }> {
    return this.request("/api/session/create", {
      method: "POST",
      body: JSON.stringify({ llm_provider: llmProvider, user_id: userId }),
    })
  }

  async getSession(sessionId: string): Promise<Session> {
    return this.request(`/api/session/${sessionId}`)
  }

  async deleteSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/api/session/${sessionId}`, {
      method: "DELETE",
    })
  }

  async setLLM(sessionId: string, llmProvider: string): Promise<{ success: boolean; llm_provider: string }> {
    return this.request(`/api/session/${sessionId}/llm`, {
      method: "POST",
      body: JSON.stringify({ llm_provider: llmProvider }),
    })
  }

  // ============================================================================
  // LLM Management
  // ============================================================================

  async getAvailableLLMs(): Promise<{ llms: string[] }> {
    return this.request("/api/llms/available")
  }

  // ============================================================================
  // Category Management
  // ============================================================================

  async getCategories(): Promise<{ categories: Category[] }> {
    return this.request("/api/categories")
  }

  async selectCategory(
    sessionId: string,
    category: string,
    userIdea: string
  ): Promise<{ success: boolean; category: string; questions: string[] }> {
    return this.request(`/api/categories/select/${sessionId}`, {
      method: "POST",
      body: JSON.stringify({ category, user_idea: userIdea }),
    })
  }

  // ============================================================================
  // Visual Settings
  // ============================================================================

  async getVisualSettingsOptions(): Promise<{
    color_palettes: string[]
    aspect_ratios: string[]
    camera_settings: string[]
    image_purposes: string[]
  }> {
    return this.request("/api/visual-settings/options")
  }

  async saveVisualSettings(
    sessionId: string,
    settings: VisualSettings
  ): Promise<{ success: boolean; settings: VisualSettings }> {
    return this.request(`/api/visual-settings/save/${sessionId}`, {
      method: "POST",
      body: JSON.stringify(settings),
    })
  }

  async generateQuickPrompt(sessionId: string): Promise<{
    success: boolean
    final_prompt: string
    timestamp: string
  }> {
    return this.request(`/api/visual-settings/generate-quick/${sessionId}`, {
      method: "POST",
    })
  }

  // ============================================================================
  // Chat Management
  // ============================================================================

  async startChat(
    sessionId: string,
    category: string,
    userIdea: string,
    visualSettings?: VisualSettings
  ): Promise<{
    success: boolean
    messages: ChatMessage[]
    first_question: string
  }> {
    return this.request(`/api/chat/start/${sessionId}`, {
      method: "POST",
      body: JSON.stringify({
        category,
        user_idea: userIdea,
        visual_settings: visualSettings,
      }),
    })
  }

  async getChatMessages(sessionId: string): Promise<{ messages: ChatMessage[] }> {
    return this.request(`/api/chat/messages/${sessionId}`)
  }

  async getCurrentQuestion(sessionId: string): Promise<{
    question: string | null
    is_complete: boolean
    conversation_step: number
  }> {
    return this.request(`/api/chat/current-question/${sessionId}`)
  }

  // ============================================================================
  // Suggestions
  // ============================================================================

  async getSuggestions(sessionId: string, refresh: number = 0): Promise<{ suggestions: string[] }> {
    return this.request(`/api/suggestions/${sessionId}?refresh=${refresh}`)
  }

  async toggleSuggestion(
    sessionId: string,
    suggestion: string,
    action: "toggle" | "add" | "remove" = "toggle"
  ): Promise<{ success: boolean; selected_suggestions: string[] }> {
    return this.request(`/api/suggestions/toggle/${sessionId}`, {
      method: "POST",
      body: JSON.stringify({ suggestion, action }),
    })
  }

  async getSelectedSuggestions(sessionId: string): Promise<{ selected: string[] }> {
    return this.request(`/api/suggestions/selected/${sessionId}`)
  }

  async clearSuggestions(sessionId: string): Promise<{ success: boolean }> {
    return this.request(`/api/suggestions/clear/${sessionId}`, {
      method: "DELETE",
    })
  }

  // ============================================================================
  // Answer Submission
  // ============================================================================

  async submitAnswer(sessionId: string, answer: string): Promise<{
    success: boolean
    next_question?: string
    should_generate_prompt?: boolean
    final_prompt?: string
  }> {
    return this.request(`/api/answer/submit/${sessionId}`, {
      method: "POST",
      body: JSON.stringify({ answer }),
    })
  }

  async skipToGeneration(sessionId: string): Promise<{
    success: boolean
    next_question?: string
    should_generate_prompt?: boolean
    final_prompt?: string
  }> {
    return this.request(`/api/chat/skip/${sessionId}`, {
      method: "POST",
    })
  }

  // ============================================================================
  // Prompt Management
  // ============================================================================

  async getFinalPrompt(sessionId: string): Promise<{
    success: boolean
    final_prompt: string
    user_idea: string
    category: string
    answers: Record<string, any>
    visual_settings: VisualSettings
  }> {
    return this.request(`/api/prompt/final/${sessionId}`)
  }

  async refinePrompt(sessionId: string, refinementInstruction: string): Promise<{
    success: boolean
    refined_prompt: string
  }> {
    return this.request(`/api/prompt/refine/${sessionId}`, {
      method: "POST",
      body: JSON.stringify({ refinement_instruction: refinementInstruction }),
    })
  }

  // ============================================================================
  // History Management
  // ============================================================================

  async getHistory(limit: number = 50, userId?: string): Promise<{
    success: boolean
    history: PromptHistory[]
  }> {
    const query = new URLSearchParams({ limit: limit.toString() });
    if (userId) query.append("user_id", userId);
    return this.request(`/api/sessions/history?${query.toString()}`)
  }

  async getHistoryItem(promptId: number): Promise<{
    success: boolean
    details: PromptHistory
    answers_json: Record<string, any>
    visual_settings: VisualSettings
  }> {
    return this.request(`/api/history/${promptId}`)
  }

  async deleteHistoryItem(promptId: number): Promise<{
    success: boolean
    message: string
  }> {
    return this.request(`/api/history/${promptId}`, {
      method: "DELETE",
    })
  }

  async clearHistory(): Promise<{
    success: boolean
    message: string
  }> {
    return this.request("/api/history", {
      method: "DELETE",
    })
  }

  // ============================================================================
  // File Uploads
  // ============================================================================

  async uploadFile(sessionId: string, file: File): Promise<{
    success: boolean
    url: string
    filename: string
    vision_analysis?: string
    analyzed_by?: string
  }> {
    const formData = new FormData()
    formData.append("file", file)

    // We use fetch directly here because request() might set Content-Type to json
    // and we need browser to set multipart/form-data boundary
    const url = `${this.baseUrl}/api/session/${sessionId}/upload`

    try {
      const response = await fetch(url, {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Unknown upload error" }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return response.json()
    } catch (error) {
      console.warn(`⚠️ Upload failed:`, error instanceof Error ? error.message : error)
      throw error
    }
  }

  async deleteSessionFile(sessionId: string, fileIndex: number): Promise<{
    success: boolean
    message: string
  }> {
    return this.request(`/api/session/${sessionId}/files/${fileIndex}`, {
      method: "DELETE",
    })
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const apiClient = new ApiClient()
export default apiClient
