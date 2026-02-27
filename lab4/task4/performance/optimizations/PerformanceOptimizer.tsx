'use client'

import React, { useEffect, useState, useCallback, memo } from 'react'
import dynamic from 'next/dynamic'
import { motion, AnimatePresence } from 'framer-motion'
import { Zap, Clock, Cpu, Database, Network, Battery } from 'lucide-react'

// Динамический импорт тяжёлых компонентов
export const HeavyComponent = dynamic(
  () => import('@/components/HeavyComponent'),
  {
    loading: () => <div className="p-8 text-center">Загружаем...</div>,
    ssr: false // Не рендерить на сервере
  }
)

// Мемоизированный компонент для предотвращения лишних ререндеров
export const MemoizedCard = memo(function MemoizedCard({ 
  title, 
  content 
}: { 
  title: string, 
  content: string 
}) {
  console.log('MemoizedCard render:', title)
  
  return (
    <div className="bg-white rounded-xl p-4 shadow-sm border">
      <h3 className="font-bold text-gray-800 mb-2">{title}</h3>
      <p className="text-gray-600">{content}</p>
    </div>
  )
})

// Виртуализированный список для большого количества элементов
export function VirtualizedList<T>({
  items,
  renderItem,
  itemHeight = 60,
  overscan = 5
}: {
  items: T[]
  renderItem: (item: T, index: number) => React.ReactNode
  itemHeight: number
  overscan?: number
}) {
  const [scrollTop, setScrollTop] = useState(0)
  const containerRef = React.useRef<HTMLDivElement>(null)
  const [containerHeight, setContainerHeight] = useState(0)

  useEffect(() => {
    const updateHeight = () => {
      if (containerRef.current) {
        setContainerHeight(containerRef.current.clientHeight)
      }
    }

    updateHeight()
    window.addEventListener('resize', updateHeight)
    return () => window.removeEventListener('resize', updateHeight)
  }, [])

  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    setScrollTop(e.currentTarget.scrollTop)
  }, [])

  // Рассчитываем видимые элементы
  const totalHeight = items.length * itemHeight
  const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan)
  const endIndex = Math.min(
    items.length - 1,
    Math.floor((scrollTop + containerHeight) / itemHeight) + overscan
  )

  const visibleItems = items.slice(startIndex, endIndex + 1)
  const offsetY = startIndex * itemHeight

  return (
    <div
      ref={containerRef}
      className="overflow-auto"
      onScroll={handleScroll}
      style={{ height: '400px' }}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div
              key={startIndex + index}
              style={{ height: itemHeight }}
            >
              {renderItem(item, startIndex + index)}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Монитор производительности
export function PerformanceMonitor() {
  const [metrics, setMetrics] = useState({
    fps: 0,
    memory: 0,
    network: 'online',
    battery: 100
  })

  const [performanceLog, setPerformanceLog] = useState<Array<{
    timestamp: string
    event: string
    duration: number
  }>>([])

  useEffect(() => {
    // Мониторинг FPS
    let frameCount = 0
    let lastTime = performance.now()
    let animationFrameId: number

    const measureFPS = () => {
      const now = performance.now()
      frameCount++

      if (now - lastTime >= 1000) {
        setMetrics(prev => ({ ...prev, fps: frameCount }))
        frameCount = 0
        lastTime = now
      }

      animationFrameId = requestAnimationFrame(measureFPS)
    }

    animationFrameId = requestAnimationFrame(measureFPS)

    // Мониторинг памяти (только в браузерах с поддержкой)
    if ('memory' in performance) {
      const memoryInfo = (performance as any).memory
      const checkMemory = () => {
        if (memoryInfo) {
          const usedMB = Math.round(memoryInfo.usedJSHeapSize / 1024 / 1024)
          setMetrics(prev => ({ ...prev, memory: usedMB }))
        }
      }
      
      const memoryInterval = setInterval(checkMemory, 5000)
    }

    // Мониторинг сети
    const handleOnline = () => setMetrics(prev => ({ ...prev, network: 'online' }))
    const handleOffline = () => setMetrics(prev => ({ ...prev, network: 'offline' }))
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    // Мониторинг батареи
    if ('getBattery' in navigator) {
      ;(navigator as any).getBattery().then((battery: any) => {
        const updateBattery = () => {
          setMetrics(prev => ({ ...prev, battery: Math.round(battery.level * 100) }))
        }
        
        updateBattery()
        battery.addEventListener('levelchange', updateBattery)
      })
    }

    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Логирование производительности
  const logPerformance = useCallback((event: string, duration: number) => {
    setPerformanceLog(prev => [
      {
        timestamp: new Date().toISOString().split('T')[1].split('.')[0],
        event,
        duration: Math.round(duration)
      },
      ...prev.slice(0, 9) // Храним только последние 10 записей
    ])
  }, [])

  return (
    <div className="fixed bottom-4 right-4 z-40">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-900 text-white rounded-xl p-4 shadow-xl max-w-xs"
      >
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center space-x-2">
            <Zap className="h-5 w-5 text-yellow-400" />
            <h3 className="font-bold">Производительность</h3>
          </div>
          <div className={`px-2 py-1 rounded text-xs font-medium ${
            metrics.fps >= 50 ? 'bg-green-500' :
            metrics.fps >= 30 ? 'bg-yellow-500' : 'bg-red-500'
          }`}>
            {metrics.fps} FPS
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Cpu className="h-4 w-4 text-blue-400" />
              <span className="text-sm">Память</span>
            </div>
            <span className="text-sm font-medium">{metrics.memory} MB</span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Network className={`h-4 w-4 ${
                metrics.network === 'online' ? 'text-green-400' : 'text-red-400'
              }`} />
              <span className="text-sm">Сеть</span>
            </div>
            <span className={`text-sm font-medium ${
              metrics.network === 'online' ? 'text-green-400' : 'text-red-400'
            }`}>
              {metrics.network === 'online' ? 'Online' : 'Offline'}
            </span>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Battery className={`h-4 w-4 ${
                metrics.battery > 50 ? 'text-green-400' :
                metrics.battery > 20 ? 'text-yellow-400' : 'text-red-400'
              }`} />
              <span className="text-sm">Батарея</span>
            </div>
            <span className={`text-sm font-medium ${
              metrics.battery > 50 ? 'text-green-400' :
              metrics.battery > 20 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {metrics.battery}%
            </span>
          </div>
        </div>

        {performanceLog.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-4 w-4 text-gray-400" />
              <span className="text-sm font-medium">События</span>
            </div>
            <div className="space-y-1 max-h-32 overflow-auto">
              {performanceLog.map((log, index) => (
                <div key={index} className="flex justify-between text-xs">
                  <span className="text-gray-400">{log.timestamp}</span>
                  <span className="text-gray-300">{log.event}</span>
                  <span className={
                    log.duration > 100 ? 'text-red-400' :
                    log.duration > 50 ? 'text-yellow-400' : 'text-green-400'
                  }>
                    {log.duration}ms
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  )
}

// Оптимизация анимаций с useAnimationFrame
export function useAnimationFrame(callback: (deltaTime: number) => void) {
  const requestRef = React.useRef<number>()
  const previousTimeRef = React.useRef<number>()

  const animate = React.useCallback((time: number) => {
    if (previousTimeRef.current !== undefined) {
      const deltaTime = time - previousTimeRef.current
      callback(deltaTime)
    }
    previousTimeRef.current = time
    requestRef.current = requestAnimationFrame(animate)
  }, [callback])

  React.useEffect(() => {
    requestRef.current = requestAnimationFrame(animate)
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current)
      }
    }
  }, [animate])
}

// Ленивая загрузка компонентов с Intersection Observer
export function LazyComponent({
  children,
  threshold = 0.1,
  rootMargin = '50px'
}: {
  children: React.ReactNode
  threshold?: number
  rootMargin?: string
}) {
  const [isVisible, setIsVisible] = useState(false)
  const ref = React.useRef<HTMLDivElement>(null)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true)
          observer.unobserve(entry.target)
        }
      },
      { threshold, rootMargin }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current)
      }
    }
  }, [threshold, rootMargin])

  return (
    <div ref={ref}>
      {isVisible ? children : (
        <div className="animate-pulse bg-gray-200 rounded-lg">
          <div className="h-full min-h-[200px] flex items-center justify-center">
            <div className="text-gray-400">Загружаем...</div>
          </div>
        </div>
      )}
    </div>
  )
}

// Кэширование запросов
export function useQueryCache<T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl = 5 * 60 * 1000 // 5 минут по умолчанию
) {
  const [data, setData] = useState<T | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const fetchData = useCallback(async () => {
    // Проверяем кэш
    const cached = localStorage.getItem(`cache_${key}`)
    if (cached) {
      const { data: cachedData, timestamp } = JSON.parse(cached)
      if (Date.now() - timestamp < ttl) {
        setData(cachedData)
        return
      }
    }

    // Загружаем новые данные
    setIsLoading(true)
    setError(null)

    try {
      const result = await fetchFn()
      setData(result)
      
      // Сохраняем в кэш
      localStorage.setItem(`cache_${key}`, JSON.stringify({
        data: result,
        timestamp: Date.now()
      }))
    } catch (err) {
      setError(err as Error)
    } finally {
      setIsLoading(false)
    }
  }, [key, fetchFn, ttl])

  const invalidateCache = useCallback(() => {
    localStorage.removeItem(`cache_${key}`)
    setData(null)
  }, [key])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, isLoading, error, refetch: fetchData, invalidateCache }
}