'use client'

import React, { useState, useEffect } from 'react'
import { motion, AnimatePresence, useMotionValue, useSpring, useTransform } from 'framer-motion'
import { 
  Heart, 
  Bookmark, 
  Share2, 
  ThumbsUp, 
  Star, 
  Sparkles,
  Zap,
  ChevronRight,
  Check,
  X,
  RefreshCw,
  Download,
  Upload,
  Eye,
  EyeOff
} from 'lucide-react'

// Анимированная кнопка с эффектом нажатия
export function AnimatedButton({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  icon,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  icon?: React.ReactNode
}) {
  const [isPressed, setIsPressed] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const scale = useMotionValue(1)
  const springScale = useSpring(scale, {
    stiffness: 400,
    damping: 30
  })

  const variants = {
    primary: 'bg-gradient-to-r from-orange-500 to-yellow-500 text-white',
    secondary: 'bg-gradient-to-r from-blue-500 to-cyan-500 text-white',
    outline: 'border-2 border-gray-300 text-gray-700 hover:border-orange-500',
    ghost: 'text-gray-700 hover:bg-gray-100'
  }

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-sm',
    lg: 'px-6 py-3 text-base'
  }

  return (
    <motion.button
      className={`
        ${variants[variant]} 
        ${sizes[size]}
        rounded-lg font-medium
        flex items-center justify-center
        transition-colors duration-200
        disabled:opacity-50 disabled:cursor-not-allowed
        relative overflow-hidden
      `}
      style={{ scale: springScale }}
      whileHover={{ y: -2 }}
      whileTap={{ scale: 0.95 }}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
      onMouseLeave={() => setIsPressed(false)}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={onClick}
      disabled={isLoading}
      {...props}
    >
      {/* Эффект нажатия */}
      <motion.div
        className="absolute inset-0 bg-white"
        initial={{ opacity: 0 }}
        animate={{ opacity: isPressed ? 0.2 : 0 }}
        transition={{ duration: 0.1 }}
      />

      {/* Эффект волны при клике */}
      {isPressed && (
        <motion.div
          className="absolute inset-0 bg-white rounded-full"
          initial={{ scale: 0, opacity: 0.4 }}
          animate={{ scale: 2, opacity: 0 }}
          transition={{ duration: 0.5 }}
        />
      )}

      {/* Контент */}
      <div className="relative z-10 flex items-center">
        {isLoading ? (
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            className="mr-2"
          >
            <RefreshCw className="h-4 w-4" />
          </motion.div>
        ) : icon ? (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="mr-2"
          >
            {icon}
          </motion.div>
        ) : null}
        
        <motion.span
          animate={isLoading ? { opacity: 0.7 } : { opacity: 1 }}
        >
          {children}
        </motion.span>
      </div>

      {/* Эффект частиц при наведении */}
      <AnimatePresence>
        {isHovered && variant === 'primary' && (
          <>
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-white rounded-full"
                initial={{
                  x: '50%',
                  y: '50%',
                  opacity: 0
                }}
                animate={{
                  x: Math.random() * 100 - 50 + '%',
                  y: Math.random() * 100 - 50 + '%',
                  opacity: [0, 1, 0]
                }}
                exit={{ opacity: 0 }}
                transition={{
                  duration: 0.8,
                  delay: i * 0.1
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>
    </motion.button>
  )
}

// Интерактивная карточка с эффектами
export function InteractiveCard({
  children,
  onClick,
  hoverEffect = true,
  glowEffect = false,
  ...props
}: React.HTMLAttributes<HTMLDivElement> & {
  onClick?: () => void
  hoverEffect?: boolean
  glowEffect?: boolean
}) {
  const [isHovered, setIsHovered] = useState(false)
  const [isClicked, setIsClicked] = useState(false)

  return (
    <motion.div
      className={`
        bg-white rounded-xl shadow-sm border border-gray-200
        relative overflow-hidden cursor-pointer
        ${onClick ? 'cursor-pointer' : ''}
      `}
      initial={false}
      animate={{
        scale: isClicked ? 0.98 : 1,
        y: isHovered && hoverEffect ? -4 : 0
      }}
      whileHover={hoverEffect ? {
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
      } : {}}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false)
        setIsClicked(false)
      }}
      onMouseDown={() => setIsClicked(true)}
      onMouseUp={() => setIsClicked(false)}
      onClick={onClick}
      {...props}
    >
      {/* Свечение при наведении */}
      {glowEffect && (
        <motion.div
          className="absolute inset-0 bg-gradient-to-r from-orange-100 to-yellow-100"
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 0.3 : 0 }}
          transition={{ duration: 0.2 }}
        />
      )}

      {/* Акцентная полоска слева */}
      <motion.div
        className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-orange-500 to-yellow-500"
        initial={{ scaleY: 0 }}
        animate={{ scaleY: isHovered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
      />

      {/* Содержимое */}
      <div className="relative z-10 p-6">
        {children}
      </div>

      {/* Эффект клика */}
      {onClick && (
        <motion.div
          className="absolute inset-0 bg-black"
          initial={{ opacity: 0 }}
          animate={{ opacity: isClicked ? 0.1 : 0 }}
          transition={{ duration: 0.1 }}
        />
      )}
    </motion.div>
  )
}

