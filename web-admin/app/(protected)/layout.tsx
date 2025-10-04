'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import { UserRole, PermissionResource, PermissionAction } from '@/lib/auth/types'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import { 
  Home, 
  Building2, 
  Users, 
  Car, 
  BarChart3, 
  Settings,
  Menu,
  LogOut,
  User,
  Shield,
  FileText
} from 'lucide-react'
import Link from 'next/link'

interface ProtectedLayoutProps {
  children: React.ReactNode
}

interface NavigationItem {
  name: string
  href: string
  icon: any
  requiredRoles?: UserRole[]
  requiredPermissions?: { resource: PermissionResource; action: PermissionAction }[]
}

// Navigation items with role-based access control
const navigation: NavigationItem[] = [
  { 
    name: 'Dashboard', 
    href: '/dashboard', 
    icon: Home 
  },
  { 
    name: 'Clients', 
    href: '/clients', 
    icon: Building2,
    requiredPermissions: [{ resource: PermissionResource.CLIENTS, action: PermissionAction.READ }]
  },
  { 
    name: 'Sites', 
    href: '/sites', 
    icon: Users,
    requiredPermissions: [{ resource: PermissionResource.SITES, action: PermissionAction.READ }]
  },
  { 
    name: 'Gates', 
    href: '/gates', 
    icon: Car,
    requiredPermissions: [{ resource: PermissionResource.GATES, action: PermissionAction.READ }]
  },
  { 
    name: 'Vehicles', 
    href: '/vehicles', 
    icon: Car,
    requiredPermissions: [{ resource: PermissionResource.VEHICLES, action: PermissionAction.READ }]
  },
  { 
    name: 'Analytics', 
    href: '/analytics', 
    icon: BarChart3,
    requiredPermissions: [{ resource: PermissionResource.ANALYTICS, action: PermissionAction.READ }]
  },
  { 
    name: 'Import', 
    href: '/import', 
    icon: FileText,
    requiredPermissions: [{ resource: PermissionResource.GATES, action: PermissionAction.CREATE }]
  },
  { 
    name: 'Users', 
    href: '/users', 
    icon: Users,
    requiredRoles: [UserRole.ADMIN, UserRole.SUPER_ADMIN],
    requiredPermissions: [{ resource: PermissionResource.USERS, action: PermissionAction.READ }]
  },
  { 
    name: 'Audit Logs', 
    href: '/audit', 
    icon: Shield,
    requiredRoles: [UserRole.ADMIN, UserRole.SUPER_ADMIN],
    requiredPermissions: [{ resource: PermissionResource.AUDIT_LOGS, action: PermissionAction.READ }]
  },
  { 
    name: 'Settings', 
    href: '/settings', 
    icon: Settings,
    requiredRoles: [UserRole.ADMIN, UserRole.SUPER_ADMIN],
    requiredPermissions: [{ resource: PermissionResource.SETTINGS, action: PermissionAction.READ }]
  },
]

export default function ProtectedLayout({ children }: ProtectedLayoutProps) {
  const router = useRouter()
  const auth = useAuth()

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!auth.isLoading && !auth.isAuthenticated) {
      router.push('/login')
    }
  }, [auth.isAuthenticated, auth.isLoading, router])

  const handleLogout = async () => {
    await auth.logout()
    router.push('/login')
  }

  // Filter navigation items based on user permissions and roles
  const filteredNavigation = navigation.filter(item => {
    // Always show items with no restrictions
    if (!item.requiredRoles && !item.requiredPermissions) {
      return true
    }

    // Check role requirements
    if (item.requiredRoles) {
      const hasRequiredRole = item.requiredRoles.some(role => auth.hasRole(role))
      if (!hasRequiredRole) return false
    }

    // Check permission requirements
    if (item.requiredPermissions) {
      const hasAllPermissions = item.requiredPermissions.every(({ resource, action }) => 
        auth.hasPermission(resource, action)
      )
      if (!hasAllPermissions) return false
    }

    return true
  })

  // Show loading state while checking authentication
  if (auth.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Don't render if not authenticated (redirect is happening)
  if (!auth.isAuthenticated) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Desktop Sidebar */}
      <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
        <div className="flex flex-col flex-grow bg-card border-r border-border pt-5 pb-4 overflow-y-auto">
          {/* Logo */}
          <div className="flex items-center flex-shrink-0 px-4">
            <h1 className="text-xl font-bold text-foreground">GarageReg Admin</h1>
          </div>
          
          {/* Navigation */}
          <nav className="mt-8 flex-1 flex flex-col divide-y divide-border overflow-y-auto" aria-label="Sidebar">
            <div className="px-2 space-y-1">
              {filteredNavigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="group flex items-center px-2 py-2 text-sm font-medium rounded-md text-secondary-700 hover:text-foreground hover:bg-secondary-100 transition-colors"
                >
                  <item.icon className="mr-3 h-5 w-5 text-secondary-400 group-hover:text-secondary-500" />
                  {item.name}
                </Link>
              ))}
            </div>
          </nav>
          
          {/* User Info */}
          {auth.user && (
            <div className="flex-shrink-0 flex border-t border-border p-4">
              <div className="flex items-center">
                <div className="inline-flex items-center justify-center h-8 w-8 rounded-full bg-primary text-primary-foreground">
                  <User className="h-4 w-4" />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-foreground">{auth.user.name}</p>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleLogout}
                    className="mt-1 text-xs text-secondary-500 hover:text-foreground p-0 h-auto"
                  >
                    <LogOut className="mr-1 h-3 w-3" />
                    Sign out
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Navigation */}
      <div className="lg:hidden">
        <div className="flex items-center justify-between bg-card border-b border-border px-4 py-3">
          <h1 className="text-lg font-semibold text-foreground">GarageReg</h1>
          
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="w-64">
              <div className="flex flex-col h-full">
                <div className="py-4">
                  <h2 className="text-lg font-semibold">Navigation</h2>
                </div>
                
                <nav className="flex-1 flex flex-col space-y-1">
                  {filteredNavigation.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      className="flex items-center px-2 py-2 text-sm font-medium rounded-md text-secondary-700 hover:text-foreground hover:bg-secondary-100"
                    >
                      <item.icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </Link>
                  ))}
                </nav>
                
                <div className="border-t border-border pt-4 mt-4">
                  {auth.user && (
                    <div className="flex items-center px-2 py-2">
                      <User className="mr-3 h-5 w-5" />
                      <span className="text-sm font-medium">{auth.user.name}</span>
                    </div>
                  )}
                  <Button
                    variant="ghost"
                    onClick={handleLogout}
                    className="flex items-center w-full px-2 py-2 text-sm justify-start"
                  >
                    <LogOut className="mr-3 h-5 w-5" />
                    Sign out
                  </Button>
                </div>
              </div>
            </SheetContent>
          </Sheet>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-64 flex flex-col flex-1">
        <main className="flex-1">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}