'use client'

import React, { useState, useEffect, useRef } from 'react'
import Image, { ImageProps } from 'next/image'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader2, Image as ImageIcon, AlertCircle } from 'lucide-react'

interface OptimizedImageProps extends Omit<ImageProps, 'onLoadingComplete'> {
  placeholderSrc?: string
  showLoading?: boolean
  lazyLoad?: boolean
  priority?: boolean
  quality?: number
  onLoad?: () => void
  onError?: () => void
}

export function OptimizedImage({
  src,
  alt,
  placeholderSrc = '/images/placeholder.jpg',
  showLoading = true,
  lazyLoad = true,
  priority = false,
  quality = 85,
  width,
  height,
  className = '',
  onLoad,
  onError,
  ...props
}: OptimizedImageProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [isInView, setIsInView] = useState(!lazyLoad)
  const imageRef = useRef<HTMLDivElement>(null)
  const observerRef = useRef<IntersectionObserver>()

  // Lazy loading с Intersection Observer
  useEffect(() => {
    if (!lazyLoad || !imageRef.current) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true)
          observer.unobserve(entry.target)
        }
      },
      {
        rootMargin: '50px', // Начинаем загружать заранее
        threshold: 0.01
      }
    )

    observer.observe(imageRef.current)
    observerRef.current = observer

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect()
      }
    }
  }, [lazyLoad])

  const handleLoad = () => {
    setIsLoading(false)
    onLoad?.()
  }

  const handleError = () => {
    setIsLoading(false)
    setHasError(true)
    onError?.()
  }

  // Размеры для placeholder
  const placeholderSize = {
    width: typeof width === 'number' ? width : 400,
    height: typeof height === 'number' ? height : 300
  }

  return (
    <div 
      ref={imageRef} 
      className={`relative overflow-hidden ${className}`}
      style={{ 
        width: width || '100%', 
        height: height || 'auto',
        aspectRatio: width && height ? `${width}/${height}` : undefined
      }}
    >
      {/* Placeholder с блюром */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="absolute inset-0"
          >
            <div className="w-full h-full bg-gradient-to-br from-gray-200 to-gray-300 animate-pulse" />
            
            {showLoading && (
              <div className="absolute inset-0 flex items-center justify-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <Loader2 className="h-8 w-8 text-gray-400" />
                </motion.div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Основное изображение */}
      {isInView && !hasError && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="w-full h-full"
        >
          <Image
            src={src}
            alt={alt}
            width={width}
            height={height}
            quality={quality}
            priority={priority}
            loading={lazyLoad ? 'lazy' : 'eager'}
            onLoadingComplete={handleLoad}
            onError={handleError}
            className="object-cover w-full h-full"
            {...props}
          />
        </motion.div>
      )}

      {/* Ошибка загрузки */}
      {hasError && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute inset-0 bg-gradient-to-br from-red-50 to-pink-50 flex flex-col items-center justify-center p-4"
        >
          <AlertCircle className="h-12 w-12 text-red-400 mb-3" />
          <p className="text-sm text-red-600 text-center">
            Не удалось загрузить изображение
          </p>
          <button
            onClick={() => {
              setHasError(false)
              setIsLoading(true)
            }}
            className="mt-3 px-4 py-2 bg-red-500 text-white rounded-lg text-sm hover:bg-red-600 transition-colors"
          >
            Повторить
          </button>
        </motion.div>
      )}

      {/* Лейбл оптимизации */}
      {process.env.NODE_ENV === 'development' && (
        <div className="absolute top-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
          {lazyLoad ? 'Lazy' : 'Eager'} • {quality}% • {priority ? 'Priority' : 'Normal'}
        </div>
      )}
    </div>
  )
}

// Компонент для изображений галереи с превью
export function GalleryImage({ src, alt, ...props }: OptimizedImageProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  return (
    <>
      <motion.div
        className="relative rounded-lg overflow-hidden cursor-pointer"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setIsExpanded(true)}
      >
        <OptimizedImage
          src={src}
          alt={alt}
          width={300}
          height={200}
          quality={75}
          lazyLoad={true}
          className="rounded-lg"
          {...props}
        />
        
        {/* Эффект при наведении */}
        <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-opacity duration-200" />
        
        {/* Иконка увеличения */}
        <div className="absolute bottom-2 right-2 bg-white bg-opacity-90 p-1.5 rounded-full">
          <ImageIcon className="h-4 w-4 text-gray-700" />
        </div>
      </motion.div>

      {/* Модальное окно для полноразмерного изображения */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-80"
            onClick={() => setIsExpanded(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="relative max-w-4xl max-h-[90vh]"
              onClick={(e) => e.stopPropagation()}
            >
              <OptimizedImage
                src={src}
                alt={alt}
                quality={100}
                priority={true}
                className="rounded-xl max-h-[90vh] object-contain"
              />
              
              <button
                onClick={() => setIsExpanded(false)}
                className="absolute top-4 right-4 bg-black bg-opacity-70 text-white p-2 rounded-full hover:bg-opacity-90 transition-opacity"
              >
                <span className="text-lg">×</span>
              </button>
              
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-70 text-white px-4 py-2 rounded-full text-sm">
                {alt}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

// Хук для предзагрузки изображений
export function useImagePreloader(imageUrls: string[]) {
  const [loadedCount, setLoadedCount] = useState(0)
  const [isComplete, setIsComplete] = useState(false)

  useEffect(() => {
    if (imageUrls.length === 0) {
      setIsComplete(true)
      return
    }

    let loaded = 0
    const images: HTMLImageElement[] = []

    const handleLoad = () => {
      loaded++
      setLoadedCount(loaded)
      
      if (loaded === imageUrls.length) {
        setIsComplete(true)
      }
    }

    imageUrls.forEach(url => {
      const img = new Image()
      img.src = url
      img.onload = handleLoad
      img.onerror = handleLoad // Считаем и ошибки загрузки
      images.push(img)
    })

    return () => {
      images.forEach(img => {
        img.onload = null
        img.onerror = null
      })
    }
  }, [imageUrls])

  return {
    loadedCount,
    totalCount: imageUrls.length,
    progress: imageUrls.length > 0 ? (loadedCount / imageUrls.length) * 100 : 0,
    isComplete
  }
}

// Компонент для прогрессивной загрузки изображений
export function ProgressiveImageLoader({ images }: { images: string[] }) {
  const { progress, isComplete } = useImagePreloader(images)

  return (
    <div className="fixed top-0 left-0 right-0 z-50">
      <AnimatePresence>
        {!isComplete && (
          <motion.div
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            exit={{ y: -100 }}
            className="bg-gradient-to-r from-blue-500 to-purple-500 text-white p-3"
          >
            <div className="max-w-4xl mx-auto flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span className="font-medium">
                  Загружаем изображения...
                </span>
              </div>
              <div className="w-32">
                <div className="h-1.5 bg-white bg-opacity-30 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-white"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>
              <span className="text-sm font-bold">{Math.round(progress)}%</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}