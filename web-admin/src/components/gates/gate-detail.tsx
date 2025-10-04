'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Edit,
  Trash2,
  ArrowLeft,
  MapPin,
  Settings,
  Zap,
  Eye,
  Shield,
  Key,
  Calendar,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle,
  ChevronRight,
  MoreHorizontal
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'

import { useApiErrorToast } from '@/lib/toast'
import { apiClient } from '@/lib/api/client'
import { Gate, GateStatus, GateType } from '@/lib/api/types'
import { withAuth } from '@/lib/auth/with-auth'
import { formatDateTime } from '@/lib/utils'

interface GateDetailProps {
  gateId: string
}

const statusConfig: Record<GateStatus, { label: string; variant: 'default' | 'secondary' | 'destructive' | 'outline'; icon: any }> = {
  active: { label: 'Aktív', variant: 'default', icon: CheckCircle },
  inactive: { label: 'Inaktív', variant: 'secondary', icon: XCircle },
  maintenance: { label: 'Karbantartás alatt', variant: 'outline', icon: Clock },
  error: { label: 'Hibás', variant: 'destructive', icon: AlertTriangle },
}

const typeConfig: Record<GateType, { label: string; icon: any }> = {
  entrance: { label: 'Bejárat', icon: ArrowLeft },
  exit: { label: 'Kijárat', icon: ChevronRight },
  service: { label: 'Szerviz', icon: Settings },
  emergency: { label: 'Vészkijárat', icon: AlertTriangle },
}

