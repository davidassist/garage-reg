'use client'

import { useEffect, useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Users,
  Building2,
  Car,
  Shield,
  Activity,
  TrendingUp,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  Clock,
  Package
} from 'lucide-react'

// Mock data interfaces
interface DashboardStats {
  clients: number
  sites: number
  gates: number
  inspections: number
}

interface RecentActivity {
  id: string
  type: 'inspection' | 'maintenance' | 'alert'
  title: string
  time: string
  status: 'completed' | 'pending' | 'warning'
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    clients: 0,
    sites: 0,
    gates: 0,
    inspections: 0
  })
  
  const [activities, setActivities] = useState<RecentActivity[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Mock API call to fetch dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        setStats({
          clients: 45,
          sites: 23,
          gates: 156,
          inspections: 89
        })
        
        setActivities([
          {
            id: '1',
            type: 'inspection',
            title: 'Kapu #156 rendszeres ellenőrzés befejezve',
            time: '2 órája',
            status: 'completed'
          },
          {
            id: '2', 
            type: 'maintenance',
            title: 'ABC Kft. telephely karbantartás ütemezve',
            time: '4 órája',
            status: 'pending'
          },
          {
            id: '3',
            type: 'alert',
            title: 'Kapu #23 szenzor hiba észlelve',
            time: '6 órája',
            status: 'warning'
          },
          {
            id: '4',
            type: 'inspection',
            title: 'XYZ Kft. biztonsági audit befejezve',
            time: '1 napja',
            status: 'completed'
          }
        ])
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchDashboardData()
  }, [])

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'inspection': return Shield
      case 'maintenance': return Package
      case 'alert': return AlertCircle
      default: return Activity
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-success-600'
      case 'pending': return 'text-warning-600'
      case 'warning': return 'text-error-600'
      default: return 'text-secondary-600'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return CheckCircle2
      case 'pending': return Clock
      case 'warning': return AlertCircle
      default: return Activity
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-secondary-200 rounded w-1/4 mb-4"></div>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-32 bg-secondary-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-secondary-600 mt-1">
            Welcome back! Here's what's happening with your garage systems.
          </p>
        </div>
        <Button>
          <Activity className="mr-2 h-4 w-4" />
          View All Activities
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Clients</CardTitle>
            <Users className="h-4 w-4 text-secondary-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.clients}</div>
            <p className="text-xs text-secondary-600">
              <span className="inline-flex items-center text-success-600">
                <TrendingUp className="mr-1 h-3 w-3" />
                +12%
              </span>
              {' '}from last month
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sites</CardTitle>
            <Building2 className="h-4 w-4 text-secondary-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.sites}</div>
            <p className="text-xs text-secondary-600">
              <span className="inline-flex items-center text-success-600">
                <TrendingUp className="mr-1 h-3 w-3" />
                +3
              </span>
              {' '}new this year
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Gates</CardTitle>
            <Car className="h-4 w-4 text-secondary-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.gates}</div>
            <p className="text-xs text-secondary-600">
              <span className="inline-flex items-center text-success-600">
                <CheckCircle2 className="mr-1 h-3 w-3" />
                98%
              </span>
              {' '}operational
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Inspections</CardTitle>
            <Shield className="h-4 w-4 text-secondary-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.inspections}</div>
            <p className="text-xs text-secondary-600">
              <span className="inline-flex items-center text-success-600">
                <TrendingUp className="mr-1 h-3 w-3" />
                +15
              </span>
              {' '}this month
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activities */}
      <div className="grid gap-6 lg:grid-cols-7">
        <Card className="lg:col-span-4">
          <CardHeader>
            <CardTitle>Recent Activities</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activities.map((activity) => {
                const ActivityIcon = getActivityIcon(activity.type)
                const StatusIcon = getStatusIcon(activity.status)
                
                return (
                  <div key={activity.id} className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <ActivityIcon className="h-5 w-5 text-secondary-500" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground">
                        {activity.title}
                      </p>
                      <p className="text-sm text-secondary-600">{activity.time}</p>
                    </div>
                    <div className="flex-shrink-0">
                      <StatusIcon className={`h-4 w-4 ${getStatusColor(activity.status)}`} />
                    </div>
                  </div>
                )
              })}
            </div>
          </CardContent>
        </Card>

        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" variant="outline">
              <Shield className="mr-2 h-4 w-4" />
              Schedule Inspection
              <ArrowRight className="ml-auto h-4 w-4" />
            </Button>
            
            <Button className="w-full justify-start" variant="outline">
              <Car className="mr-2 h-4 w-4" />
              Add New Gate
              <ArrowRight className="ml-auto h-4 w-4" />
            </Button>
            
            <Button className="w-full justify-start" variant="outline">
              <Users className="mr-2 h-4 w-4" />
              Manage Clients
              <ArrowRight className="ml-auto h-4 w-4" />
            </Button>
            
            <Button className="w-full justify-start" variant="outline">
              <Building2 className="mr-2 h-4 w-4" />
              View All Sites
              <ArrowRight className="ml-auto h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-success-600" />
              <span className="text-sm">API Services</span>
              <Badge variant="secondary" className="bg-success-100 text-success-800">
                Operational
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="h-5 w-5 text-success-600" />
              <span className="text-sm">Database</span>
              <Badge variant="secondary" className="bg-success-100 text-success-800">
                Healthy
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-warning-600" />
              <span className="text-sm">Background Jobs</span>
              <Badge variant="secondary" className="bg-warning-100 text-warning-800">
                1 Delayed
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}