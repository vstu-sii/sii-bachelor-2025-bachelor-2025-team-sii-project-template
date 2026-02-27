'use client'

import React, { Component, ErrorInfo, ReactNode } from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import Button from '@/components/ui/Button'

interface Props {
  children: ReactNode
  fallback?: ReactNode
  onReset?: () => void
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    // Логирование ошибки в сервис мониторинга
    this.logErrorToService(error, errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })
  }

  private logErrorToService(error: Error, errorInfo: ErrorInfo): void {
    // В реальном приложении здесь была бы интеграция с Sentry, LogRocket и т.д.
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    }
    
    console.log('Error logged:', errorData)
    
    // Отправка в сервис мониторинга
    if (process.env.NODE_ENV === 'production') {
      // fetch('/api/log-error', { method: 'POST', body: JSON.stringify(errorData) })
    }
  }

  private handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    })
    
    if (this.props.onReset) {
      this.props.onReset()
    }
  }

  private handleGoHome = (): void => {
    window.location.href = '/'
  }

  private handleReload = (): void => {
    window.location.reload()
  }

  render(): ReactNode {
    if (this.state.hasError) {
      // Если передан кастомный fallback
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-6">
                <AlertTriangle className="h-8 w-8 text-red-600" />
              </div>
              
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Упс! Что-то пошло не так
              </h2>
              
              <p className="text-gray-600 mb-6">
                Произошла непредвиденная ошибка. Мы уже работаем над её устранением.
              </p>

              {/* Детали ошибки для разработчиков */}
              {process.env.NODE_ENV !== 'production' && this.state.error && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg text-left">
                  <details className="text-sm">
                    <summary className="font-medium text-gray-700 cursor-pointer mb-2">
                      Детали ошибки (только для разработки)
                    </summary>
                    <div className="mt-2 space-y-2">
                      <div>
                        <span className="font-medium">Сообщение:</span>
                        <div className="text-red-600 font-mono text-xs mt-1 p-2 bg-red-50 rounded">
                          {this.state.error.message}
                        </div>
                      </div>
                      {this.state.error.stack && (
                        <div>
                          <span className="font-medium">Стек вызовов:</span>
                          <pre className="text-xs text-gray-600 mt-1 p-2 bg-gray-100 rounded overflow-auto max-h-40">
                            {this.state.error.stack}
                          </pre>
                        </div>
                      )}
                    </div>
                  </details>
                </div>
              )}

              <div className="space-y-3">
                <Button
                  onClick={this.handleReset}
                  variant="primary"
                  fullWidth
                  icon={<RefreshCw className="h-4 w-4" />}
                >
                  Попробовать снова
                </Button>
                
                <Button
                  onClick={this.handleGoHome}
                  variant="outline"
                  fullWidth
                  icon={<Home className="h-4 w-4" />}
                >
                  На главную
                </Button>
                
                <Button
                  onClick={this.handleReload}
                  variant="ghost"
                  fullWidth
                >
                  Обновить страницу
                </Button>
              </div>

              <div className="mt-8 pt-6 border-t border-gray-200">
                <p className="text-sm text-gray-500">
                  Если ошибка повторяется, пожалуйста, сообщите нам об этом
                </p>
                <a
                  href="mailto:support@cooking-assistant.com"
                  className="text-sm text-orange-500 hover:text-orange-600 font-medium"
                >
                  support@cooking-assistant.com
                </a>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// HOC для удобного использования Error Boundary
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  errorBoundaryProps?: Partial<Props>
): React.FC<P> {
  const WrappedComponent: React.FC<P> = (props) => (
    <ErrorBoundary {...errorBoundaryProps}>
      <Component {...props} />
    </ErrorBoundary>
  )
  
  WrappedComponent.displayName = `withErrorBoundary(${Component.displayName || Component.name})`
  
  return WrappedComponent
}

// Компонент для отлова ошибок в конкретных местах
export function ErrorBoundaryArea({ children, area }: { children: ReactNode, area: string }) {
  return (
    <ErrorBoundary
      onReset={() => console.log(`Error boundary reset for area: ${area}`)}
      fallback={
        <div className="p-4 border border-red-200 bg-red-50 rounded-lg">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
            <span className="text-sm font-medium text-red-800">
              Ошибка в компоненте: {area}
            </span>
          </div>
          <p className="text-sm text-red-600 mt-1">
            Эта часть приложения временно недоступна
          </p>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  )
}
