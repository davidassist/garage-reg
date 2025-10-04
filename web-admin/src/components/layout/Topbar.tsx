'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import { 
  Search,
  Bell,
  Settings,
  User,
  LogOut,
  Menu,
  Shield,
  ChevronDown,
  Sun,
  Moon,
  Globe,
  HelpCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface TopbarProps {
  onToggleSidebar: () => void
  className?: string
}

interface Notification {
  id: string
  title: string
  message: string
  type: 'info' | 'warning' | 'error' | 'success'
  timestamp: Date
  read: boolean
}

const mockNotifications: Notification[] = [
  {
    id: '1',
    title: 'Új hibajegy',
    message: 'Kapu #3 karbantartást igényel',
    type: 'warning',
    timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    read: false,
  },
  {
    id: '2',
    title: 'Ellenőrzés befejezve',
    message: 'Épület A ellenőrzése sikeresen lezárult',
    type: 'success',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    read: false,
  },
  {
    id: '3',
    title: 'Rendszerfrissítés',
    message: 'A rendszer karbantartása ma este 22:00-kor kezdődik',
    type: 'info',
    timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000), // 4 hours ago
    read: true,
  },
]

export default function Topbar({ onToggleSidebar, className }: TopbarProps) {
  const router = useRouter()
  const { user, logout } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false)
  const [isNotificationMenuOpen, setIsNotificationMenuOpen] = useState(false)
  const [notifications, setNotifications] = useState(mockNotifications)
  const [isSearchFocused, setIsSearchFocused] = useState(false)

  const userMenuRef = useRef<HTMLDivElement>(null)
  const notificationMenuRef = useRef<HTMLDivElement>(null)
  const searchRef = useRef<HTMLInputElement>(null)

  // Close menus on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false)
      }
      if (notificationMenuRef.current && !notificationMenuRef.current.contains(event.target as Node)) {
        setIsNotificationMenuOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Keyboard navigation for menus
  const handleKeyDown = (event: React.KeyboardEvent, action: () => void) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      action()
    } else if (event.key === 'Escape') {
      setIsUserMenuOpen(false)
      setIsNotificationMenuOpen(false)
    }
  }

  // Search functionality
  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
      setSearchQuery('')
      searchRef.current?.blur()
    }
  }

  const handleSearchKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Escape') {
      setSearchQuery('')
      searchRef.current?.blur()
      setIsSearchFocused(false)
    }
  }

  // Notification functions
  const unreadNotifications = notifications.filter(n => !n.read)
  
  const markNotificationAsRead = (notificationId: string) => {
    setNotifications(prev => 
      prev.map(n => 
        n.id === notificationId ? { ...n, read: true } : n
      )
    )
  }

  const markAllAsRead = () => {
    setNotifications(prev => 
      prev.map(n => ({ ...n, read: true }))
    )
  }

  const formatTimeAgo = (timestamp: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - timestamp.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Most'
    if (diffInMinutes < 60) return `${diffInMinutes} perce`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} órája`
    return `${Math.floor(diffInMinutes / 1440)} napja`
  }

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'warning': return '⚠️'
      case 'error': return '❌'
      case 'success': return '✅'
      default: return 'ℹ️'
    }
  }

  const handleLogout = async () => {
    await logout()
    router.push('/login')
  }

  return (
    <header 
      className={cn(
        'sticky top-0 z-30 bg-white border-b border-gray-200 shadow-sm',
        className
      )}
      role="banner"
    >
      <div className="flex items-center justify-between h-16 px-4 lg:px-6">
        {/* Left section */}
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={onToggleSidebar}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            aria-label="Navigáció megnyitása"
          >
            <Menu className="h-5 w-5" aria-hidden="true" />
          </button>

          {/* Search */}
          <div className="relative">
            <form onSubmit={handleSearch} className="relative">
              <div className="relative">
                <Search 
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" 
                  aria-hidden="true"
                />
                <input
                  ref={searchRef}
                  type="text"
                  placeholder="Keresés..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => setIsSearchFocused(true)}
                  onBlur={() => setIsSearchFocused(false)}
                  onKeyDown={handleSearchKeyDown}
                  className={cn(
                    'w-64 pl-10 pr-4 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200',
                    isSearchFocused ? 'w-80' : 'w-64'
                  )}
                  aria-label="Keresés a rendszerben"
                />
              </div>
            </form>

            {/* Search suggestions could go here */}
            {isSearchFocused && searchQuery && (
              <div 
                className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
                role="listbox"
                aria-label="Keresési javaslatok"
              >
                <div className="p-2 text-sm text-gray-500">
                  Keresés: "{searchQuery}"
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right section */}
        <div className="flex items-center space-x-2">
          {/* Help button */}
          <button
            className="p-2 rounded-lg text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            aria-label="Súgó"
          >
            <HelpCircle className="h-5 w-5" aria-hidden="true" />
          </button>

          {/* Notifications */}
          <div className="relative" ref={notificationMenuRef}>
            <button
              onClick={() => setIsNotificationMenuOpen(!isNotificationMenuOpen)}
              onKeyDown={(e) => handleKeyDown(e, () => setIsNotificationMenuOpen(!isNotificationMenuOpen))}
              className="relative p-2 rounded-lg text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              aria-label={`Értesítések ${unreadNotifications.length > 0 ? `(${unreadNotifications.length} olvasatlan)` : ''}`}
              aria-expanded={isNotificationMenuOpen}
              aria-haspopup="true"
            >
              <Bell className="h-5 w-5" aria-hidden="true" />
              {unreadNotifications.length > 0 && (
                <span 
                  className="absolute top-1 right-1 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full"
                  aria-hidden="true"
                >
                  {unreadNotifications.length}
                </span>
              )}
            </button>

            {/* Notification dropdown */}
            {isNotificationMenuOpen && (
              <div 
                className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
                role="menu"
                aria-label="Értesítések menü"
              >
                <div className="p-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-medium text-gray-900">Értesítések</h3>
                    {unreadNotifications.length > 0 && (
                      <button
                        onClick={markAllAsRead}
                        className="text-xs text-blue-600 hover:text-blue-500 font-medium"
                        aria-label="Összes megjelölése olvasottként"
                      >
                        Összes olvasva
                      </button>
                    )}
                  </div>
                </div>

                <div className="max-h-96 overflow-y-auto">
                  {notifications.length > 0 ? (
                    notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={cn(
                          'p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer transition-colors',
                          !notification.read && 'bg-blue-50'
                        )}
                        onClick={() => markNotificationAsRead(notification.id)}
                        role="menuitem"
                        tabIndex={0}
                        onKeyDown={(e) => handleKeyDown(e, () => markNotificationAsRead(notification.id))}
                        aria-label={`Értesítés: ${notification.title}`}
                      >
                        <div className="flex items-start space-x-3">
                          <span className="text-lg" aria-hidden="true">
                            {getNotificationIcon(notification.type)}
                          </span>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {notification.title}
                              </p>
                              <span className="text-xs text-gray-500">
                                {formatTimeAgo(notification.timestamp)}
                              </span>
                            </div>
                            <p className="text-sm text-gray-600 mt-1">
                              {notification.message}
                            </p>
                          </div>
                          {!notification.read && (
                            <div 
                              className="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0"
                              aria-label="Olvasatlan értesítés"
                            />
                          )}
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="p-8 text-center text-gray-500">
                      <Bell className="h-8 w-8 mx-auto mb-2 text-gray-300" aria-hidden="true" />
                      <p>Nincsenek értesítések</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="relative" ref={userMenuRef}>
            <button
              onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
              onKeyDown={(e) => handleKeyDown(e, () => setIsUserMenuOpen(!isUserMenuOpen))}
              className="flex items-center space-x-2 p-2 rounded-lg text-gray-700 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              aria-label="Felhasználói menü"
              aria-expanded={isUserMenuOpen}
              aria-haspopup="true"
            >
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="hidden md:block text-left">
                  <div className="text-sm font-medium text-gray-900">
                    {user?.name || 'Felhasználó'}
                  </div>
                  <div className="text-xs text-gray-500 flex items-center">
                    <Shield className="h-3 w-3 mr-1" aria-hidden="true" />
                    {user?.roles?.[0]?.name || 'Felhasználó'}
                  </div>
                </div>
                <ChevronDown 
                  className={cn(
                    'h-4 w-4 text-gray-400 transition-transform duration-200',
                    isUserMenuOpen ? 'transform rotate-180' : ''
                  )}
                  aria-hidden="true"
                />
              </div>
            </button>

            {/* User dropdown */}
            {isUserMenuOpen && (
              <div 
                className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50"
                role="menu"
                aria-label="Felhasználói menü"
              >
                <div className="p-3 border-b border-gray-200">
                  <div className="text-sm font-medium text-gray-900">{user?.name}</div>
                  <div className="text-xs text-gray-500">{user?.email}</div>
                </div>

                <div className="py-1">
                  <button
                    onClick={() => router.push('/profile')}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    role="menuitem"
                  >
                    <User className="h-4 w-4 mr-3" aria-hidden="true" />
                    Profil
                  </button>

                  <button
                    onClick={() => router.push('/settings')}
                    className="w-full flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                    role="menuitem"
                  >
                    <Settings className="h-4 w-4 mr-3" aria-hidden="true" />
                    Beállítások
                  </button>

                  <div className="border-t border-gray-200 my-1" role="separator" />

                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                    role="menuitem"
                  >
                    <LogOut className="h-4 w-4 mr-3" aria-hidden="true" />
                    Kijelentkezés
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}