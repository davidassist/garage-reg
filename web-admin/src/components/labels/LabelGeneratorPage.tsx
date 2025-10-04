'use client'

import React, { useState, useEffect } from 'react'
import { LabelSheetPreview } from '@/components/labels/LabelSheetPreview'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  QrCode,
  FileText,
  Printer,
  Download,
  Grid3x3,
  Maximize2,
  CheckCircle2,
  AlertCircle
} from 'lucide-react'

interface LabelGeneratorPageProps {
  initialGates?: Array<{
    id: string
    name: string
    serialNumber?: string
    location?: string
  }>
}

export function LabelGeneratorPage({ initialGates = [] }: LabelGeneratorPageProps) {
  const [selectedGates, setSelectedGates] = useState(initialGates)
  const [printStats, setPrintStats] = useState({
    totalLabels: 0,
    totalPages: 0,
    estimatedTime: 0 // minutes
  })

  // Mock gates data if none provided
  const mockGates = [
    {
      id: 'gate-001',
      name: 'Főbejárat',
      serialNumber: 'SN-2024-001',
      location: 'Épület A - Főbejárat'
    },
    {
      id: 'gate-002', 
      name: 'Hátsó kapu',
      serialNumber: 'SN-2024-002',
      location: 'Épület A - Hátsó'
    },
    {
      id: 'gate-003',
      name: 'Személyzeti bejárat',
      serialNumber: 'SN-2024-003', 
      location: 'Épület B - Személyzet'
    },
    {
      id: 'gate-004',
      name: 'Teherkapu',
      serialNumber: 'SN-2024-004',
      location: 'Raktár - Teher'
    }
  ]

  const gates = selectedGates.length > 0 ? selectedGates : mockGates

  const handlePrint = (printUrl: string) => {
    console.log('Print URL generated:', printUrl)
    // Additional analytics or logging could go here
  }

  const features = [
    {
      icon: QrCode,
      title: 'QR kódos címkék',
      description: 'Automatikus QR kód generálás minden kapuhoz egyedi URL-lel'
    },
    {
      icon: Grid3x3,
      title: 'Többféle méret',
      description: '25×25mm, 38×19mm, 50×30mm és egyéb méretek A4 lapon'
    },
    {
      icon: Printer,
      title: 'Nyomtatóbarát',
      description: 'Optimalizálva Chrome/Edge margó nélküli nyomtatáshoz'
    },
    {
      icon: FileText,
      title: 'PDF export',
      description: 'Mentés PDF formátumban további feldolgozáshoz'
    }
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b pb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Címke generálás és nyomtatás
            </h1>
            <p className="mt-2 text-lg text-gray-600">
              QR kódos címkék készítése kapukhoz - nyomtatóbarát A4 elrendezéssel
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <Badge variant="secondary" className="gap-1">
              <CheckCircle2 className="w-3 h-3" />
              {gates.length} kapu
            </Badge>
            <Badge variant="outline" className="gap-1">
              <Printer className="w-3 h-3" />
              Chrome/Edge ready
            </Badge>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <Card key={index}>
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <feature.icon className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-medium">{feature.title}</h3>
                </div>
              </div>
              <p className="mt-2 text-sm text-gray-600">{feature.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Print Requirements */}
      <Card className="border-amber-200 bg-amber-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-800">
            <AlertCircle className="w-5 h-5" />
            Nyomtatási követelmények
          </CardTitle>
        </CardHeader>
        <CardContent className="text-amber-700">
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div>
              <h4 className="font-medium mb-2">📄 Papír</h4>
              <ul className="space-y-1">
                <li>• A4 fehér öntapadós címkelap</li>
                <li>• Megfelelő címke méret</li>
                <li>• Lézernyomtató ajánlott</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">🖨️ Beállítások</h4>
              <ul className="space-y-1">
                <li>• Margók: 0mm minden oldalon</li>
                <li>• Méretezés: 100%</li>
                <li>• Háttérszínek: Bekapcsolva</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">✅ Ellenőrzés</h4>
              <ul className="space-y-1">
                <li>• Próbanyomtatás normál papírra</li>
                <li>• QR kód tesztelés</li>
                <li>• Méret illeszkedés</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Label Generator */}
      <LabelSheetPreview 
        gates={gates}
        onPrint={handlePrint}
      />

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Gyors műveletek</CardTitle>
          <CardDescription>
            Gyakran használt funkciók közvetlen elérése
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <Button 
              variant="outline" 
              className="h-auto p-4 flex-col gap-2"
              onClick={() => window.open('/print/view', '_blank', 'width=1024,height=768')}
            >
              <Maximize2 className="w-6 h-6" />
              <span className="font-medium">Print View</span>
              <span className="text-xs text-gray-500">Dedikált nyomtatási nézet</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-auto p-4 flex-col gap-2"
              onClick={() => window.open('/print/view?mode=pdf', '_blank', 'width=1024,height=768')}
            >
              <Download className="w-6 h-6" />
              <span className="font-medium">PDF Előnézet</span>
              <span className="text-xs text-gray-500">Mentés PDF-ként</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-auto p-4 flex-col gap-2"
              onClick={() => window.open('https://docs.garagereg.hu/labels', '_blank')}
            >
              <FileText className="w-6 h-6" />
              <span className="font-medium">Dokumentáció</span>
              <span className="text-xs text-gray-500">Nyomtatási útmutató</span>
            </Button>
            
            <Button 
              variant="outline" 
              className="h-auto p-4 flex-col gap-2"
              onClick={() => window.open('/gates', '_blank')}
            >
              <QrCode className="w-6 h-6" />
              <span className="font-medium">QR Teszt</span>
              <span className="text-xs text-gray-500">Kódok ellenőrzése</span>
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Print Quality Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Nyomtatási minőség javítása</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-medium mb-3 text-green-700">✅ Javaslatok</h4>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-green-500">•</span>
                  <span>Lézernyomtató használata (éles QR kódok)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">•</span>
                  <span>Eredeti toner/festékpatron</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">•</span>
                  <span>Tiszta nyomtatófej</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500">•</span>
                  <span>Megfelelő papírminőség</span>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-3 text-red-700">❌ Kerülendő</h4>
              <ul className="space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-red-500">•</span>
                  <span>Rossz minőségű utántöltött patron</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">•</span>
                  <span>Gyors/piszkozat nyomtatási mód</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">•</span>
                  <span>Nem megfelelő címke méret</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">•</span>
                  <span>Böngésző nagyítás != 100%</span>
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}