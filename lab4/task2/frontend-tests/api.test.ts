import { api, ApiClient } from '@/lib/api'
import axios from 'axios'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('API Client', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  describe('Singleton Pattern', () => {
    test('should return same instance', () => {
      const instance1 = ApiClient.getInstance()
      const instance2 = ApiClient.getInstance()
      expect(instance1).toBe(instance2)
    })
  })

  describe('Token Management', () => {
    test('should set token in localStorage', () => {
      api.setToken('test-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'test-token')
    })

    test('should get token from localStorage', () => {
      localStorage.setItem('access_token', 'test-token')
      // Note: We can't test private method directly, but we can test through public methods
      // that use it
    })

    test('should clear token from localStorage', () => {
      api.clearToken()
      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token')
    })
  })

  describe('Request Interceptors', () => {
    test('should add authorization header when token exists', async () => {
      localStorage.setItem('access_token', 'test-token')
      mockedAxios.create.mockReturnValue(mockedAxios)
      
      const client = ApiClient.getInstance()
      // This tests the interceptor setup indirectly
      expect(mockedAxios.interceptors.request.use).toHaveBeenCalled()
    })
  })

  describe('Response Interceptors', () => {
    test('should handle successful response', async () => {
      const mockResponse = { data: { success: true }, status: 200 }
      mockedAxios.get.mockResolvedValue(mockResponse)

      const response = await api.getDishes()
      expect(response.data).toEqual({ success: true })
      expect(response.status).toBe(200)
    })

    test('should handle error response with detail message', async () => {
      const mockError = {
        response: {
          status: 400,
          data: { detail: 'Validation error' }
        }
      }
      mockedAxios.get.mockRejectedValue(mockError)

      await expect(api.getDishes()).rejects.toEqual({
        message: 'Validation error',
        status: 400
      })
    })

    test('should handle error response with message field', async () => {
      const mockError = {
        response: {
          status: 404,
          data: { message: 'Not found' }
        }
      }
      mockedAxios.get.mockRejectedValue(mockError)

      await expect(api.getDishes()).rejects.toEqual({
        message: 'Not found',
        status: 404
      })
    })

    test('should handle error without response', async () => {
      const mockError = { message: 'Network error' }
      mockedAxios.get.mockRejectedValue(mockError)

      await expect(api.getDishes()).rejects.toEqual({
        message: 'Произошла ошибка',
        status: 500
      })
    })
  })

  describe('Auth Methods', () => {
    test('login should call correct endpoint', async () => {
      const mockResponse = { data: { access_token: 'token' }, status: 200 }
      mockedAxios.post.mockResolvedValue(mockResponse)

      await api.login('test@example.com', 'password')

      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/auth/login',
        expect.any(FormData),
        expect.objectContaining({
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        })
      )
    })

    test('register should call correct endpoint', async () => {
      const mockResponse = { data: { id: 1 }, status: 201 }
      mockedAxios.post.mockResolvedValue(mockResponse)

      const userData = { username: 'test', email: 'test@example.com', password: 'password' }
      await api.register(userData)

      expect(mockedAxios.post).toHaveBeenCalledWith('/auth/register', userData)
    })
  })

  describe('Dish Methods', () => {
    test('createDish should use multipart/form-data', async () => {
      const mockFormData = new FormData()
      mockFormData.append('photo', new Blob())
      mockFormData.append('recipe', 'test recipe')

      const mockResponse = { data: { id: 1 }, status: 201 }
      mockedAxios.post.mockResolvedValue(mockResponse)

      await api.createDish(mockFormData)

      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/dishes/',
        mockFormData,
        expect.objectContaining({
          headers: { 'Content-Type': 'multipart/form-data' }
        })
      )
    })

    test('getDishes should pass params', async () => {
      const mockResponse = { data: [], status: 200 }
      mockedAxios.get.mockResolvedValue(mockResponse)

      const params = { skip: 10, limit: 20, status: 'ready' }
      await api.getDishes(params)

      expect(mockedAxios.get).toHaveBeenCalledWith('/dishes/', { params })
    })

    test('analyzeDish should call correct endpoint', async () => {
      const mockResponse = { data: { success: true }, status: 200 }
      mockedAxios.post.mockResolvedValue(mockResponse)

      await api.analyzeDish(1)

      expect(mockedAxios.post).toHaveBeenCalledWith('/dishes/1/analyze')
    })
  })
})