export function GateDetail({ gateId }: GateDetailProps) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const { showError } = useApiErrorToast()
  
  // Fetch gate details
  const { data: gate, isLoading, error } = useQuery({
    queryKey: ['gate', gateId],
    queryFn: () => apiClient.getGate(gateId),
  })

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: () => apiClient.deleteGate(gateId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gates'] })
      router.push('/gates')
    },
    onError: showError,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground mt-2">Adatok betöltése...</p>
        </div>
      </div>
    )
  }

  if (error || !gate) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-center">
          <XCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <h3 className="text-lg font-semibold">Hiba történt</h3>
          <p className="text-muted-foreground">A kapu adatai nem tölthetők be.</p>
          <Button variant="outline" className="mt-4" onClick={() => router.back()}>
            Vissza
          </Button>
        </div>
      </div>
    )
  }

  const gateData = gate as Gate
  const StatusIcon = statusConfig[gateData.status].icon
  const TypeIcon = typeConfig[gateData.type].icon

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Button variant="ghost" size="sm" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-1" />
              Vissza
            </Button>
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
            <h1 className="text-2xl font-bold tracking-tight">{gateData.name}</h1>
          </div>
          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
            <div className="flex items-center">
              <MapPin className="h-4 w-4 mr-1" />
              {gateData.siteId}
            </div>
            <div className="flex items-center">
              <TypeIcon className="h-4 w-4 mr-1" />
              {typeConfig[gateData.type].label}
            </div>
            <Badge variant={statusConfig[gateData.status].variant}>
              <StatusIcon className="h-3 w-3 mr-1" />
              {statusConfig[gateData.status].label}
            </Badge>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button variant="outline" asChild>
            <Link href={`/gates/${gateId}/edit`}>
              <Edit className="h-4 w-4 mr-2" />
              Szerkesztés
            </Link>
          </Button>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem asChild>
                <Link href={`/gates/${gateId}/maintenance`}>
                  <Settings className="h-4 w-4 mr-2" />
                  Karbantartás
                </Link>
              </DropdownMenuItem>
              <DropdownMenuItem asChild>
                <Link href={`/gates/${gateId}/inspections`}>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Felülvizsgálatok
                </Link>
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <DropdownMenuItem 
                    className="text-destructive focus:text-destructive"
                    onSelect={(e) => e.preventDefault()}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Törlés
                  </DropdownMenuItem>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Kapu törlése</AlertDialogTitle>
                    <AlertDialogDescription>
                      Biztosan törölni szeretné a(z) "{gateData.name}" kapuját? 
                      Ez a művelet nem vonható vissza és törli az összes kapcsolódó adatot.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Mégse</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={() => deleteMutation.mutate()}
                      disabled={deleteMutation.isPending}
                      className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                    >
                      {deleteMutation.isPending ? 'Törlés...' : 'Törlés'}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Alapadatok */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="mr-2 h-5 w-5" />
                Alapadatok
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                  <p className="text-sm">{gate.manufacturer || 'Nincs megadva'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Modell</label>
                  <p className="text-sm">{gate.model || 'Nincs megadva'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Sorozatszám</label>
                  <p className="text-sm font-mono">{gate.serialNumber || 'Nincs megadva'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Állapot</label>
                  <div className="flex items-center mt-1">
                    <Badge variant={statusConfig[gate.status].variant}>
                      <StatusIcon className="h-3 w-3 mr-1" />
                      {statusConfig[gate.status].label}
                    </Badge>
                  </div>
                </div>
              </div>

              {(gate.width || gate.height || gate.weight) && (
                <>
                  <Separator />
                  <div>
                    <h4 className="font-medium mb-2">Fizikai méretek</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {gate.width && (
                        <div>
                          <label className="text-sm font-medium text-muted-foreground">Szélesség</label>
                          <p className="text-sm">{gate.width} m</p>
                        </div>
                      )}
                      {gate.height && (
                        <div>
                          <label className="text-sm font-medium text-muted-foreground">Magasság</label>
                          <p className="text-sm">{gate.height} m</p>
                        </div>
                      )}
                      {gate.weight && (
                        <div>
                          <label className="text-sm font-medium text-muted-foreground">Súly</label>
                          <p className="text-sm">{gate.weight} kg</p>
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Motor és vezérlő */}
          {(gate.motor || gate.controller) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {gate.motor && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-lg">
                      <Zap className="mr-2 h-5 w-5" />
                      Motor
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {gate.motor.type && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Típus</label>
                        <p className="text-sm capitalize">{gate.motor.type}</p>
                      </div>
                    )}
                    {gate.motor.power && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Teljesítmény</label>
                        <p className="text-sm">{gate.motor.power} kW</p>
                      </div>
                    )}
                    {gate.motor.manufacturer && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                        <p className="text-sm">{gate.motor.manufacturer}</p>
                      </div>
                    )}
                    {gate.motor.model && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Modell</label>
                        <p className="text-sm">{gate.motor.model}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {gate.controller && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-lg">
                      <Settings className="mr-2 h-5 w-5" />
                      Vezérlő
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {gate.controller.manufacturer && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                        <p className="text-sm">{gate.controller.manufacturer}</p>
                      </div>
                    )}
                    {gate.controller.model && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Modell</label>
                        <p className="text-sm">{gate.controller.model}</p>
                      </div>
                    )}
                    {gate.controller.serialNumber && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Sorozatszám</label>
                        <p className="text-sm font-mono">{gate.controller.serialNumber}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Rugók és sínek */}
          {(gate.springs || gate.tracks) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {gate.springs && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Rugók</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {gate.springs.type && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Típus</label>
                        <p className="text-sm capitalize">{gate.springs.type === 'torsion' ? 'Torziós' : 'Húzórugó'}</p>
                      </div>
                    )}
                    {gate.springs.count && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Darabszám</label>
                        <p className="text-sm">{gate.springs.count} db</p>
                      </div>
                    )}
                    {gate.springs.manufacturer && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                        <p className="text-sm">{gate.springs.manufacturer}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {gate.tracks && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Sínek</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {gate.tracks.material && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Anyag</label>
                        <p className="text-sm capitalize">{gate.tracks.material === 'steel' ? 'Acél' : 'Alumínium'}</p>
                      </div>
                    )}
                    {gate.tracks.length && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Hossz</label>
                        <p className="text-sm">{gate.tracks.length} m</p>
                      </div>
                    )}
                    {gate.tracks.manufacturer && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                        <p className="text-sm">{gate.tracks.manufacturer}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          )}

          {/* Biztonságtechnika */}
          <Card>
            <CardHeader>
              <CardTitle>Biztonságtechnikai elemek</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Fotocella */}
              <div className="flex items-start space-x-3">
                <Eye className="h-5 w-5 mt-0.5 text-muted-foreground" />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">Fotocella</h4>
                    <Badge variant={gate.photocell?.hasPhotocell ? 'default' : 'secondary'}>
                      {gate.photocell?.hasPhotocell ? 'Telepítve' : 'Nincs telepítve'}
                    </Badge>
                  </div>
                  {gate.photocell?.hasPhotocell && (
                    <div className="mt-2 text-sm text-muted-foreground space-y-1">
                      {gate.photocell.manufacturer && <p>Gyártó: {gate.photocell.manufacturer}</p>}
                      {gate.photocell.model && <p>Modell: {gate.photocell.model}</p>}
                      {gate.photocell.beamCount && <p>Fotosugarak: {gate.photocell.beamCount} db</p>}
                    </div>
                  )}
                </div>
              </div>

              <Separator />

              {/* Élvédelem */}
              <div className="flex items-start space-x-3">
                <Shield className="h-5 w-5 mt-0.5 text-muted-foreground" />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">Élvédelem</h4>
                    <Badge variant={gate.edgeProtection?.hasEdgeProtection ? 'default' : 'secondary'}>
                      {gate.edgeProtection?.hasEdgeProtection ? 'Telepítve' : 'Nincs telepítve'}
                    </Badge>
                  </div>
                  {gate.edgeProtection?.hasEdgeProtection && (
                    <div className="mt-2 text-sm text-muted-foreground space-y-1">
                      {gate.edgeProtection.type && (
                        <p>Típus: {
                          gate.edgeProtection.type === 'pneumatic' ? 'Pneumatikus' :
                          gate.edgeProtection.type === 'optical' ? 'Optikai' : 'Mechanikus'
                        }</p>
                      )}
                      {gate.edgeProtection.manufacturer && <p>Gyártó: {gate.edgeProtection.manufacturer}</p>}
                    </div>
                  )}
                </div>
              </div>

              <Separator />

              {/* Kézi kioldó */}
              <div className="flex items-start space-x-3">
                <Key className="h-5 w-5 mt-0.5 text-muted-foreground" />
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">Kézi kioldó</h4>
                    <Badge variant={gate.manualRelease?.hasManualRelease ? 'default' : 'secondary'}>
                      {gate.manualRelease?.hasManualRelease ? 'Telepítve' : 'Nincs telepítve'}
                    </Badge>
                  </div>
                  {gate.manualRelease?.hasManualRelease && (
                    <div className="mt-2 text-sm text-muted-foreground space-y-1">
                      {gate.manualRelease.type && (
                        <p>Típus: {
                          gate.manualRelease.type === 'key' ? 'Kulcs' :
                          gate.manualRelease.type === 'lever' ? 'Kar' : 'Zsinór'
                        }</p>
                      )}
                      {gate.manualRelease.location && <p>Helye: {gate.manualRelease.location}</p>}
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Oldalsáv - Karbantartási adatok */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="mr-2 h-5 w-5" />
                Karbantartás
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {gate.installationDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Telepítés</label>
                  <p className="text-sm">{formatDateTime(gate.installationDate)}</p>
                </div>
              )}
              
              {gate.lastMaintenanceDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Utolsó karbantartás</label>
                  <p className="text-sm">{formatDateTime(gate.lastMaintenanceDate)}</p>
                </div>
              )}
              
              {gate.nextMaintenanceDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Következő karbantartás</label>
                  <p className="text-sm">{formatDateTime(gate.nextMaintenanceDate)}</p>
                </div>
              )}
              
              {gate.warrantyExpiryDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Garancia lejárat</label>
                  <p className="text-sm">{formatDateTime(gate.warrantyExpiryDate)}</p>
                </div>
              )}

              <div className="pt-2">
                <Button variant="outline" className="w-full" asChild>
                  <Link href={`/gates/${gateId}/maintenance`}>
                    <Settings className="h-4 w-4 mr-2" />
                    Karbantartás ütemezése
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>

          {gate.notes && (
            <Card>
              <CardHeader>
                <CardTitle>Megjegyzések</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-wrap">{gate.notes}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

export default withAuth(GateDetail, {
  permissions: [
    { resource: PermissionResource.GATES, action: Permission.READ }
  ]
})