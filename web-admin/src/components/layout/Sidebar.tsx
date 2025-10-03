'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import { PermissionResource, PermissionAction } from '@/lib/auth/types'
import { 
  LayoutDashboard,
  Users,
  Building2,
  Home,
  DoorOpen,
  Shield,
  Bug,
  FileText,
  FolderOpen,
  BarChart3,
  Package,
  Settings,
  ChevronRight,
  ChevronDown,
  X,
  Menu,
  QrCode
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface MenuItem {
  id: string
  name: string
  href: string
  icon: any
  badge?: number
  children?: MenuItem[]
  requiredPermission?: {
    resource: PermissionResource
    action: PermissionAction
  }
  requiredRole?: string[]
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    id: 'clients',
    name: 'Ügyfelek',
    href: '/clients',
    icon: Users,
    requiredPermission: {
      resource: PermissionResource.USERS,
      action: PermissionAction.READ,
    },
    children: [
      {
        id: 'clients-list',
        name: 'Ügyfél lista',
        href: '/clients',
        icon: Users,
      },
      {
        id: 'clients-new',
        name: 'Új ügyfél',
        href: '/clients/new',
        icon: Users,
        requiredPermission: {
          resource: PermissionResource.USERS,
          action: PermissionAction.CREATE,
        },
      },
    ],
  },
  {
    id: 'sites',
    name: 'Telephelyek',
    href: '/sites',
    icon: Building2,
    requiredPermission: {
      resource: PermissionResource.VEHICLES, // Using vehicles as site management
      action: PermissionAction.READ,
    },
    children: [
      {
        id: 'sites-list',
        name: 'Telephely lista',
        href: '/sites',
        icon: Building2,
      },
      {
        id: 'sites-map',
        name: 'Térkép nézet',
        href: '/sites/map',
        icon: Building2,
      },
    ],
  },
  {
    id: 'buildings',
    name: 'Épületek',
    href: '/buildings',
    icon: Home,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    },
  },
  {
    id: 'gates',
    name: 'Kapuk',
    href: '/gates',
    icon: DoorOpen,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    },
    badge: 3, // Example: 3 gates need attention
  },
  {
    id: 'inspections',
    name: 'Ellenőrzések',
    href: '/inspections',
    icon: Shield,
    requiredPermission: {
      resource: PermissionResource.REGISTRATIONS,
      action: PermissionAction.READ,
    },
    children: [
      {
        id: 'inspections-pending',
        name: 'Függő ellenőrzések',
        href: '/inspections/pending',
        icon: Shield,
        badge: 12,
      },
      {
        id: 'inspections-completed',
        name: 'Befejezett ellenőrzések',
        href: '/inspections/completed',
        icon: Shield,
      },
      {
        id: 'inspections-schedule',
        name: 'Ütemezés',
        href: '/inspections/schedule',
        icon: Shield,
      },
    ],
  },
  {
    id: 'tickets',
    name: 'Hibajegyek',
    href: '/tickets',
    icon: Bug,
    requiredPermission: {
      resource: PermissionResource.REGISTRATIONS,
      action: PermissionAction.READ,
    },
    badge: 7, // Example: 7 open tickets
  },
  {
    id: 'workorders',
    name: 'Munkalapok',
    href: '/workorders',
    icon: FileText,
    requiredPermission: {
      resource: PermissionResource.REGISTRATIONS,
      action: PermissionAction.READ,
    },
    children: [
      {
        id: 'workorders-active',
        name: 'Aktív munkalapok',
        href: '/workorders/active',
        icon: FileText,
        badge: 5,
      },
      {
        id: 'workorders-completed',
        name: 'Befejezett munkalapok',
        href: '/workorders/completed',
        icon: FileText,
      },
    ],
  },
  {
    id: 'documents',
    name: 'Dokumentumok',
    href: '/documents',
    icon: FolderOpen,
    requiredPermission: {
      resource: PermissionResource.REGISTRATIONS,
      action: PermissionAction.READ,
    },
    children: [
      {
        id: 'documents-templates',
        name: 'Sablonok',
        href: '/documents/templates',
        icon: FolderOpen,
      },
      {
        id: 'documents-generated',
        name: 'Generált dokumentumok',
        href: '/documents/generated',
        icon: FolderOpen,
      },
    ],
  },
  {
    id: 'reports',
    name: 'Riportok',
    href: '/reports',
    icon: BarChart3,
    requiredPermission: {
      resource: PermissionResource.ANALYTICS,
      action: PermissionAction.READ,
    },
    children: [
      {
        id: 'reports-performance',
        name: 'Teljesítmény riportok',
        href: '/reports/performance',
        icon: BarChart3,
      },
      {
        id: 'reports-compliance',
        name: 'Megfelelőségi riportok',
        href: '/reports/compliance',
        icon: BarChart3,
      },
      {
        id: 'reports-custom',
        name: 'Egyedi riportok',
        href: '/reports/custom',
        icon: BarChart3,
        requiredPermission: {
          resource: PermissionResource.ANALYTICS,
          action: PermissionAction.CREATE,
        },
      },
    ],
  },
  {
    id: 'labels',
    name: 'Címkék',
    href: '/labels',
    icon: QrCode,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    },
  },
  {
    id: 'inventory',
    name: 'Raktár',
    href: '/inventory',
    icon: Package,
    requiredPermission: {
      resource: PermissionResource.VEHICLES,
      action: PermissionAction.READ,
    },
    children: [
      {
        id: 'inventory-items',
        name: 'Raktári tételek',
        href: '/inventory/items',
        icon: Package,
      },
      {
        id: 'inventory-low-stock',
        name: 'Alacsony készlet',
        href: '/inventory/low-stock',
        icon: Package,
        badge: 8,
      },
    ],
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
    children: [
      {
        id: 'settings-general',
        name: 'Általános beállítások',
        href: '/settings/general',
        icon: Settings,
      },
      {
        id: 'settings-users',
        name: 'Felhasználók',
        href: '/settings/users',
        icon: Settings,
        requiredPermission: {
          resource: PermissionResource.USERS,
          action: PermissionAction.MANAGE,
        },
      },
      {
        id: 'settings-api-test',
        name: 'API Hibakezelés Teszt',
        href: '/api-test',
        icon: Settings,
        requiredPermission: {
          resource: PermissionResource.SETTINGS,
          action: PermissionAction.READ,
        },
      },
      {
        id: 'settings-security',
        name: 'Biztonsági beállítások',
        href: '/settings/security',
        icon: Settings,
        requiredRole: ['admin', 'super_admin'],
      },
    ],
  },
]

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
  className?: string
}

