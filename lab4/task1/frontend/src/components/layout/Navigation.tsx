'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, PlusCircle, History, BarChart, User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

const navItems = [
  { name: 'Главная', icon: Home, href: '/' },
  { name: 'Новое блюдо', icon: PlusCircle, href: '/new-dish' },
  { name: 'История', icon: History, href: '/history' },
  { name: 'Статистика', icon: BarChart, href: '/statistics' },
  { name: 'Профиль', icon: User, href: '/profile' },
]

export default function Navigation() {
  const pathname = usePathname()
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) return null

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 md:hidden">
      <div className="flex justify-around items-center h-16">
        {navItems.map((item) => {
          const isActive = pathname === item.href
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex flex-col items-center justify-center p-2 transition-colors ${
                isActive
                  ? 'text-orange-500'
                  : 'text-gray-600 hover:text-orange-500'
              }`}
            >
              <item.icon className="h-6 w-6" />
              <span className="text-xs mt-1">{item.name}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
