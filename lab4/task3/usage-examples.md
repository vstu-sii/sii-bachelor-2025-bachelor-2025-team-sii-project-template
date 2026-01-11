
## 🎯 Примеры использования

```bash
cat > task3/examples/usage-examples.md << 'EOF'
# Примеры использования системы обработки ошибок

## Пример 1: Обработка ошибки загрузки блюда

```tsx
'use client'

import { useState } from 'react'
import { useApp } from '@/contexts/AppContext'
import ErrorDisplay, { LoadingErrorDisplay } from '@/errors/components/ErrorDisplay'
import { ErrorBoundaryArea } from '@/errors/components/ErrorBoundary'
import { useErrorToast } from '@/errors/hooks/useErrorMessages'

export default function DishPage({ dishId }: { dishId: number }) {
  const [error, setError] = useState(null)
  const { fetchDish, isLoading } = useApp()
  const { showErrorToast } = useErrorToast()

  const loadDish = async () => {
    try {
      setError(null)
      await fetchDish(dishId)
    } catch (err) {
      setError(err)
      showErrorToast(err, 'dish')
    }
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  return (
    <ErrorBoundaryArea area="DishPage">
      <div className="p-4">
        {error && (
          <ErrorDisplay
            error={error}
            context="dish"
            onRetry={loadDish}
          />
        )}
        
        <DishContent />
      </div>
    </ErrorBoundaryArea>
  )
}

Пример 2: Использование кастомных исключений в API
python

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend_exceptions.custom_exceptions.business import (
    DishNotFoundException,
    DishAlreadyAnalyzedException,
    RecipeTooShortException
)
from backend_exceptions.custom_exceptions.base import ValidationException
from retry_logic.ai_retry_strategy import resilient_ai_function

router = APIRouter()

@router.post("/dishes/{dish_id}/analyze")
async def analyze_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # 1. Проверяем существование блюда
    dish = await get_dish(db, dish_id)
    if not dish:
        raise DishNotFoundException(dish_id)
    
    # 2. Проверяем что блюдо принадлежит пользователю
    if dish.user_id != current_user.id:
        raise AuthorizationException()
    
    # 3. Проверяем что анализ ещё не выполнялся
    if dish.status == "ready":
        raise DishAlreadyAnalyzedException(dish_id)
    
    # 4. Проверяем длину рецепта
    if len(dish.user_recipe_text) < 50:
        raise RecipeTooShortException(min_length=50)
    
    # 5. Выполняем AI анализ с retry стратегией
    @resilient_ai_function
    async def analyze_with_ai():
        return await ai_service.analyze_dish(dish)
    
    try:
        analysis = await analyze_with_ai()
        
        # 6. Сохраняем результат
        await save_analysis(db, dish_id, analysis)
        
        return {
            "status": "success",
            "analysis": analysis
        }
        
    except Exception as exc:
        # 7. Логируем ошибку и пробрасываем дальше
        logger.error(f"AI analysis failed for dish {dish_id}: {exc}")
        raise AIAnalysisFailedException(str(exc))

Пример 3: Retry стратегия с Circuit Breaker
python

from retry_logic.ai_retry_strategy import (
    ai_retry_strategy,
    ai_circuit_breaker,
    ai_monitoring
)

class AIService:
    @ai_retry_strategy
    async def analyze_dish(self, dish_data: DishAnalysisRequest):
        # Мониторинг вызова
        ai_monitoring.record_request()
        
        # Проверяем состояние circuit breaker
        if ai_circuit_breaker.state == "OPEN":
            raise ExternalServiceException("AI сервис временно недоступен")
        
        try:
            # Имитируем вызов к реальному AI API
            result = await self._call_ai_api(dish_data)
            
            # Записываем успех
            ai_monitoring.record_success(response_time=1.5)
            ai_circuit_breaker._on_success()
            
            return result
            
        except (TimeoutError, ConnectionError) as exc:
            # Записываем ошибку
            ai_monitoring.record_failure(exc)
            ai_circuit_breaker._on_failure()
            
            # Пробрасываем для retry логики
            raise ExternalServiceException("AI API временно недоступен")
            
        except Exception as exc:
            # Критические ошибки не повторяем
            ai_monitoring.record_failure(exc)
            raise AIAnalysisFailedException(str(exc))
    
    def get_health_status(self):
        """Возвращает статус здоровья AI сервиса"""
        return ai_monitoring.get_health_status()

Пример 4: User-Friendly сообщения в UI
tsx

import { useErrorDisplay } from '@/errors/hooks/useErrorMessages'

function UploadPhotoForm() {
  const [uploadError, setUploadError] = useState(null)
  const { ErrorDisplay } = useErrorDisplay(uploadError, 'upload')
  
  const handleFileUpload = async (file: File) => {
    try {
      // Проверяем размер файла
      if (file.size > 10 * 1024 * 1024) {
        throw {
          status: 422,
          message: 'Файл слишком большой',
          errors: { photo: ['Максимальный размер: 10MB'] }
        }
      }
      
      // Проверяем формат
      if (!file.type.startsWith('image/')) {
        throw {
          status: 422,
          message: 'Неверный формат файла',
          errors: { photo: ['Разрешены только изображения'] }
        }
      }
      
      // Загружаем файл
      await api.uploadPhoto(file)
      
    } catch (error) {
      setUploadError(error)
    }
  }
  
  return (
    <div className="space-y-4">
      {uploadError && (
        <ErrorDisplay
          error={uploadError}
          context="upload"
          onRetry={() => setUploadError(null)}
        />
      )}
      
      <FileUpload onFileSelect={handleFileUpload} />
      
      <div className="text-sm text-gray-500">
        <p>📸 Совет: Используйте хорошее освещение</p>
        <p>📁 Максимальный размер: 10MB</p>
        <p>🖼️ Форматы: JPG, PNG, WebP</p>
      </div>
    </div>
  )
}

Пример 5: Глобальная обработка ошибок
tsx

// В корневом layout.tsx
import { ErrorBoundary } from '@/errors/components/ErrorBoundary'
import { GlobalErrorHandler } from '@/errors/components/GlobalErrorHandler'
import { Toaster } from 'react-hot-toast'

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>
        <ErrorBoundary
          onReset={() => {
            // Дополнительная логика при восстановлении
            console.log('Application recovered from error')
          }}
        >
          <GlobalErrorHandler>
            {children}
            <Toaster />
          </GlobalErrorHandler>
        </ErrorBoundary>
      </body>
    </html>
  )
}

