'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { ColumnDef } from '@tanstack/react-table'
import { 
  Plus, 
  Edit, 
  Trash2, 
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
// import { withAuth } from '@/lib/auth/with-auth'
// import { PermissionResource, PermissionAction } from '@/lib/auth/types'
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

function GatesListPage() {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { showError } = useApiErrorToast()

  const [selectedSite, setSelectedSite] = useState<string>('')

  // Fetch gates
  const {
    data: gatesResponse,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['gates', { siteId: selectedSite }],
    queryFn: () => apiClient.getGates({ siteId: selectedSite }),
  })

  const gates = gatesResponse?.data?.items || []

  // Fetch sites for filter
  const { data: sitesResponse } = useQuery({
    queryKey: ['sites'],
    queryFn: () => apiClient.getSites({ limit: 100 }),
  })

  const sites = sitesResponse?.data?.items || []

  // Delete gate mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => apiClient.deleteGate(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gates'] })
    },
    onError: (error) => {
      showError(error, 'Kapu törlése sikertelen')
    },
  })

  // Columns definition
  const columns: ColumnDef<Gate>[] = [
    {
      accessorKey: 'name',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Név" />
      ),
      meta: { displayName: 'Név' },
      cell: ({ row }) => {
        const gate = row.original
        const typeConfig = gateTypeConfig[gate.type]
        const TypeIcon = typeConfig.icon
        
        return (
          <div className="flex items-center space-x-2">
            <TypeIcon className="h-4 w-4 text-gray-500" />
            <div>
              <p className="font-medium">{gate.name}</p>
              <p className="text-sm text-gray-500">{typeConfig.label}</p>
            </div>
          </div>
        )
      },
    },
    {
      accessorKey: 'status',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Állapot" />
      ),
      meta: { displayName: 'Állapot' },
      cell: ({ row }) => {
        const status = row.getValue('status') as GateStatus
        const config = gateStatusConfig[status]
        const StatusIcon = config.icon
        
        return (
          <Badge variant={config.variant} className="flex items-center space-x-1 w-fit">
            <StatusIcon className="h-3 w-3" />
            <span>{config.label}</span>
          </Badge>
        )
      },
    },
    {
      accessorKey: 'manufacturer',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Gyártó" />
      ),
      meta: { displayName: 'Gyártó' },
      cell: ({ row }) => {
        const gate = row.original
        return (
          <div>
            <p className="font-medium">{gate.manufacturer || 'Nincs megadva'}</p>
            <p className="text-sm text-gray-500">{gate.model || ''}</p>
          </div>
        )
      },
    },
    {
      accessorKey: 'serialNumber',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Sorozatszám" />
      ),
      meta: { displayName: 'Sorozatszám' },
      cell: ({ row }) => {
        const serialNumber = row.getValue('serialNumber') as string
        return (
          <span className="font-mono text-sm">
            {serialNumber || 'Nincs megadva'}
          </span>
        )
      },
    },
    {
      accessorKey: 'motor.type',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Motor" />
      ),
      meta: { displayName: 'Motor' },
      cell: ({ row }) => {
        const gate = row.original
        const motorType = gate.motor?.type
        const motorPower = gate.motor?.power
        
        if (!motorType) return <span className="text-gray-500">Nincs megadva</span>
        
        const motorTypeLabels = {
          hydraulic: 'Hidraulikus',
          electric: 'Elektromos', 
          pneumatic: 'Pneumatikus'
        }
        
        return (
          <div className="flex items-center space-x-1">
            <Zap className="h-3 w-3 text-blue-500" />
            <span>{motorTypeLabels[motorType]}</span>
            {motorPower && (
              <span className="text-sm text-gray-500">({motorPower} kW)</span>
            )}
          </div>
        )
      },
    },
    {
      accessorKey: 'lastMaintenanceDate',
      header: ({ column }) => (
        <DataTableColumnHeader column={column} title="Utolsó karbantartás" />
      ),
      meta: { displayName: 'Utolsó karbantartás' },
      cell: ({ row }) => {
        const date = row.getValue('lastMaintenanceDate') as string
        if (!date) return <span className="text-gray-500">Nincs adat</span>
        
        return (
          <div className="flex items-center space-x-1">
            <Clock className="h-3 w-3 text-gray-500" />
            <span className="text-sm">
              {format(new Date(date), 'yyyy. MMM dd.', { locale: hu })}
            </span>
          </div>
        )
      },
    },
    {
      accessorKey: 'photocell.hasPhotocell',
      header: 'Fotocella',
      meta: { displayName: 'Fotocella' },
      cell: ({ row }) => {
        const hasPhotocell = row.original.photocell?.hasPhotocell
        return hasPhotocell ? (
          <CheckCircle className="h-4 w-4 text-green-500" />
        ) : (
          <XCircle className="h-4 w-4 text-gray-400" />
        )
      },
    },
    {
      accessorKey: 'edgeProtection.hasEdgeProtection',
      header: 'Élvédelem',
      meta: { displayName: 'Élvédelem' },
      cell: ({ row }) => {
        const hasEdgeProtection = row.original.edgeProtection?.hasEdgeProtection
        return hasEdgeProtection ? (
          <CheckCircle className="h-4 w-4 text-green-500" />
        ) : (
          <XCircle className="h-4 w-4 text-gray-400" />
        )
      },
    },
    {
      id: 'actions',
      header: 'Műveletek',
      meta: { displayName: 'Műveletek' },
      cell: ({ row }) => {
        const gate = row.original

        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Műveletek megnyitása</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Műveletek</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => router.push(`/gates/${gate.id}`)}
              >
                <Eye className="mr-2 h-4 w-4" />
                Megtekintés
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => router.push(`/gates/${gate.id}/edit`)}
              >
                <Edit className="mr-2 h-4 w-4" />
                Szerkesztés
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => router.push(`/gates/${gate.id}/inspections`)}
              >
                <Settings className="mr-2 h-4 w-4" />
                Ellenőrzések
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => {
                  if (confirm('Biztosan törli ezt a kaput?')) {
                    deleteMutation.mutate(gate.id)
                  }
                }}
                className="text-red-600"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Törlés
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Kapuk</h1>
          <p className="text-muted-foreground">
            Kapuk kezelése és karbantartásának nyomon követése
          </p>
        </div>
        <Button onClick={() => router.push('/gates/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Új kapu
        </Button>
      </div>

      {/* Site Filter */}
      {sites.length > 0 && (
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium">Telephely szűrő:</label>
          <select
            value={selectedSite}
            onChange={(e) => setSelectedSite(e.target.value)}
            className="border rounded px-3 py-1 text-sm"
          >
            <option value="">Összes telephely</option>
            {sites.map((site: any) => (
              <option key={site.id} value={site.id}>
                {site.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Data Table */}
      <DataTable
        columns={columns}
        data={gates}
        searchKey="name"
        searchPlaceholder="Keresés kapuk között..."
        isLoading={isLoading}
        error={error}
        onRowClick={(gate) => router.push(`/gates/${gate.id}`)}
        toolbar={
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              Export
            </Button>
          </div>
        }
      />
    </div>
  )
}

export default GatesListPage