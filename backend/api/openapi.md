# API Спецификация Cooking Assistant

## Общая информация

**Базовый URL:** `https://api.cooking-assistant.com/v1`

**Формат данных:** JSON для всех запросов и ответов, кроме загрузки файлов (multipart/form-data)

## Аутентификация

Все запросы (кроме регистрации и логина) требуют JWT токен в заголовке:
```
Authorization: Bearer <your_jwt_token>
```

## Эндпоинты

### 🔐 Аутентификация

#### Регистрация нового пользователя
```http
POST /auth/register
```

**Тело запроса:**
```json
{
  "username": "chef_alex",
  "email": "alex@example.com",
  "password": "securePassword123"
}
```

**Успешный ответ (201):**
```json
{
  "message": "User created successfully",
  "userId": "user_123"
}
```

#### Авторизация
```http
POST /auth/login
```

**Тело запроса:**
```json
{
  "email": "alex@example.com",
  "password": "securePassword123"
}
```

**Успешный ответ (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "username": "chef_alex",
    "email": "alex@example.com",
    "created_at": "2024-01-15T10:30:00Z",
    "email_verified": true
  }
}
```

#### Подтверждение email
```http
POST /auth/verify-email
```

**Тело запроса:**
```json
{
  "token": "verification_token_from_email"
}
```

### 🍽️ Управление блюдами

#### Создание нового блюда для анализа
```http
POST /dishes
Content-Type: multipart/form-data
```

**Параметры:**
- `photo` (обязательный) - файл изображения (JPEG, PNG, max 10MB)
- `user_recipe_text` (обязательный) - текст рецепта (50-2000 символов)
- `dish_type` - тип блюда: breakfast, lunch, dinner, dessert, baking, other

**Успешный ответ (202):**
```json
{
  "dish_id": "dish_abc123",
  "status": "processing",
  "estimated_time": 30
}
```

#### Получение истории блюд
```http
GET /dishes?page=1&limit=20&dish_type=dinner&status=ready
```

**Параметры запроса:**
- `page` - номер страницы (по умолчанию 1)
- `limit` - количество элементов на странице (1-50, по умолчанию 20)
- `dish_type` - фильтр по типу блюда
- `status` - фильтр по статусу: processing, ready, draft

**Успешный ответ (200):**
```json
{
  "dishes": [
    {
      "id": "dish_abc123",
      "user_id": "user_123",
      "photo_url": "https://storage.example.com/photos/dish_abc123.jpg",
      "dish_type": "dinner",
      "user_recipe_text": "Паста карбонара...",
      "status": "ready",
      "created_at": "2024-01-15T14:30:00Z",
      "analysis_result": {
        "appearance_score": 4,
        "recipe_score": 3,
        "appearance_feedback": "Блюдо выглядит аппетитно...",
        "recipe_feedback": "Соответствует рецепту...",
        "recommendations": "Попробуйте уменьшить время приготовления...",
        "analyzed_at": "2024-01-15T14:35:00Z"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 42,
    "total_pages": 3
  }
}
```

#### Получение информации о конкретном блюде
```http
GET /dishes/{dish_id}
```

#### Получение результатов анализа блюда
```http
GET /dishes/{dish_id}/analysis
```

**Возможные ответы:**

**Анализ завершен (200):**
```json
{
  "appearance_score": 4,
  "recipe_score": 3,
  "appearance_feedback": "Паста имеет аппетитный вид, хорошая текстура...",
  "recipe_feedback": "Основные ингредиенты соответствуют рецепту...",
  "recommendations": "Для лучшей консистенции соуса попробуйте...",
  "analyzed_at": "2024-01-15T14:35:00Z"
}
```

**Анализ в процессе (202):**
```json
{
  "status": "processing",
  "progress": 75
}
```

### 📊 Статистика

#### Общая статистика пользователя
```http
GET /statistics/overview
```

**Успешный ответ (200):**
```json
{
  "total_dishes": 42,
  "average_appearance_score": 4.2,
  "average_recipe_score": 3.8,
  "by_dish_type": [
    {
      "dish_type": "dinner",
      "count": 15,
      "avg_appearance_score": 4.5,
      "avg_recipe_score": 4.2,
      "trend": "improving"
    },
    {
      "dish_type": "breakfast",
      "count": 10,
      "avg_appearance_score": 3.8,
      "avg_recipe_score": 3.5,
      "trend": "stable"
    }
  ]
}
```

#### Статистика по типу блюд
```http
GET /statistics/dish-types/{dish_type}
```

**Успешный ответ (200):**
```json
{
  "dish_type": "dinner",
  "overall_stats": {
    "dish_type": "dinner",
    "count": 15,
    "avg_appearance_score": 4.5,
    "avg_recipe_score": 4.2,
    "trend": "improving"
  },
  "recent_dishes": [
    {
      "id": "dish_abc123",
      "photo_url": "https://storage.example.com/photos/dish_abc123.jpg",
      "created_at": "2024-01-15T14:30:00Z",
      "analysis_result": {
        "appearance_score": 4,
        "recipe_score": 3
      }
    }
  ],
  "ai_recommendations": "Вы показываете стабильный прогресс в приготовлении ужинов. Особенно хорошо получаются мясные блюда. Рекомендуем обратить внимание на гарниры - попробуйте экспериментировать с разными видами овощей."
}
```

### 🤖 AI Processing (внутренние эндпоинты)

#### Прямой анализ блюда
```http
POST /ai/analyze
```

**Тело запроса:**
```json
{
  "dish_id": "dish_abc123",
  "image_url": "https://storage.example.com/photos/dish_abc123.jpg",
  "user_recipe_text": "Паста карбонара: 200г спагетти, 100г бекона..."
}
```

## Модели данных

### Пользователь (User)
```typescript
interface User {
  id: string;
  username: string;
  email: string;
  created_at: string; // ISO date
  email_verified: boolean;
}
```

### Блюдо (Dish)
```typescript
interface Dish {
  id: string;
  user_id: string;
  photo_url: string;
  dish_type: 'breakfast' | 'lunch' | 'dinner' | 'dessert' | 'baking' | 'other';
  user_recipe_text: string;
  status: 'draft' | 'processing' | 'ready';
  created_at: string; // ISO date
  analysis_result?: AnalysisResult;
}
```

### Результат анализа (AnalysisResult)
```typescript
interface AnalysisResult {
  appearance_score: number; // 1-5
  recipe_score: number; // 1-5
  appearance_feedback: string;
  recipe_feedback: string;
  recommendations: string;
  analyzed_at: string; // ISO date
}
```

### Статистика по типу блюд (DishTypeStats)
```typescript
interface DishTypeStats {
  dish_type: string;
  count: number;
  avg_appearance_score: number;
  avg_recipe_score: number;
  trend: 'improving' | 'stable' | 'declining';
}
```

## Rate Limiting

### Глобальные лимиты
- **1000 запросов** в час на IP
- **Burst**: 50 запросов одновременно

### Лимиты по эндпоинтам

| Эндпоинт | Метод | Лимит | Период |
|----------|--------|-------|---------|
| `/auth/*` | POST | 10 запросов | 5 минут |
| `/dishes` | POST | 20 запросов | 1 час |
| `/dishes` | GET | 100 запросов | 1 час |
| `/ai/analyze` | POST | 50 запросов | 1 час |

### Лимиты по тарифам

| Тариф | Запросов в день | Одновременных анализов |
|-------|-----------------|------------------------|
| Free | 50 | 1 |
| Premium | 500 | 3 |
| Pro | 5000 | 10 |

## Коды ошибок

### HTTP Status Codes
- `400` - Невалидные данные запроса
- `401` - Неавторизованный доступ
- `403` - Доступ запрещен
- `404` - Ресурс не найден
- `409` - Конфликт (пользователь уже существует)
- `413` - Файл слишком большой
- `415` - Неподдерживаемый формат файла
- `429` - Слишком много запросов
- `500` - Внутренняя ошибка сервера

### Формат ошибки
```json
{
  "error": "invalid_request",
  "message": "Невалидные данные запроса",
  "details": [
    {
      "field": "email",
      "message": "Укажите корректный email"
    }
  ]
}
```

## Примеры использования

### Полный цикл анализа блюда

1. **Создание блюда:**
```bash
curl -X POST https://api.cooking-assistant.com/v1/dishes \
  -H "Authorization: Bearer $TOKEN" \
  -F "photo=@pasta.jpg" \
  -F "user_recipe_text=Паста карбонара с беконом и пармезаном..." \
  -F "dish_type=dinner"
```

2. **Проверка статуса анализа:**
```bash
curl -X GET https://api.cooking-assistant.com/v1/dishes/dish_abc123/analysis \
  -H "Authorization: Bearer $TOKEN"
```

3. **Получение результатов:**
```bash
curl -X GET https://api.cooking-assistant.com/v1/dishes/dish_abc123 \
  -H "Authorization: Bearer $TOKEN"
```

Эта спецификация обеспечивает полное покрытие всех Use Cases приложения и готова к использованию для разработки клиентских приложений и бэкенд-системы.****
