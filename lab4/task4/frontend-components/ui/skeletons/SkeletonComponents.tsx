'use client'

import React from 'react'
import { motion } from 'framer-motion'

// Базовый скелетон
export function Skeleton({
  className = '',
  animated = true,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  animated?: boolean
}) {
  return (
    <motion.div
      className={`bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded ${className}`}
      animate={animated ? {
        backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
      } : {}}
      transition={{
        duration: 2,
        repeat: Infinity,
        ease: "linear"
      }}
      style={{
        backgroundSize: '200% 100%'
      }}
      {...props}
    />
  )
}

// Скелетон карточки блюда
export function DishCardSkeleton() {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div className="space-y-3">
        {/* Изображение */}
        <Skeleton className="h-48 rounded-lg" />
        
        {/* Заголовок */}
        <div className="space-y-2">
          <Skeleton className="h-4 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
        
        {/* Оценки */}
        <div className="flex space-x-2">
          <Skeleton className="h-3 flex-1" />
          <Skeleton className="h-3 flex-1" />
        </div>
        
        {/* Кнопки */}
        <div className="flex space-x-2 pt-2">
          <Skeleton className="h-8 flex-1 rounded" />
          <Skeleton className="h-8 w-8 rounded" />
        </div>
      </div>
    </div>
  )
}

// Скелетон списка блюд
export function DishListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {[...Array(count)].map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <DishCardSkeleton />
        </motion.div>
      ))}
    </div>
  )
}

// Скелетон страницы создания блюда
export function NewDishPageSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Шаги */}
      <div className="space-y-2">
        <Skeleton className="h-2 rounded-full" />
        <div className="flex justify-between">
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-16" />
          <Skeleton className="h-3 w-16" />
        </div>
      </div>
      
      {/* Загрузка фото */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-64 rounded-2xl" />
        <div className="flex space-x-3">
          <Skeleton className="h-10 flex-1 rounded-lg" />
          <Skeleton className="h-10 flex-1 rounded-lg" />
        </div>
      </div>
      
      {/* Рецепт */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-40 rounded-xl" />
      </div>
      
      {/* Тип блюда */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-40" />
        <div className="grid grid-cols-3 gap-3">
          {[...Array(6)].map((_, i) => (
            <Skeleton key={i} className="h-16 rounded-xl" />
          ))}
        </div>
      </div>
      
      {/* Кнопка отправки */}
      <Skeleton className="h-12 rounded-lg" />
    </div>
  )
}

// Скелетон AI анализа
export function AIAnalysisSkeleton() {
  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="text-center">
        <Skeleton className="h-8 w-64 mx-auto" />
        <Skeleton className="h-4 w-48 mx-auto mt-2" />
      </div>
      
      {/* Визуализация процесса */}
      <div className="relative">
        <Skeleton className="h-32 rounded-xl" />
        
        {/* Анимированные элементы */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="flex space-x-2">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="w-2 h-2 bg-white rounded-full"
                animate={{
                  y: [0, -6, 0]
                }}
                transition={{
                  duration: 0.6,
                  repeat: Infinity,
                  delay: i * 0.1
                }}
              />
            ))}
          </div>
        </div>
      </div>
      
      {/* Прогресс бар */}
      <div className="space-y-2">
        <div className="flex justify-between">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-4 w-12" />
        </div>
        <Skeleton className="h-2 rounded-full" />
      </div>
      
      {/* Этапы анализа */}
      <div className="space-y-3">
        {['Анализ фото', 'Обработка рецепта', 'Генерация рекомендаций'].map((step, i) => (
          <div key={i} className="flex items-center space-x-3">
            <Skeleton className="h-8 w-8 rounded-full" />
            <Skeleton className="h-4 flex-1" />
          </div>
        ))}
      </div>
    </div>
  )
}

// Скелетон статистики
export function StatisticsSkeleton() {
  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div>
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64 mt-2" />
      </div>
      
      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="space-y-3">
            <Skeleton className="h-32 rounded-xl" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-3 w-1/2" />
          </div>
        ))}
      </div>
      
      {/* Графики */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-64 rounded-xl" />
      </div>
      
      {/* Список достижений */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-40" />
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-center space-x-3">
              <Skeleton className="h-10 w-10 rounded-lg" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-2 w-full" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Скелетон профиля пользователя
export function ProfileSkeleton() {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Аватар и информация */}
      <div className="flex items-center space-x-4">
        <Skeleton className="h-20 w-20 rounded-full" />
        <div className="space-y-2">
          <Skeleton className="h-6 w-48" />
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-24" />
        </div>
      </div>
      
      {/* Статистика профиля */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="text-center space-y-2">
            <Skeleton className="h-12 w-12 rounded-lg mx-auto" />
            <Skeleton className="h-4 w-16 mx-auto" />
            <Skeleton className="h-3 w-12 mx-auto" />
          </div>
        ))}
      </div>
      
      {/* Настройки */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3 border rounded-lg">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-6 w-12 rounded" />
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Хук для управления скелетонами
export function useSkeleton(showSkeleton: boolean, content: React.ReactNode) {
  if (showSkeleton) {
    return <DishListSkeleton />
  }
  
  return content
}

// Компонент для плавного перехода от скелетона к контенту
export function SkeletonTransition({
  isLoading,
  skeleton,
  children
}: {
  isLoading: boolean
  skeleton: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <div className="relative">
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="skeleton"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {skeleton}
          </motion.div>
        ) : (
          <motion.div
            key="content"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}