// Кнопка лайка с анимацией
export function LikeButton({
  initialLiked = false,
  count = 0,
  onLike
}: {
  initialLiked?: boolean
  count?: number
  onLike?: (liked: boolean) => void
}) {
  const [isLiked, setIsLiked] = useState(initialLiked)
  const [isAnimating, setIsAnimating] = useState(false)
  const [likeCount, setLikeCount] = useState(count)

  const handleClick = () => {
    const newLiked = !isLiked
    setIsLiked(newLiked)
    setLikeCount(prev => newLiked ? prev + 1 : prev - 1)
    setIsAnimating(true)
    
    setTimeout(() => setIsAnimating(false), 600)
    onLike?.(newLiked)
  }

  return (
    <motion.button
      className={`
        flex items-center space-x-2 px-3 py-1.5 rounded-full
        ${isLiked 
          ? 'bg-gradient-to-r from-pink-50 to-rose-50 text-pink-600' 
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
        }
        transition-colors duration-200
      `}
      whileTap={{ scale: 0.95 }}
      onClick={handleClick}
    >
      <div className="relative">
        <motion.div
          animate={isAnimating ? {
            scale: [1, 1.3, 1],
            rotate: isLiked ? [0, -10, 10, 0] : [0, 10, -10, 0]
          } : {}}
          transition={{ duration: 0.6 }}
        >
          <Heart className={`h-5 w-5 ${isLiked ? 'fill-current' : ''}`} />
        </motion.div>
        
        {/* Эффект частиц при лайке */}
        {isAnimating && isLiked && (
          <>
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-pink-500 rounded-full"
                initial={{
                  x: 0,
                  y: 0,
                  opacity: 1,
                  scale: 1
                }}
                animate={{
                  x: Math.cos((i * 60) * Math.PI / 180) * 30,
                  y: Math.sin((i * 60) * Math.PI / 180) * 30,
                  opacity: 0,
                  scale: 0
                }}
                transition={{
                  duration: 0.8,
                  delay: i * 0.05
                }}
              />
            ))}
          </>
        )}
      </div>
      
      <motion.span
        key={likeCount}
        initial={{ y: isLiked ? -10 : 10, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="font-medium text-sm"
      >
        {likeCount}
      </motion.span>
    </motion.button>
  )
}

// Переключатель с анимацией
export function AnimatedToggle({
  enabled,
  onChange,
  size = 'md'
}: {
  enabled: boolean
  onChange: (enabled: boolean) => void
  size?: 'sm' | 'md' | 'lg'
}) {
  const spring = useSpring(0, { stiffness: 500, damping: 30 })
  const x = useTransform(spring, [0, 1], [2, size === 'sm' ? 18 : size === 'lg' ? 26 : 22])

  useEffect(() => {
    spring.set(enabled ? 1 : 0)
  }, [enabled, spring])

  const sizes = {
    sm: { width: 40, height: 20 },
    md: { width: 52, height: 28 },
    lg: { width: 64, height: 32 }
  }

  return (
    <button
      className={`
        relative rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500
        ${enabled 
          ? 'bg-gradient-to-r from-green-500 to-emerald-500' 
          : 'bg-gray-300'
        }
        transition-colors duration-200
      `}
      style={{
        width: sizes[size].width,
        height: sizes[size].height
      }}
      onClick={() => onChange(!enabled)}
      aria-label={enabled ? 'Выключить' : 'Включить'}
    >
      <motion.div
        className="absolute top-1 bg-white rounded-full shadow-lg"
        style={{
          width: sizes[size].height - 8,
          height: sizes[size].height - 8,
          x
        }}
      >
        {/* Иконка внутри переключателя */}
        <div className="flex items-center justify-center h-full">
          {enabled ? (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              <Check className="h-3 w-3 text-green-500" />
            </motion.div>
          ) : (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
            >
              <X className="h-3 w-3 text-gray-400" />
            </motion.div>
          )}
        </div>
      </motion.div>
    </button>
  )
}

