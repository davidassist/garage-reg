import GatesListPage from './gates-list'import GatesListPage from './gates-list'import GatesListPage from './gates-list'import GatesListPage from './gates-list'



export default GatesListPage

export default GatesListPage

export default GatesListPageexport default GatesListPage 
  Eye,
  MoreHorizontal,
  Building2,
  Settings,
  Zap,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Wrench
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { DataTable, DataTableColumnHeader } from '@/components/ui/data-table'
import { useApiErrorToast } from '@/lib/toast'
import { apiClient } from '@/lib/api/client'
import { Gate, GateStatus, GateType } from '@/lib/api/types'
import { withAuth } from '@/lib/auth/with-auth'
import { PermissionResource, PermissionAction } from '@/lib/auth/types'
import { format } from 'date-fns'
import { hu } from 'date-fns/locale'

// Gate status display configuration
const gateStatusConfig: Record<GateStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; icon: any }> = {
  active: { 
    label: 'Aktív', 
    variant: 'default', 
    icon: CheckCircle 
  },
  inactive: { 
    label: 'Inaktív', 
    variant: 'secondary', 
    icon: XCircle 
  },
  maintenance: { 
    label: 'Karbantartás alatt', 
    variant: 'outline', 
    icon: Wrench 
  },
  error: { 
    label: 'Hibás', 
    variant: 'destructive', 
    icon: AlertTriangle 
  },
}

// Gate type display configuration  
const gateTypeConfig: Record<GateType, { label: string; icon: any }> = {
  entrance: { label: 'Bejárat', icon: Building2 },
  exit: { label: 'Kijárat', icon: Building2 },
  service: { label: 'Szerviz', icon: Settings },
  emergency: { label: 'Vészkijárat', icon: AlertTriangle },
}
  manufacturer: string
  model: string
  serialNumber: string
  installationDate: string
  status: 'active' | 'inactive' | 'maintenance' | 'error'
  connectivity: 'online' | 'offline'
  lastMaintenance: string | null
  nextMaintenance: string
  batteryLevel?: number
  signalStrength?: number
  firmware: string
  contactPerson: string
  contactPhone: string
  createdAt: string
  updatedAt: string
}

const mockGates: Gate[] = [
  {
    id: '1',
    name: 'Főbejárat',
    buildingId: '1',
    buildingName: 'A épület',
    siteName: 'Buda Castle Business Center',
    clientName: 'Budapesti Városkapu Kft.',
    gateType: 'entry',
    location: 'Földszint, főlépcsőház',
    manufacturer: 'SecureGate',
    model: 'SG-2000 Pro',
    serialNumber: 'SG2000-2024-001',
    installationDate: '2024-01-15T10:00:00Z',
    status: 'active',
    connectivity: 'online',
    lastMaintenance: '2024-08-15T10:00:00Z',
    nextMaintenance: '2024-11-15T10:00:00Z',
    batteryLevel: 85,
    signalStrength: 4,
    firmware: '2.4.1',
    contactPerson: 'Nagy Péter',
    contactPhone: '+36 1 234 5678',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-10-01T14:30:00Z'
  },
  {
    id: '2',
    name: 'Parkoló bejárat',
    buildingId: '1',
    buildingName: 'A épület',
    siteName: 'Buda Castle Business Center',
    clientName: 'Budapesti Városkapu Kft.',
    gateType: 'bidirectional',
    location: 'Mélygarázs, -1. szint',
    manufacturer: 'SecureGate',
    model: 'SG-1500',
    serialNumber: 'SG1500-2024-002',
    installationDate: '2024-01-20T14:00:00Z',
    status: 'active',
    connectivity: 'online',
    lastMaintenance: '2024-09-10T16:00:00Z',
    nextMaintenance: '2024-12-10T16:00:00Z',
    batteryLevel: 92,
    signalStrength: 3,
    firmware: '2.3.5',
    contactPerson: 'Nagy Péter',
    contactPhone: '+36 1 234 5678',
    createdAt: '2024-01-20T14:00:00Z',
    updatedAt: '2024-09-28T16:45:00Z'
  },
  {
    id: '3',
    name: 'Vészijárat',
    buildingId: '2',
    buildingName: 'B épület',
    siteName: 'Buda Castle Business Center',
    clientName: 'Budapesti Városkapu Kft.',
    gateType: 'emergency',
    location: '2. szint, hátsó lépcsőház',
    manufacturer: 'SafeExit',
    model: 'SE-1000',
    serialNumber: 'SE1000-2024-001',
    installationDate: '2024-02-01T09:00:00Z',
    status: 'maintenance',
    connectivity: 'offline',
    lastMaintenance: '2024-06-01T10:00:00Z',
    nextMaintenance: '2024-10-10T10:00:00Z', // Overdue
    batteryLevel: 45,
    signalStrength: 0,
    firmware: '1.8.2',
    contactPerson: 'Nagy Péter',
    contactPhone: '+36 1 234 5678',
    createdAt: '2024-02-01T09:00:00Z',
    updatedAt: '2024-08-15T13:20:00Z'
  }
]

