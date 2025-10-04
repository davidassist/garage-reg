'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  FileText,
  Package,
  Wrench,
  BarChart3,
  TrendingUp,
  Eye,
  Plus,
  Bell,
  Activity,
  History,
  Settings
} from 'lucide-react'

import { MaintenanceTicketList } from '@/components/maintenance/MaintenanceTicketList'
import { WorkOrderKanban } from '@/components/maintenance/WorkOrderKanban'
import { PartsUsageTracker } from '@/components/maintenance/PartsUsageTracker'

interface MaintenanceStats {
  openTickets: number
  inProgressWork: number
  slaBreaches: number
  completedToday: number
  totalCost: number
  partsUsed: number
  lowStockItems: number
  avgResolutionTime: number
}

// Mock data for demonstration
const mockStats: MaintenanceStats = {
  openTickets: 12,
  inProgressWork: 8,
  slaBreaches: 3,
  completedToday: 5,
  totalCost: 245000,
  partsUsed: 15,
  lowStockItems: 4,
  avgResolutionTime: 4.2
}

export default function MaintenanceLifecyclePage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [stats] = useState<MaintenanceStats>(mockStats)

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <div className="flex items-center justify-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-br from-green-500 to-blue-600 rounded-xl">
            <Settings className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-green-600 to-blue-600 bg-clip-text text-transparent">
            Karbantartási Lifecycle Rendszer
          </h1>
        </div>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Teljes karbantartási lifecycle kezelés SLA vizualizációval, Kanban workflow-val és alkatrész felhasználás követéssel
        </p>
        
        {/* Quick Stats */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
          <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
            <CardContent className="p-4 text-center">
              <AlertTriangle className="w-6 h-6 text-red-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-red-900">{stats.slaBreaches}</div>
              <div className="text-xs text-red-700">SLA túllépés</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardContent className="p-4 text-center">
              <Activity className="w-6 h-6 text-blue-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-blue-900">{stats.inProgressWork}</div>
              <div className="text-xs text-blue-700">Aktív munka</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardContent className="p-4 text-center">
              <CheckCircle2 className="w-6 h-6 text-green-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-green-900">{stats.completedToday}</div>
              <div className="text-xs text-green-700">Ma befejezve</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardContent className="p-4 text-center">
              <Package className="w-6 h-6 text-purple-600 mx-auto mb-2" />
              <div className="text-lg font-bold text-purple-900">{stats.partsUsed}</div>
              <div className="text-xs text-purple-700">Felhasznált alkatrész</div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Main Tabs */}
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
            value="tickets" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm flex flex-col gap-1 p-3"
          >
            <FileText className="w-4 h-4" />
            <span className="text-xs">Hibajegyek</span>
          </TabsTrigger>
          <TabsTrigger 
            value="kanban" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm flex flex-col gap-1 p-3"
          >
            <Activity className="w-4 h-4" />
            <span className="text-xs">Kanban Workflow</span>
          </TabsTrigger>
          <TabsTrigger 
            value="parts" 
            className="data-[state=active]:bg-white data-[state=active]:shadow-sm flex flex-col gap-1 p-3"
          >
            <Package className="w-4 h-4" />
            <span className="text-xs">Alkatrészek</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6 space-y-6">
          <div className="grid lg:grid-cols-3 gap-6">
            {/* SLA Dashboard */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  SLA Teljesítés
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Kritikus (2h)</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-red-200 rounded-full h-2">
                        <div className="bg-red-600 h-2 rounded-full" style={{width: '75%'}} />
                      </div>
                      <span className="text-sm text-red-600">75%</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Magas (8h)</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-orange-200 rounded-full h-2">
                        <div className="bg-orange-600 h-2 rounded-full" style={{width: '60%'}} />
                      </div>
                      <span className="text-sm text-orange-600">60%</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Közepes (24h)</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-yellow-200 rounded-full h-2">
                        <div className="bg-yellow-600 h-2 rounded-full" style={{width: '40%'}} />
                      </div>
                      <span className="text-sm text-yellow-600">40%</span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Alacsony (72h)</span>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-green-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{width: '20%'}} />
                      </div>
                      <span className="text-sm text-green-600">20%</span>
                    </div>
                  </div>
                </div>
                
                <div className="pt-3 border-t">
                  <div className="flex items-center gap-2 text-red-600">
                    <Bell className="w-4 h-4" />
                    <span className="text-sm font-medium">{stats.slaBreaches} SLA túllépés</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Azonnali beavatkozás szükséges
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Workflow Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Workflow Állapot
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="text-center p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-bold text-blue-600">{stats.openTickets}</div>
                    <div className="text-xs text-blue-600">Nyitott jegy</div>
                  </div>
                  
                  <div className="text-center p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-bold text-purple-600">{stats.inProgressWork}</div>
                    <div className="text-xs text-purple-600">Folyamatban</div>
                  </div>
                  
                  <div className="text-center p-3 bg-green-50 rounded-lg">
                    <div className="text-xl font-bold text-green-600">{stats.completedToday}</div>
                    <div className="text-xs text-green-600">Ma kész</div>
                  </div>
                  
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-xl font-bold text-gray-600">{stats.avgResolutionTime}h</div>
                    <div className="text-xs text-gray-600">Átlag idő</div>
                  </div>
                </div>
                
                <div className="pt-3 border-t">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Teljesítmény trend:</span>
                      <span className="text-green-600 flex items-center gap-1">
                        <TrendingUp className="w-3 h-3" />
                        +12%
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">
                      Az elmúlt héthez képest javulás
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Parts & Inventory */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Package className="w-5 h-5" />
                  Alkatrész Helyzet
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Felhasznált ma</span>
                    <span className="font-medium">{stats.partsUsed} db</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Költség ma</span>
                    <span className="font-medium">{stats.totalCost.toLocaleString()} Ft</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-red-600">Alacsony készlet</span>
                    <Badge variant="destructive">{stats.lowStockItems} tétel</Badge>
                  </div>
                </div>
                
                <div className="pt-3 border-t space-y-2">
                  <h4 className="text-sm font-medium">Kritikus tételek:</h4>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span>LED panel 40W</span>
                      <span className="text-red-600">0 db</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Motor kenőanyag</span>
                      <span className="text-orange-600">2 db</span>
                    </div>
                  </div>
                  
                  <Button size="sm" variant="outline" className="w-full mt-2">
                    Rendelés szükséges
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="w-5 h-5" />
                Legutóbbi aktivitás
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                  <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">SLA túllépés - MAINT-003</p>
                    <p className="text-xs text-gray-600">Távvezérlő szinkronizáció hiba - 30 perc túllépés</p>
                    <p className="text-xs text-gray-500">5 perce</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
                  <CheckCircle2 className="w-5 h-5 text-green-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Munkalap befejezve - WO-004</p>
                    <p className="text-xs text-gray-600">LED panel csere sikeresen befejezve</p>
                    <p className="text-xs text-gray-500">15 perce</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                  <Package className="w-5 h-5 text-blue-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Alkatrész felhasználás</p>
                    <p className="text-xs text-gray-600">2x Biztonsági szenzor használva - GATE-123</p>
                    <p className="text-xs text-gray-500">25 perce</p>
                  </div>
                </div>
                
                <div className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg">
                  <Bell className="w-5 h-5 text-orange-500 mt-0.5" />
                  <div className="flex-1">
                    <p className="text-sm font-medium">Készlet figyelmeztetés</p>
                    <p className="text-xs text-gray-600">Motor kenőanyag alacsony készlet (2 db maradt)</p>
                    <p className="text-xs text-gray-500">1 órája</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Gyors műveletek</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4">
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col gap-2"
                  onClick={() => setActiveTab('tickets')}
                >
                  <FileText className="w-6 h-6" />
                  <span>Hibajegyek</span>
                  <span className="text-xs text-gray-500">Lista és SLA státusz</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col gap-2"
                  onClick={() => setActiveTab('kanban')}
                >
                  <Activity className="w-6 h-6" />
                  <span>Kanban</span>
                  <span className="text-xs text-gray-500">Drag & drop workflow</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col gap-2"
                  onClick={() => setActiveTab('parts')}
                >
                  <Package className="w-6 h-6" />
                  <span>Alkatrészek</span>
                  <span className="text-xs text-gray-500">Készlet és felhasználás</span>
                </Button>
                
                <Button 
                  variant="outline" 
                  className="h-auto p-4 flex flex-col gap-2"
                >
                  <Plus className="w-6 h-6" />
                  <span>Új hibajegy</span>
                  <span className="text-xs text-gray-500">Probléma bejelentése</span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tickets Tab */}
        <TabsContent value="tickets" className="mt-6">
          <MaintenanceTicketList />
        </TabsContent>

        {/* Kanban Tab */}
        <TabsContent value="kanban" className="mt-6">
          <WorkOrderKanban />
        </TabsContent>

        {/* Parts Tab */}
        <TabsContent value="parts" className="mt-6">
          <PartsUsageTracker />
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <Card className="bg-gradient-to-r from-gray-50 to-gray-100 border-gray-200">
        <CardContent className="p-6">
          <div className="text-center space-y-2">
            <h3 className="font-semibold text-lg">🔧 Karbantartási Lifecycle Rendszer</h3>
            <p className="text-gray-600">
              Komplett karbantartási folyamat kezelés SLA monitorozással, auditált workflow-val és készletkezeléssel.
            </p>
            <div className="flex items-center justify-center gap-4 mt-4">
              <Badge variant="outline" className="gap-1">
                <Clock className="w-3 h-3" />
                SLA Vizualizáció
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Activity className="w-3 h-3" />
                Drag & Drop Kanban
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Package className="w-3 h-3" />
                Alkatrész Tracking
              </Badge>
              <Badge variant="outline" className="gap-1">
                <Bell className="w-3 h-3" />
                Proaktív Riasztások
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}