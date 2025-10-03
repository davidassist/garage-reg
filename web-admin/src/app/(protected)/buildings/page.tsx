'use client'

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter, useSearchParams } from 'next/navigation'
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Building2, 
  DoorOpen,
  Users,
  MoreHorizontal,
  Filter,
  Download,
  Upload,
  ArrowLeft,
  Calendar,
  CheckCircle,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { withAuth } from '@/lib/auth/with-auth'
import { PermissionResource, PermissionAction } from '@/lib/auth/types'
import { cn } from '@/lib/utils'

// Temporary toast implementation
const toast = ({ title, description, variant }: { title: string, description: string, variant?: string }) => {
  console.log(`${variant === 'destructive' ? 'ERROR' : 'INFO'}: ${title} - ${description}`)
  alert(`${title}: ${description}`)
}

interface Building {
  id: string
  name: string
  siteId: string
  siteName: string
  clientName: string
  buildingType: 'residential' | 'office' | 'industrial' | 'mixed'
  floors: number
  units: number
  gatesCount: number
  status: 'active' | 'inactive' | 'maintenance' | 'construction'
  lastInspection: string | null
  nextInspection: string
  contactPerson: string
  contactPhone: string
  createdAt: string
  updatedAt: string
}

const mockBuildings: Building[] = [
  {
    id: '1',
    name: 'A épület',
    siteId: '1',
    siteName: 'Buda Castle Business Center',
    clientName: 'Budapesti Városkapu Kft.',
    buildingType: 'office',
    floors: 12,
    units: 48,
    gatesCount: 3,
    status: 'active',
    lastInspection: '2024-08-15T10:00:00Z',
    nextInspection: '2024-11-15T10:00:00Z',
    contactPerson: 'Nagy Péter',
    contactPhone: '+36 1 234 5678',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-10-01T14:30:00Z'
  },
  {
    id: '2',
    name: 'B épület',
    siteId: '1',
    siteName: 'Buda Castle Business Center',
    clientName: 'Budapesti Városkapu Kft.',
    buildingType: 'office',
    floors: 8,
    units: 32,
    gatesCount: 2,
    status: 'active',
    lastInspection: '2024-09-20T14:00:00Z',
    nextInspection: '2024-12-20T14:00:00Z',
    contactPerson: 'Nagy Péter',
    contactPhone: '+36 1 234 5678',
    createdAt: '2024-02-01T09:15:00Z',
    updatedAt: '2024-09-28T16:45:00Z'
  },
  {
    id: '3',
    name: 'Lakótömb 1',
    siteId: '3',
    siteName: 'Debrecen Industrial Park',
    clientName: 'Debreceni Lakópark Zrt.',
    buildingType: 'residential',
    floors: 4,
    units: 24,
    gatesCount: 1,
    status: 'maintenance',
    lastInspection: '2024-06-10T11:30:00Z',
    nextInspection: '2024-10-15T11:30:00Z', // Overdue
    contactPerson: 'Szabó László',
    contactPhone: '+36 52 123 456',
    createdAt: '2024-03-10T11:30:00Z',
    updatedAt: '2024-08-15T13:20:00Z'
  }
]

const buildingTypeConfig = {
  residential: { label: 'Lakó', className: 'bg-blue-100 text-blue-800 border-blue-200' },
  office: { label: 'Iroda', className: 'bg-green-100 text-green-800 border-green-200' },
  industrial: { label: 'Ipari', className: 'bg-gray-100 text-gray-800 border-gray-200' },
  mixed: { label: 'Vegyes', className: 'bg-purple-100 text-purple-800 border-purple-200' }
}

const statusConfig = {
  active: { 
    label: 'Aktív', 
    className: 'bg-green-100 text-green-800 border-green-200',
    icon: CheckCircle
  },
  inactive: { 
    label: 'Inaktív', 
    className: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: AlertCircle
  },
  maintenance: { 
    label: 'Karbantartás', 
    className: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: AlertCircle
  },
  construction: { 
    label: 'Építés alatt', 
    className: 'bg-orange-100 text-orange-800 border-orange-200',
    icon: AlertCircle
  }
}

