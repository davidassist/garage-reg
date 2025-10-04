'use client'

import React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import Link from 'next/link'
import { 
  Calendar,
  Clock,
  Users,
  Download,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  FileText,
  Keyboard,
  Eye,
  Filter
} from 'lucide-react'

export default function CalendarDemoPage() {
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-900">Karbantartási Naptár Demo</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Teljes körű naptár nézet ellenőrzésekhez és munkalapokhoz hét/hónap nézettel, 
          technikus szűrővel és ICS export funkcióval.
        </p>
        
        <div className="flex justify-center">
          <Link href="/calendar">
            <Button size="lg" className="gap-2">
              <Calendar className="w-5 h-5" />
              Naptár megnyitása
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </div>

      {/* Key Features */}
      <div className="grid md:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              Hét/Hónap nézetek
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Váltás heti és havi nézet között gyors navigációval.
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Heti részletes nézet
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Havi áttekintő nézet
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Gyors dátum navigáció
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5 text-purple-600" />
              Technikus szűrő
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Szűrés technikusok szerint a jobb áttekinthetőség érdekében.
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-purple-600" />
                Nagy Péter
              </li>
              <li className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-purple-600" />
                Szabó Anna
              </li>
              <li className="flex items-center gap-2">
                <Filter className="w-4 h-4 text-purple-600" />
                További technikusok...
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Download className="w-5 h-5 text-green-600" />
              ICS Export
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Exportálás .ics formátumban külső naptár alkalmazásokba.
            </p>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Outlook kompatibilis
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Google Calendar
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                Apple Calendar
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Keyboard Navigation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Keyboard className="w-5 h-5 text-indigo-600" />
            Billentyűzet navigáció
          </CardTitle>
          <CardDescription>
            Gyors és hatékony navigáció billentyűzettel az akadálymentesség érdekében
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Navigációs billentyűk:</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Fel/Le nyíl</span>
                  <Badge variant="outline">Esemény navigáció</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Enter / Szóköz</span>
                  <Badge variant="outline">Esemény megnyitása</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Escape</span>
                  <Badge variant="outline">Navigáció visszaállítása</Badge>
                </div>
              </div>
            </div>
            
            <div className="space-y-3">
              <h4 className="font-medium text-gray-900">Elfogadási kritériumok:</h4>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ✅ Navigáció gyors
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ✅ Esemény kártya billentyűvel nyitható
                </li>
                <li className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  ✅ Akadálymentesség támogatás
                </li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Sample Events */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-orange-600" />
            Minta események
          </CardTitle>
          <CardDescription>
            A naptárban található események típusai és státuszai
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Esemény típusok:</h4>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <div>
                    <div className="font-medium">Ellenőrzések</div>
                    <div className="text-sm text-gray-600">Rendszeres biztonsági ellenőrzések</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <div>
                    <div className="font-medium">Karbantartás</div>
                    <div className="text-sm text-gray-600">Tervezett karbantartási munkák</div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3 p-3 border rounded-lg">
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <div>
                    <div className="font-medium">Javítás</div>
                    <div className="text-sm text-gray-600">Hibaelhárítási munkák</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-medium text-gray-900">Státusz jelzések:</h4>
              
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle2 className="w-4 h-4 text-green-600" />
                  <span className="text-sm">Befejezett</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <Clock className="w-4 h-4 text-blue-600" />
                  <span className="text-sm">Folyamatban</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <AlertTriangle className="w-4 h-4 text-red-600" />
                  <span className="text-sm">Késésben</span>
                </div>
                
                <div className="flex items-center gap-3">
                  <FileText className="w-4 h-4 text-gray-600" />
                  <span className="text-sm">Tervezett</span>
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
            A naptárban elérhető főbb funkciók
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
              <Eye className="w-6 h-6" />
              <span className="text-sm">Esemény részletek</span>
            </Button>
            
            <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
              <Filter className="w-6 h-6" />
              <span className="text-sm">Technikus szűrő</span>
            </Button>
            
            <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
              <Download className="w-6 h-6" />
              <span className="text-sm">ICS Export</span>
            </Button>
            
            <Link href="/calendar">
              <Button className="h-auto p-4 flex flex-col gap-2 w-full">
                <Calendar className="w-6 h-6" />
                <span className="text-sm">Naptár megnyitása</span>
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
            A naptár rendszer főbb jellemzői
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Nézetek:</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• Heti nézet (7 nap)</li>
                <li>• Havi nézet (6 hét rács)</li>
                <li>• Hét kezdése hétfőn</li>
                <li>• Hétvégék kiemelése</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Interakció:</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• Gyors dátum navigáció</li>
                <li>• Esemény kattintás/billentyű</li>
                <li>• Technikus szűrés</li>
                <li>• Ma gomb</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Export:</h4>
              <ul className="space-y-1 text-sm text-gray-600">
                <li>• iCalendar (.ics) formátum</li>
                <li>• Összes esemény adat</li>
                <li>• Külső naptár kompatibilitás</li>
                <li>• Automatikus fájl letöltés</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Call to Action */}
      <div className="text-center space-y-4 p-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
        <h2 className="text-2xl font-bold text-gray-900">Próbálja ki a naptár rendszert!</h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Navigáljon a teljes karbantartási naptárban, szűrjön technikusok szerint, 
          és exportálja az eseményeket külső alkalmazásokba.
        </p>
        
        <div className="flex justify-center gap-4">
          <Link href="/calendar">
            <Button size="lg" className="gap-2">
              <Calendar className="w-5 h-5" />
              Naptár indítása
            </Button>
          </Link>
          
          <Link href="/maintenance">
            <Button size="lg" variant="outline" className="gap-2">
              <FileText className="w-5 h-5" />
              Karbantartás áttekintés
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}