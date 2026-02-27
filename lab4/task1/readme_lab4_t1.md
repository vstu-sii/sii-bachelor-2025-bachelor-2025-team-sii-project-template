cat > task1/README.md << 'EOF'
# Задание 1: Frontend + Backend интеграция

## 🎯 Цель
Создать полнофункциональное приложение Cooking Assistant с полной интеграцией фронтенда (Next.js) и бэкенда (FastAPI).

## ✅ Выполненные задачи

### 1. Полная реализация всех use-cases
- **Регистрация/авторизация** пользователей
- **Загрузка фото блюд** с предпросмотром и валидацией
- **Создание блюд** с описанием рецептов (3-шаговый процесс)
- **AI анализ блюд** (mock сервис с реалистичными данными)
- **Просмотр истории** блюд с фильтрацией и поиском
- **Статистика** и прогресс пользователя

### 2. Связка React ↔ FastAPI
- **API клиент на Axios** с интерцепторами для авторизации и обработки ошибок
- **React контексты** для управления состоянием (AuthContext, AppContext)
- **TypeScript типизация** для всех компонентов и API
- **Маршрутизация Next.js** с App Router
- **CORS настройка** для взаимодействия фронтенда и бэкенда

### 3. Обработка loading/error states
- **Loading спиннеры** для всех асинхронных операций
- **Error boundaries** в React компонентах
- **Toast уведомления** для пользовательской обратной связи
- **Валидация форм** в реальном времени
- **Обработка ошибок API** с user-friendly сообщениями

### 4. Responsive дизайн доработка
- **Адаптивная сетка** Tailwind CSS для мобильных устройств
- **Bottom navigation** для мобильного приложения
- **Оптимизированные компоненты** под разные экраны
- **Плавные анимации** и переходы
- **Кастомные UI компоненты** (Button, Card, LoadingSpinner)

## 🏗️ Архитектура

### Frontend (Next.js 14)
frontend/
├── src/app/ # Страницы App Router
│ ├── page.tsx # Главная страница
│ ├── new-dish/page.tsx # Создание блюда
│ ├── history/page.tsx # История блюд
│ └── layout.tsx # Главный layout
├── src/components/ # React компоненты
│ ├── layout/ # Header, Navigation
│ └── ui/ # Button, Card, LoadingSpinner
├── src/contexts/ # React контексты
│ ├── AuthContext.tsx # Аутентификация
│ └── AppContext.tsx # Состояние приложения
├── src/lib/ # Утилиты
│ └── api.ts # API клиент
└── src/types/ # TypeScript типы
text


### Backend (FastAPI)

backend/
├── api/ # FastAPI роутеры
│ ├── routes/ # Эндпоинты (auth, dishes, statistics)
│ └── dependencies/ # Зависимости (авторизация)
├── models/ # SQLAlchemy модели
├── schemas/ # Pydantic схемы
├── crud/ # CRUD операции
├── services/ # Бизнес-логика (AI сервис)
├── database.py # Подключение к БД
└── main.py # Точка входа
text


## 🚀 Запуск проекта

### Frontend:
```bash
cd frontend
npm install
npm run dev
# Открыть http://localhost:3000