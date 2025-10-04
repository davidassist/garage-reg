'use client'

import React from 'react'
import { AnalyticsCharts } from '@/components/analytics/AnalyticsCharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  BarChart3, 
  PieChart, 
  TrendingUp, 
  Download, 
  Filter,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Eye,
  Settings,
  RefreshCw
} from 'lucide-react'

export default function AnalyticsDemoPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Analitikai grafikonok és export rendszer
              </h1>
              <p className="mt-2 text-lg text-gray-600">
                Recharts alapú vizualizációk szűrőkkel és CSV/XLSX export funkcióval
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                <CheckCircle2 className="w-3 h-3 mr-1" />
                Teljes implementáció
              </Badge>
            </div>
          </div>
        </div>
      </div>

      {/* Features Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="text-center">
              <BarChart3 className="w-12 h-12 mx-auto text-blue-600 mb-4" />
              <CardTitle>Recharts grafikonok</CardTitle>
              <CardDescription>
                Bar, Line, Pie és Area chartok komplett tooltipekkel és legendákkal
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Lejáró ellenőrzések pie chart</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>SLA teljesülés line chart</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Hibastatisztika horizontal bar chart</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Responsive design minden eszközön</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <Filter className="w-12 h-12 mx-auto text-purple-600 mb-4" />
              <CardTitle>Univerzális szűrők</CardTitle>
              <CardDescription>
                Minden grafikonra alkalmazható szűrési rendszer
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Dátum szűrő (hét/hónap/negyedév/év)</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Telephely alapú szűrés</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Státusz szerinti csoportosítás</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Kategória alapú összesítés</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="text-center">
              <Download className="w-12 h-12 mx-auto text-green-600 mb-4" />
              <CardTitle>Export funkciók</CardTitle>
              <CardDescription>
                CSV és XLSX export minden adattípushoz
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>CSV letöltés react-csv-vel</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Excel export xlsx könyvtárral</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Szűrt adatok export támogatás</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="w-4 h-4 text-green-600" />
                <span>Automatikus fájlnév dátummal</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Technical Implementation */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Technikai megvalósítás részletei
            </CardTitle>
            <CardDescription>
              Recharts integráció, export rendszer és adatkezelés
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-3">Chart könyvtárak</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">recharts</code> - Fő chart könyvtár
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">ResponsiveContainer</code> - Reszponzív méretek
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">Tooltip, Legend</code> - Interaktivitás
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">CartesianGrid</code> - Rács megjelenítés
                  </li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Export funkciók</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">react-csv</code> - CSV export kezelés
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">xlsx</code> - Excel fájl generálás
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">date-fns</code> - Dátum formázás
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600" />
                    <code className="bg-gray-100 px-2 py-1 rounded">DropdownMenu</code> - Export opciók UI
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h4 className="font-semibold text-blue-900 mb-2">Szűrési algoritmus</h4>
              <p className="text-blue-800 text-sm">
                A <code className="bg-blue-100 px-1 rounded">useMemo</code> hook biztosítja a hatékony adatszűrést. 
                Minden szűrő változásnál újraszámolásra kerül az összes chart adat, 
                így biztosítva a konzisztens megjelenítést minden vizualizációban.
              </p>
            </div>

            <div className="mt-4 p-4 bg-green-50 rounded-lg">
              <h4 className="font-semibold text-green-900 mb-2">Teljesítmény optimalizálás</h4>
              <p className="text-green-800 text-sm">
                A <code className="bg-green-100 px-1 rounded">useCallback</code> hooks minimalizálják az újrarenderelést. 
                A <code className="bg-green-100 px-1 rounded">ResponsiveContainer</code> automatikusan alkalmazkodik a képernyő méretekhez,
                míg a színsémák const objektumokban tárolódnak a memória hatékonyság érdekében.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Data Structure Examples */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="w-5 h-5" />
              Adatstruktúra példák
            </CardTitle>
            <CardDescription>
              Chart típusok és a hozzájuk tartozó adatformátumok
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid lg:grid-cols-3 gap-6">
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <PieChart className="w-4 h-4" />
                  Lejáró ellenőrzések (Pie)
                </h3>
                <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
{`[
  { name: "Lejárt", value: 2 },
  { name: "1-3 nap", value: 3 },
  { name: "4-7 nap", value: 1 },
  { name: "1+ hét", value: 4 }
]`}
                </pre>
              </div>
              
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  SLA teljesülés (Line)
                </h3>
                <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
{`[
  {
    period: "Jan 2024",
    target: 95,
    achieved: 87,
    total: 150
  },
  ...
]`}
                </pre>
              </div>
              
              <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Hibastatisztika (Bar)
                </h3>
                <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
{`[
  {
    category: "Kapu meghibásodás",
    count: 15,
    severity: "high"
  },
  ...
]`}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Integration Guide */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <RefreshCw className="w-5 h-5" />
              Integrációs útmutató
            </CardTitle>
            <CardDescription>
              Valós adatforrások csatlakoztatása és API integráció
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border-l-4 border-blue-500 bg-blue-50">
                <h4 className="font-semibold text-blue-900 mb-2">1. API adatok lecserélése</h4>
                <p className="text-blue-800 text-sm mb-2">
                  A jelenlegi mock adatgenerátorokat cserélje le valós API hívásokra:
                </p>
                <pre className="text-xs bg-blue-100 p-2 rounded">
{`// Helyette: generateExpiringInspections()
const fetchInspections = async () => {
  const response = await fetch('/api/inspections')
  return response.json()
}`}
                </pre>
              </div>

              <div className="p-4 border-l-4 border-green-500 bg-green-50">
                <h4 className="font-semibold text-green-900 mb-2">2. Szűrők backend továbbítása</h4>
                <p className="text-green-800 text-sm mb-2">
                  A szűrő paramétereket küldje el a backend API-nak optimális teljesítményért:
                </p>
                <pre className="text-xs bg-green-100 p-2 rounded">
{`const fetchFilteredData = async (filters) => {
  const params = new URLSearchParams(filters)
  const response = await fetch(\`/api/analytics?\${params}\`)
  return response.json()
}`}
                </pre>
              </div>

              <div className="p-4 border-l-4 border-orange-500 bg-orange-50">
                <h4 className="font-semibold text-orange-900 mb-2">3. Real-time frissítés</h4>
                <p className="text-orange-800 text-sm mb-2">
                  WebSocket vagy polling mechanizmus implementálása valós idejű adatokhoz:
                </p>
                <pre className="text-xs bg-orange-100 p-2 rounded">
{`useEffect(() => {
  const interval = setInterval(fetchData, 30000) // 30s
  return () => clearInterval(interval)
}, [filters])`}
                </pre>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Live Demo Button */}
        <div className="text-center">
          <Button size="lg" className="gap-2">
            <Eye className="w-5 h-5" />
            Élő demó megtekintése
            <ArrowRight className="w-5 h-5" />
          </Button>
          <p className="text-gray-600 text-sm mt-2">
            Tekintse meg az analitikai rendszer teljes funkcionalitását
          </p>
        </div>
      </div>

      {/* Live Analytics Component */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <AnalyticsCharts />
        </div>
      </div>
    </div>
  )
}