// В API клиенте (src/lib/api.ts)
class ApiClient {
  private setupInterceptors() {
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Преобразуем ошибку в стандартный формат
        const apiError = {
          message: this.getUserFriendlyMessage(error),
          status: error.response?.status || 500,
          errors: error.response?.data?.errors,
        }
        
        // Логируем ошибку
        this.logError(apiError)
        
        // Показываем toast уведомление для пользователя
        if (typeof window !== 'undefined') {
          import('react-hot-toast').then(({ default: toast }) => {
            toast.error(this.getToastMessage(apiError), {
              duration: 5000,
              position: 'top-right',
            })
          })
        }
        
        return Promise.reject(apiError)
      }
    )
  }
  
  private getUserFriendlyMessage(error: any): string {
    const status = error.response?.status
    
    switch (status) {
      case 401:
        return 'Сессия истекла. Пожалуйста, войдите снова.'
      case 403:
        return 'У вас недостаточно прав для этого действия.'
      case 404:
        return 'Запрашиваемый ресурс не найден.'
      case 429:
        return 'Слишком много запросов. Пожалуйста, подождите.'
      case 500:
        return 'Внутренняя ошибка сервера. Мы уже работаем над решением.'
      default:
        return error.response?.data?.detail || 'Произошла ошибка при выполнении запроса.'
    }
  }
}

Пример 6: Тестирование системы ошибок
python

# Тестирование обработчиков ошибок API
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

def test_404_error_handler(client: TestClient):
    """Тест что несуществующий endpoint возвращает 404 с правильным форматом"""
    response = client.get("/api/nonexistent")
    
    assert response.status_code == 404
    assert response.json()["error_code"] == "NOT_FOUND"
    assert "Запрашиваемый ресурс не найден" in response.json()["detail"]

def test_validation_error_handler(client: TestClient, auth_headers):
    """Тест обработки ошибок валидации"""
    # Пытаемся создать блюдо с коротким рецептом
    response = client.post(
        "/api/dishes/",
        headers=auth_headers,
        data={"user_recipe_text": "short"},
        files={"photo": ("test.jpg", b"fake", "image/jpeg")}
    )
    
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "errors" in data
    assert len(data["errors"]) > 0

def test_retry_strategy_on_timeout():
    """Тест retry стратегии при таймаутах"""
    mock_ai_service = Mock()
    mock_ai_service.analyze.side_effect = [
        TimeoutError("First timeout"),
        TimeoutError("Second timeout"),
        {"score": 4.5}  # Успех на третьей попытке
    ]
    
    from retry_logic.ai_retry_strategy import ai_retry_strategy
    
    @ai_retry_strategy
    async def analyze():
        return await mock_ai_service.analyze()
    
    # Должно быть 3 вызова из-за retry
    result = asyncio.run(analyze())
    assert mock_ai_service.analyze.call_count == 3
    assert result["score"] == 4.5

def test_circuit_breaker_opens_on_failures():
    """Тест что circuit breaker открывается при нескольких ошибках"""
    from retry_logic.ai_retry_strategy import ai_circuit_breaker
    
    # Сбрасываем состояние
    ai_circuit_breaker.state = "CLOSED"
    ai_circuit_breaker.failure_count = 0
    
    # Симулируем 5 ошибок подряд
    for _ in range(5):
        ai_circuit_breaker._on_failure()
    
    assert ai_circuit_breaker.state == "OPEN"
    assert ai_circuit_breaker.failure_count == 5

🎯 Итог

Система обработки ошибок предоставляет:

    Для пользователей: Понятные сообщения и возможности восстановления

    Для разработчиков: Детальное логирование и упрощение отладки

    Для DevOps: Мониторинг и алертинг о проблемах

    Для бизнеса: Уменьшение потерь из-за ошибок и улучшение UX

Все компоненты готовы к использованию и легко интегрируются в существующий проект.