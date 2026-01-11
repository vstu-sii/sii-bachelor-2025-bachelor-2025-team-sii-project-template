'use client'

import { useState, useEffect } from 'react'
import Header from '@/components/layout/Header'
import Navigation from '@/components/layout/Navigation'
import { Filter, Search, ChefHat, Calendar, Star, MessageSquare } from 'lucide-react'
import { useApp } from '@/contexts/AppContext'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import LoadingSpinner from '@/components/ui/LoadingSpinner'

export default function HistoryPage() {
  const { dishes, fetchDishes, isLoading } = useApp()
  const [filter, setFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [filteredDishes, setFilteredDishes] = useState(dishes)

  useEffect(() => {
    fetchDishes()
  }, [fetchDishes])

  useEffect(() => {
    let result = dishes
    
    if (filter !== 'all') {
      result = result.filter(dish => dish.dish_type === filter)
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(dish => 
        dish.user_recipe_text.toLowerCase().includes(query) ||
        dish.dish_type.toLowerCase().includes(query)
      )
    }
    
    setFilteredDishes(result)
  }, [dishes, filter, searchQuery])

  const dishTypes = [
    { value: 'all', label: 'Все', count: dishes.length },
    { value: 'breakfast', label: 'Завтраки', count: dishes.filter(d => d.dish_type === 'breakfast').length },
    { value: 'lunch', label: 'Обеды', count: dishes.filter(d => d.dish_type === 'lunch').length },
    { value: 'dinner', label: 'Ужины', count: dishes.filter(d => d.dish_type === 'dinner').length },
    { value: 'dessert', label: 'Десерты', count: dishes.filter(d => d.dish_type === 'dessert').length },
  ]

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 pb-16">
        <Header title="История блюд" />
        <div className="p-4 flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
        <Navigation />
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50 pb-16">
      <Header title="История блюд" />
      
      <div className="p-4 max-w-4xl mx-auto">
        {/* Поиск и фильтры */}
        <Card className="mb-6">
          <div className="mb-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по рецептам..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex flex-wrap gap-2">
            {dishTypes.map((type) => (
              <button
                key={type.value}
                onClick={() => setFilter(type.value)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  filter === type.value
                    ? 'bg-orange-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type.label}
                <span className="ml-2 bg-white bg-opacity-20 px-2 py-0.5 rounded-full text-xs">
                  {type.count}
                </span>
              </button>
            ))}
          </div>
        </Card>

        {/* Результаты */}
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-800">
              Всего блюд: {filteredDishes.length}
            </h2>
            <Button
              variant="outline"
              size="sm"
              icon={<Filter className="h-4 w-4" />}
            >
              Сортировка
            </Button>
          </div>

          {filteredDishes.length === 0 ? (
            <Card className="text-center p-8">
              <div className="h-16 w-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <ChefHat className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">
                Блюд не найдено
              </h3>
              <p className="text-gray-600">
                {searchQuery
                  ? 'Попробуйте изменить поисковый запрос'
                  : 'Создайте первое блюдо чтобы начать историю'}
              </p>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredDishes.map((dish) => (
                <Card key={dish.id} hover className="p-4">
                  <div className="flex flex-col sm:flex-row sm:items-start gap-4">
                    {/* Фото */}
                    <div className="flex-shrink-0">
                      <div className="h-32 w-32 rounded-lg overflow-hidden bg-gray-100">
                        {dish.photo_url ? (
                          <img
                            src={dish.photo_url}
                            alt={dish.dish_type}
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div className="h-full w-full flex items-center justify-center">
                            <ChefHat className="h-12 w-12 text-gray-400" />
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Информация */}
                    <div className="flex-1">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-bold text-gray-800">
                            Блюдо #{dish.id}
                          </h3>
                          <div className="flex items-center text-sm text-gray-500 mt-1">
                            <Calendar className="h-3 w-3 mr-1" />
                            {new Date(dish.created_at).toLocaleDateString('ru-RU')}
                            <span className="mx-2">•</span>
                            <ChefHat className="h-3 w-3 mr-1" />
                            <span className="capitalize">{dish.dish_type}</span>
                          </div>
                        </div>
                        
                        <div className="text-right">
                          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                            dish.status === 'ready' ? 'bg-green-100 text-green-800' :
                            dish.status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {dish.status === 'ready' ? 'Проанализировано' :
                             dish.status === 'processing' ? 'В обработке' : 'Черновик'}
                          </div>
                        </div>
                      </div>

                      {/* Оценки */}
                      {dish.rating && (
                        <div className="mt-4 grid grid-cols-2 gap-4">
                          <div className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-gray-700">
                                Внешний вид
                              </span>
                              <div className="flex items-center">
                                <Star className="h-4 w-4 text-yellow-500 fill-current" />
                                <span className="ml-1 font-bold">
                                  {dish.rating.appearance_score}/5
                                </span>
                              </div>
                            </div>
                            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-orange-400 to-yellow-400"
                                style={{ width: `${(dish.rating.appearance_score / 5) * 100}%` }}
                              />
                            </div>
                          </div>
                          
                          <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-3">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-sm font-medium text-gray-700">
                                Рецепт
                              </span>
                              <div className="flex items-center">
                                <Star className="h-4 w-4 text-green-500 fill-current" />
                                <span className="ml-1 font-bold">
                                  {dish.rating.recipe_score}/5
                                </span>
                              </div>
                            </div>
                            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-green-400 to-emerald-400"
                                style={{ width: `${(dish.rating.recipe_score / 5) * 100}%` }}
                              />
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Действия */}
                      <div className="mt-4 flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => window.location.href = `/dishes/${dish.id}`}
                        >
                          Подробнее
                        </Button>
                        {dish.status === 'ready' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            icon={<MessageSquare className="h-4 w-4" />}
                          >
                            Рекомендации
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      <Navigation />
    </main>
  )
}
