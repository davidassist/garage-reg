import { ReactNode, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/auth'
import { usePermissions } from '@/hooks/permissions'
import { Button } from '@/components/ui/button'
import { 
  Building2, 
  Users, 
  MapPin, 
  DoorOpen, 
  LayoutDashboard,
  Menu,
  X,
  LogOut,
  User,
  FileSearch
} from 'lucide-react'

interface LayoutProps {
  children: ReactNode
}

interface NavItem {
  path: string
  label: string
  icon: React.ElementType
  permission?: { resource: string; action: string }
}

export function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { user, logout } = useAuthStore()
  const { hasPermission } = usePermissions()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const navItems: NavItem[] = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      path: '/clients',
      label: 'Ügyfelek',
      icon: Users,
      permission: { resource: 'clients', action: 'read' },
    },
    {
      path: '/sites',
      label: 'Telephelyek',
      icon: MapPin,
      permission: { resource: 'sites', action: 'read' },
    },
    {
      path: '/buildings',
      label: 'Épületek',
      icon: Building2,
      permission: { resource: 'buildings', action: 'read' },
    },
    {
      path: '/gates',
      label: 'Kapuk',
      icon: DoorOpen,
      permission: { resource: 'gates', action: 'read' },
    },
    {
      path: '/audit',
      label: 'Audit Naplók',
      icon: FileSearch,
      permission: { resource: 'reports', action: 'read' },
    },
  ]

  const filteredNavItems = navItems.filter(item => {
    if (!item.permission) return true
    return hasPermission(item.permission.resource as any, item.permission.action as any)
  })

  const handleLogout = () => {
    logout()
    window.location.href = '/'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-200 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:inset-0
      `}>
        <div className="flex items-center justify-between h-16 px-4 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">GarageReg Admin</h1>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 px-2 py-4 space-y-1">
          {filteredNavItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path || 
                           (item.path !== '/dashboard' && location.pathname.startsWith(item.path))
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors
                  ${isActive 
                    ? 'bg-primary text-primary-foreground' 
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }
                `}
                onClick={() => setSidebarOpen(false)}
              >
                <Icon className="mr-3 h-5 w-5 flex-shrink-0" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        {/* User info and logout */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-primary-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.display_name || `${user?.first_name} ${user?.last_name}` || user?.username}
              </p>
              <p className="text-xs text-gray-500 truncate">
                {user?.email}
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="w-full"
            onClick={handleLogout}
          >
            <LogOut className="mr-2 h-4 w-4" />
            Kijelentkezés
          </Button>
        </div>
      </div>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between h-16 px-4">
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(true)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            
            <div className="hidden lg:block">
              <h2 className="text-lg font-semibold text-gray-900">
                {navItems.find(item => {
                  const isActive = location.pathname === item.path || 
                                 (item.path !== '/dashboard' && location.pathname.startsWith(item.path))
                  return isActive
                })?.label || 'Dashboard'}
              </h2>
            </div>

            <div className="lg:hidden">
              <span className="text-sm font-medium text-gray-900">
                {user?.display_name || `${user?.first_name} ${user?.last_name}` || user?.username}
              </span>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  )
}