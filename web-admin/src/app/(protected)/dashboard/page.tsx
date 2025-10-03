'use client'

import { useAuth } from '@/lib/auth/context'
import { withRequiredAuth } from '@/lib/auth/with-auth'
import { 
  Home,
  Users,
  Building2,
  DoorOpen,
  Shield,
  Bug,
  FileText,
  Package,
  AlertTriangle,
  TrendingUp,
  Activity,
  CheckCircle,
  Clock,
  ArrowRight,
  BarChart3,
  Bell
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface DashboardCard {
  title: string
  value: string | number
  change?: {
    value: number
    label: string
    trend: 'up' | 'down' | 'neutral'
  }
  icon: React.ElementType
  color: string
  href?: string
}

interface Activity {
  id: string
  type: 'inspection' | 'ticket' | 'maintenance' | 'alert'
  title: string
  description: string
  time: Date
  status: 'success' | 'warning' | 'error' | 'info'
  user?: string
}

const dashboardCards: DashboardCard[] = [
  {
    title: 'Aktív ügyfelek',
    value: 45,
    change: { value: 12, label: 'Ez hónapban', trend: 'up' },
    icon: Users,
    color: 'bg-blue-500',
    href: '/clients'
  },
  {
    title: 'Telephelyek száma',
    value: 23,
    change: { value: 3, label: 'Ez évben', trend: 'up' },
    icon: Building2,
    color: 'bg-green-500',
    href: '/sites'
  },
  {
    title: 'Aktív kapuk',
    value: 156,
    change: { value: 8, label: 'Működik', trend: 'neutral' },
    icon: DoorOpen,
    color: 'bg-purple-500',
    href: '/gates'
  },
  {
    title: 'Nyitott hibajegyek',
    value: 12,
    change: { value: -3, label: 'Ez héten', trend: 'down' },
    icon: Bug,
    color: 'bg-red-500',
    href: '/tickets'
  },
  {
    title: 'Ellenőrzések (hónap)',
    value: 89,
    change: { value: 15, label: 'Befejezve', trend: 'up' },
    icon: Shield,
    color: 'bg-indigo-500',
    href: '/inspections'
  },
  {
    title: 'Raktári tételek',
    value: '2.3K',
    change: { value: 156, label: 'Készleten', trend: 'up' },
    icon: Package,
    color: 'bg-yellow-500',
    href: '/inventory'
  }
]

const recentActivities: Activity[] = [
  {
    id: '1',
    type: 'inspection',
    title: 'Biztonsági ellenőrzés befejezve',
    description: 'ABC Logistics - Budapest Raktárközpont',
    time: new Date(Date.now() - 30 * 60 * 1000),
    status: 'success',
    user: 'Nagy Péter'
  },
  {
    id: '2',
    type: 'ticket',
    title: 'Új hibajegy létrehozva',
    description: 'Kapu A-003 szenzor hibája',
    time: new Date(Date.now() - 1 * 60 * 60 * 1000),
    status: 'error',
    user: 'Kiss Anna'
  },
  {
    id: '3',
    type: 'maintenance',
    title: 'Karbantartás ütemezve',
    description: 'Kapu B-007 - 2025.01.15',
    time: new Date(Date.now() - 2 * 60 * 60 * 1000),
    status: 'warning',
    user: 'Kovács János'
  },
  {
    id: '4',
    type: 'alert',
    title: 'Rendszer frissítés',
    description: 'Új funkciók és javítások',
    time: new Date(Date.now() - 4 * 60 * 60 * 1000),
    status: 'info',
    user: 'Rendszer'
  }
]

const quickActions = [
  {
    title: 'Új ügyfél hozzáadása',
    description: 'Új ügyfél regisztrálása a rendszerben',
    icon: Users,
    href: '/clients/new',
    color: 'bg-blue-50 text-blue-600 border-blue-200'
  },
  {
    title: 'Ellenőrzés indítása',
    description: 'Új biztonsági ellenőrzés kezdeményezése',
    icon: Shield,
    href: '/inspections/new',
    color: 'bg-green-50 text-green-600 border-green-200'
  },
  {
    title: 'Hibajegy létrehozása',
    description: 'Új probléma jelentése és nyomon követése',
    icon: Bug,
    href: '/tickets/new',
    color: 'bg-red-50 text-red-600 border-red-200'
  },
  {
    title: 'Riport generálása',
    description: 'Összesítő riport készítése',
    icon: BarChart3,
    href: '/reports/new',
    color: 'bg-purple-50 text-purple-600 border-purple-200'
  }
]

function Dashboard() {
  const { user } = useAuth()

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))
    
    if (diffInMinutes < 1) return 'Most'
    if (diffInMinutes < 60) return `${diffInMinutes} perce`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} órája`
    return `${Math.floor(diffInMinutes / 1440)} napja`
  }

  const getTrendIcon = (trend: 'up' | 'down' | 'neutral') => {
    if (trend === 'up') return <TrendingUp className="h-4 w-4 text-green-500" />
    if (trend === 'down') return <TrendingUp className="h-4 w-4 text-red-500 rotate-180" />
    return <Activity className="h-4 w-4 text-gray-500" />
  }

  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'inspection': return Shield
      case 'ticket': return Bug
      case 'maintenance': return FileText
      case 'alert': return Bell
    }
  }

  const getActivityColor = (status: Activity['status']) => {
    switch (status) {
      case 'success': return 'bg-green-50 text-green-700'
      case 'warning': return 'bg-yellow-50 text-yellow-700'
      case 'error': return 'bg-red-50 text-red-700'
      case 'info': return 'bg-blue-50 text-blue-700'
    }
  }

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Üdvözöljük, {user?.name}!
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Itt áttekintést kap a rendszer aktuális állapotáról
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-500">
              Utolsó frissítés: {new Date().toLocaleString('hu-HU')}
            </span>
          </div>
        </div>
      </div>

      {/* Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {dashboardCards.map((card) => {
          const Icon = card.icon
          return (
            <div
              key={card.title}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    {card.title}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {card.value}
                  </p>
                </div>
                <div className={cn('p-3 rounded-lg', card.color)}>
                  <Icon className="h-6 w-6 text-white" />
                </div>
              </div>
              
              {card.change && (
                <div className="flex items-center mt-4">
                  {getTrendIcon(card.change.trend)}
                  <span className="ml-2 text-sm text-gray-600">
                    <span className={cn(
                      'font-medium',
                      card.change.trend === 'up' ? 'text-green-600' :
                      card.change.trend === 'down' ? 'text-red-600' :
                      'text-gray-600'
                    )}>
                      {card.change.trend === 'up' ? '+' : ''}
                      {card.change.value}
                    </span>
                    {' '}{card.change.label}
                  </span>
                </div>
              )}
              
              {card.href && (
                <div className="mt-4">
                  <a
                    href={card.href}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center"
                  >
                    Részletek megtekintése
                    <ArrowRight className="h-4 w-4 ml-1" />
                  </a>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">
                  Legutóbbi tevékenységek
                </h2>
                <a
                  href="/activity"
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Összes megtekintése
                </a>
              </div>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                {recentActivities.map((activity) => {
                  const Icon = getActivityIcon(activity.type)
                  return (
                    <div
                      key={activity.id}
                      className="flex items-start space-x-3"
                    >
                      <div className={cn(
                        'p-2 rounded-lg',
                        getActivityColor(activity.status)
                      )}>
                        <Icon className="h-4 w-4" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.title}
                        </p>
                        <p className="text-sm text-gray-600">
                          {activity.description}
                        </p>
                        <div className="flex items-center mt-1 text-xs text-gray-500">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatTimeAgo(activity.time)}
                          {activity.user && (
                            <>
                              <span className="mx-1">•</span>
                              {activity.user}
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Gyors műveletek
              </h2>
            </div>
            
            <div className="p-6">
              <div className="space-y-3">
                {quickActions.map((action) => {
                  const Icon = action.icon
                  return (
                    <a
                      key={action.title}
                      href={action.href}
                      className="flex items-start p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className={cn('p-2 rounded-lg mr-3', action.color)}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          {action.title}
                        </p>
                        <p className="text-xs text-gray-600 mt-1">
                          {action.description}
                        </p>
                      </div>
                    </a>
                  )
                })}
              </div>
            </div>
          </div>

          {/* System Status */}
          <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Rendszer állapot
              </h2>
            </div>
            
            <div className="p-6">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">API szolgáltatás</span>
                  <div className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm text-green-600">Működik</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Adatbázis</span>
                  <div className="flex items-center">
                    <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
                    <span className="text-sm text-green-600">Működik</span>
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Értesítések</span>
                  <div className="flex items-center">
                    <AlertTriangle className="h-4 w-4 text-yellow-500 mr-1" />
                    <span className="text-sm text-yellow-600">Karbantartás</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default withRequiredAuth(Dashboard)