export default function Sidebar({ isOpen, onClose, className }: SidebarProps) {
  const pathname = usePathname()
  const { checkPermission, hasRole } = useAuth()
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set(['dashboard']))

  // Filter menu items based on user permissions
  const filterMenuItems = (items: MenuItem[]): MenuItem[] => {
    return items.filter(item => {
      // Check role requirement
      if (item.requiredRole) {
        const hasRequiredRole = item.requiredRole.some(role => hasRole(role))
        if (!hasRequiredRole) return false
      }
      
      // Check permission requirement
      if (item.requiredPermission) {
        const hasPermission = checkPermission(
          item.requiredPermission.resource,
          item.requiredPermission.action
        )
        if (!hasPermission) return false
      }
      
      // Filter children recursively
      if (item.children) {
        item.children = filterMenuItems(item.children)
      }
      
      return true
    })
  }

  const filteredMenuItems = filterMenuItems([...menuItems])

  const toggleExpanded = (itemId: string) => {
    const newExpanded = new Set(expandedItems)
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId)
    } else {
      newExpanded.add(itemId)
    }
    setExpandedItems(newExpanded)
  }

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/')
  }

  const handleKeyDown = (event: React.KeyboardEvent, action: () => void) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault()
      action()
    }
  }

  const renderMenuItem = (item: MenuItem, level: number = 0) => {
    const Icon = item.icon
    const isExpanded = expandedItems.has(item.id)
    const itemIsActive = isActive(item.href)
    const hasChildren = item.children && item.children.length > 0

    return (
      <li key={item.id} className="mb-1">
        <div className="relative">
          {hasChildren ? (
            // Expandable menu item
            <button
              onClick={() => toggleExpanded(item.id)}
              onKeyDown={(e) => handleKeyDown(e, () => toggleExpanded(item.id))}
              className={cn(
                'w-full flex items-center justify-between px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                level === 0 ? 'pl-3' : 'pl-8',
                itemIsActive
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              )}
              aria-expanded={isExpanded}
              aria-controls={`submenu-${item.id}`}
              aria-label={`${item.name} menü ${isExpanded ? 'bezárása' : 'kinyitása'}`}
            >
              <div className="flex items-center">
                <Icon 
                  className={cn(
                    'h-5 w-5 mr-3 flex-shrink-0',
                    itemIsActive ? 'text-blue-600' : 'text-gray-400'
                  )} 
                  aria-hidden="true"
                />
                <span className="truncate">{item.name}</span>
                {item.badge && (
                  <span 
                    className="ml-2 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full"
                    aria-label={`${item.badge} új elem`}
                  >
                    {item.badge}
                  </span>
                )}
              </div>
              <ChevronRight 
                className={cn(
                  'h-4 w-4 transition-transform duration-200',
                  isExpanded ? 'transform rotate-90' : ''
                )}
                aria-hidden="true"
              />
            </button>
          ) : (
            // Regular menu item
            <Link
              href={item.href}
              onClick={onClose}
              onKeyDown={(e) => handleKeyDown(e, () => {
                window.location.href = item.href
                onClose()
              })}
              className={cn(
                'flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
                level === 0 ? 'pl-3' : 'pl-8',
                itemIsActive
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
              )}
              aria-current={itemIsActive ? 'page' : undefined}
            >
              <Icon 
                className={cn(
                  'h-5 w-5 mr-3 flex-shrink-0',
                  itemIsActive ? 'text-blue-600' : 'text-gray-400'
                )} 
                aria-hidden="true"
              />
              <span className="truncate">{item.name}</span>
              {item.badge && (
                <span 
                  className="ml-auto inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-red-100 bg-red-600 rounded-full"
                  aria-label={`${item.badge} új elem`}
                >
                  {item.badge}
                </span>
              )}
            </Link>
          )}

          {/* Submenu */}
          {hasChildren && isExpanded && (
            <ul 
              id={`submenu-${item.id}`}
              className="mt-1 space-y-1"
              role="menu"
              aria-label={`${item.name} almenü`}
            >
              {item.children?.map(child => renderMenuItem(child, level + 1))}
            </ul>
          )}
        </div>
      </li>
    )
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 shadow-lg transform transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          className
        )}
        aria-label="Fő navigáció"
        role="navigation"
      >
        {/* Header */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <div className="flex items-center">
            <h1 className="text-lg font-semibold text-gray-900">GarageReg</h1>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="Navigáció bezárása"
          >
            <X className="h-5 w-5" aria-hidden="true" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 overflow-y-auto" aria-label="Fő menü">
          <ul className="space-y-1" role="menubar">
            {filteredMenuItems.map(item => renderMenuItem(item))}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 text-center">
            © 2025 GarageReg
          </div>
        </div>
      </aside>
    </>
  )
}