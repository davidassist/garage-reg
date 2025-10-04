'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  AlertTriangle,
  FileText,
  Play,
  CheckCircle2,
  XCircle,
  Clock,
  Calendar,
  User,
  Building2,
  Car,
  Target,
  BarChart3,
  TrendingUp,
  History
} from 'lucide-react'
import { StartInspectionDialog } from './StartInspectionDialog'
import { LiveInspectionForm } from './LiveInspectionForm'
import { InspectionCompleteSummary } from './InspectionCompleteSummary'

interface InspectionHistory {
  id: string
  templateName: string
  objectType: 'gate' | 'building' | 'vehicle'
  objectId: string
  inspector: string
  completedAt: Date
  status: 'passed' | 'failed' | 'warning'
  duration: number // minutes
  totalItems: number
  failedItems: number
}

interface DashboardStats {
  totalInspections: number
  completedToday: number
  failedInspections: number
  averageDuration: number
  upcomingInspections: number
}

// Mock data for demonstration
const mockHistory: InspectionHistory[] = [
  {
    id: 'inspection-001',
    templateName: 'Napi biztonsági ellenőrzés',
    objectType: 'gate',
    objectId: 'gate-123',
    inspector: 'Kovács János',
    completedAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    status: 'warning',
    duration: 18,
    totalItems: 6,
    failedItems: 1
  },
  {
    id: 'inspection-002',
    templateName: 'Heti karbantartási ellenőrzés',
    objectType: 'building',
    objectId: 'building-456',
    inspector: 'Nagy Anna',
    completedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
    status: 'passed',
    duration: 45,
    totalItems: 12,
    failedItems: 0
  },
  {
    id: 'inspection-003',
    templateName: 'Jármű műszaki vizsgálat',
    objectType: 'vehicle',
    objectId: 'vehicle-789',
    inspector: 'Szabó Péter',
    completedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000), // 2 days ago
    status: 'failed',
    duration: 30,
    totalItems: 8,
    failedItems: 3
  },
  {
    id: 'inspection-004',
    templateName: 'Napi biztonsági ellenőrzés',
    objectType: 'gate',
    objectId: 'gate-124',
    inspector: 'Kovács János',
    completedAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
    status: 'passed',
    duration: 12,
    totalItems: 6,
    failedItems: 0
  }
]

const mockStats: DashboardStats = {
  totalInspections: 156,
  completedToday: 4,
  failedInspections: 12,
  averageDuration: 22,
  upcomingInspections: 8
}

