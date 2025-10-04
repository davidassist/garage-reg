'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  FileText,
  User,
  Calendar,
  MapPin,
  Camera,
  MessageSquare,
  Download,
  Share2,
  Flag,
  Eye,
  AlertCircle,
  Building2,
  Car,
  CheckSquare,
  Target
} from 'lucide-react'

interface InspectionSummary {
  id: string
  templateName: string
  objectType: 'gate' | 'building' | 'vehicle'
  objectId: string
  inspector: string
  startedAt: Date
  completedAt: Date
  actualDuration: number // minutes
  estimatedDuration: number
  totalItems: number
  completedItems: number
  failedItems: number
  skippedItems: number
  overallStatus: 'passed' | 'failed' | 'warning'
  notes: string
  photos: string[]
  location?: {
    lat: number
    lng: number
    address: string
  }
  checklist: {
    id: string
    title: string
    category: 'safety' | 'maintenance' | 'compliance' | 'documentation'
    status: 'completed' | 'failed' | 'skipped'
    value?: any
    notes?: string
    photos?: string[]
    required: boolean
    timestamp: Date
  }[]
}

interface InspectionCompleteSummaryProps {
  inspection: InspectionSummary
  onClose: () => void
  onNewInspection?: () => void
  onViewDetails?: () => void
}

// Mock data for demonstration
const mockInspection: InspectionSummary = {
  id: 'inspection-001',
  templateName: 'Napi biztonsági ellenőrzés',
  objectType: 'gate',
  objectId: 'gate-123',
  inspector: 'Kovács János',
  startedAt: new Date(Date.now() - 18 * 60 * 1000), // Started 18 minutes ago
  completedAt: new Date(),
  actualDuration: 18,
  estimatedDuration: 15,
  totalItems: 6,
  completedItems: 4,
  failedItems: 1,
  skippedItems: 1,
  overallStatus: 'warning',
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
  checklist: [
    {
      id: 'check-1',
      title: 'Kapu működésének ellenőrzése',
      category: 'safety',
      status: 'completed',
      value: true,
      required: true,
      timestamp: new Date(Date.now() - 16 * 60 * 1000)
    },
    {
      id: 'check-2',
      title: 'Biztonsági szenzorok tesztelése',
      category: 'safety',
      status: 'failed',
      value: 'Hibás',
      notes: 'Alsó szenzor nem érzékeli az akadályokat',
      required: true,
      timestamp: new Date(Date.now() - 12 * 60 * 1000)
    },
    {
      id: 'check-3',
      title: 'Távvezérlő funkciók',
      category: 'maintenance',
      status: 'completed',
      value: true,
      required: false,
      timestamp: new Date(Date.now() - 8 * 60 * 1000)
    },
    {
      id: 'check-4',
      title: 'Kenőanyag szint',
      category: 'maintenance',
      status: 'completed',
      value: 'Megfelelő',
      required: true,
      timestamp: new Date(Date.now() - 5 * 60 * 1000)
    },
    {
      id: 'check-5',
      title: 'Dokumentáció fotók',
      category: 'documentation',
      status: 'completed',
      photos: ['photo1.jpg', 'photo2.jpg'],
      required: false,
      timestamp: new Date(Date.now() - 3 * 60 * 1000)
    },
    {
      id: 'check-6',
      title: 'Megjegyzések',
      category: 'documentation',
      status: 'skipped',
      required: false,
      timestamp: new Date(Date.now() - 1 * 60 * 1000)
    }
  ]
}

