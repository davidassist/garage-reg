'use client'

import { useState, useRef, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/lib/auth/context'
import { UserRole, PermissionResource, PermissionAction } from '@/lib/auth/types'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  Home,
  Users,
  Building2,
  Building,
  DoorOpen,
  ClipboardCheck,
  AlertTriangle,
  FileText,
  FolderOpen,
  BarChart3,
  Package,
  Settings,
  ChevronLeft,
  ChevronRight,
  User,
  LogOut,
  QrCode,
  Calendar
} from 'lucide-react'

interface MenuItem {
  id: string
  name: string
  href: string
  icon: any
  badge?: string
  requiredPermission?: {
    resource: PermissionResource
    action: PermissionAction
  }
  requiredRoles?: UserRole[]
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    href: '/dashboard',
    icon: Home
  },
  {
    id: 'clients',
    name: 'Ügyfelek',
    href: '/clients',
    icon: Users,
    requiredPermission: {
      resource: PermissionResource.CLIENTS,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'sites',
    name: 'Telephelyek',
    href: '/sites',
    icon: Building2,
    requiredPermission: {
      resource: PermissionResource.SITES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'buildings',
    name: 'Épületek',
    href: '/buildings',
    icon: Building,
    requiredPermission: {
      resource: PermissionResource.BUILDINGS,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'gates',
    name: 'Kapuk',
    href: '/gates',
    icon: DoorOpen,
    requiredPermission: {
      resource: PermissionResource.GATES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'labels',
    name: 'Címkék',
    href: '/labels',
    icon: QrCode,
    requiredPermission: {
      resource: PermissionResource.GATES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'inspections',
    name: 'Ellenőrzések',
    href: '/inspections',
    icon: ClipboardCheck,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'calendar',
    name: 'Naptár',
    href: '/calendar',
    icon: Calendar,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'tickets',
    name: 'Hibajegyek',
    href: '/tickets',
    icon: AlertTriangle,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'worksheets',
    name: 'Munkalapok',
    href: '/worksheets',
    icon: FileText,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'documents',
    name: 'Dokumentumok',
    href: '/documents',
    icon: FolderOpen,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'reports',
    name: 'Riportok',
    href: '/reports',
    icon: BarChart3,
    requiredPermission: {
      resource: PermissionResource.ANALYTICS,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'inventory',
    name: 'Raktár',
    href: '/inventory',
    icon: Package,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    }
  },
  {
    id: 'settings',
    name: 'Beállítások',
    href: '/settings',
    icon: Settings,
    requiredPermission: {
      resource: PermissionResource.SETTINGS,
      action: PermissionAction.READ,
    },
    requiredRoles: [UserRole.ADMIN, UserRole.SUPER_ADMIN]
  }
]

interface SidebarProps {
  isCollapsed?: boolean
  onToggle?: () => void
  className?: string
}

export function Sidebar({ isCollapsed = false, onToggle, className }: SidebarProps) {
  const pathname = usePathname()
  const auth = useAuth()
  const [focusedIndex, setFocusedIndex] = useState(-1)
  const menuRef = useRef<HTMLDivElement>(null)
  const itemRefs = useRef<(HTMLAnchorElement | null)[]>([])

  // Filter menu items based on user permissions and roles
  const filteredMenuItems = menuItems.filter(item => {
    // Always show items with no restrictions
    if (!item.requiredRoles && !item.requiredPermission) {
      return true
    }

    // Check role requirements
    if (item.requiredRoles) {
      const hasRequiredRole = item.requiredRoles.some(role => auth.hasRole(role))
      if (!hasRequiredRole) return false
    }

    // Check permission requirements
    if (item.requiredPermission) {
      const hasPermission = auth.hasPermission(
        item.requiredPermission.resource,
        item.requiredPermission.action
      )
      if (!hasPermission) return false
    }

    return true
  })

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!menuRef.current?.contains(e.target as Node)) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setFocusedIndex(prev => 
            prev < filteredMenuItems.length - 1 ? prev + 1 : 0
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setFocusedIndex(prev => 
            prev > 0 ? prev - 1 : filteredMenuItems.length - 1
          )
          break
        case 'Home':
          e.preventDefault()
          setFocusedIndex(0)
          break
        case 'End':
          e.preventDefault()
          setFocusedIndex(filteredMenuItems.length - 1)
          break
        case 'Enter':
        case ' ':
          if (focusedIndex >= 0 && itemRefs.current[focusedIndex]) {
            e.preventDefault()
            itemRefs.current[focusedIndex]?.click()
          }
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [focusedIndex, filteredMenuItems.length])

  // Focus management
  useEffect(() => {
    if (focusedIndex >= 0 && itemRefs.current[focusedIndex]) {
      itemRefs.current[focusedIndex]?.focus()
    }
  }, [focusedIndex])

  const handleLogout = async () => {
    await auth.logout()
  }

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-white border-r border-gray-200 transition-all duration-300",
        isCollapsed ? "w-16" : "w-64",
        className
      )}
      aria-label="Oldalsáv navigáció"
    >
      {/* Logo and Toggle */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        {!isCollapsed && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">GR</span>
            </div>
            <span className="font-semibold text-gray-900">GarageReg</span>
          </div>
        )}
        
        {onToggle && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="p-1.5"
            aria-label={isCollapsed ? "Oldalsáv kiterjesztése" : "Oldalsáv összecsukása"}
            aria-expanded={!isCollapsed}
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>

      {/* Navigation Menu */}
      <nav 
        className="flex-1 overflow-y-auto py-4"
        role="navigation"
        aria-label="Fő navigáció"
        ref={menuRef}
      >
        <ul className="space-y-1 px-3" role="menubar">
          {filteredMenuItems.map((item, index) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            const Icon = item.icon

            return (
              <li key={item.id} role="none">
                <Link
                  ref={el => { itemRefs.current[index] = el }}
                  href={item.href}
                  role="menuitem"
                  tabIndex={focusedIndex === index ? 0 : -1}
                  onFocus={() => setFocusedIndex(index)}
                  onBlur={() => setFocusedIndex(-1)}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors group relative",
                    "focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2",
                    isActive
                      ? "bg-blue-50 text-blue-700 border border-blue-200"
                      : "text-gray-700 hover:bg-gray-100 hover:text-gray-900",
                    isCollapsed && "justify-center px-2"
                  )}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon 
                    className={cn(
                      "flex-shrink-0 h-5 w-5",
                      isActive ? "text-blue-600" : "text-gray-500 group-hover:text-gray-700",
                      !isCollapsed && "mr-3"
                    )}
                    aria-hidden="true"
                  />
                  
                  {!isCollapsed && (
                    <>
                      <span className="truncate">{item.name}</span>
                      {item.badge && (
                        <span 
                          className="ml-auto inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                          aria-label={`${item.badge} értesítés`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}

                  {/* Tooltip for collapsed state */}
                  {isCollapsed && (
                    <div className="absolute left-full ml-2 px-2 py-1 bg-gray-900 text-white text-xs rounded opacity-0 pointer-events-none group-hover:opacity-100 transition-opacity whitespace-nowrap z-50">
                      {item.name}
                      <div className="absolute top-1/2 -left-1 w-2 h-2 bg-gray-900 rotate-45 transform -translate-y-1/2"></div>
                    </div>
                  )}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* User Profile */}
      {auth.user && (
        <div className="border-t border-gray-200 p-4">
          <div className={cn(
            "flex items-center space-x-3",
            isCollapsed && "justify-center"
          )}>
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <User className="h-4 w-4 text-gray-600" />
              </div>
            </div>
            
            {!isCollapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {auth.user.name}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {auth.user.email}
                </p>
              </div>
            )}
            
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="p-1.5"
              aria-label="Kijelentkezés"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </aside>
  )
}