export function InspectionSystemDemo() {
  const [currentView, setCurrentView] = useState<'dashboard' | 'inspection' | 'complete'>('dashboard')
  const [selectedInspection, setSelectedInspection] = useState<any>(null)
  const [history, setHistory] = useState<InspectionHistory[]>(mockHistory)
  const [stats, setStats] = useState<DashboardStats>(mockStats)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'passed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getObjectIcon = (objectType: string) => {
    switch (objectType) {
      case 'gate':
        return <Car className="w-4 h-4" />
      case 'building':
        return <Building2 className="w-4 h-4" />
      case 'vehicle':
        return <Car className="w-4 h-4" />
      default:
        return <Target className="w-4 h-4" />
    }
  }

  const handleStartInspection = (inspectionData: any) => {
    console.log('Starting inspection:', inspectionData)
    setSelectedInspection(inspectionData)
    setCurrentView('inspection')
  }

  const handleCompleteInspection = (completedData: any) => {
    console.log('Inspection completed:', completedData)
    
    // Add to history
    const newHistoryItem: InspectionHistory = {
      id: `inspection-${Date.now()}`,
      templateName: selectedInspection?.template?.name || 'Ellenőrzés',
      objectType: selectedInspection?.objectType || 'gate',
      objectId: selectedInspection?.objectId || 'unknown',
      inspector: selectedInspection?.inspector || 'Ismeretlen',
      completedAt: new Date(),
      status: completedData.overallStatus,
      duration: completedData.actualDuration,
      totalItems: completedData.totalItems,
      failedItems: completedData.failedItems
    }
    
    setHistory(prev => [newHistoryItem, ...prev])
    
    // Update stats
    setStats(prev => ({
      ...prev,
      totalInspections: prev.totalInspections + 1,
      completedToday: prev.completedToday + 1,
      failedInspections: prev.failedInspections + (completedData.overallStatus === 'failed' ? 1 : 0)
    }))
    
    setCurrentView('complete')
  }

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    
    if (hours > 0) {
      return `${hours}ó ${mins}p`
    }
    return `${mins}p`
  }

  if (currentView === 'inspection') {
    return (
      <LiveInspectionForm
        sessionId={selectedInspection?.id || 'session-001'}
        onComplete={handleCompleteInspection}
        onCancel={() => setCurrentView('dashboard')}
      />
    )
  }

  if (currentView === 'complete') {
    // Create a mock completed inspection for the summary
    const completedInspection = {
      id: 'inspection-001',
      templateName: selectedInspection?.templateName || 'Napi biztonsági ellenőrzés',
      objectType: selectedInspection?.objectType || 'gate' as const,
      objectId: selectedInspection?.objectId || 'gate-123',
      inspector: selectedInspection?.inspector || 'Kovács János',
      startedAt: new Date(Date.now() - 18 * 60 * 1000),
      completedAt: new Date(),
      actualDuration: 18,
      estimatedDuration: 15,
      totalItems: 6,
      completedItems: 4,
      failedItems: 1,
      skippedItems: 1,
      overallStatus: 'warning' as const,
      notes: 'A kapu szenzorai időnként hibásan reagálnak. Javítás szükséges 1 héten belül.',
      photos: [
        'https://images.unsplash.com/photo-1558618047-3c8c76ca7e26?w=400',
        'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400'
      ],
      location: {
        lat: 47.4979,
        lng: 19.0402,
        address: '1051 Budapest, Bajcsy-Zsilinszky út 12.'
      },
      checklist: []
    }

    return (
      <InspectionCompleteSummary
        inspection={completedInspection}
        onClose={() => setCurrentView('dashboard')}
        onNewInspection={() => setCurrentView('dashboard')}
        onViewDetails={() => console.log('View details')}
      />
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ellenőrzési Rendszer</h1>
          <p className="text-gray-600 mt-2">
            Átfogó ellenőrzési és auditálási rendszer garázs kapuk, épületek és járművek számára
          </p>
        </div>
        
        <StartInspectionDialog 
          onStart={handleStartInspection}
          trigger={
            <Button size="lg" className="gap-2">
              <Play className="w-5 h-5" />
              Új ellenőrzés indítása
            </Button>
          }
        />
      </div>

      {/* Statistics Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Összes ellenőrzés</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalInspections}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Ma befejezett</p>
                <p className="text-2xl font-bold text-green-700">{stats.completedToday}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="w-5 h-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Sikertelen</p>
                <p className="text-2xl font-bold text-red-700">{stats.failedInspections}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Clock className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Átlag időtartam</p>
                <p className="text-2xl font-bold text-purple-700">{formatDuration(stats.averageDuration)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Calendar className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Függőben</p>
                <p className="text-2xl font-bold text-orange-700">{stats.upcomingInspections}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Inspections */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <History className="w-5 h-5" />
                  Legutóbbi ellenőrzések
                </CardTitle>
                <Button variant="ghost" size="sm">
                  Összes megtekintése
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {history.slice(0, 6).map((inspection) => (
                  <div
                    key={inspection.id}
                    className="flex items-center gap-4 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-2">
                      {getObjectIcon(inspection.objectType)}
                      <div>
                        <p className="font-medium text-sm">{inspection.templateName}</p>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <User className="w-3 h-3" />
                          {inspection.inspector}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex-1 text-center">
                      <p className="text-sm font-medium">
                        {inspection.objectType === 'gate' && 'Kapu'} 
                        {inspection.objectType === 'building' && 'Épület'}
                        {inspection.objectType === 'vehicle' && 'Jármű'} 
                        #{inspection.objectId}
                      </p>
                    </div>
                    
                    <div className="text-center">
                      <Badge className={`text-xs ${getStatusColor(inspection.status)}`}>
                        {getStatusIcon(inspection.status)}
                        <span className="ml-1">
                          {inspection.status === 'passed' && 'Sikeres'}
                          {inspection.status === 'failed' && 'Sikertelen'}
                          {inspection.status === 'warning' && 'Figyelem'}
                        </span>
                      </Badge>
                      <p className="text-xs text-gray-500 mt-1">
                        {formatDuration(inspection.duration)}
                      </p>
                    </div>
                    
                    <div className="text-right text-xs text-gray-500">
                      <p>{inspection.completedAt.toLocaleDateString('hu-HU')}</p>
                      <p>{inspection.completedAt.toLocaleTimeString('hu-HU', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions & Summary */}
        <div className="space-y-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Gyors műveletek</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <StartInspectionDialog 
                onStart={handleStartInspection}
                trigger={
                  <Button className="w-full gap-2">
                    <Play className="w-4 h-4" />
                    Új ellenőrzés
                  </Button>
                }
              />
              
              <Button variant="outline" className="w-full gap-2">
                <FileText className="w-4 h-4" />
                Sablon kezelés
              </Button>
              
              <Button variant="outline" className="w-full gap-2">
                <BarChart3 className="w-4 h-4" />
                Jelentések
              </Button>
              
              <Button variant="outline" className="w-full gap-2">
                <Calendar className="w-4 h-4" />
                Ütemezett ellenőrzések
              </Button>
            </CardContent>
          </Card>

          {/* Performance Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                Teljesítmény összesítő
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Sikeres ellenőrzések</span>
                  <span className="text-sm font-medium">
                    {Math.round(((stats.totalInspections - stats.failedInspections) / stats.totalInspections) * 100)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-600 h-2 rounded-full"
                    style={{
                      width: `${((stats.totalInspections - stats.failedInspections) / stats.totalInspections) * 100}%`
                    }}
                  />
                </div>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Mai teljesítmény</span>
                  <span className="text-sm font-medium">
                    {stats.completedToday}/8
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full"
                    style={{
                      width: `${(stats.completedToday / 8) * 100}%`
                    }}
                  />
                </div>
              </div>
              
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600 mb-2">Következő ellenőrzés:</p>
                <div className="flex items-center gap-2 text-sm">
                  <Car className="w-4 h-4 text-gray-400" />
                  <span>Kapu #125 - 14:30</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Alert Cards */}
          {stats.failedInspections > 0 && (
            <Card className="border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2 text-red-700">
                  <AlertTriangle className="w-5 h-5" />
                  Figyelem szükséges
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-red-700 mb-3">
                  {stats.failedInspections} sikertelen ellenőrzés igényel azonnali beavatkozást.
                </p>
                <Button size="sm" variant="destructive" className="w-full">
                  Problémák megtekintése
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}