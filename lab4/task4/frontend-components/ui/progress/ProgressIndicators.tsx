'use client'

import React from 'react'
import { Check, Clock, TrendingUp, Target, Award, Star } from 'lucide-react'
import { motion } from 'framer-motion'

interface ProgressBarProps {
  value: number
  max?: number
  label?: string
  color?: 'orange' | 'blue' | 'green' | 'purple' | 'red'
  showValue?: boolean
  animated?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function ProgressBar({
  value,
  max = 100,
  label,
  color = 'orange',
  showValue = true,
  animated = true,
  size = 'md'
}: ProgressBarProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))
  
  const colorClasses = {
    orange: 'from-orange-400 to-yellow-400',
    blue: 'from-blue-400 to-cyan-400',
    green: 'from-green-400 to-emerald-400',
    purple: 'from-purple-400 to-pink-400',
    red: 'from-red-400 to-pink-400'
  }

  const sizeClasses = {
    sm: 'h-1.5',
    md: 'h-2.5',
    lg: 'h-4'
  }

  return (
    <div className="space-y-2">
      {(label || showValue) && (
        <div className="flex justify-between items-center">
          {label && (
            <span className="text-sm font-medium text-gray-700">{label}</span>
          )}
          {showValue && (
            <span className="text-sm font-bold text-gray-800">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}
      
      <div className={`${sizeClasses[size]} bg-gray-200 rounded-full overflow-hidden`}>
        <motion.div
          className={`h-full rounded-full bg-gradient-to-r ${colorClasses[color]}`}
          initial={animated ? { width: 0 } : false}
          animate={{ width: `${percentage}%` }}
          transition={{
            duration: 1,
            ease: "easeOut"
          }}
        />
      </div>
    </div>
  )
}

interface StepProgressProps {
  steps: string[]
  currentStep: number
  completed?: boolean
  onStepClick?: (step: number) => void
}

export function StepProgress({
  steps,
  currentStep,
  completed = false,
  onStepClick
}: StepProgressProps) {
  return (
    <div className="relative">
      {/* Линия прогресса */}
      <div className="absolute left-0 right-0 top-4 h-0.5 bg-gray-200 -translate-y-1/2">
        <motion.div
          className="h-full bg-gradient-to-r from-orange-500 to-yellow-500"
          initial={{ width: 0 }}
          animate={{ 
            width: completed ? '100%' : `${(currentStep / (steps.length - 1)) * 100}%` 
          }}
          transition={{ duration: 0.5 }}
        />
      </div>

      {/* Шаги */}
      <div className="relative flex justify-between">
        {steps.map((step, index) => {
          const isCompleted = completed || index < currentStep
          const isCurrent = !completed && index === currentStep
          
          return (
            <div key={index} className="flex flex-col items-center">
              <motion.button
                className={`
                  relative z-10 flex items-center justify-center w-8 h-8 rounded-full
                  ${isCompleted 
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white' 
                    : isCurrent
                    ? 'bg-gradient-to-r from-orange-500 to-yellow-500 text-white ring-4 ring-orange-100'
                    : 'bg-white border-2 border-gray-300 text-gray-400'
                  }
                  transition-all duration-200
                  ${onStepClick ? 'cursor-pointer hover:scale-110' : 'cursor-default'}
                `}
                whileHover={onStepClick ? { scale: 1.1 } : {}}
                whileTap={onStepClick ? { scale: 0.95 } : {}}
                onClick={() => onStepClick?.(index)}
              >
                {isCompleted ? (
                  <Check className="h-4 w-4" />
                ) : (
                  <span className="font-bold">{index + 1}</span>
                )}
              </motion.button>
              
              <span className={`
                mt-2 text-xs font-medium text-center max-w-20
                ${isCurrent ? 'text-orange-600 font-bold' : 'text-gray-600'}
              `}>
                {step}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

interface CircularProgressProps {
  value: number
  max?: number
  size?: number
  strokeWidth?: number
  label?: string
  sublabel?: string
  color?: 'orange' | 'blue' | 'green' | 'purple'
  showValue?: boolean
  animated?: boolean
}

export function CircularProgress({
  value,
  max = 100,
  size = 100,
  strokeWidth = 8,
  label,
  sublabel,
  color = 'orange',
  showValue = true,
  animated = true
}: CircularProgressProps) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const percentage = Math.min(100, Math.max(0, (value / max) * 100))
  const strokeDashoffset = circumference - (percentage / 100) * circumference
  
  const colorClasses = {
    orange: 'stroke-orange-500',
    blue: 'stroke-blue-500',
    green: 'stroke-green-500',
    purple: 'stroke-purple-500'
  }

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg
        width={size}
        height={size}
        className="transform -rotate-90"
      >
        {/* Фоновый круг */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          className="stroke-gray-200 fill-none"
        />
        
        {/* Прогресс круг */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          strokeWidth={strokeWidth}
          className={`${colorClasses[color]} fill-none`}
          strokeLinecap="round"
          initial={animated ? { strokeDashoffset: circumference } : false}
          animate={{ strokeDashoffset }}
          transition={{
            duration: 1.5,
            ease: "easeOut"
          }}
          strokeDasharray={circumference}
        />
      </svg>
      
      {/* Текст в центре */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        {showValue && (
          <span className="text-2xl font-bold text-gray-800">
            {Math.round(percentage)}%
          </span>
        )}
        {label && (
          <span className="text-sm font-medium text-gray-700">{label}</span>
        )}
        {sublabel && (
          <span className="text-xs text-gray-500">{sublabel}</span>
        )}
      </div>
    </div>
  )
}

interface ScoreIndicatorProps {
  score: number
  maxScore?: number
  label?: string
  size?: 'sm' | 'md' | 'lg'
  showStars?: boolean
  animated?: boolean
}

export function ScoreIndicator({
  score,
  maxScore = 5,
  label,
  size = 'md',
  showStars = true,
  animated = true
}: ScoreIndicatorProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  }

  const filledStars = Math.floor(score)
  const partialStar = score - filledStars
  const emptyStars = maxScore - filledStars - (partialStar > 0 ? 1 : 0)

  return (
    <div className="space-y-2">
      {label && (
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-sm font-bold text-gray-800">
            {score.toFixed(1)}/{maxScore}
          </span>
        </div>
      )}
      
      {showStars && (
        <div className="flex items-center space-x-1">
          {/* Заполненные звезды */}
          {[...Array(filledStars)].map((_, i) => (
            <motion.div
              key={`filled-${i}`}
              initial={animated ? { scale: 0, rotate: -180 } : false}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ delay: i * 0.1, duration: 0.5 }}
            >
              <Star className={`${sizeClasses[size]} text-yellow-500 fill-current`} />
            </motion.div>
          ))}
          
          {/* Частично заполненная звезда */}
          {partialStar > 0 && (
            <div className="relative">
              <Star className={`${sizeClasses[size]} text-gray-300`} />
              <motion.div
                className="absolute inset-0 overflow-hidden"
                initial={animated ? { width: 0 } : false}
                animate={{ width: `${partialStar * 100}%` }}
                transition={{ delay: filledStars * 0.1, duration: 0.5 }}
              >
                <Star className={`${sizeClasses[size]} text-yellow-500 fill-current`} />
              </motion.div>
            </div>
          )}
          
          {/* Пустые звезды */}
          {[...Array(emptyStars)].map((_, i) => (
            <motion.div
              key={`empty-${i}`}
              initial={animated ? { scale: 0 } : false}
              animate={{ scale: 1 }}
              transition={{ 
                delay: (filledStars + (partialStar > 0 ? 1 : 0) + i) * 0.1,
                duration: 0.5 
              }}
            >
              <Star className={`${sizeClasses[size]} text-gray-300`} />
            </motion.div>
          ))}
        </div>
      )}
      
      {!showStars && (
        <ProgressBar 
          value={(score / maxScore) * 100} 
          color="yellow"
          animated={animated}
        />
      )}
    </div>
  )
}

interface AchievementProgressProps {
  title: string
  description: string
  current: number
  target: number
  icon?: React.ReactNode
  color?: 'orange' | 'blue' | 'green' | 'purple'
}

export function AchievementProgress({
  title,
  description,
  current,
  target,
  icon = <Award className="h-6 w-6" />,
  color = 'orange'
}: AchievementProgressProps) {
  const percentage = Math.min(100, (current / target) * 100)
  const isComplete = current >= target
  
  const colorClasses = {
    orange: 'bg-gradient-to-r from-orange-50 to-yellow-50 border-orange-200',
    blue: 'bg-gradient-to-r from-blue-50 to-cyan-50 border-blue-200',
    green: 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200',
    purple: 'bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200'
  }

  const textColors = {
    orange: 'text-orange-700',
    blue: 'text-blue-700',
    green: 'text-green-700',
    purple: 'text-purple-700'
  }

  return (
    <motion.div
      className={`${colorClasses[color]} border rounded-xl p-4`}
      whileHover={{ y: -2, transition: { duration: 0.2 } }}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-3">
          <div className={`p-2 rounded-lg ${textColors[color]} bg-white`}>
            {icon}
          </div>
          <div>
            <h4 className="font-bold text-gray-800">{title}</h4>
            <p className="text-sm text-gray-600">{description}</p>
          </div>
        </div>
        
        {isComplete && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="bg-gradient-to-r from-green-500 to-emerald-500 text-white p-1 rounded-full"
          >
            <Check className="h-4 w-4" />
          </motion.div>
        )}
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium text-gray-700">
            Прогресс: {current}/{target}
          </span>
          <span className="font-bold text-gray-800">
            {Math.round(percentage)}%
          </span>
        </div>
        
        <ProgressBar value={percentage} color={color} />
        
        {!isComplete && (
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="h-3 w-3 mr-1" />
            <span>Осталось {target - current} до достижения</span>
          </div>
        )}
        
        {isComplete && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center text-sm text-green-600 font-medium"
          >
            <TrendingUp className="h-3 w-3 mr-1" />
            <span>Достижение получено! 🎉</span>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}

// Хук для анимированного прогресса
export function useAnimatedProgress(initialValue = 0, duration = 1000) {
  const [progress, setProgress] = React.useState(initialValue)
  
  const animateTo = React.useCallback((targetValue: number) => {
    const startTime = Date.now()
    const startValue = progress
    
    const animate = () => {
      const elapsed = Date.now() - startTime
      const fraction = Math.min(1, elapsed / duration)
      
      // Используем easeOutCubic для плавного замедления
      const eased = 1 - Math.pow(1 - fraction, 3)
      const newValue = startValue + (targetValue - startValue) * eased
      
      setProgress(newValue)
      
      if (fraction < 1) {
        requestAnimationFrame(animate)
      }
    }
    
    requestAnimationFrame(animate)
  }, [progress, duration])
  
  return { progress, animateTo, setProgress }
}
