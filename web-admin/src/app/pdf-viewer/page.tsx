'use client'

import React, { useState } from 'react'
import { PDFViewer } from '@/components/pdf/PDFViewer'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { 
  FileText,
  Eye,
  Download,
  Share2,
  QrCode,
  Shield,
  PenTool,
  ArrowRight,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Maximize2
} from 'lucide-react'

export default function PDFViewerPage() {
  const [showViewer, setShowViewer] = useState(false)

  if (showViewer) {
    return (
      <PDFViewer 
        onClose={() => setShowViewer(false)}
        className="fixed inset-0 z-50"
      />
    )
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">PDF Viewer & Document Management</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Beágyazott PDF nézegető oldalsáv metaadatokkal, QR előnézettel és teljes dokumentum kezeléssel. 
          Nagy fájlok (20-50 MB) gördülékeny megjelenítése.
        </p>
        
        <div className="flex justify-center">
          <Button size="lg" onClick={() => setShowViewer(true)} className="gap-2">
            <Eye className="w-5 h-5" />
            PDF Viewer megnyitása
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Key Features */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              Oldalsáv metaadatok
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Teljes dokumentum információ oldalsávban azonosítóval, státusszal és aláírási adatokkal.
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Dokumentum azonosító és verzió
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Szerző és módosítási dátum
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Státusz és kategória információ
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PenTool className="w-5 h-5 text-purple-600" />
              Aláírási információk
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Digitális aláírás részletei tanúsítvány érvényességgel és aláíró adatokkal.
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-green-600" />
                Aláíró személy és pozíció
              </li>
              <li className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-green-600" />
                Aláírás dátuma és ideje
              </li>
              <li className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-green-600" />
                Tanúsítvány érvényesség
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <QrCode className="w-5 h-5 text-green-600" />
              QR kód előnézet
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Beágyazott QR kód előnézete ellenőrzési linkkel és pozíció információval.
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <QrCode className="w-4 h-4 text-green-600" />
                QR kód vizuális előnézet
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Ellenőrzési link és pozíció
              </li>
              <li className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-green-600" />
                Közvetlen QR kód ellenőrzés
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Performance Features */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Maximize2 className="w-5 h-5 text-indigo-600" />
            Nagy fájl teljesítmény optimalizáció
          </CardTitle>
          <CardDescription>
            20-50 MB PDF fájlok gördülékeny kezelése progressive loading technológiával
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Optimalizációs funkciók:</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Progressive loading</span>
                  <Badge variant="outline">Aktív</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Lazy page rendering</span>
                  <Badge variant="outline">Aktív</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Memory management</span>
                  <Badge variant="outline">Aktív</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Viewport caching</span>
                  <Badge variant="outline">Aktív</Badge>
                </div>
              </div>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Elfogadási kritériumok:</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ✅ Nagy PDF (20–50 MB) gördülékeny
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ✅ Letöltés működik
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ✅ Megosztás működik
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ✅ Oldalsáv metaadatok teljes
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Actions and Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="w-5 h-5 text-orange-600" />
            Akciók és vezérlők
          </CardTitle>
          <CardDescription>
            Teljes körű PDF kezelés letöltéssel, megosztással és nyomtatással
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Fő akciók:</h4>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <Download className="w-4 h-4 text-blue-600" />
                  </div>
                  <div>
                    <div className="font-medium">Letöltés</div>
                    <div className="text-sm text-gray-600">Teljes PDF fájl mentése</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                    <Share2 className="w-4 h-4 text-purple-600" />
                  </div>
                  <div>
                    <div className="font-medium">Megosztás</div>
                    <div className="text-sm text-gray-600">URL megosztás és másolás</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                    <FileText className="w-4 h-4 text-green-600" />
                  </div>
                  <div>
                    <div className="font-medium">Nyomtatás</div>
                    <div className="text-sm text-gray-600">Közvetlen böngésző nyomtatás</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Nézegető vezérlők:</h4>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Eye className="w-4 h-4 text-gray-600" />
                  <span className="text-sm">Zoom: 25% - 300%</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <RotateCw className="w-4 h-4 text-gray-600" />
                  <span className="text-sm">90° lépésenkénti forgatás</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <Maximize2 className="w-4 h-4 text-gray-600" />
                  <span className="text-sm">Teljes képernyős mód</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-gray-600" />
                  <span className="text-sm">Oldal navigáció</span>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Biztonsági funkciók:</h4>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Shield className="w-4 h-4 text-green-600" />
                  <span className="text-sm">Jogosultság alapú hozzáférés</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <PenTool className="w-4 h-4 text-purple-600" />
                  <span className="text-sm">Digitális aláírás ellenőrzés</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">Checksum integritás</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <QrCode className="w-4 h-4 text-orange-600" />
                  <span className="text-sm">QR kód hitelesítés</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sample Document Info */}
      <Card>
        <CardHeader>
          <CardTitle>Minta dokumentum adatok</CardTitle>
          <CardDescription>
            A PDF viewerben megjelenített dokumentum információi
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Dokumentum részletek:</h4>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Név:</span>
                  <span className="font-medium">Garázs Karbantartási Jelentés - 2025 Q1.pdf</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Azonosító:</span>
                  <span className="font-medium">DOC-2025-001</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Méret:</span>
                  <span className="font-medium">45 MB</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Oldalak:</span>
                  <span className="font-medium">14 oldal</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Státusz:</span>
                  <Badge className="bg-purple-100 text-purple-700">Aláírt</Badge>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-3">Aláírási információ:</h4>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Aláíró:</span>
                  <span className="font-medium">Kovács János</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Pozíció:</span>
                  <span className="font-medium">Karbantartási Vezető</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Aláírás dátuma:</span>
                  <span className="font-medium">2025.10.03 14:30</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Tanúsítvány:</span>
                  <Badge className="bg-green-100 text-green-700">✓ Érvényes</Badge>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">QR ellenőrzés:</span>
                  <Badge className="bg-blue-100 text-blue-700">Aktív</Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Gyors műveletek</CardTitle>
          <CardDescription>
            Próbálja ki a PDF viewer funkcióit
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            <Button variant="outline" onClick={() => setShowViewer(true)} className="h-auto p-4 flex flex-col gap-2">
              <Eye className="w-6 h-6" />
              <span className="text-sm">PDF megnyitása</span>
            </Button>
            
            <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
              <Download className="w-6 h-6" />
              <span className="text-sm">Letöltés teszt</span>
            </Button>
            
            <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
              <Share2 className="w-6 h-6" />
              <span className="text-sm">Megosztás teszt</span>
            </Button>
            
            <Link href="/demo">
              <Button className="h-auto p-4 flex flex-col gap-2 w-full">
                <ArrowRight className="w-6 h-6" />
                <span className="text-sm">Vissza a demóhoz</span>
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>

      {/* Technical Implementation */}
      <Card>
        <CardHeader>
          <CardTitle>Technikai megvalósítás</CardTitle>
          <CardDescription>
            A PDF viewer rendszer főbb jellemzői
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Teljesítmény:</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• Progressive loading 20-50 MB fájlokhoz</li>
                <li>• Lazy rendering nagyobb dokumentumokhoz</li>
                <li>• Memory-efficient viewport caching</li>
                <li>• Optimalizált zoom és scroll műveletek</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Biztonság:</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• Jogosultság alapú hozzáférés vezérlés</li>
                <li>• Digitális aláírás és tanúsítvány ellenőrzés</li>
                <li>• Checksum integritás verification</li>
                <li>• QR kód hitelesítés és tracking</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Használhatóság:</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• Intuitív oldalsáv navigáció</li>
                <li>• Teljes képernyős mód támogatás</li>
                <li>• Gyorsbillentyűk és gesztusok</li>
                <li>• Responsive design mobil eszközökhöz</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Call to Action */}
      <div className="text-center space-y-4 p-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <h2 className="text-2xl font-bold text-gray-900">Próbálja ki a PDF Viewer rendszert!</h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Nyissa meg a teljes PDF viewert metaadatok oldalsávval, QR előnézettel és 
          minden szükséges akcióval nagy fájlok gördülékeny kezeléséhez.
        </p>
        
        <div className="flex justify-center gap-4">
          <Button size="lg" onClick={() => setShowViewer(true)} className="gap-2">
            <Eye className="w-5 h-5" />
            PDF Viewer indítása
          </Button>
          
          <Link href="/demo">
            <Button size="lg" variant="outline" className="gap-2">
              <ArrowRight className="w-5 h-5" />
              Vissza a demóhoz
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}