// Прогресс бар с анимацией заполнения
export function AnimatedProgressBar({
  progress,
  label,
  color = 'orange',
  showParticles = true
}: {
  progress: number
  label?: string
  color?: 'orange' | 'blue' | 'green' | 'purple'
  showParticles?: boolean
}) {
  const [prevProgress, setPrevProgress] = useState(0)
  const [particles, setParticles] = useState<Array<{ id: number; x: number; y: number }>>([])

  useEffect(() => {
    if (progress > prevProgress && showParticles) {
      // Создаём частицы при увеличении прогресса
      const newParticles = [...Array(3)].map((_, i) => ({
        id: Date.now() + i,
        x: Math.random() * 100,
        y: Math.random() * 100
      }))
      setParticles(prev => [...prev, ...newParticles])

      // Удаляем частицы через 1 секунду
      setTimeout(() => {
        setParticles(prev => prev.filter(p => !newParticles.find(np => np.id === p.id)))
      }, 1000)
    }
    setPrevProgress(progress)
  }, [progress, prevProgress, showParticles])

  const colorClasses = {
    orange: 'from-orange-400 to-yellow-400',
    blue: 'from-blue-400 to-cyan-400',
    green: 'from-green-400 to-emerald-400',
    purple: 'from-purple-400 to-pink-400'
  }

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex justify-between">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-sm font-bold text-gray-800">{Math.round(progress)}%</span>
        </div>
      )}
      
      <div className="relative h-2.5 bg-gray-200 rounded-full overflow-hidden">
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${colorClasses[color]}`}
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
        />
        
        {/* Анимированные частицы */}
        {showParticles && (
          <>
            {particles.map(particle => (
              <motion.div
                key={particle.id}
                className="absolute w-1 h-1 bg-white rounded-full"
                initial={{
                  x: `${particle.x}%`,
                  y: 0,
                  opacity: 1,
                  scale: 1
                }}
                animate={{
                  y: -10,
                  opacity: 0,
                  scale: 0
                }}
                transition={{ duration: 1 }}
              />
            ))}
          </>
        )}
      </div>
    </div>
  )
}

// Анимированный аккордеон
export function AnimatedAccordion({
  title,
  children,
  defaultOpen = false
}: {
  title: string
  children: React.ReactNode
  defaultOpen?: boolean
}) {
  const [isOpen, setIsOpen] = useState(defaultOpen)

  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="font-semibold text-gray-800">{title}</span>
        <motion.div
          animate={{ rotate: isOpen ? 90 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronRight className="h-5 w-5 text-gray-500" />
        </motion.div>
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="p-4 pt-0 border-t border-gray-100">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

// Эффект конфетти для праздничных событий
export function ConfettiEffect({ trigger }: { trigger: boolean }) {
  const [confetti, setConfetti] = useState<Array<{
    id: number
    x: number
    y: number
    color: string
    shape: 'circle' | 'square' | 'triangle'
  }>>([])

  useEffect(() => {
    if (trigger) {
      // Создаём 50 частиц конфетти
      const newConfetti = [...Array(50)].map((_, i) => ({
        id: Date.now() + i,
        x: Math.random() * 100,
        y: -10,
        color: ['#FF6B6B', '#4ECDC4', '#FFD166', '#06D6A0', '#118AB2'][Math.floor(Math.random() * 5)],
        shape: ['circle', 'square', 'triangle'][Math.floor(Math.random() * 3)] as 'circle' | 'square' | 'triangle'
      }))
      
      setConfetti(newConfetti)

      // Убираем конфетти через 3 секунды
      setTimeout(() => {
        setConfetti([])
      }, 3000)
    }
  }, [trigger])

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {confetti.map(particle => (
        <motion.div
          key={particle.id}
          className="absolute"
          style={{
            left: `${particle.x}%`,
            backgroundColor: particle.color
          }}
          initial={{
            y: particle.y,
            x: 0,
            rotate: 0,
            scale: 1,
            opacity: 1
          }}
          animate={{
            y: '100vh',
            x: Math.random() * 200 - 100,
            rotate: 360,
            scale: 0,
            opacity: 0
          }}
          transition={{
            duration: 3,
            ease: "easeOut"
          }}
          style={{
            width: particle.shape === 'triangle' ? 0 : 8,
            height: particle.shape === 'triangle' ? 0 : 8,
            borderBottom: particle.shape === 'triangle' ? '8px solid transparent' : 'none',
            borderTop: particle.shape === 'triangle' ? `8px solid ${particle.color}` : 'none',
            borderLeft: particle.shape === 'triangle' ? '4px solid transparent' : 'none',
            borderRight: particle.shape === 'triangle' ? '4px solid transparent' : 'none',
            borderRadius: particle.shape === 'circle' ? '50%' : particle.shape === 'square' ? '2px' : '0'
          }}
        />
      ))}
    </div>
  )
}

// Хук для микроинтеракций
export function useMicroInteraction() {
  const [interactionState, setInteractionState] = useState<'idle' | 'hover' | 'active' | 'success' | 'error'>('idle')
  const [interactionCount, setInteractionCount] = useState(0)

  const handleInteraction = (type: 'hover' | 'click' | 'success' | 'error') => {
    setInteractionState(type === 'click' ? 'active' : type)
    setInteractionCount(prev => prev + 1)

    if (type === 'click') {
      setTimeout(() => setInteractionState('idle'), 200)
    }
  }

  const getFeedback = () => {
    switch (interactionState) {
      case 'success':
        return { message: 'Успешно!', icon: Check, color: 'text-green-500' }
      case 'error':
        return { message: 'Ошибка', icon: X, color: 'text-red-500' }
      case 'active':
        return { message: 'Загрузка...', icon: RefreshCw, color: 'text-blue-500' }
      default:
        return null
    }
  }

  return {
    interactionState,
    interactionCount,
    handleInteraction,
    getFeedback
  }
}