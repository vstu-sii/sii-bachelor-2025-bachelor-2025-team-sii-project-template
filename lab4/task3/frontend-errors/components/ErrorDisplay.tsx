'use client'

import React from 'react'
import { AlertTriangle, XCircle, Info, CheckCircle, RefreshCw } from 'lucide-react'
import { useErrorDisplay } from '../hooks/useErrorMessages'
import { ApiError } from '@/lib/api'
import Button from '@/components/ui/Button'

interface ErrorDisplayProps {
  error: ApiError | null
  context?: string
  onRetry?: () => void
  onDismiss?: () => void
  className?: string
  showIcon?: boolean
  showAction?: boolean
}

export default function ErrorDisplay({
  error,
  context,
  onRetry,
  onDismiss,
  className = '',
  showIcon = true,
  showAction = true,
}: ErrorDisplayProps) {
  const { ErrorDisplay: ErrorDisplayComponent } = useErrorDisplay(error, context)
  
  if (!error) return null
  
  const getSeverityConfig = (status: number) => {
    if (status >= 500) {
      return {
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        textColor: 'text-red-800',
        icon: <XCircle className="h-5 w-5 text-red-500" />,
        title: 'Ошибка сервера',
      }
    } else if (status === 429) {
      return {
        bgColor: 'bg-yellow-50',
        borderColor: 'border-yellow-200',
        textColor: 'text-yellow-800',
        icon: <AlertTriangle className="h-5 w-5 text-yellow-500" />,
        title: 'Слишком много запросов',
      }
    } else if (status === 404) {
      return {
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
        textColor: 'text-blue-800',
        icon: <Info className="h-5 w-5 text-blue-500" />,
        title: 'Не найдено',
      }
    } else if (status === 403) {
      return {
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
        textColor: 'text-orange-800',
        icon: <AlertTriangle className="h-5 w-5 text-orange-500" />,
        title: 'Доступ запрещен',
      }
    } else {
      return {
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
        textColor: 'text-red-800',
        icon: <AlertTriangle className="h-5 w-5 text-red-500" />,
        title: 'Ошибка',
      }
    }
  }
  
  const config = getSeverityConfig(error.status)
  const isRetryable = error.status >= 500 || error.status === 429
  
  return (
    <div className={`${config.bgColor} ${config.borderColor} ${config.textColor} border rounded-xl p-4 ${className}`}>
      <div className="flex items-start">
        {showIcon && <div className="mr-3 mt-0.5">{config.icon}</div>}
        
        <div className="flex-1">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold">{config.title}</h3>
              <p className="mt-1 text-sm">{error.message}</p>
              
              {error.errors && Object.keys(error.errors).length > 0 && (
                <div className="mt-3 text-sm">
                  <details>
                    <summary className="cursor-pointer font-medium">
                      Детали ошибки
                    </summary>
                    <ul className="mt-2 space-y-1">
                      {Object.entries(error.errors).map(([field, messages]) => (
                        <li key={field} className="pl-2">
                          <span className="font-medium">{field}:</span>{' '}
                          {messages.join(', ')}
                        </li>
                      ))}
                    </ul>
                  </details>
                </div>
              )}
            </div>
            
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="ml-2 text-gray-500 hover:text-gray-700"
                aria-label="Закрыть"
              >
                <XCircle className="h-5 w-5" />
              </button>
            )}
          </div>
          
          {showAction && (
            <div className="mt-4 flex flex-wrap gap-2">
              {isRetryable && onRetry && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={onRetry}
                  icon={<RefreshCw className="h-4 w-4" />}
                >
                  Повторить
                </Button>
              )}
              
              {error.status === 401 && (
                <Button
                  size="sm"
                  variant="primary"
                  onClick={() => window.location.href = '/login'}
                >
                  Войти в систему
                </Button>
              )}
              
              {error.status === 403 && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => window.location.href = '/'}
                >
                  На главную
                </Button>
              )}
              
              <Button
                size="sm"
                variant="ghost"
                onClick={() => window.location.reload()}
              >
                Обновить страницу
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Специализированные компоненты ошибок
export function NetworkErrorDisplay({ onRetry }: { onRetry?: () => void }) {
  return (
    <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6 text-center">
      <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-yellow-800 mb-2">
        Проблемы с соединением
      </h3>
      <p className="text-yellow-700 mb-4">
        Не удалось подключиться к серверу. Проверьте подключение к интернету.
      </p>
      {onRetry && (
        <Button
          variant="outline"
          onClick={onRetry}
          icon={<RefreshCw className="h-4 w-4" />}
        >
          Повторить попытку
        </Button>
      )}
    </div>
  )
}

export function LoadingErrorDisplay({ resourceName, onRetry }: { 
  resourceName: string, 
  onRetry?: () => void 
}) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
      <XCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-red-800 mb-2">
        Ошибка загрузки
      </h3>
      <p className="text-red-700 mb-4">
        Не удалось загрузить {resourceName}. Пожалуйста, попробуйте снова.
      </p>
      {onRetry && (
        <Button
          variant="outline"
          onClick={onRetry}
          icon={<RefreshCw className="h-4 w-4" />}
        >
          Загрузить снова
        </Button>
      )}
    </div>
  )
}

export function EmptyStateDisplay({ 
  title, 
  message, 
  action 
}: { 
  title: string, 
  message: string, 
  action?: { label: string, onClick: () => void } 
}) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded-xl p-8 text-center">
      <Info className="h-12 w-12 text-gray-400 mx-auto mb-4" />
      <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600 mb-6">{message}</p>
      {action && (
        <Button
          variant="primary"
          onClick={action.onClick}
        >
          {action.label}
        </Button>
      )}
    </div>
  )
}