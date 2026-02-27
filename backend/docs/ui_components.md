## Компонентная архитектура UI
https://www.figma.com/design/3X6radG5GO2qBrfiddx1hv/cooking_assistant?node-id=0-1&t=nn1xOuOE6scHLKC4-1
### 1. Анализ экранов из Figma

На основе макетов идентифицирую следующие основные экраны:
- **Главная** (навигация: Новое блюдо, История, Готовятся, Оценка, Статистика)
- **Новое блюдо** → **Камера** → **Ввод рецепта** → **Результат анализа**
- **Профиль**
- **Авторизация** → **Регистрация** → **Подтверждение почты**
- **Статистика по типам блюд**
- **История готовок**

### 2. Компонентная структура

#### **Atomic Design подход:**

**Atoms (Базовые компоненты):**
```typescript
- Button (кнопки: основная, второстепенная, текстовая)
- Input (текстовые поля с валидацией)
- ScoreBadge (бейдж оценки 8/10)
- CameraView (компонент камеры)
- Avatar (аватар пользователя)
- Icon (иконки навигации)
- ProgressBar (индикатор загрузки)
- TabBar (нижняя навигация)
```

**Molecules (Группы атомов):**
```typescript
- NavigationTab (вкладка навигации с иконкой и текстом)
- DishCard (карточка блюда: фото + название + дата + оценки)
- ScoreDisplay (отображение парных оценок: внешний вид/рецепт)
- StatisticsCard (карточка статистики по типу блюда)
- RecipeForm (форма ввода рецепта с текстовым полем)
- AuthForm (группа полей для авторизации)
```

**Organisms (Сложные компоненты):**
```typescript
- Header (шапка с заголовком и действиями)
- DishGallery (галерея карточек блюд)
- StatisticsOverview (сводка статистики по всем типам блюд)
- CameraScreen (полноэкранный компонент камеры с контролами)
- AnalysisResult (экран результатов анализа с оценками и рекомендациями)
- ProfileSection (секция профиля с данными пользователя)
```

**Templates (Шаблоны экранов):**
```typescript
- MainLayout (основной шаблон с нижней навигацией)
- AuthLayout (шаблон для авторизации без навигации)
- ModalLayout (шаблон для модальных окон)
```

### 3. Иерархия компонентов

```
App
├── Router
│   ├── MainLayout (с TabBar)
│   │   ├── HomeScreen
│   │   │   ├── Header
│   │   │   ├── NavigationGrid
│   │   │   │   └── NavigationTab[5]
│   │   │   └── QuickStats
│   │   ├── NewDishFlow
│   │   │   ├── CameraScreen
│   │   │   │   ├── CameraView
│   │   │   │   └── CameraControls
│   │   │   ├── RecipeFormScreen
│   │   │   │   └── RecipeForm
│   │   │   └── AnalysisScreen
│   │   │       ├── ScoreDisplay
│   │   │       ├── AnalysisComments
│   │   │       └── Recommendations
│   │   ├── HistoryScreen
│   │   │   ├── FilterBar
│   │   │   └── DishGallery
│   │   │       └── DishCard[]
│   │   ├── CookingScreen
│   │   │   └── CookingList
│   │   │       └── CookingCard[]
│   │   ├── RatingsScreen
│   │   │   └── RatedDishes
│   │   │       └── DishCard[]
│   │   └── StatisticsScreen
│   │       ├── StatisticsOverview
│   │       │   └── StatisticsCard[]
│   │       └── DishTypeStatistics
│   ├── AuthLayout
│   │   ├── LoginScreen
│   │   │   └── AuthForm
│   │   ├── RegisterScreen
│   │   │   └── AuthForm
│   │   └── VerificationScreen
│   └── ProfileLayout
│       └── ProfileScreen
│           ├── UserInfo
│           ├── StatsSummary
│           └── SettingsSection
```

### 4. Состояние (State Management)

**Global State (Redux/Zustand):**
```typescript
interface AppState {
  auth: {
    user: User | null
    isAuthenticated: boolean
    isLoading: boolean
  }
  dishes: {
    items: Dish[]
    currentDish: Dish | null
    cooking: Dish[]
    history: Dish[]
    isLoading: boolean
  }
  camera: {
    isActive: boolean
    currentPhoto: string | null
  }
  analysis: {
    isAnalyzing: boolean
    currentResult: AnalysisResult | null
  }
  statistics: {
    overview: Statistics
    byDishType: Record<string, DishTypeStats>
  }
}
```

**Local Component States:**
- `RecipeForm`: текущий текст рецепта, валидация
- `CameraScreen`: состояние камеры, пермишены
- `FilterBar`: выбранные фильтры для истории
- `AuthForm`: данные формы, ошибки валидации

### 5. Навигация

**Tab Navigator (основной):**
```
Home → NewDish → History → Cooking → Ratings → Statistics
```

**Stack Navigators:**
```
NewDishStack:
  Camera → RecipeForm → AnalysisResult

AuthStack:
  Login → Register → EmailVerification

ProfileStack:
  Profile → EditProfile → DishTypeStatistics
```

### 6. Props Interfaces

```typescript
// Базовые интерфейсы
interface Dish {
  id: string
  name: string
  photoUrl: string
  dishType: string
  userRecipeText: string
  createdAt: Date
  status: 'draft' | 'processing' | 'ready'
}

interface AnalysisResult {
  appearanceScore: number
  recipeScore: number
  appearanceFeedback: string
  recipeFeedback: string
  recommendations: string
}

// Пропсы компонентов
interface DishCardProps {
  dish: Dish
  onPress?: (dish: Dish) => void
  showScores?: boolean
}

interface ScoreDisplayProps {
  appearanceScore: number
  recipeScore: number
  size?: 'small' | 'medium' | 'large'
}

interface CameraScreenProps {
  onPhotoTaken: (photoUri: string) => void
  onCancel: () => void
}
```

### 7. Ключевые пользовательские потоки

**Flow 1: Добавление нового блюда**
```
User → MainLayout → NewDishFlow → CameraScreen (фото) 
→ RecipeFormScreen (рецепт) → AnalysisScreen (результат)
→ автоматически в History
```

**Flow 2: Просмотр статистики**
```
User → MainLayout → StatisticsScreen → StatisticsOverview
→ Tap on dish type → DishTypeStatistics (детальная статистика)
```

**Flow 3: Работа с профилем**
```
User → ProfileIcon → ProfileScreen → EditProfile
→ Save changes → Back to Profile
```
