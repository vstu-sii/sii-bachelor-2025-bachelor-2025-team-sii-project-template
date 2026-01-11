'use client'

import React, { useState, useEffect } from 'react'
import { Brain, Sparkles, Zap, Target, TrendingUp, Lightbulb } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface AIInteractionEnhancerProps {
  children: React.ReactNode
  analysisType?: 'appearance' | 'recipe' | 'nutrition' | 'general'
  showTips?: boolean
  interactiveMode?: boolean
}

export function AIInteractionEnhancer({
  children,
  analysisType = 'general',
  showTips = true,
  interactiveMode = false
}: AIInteractionEnhancerProps) {
  const [showThinking, setShowThinking] = useState(false)
  const [aiTips, setAiTips] = useState<string[]>([])
  const [interactionStep, setInteractionStep] = useState(0)
  const [userFeedback, setUserFeedback] = useState<'positive' | 'negative' | null>(null)

  useEffect(() => {
    if (interactiveMode) {
      // Симулируем "думающий" AI
      const timer = setTimeout(() => {
        setShowThinking(true)
        setTimeout(() => setShowThinking(false), 1500)
      }, 1000)

      return () => clearTimeout(timer)
    }
  }, [interactiveMode])

  useEffect(() => {
    // Генерируем советы на основе типа анализа
    const tips = generateAITips(analysisType)
    setAiTips(tips)
  }, [analysisType])

  const generateAITips = (type: string): string[] => {
    const tipsByType = {
      appearance: [
        'Сфотографируйте блюдо сверху при естественном освещении',
        'Убедитесь, что всё блюдо помещается в кадр',
        'Используйте контрастный фон для лучшей детализации',
        'Сфотографируйте с разных ракурсов для полного анализа'
      ],
      recipe: [
        'Опишите ингредиенты в порядке их использования',
        'Укажите точные пропорции для более точного анализа',
        'Добавьте информацию о времени приготовления',
        'Опишите все этапы приготовления подробно'
      ],
      nutrition: [
        'Укажите все ингредиенты для анализа питательности',
        'Добавьте информацию о способе приготовления',
        'Упомяните размер порции',
        'Отметьте если использовались диетические продукты'
      ],
      general: [
        'AI анализирует как внешний вид, так и соответствие рецепту',
        'Чем детальнее описание, тем точнее анализ',
        'Результаты включают персонализированные рекомендации',
        'Анализ занимает обычно 30-60 секунд'
      ]
    }

    return tipsByType[type as keyof typeof tipsByType] || tipsByType.general
  }

  const handleFeedback = (type: 'positive' | 'negative') => {
    setUserFeedback(type)
    
    // Анимация и логирование фидбека
    setTimeout(() => setUserFeedback(null), 2000)
    
    // В реальном приложении здесь была бы отправка фидбека на сервер
    console.log(`User feedback: ${type}`)
  }

  const handleInteraction = () => {
    if (interactiveMode) {
      setInteractionStep(prev => (prev + 1) % 3)
    }
  }

  return (
    <div className="relative">
      {/* Индикатор работы AI */}
      <AnimatePresence>
        {showThinking && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute -top-12 left-0 right-0"
          >
            <div className="flex items-center justify-center space-x-2">
              <div className="flex space-x-1">
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                    animate={{ y: [0, -4, 0] }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.1
                    }}
                  />
                ))}
              </div>
              <span className="text-sm font-medium text-purple-600">
                AI анализирует...
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Основной контент с улучшениями */}
      <motion.div
        className="relative"
        whileHover={interactiveMode ? { scale: 1.01 } : {}}
        onClick={interactiveMode ? handleInteraction : undefined}
      >
        {children}
      </motion.div>

      {/* Советы от AI */}
      {showTips && aiTips.length > 0 && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          className="mt-6"
        >
          <div className="bg-gradient-to-r from-blue-50 to-cyan-50 rounded-xl p-4 border border-blue-100">
            <div className="flex items-center mb-3">
              <Lightbulb className="h-5 w-5 text-blue-500 mr-2" />
              <h3 className="font-semibold text-blue-800">Советы от AI</h3>
            </div>
            <div className="space-y-2">
              {aiTips.map((tip, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-start"
                >
                  <Sparkles className="h-4 w-4 text-blue-400 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-blue-700">{tip}</span>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      )}

      {/* Интерактивный режим - шаги взаимодействия */}
      {interactiveMode && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Brain className="h-5 w-5 text-purple-500" />
              <span className="text-sm font-medium text-gray-700">
                Интерактивный анализ
              </span>
            </div>
            <div className="flex space-x-1">
              {[...Array(3)].map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full ${
                    index <= interactionStep
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                      : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {interactionStep >= 0 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center p-2 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg"
              >
                <Target className="h-4 w-4 text-purple-500 mr-2" />
                <span className="text-sm text-purple-700">
                  Анализирую внешний вид...
                </span>
              </motion.div>
            )}

            {interactionStep >= 1 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center p-2 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg"
              >
                <TrendingUp className="h-4 w-4 text-green-500 mr-2" />
                <span className="text-sm text-green-700">
                  Оцениваю соответствие рецепту...
                </span>
              </motion.div>
            )}

            {interactionStep >= 2 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center p-2 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg"
              >
                <Zap className="h-4 w-4 text-orange-500 mr-2" />
                <span className="text-sm text-orange-700">
                  Готовлю рекомендации...
                </span>
              </motion.div>
            )}
          </div>
        </div>
      )}

      {/* Фидбек пользователя */}
      <AnimatePresence>
        {userFeedback && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className={`fixed bottom-4 right-4 p-4 rounded-xl shadow-lg z-50 ${
              userFeedback === 'positive'
                ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                : 'bg-gradient-to-r from-red-500 to-pink-500'
            }`}
          >
            <div className="flex items-center text-white">
              {userFeedback === 'positive' ? (
                <>
                  <Sparkles className="h-5 w-5 mr-2" />
                  <span>Спасибо за фидбек! 🎉</span>
                </>
              ) : (
                <>
                  <Lightbulb className="h-5 w-5 mr-2" />
                  <span>Учту на будущее! ✨</span>
                </>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Кнопки фидбека (опционально) */}
      {interactiveMode && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-center space-x-4 mt-4"
        >
          <button
            onClick={() => handleFeedback('positive')}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Полезный анализ
          </button>
          <button
            onClick={() => handleFeedback('negative')}
            className="flex items-center px-4 py-2 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <Lightbulb className="h-4 w-4 mr-2" />
            Можно лучше
          </button>
        </motion.div>
      )}
    </div>
  )
}

