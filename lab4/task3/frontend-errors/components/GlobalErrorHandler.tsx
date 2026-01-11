'use client'

import { useEffect } from 'react'
import toast from 'react-hot-toast'

interface GlobalErrorHandlerProps {
  children: React.ReactNode
}

export function GlobalErrorHandler({ children }: GlobalErrorHandlerProps) {
  useEffect(() => {
    const handleGlobalError = (event: ErrorEvent) => {
      console.error('Global error caught:', event.error)
      
      // Игнорируем некоторые ошибки
      if (shouldIgnoreError(event.error)) {
        return
      }
      
      // Показываем пользователю понятное сообщение
      toast.error(
        'Произошла ошибка в приложении. Пожалуйста, обновите страницу.',
        {
          duration: 5000,
          id: 'global-error',
        }
      )
      
      // Логируем ошибку
      logErrorToService(event.error)
    }

    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      console.error('Unhandled promise rejection:', event.reason)
      
      toast.error(
        'Не удалось выполнить операцию. Попробуйте ещё раз.',
        {
          duration: 4000,
          id: 'promise-error',
        }
      )
      
      logErrorToService(event.reason)
    }

    const handleOffline = () => {
      toast.error(
        'Отсутствует подключение к интернету. Проверьте соединение.',
        {
          duration: 6000,
          icon: '��',
          id: 'offline-error',
        }
      )
    }

    const handleOnline = () => {
      toast.success(
        'Подключение восстановлено',
        {
          duration: 3000,
          icon: '✅',
          id: 'online-success',
        }
      )
    }

    // Подписываемся на события
    window.addEventListener('error', handleGlobalError)
    window.addEventListener('unhandledrejection', handleUnhandledRejection)
    window.addEventListener('offline', handleOffline)
    window.addEventListener('online', handleOnline)

    return () => {
      window.removeEventListener('error', handleGlobalError)
      window.removeEventListener('unhandledrejection', handleUnhandledRejection)
      window.removeEventListener('offline', handleOffline)
      window.removeEventListener('online', handleOnline)
    }
  }, [])

  return <>{children}</>
}

function shouldIgnoreError(error: any): boolean {
  // Игнорируем ошибки из сторонних скриптов
  if (error?.message?.includes('Script error')) {
    return true
  }
  
  // Игнорируем ошибки отключения сети (их обрабатываем отдельно)
  if (error?.message?.includes('NetworkError') || error?.message?.includes('Failed to fetch')) {
    return false // Не игнорируем, обрабатываем отдельно
  }
  
  // Игнорируем некоторые специфические ошибки
  const ignoredPatterns = [
    'ResizeObserver',
    'webkitExitFullScreen',
    'cancelFullScreen',
    'requestFullscreen',
  ]
  
  return ignoredPatterns.some(pattern => 
    error?.message?.includes(pattern) || 
    error?.name?.includes(pattern)
  )
}

function logErrorToService(error: any): void {
  const errorData = {
    type: 'global_error',
    message: error?.message || 'Unknown error',
    name: error?.name || 'Error',
    stack: error?.stack,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    userAgent: navigator.userAgent,
  }
  
  // В реальном приложении здесь была бы отправка в сервис мониторинга
  console.log('Global error logged:', errorData)
  
  if (process.env.NODE_ENV === 'production') {
    // fetch('/api/log-error', { method: 'POST', body: JSON.stringify(errorData) })
  }
}
