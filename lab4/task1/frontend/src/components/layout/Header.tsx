'use client'

import { ChefHat, Bell, User } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

interface HeaderProps {
  title?: string
}

export default function Header({ title = 'Cooking Assistant' }: HeaderProps) {
  const { user, isAuthenticated } = useAuth()

  return (
    <header className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between px-4 py-3">
        <div className="flex items-center space-x-2">
          <ChefHat className="h-8 w-8 text-orange-500" />
          <h1 className="text-xl font-bold text-gray-800">{title}</h1>
        </div>
        
        <div className="flex items-center space-x-3">
          {isAuthenticated && (
            <>
              <button className="p-2 text-gray-600 hover:text-orange-500 relative">
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 h-2 w-2 bg-red-500 rounded-full"></span>
              </button>
              
              <div className="flex items-center space-x-2">
                <div className="text-right hidden sm:block">
                  <div className="text-sm font-medium text-gray-800">
                    {user?.username}
                  </div>
                  <div className="text-xs text-gray-500">Шеф</div>
                </div>
                <div className="h-8 w-8 bg-gradient-to-r from-orange-400 to-yellow-400 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