// Компонент для визуализации AI процесса
export function AIProcessVisualizer({ status, progress }: { 
  status: 'idle' | 'analyzing' | 'processing' | 'complete'
  progress?: number 
}) {
  const statusConfig = {
    idle: { color: 'gray', icon: Brain, label: 'Готов к анализу' },
    analyzing: { color: 'purple', icon: Sparkles, label: 'Анализирую фото...' },
    processing: { color: 'blue', icon: Zap, label: 'Обрабатываю рецепт...' },
    complete: { color: 'green', icon: Target, label: 'Анализ завершён!' }
  }

  const config = statusConfig[status]
  const Icon = config.icon

  return (
    <div className="relative">
      {/* Анимированный фон */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-purple-100 to-pink-100 rounded-xl"
        animate={{
          background: [
            'linear-gradient(90deg, #f3e8ff 0%, #fce7f3 50%, #f3e8ff 100%)',
            'linear-gradient(90deg, #fce7f3 0%, #f3e8ff 50%, #fce7f3 100%)',
            'linear-gradient(90deg, #f3e8ff 0%, #fce7f3 50%, #f3e8ff 100%)',
          ]
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "linear"
        }}
      />

      {/* Контент */}
      <div className="relative p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <motion.div
              animate={status === 'analyzing' || status === 'processing' ? {
                rotate: 360
              } : {}}
              transition={{
                duration: 2,
                repeat: Infinity,
                ease: "linear"
              }}
            >
              <Icon className={`h-8 w-8 text-${config.color}-500`} />
            </motion.div>
            <div>
              <h3 className="font-bold text-gray-800">AI Анализ</h3>
              <p className="text-sm text-gray-600">{config.label}</p>
            </div>
          </div>

          {progress !== undefined && (
            <div className="text-right">
              <div className="text-2xl font-bold text-gray-800">
                {Math.round(progress)}%
              </div>
              <div className="text-xs text-gray-500">прогресс</div>
            </div>
          )}
        </div>

        {/* Прогресс бар */}
        {progress !== undefined && (
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div
              className={`h-full bg-gradient-to-r from-${config.color}-400 to-${config.color}-600`}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        )}

        {/* Анимационные частицы для анализа */}
        {(status === 'analyzing' || status === 'processing') && (
          <div className="absolute top-0 left-0 right-0 bottom-0 overflow-hidden rounded-xl pointer-events-none">
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full"
                initial={{
                  x: Math.random() * 100 - 50,
                  y: Math.random() * 100 - 50,
                  opacity: 0
                }}
                animate={{
                  x: [
                    Math.random() * 100 - 50,
                    Math.random() * 200 - 100,
                    Math.random() * 100 - 50
                  ],
                  y: [
                    Math.random() * 100 - 50,
                    Math.random() * 200 - 100,
                    Math.random() * 100 - 50
                  ],
                  opacity: [0, 1, 0]
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: i * 0.2
                }}
                style={{
                  left: `${20 + (i * 10)}%`,
                  top: `${30 + (i * 5)}%`
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

// Хук для управления AI взаимодействием
export function useAIInteraction() {
  const [aiState, setAiState] = useState({
    isAnalyzing: false,
    progress: 0,
    currentStep: 0,
    insights: [] as string[],
    showTips: true
  })

  const startAnalysis = async (analysisData: any) => {
    setAiState(prev => ({ ...prev, isAnalyzing: true, progress: 0 }))
    
    // Симуляция процесса анализа
    const steps = [
      { label: 'Загрузка фото', duration: 1000 },
      { label: 'Анализ внешнего вида', duration: 2000 },
      { label: 'Обработка рецепта', duration: 1500 },
      { label: 'Генерация рекомендаций', duration: 1000 }
    ]

    for (let i = 0; i < steps.length; i++) {
      setAiState(prev => ({ 
        ...prev, 
        currentStep: i,
        progress: Math.round(((i + 1) / steps.length) * 100)
      }))
      
      await new Promise(resolve => setTimeout(resolve, steps[i].duration))
    }

    setAiState(prev => ({ 
      ...prev, 
      isAnalyzing: false,
      insights: generateInsights(analysisData)
    }))
  }

  const generateInsights = (data: any): string[] => {
    return [
      'Блюдо имеет привлекательный внешний вид',
      'Пропорции ингредиентов сбалансированы',
      'Можно улучшить время приготовления',
      'Рекомендуется добавить свежие травы'
    ]
  }

  const toggleTips = () => {
    setAiState(prev => ({ ...prev, showTips: !prev.showTips }))
  }

  return {
    aiState,
    startAnalysis,
    toggleTips,
    resetAnalysis: () => setAiState({
      isAnalyzing: false,
      progress: 0,
      currentStep: 0,
      insights: [],
      showTips: true
    })
  }
}