const gateTypeConfig = {
  entry: { label: 'Belépő', className: 'bg-green-100 text-green-800 border-green-200', icon: DoorOpen },
  exit: { label: 'Kilépő', className: 'bg-red-100 text-red-800 border-red-200', icon: DoorOpen },
  bidirectional: { label: 'Kétirányú', className: 'bg-blue-100 text-blue-800 border-blue-200', icon: DoorOpen },
  emergency: { label: 'Vész', className: 'bg-orange-100 text-orange-800 border-orange-200', icon: Shield }
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
    icon: Settings
  },
  error: { 
    label: 'Hiba', 
    className: 'bg-red-100 text-red-800 border-red-200',
    icon: AlertCircle
  }
}

function GatesPageContent() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedGate, setSelectedGate] = useState<Gate | null>(null)
  const [selectedGates, setSelectedGates] = useState<string[]>([])
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  
  const router = useRouter()
  const searchParams = useSearchParams()
  const buildingFilter = searchParams.get('building')

  // Mock query for gates data
  const { data: gates = mockGates, isLoading } = useQuery({
    queryKey: ['gates', searchTerm, buildingFilter],
    queryFn: async () => {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      
      let filteredGates = mockGates

      // Filter by building if specified
      if (buildingFilter) {
        filteredGates = filteredGates.filter(gate => gate.buildingId === buildingFilter)
      }

      // Filter by search term
      if (searchTerm) {
        filteredGates = filteredGates.filter(gate => 
          gate.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
          gate.buildingName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          gate.siteName.toLowerCase().includes(searchTerm.toLowerCase()) ||
          gate.manufacturer.toLowerCase().includes(searchTerm.toLowerCase()) ||
          gate.model.toLowerCase().includes(searchTerm.toLowerCase()) ||
          gate.serialNumber.toLowerCase().includes(searchTerm.toLowerCase())
        )
      }
      
      return filteredGates
    }
  })

  const handleEditGate = (gate: Gate) => {
    setSelectedGate(gate)
    setIsEditDialogOpen(true)
  }

  const handleDeleteGate = (gate: Gate) => {
    if (confirm(`Biztosan törölni szeretné a következő kaput: ${gate.name}?`)) {
      toast({
        title: "Kapu törölve",
        description: "A kapu sikeresen törölve lett."
      })
    }
  }

  const handleOpenGate = (gate: Gate) => {
    if (gate.status === 'active' && gate.connectivity === 'online') {
      toast({
        title: "Kapu nyitása",
        description: `${gate.name} kapu nyitása folyamatban...`
      })
    } else {
      toast({
        title: "Hiba",
        description: "A kapu jelenleg nem működőképes.",
        variant: "destructive"
      })
    }
  }

  const isMaintenanceOverdue = (nextMaintenance: string) => {
    return new Date(nextMaintenance) < new Date()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('hu-HU')
  }

  const getBatteryColor = (level?: number) => {
    if (!level) return 'text-gray-400'
    if (level > 50) return 'text-green-500'
    if (level > 20) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getSignalBars = (strength?: number) => {
    if (!strength) return []
    return Array.from({ length: 4 }, (_, i) => i < strength)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            {buildingFilter && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => router.push('/buildings')}
                className="p-0 h-auto"
              >
                <ArrowLeft className="h-4 w-4 mr-1" />
                Vissza az épületekhez
              </Button>
            )}
          </div>
          <h1 className="text-3xl font-bold tracking-tight">
            Kapuk
            {buildingFilter && gates.length > 0 && (
              <span className="text-xl font-normal text-muted-foreground ml-2">
                - {gates[0].buildingName}
              </span>
            )}
          </h1>
          <p className="text-muted-foreground">
            Kapuk kezelése és információik megtekintése
          </p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {selectedGates.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">
                {selectedGates.length} kiválasztva
              </span>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setSelectedGates([])}
              >
                Törlés
              </Button>
            </div>
          )}
          
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => {
              if (selectedGates.length === gates.length) {
                setSelectedGates([])
              } else {
                setSelectedGates(gates.map(g => g.id))
              }
            }}
          >
            {selectedGates.length === gates.length ? 'Kijelölés törlése' : 'Összes kijelölése'}
          </Button>
          
          <LabelPreview gates={gates.filter(gate => selectedGates.includes(gate.id))} />
          <BulkLabelGenerator selectedGates={gates.filter(gate => selectedGates.includes(gate.id))} />
          <FactoryQRImport onImportComplete={(result: any) => {
            toast({ 
              title: 'Import befejezve',
              description: `${result.successCount} kapu frissítve, ${result.errorCount} hiba`
            })
          }} />
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
            Új kapu
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
                placeholder="Keresés név, épület, gyártó vagy sorozatszám alapján..."
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
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Összes kapu</CardTitle>
            <DoorOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{gates.length}</div>
            <p className="text-xs text-muted-foreground">
              {gates.filter(g => g.status === 'active').length} aktív
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Online</CardTitle>
            <Wifi className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {gates.filter(g => g.connectivity === 'online').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Kapcsolódva
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Offline</CardTitle>
            <WifiOff className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {gates.filter(g => g.connectivity === 'offline').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Kapcsolat nélkül
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Karbantartás</CardTitle>
            <Settings className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {gates.filter(g => g.status === 'maintenance').length}
            </div>
            <p className="text-xs text-muted-foreground">
              Kapu
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Lejárt karbantartás</CardTitle>
            <Calendar className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {gates.filter(g => isMaintenanceOverdue(g.nextMaintenance)).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Kapu
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Gates Grid */}
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
        ) : gates.length > 0 ? (
          gates.map((gate) => {
            const StatusIcon = statusConfig[gate.status].icon
            const TypeIcon = gateTypeConfig[gate.gateType].icon
            const isOverdue = isMaintenanceOverdue(gate.nextMaintenance)
            const ConnectivityIcon = gate.connectivity === 'online' ? Wifi : WifiOff
            const signalBars = getSignalBars(gate.signalStrength)
            
            return (
              <Card key={gate.id} className={cn(
                "hover:shadow-lg transition-shadow cursor-pointer",
                selectedGates.includes(gate.id) && "ring-2 ring-blue-500"
              )}>
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-1 flex-1">
                      <CardTitle className="text-lg flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={selectedGates.includes(gate.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedGates(prev => [...prev, gate.id])
                            } else {
                              setSelectedGates(prev => prev.filter(id => id !== gate.id))
                            }
                          }}
                          className="h-4 w-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500"
                        />
                        <TypeIcon className="h-5 w-5" />
                        {gate.name}
                      </CardTitle>
                      <CardDescription className="text-sm">
                        {gate.buildingName} - {gate.siteName}
                      </CardDescription>
                      <CardDescription className="text-xs text-muted-foreground">
                        {gate.location}
                      </CardDescription>
                    </div>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-3">
                    {/* Status and Type Badges */}
                    <div className="flex items-center gap-2 flex-wrap">
                      <div className={cn(
                        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
                        statusConfig[gate.status].className
                      )}>
                        <StatusIcon className="mr-1 h-3 w-3" />
                        {statusConfig[gate.status].label}
                      </div>
                      
                      <div className={cn(
                        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold",
                        gateTypeConfig[gate.gateType].className
                      )}>
                        {gateTypeConfig[gate.gateType].label}
                      </div>
                    </div>

                    {/* Connectivity and Technical Info */}
                    <div className="grid grid-cols-2 gap-3 py-3 border-t border-b">
                      <div className="flex items-center gap-2">
                        <ConnectivityIcon className={cn(
                          "h-4 w-4",
                          gate.connectivity === 'online' ? 'text-green-500' : 'text-red-500'
                        )} />
                        <span className="text-sm font-medium">
                          {gate.connectivity === 'online' ? 'Online' : 'Offline'}
                        </span>
                      </div>
                      
                      {gate.batteryLevel && (
                        <div className="flex items-center gap-2">
                          <Zap className={cn("h-4 w-4", getBatteryColor(gate.batteryLevel))} />
                          <span className="text-sm font-medium">{gate.batteryLevel}%</span>
                        </div>
                      )}
                    </div>

                    {/* Signal Strength */}
                    {gate.signalStrength !== undefined && (
                      <div className="flex items-center gap-2">
                        <span className="text-sm">Jelerősség:</span>
                        <div className="flex gap-1">
                          {signalBars.map((filled, i) => (
                            <div
                              key={i}
                              className={cn(
                                "w-1 h-3 rounded-sm",
                                filled ? "bg-green-500" : "bg-gray-200"
                              )}
                            />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Device Info */}
                    <div className="space-y-1 text-sm">
                      <div>
                        <span className="font-medium">Gyártó:</span> {gate.manufacturer} {gate.model}
                      </div>
                      <div>
                        <span className="font-medium">Sorozatszám:</span> {gate.serialNumber}
                      </div>
                      <div>
                        <span className="font-medium">Firmware:</span> {gate.firmware}
                      </div>
                    </div>

                    {/* Maintenance Info */}
                    <div className="space-y-1 text-sm">
                      {gate.lastMaintenance && (
                        <div>
                          <span className="font-medium">Utolsó karbantartás:</span> {formatDate(gate.lastMaintenance)}
                        </div>
                      )}
                      <div className={isOverdue ? "text-red-600 font-medium" : ""}>
                        <span className="font-medium">Következő karbantartás:</span> {formatDate(gate.nextMaintenance)}
                        {isOverdue && <span className="ml-2 text-xs">(Lejárt)</span>}
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex gap-2 pt-3">
                      <Button 
                        variant={gate.status === 'active' && gate.connectivity === 'online' ? 'default' : 'outline'}
                        size="sm" 
                        className="flex-1"
                        onClick={() => handleOpenGate(gate)}
                        disabled={gate.status !== 'active' || gate.connectivity !== 'online'}
                      >
                        <DoorOpen className="mr-2 h-4 w-4" />
                        Nyitás
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleEditGate(gate)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => handleDeleteGate(gate)}
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
            <DoorOpen className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nincsenek kapuk</h3>
            <p className="mt-1 text-sm text-gray-500">
              {buildingFilter 
                ? "Ebben az épületben még nincsenek kapuk."
                : "Kezdje el az első kapu hozzáadásával."
              }
            </p>
            <div className="mt-6">
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Új kapu
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default withAuth(GatesPageContent, {
  requireAuth: true,
  requiredPermission: { resource: PermissionResource.GATES, action: PermissionAction.READ }
})