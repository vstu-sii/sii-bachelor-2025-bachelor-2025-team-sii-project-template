'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import Header from '@/components/layout/Header'
import Navigation from '@/components/layout/Navigation'
import { PlusCircle, History, BarChart, ChefHat, TrendingUp, AlertCircle } from 'lucide-react'
import { useApp } from '@/contexts/AppContext'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function Home() {
  const { dishes, fetchDishes, isLoading: dishesLoading } = useApp()
  const [recentDishes, setRecentDishes] = useState<any[]>([])

  useEffect(() => {
    fetchDishes({ limit: 5, status: 'ready' })
  }, [fetchDishes])

  useEffect(() => {
    if (dishes.length > 0) {
      setRecentDishes(dishes.slice(0, 3).map(dish => ({
        name: `Блюдо #${dish.id}`,
        date: new Date(dish.created_at).toLocaleDateString('ru-RU'),
        scores: `${dish.rating?.appearance_score || '?'}/${dish.rating?.recipe_score || '?'}`,
        dish,
      })))
    }
  }, [dishes])

  const quickActions = [
    { 
      icon: PlusCircle, 
      title: 'Новое блюдо', 
      description: 'Проанализировать приготовленное блюдо', 
      href: '/new-dish', 
      color: 'bg-orange-500' 
    },
    { 
      icon: History, 
      title: 'История', 
      description: 'Просмотр всех ваших блюд', 
      href: '/history', 
      color: 'bg-blue-500' 
    },
    { 
      icon: BarChart, 
      title: 'Статистика', 
      description: 'Ваш прогресс в готовке', 
      href: '/statistics', 
      color: 'bg-green-500' 
    },
  ]

  if (dishesLoading) {
    return (
      <main className="min-h-screen bg-gray-50 pb-16">
        <Header />
        <div className="p-4 flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
        <Navigation />
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50 pb-16">
      <Header />
      
      <div className="p-4 max-w-4xl mx-auto">
        {/* Приветствие */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-2">
            Добро пожаловать, Шеф! 👨‍🍳
          </h2>
          <p className="text-gray-600">
            {dishes.length > 0 
              ? `У вас ${dishes.length} блюд в истории. Продолжайте совершенствоваться!`
              : 'Начните свой кулинарный путь с первого блюда!'}
          </p>
        </div>

        {/* Быстрые действия */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">
            Быстрые действия
          </h3>
          <div className="grid grid-cols-1 gap-4">
            {quickActions.map((action) => (
              <Link key={action.title} href={action.href}>
                <Card hover className="flex items-center space-x-4 p-4">
                  <div className={`${action.color} p-3 rounded-lg`}>
                    <action.icon className="h-6 w-6 text-white" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-800">{action.title}</h4>
                    <p className="text-sm text-gray-600">{action.description}</p>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        </div>

        {/* Последние блюда */}
        {recentDishes.length > 0 && (
          <div className="mb-8">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-800">
                Последние блюда
              </h3>
              <Link 
                href="/history" 
                className="text-sm text-orange-500 font-medium hover:text-orange-600"
              >
                Вся история →
              </Link>
            </div>
            <div className="space-y-3">
              {recentDishes.map((item, index) => (
                <Link key={index} href={`/dishes/${item.dish.id}`}>
                  <Card hover className="p-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <h4 className="font-medium text-gray-800">{item.name}</h4>
                        <p className="text-sm text-gray-500">{item.date}</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="text-right">
                          <div className="font-bold text-gray-800">{item.scores}</div>
                          <div className="text-xs text-gray-500">оценка</div>
                        </div>
                        <ChefHat className="h-5 w-5 text-orange-500" />
                      </div>
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Статистика */}
        {dishes.length > 0 && (
          <div className="bg-gradient-to-r from-orange-500 to-yellow-500 rounded-2xl p-6 text-white mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold">Ваш прогресс</h3>
                <p className="text-orange-100">
                  {dishes.length} блюд приготовлено
                </p>
              </div>
              <TrendingUp className="h-8 w-8" />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{dishes.length}</div>
                <div className="text-xs opacity-90">блюда</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {dishes.filter(d => d.rating).length > 0 
                    ? (dishes.reduce((acc, d) => acc + (d.rating?.appearance_score || 0), 0) / dishes.filter(d => d.rating).length).toFixed(1)
                    : '0.0'}
                </div>
                <div className="text-xs opacity-90">средняя</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {new Set(dishes.map(d => new Date(d.created_at).toDateString())).size}
                </div>
                <div className="text-xs opacity-90">дней</div>
              </div>
            </div>
          </div>
        )}

        {/* Нет блюд */}
        {dishes.length === 0 && !dishesLoading && (
          <Card className="text-center p-8">
            <div className="h-16 w-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ChefHat className="h-8 w-8 text-orange-500" />
            </div>
            <h3 className="text-lg font-semibold text-gray-800 mb-2">
              У вас ещё нет блюд
            </h3>
            <p className="text-gray-600 mb-6">
              Начните с создания первого блюда, чтобы получить AI анализ и рекомендации
            </p>
            <Link href="/new-dish">
              <Button variant="primary" icon={<PlusCircle className="h-5 w-5" />}>
                Создать первое блюдо
              </Button>
            </Link>
          </Card>
        )}

        {/* Советы */}
        <Card className="mt-8">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-semibold text-gray-800 mb-2">Советы для начала</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Используйте хорошее освещение при фотографировании блюд</li>
                <li>• Подробно описывайте рецепт для более точного анализа</li>
                <li>• Регулярно проверяйте статистику для отслеживания прогресса</li>
                <li>• Экспериментируйте с разными типами блюд</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>

      <Navigation />
    </main>
  )
}
