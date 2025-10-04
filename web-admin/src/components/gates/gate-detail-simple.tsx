'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { 
  Edit,
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
  ChevronRight
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

import { useApiErrorToast } from '@/lib/toast'
import { apiClient } from '@/lib/api/client'
import { Gate, GateStatus, GateType } from '@/lib/api/types'
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
                  <p className="text-sm">{gateData.manufacturer || 'Nincs megadva'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Modell</label>
                  <p className="text-sm">{gateData.model || 'Nincs megadva'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Sorozatszám</label>
                  <p className="text-sm font-mono">{gateData.serialNumber || 'Nincs megadva'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Állapot</label>
                  <div className="flex items-center mt-1">
                    <Badge variant={statusConfig[gateData.status].variant}>
                      <StatusIcon className="h-3 w-3 mr-1" />
                      {statusConfig[gateData.status].label}
                    </Badge>
                  </div>
                </div>
              </div>

              {(gateData.width || gateData.height || gateData.weight) && (
                <>
                  <Separator />
                  <div>
                    <h4 className="font-medium mb-2">Fizikai méretek</h4>
                    <div className="grid grid-cols-3 gap-4">
                      {gateData.width && (
                        <div>
                          <label className="text-sm font-medium text-muted-foreground">Szélesség</label>
                          <p className="text-sm">{gateData.width} m</p>
                        </div>
                      )}
                      {gateData.height && (
                        <div>
                          <label className="text-sm font-medium text-muted-foreground">Magasság</label>
                          <p className="text-sm">{gateData.height} m</p>
                        </div>
                      )}
                      {gateData.weight && (
                        <div>
                          <label className="text-sm font-medium text-muted-foreground">Súly</label>
                          <p className="text-sm">{gateData.weight} kg</p>
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}
            </CardContent>
          </Card>

          {/* Motor és vezérlő */}
          {(gateData.motor || gateData.controller) && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {gateData.motor && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-lg">
                      <Zap className="mr-2 h-5 w-5" />
                      Motor
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {gateData.motor.type && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Típus</label>
                        <p className="text-sm capitalize">{gateData.motor.type}</p>
                      </div>
                    )}
                    {gateData.motor.power && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Teljesítmény</label>
                        <p className="text-sm">{gateData.motor.power} kW</p>
                      </div>
                    )}
                    {gateData.motor.manufacturer && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                        <p className="text-sm">{gateData.motor.manufacturer}</p>
                      </div>
                    )}
                    {gateData.motor.model && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Modell</label>
                        <p className="text-sm">{gateData.motor.model}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}

              {gateData.controller && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center text-lg">
                      <Settings className="mr-2 h-5 w-5" />
                      Vezérlő
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {gateData.controller.manufacturer && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Gyártó</label>
                        <p className="text-sm">{gateData.controller.manufacturer}</p>
                      </div>
                    )}
                    {gateData.controller.model && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Modell</label>
                        <p className="text-sm">{gateData.controller.model}</p>
                      </div>
                    )}
                    {gateData.controller.serialNumber && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">Sorozatszám</label>
                        <p className="text-sm font-mono">{gateData.controller.serialNumber}</p>
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
                    <Badge variant={gateData.photocell?.hasPhotocell ? 'default' : 'secondary'}>
                      {gateData.photocell?.hasPhotocell ? 'Telepítve' : 'Nincs telepítve'}
                    </Badge>
                  </div>
                  {gateData.photocell?.hasPhotocell && (
                    <div className="mt-2 text-sm text-muted-foreground space-y-1">
                      {gateData.photocell.manufacturer && <p>Gyártó: {gateData.photocell.manufacturer}</p>}
                      {gateData.photocell.model && <p>Modell: {gateData.photocell.model}</p>}
                      {gateData.photocell.beamCount && <p>Fotosugarak: {gateData.photocell.beamCount} db</p>}
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
                    <Badge variant={gateData.edgeProtection?.hasEdgeProtection ? 'default' : 'secondary'}>
                      {gateData.edgeProtection?.hasEdgeProtection ? 'Telepítve' : 'Nincs telepítve'}
                    </Badge>
                  </div>
                  {gateData.edgeProtection?.hasEdgeProtection && (
                    <div className="mt-2 text-sm text-muted-foreground space-y-1">
                      {gateData.edgeProtection.type && (
                        <p>Típus: {
                          gateData.edgeProtection.type === 'pneumatic' ? 'Pneumatikus' :
                          gateData.edgeProtection.type === 'optical' ? 'Optikai' : 'Mechanikus'
                        }</p>
                      )}
                      {gateData.edgeProtection.manufacturer && <p>Gyártó: {gateData.edgeProtection.manufacturer}</p>}
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
                    <Badge variant={gateData.manualRelease?.hasManualRelease ? 'default' : 'secondary'}>
                      {gateData.manualRelease?.hasManualRelease ? 'Telepítve' : 'Nincs telepítve'}
                    </Badge>
                  </div>
                  {gateData.manualRelease?.hasManualRelease && (
                    <div className="mt-2 text-sm text-muted-foreground space-y-1">
                      {gateData.manualRelease.type && (
                        <p>Típus: {
                          gateData.manualRelease.type === 'key' ? 'Kulcs' :
                          gateData.manualRelease.type === 'lever' ? 'Kar' : 'Zsinór'
                        }</p>
                      )}
                      {gateData.manualRelease.location && <p>Helye: {gateData.manualRelease.location}</p>}
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
              {gateData.installationDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Telepítés</label>
                  <p className="text-sm">{formatDateTime(gateData.installationDate)}</p>
                </div>
              )}
              
              {gateData.lastMaintenanceDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Utolsó karbantartás</label>
                  <p className="text-sm">{formatDateTime(gateData.lastMaintenanceDate)}</p>
                </div>
              )}
              
              {gateData.nextMaintenanceDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Következő karbantartás</label>
                  <p className="text-sm">{formatDateTime(gateData.nextMaintenanceDate)}</p>
                </div>
              )}
              
              {gateData.warrantyExpiryDate && (
                <div>
                  <label className="text-sm font-medium text-muted-foreground">Garancia lejárat</label>
                  <p className="text-sm">{formatDateTime(gateData.warrantyExpiryDate)}</p>
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

          {gateData.notes && (
            <Card>
              <CardHeader>
                <CardTitle>Megjegyzések</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm whitespace-pre-wrap">{gateData.notes}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}