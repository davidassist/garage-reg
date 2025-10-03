/**
 * API Service - Handles communication with the backend server
 * RESTful API client with authentication and error handling
 */

import {
  User,
  Gate,
  Inspection,
  ChecklistTemplate,
  InspectionPhoto,
  APIError,
  AuthToken
} from '../types'

export interface LoginCredentials {
  username: string
  password: string
}

export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export class APIService {
  private baseURL: string
  private authToken?: string

  constructor(baseURL = 'http://localhost:8000/api') {
    this.baseURL = baseURL
  }

  /**
   * Set authentication token
   */
  public setAuthToken(token: string): void {
    this.authToken = token
  }

  /**
   * Get authentication headers
   */
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    }

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`
    }

    return headers
  }

  /**
   * Make authenticated API request
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<APIResponse<T>> {
    try {
      const url = `${this.baseURL}${endpoint}`
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getAuthHeaders(),
          ...options.headers,
        },
      })

      const data = await response.json()

      if (!response.ok) {
        throw new APIError(
          data.message || `HTTP ${response.status}`,
          response.status,
          data
        )
      }

      return {
        success: true,
        data: data.data || data,
        message: data.message
      }
    } catch (error) {
      if (error instanceof APIError) {
        throw error
      }
      
      throw new APIError(
        error instanceof Error ? error.message : 'Network request failed',
        0
      )
    }
  }

  /**
   * User authentication
   */
  public async login(credentials: LoginCredentials): Promise<{
    user: User
    token: AuthToken
  }> {
    const response = await this.request<{
      user: User
      token: AuthToken
    }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    })

    if (!response.data) {
      throw new APIError('Login failed: No data received', 401)
    }

    // Store token for future requests
    this.setAuthToken(response.data.token.accessToken)

    return response.data
  }

  /**
   * Refresh authentication token
   */
  public async refreshToken(refreshToken: string): Promise<AuthToken> {
    const response = await this.request<AuthToken>('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refreshToken }),
    })

    if (!response.data) {
      throw new APIError('Token refresh failed', 401)
    }

    this.setAuthToken(response.data.accessToken)
    return response.data
  }

  /**
   * User logout
   */
  public async logout(): Promise<void> {
    await this.request('/auth/logout', {
      method: 'POST',
    })
    
    this.authToken = undefined
  }

  /**
   * Get user profile
   */
  public async getUserProfile(): Promise<User> {
    const response = await this.request<User>('/auth/me')
    
    if (!response.data) {
      throw new APIError('Failed to get user profile', 500)
    }

    return response.data
  }

  /**
   * Get gates list
   */
  public async getGates(): Promise<Gate[]> {
    const response = await this.request<Gate[]>('/gates')
    return response.data || []
  }

  /**
   * Get gate by ID
   */
  public async getGate(id: string): Promise<Gate> {
    const response = await this.request<Gate>(`/gates/${id}`)
    
    if (!response.data) {
      throw new APIError('Gate not found', 404)
    }

    return response.data
  }

  /**
   * Get gate by QR code
   */
  public async getGateByQR(qrCode: string): Promise<Gate> {
    const response = await this.request<Gate>(`/gates/qr/${encodeURIComponent(qrCode)}`)
    
    if (!response.data) {
      throw new APIError('Gate not found', 404)
    }

    return response.data
  }

  /**
   * Get inspection templates
   */
  public async getInspectionTemplates(): Promise<ChecklistTemplate[]> {
    const response = await this.request<ChecklistTemplate[]>('/templates/checklists')
    return response.data || []
  }

  /**
   * Get template by ID
   */
  public async getTemplate(id: string): Promise<ChecklistTemplate> {
    const response = await this.request<ChecklistTemplate>(`/templates/checklists/${id}`)
    
    if (!response.data) {
      throw new APIError('Template not found', 404)
    }

    return response.data
  }

  /**
   * Get inspections
   */
  public async getInspections(params?: {
    gateId?: string
    status?: string
    startDate?: string
    endDate?: string
  }): Promise<Inspection[]> {
    let endpoint = '/inspections'
    
    if (params) {
      const query = new URLSearchParams()
      if (params.gateId) query.append('gateId', params.gateId)
      if (params.status) query.append('status', params.status)
      if (params.startDate) query.append('startDate', params.startDate)
      if (params.endDate) query.append('endDate', params.endDate)
      
      const queryString = query.toString()
      if (queryString) {
        endpoint += `?${queryString}`
      }
    }

    const response = await this.request<Inspection[]>(endpoint)
    return response.data || []
  }

  /**
   * Get inspection by ID
   */
  public async getInspection(id: string): Promise<Inspection> {
    const response = await this.request<Inspection>(`/inspections/${id}`)
    
    if (!response.data) {
      throw new APIError('Inspection not found', 404)
    }

    return response.data
  }

  /**
   * Create new inspection
   */
  public async createInspection(inspection: Omit<Inspection, 'id' | 'createdAt'>): Promise<Inspection> {
    const response = await this.request<Inspection>('/inspections', {
      method: 'POST',
      body: JSON.stringify(inspection),
    })

    if (!response.data) {
      throw new APIError('Failed to create inspection', 500)
    }

    return response.data
  }

  /**
   * Update existing inspection
   */
  public async updateInspection(id: string, updates: Partial<Inspection>): Promise<Inspection> {
    const response = await this.request<Inspection>(`/inspections/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    })

    if (!response.data) {
      throw new APIError('Failed to update inspection', 500)
    }

    return response.data
  }

  /**
   * Create or update inspection (for sync)
   */
  public async createOrUpdateInspection(inspection: Inspection): Promise<Inspection> {
    try {
      // Try to update first
      return await this.updateInspection(inspection.id, inspection)
    } catch (error) {
      if (error instanceof APIError && (error as APIError).statusCode === 404) {
        // If not found, create new
        return await this.createInspection(inspection)
      }
      throw error
    }
  }

  /**
   * Delete inspection
   */
  public async deleteInspection(id: string): Promise<void> {
    await this.request(`/inspections/${id}`, {
      method: 'DELETE',
    })
  }

  /**
   * Upload inspection photo
   */
  public async uploadPhoto(photo: InspectionPhoto, file: Blob): Promise<InspectionPhoto> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('inspectionId', photo.inspectionId)
    formData.append('checklistItemId', photo.checklistItemId || '')
    formData.append('description', photo.description || '')

    const response = await fetch(`${this.baseURL}/photos`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.authToken}`,
      },
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new APIError(
        errorData.message || 'Photo upload failed',
        response.status,
        errorData
      )
    }

    const data = await response.json()
    return data.data || data
  }

  /**
   * Get inspection photos
   */
  public async getInspectionPhotos(inspectionId: string): Promise<InspectionPhoto[]> {
    const response = await this.request<InspectionPhoto[]>(`/inspections/${inspectionId}/photos`)
    return response.data || []
  }

  /**
   * Delete photo
   */
  public async deletePhoto(photoId: string): Promise<void> {
    await this.request(`/photos/${photoId}`, {
      method: 'DELETE',
    })
  }

  /**
   * Check server connectivity
   */
  public async ping(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        timeout: 5000,
      } as RequestInit)
      
      return response.ok
    } catch {
      return false
    }
  }

  /**
   * Get server status
   */
  public async getServerStatus(): Promise<{
    status: string
    version: string
    timestamp: string
  }> {
    const response = await this.request<{
      status: string
      version: string
      timestamp: string
    }>('/health')

    return response.data || {
      status: 'unknown',
      version: '0.0.0',
      timestamp: new Date().toISOString()
    }
  }

  /**
   * Push delta batch to server
   */
  public async pushDeltaBatch(batch: {
    batchId: string
    operations: any[]
    lastSyncToken?: string
  }): Promise<any> {
    const response = await this.request('/sync/push', {
      method: 'POST',
      body: JSON.stringify(batch)
    })

    return response.data
  }

  /**
   * Pull delta batch from server
   */
  public async pullDeltaBatch(request: {
    batchId: string
    lastSyncToken?: string
    batchSize: number
  }): Promise<any> {
    const response = await this.request('/sync/pull', {
      method: 'POST',
      body: JSON.stringify(request)
    })

    return response.data
  }

  /**
   * Get sync token for incremental sync
   */
  public async getSyncToken(): Promise<string> {
    const response = await this.request<{ token: string }>('/sync/token')
    return response.data?.token || ''
  }

  /**
   * Resolve conflict on server
   */
  public async resolveConflict(conflictId: string, resolution: any): Promise<any> {
    const response = await this.request(`/sync/conflicts/${conflictId}/resolve`, {
      method: 'POST',
      body: JSON.stringify(resolution)
    })

    return response.data
  }
}