function BuildingsPageContent() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  
  const router = useRouter()
  const searchParams = useSearchParams()
  const siteFilter = searchParams.get('site')

  // Mock query for buildings data
  const { data: buildings = mockBuildings, isLoading } = useQuery({
    queryKey: ['buildings', searchTerm, siteFilter],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      let filteredBuildings = mockBuildings

      // Filter by site if specified
      if (siteFilter) {
        filteredBuildings = filteredBuildings.filter(building => building.siteId === siteFilter)
      }

      // Filter by search term
      if (searchTerm) {
        filteredBuildings = filteredBuildings.filter(building => 
          building.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          building.siteName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          building.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          building.contactPerson.toLowerCase().includes(searchTerm.toLowerCase())
        )
      }
      
      return filteredBuildings
    }
  })

  const handleEditBuilding = (building: Building) => {
    setSelectedBuilding(building)
    setIsEditDialogOpen(true)
  }

  const handleDeleteBuilding = (building: Building) => {
    if (confirm(`Biztosan törölni szeretné a következő épületet: ${building.name}?`)) {
      toast({
        title: "Épület törölve",
        description: "Az épület sikeresen törölve lett."
      })
    }
  }

  const handleViewGates = (building: Building) => {
    router.push(`/gates?building=${building.id}`)
  }

  const isInspectionOverdue = (nextInspection: string) => {
    return new Date(nextInspection) < new Date()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('hu-HU')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            {siteFilter && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => router.push('/sites')}
                className="p-0 h-auto"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Vissza a telephelyekhez
              </Button>
            )}
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Épületek
            {siteFilter && buildings.length > 0 && (
              <span className="text-xl font-normal text-muted-foreground ml-2">
                - {buildings[0].siteName}
              </span>
            )}
          </h1>
          <p className="text-muted-foreground">
            Épületek kezelése és információik megtekintése
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Upload className="mr-2 h-4 w-4" />
            Import
          </Button>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Új épület
          </Button>
        </div>
      </div>

      {/* Filters & Search */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Keresés név, telephely vagy kapcsolattartó alapján..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" size="sm">
              <Filter className="mr-2 h-4 w-4" />
              Szűrők
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Összes épület</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{buildings.length}</div>
            <p className="text-xs text-muted-foreground">
              {buildings.filter(b => b.status === 'active').length} aktív
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Egységek</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {buildings.reduce((sum, building) => sum + building.units, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Összesen
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Kapuk</CardTitle>
            <DoorOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {buildings.reduce((sum, building) => sum + building.gatesCount, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              Összesen
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lejárt ellenőrzések</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {buildings.filter(b => isInspectionOverdue(b.nextInspection)).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Épület
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Buildings Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {isLoading ? (
          Array.from({ length: 6 }, (_, i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="h-3 bg-gray-200 rounded"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </CardContent>
            </Card>
          ))
        ) : buildings.length > 0 ? (
          buildings.map((building) => {
            const StatusIcon = statusConfig[building.status].icon
            const isOverdue = isInspectionOverdue(building.nextInspection)
            
            return (
              <Card key={building.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{building.name}</CardTitle>
                      <CardDescription className="text-sm">
                        {building.siteName}
                      </CardDescription>
                      <CardDescription className="text-xs text-muted-foreground">
                        {building.clientName}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={cn(
                        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
                        buildingTypeConfig[building.buildingType].className
                      )}>
                        {buildingTypeConfig[building.buildingType].label}
                      </div>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className={cn(
                        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
                        statusConfig[building.status].className
                      )}>
                        <StatusIcon className="mr-1 h-3 w-3" />
                        {statusConfig[building.status].label}
                      </div>
                      
                      {isOverdue && (
                        <div className="inline-flex items-center rounded-full bg-red-100 border-red-200 text-red-800 px-2.5 py-0.5 text-xs font-semibold">
                          <Calendar className="mr-1 h-3 w-3" />
                          Lejárt ellenőrzés
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-3 gap-3 py-3 border-t border-b">
                      <div className="text-center">
                        <div className="text-lg font-bold text-primary">{building.floors}</div>
                        <div className="text-xs text-muted-foreground">Szint</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-primary">{building.units}</div>
                        <div className="text-xs text-muted-foreground">Egység</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-bold text-primary">{building.gatesCount}</div>
                        <div className="text-xs text-muted-foreground">Kapu</div>
                      </div>
                    </div>

                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium">Kapcsolattartó:</span> {building.contactPerson}
                      </div>
                      {building.lastInspection && (
                        <div>
                          <span className="font-medium">Utolsó ellenőrzés:</span> {formatDate(building.lastInspection)}
                        </div>
                      )}
                      <div className={isOverdue ? "text-red-600 font-medium" : ""}>
                        <span className="font-medium">Következő ellenőrzés:</span> {formatDate(building.nextInspection)}
                      </div>
                    </div>

                    <div className="flex gap-2 pt-3">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="flex-1"
                        onClick={() => handleViewGates(building)}
                      >
                        <DoorOpen className="mr-2 h-4 w-4" />
                        Kapuk
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEditBuilding(building)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteBuilding(building)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })
        ) : (
          <div className="col-span-full text-center py-12">
            <Building2 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nincsenek épületek</h3>
            <p className="mt-1 text-sm text-gray-500">
              {siteFilter 
                ? "Ezen a telephelyen még nincsenek épületek."
                : "Kezdje el az első épület hozzáadásával."
              }
            </p>
            <div className="mt-6">
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Új épület
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default withAuth(BuildingsPageContent, {
  requireAuth: true,
  requiredPermission: { resource: PermissionResource.BUILDINGS, action: PermissionAction.READ }
})