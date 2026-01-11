'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import Header from '@/components/layout/Header'
import Navigation from '@/components/layout/Navigation'
import { Camera, Upload, FileText, Send, ArrowLeft, CheckCircle } from 'lucide-react'
import { useApp } from '@/contexts/AppContext'
import toast from 'react-hot-toast'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

type DishType = 'breakfast' | 'lunch' | 'dinner' | 'dessert' | 'baking' | 'other'

export default function NewDishPage() {
  const router = useRouter()
  const { createDish, analyzeDish, isLoading } = useApp()
  
  const [step, setStep] = useState(1)
  const [photo, setPhoto] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [recipe, setRecipe] = useState('')
  const [dishType, setDishType] = useState<DishType>('other')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [createdDishId, setCreatedDishId] = useState<number | null>(null)
  const [analysisStarted, setAnalysisStarted] = useState(false)

  const handlePhotoUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        toast.error('Файл слишком большой. Максимальный размер: 10MB')
        return
      }

      if (!file.type.startsWith('image/')) {
        toast.error('Пожалуйста, выберите файл изображения')
        return
      }

      setPhoto(file)
      
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
      
      setStep(2)
      toast.success('Фото загружено! Теперь опишите рецепт')
    }
  }, [])

  const handleSubmit = useCallback(async () => {
    if (!photo || recipe.length < 50) {
      toast.error('Загрузите фото и опишите рецепт (минимум 50 символов)')
      return
    }

    setIsSubmitting(true)
    
    try {
      const formData = new FormData()
      formData.append('photo', photo)
      formData.append('dish_type', dishType)
      formData.append('user_recipe_text', recipe)

      toast.loading('Создаём блюдо...')
      const dish = await createDish(formData)
      
      toast.dismiss()
      toast.success('Блюдо успешно создано!')
      
      setCreatedDishId(dish.id)
      setStep(3)
    } catch (error: any) {
      toast.dismiss()
      toast.error(error.message || 'Не удалось создать блюдо')
    } finally {
      setIsSubmitting(false)
    }
  }, [photo, recipe, dishType, createDish])

  const handleStartAnalysis = useCallback(async () => {
    if (!createdDishId) return

    setAnalysisStarted(true)
    
    try {
      toast.loading('Запускаем AI анализ...')
      await analyzeDish(createdDishId)
      
      toast.dismiss()
      toast.success('Анализ запущен! Результаты будут готовы через несколько секунд')
      
      setTimeout(() => {
        router.push(`/dishes/${createdDishId}`)
      }, 2000)
    } catch (error: any) {
      toast.dismiss()
      toast.error(error.message || 'Не удалось запустить анализ')
      setAnalysisStarted(false)
    }
  }, [createdDishId, analyzeDish, router])

  const dishTypes: { value: DishType; label: string; icon: string }[] = [
    { value: 'breakfast', label: 'Завтрак', icon: '🥞' },
    { value: 'lunch', label: 'Обед', icon: '🍲' },
    { value: 'dinner', label: 'Ужин', icon: '🍝' },
    { value: 'dessert', label: 'Десерт', icon: '🍰' },
    { value: 'baking', label: 'Выпечка', icon: '🥖' },
    { value: 'other', label: 'Другое', icon: '🍽️' },
  ]

  return (
    <main className="min-h-screen bg-gray-50 pb-16">
      <Header title="Новое блюдо" />
      
      <div className="p-4 max-w-4xl mx-auto">
        {/* Шаги */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <button
              onClick={() => step > 1 ? setStep(step - 1) : router.back()}
              className="flex items-center text-gray-600 hover:text-gray-800"
            >
              <ArrowLeft className="h-5 w-5 mr-1" />
              Назад
            </button>
            <div className="text-sm font-medium text-gray-700">
              Шаг {step} из 3
            </div>
          </div>
          
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-orange-500 to-yellow-500 transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            />
          </div>
          
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>Фото</span>
            <span>Рецепт</span>
            <span>Готово</span>
          </div>
        </div>

        {/* Шаг 1: Загрузка фото */}
        {step === 1 && (
          <Card className="text-center" padding="lg">
            <div className="mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Сфотографируйте ваше блюдо
              </h2>
              <p className="text-gray-600">
                Убедитесь, что фото хорошо освещено и блюдо полностью видно
              </p>
            </div>

            <div className="relative mb-8">
              <div className="aspect-square max-w-md mx-auto bg-gradient-to-br from-orange-50 to-yellow-50 rounded-2xl border-3 border-dashed border-orange-200 flex flex-col items-center justify-center p-8">
                <Camera className="h-20 w-20 text-orange-400 mb-4" />
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                  Добавьте фото
                </h3>
                <p className="text-gray-600 mb-6 text-center">
                  Используйте камеру или загрузите существующее фото
                </p>
                
                <div className="space-y-3 w-full max-w-xs">
                  <label className="block">
                    <input
                      type="file"
                      accept="image/*"
                      capture="environment"
                      className="hidden"
                      onChange={handlePhotoUpload}
                      disabled={isLoading}
                    />
                    <Button
                      variant="primary"
                      fullWidth
                      icon={<Camera className="h-5 w-5" />}
                      disabled={isLoading}
                    >
                      Сделать фото
                    </Button>
                  </label>
                  
                  <label className="block">
                    <input
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={handlePhotoUpload}
                      disabled={isLoading}
                    />
                    <Button
                      variant="outline"
                      fullWidth
                      icon={<Upload className="h-5 w-5" />}
                      disabled={isLoading}
                    >
                      Загрузить фото
                    </Button>
                  </label>
                </div>
              </div>
            </div>

            <div className="text-sm text-gray-500 space-y-1">
              <p>📸 Совет: Сфотографируйте блюдо сверху при естественном освещении</p>
              <p>�� Максимальный размер файла: 10MB</p>
              <p>🖼️ Поддерживаемые форматы: JPG, PNG, WebP</p>
            </div>
          </Card>
        )}

        {/* Шаг 2: Ввод рецепта */}
        {step === 2 && (
          <div className="space-y-6">
            {/* Предпросмотр фото */}
            {preview && (
              <Card>
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-gray-800">Ваше фото</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setPhoto(null)
                      setPreview(null)
                      setStep(1)
                    }}
                  >
                    Изменить
                  </Button>
                </div>
                <div className="relative aspect-video rounded-xl overflow-hidden">
                  <img 
                    src={preview} 
                    alt="Загруженное блюдо" 
                    className="w-full h-full object-cover"
                  />
                </div>
              </Card>
            )}

            {/* Выбор типа блюда */}
            <Card>
              <h3 className="font-semibold text-gray-800 mb-4">Тип блюда</h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                {dishTypes.map((type) => (
                  <button
                    key={type.value}
                    onClick={() => setDishType(type.value)}
                    className={`p-4 rounded-xl border-2 flex flex-col items-center justify-center transition-all ${
                      dishType === type.value
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <span className="text-2xl mb-2">{type.icon}</span>
                    <span className="font-medium text-gray-800">{type.label}</span>
                  </button>
                ))}
              </div>
            </Card>

            {/* Поле для рецепта */}
            <Card>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <div className="flex items-center space-x-2">
                    <FileText className="h-5 w-5" />
                    <span>Рецепт блюда</span>
                  </div>
                </label>
                <textarea
                  value={recipe}
                  onChange={(e) => setRecipe(e.target.value)}
                  placeholder="Опишите ингредиенты и шаги приготовления. Например:
• Ингредиенты: 200г пасты, 100г бекона, 2 яйца, 50г пармезана
• Шаги: 1. Варим пасту al dente 2. Обжариваем бекон..."
                  className="w-full h-64 p-4 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                  disabled={isSubmitting}
                />
                <div className="flex justify-between items-center mt-2">
                  <div className="text-sm text-gray-500">
                    Минимум 50 символов
                  </div>
                  <div className={`text-sm ${
                    recipe.length < 50 ? 'text-red-500' : 'text-green-500'
                  }`}>
                    {recipe.length}/2000 символов
                  </div>
                </div>
              </div>

              <Button
                onClick={handleSubmit}
                disabled={recipe.length < 50 || isSubmitting}
                variant="primary"
                fullWidth
                size="lg"
                isLoading={isSubmitting}
                icon={<Send className="h-5 w-5" />}
              >
                {isSubmitting ? 'Создаём блюдо...' : 'Создать блюдо'}
              </Button>
            </Card>
          </div>
        )}

        {/* Шаг 3: Успешное создание */}
        {step === 3 && createdDishId && (
          <Card className="text-center" padding="lg">
            <div className="mb-8">
              <div className="h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Блюдо успешно создано! 🎉
              </h2>
              <p className="text-gray-600">
                Теперь вы можете запустить AI анализ или перейти к другим действиям
              </p>
            </div>

            <div className="space-y-4 mb-8">
              <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl p-6">
                <h3 className="font-semibold text-gray-800 mb-2">🤖 AI Анализ</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Проанализируйте ваше блюдо с помощью искусственного интеллекта
                </p>
                <Button
                  onClick={handleStartAnalysis}
                  variant="primary"
                  fullWidth
                  isLoading={analysisStarted}
                  disabled={analysisStarted}
                >
                  {analysisStarted ? 'Запускаем анализ...' : 'Запустить AI анализ'}
                </Button>
              </div>

              <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl p-6">
                <h3 className="font-semibold text-gray-800 mb-2">📊 Просмотр блюда</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Перейти к детальной информации о блюде
                </p>
                <Button
                  onClick={() => router.push(`/dishes/${createdDishId}`)}
                  variant="outline"
                  fullWidth
                >
                  Перейти к блюду
                </Button>
              </div>

              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6">
                <h3 className="font-semibold text-gray-800 mb-2">➕ Новое блюдо</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Создать ещё одно блюдо
                </p>
                <Button
                  onClick={() => {
                    setPhoto(null)
                    setPreview(null)
                    setRecipe('')
                    setDishType('other')
                    setCreatedDishId(null)
                    setStep(1)
                  }}
                  variant="outline"
                  fullWidth
                >
                  Создать новое блюдо
                </Button>
              </div>
            </div>

            <div className="text-sm text-gray-500">
              <p>📝 Рецепт сохранён и готов к анализу</p>
              <p>🕒 AI анализ занимает обычно 30-60 секунд</p>
              <p>📱 Вы можете закрыть эту страницу - мы уведомим вас о результатах</p>
            </div>
          </Card>
        )}

        {/* Общий loading state */}
        {(isLoading || isSubmitting) && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-2xl p-8 flex flex-col items-center">
              <LoadingSpinner size="lg" />
              <p className="mt-4 text-gray-700 font-medium">
                {isSubmitting ? 'Создаём ваше блюдо...' : 'Загружаем...'}
              </p>
            </div>
          </div>
        )}
      </div>

      <Navigation />
    </main>
  )
}
