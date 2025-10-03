import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { useDashboardStats, useUpcomingInspections } from '@/hooks/api'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { 
  Building2, 
  Users, 
  MapPin, 
  DoorOpen, 
  Calendar, 
  AlertTriangle,
  CheckCircle,
  Clock
} from 'lucide-react'

export function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useDashboardStats()
  const { data: upcomingInspections, isLoading: inspectionsLoading, error: inspectionsError } = useUpcomingInspections()

  if (statsLoading || inspectionsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (statsError || inspectionsError) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Hiba történt az adatok betöltése során. Kérjük, próbálja újra később.
        </AlertDescription>
      </Alert>
    )
  }

  const priorityColors = {
    LOW: 'bg-green-100 text-green-800',
    MEDIUM: 'bg-yellow-100 text-yellow-800', 
    HIGH: 'bg-orange-100 text-orange-800',
    CRITICAL: 'bg-red-100 text-red-800',
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Áttekintő nézet a rendszer állapotáról</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ügyfelek</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_clients ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Telephelyek</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_sites ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Épületek</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_buildings ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Kapuk</CardTitle>
            <DoorOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_gates ?? 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Függő ellenőrzések</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats?.pending_inspections ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lejárt ellenőrzések</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats?.overdue_inspections ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Aktív munkarendelések</CardTitle>
            <Calendar className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats?.active_work_orders ?? 0}</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Befejezett (hó)</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats?.completed_this_month ?? 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Inspections */}
      <Card>
        <CardHeader>
          <CardTitle>Közelgő ellenőrzések</CardTitle>
          <CardDescription>
            Hamarosan esedékes ellenőrzések listája
          </CardDescription>
        </CardHeader>
        <CardContent>
          {upcomingInspections && upcomingInspections.length > 0 ? (
            <div className="space-y-4">
              {upcomingInspections.slice(0, 10).map((inspection) => (
                <div 
                  key={inspection.id} 
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="font-semibold">{inspection.gate_name}</h4>
                      <Badge 
                        variant="outline"
                        className={priorityColors[inspection.priority]}
                      >
                        {inspection.priority}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{inspection.gate_location}</p>
                    <p className="text-sm text-gray-500">
                      Típus: {inspection.inspection_type}
                      {inspection.inspector_name && ` • Ellenőr: ${inspection.inspector_name}`}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="font-semibold">
                      {new Date(inspection.due_date).toLocaleDateString('hu-HU')}
                    </div>
                    <div className="text-sm text-gray-500">
                      {inspection.days_until_due} nap múlva
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Calendar className="h-12 w-12 mx-auto mb-4 text-gray-400" />
              <p>Nincsenek közelgő ellenőrzések</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}