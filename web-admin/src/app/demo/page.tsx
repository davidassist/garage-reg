'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  FileText,
  Play,
  CheckCircle2,
  AlertTriangle,
  Camera,
  Upload,
  Eye,
  Code2,
  Layers3,
  Palette,
  FormInput,
  Database,
  Calendar
} from 'lucide-react'

import { InspectionSystemDemo } from '@/components/inspections/InspectionSystemDemo'

interface DemoStats {
  formComponents: number
  maxFileSize: string
  supportedFormats: string[]
  inspectionTemplates: number
  autoSaveInterval: string
  offlineSupport: boolean
}

const demoStats: DemoStats = {
  formComponents: 5,
  maxFileSize: '100MB',
  supportedFormats: ['JPEG', 'PNG', 'WEBP', 'HEIC'],
  inspectionTemplates: 4,
  autoSaveInterval: '2 másodperc',
  offlineSupport: true
}

export default function CompleteDemoPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [demoFormData, setDemoFormData] = useState<any>(null)
  const [uploadedPhotos, setUploadedPhotos] = useState<string[]>([])

  const handleFormSubmit = (data: any) => {
    console.log('Form submitted:', data)
    setDemoFormData(data)
  }

  const handlePhotosUploaded = (photos: any[]) => {
    console.log('Photos uploaded:', photos)
    setUploadedPhotos(photos.map(p => p.url))
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl">
            <Layers3 className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            Komplex Rendszer Demó
          </h1>
        </div>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Átfogó bemutató a dinamikus űrlap motor, fejlett fotó feltöltés és 
          intelligens ellenőrzési rendszer funkcióiról
        </p>
        
        {/* Quick Stats */}
        <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4 mt-8">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-4 text-center">
              <FormInput className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-blue-900">{demoStats.formComponents}</div>
              <div className="text-xs text-blue-700">Űrlap komponens</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-4 text-center">
              <Upload className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-green-900">{demoStats.maxFileSize}</div>
              <div className="text-xs text-green-700">Max fájlméret</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="p-4 text-center">
              <Camera className="w-6 h-6 text-purple-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-purple-900">{demoStats.supportedFormats.length}</div>
              <div className="text-xs text-purple-700">Képformátum</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <CardContent className="p-4 text-center">
              <FileText className="w-6 h-6 text-orange-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-orange-900">{demoStats.inspectionTemplates}</div>
              <div className="text-xs text-orange-700">Ellenőrzési sablon</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <CardContent className="p-4 text-center">
              <Database className="w-6 h-6 text-red-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-red-900">{demoStats.autoSaveInterval}</div>
              <div className="text-xs text-red-700">Auto-mentés</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-gray-50 to-gray-100 border-gray-200">
            <CardContent className="p-4 text-center">
              <CheckCircle2 className="w-6 h-6 text-gray-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-gray-900">
                {demoStats.offlineSupport ? 'IGEN' : 'NEM'}
              </div>
              <div className="text-xs text-gray-700">Offline támogatás</div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Demo Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-4 gap-1 h-auto p-1 bg-gray-100">
          <TabsTrigger 
            value="overview" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm flex flex-col gap-1 p-3"
          >
            <Eye className="w-4 h-4" />
            <span className="text-xs">Áttekintés</span>
          </TabsTrigger>
          <TabsTrigger 
            value="forms" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm flex flex-col gap-1 p-3"
          >
            <FormInput className="w-4 h-4" />
            <span className="text-xs">Dinamikus Űrlapok</span>
          </TabsTrigger>
          <TabsTrigger 
            value="photos" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm flex flex-col gap-1 p-3"
          >
            <Camera className="w-4 h-4" />
            <span className="text-xs">Fotó Rendszer</span>
          </TabsTrigger>
          <TabsTrigger 
            value="inspections" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm flex flex-col gap-1 p-3"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span className="text-xs">Ellenőrzések</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6 space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* System Architecture */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Layers3 className="w-5 h-5" />
                  Rendszer architektúra
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      <FormInput className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <h4 className="font-medium">Dinamikus Űrlap Motor</h4>
                      <p className="text-sm text-gray-600">5 komponens típus, validáció, függőségek</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                      <Camera className="w-4 h-4 text-green-600" />
                    </div>
                    <div>
                      <h4 className="font-medium">Fejlett Fotó Rendszer</h4>
                      <p className="text-sm text-gray-600">100MB fájlok, folytatható feltöltés, EXIF</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                      <CheckCircle2 className="w-4 h-4 text-purple-600" />
                    </div>
                    <div>
                      <h4 className="font-medium">Intelligens Ellenőrzések</h4>
                      <p className="text-sm text-gray-600">Auto-mentés, offline mód, workflow</p>
                    </div>
                  </div>
                </div>
                
                <div className="pt-3 border-t">
                  <h4 className="font-medium mb-2">Kulcs technológiák:</h4>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">Next.js 14</Badge>
                    <Badge variant="outline">TypeScript</Badge>
                    <Badge variant="outline">React 18+</Badge>
                    <Badge variant="outline">shadcn/ui</Badge>
                    <Badge variant="outline">Tailwind CSS</Badge>
                    <Badge variant="outline">localStorage</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Key Features */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="w-5 h-5" />
                  Főbb funkcionalitások
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">✓</div>
                    <div className="text-sm font-medium">Rugalmas űrlapok</div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">✓</div>
                    <div className="text-sm font-medium">Nagy fájlok</div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">✓</div>
                    <div className="text-sm font-medium">Auto-mentés</div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">✓</div>
                    <div className="text-sm font-medium">Offline mód</div>
                  </div>
                </div>
                
                <div className="space-y-2">
                  <h4 className="font-medium">Teljesítmény mutatók:</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Űrlap renderelési idő:</span>
                      <span className="font-medium text-green-600">&lt; 100ms</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Feltöltési sebesség:</span>
                      <span className="font-medium text-blue-600">5MB/s</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Offline perzisztencia:</span>
                      <span className="font-medium text-purple-600">localStorage</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Gyors navigáció</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col gap-2"
                  onClick={() => setActiveTab('forms')}
                >
                  <FormInput className="w-6 h-6" />
                  <span>Űrlap demó megtekintése</span>
                  <span className="text-xs text-gray-500">5 komponens típus kipróbálása</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col gap-2"
                  onClick={() => setActiveTab('photos')}
                >
                  <Camera className="w-6 h-6" />
                  <span>Fotó rendszer tesztelése</span>
                  <span className="text-xs text-gray-500">Nagy fájlok és EXIF adatok</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col gap-2"
                  onClick={() => setActiveTab('inspections')}
                >
                  <CheckCircle2 className="w-6 h-6" />
                  <span>Ellenőrzés indítása</span>
                  <span className="text-xs text-gray-500">Teljes workflow kipróbálása</span>
                </Button>
                
                <Link href="/calendar/demo">
                  <Button 
                    variant="outline" 
                    className="h-auto p-4 flex flex-col gap-2 w-full"
                  >
                    <Calendar className="w-6 h-6" />
                    <span>Karbantartási Naptár</span>
                    <span className="text-xs text-gray-500">Hét/hónap nézet + ICS export</span>
                  </Button>
                </Link>
                
                <Link href="/pdf-viewer">
                  <Button 
                    variant="default" 
                    className="h-auto p-4 flex flex-col gap-2 w-full"
                  >
                    <FileText className="w-6 h-6" />
                    <span>PDF Viewer</span>
                    <span className="text-xs opacity-90">Nagy fájl + metaadatok</span>
                  </Button>
                </Link>
                
                <Link href="/analytics/demo">
                  <Button 
                    variant="default" 
                    className="h-auto p-4 flex flex-col gap-2 w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                  >
                    <div className="flex items-center gap-1">
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M3 4a1 1 0 011-1h12a1 1 0 011 1v2a1 1 0 01-1 1H4a1 1 0 01-1-1V4zM3 10a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H4a1 1 0 01-1-1v-6zM14 9a1 1 0 00-1 1v6a1 1 0 001 1h2a1 1 0 001-1v-6a1 1 0 00-1-1h-2z" />
                      </svg>
                    </div>
                    <span>Analitikai Grafikonok</span>
                    <span className="text-xs opacity-90">Recharts + CSV/XLSX export</span>
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Forms Tab */}
        <TabsContent value="forms" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FormInput className="w-5 h-5" />
                Dinamikus Űrlap Motor Demó
              </CardTitle>
              <div className="text-sm text-gray-600">
                Interaktív bemutató a 5 űrlap komponens típusról: szöveges, numerikus, választó, dátum és fájl feltöltés
              </div>
            </CardHeader>
            <CardContent>
              <div className="p-8 bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg border-2 border-dashed border-blue-200 text-center">
                <FormInput className="w-12 h-12 text-blue-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Dinamikus Űrlap Motor</h3>
                <p className="text-gray-600 mb-4">
                  5 komponens típus: szöveges mezők, számok, választók, dátumok és fájl feltöltés
                </p>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
                  <Badge variant="outline" className="p-2">Text Input</Badge>
                  <Badge variant="outline" className="p-2">Number</Badge>
                  <Badge variant="outline" className="p-2">Select</Badge>
                  <Badge variant="outline" className="p-2">Date</Badge>
                  <Badge variant="outline" className="p-2">File Upload</Badge>
                </div>
                <p className="text-sm text-blue-600">
                  ✓ Dinamikus validáció • ✓ Függőségi logika • ✓ Automatikus layout
                </p>
              </div>
              
              {demoFormData && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">✓ Űrlap sikeresen elküldve</h4>
                  <pre className="text-xs text-green-700 overflow-auto">
                    {JSON.stringify(demoFormData, null, 2)}
                  </pre>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Photos Tab */}
        <TabsContent value="photos" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="w-5 h-5" />
                Fejlett Fotó Feltöltő Rendszer
              </CardTitle>
              <div className="text-sm text-gray-600">
                Nagyfelbontású képek, folytatható feltöltés, EXIF metaadatok és galéria nézet
              </div>
            </CardHeader>
            <CardContent>
              <div className="p-8 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg border-2 border-dashed border-green-200 text-center">
                <Camera className="w-12 h-12 text-green-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-800 mb-2">Fejlett Fotó Rendszer</h3>
                <p className="text-gray-600 mb-4">
                  Nagy fájlok (100MB), folytatható feltöltés, EXIF feldolgozás és galéria nézet
                </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  <Badge variant="outline" className="p-2">JPEG/PNG</Badge>
                  <Badge variant="outline" className="p-2">WEBP/HEIC</Badge>
                  <Badge variant="outline" className="p-2">100MB Max</Badge>
                  <Badge variant="outline" className="p-2">Drag & Drop</Badge>
                </div>
                <p className="text-sm text-green-600">
                  ✓ Folytatható feltöltés • ✓ EXIF metaadatok • ✓ Képoptimalizálás
                </p>
              </div>
              
              {uploadedPhotos.length > 0 && (
                <div className="mt-6">
                  <h4 className="font-medium mb-3">Feltöltött fotók ({uploadedPhotos.length})</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                    {uploadedPhotos.map((photo, index) => (
                      <div key={index} className="aspect-square relative">
                        <img
                          src={photo}
                          alt={`Uploaded photo ${index + 1}`}
                          className="w-full h-full object-cover rounded border"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Inspections Tab */}
        <TabsContent value="inspections" className="mt-6">
          <InspectionSystemDemo />
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <Card className="bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200">
        <CardContent className="p-6">
          <div className="text-center space-y-2">
            <h3 className="font-semibold text-lg">🎉 Komplex Rendszer Demó</h3>
            <p className="text-gray-600">
              Ez a bemutató a teljes rendszer képességeit mutatja be egyetlen, integrált felületen keresztül.
            </p>
            <div className="flex items-center justify-center gap-4 mt-4">
              <Badge variant="outline" className="gap-1">
                <Code2 className="w-3 h-3" />
                TypeScript Ready
              </Badge>
              <Badge variant="outline" className="gap-1">
                <CheckCircle2 className="w-3 h-3" />
                Production Quality
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Layers3 className="w-3 h-3" />
                Modular Architecture
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}