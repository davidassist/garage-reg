'use client'

import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { ChevronRight, Home } from 'lucide-react'
import { cn } from '@/lib/utils'

interface BreadcrumbItem {
  label: string
  href?: string
  icon?: any
  isActive?: boolean
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[]
  className?: string
  separator?: React.ReactNode
}

// Route mapping for Hungarian labels
const routeMapping: Record<string, string> = {
  'dashboard': 'Irányítópult',
  'clients': 'Ügyfelek',
  'sites': 'Telephelyek',
  'buildings': 'Épületek',
  'gates': 'Kapuk',
  'inspections': 'Ellenőrzések',
  'tickets': 'Hibajegyek',
  'workorders': 'Munkalapok',
  'documents': 'Dokumentumok',
  'reports': 'Riportok',
  'inventory': 'Raktár',
  'settings': 'Beállítások',
  'profile': 'Profil',
  'users': 'Felhasználók',
  'general': 'Általános',
  'security': 'Biztonság',
  'new': 'Új',
  'edit': 'Szerkesztés',
  'view': 'Megtekintés',
  'list': 'Lista',
  'map': 'Térkép',
  'pending': 'Függő',
  'completed': 'Befejezett',
  'schedule': 'Ütemezés',
  'active': 'Aktív',
  'templates': 'Sablonok',
  'generated': 'Generált',
  'performance': 'Teljesítmény',
  'compliance': 'Megfelelőség',
  'custom': 'Egyedi',
  'items': 'Tételek',
  'low-stock': 'Alacsony készlet',
}

// Generate breadcrumb items from current pathname
const generateBreadcrumbsFromPath = (pathname: string): BreadcrumbItem[] => {
  // Remove leading slash and split by '/'
  const segments = pathname.replace(/^\//, '').split('/').filter(Boolean)
  
  if (segments.length === 0) {
    return [{ label: 'Irányítópult', href: '/dashboard', icon: Home, isActive: true }]
  }

  const breadcrumbs: BreadcrumbItem[] = [
    { label: 'Főoldal', href: '/dashboard', icon: Home }
  ]

  let currentPath = ''
  
  segments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const isLast = index === segments.length - 1
    
    // Get Hungarian label or fallback to segment
    const label = routeMapping[segment] || segment.charAt(0).toUpperCase() + segment.slice(1)
    
    breadcrumbs.push({
      label,
      href: isLast ? undefined : currentPath,
      isActive: isLast
    })
  })

  return breadcrumbs
}

export default function Breadcrumbs({ 
  items, 
  className, 
  separator = <ChevronRight className="h-4 w-4 text-gray-400" aria-hidden="true" />
}: BreadcrumbsProps) {
  const pathname = usePathname()
  
  // Use provided items or generate from pathname
  const breadcrumbItems = items || generateBreadcrumbsFromPath(pathname)

  // Don't show breadcrumbs if there's only one item (homepage)
  if (breadcrumbItems.length <= 1) {
    return null
  }

  return (
    <nav 
      className={cn('flex', className)}
      aria-label="Breadcrumb navigáció"
      role="navigation"
    >
      <ol 
        className="flex items-center space-x-2 text-sm"
        role="list"
      >
        {breadcrumbItems.map((item, index) => {
          const Icon = item.icon
          const isLast = index === breadcrumbItems.length - 1

          return (
            <li 
              key={index}
              className="flex items-center"
              role="listitem"
            >
              {/* Separator (except for first item) */}
              {index > 0 && (
                <span className="mx-2" aria-hidden="true">
                  {separator}
                </span>
              )}

              {/* Breadcrumb item */}
              {item.href && !isLast ? (
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center text-gray-500 hover:text-gray-700 transition-colors duration-200 focus:outline-none focus:text-gray-700 focus:underline',
                    'rounded px-1 py-0.5 focus:ring-2 focus:ring-blue-500 focus:ring-offset-1'
                  )}
                  aria-label={`Navigálás ide: ${item.label}`}
                >
                  {Icon && (
                    <Icon 
                      className="h-4 w-4 mr-1 flex-shrink-0" 
                      aria-hidden="true"
                    />
                  )}
                  <span className="truncate max-w-xs">{item.label}</span>
                </Link>
              ) : (
                <span
                  className={cn(
                    'flex items-center',
                    isLast 
                      ? 'text-gray-900 font-medium' 
                      : 'text-gray-500'
                  )}
                  aria-current={isLast ? 'page' : undefined}
                  aria-label={isLast ? `Jelenlegi oldal: ${item.label}` : item.label}
                >
                  {Icon && (
                    <Icon 
                      className="h-4 w-4 mr-1 flex-shrink-0" 
                      aria-hidden="true"
                    />
                  )}
                  <span className="truncate max-w-xs">{item.label}</span>
                </span>
              )}
            </li>
          )
        })}
      </ol>
    </nav>
  )
}

// Utility function to create custom breadcrumbs
export const createBreadcrumbs = (items: Omit<BreadcrumbItem, 'isActive'>[]): BreadcrumbItem[] => {
  return items.map((item, index) => ({
    ...item,
    isActive: index === items.length - 1
  }))
}

// Common breadcrumb patterns for easy reuse
export const commonBreadcrumbs = {
  // Client management
  clients: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Ügyfelek', href: '/clients' }
  ]),
  
  clientNew: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Ügyfelek', href: '/clients' },
    { label: 'Új ügyfél' }
  ]),
  
  clientEdit: (clientName?: string) => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Ügyfelek', href: '/clients' },
    { label: clientName || 'Ügyfél szerkesztése' }
  ]),

  // Site management
  sites: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Telephelyek', href: '/sites' }
  ]),
  
  siteView: (siteName?: string) => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Telephelyek', href: '/sites' },
    { label: siteName || 'Telephely részletei' }
  ]),

  // Inspection management  
  inspections: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Ellenőrzések', href: '/inspections' }
  ]),
  
  inspectionsPending: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Ellenőrzések', href: '/inspections' },
    { label: 'Függő ellenőrzések' }
  ]),

  // Settings
  settings: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Beállítások', href: '/settings' }
  ]),
  
  settingsUsers: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Beállítások', href: '/settings' },
    { label: 'Felhasználók' }
  ]),

  // Reports
  reports: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Riportok', href: '/reports' }
  ]),
  
  reportsPerformance: () => createBreadcrumbs([
    { label: 'Főoldal', href: '/dashboard', icon: Home },
    { label: 'Riportok', href: '/reports' },
    { label: 'Teljesítmény riportok' }
  ]),
}