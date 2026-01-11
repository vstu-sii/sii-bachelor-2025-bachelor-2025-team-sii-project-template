'use client'

import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'

interface Dish {
  id: number
  user_id: number
  photo_url: string
  dish_type: string
  user_recipe_text: string
  status: 'draft' | 'processing' | 'ready'
  created_at: string
  updated_at?: string
  rating?: {
    appearance_score: number
    recipe_score: number
    appearance_feedback: string
    recipe_feedback: string
    recommendations: string
  }
}

interface Analysis {
  id: number
  dish_id: number
  appearance_score: number
  recipe_score: number
  appearance_feedback: string
  recipe_feedback: string
  recommendations: string
  created_at: string
}

interface AppContextType {
  dishes: Dish[]
  isLoading: boolean
  error: string | null
  fetchDishes: (params?: any) => Promise<void>
  fetchDish: (id: number) => Promise<Dish>
  createDish: (formData: FormData) => Promise<Dish>
  analyzeDish: (id: number) => Promise<Analysis>
  deleteDish: (id: number) => Promise<void>
  clearError: () => void
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export const useApp = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}

interface AppProviderProps {
  children: ReactNode
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [dishes, setDishes] = useState<Dish[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const clearError = () => setError(null)

  const fetchDishes = useCallback(async (params?: any) => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.getDishes(params)
      setDishes(response.data)
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dishes')
      toast.error(err.message || 'Не удалось загрузить блюда')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const fetchDish = useCallback(async (id: number): Promise<Dish> => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.getDish(id)
      return response.data
    } catch (err: any) {
      setError(err.message || `Failed to fetch dish ${id}`)
      toast.error(err.message || 'Не удалось загрузить блюдо')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const createDish = useCallback(async (formData: FormData): Promise<Dish> => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.createDish(formData)
      toast.success('Блюдо успешно создано!')
      return response.data
    } catch (err: any) {
      setError(err.message || 'Failed to create dish')
      toast.error(err.message || 'Не удалось создать блюдо')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const analyzeDish = useCallback(async (id: number): Promise<Analysis> => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.analyzeDish(id)
      toast.success('Анализ запущен! Результаты скоро будут готовы.')
      return response.data
    } catch (err: any) {
      setError(err.message || 'Failed to analyze dish')
      toast.error(err.message || 'Не удалось запустить анализ')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const deleteDish = useCallback(async (id: number) => {
    setIsLoading(true)
    setError(null)
    try {
      await api.deleteDish(id)
      setDishes(prev => prev.filter(dish => dish.id !== id))
      toast.success('Блюдо удалено')
    } catch (err: any) {
      setError(err.message || 'Failed to delete dish')
      toast.error(err.message || 'Не удалось удалить блюдо')
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const value: AppContextType = {
    dishes,
    isLoading,
    error,
    fetchDishes,
    fetchDish,
    createDish,
    analyzeDish,
    deleteDish,
    clearError,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}
