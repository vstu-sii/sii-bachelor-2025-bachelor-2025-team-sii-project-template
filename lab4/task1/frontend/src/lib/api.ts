import axios, { AxiosInstance, AxiosError, AxiosResponse } from 'axios'

export interface ApiResponse<T = any> {
  data: T
  message?: string
  status: number
}

export interface ApiError {
  message: string
  status: number
  errors?: Record<string, string[]>
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

class ApiClient {
  private client: AxiosInstance
  private static instance: ApiClient

  private constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient()
    }
    return ApiClient.instance
  }

  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        const apiError: ApiError = {
          message: 'Произошла ошибка',
          status: error.response?.status || 500,
        }

        if (error.response?.data) {
          const data = error.response.data as any
          apiError.message = data.detail || data.message || apiError.message
          apiError.errors = data.errors
        }

        return Promise.reject(apiError)
      }
    )
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('access_token')
  }

  public setToken(token: string): void {
    localStorage.setItem('access_token', token)
  }

  public clearToken(): void {
    localStorage.removeItem('access_token')
  }

  // Auth methods
  async login(email: string, password: string): Promise<ApiResponse<{ access_token: string }>> {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    
    if (response.data.access_token) {
      this.setToken(response.data.access_token)
    }
    
    return {
      data: response.data,
      status: response.status,
    }
  }

  async register(userData: { username: string; email: string; password: string }): Promise<ApiResponse> {
    const response = await this.client.post('/auth/register', userData)
    return {
      data: response.data,
      status: response.status,
    }
  }

  async getCurrentUser(): Promise<ApiResponse> {
    const response = await this.client.get('/auth/me')
    return {
      data: response.data,
      status: response.status,
    }
  }

  // Dishes methods
  async createDish(formData: FormData): Promise<ApiResponse> {
    const response = await this.client.post('/dishes/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return {
      data: response.data,
      status: response.status,
    }
  }

  async getDishes(params?: {
    skip?: number
    limit?: number
    status?: string
  }): Promise<ApiResponse> {
    const response = await this.client.get('/dishes/', { params })
    return {
      data: response.data,
      status: response.status,
    }
  }

  async getDish(id: number): Promise<ApiResponse> {
    const response = await this.client.get(`/dishes/${id}`)
    return {
      data: response.data,
      status: response.status,
    }
  }

  async analyzeDish(id: number): Promise<ApiResponse> {
    const response = await this.client.post(`/dishes/${id}/analyze`)
    return {
      data: response.data,
      status: response.status,
    }
  }

  async getDishAnalysis(id: number): Promise<ApiResponse> {
    const response = await this.client.get(`/dishes/${id}/analysis`)
    return {
      data: response.data,
      status: response.status,
    }
  }

  async deleteDish(id: number): Promise<ApiResponse> {
    const response = await this.client.delete(`/dishes/${id}`)
    return {
      data: response.data,
      status: response.status,
    }
  }

  // Statistics methods
  async getStatisticsOverview(): Promise<ApiResponse> {
    const response = await this.client.get('/statistics/overview')
    return {
      data: response.data,
      status: response.status,
    }
  }

  async getDishTypeStatistics(dishType: string): Promise<ApiResponse> {
    const response = await this.client.get(`/statistics/dish-types/${dishType}`)
    return {
      data: response.data,
      status: response.status,
    }
  }

  async getProgressTimeline(days: number = 30): Promise<ApiResponse> {
    const response = await this.client.get('/statistics/progress', { params: { days } })
    return {
      data: response.data,
      status: response.status,
    }
  }
}

export const api = ApiClient.getInstance()