export function InspectionCompleteSummary({
  inspection = mockInspection,
  onClose,
  onNewInspection,
  onViewDetails
}: InspectionCompleteSummaryProps) {
  const [showFullChecklist, setShowFullChecklist] = useState(false)

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4 text-green-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'skipped':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />
      default:
        return <CheckSquare className="w-4 h-4 text-gray-400" />
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

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'safety':
        return 'bg-red-50 text-red-700 border-red-200'
      case 'maintenance':
        return 'bg-blue-50 text-blue-700 border-blue-200'
      case 'compliance':
        return 'bg-green-50 text-green-700 border-green-200'
      case 'documentation':
        return 'bg-purple-50 text-purple-700 border-purple-200'
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200'
    }
  }

  const getObjectIcon = (objectType: string) => {
    switch (objectType) {
      case 'gate':
        return <Car className="w-5 h-5" />
      case 'building':
        return <Building2 className="w-5 h-5" />
      case 'vehicle':
        return <Car className="w-5 h-5" />
      default:
        return <Target className="w-5 h-5" />
    }
  }

  const formatDuration = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    
    if (hours > 0) {
      return `${hours}ó ${mins}p`
    }
    return `${mins} perc`
  }

  const completionRate = (inspection.completedItems / inspection.totalItems) * 100
  const isOvertime = inspection.actualDuration > inspection.estimatedDuration

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <Card className="border-2 border-green-200 bg-green-50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2 text-2xl">
                <Flag className="w-7 h-7 text-green-600" />
                Ellenőrzés befejezve
              </CardTitle>
              <p className="text-green-700 mt-2">
                Az ellenőrzés sikeresen befejezését követően az alábbi összesítő készült.
              </p>
            </div>
            
            <Badge className={`text-lg px-4 py-2 ${getStatusColor(inspection.overallStatus)}`}>
              {inspection.overallStatus === 'passed' && 'Megfelelő'}
              {inspection.overallStatus === 'failed' && 'Sikertelen'}
              {inspection.overallStatus === 'warning' && 'Figyelmeztetés'}
            </Badge>
          </div>
        </CardHeader>
      </Card>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Main Summary */}
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="w-5 h-5" />
                Ellenőrzés adatok
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label>Sablon neve</Label>
                  <p className="font-medium">{inspection.templateName}</p>
                </div>
                <div>
                  <Label>Ellenőr</Label>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-gray-500" />
                    <span className="font-medium">{inspection.inspector}</span>
                  </div>
                </div>
                <div>
                  <Label>Ellenőrzés tárgya</Label>
                  <div className="flex items-center gap-2">
                    {getObjectIcon(inspection.objectType)}
                    <span className="font-medium">
                      {inspection.objectType === 'gate' && 'Garázs kapu'}
                      {inspection.objectType === 'building' && 'Épület'}
                      {inspection.objectType === 'vehicle' && 'Jármű'}
                      #{inspection.objectId}
                    </span>
                  </div>
                </div>
                <div>
                  <Label>Befejezés időpontja</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-500" />
                    <span className="font-medium">
                      {inspection.completedAt.toLocaleString('hu-HU')}
                    </span>
                  </div>
                </div>
              </div>
              
              {inspection.location && (
                <div>
                  <Label>Helyszín</Label>
                  <div className="flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-gray-500" />
                    <span className="font-medium">{inspection.location.address}</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Ellenőrzési statisztikák</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {inspection.totalItems}
                  </div>
                  <div className="text-sm text-gray-600">Összes pont</div>
                </div>
                
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-700">
                    {inspection.completedItems}
                  </div>
                  <div className="text-sm text-green-600">Sikeres</div>
                </div>
                
                <div className="text-center p-4 bg-red-50 rounded-lg">
                  <div className="text-2xl font-bold text-red-700">
                    {inspection.failedItems}
                  </div>
                  <div className="text-sm text-red-600">Hibás</div>
                </div>
                
                <div className="text-center p-4 bg-yellow-50 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-700">
                    {inspection.skippedItems}
                  </div>
                  <div className="text-sm text-yellow-600">Kihagyva</div>
                </div>
              </div>
              
              <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Teljesítési arány</span>
                  <span className="font-bold text-blue-700">
                    {Math.round(completionRate)}%
                  </span>
                </div>
                <div className="w-full bg-blue-200 rounded-full h-2">
                  <div 
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{ width: `${completionRate}%` }}
                  />
                </div>
              </div>
              
              <div className="mt-4 flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-gray-500" />
                  <span>Időtartam:</span>
                  <span className={`font-medium ${isOvertime ? 'text-red-600' : 'text-green-600'}`}>
                    {formatDuration(inspection.actualDuration)}
                  </span>
                  <span className="text-gray-500">
                    / {formatDuration(inspection.estimatedDuration)} tervezett
                  </span>
                </div>
                
                {isOvertime && (
                  <div className="flex items-center gap-1 text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <span>Túllépés: {formatDuration(inspection.actualDuration - inspection.estimatedDuration)}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Checklist Summary */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Ellenőrzési lista részletei</CardTitle>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFullChecklist(!showFullChecklist)}
                >
                  {showFullChecklist ? 'Összevonás' : 'Részletek'}
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {inspection.checklist
                  .filter((_, index) => showFullChecklist || index < 3)
                  .map((item) => (
                    <div
                      key={item.id}
                      className="flex items-start gap-3 p-3 border rounded-lg"
                    >
                      {getStatusIcon(item.status)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{item.title}</h4>
                          <Badge className={`text-xs ${getCategoryColor(item.category)}`}>
                            {item.category}
                          </Badge>
                          {item.required && (
                            <Badge variant="destructive" className="text-xs">
                              Kötelező
                            </Badge>
                          )}
                        </div>
                        
                        {item.value && (
                          <p className="text-sm text-gray-600 mb-1">
                            <strong>Eredmény:</strong> {item.value.toString()}
                          </p>
                        )}
                        
                        {item.notes && (
                          <p className="text-sm text-gray-600 mb-1">
                            <strong>Megjegyzés:</strong> {item.notes}
                          </p>
                        )}
                        
                        {item.photos && item.photos.length > 0 && (
                          <div className="flex items-center gap-1 text-sm text-blue-600">
                            <Camera className="w-3 h-3" />
                            {item.photos.length} fotó
                          </div>
                        )}
                        
                        <div className="text-xs text-gray-500 mt-2">
                          {item.timestamp.toLocaleString('hu-HU')}
                        </div>
                      </div>
                    </div>
                  ))}
                
                {!showFullChecklist && inspection.checklist.length > 3 && (
                  <div className="text-center py-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowFullChecklist(true)}
                    >
                      +{inspection.checklist.length - 3} további elem megtekintése
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Műveletek</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button className="w-full gap-2" onClick={onViewDetails}>
                <Eye className="w-4 h-4" />
                Részletek megtekintése
              </Button>
              
              <Button variant="outline" className="w-full gap-2">
                <Download className="w-4 h-4" />
                Jelentés letöltése
              </Button>
              
              <Button variant="outline" className="w-full gap-2">
                <Share2 className="w-4 h-4" />
                Jelentés megosztása
              </Button>
              
              {onNewInspection && (
                <Button variant="outline" className="w-full gap-2" onClick={onNewInspection}>
                  <FileText className="w-4 h-4" />
                  Új ellenőrzés
                </Button>
              )}
              
              <Button variant="outline" className="w-full" onClick={onClose}>
                Bezárás
              </Button>
            </CardContent>
          </Card>

          {/* Photos */}
          {inspection.photos.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Camera className="w-4 h-4" />
                  Fotók ({inspection.photos.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2">
                  {inspection.photos.slice(0, 4).map((photo, index) => (
                    <div key={index} className="aspect-square relative">
                      <img
                        src={photo}
                        alt={`Inspection photo ${index + 1}`}
                        className="w-full h-full object-cover rounded border"
                      />
                      {index === 3 && inspection.photos.length > 4 && (
                        <div className="absolute inset-0 bg-black/50 rounded flex items-center justify-center">
                          <span className="text-white font-medium">
                            +{inspection.photos.length - 4}
                          </span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* General Notes */}
          {inspection.notes && (
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Általános megjegyzések
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-700 leading-relaxed">
                  {inspection.notes}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Key Issues */}
          {inspection.failedItems > 0 && (
            <Card className="border-red-200 bg-red-50">
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2 text-red-700">
                  <AlertCircle className="w-4 h-4" />
                  Kritikus problémák
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {inspection.checklist
                    .filter(item => item.status === 'failed')
                    .map(item => (
                      <div key={item.id} className="text-sm">
                        <p className="font-medium text-red-800">{item.title}</p>
                        {item.notes && (
                          <p className="text-red-600 mt-1">{item.notes}</p>
                        )}
                      </div>
                    ))}
                </div>
                
                <div className="mt-3 p-3 bg-red-100 rounded border border-red-200">
                  <p className="text-sm text-red-800 font-medium">
                    Ajánlás: A hibás elemek sürgős javítást igényelnek.
                  </p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}

// Helper Label component
function Label({ children }: { children: React.ReactNode }) {
  return (
    <label className="text-sm font-medium text-gray-700 block mb-1">
      {children}
    </label>
  )
}