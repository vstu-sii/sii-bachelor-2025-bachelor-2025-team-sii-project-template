# Интеграция системы обработки ошибок

## 🚀 Быстрый старт

### 1. Интеграция Error Boundaries

```tsx
// В src/app/layout.tsx
import { ErrorBoundary } from '@/errors/components/ErrorBoundary'
import { GlobalErrorHandler } from '@/errors/components/GlobalErrorHandler'

export default function RootLayout({ children }) {
  return (
    <ErrorBoundary>
      <GlobalErrorHandler>
        {children}
      </GlobalErrorHandler>
    </ErrorBoundary>
  )
}

// Для отдельных компонентов
import { ErrorBoundaryArea } from '@/errors/components/ErrorBoundary'

function MyComponent() {
  return (
    <ErrorBoundaryArea area="MyComponent">
      <div>Контент компонента</div>
    </ErrorBoundaryArea>
  )
}

2. Интеграция обработки ошибок API
python

# В backend/api/main.py
from backend_exceptions.handlers.error_handler import setup_exception_handlers

def create_application() -> FastAPI:
    app = FastAPI(...)
    setup_exception_handlers(app)  # Добавить эту строку
    return app

3. Использование кастомных исключений
python

from backend_exceptions.custom_exceptions.business import (
    DishNotFoundException,
    DishAlreadyAnalyzedException,
    RecipeTooShortException
)

@router.get("/dishes/{dish_id}")
async def get_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = await get_dish_from_db(dish_id)
    
    if not dish:
        raise DishNotFoundException(dish_id)  # Бросаем кастомное исключение
    
    return dish

4. Использование retry логики для AI
python

from retry_logic.ai_retry_strategy import resilient_ai_function

@resilient_ai_function
async def analyze_dish_with_ai(photo_url: str, recipe: str):
    # Ваш код AI анализа
    result = await ai_service.analyze(photo_url, recipe)
    return result

5. Использование хуков ошибок на фронтенде
tsx

import { useErrorDisplay, useErrorToast } from '@/errors/hooks/useErrorMessages'

function MyComponent() {
  const [error, setError] = useState<ApiError | null>(null)
  const { showErrorToast } = useErrorToast()
  const { ErrorDisplay, hasError } = useErrorDisplay(error, 'dish')
  
  const handleAction = async () => {
    try {
      await someApiCall()
    } catch (err) {
      setError(err)
      showErrorToast(err, 'analysis')
    }
  }
  
  return (
    <div>
      {hasError && <ErrorDisplay />}
      <button onClick={handleAction}>Выполнить</button>
    </div>
  )
}

📁 Структура файлов после интеграции
text

task1/
├── frontend/
│   ├── src/
│   │   ├── errors/                    # Новая папка с обработкой ошибок
│   │   │   ├── components/
│   │   │   │   ├── ErrorBoundary.tsx
│   │   │   │   ├── GlobalErrorHandler.tsx
│   │   │   │   └── ErrorDisplay.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useErrorMessages.ts
│   │   │   └── contexts/
│   │   └── app/
│   │       └── layout.tsx            # Обновлён с ErrorBoundary
│   └── package.json                  # Добавлены зависимости если нужно
│
├── backend/
│   ├── backend_exceptions/           # Новая папка с исключениями
│   │   ├── handlers/
│   │   │   └── error_handler.py
│   │   ├── custom_exceptions/
│   │   │   ├── base.py
│   │   │   ├── business.py
│   │   │   └── __init__.py
│   │   └── middleware/
│   ├── services/
│   │   └── ai_service.py            # Обновлён с retry логикой
│   ├── retry_logic/                  # Новая папка
│   │   └── ai_retry_strategy.py
│   └── api/
│       └── main.py                  # Обновлён с обработчиками ошибок
│
└── task3/                           # Документация и примеры
    ├── integration-guide.md
    └── examples/

🔧 Конфигурация
Frontend Environment Variables
env

NEXT_PUBLIC_ERROR_REPORTING_ENABLED=true
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn # Если используется Sentry
NEXT_PUBLIC_LOG_ROCKET_ID=your-logrocket-id # Если используется LogRocket

Backend Environment Variables
env

ERROR_REPORTING_ENABLED=true
SENTRY_DSN=your-sentry-dsn
LOG_LEVEL=INFO
DEBUG=false # В production всегда false

🧪 Тестирование ошибок
Тестирование Error Boundaries
tsx

// В тестах
import { render, screen, fireEvent } from '@testing-library/react'
import { ErrorBoundary } from '@/errors/components/ErrorBoundary'

const ThrowError = () => {
  throw new Error('Test error')
}

test('ErrorBoundary catches errors and shows fallback', () => {
  render(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  )
  
  expect(screen.getByText(/Упс! Что-то пошло не так/i)).toBeInTheDocument()
})

Тестирование API Error Handlers
python

# В тестах бэкенда
import pytest
from fastapi import status
from backend_exceptions.custom_exceptions.business import DishNotFoundException

def test_dish_not_found_exception():
    with pytest.raises(DishNotFoundException) as exc_info:
        raise DishNotFoundException(123)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Блюдо с ID 123 не найдено" in str(exc_info.value.detail)

📊 Мониторинг ошибок
1. Логирование ошибок на фронтенде
typescript

// В ErrorBoundary.tsx
private logErrorToService(error: Error, errorInfo: ErrorInfo) {
  const errorData = {
    message: error.message,
    componentStack: errorInfo.componentStack,
    url: window.location.href,
    timestamp: new Date().toISOString(),
  }
  
  // Отправка в ваш сервис мониторинга
  if (process.env.NEXT_PUBLIC_ERROR_REPORTING_ENABLED === 'true') {
    navigator.sendBeacon('/api/client-errors', JSON.stringify(errorData))
  }
}

2. Логирование ошибок на бэкенде
python

# В error_handler.py
import logging
import structlog

logger = structlog.get_logger()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        "unhandled_exception",
        exc_info=True,
        path=request.url.path,
        method=request.method,
        error_type=type(exc).__name__,
        error_message=str(exc)
    )
    
    # Отправка в Sentry/DataDog/etc
    if settings.ERROR_REPORTING_ENABLED:
        sentry_sdk.capture_exception(exc)

🚨 Процедура обработки инцидентов
1. Критическая ошибка (500)

    Автоматически логируется

    Пользователь видит дружелюбное сообщение

    Отправляется уведомление команде

    Создается инцидент в системе мониторинга

2. Ошибка валидации (422)

    Подробные сообщения для пользователя

    Подсветка проблемных полей

    Предложения по исправлению

3. Ошибка аутентификации (401/403)

    Перенаправление на страницу входа

    Сохранение текущего URL для возврата

    Очистка невалидных токенов

4. Ошибка сети

    Автоматические повторные попытки

    Показать состояние оффлайн

    Кэширование данных если возможно

📈 Метрики и аналитика

Отслеживайте следующие метрики:

    Error Rate: Процент запросов с ошибками

    MTTR: Среднее время восстановления

    Error by Type: Распределение ошибок по типам

    User Impact: Сколько пользователей затронуто

    Retry Success Rate: Эффективность повторных попыток

🔮 Дальнейшее развитие

    Интеграция с Sentry/DataDog

    Real-time оповещения в Slack/Telegram

    Error dashboard для команды

    Automatic error grouping и дедупликация

    Performance monitoring вместе с error tracking

✅ Чеклист внедрения

    Добавить ErrorBoundary в корневой layout

    Интеграция обработчиков ошибок в FastAPI

    Заменить простые исключения на кастомные

    Добавить retry логику для AI запросов

    Создать user-friendly сообщения об ошибках

    Настроить логирование ошибок

    Протестировать все сценарии ошибок

    Обновить документацию

Статус интеграции: ✅ Готово к использованию
Время на интеграцию: 2-4 часа
Сложность: Средняя