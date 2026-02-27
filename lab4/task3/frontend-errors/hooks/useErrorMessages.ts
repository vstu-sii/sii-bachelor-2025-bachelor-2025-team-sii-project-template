'use client'
import { useMemo } from 'react'
import { ApiError } from '@/lib/api'

export interface ErrorMessage {
  title: string
  message: string
  severity: 'error' | 'warning' | 'info'
  suggestion?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function useErrorMessages(error: ApiError | null, context?: string): ErrorMessage | null {
  return useMemo(() => {
    if (!error) return null
    
    const { status, message, errors } = error
    
    // Базовый шаблон ошибки
    let errorMessage: ErrorMessage = {
      title: 'Ошибка',
      message: message || 'Произошла неизвестная ошибка',
      severity: 'error' as const,
    }
    
    // Обработка по статус кодам
    switch (status) {
      case 400:
        errorMessage.title = 'Неверный запрос'
        errorMessage.message = 'Проверьте введенные данные и попробуйте снова.'
        errorMessage.suggestion = errors ? getValidationSuggestions(errors) : 'Проверьте все обязательные поля.'
        break
        
      case 401:
        errorMessage.title = 'Неавторизованный доступ'
        errorMessage.message = 'Для доступа к этой странице необходимо войти в систему.'
        errorMessage.severity = 'warning'
        errorMessage.action = {
          label: 'Войти',
          onClick: () => window.location.href = '/login'
        }
        break
        
      case 403:
        errorMessage.title = 'Доступ запрещен'
        errorMessage.message = 'У вас недостаточно прав для выполнения этого действия.'
        errorMessage.severity = 'warning'
        break
        
      case 404:
        errorMessage.title = 'Не найдено'
        if (context === 'dish') {
          errorMessage.message = 'Блюдо не найдено. Возможно, оно было удалено.'
        } else if (context === 'analysis') {
          errorMessage.message = 'Анализ не найден. Попробуйте запустить анализ снова.'
        } else {
          errorMessage.message = 'Запрашиваемый ресурс не найден.'
        }
        break
        
      case 409:
        errorMessage.title = 'Конфликт'
        errorMessage.message = 'Не удалось выполнить операцию из-за конфликта данных.'
        if (message.includes('уже существует')) {
          errorMessage.suggestion = 'Попробуйте использовать другие данные.'
        }
        break
        
      case 422:
        errorMessage.title = 'Ошибка валидации'
        errorMessage.message = 'Пожалуйста, проверьте введенные данные.'
        errorMessage.suggestion = errors ? getValidationSuggestions(errors) : 'Исправьте выделенные ошибки.'
        break
        
      case 429:
        errorMessage.title = 'Слишком много запросов'
        errorMessage.message = 'Вы превысили лимит запросов. Пожалуйста, подождите немного.'
        errorMessage.severity = 'warning'
        errorMessage.suggestion = 'Попробуйте снова через несколько минут.'
        break
        
      case 500:
        errorMessage.title = 'Ошибка сервера'
        errorMessage.message = 'На сервере произошла ошибка. Мы уже работаем над её устранением.'
        errorMessage.suggestion = 'Попробуйте обновить страницу или повторить попытку позже.'
        break
        
      case 502:
      case 503:
      case 504:
        errorMessage.title = 'Сервис недоступен'
        errorMessage.message = 'Сервис временно недоступен. Пожалуйста, попробуйте позже.'
        errorMessage.suggestion = 'Проверьте подключение к интернету и попробуйте обновить страницу.'
        break
        
      default:
        if (status >= 500) {
          errorMessage.title = 'Ошибка сервера'
          errorMessage.message = 'Произошла внутренняя ошибка сервера.'
        } else if (status >= 400) {
          errorMessage.title = 'Ошибка клиента'
        }
    }
    
    // Контекст-специфичные сообщения
    if (context) {
      errorMessage = applyContextSpecificMessages(errorMessage, context, message)
    }
    
    // Добавляем детали ошибок валидации
    if (errors && Object.keys(errors).length > 0) {
      errorMessage.message += `\n\nДетали:\n${formatValidationErrors(errors)}`
    }
    
    return errorMessage
    
  }, [error, context])
}

function getValidationSuggestions(errors: Record<string, string[]>): string {
  const suggestions: string[] = []
  
  Object.entries(errors).forEach(([field, messages]) => {
    const fieldName = getFieldDisplayName(field)
    
    messages.forEach(msg => {
      if (msg.includes('required') || msg.includes('обязательно')) {
        suggestions.push(`Заполните поле "${fieldName}"`)
      } else if (msg.includes('email') || msg.includes('почта')) {
        suggestions.push('Введите корректный email адрес')
      } else if (msg.includes('password') || msg.includes('пароль')) {
        suggestions.push('Пароль должен содержать не менее 6 символов')
      } else if (msg.includes('length') || msg.includes('длина')) {
        if (msg.includes('min')) {
          suggestions.push(`Поле "${fieldName}" должно быть длиннее`)
        } else if (msg.includes('max')) {
          suggestions.push(`Поле "${fieldName}" должно быть короче`)
        }
      } else if (msg.includes('file') || msg.includes('файл')) {
        suggestions.push('Проверьте размер и формат загружаемого файла')
      }
    })
  })
  
  return suggestions.length > 0 
    ? suggestions.slice(0, 3).join('. ') + '.'
    : 'Проверьте введенные данные.'
}

function getFieldDisplayName(field: string): string {
  const fieldMap: Record<string, string> = {
    'username': 'Имя пользователя',
    'email': 'Email',
    'password': 'Пароль',
    'photo': 'Фото',
    'dish_type': 'Тип блюда',
    'user_recipe_text': 'Рецепт',
    'title': 'Название',
    'description': 'Описание',
  }
  
  return fieldMap[field] || field
}

function formatValidationErrors(errors: Record<string, string[]>): string {
  return Object.entries(errors)
    .map(([field, messages]) => {
      const fieldName = getFieldDisplayName(field)
      return `• ${fieldName}: ${messages.join(', ')}`
    })
    .join('\n')
}

function applyContextSpecificMessages(
  baseMessage: ErrorMessage,
  context: string,
  originalMessage: string
): ErrorMessage {
  const newMessage = { ...baseMessage }
  
  switch (context) {
    case 'login':
      if (originalMessage.includes('Неверный email или пароль')) {
        newMessage.title = 'Ошибка входа'
        newMessage.message = 'Неверный email или пароль.'
        newMessage.suggestion = 'Проверьте правильность введенных данных или восстановите пароль.'
        newMessage.action = {
          label: 'Восстановить пароль',
          onClick: () => window.location.href = '/forgot-password'
        }
      }
      break
      
    case 'register':
      if (originalMessage.includes('уже существует')) {
        newMessage.title = 'Пользователь уже существует'
        newMessage.message = 'Пользователь с таким email уже зарегистрирован.'
        newMessage.suggestion = 'Попробуйте использовать другой email или войдите в существующий аккаунт.'
        newMessage.action = {
          label: 'Войти',
          onClick: () => window.location.href = '/login'
        }
      }
      break
      
    case 'upload':
      if (originalMessage.includes('too large') || originalMessage.includes('большой')) {
        newMessage.title = 'Файл слишком большой'
        newMessage.message = 'Размер файла превышает допустимый лимит.'
        newMessage.suggestion = 'Выберите файл размером до 10MB или сожмите изображение.'
      } else if (originalMessage.includes('format') || originalMessage.includes('формат')) {
        newMessage.title = 'Неверный формат файла'
        newMessage.message = 'Формат файла не поддерживается.'
        newMessage.suggestion = 'Используйте файлы форматов JPG, PNG или WebP.'
      }
      break
      
    case 'analysis':
      if (originalMessage.includes('уже проанализировано')) {
        newMessage.title = 'Анализ уже выполнен'
        newMessage.message = 'Это блюдо уже было проанализировано.'
        newMessage.severity = 'info'
        newMessage.suggestion = 'Вы можете просмотреть существующий анализ.'
      } else if (originalMessage.includes('Не удалось проанализировать')) {
        newMessage.title = 'Ошибка анализа'
        newMessage.message = 'Не удалось проанализировать блюдо.'
        newMessage.suggestion = 'Попробуйте загрузить другое фото или подробнее описать рецепт.'
        newMessage.action = {
          label: 'Повторить',
          onClick: () => window.location.reload()
        }
      }
      break
      
    case 'network':
      newMessage.title = 'Проблемы с соединением'
      newMessage.message = 'Не удалось подключиться к серверу.'
      newMessage.suggestion = 'Проверьте подключение к интернету и попробуйте снова.'
      newMessage.action = {
        label: 'Обновить',
        onClick: () => window.location.reload()
      }
      break
  }
  
  return newMessage
}

// Хук для отображения ошибок в формате toast
export function useErrorToast() {
  const showErrorToast = (error: ApiError | string, context?: string) => {
    const errorMessage = typeof error === 'string' 
      ? { message: error, status: 500 }
      : error
    
    const formattedError = useErrorMessages(errorMessage, context)
    
    if (formattedError && typeof window !== 'undefined') {
      // Импортируем toast только на клиенте
      import('react-hot-toast').then(({ default: toast }) => {
        toast.error(
          <div>
            <div className="font-semibold">{formattedError.title}</div>
            <div className="text-sm mt-1">{formattedError.message}</div>
            {formattedError.suggestion && (
              <div className="text-xs mt-2 text-gray-600">{formattedError.suggestion}</div>
            )}
          </div>,
          {
            duration: 5000,
            position: 'top-right',
          }
        )
      })
    }
  }
  
  return { showErrorToast }
}

// Хук для отображения ошибок в UI компонентах
export function useErrorDisplay(error: ApiError | null, context?: string) {
  const errorMessage = useErrorMessages(error, context)
  
  const ErrorDisplay = () => {
    if (!errorMessage) return null
    
    const bgColor = {
      error: 'bg-red-50 border-red-200 text-red-800',
      warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      info: 'bg-blue-50 border-blue-200 text-blue-800',
    }[errorMessage.severity]
    
    const icon = {
      error: '❌',
      warning: '⚠️',
      info: 'ℹ️',
    }[errorMessage.severity]
    
    return (
      <div className={`${bgColor} border rounded-lg p-4 mb-4`}>
        <div className="flex items-start">
          <span className="text-lg mr-2">{icon}</span>
          <div className="flex-1">
            <div className="font-semibold">{errorMessage.title}</div>
            <div className="mt-1">{errorMessage.message}</div>
            {errorMessage.suggestion && (
              <div className="mt-2 text-sm opacity-90">{errorMessage.suggestion}</div>
            )}
            {errorMessage.action && (
              <button
                onClick={errorMessage.action.onClick}
                className="mt-3 px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded text-sm font-medium transition-colors"
              >
                {errorMessage.action.label}
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }
  
  return {
    ErrorDisplay,
    hasError: !!errorMessage,
    errorMessage
  }
}
