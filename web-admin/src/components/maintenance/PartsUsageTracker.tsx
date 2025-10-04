'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Package,
  Search,
  Filter,
  Plus,
  Minus,
  AlertTriangle,
  TrendingDown,
  TrendingUp,
  Eye,
  ShoppingCart,
  Wrench,
  Calendar,
  BarChart3,
  History,
  AlertCircle
} from 'lucide-react'

interface PartUsage {
  id: string
  partId: string
  partName: string
  partNumber: string
  category: 'electronic' | 'mechanical' | 'hydraulic' | 'consumable' | 'safety'
  workOrderId: string
  workOrderTitle: string
  quantity: number
  unitPrice: number
  totalCost: number
  technician: string
  usedAt: Date
  location: string
  objectType: 'gate' | 'building' | 'vehicle'
  objectId: string
  notes?: string
  supplier: string
  warrantyMonths?: number
}

interface PartInventory {
  id: string
  partName: string
  partNumber: string
  category: 'electronic' | 'mechanical' | 'hydraulic' | 'consumable' | 'safety'
  currentStock: number
  minStock: number
  maxStock: number
  unitPrice: number
  supplier: string
  location: string
  lastRestocked: Date
  monthlyUsage: number
  status: 'in-stock' | 'low-stock' | 'out-of-stock' | 'overstocked'
}

// Mock data
const mockPartUsage: PartUsage[] = [
  {
    id: 'PU-001',
    partId: 'PART-101',
    partName: 'Biztonsági szenzor - infrared',
    partNumber: 'SNS-IR-001',
    category: 'safety',
    workOrderId: 'WO-001',
    workOrderTitle: 'Garázs kapu szenzor javítás',
    quantity: 2,
    unitPrice: 15000,
    totalCost: 30000,
    technician: 'Nagy Péter',
    usedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    location: 'Budapest, Garázs A/1',
    objectType: 'gate',
    objectId: 'GATE-123',
    notes: 'Alsó és felső szenzor cseréje biztonsági okokból',
    supplier: 'TechSafe Kft.',
    warrantyMonths: 24
  },
  {
    id: 'PU-002',
    partId: 'PART-205',
    partName: 'Kapu motor kenőanyag',
    partNumber: 'LUB-MT-205',
    category: 'consumable',
    workOrderId: 'WO-003',
    workOrderTitle: 'Heti karbantartás - A épület',
    quantity: 1,
    unitPrice: 8500,
    totalCost: 8500,
    technician: 'Szabó Anna',
    usedAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    location: 'Budapest, A épület',
    objectType: 'building',
    objectId: 'BLDG-A',
    supplier: 'MotoLub Zrt.',
    warrantyMonths: 6
  },
  {
    id: 'PU-003',
    partId: 'PART-150',
    partName: 'LED panel 40W',
    partNumber: 'LED-40W-150',
    category: 'electronic',
    workOrderId: 'WO-004',
    workOrderTitle: 'LED panel csere',
    quantity: 4,
    unitPrice: 3200,
    totalCost: 12800,
    technician: 'Varga Béla',
    usedAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    location: 'Budapest, Lépcsőház C',
    objectType: 'building',
    objectId: 'BLDG-001',
    notes: '4 db LED panel csere égő miatt',
    supplier: 'LightTech Bt.',
    warrantyMonths: 36
  },
  {
    id: 'PU-004',
    partId: 'PART-301',
    partName: 'Távvezérlő elem',
    partNumber: 'BAT-CR2032',
    category: 'consumable',
    workOrderId: 'WO-002',
    workOrderTitle: 'Távvezérlő szinkronizáció',
    quantity: 2,
    unitPrice: 500,
    totalCost: 1000,
    technician: 'Kiss József',
    usedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    location: 'Budapest, Garázs B/4',
    objectType: 'gate',
    objectId: 'GATE-401',
    supplier: 'BatteryShop Kft.'
  },
  {
    id: 'PU-005',
    partId: 'PART-402',
    partName: 'Kapu lánckerék',
    partNumber: 'SPR-CG-402',
    category: 'mechanical',
    workOrderId: 'WO-005',
    workOrderTitle: 'Kapu láncmechanika javítás',
    quantity: 1,
    unitPrice: 25000,
    totalCost: 25000,
    technician: 'Nagy Péter',
    usedAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
    location: 'Budapest, Garázs D/3',
    objectType: 'gate',
    objectId: 'GATE-340',
    notes: 'Kopott lánckerék cseréje',
    supplier: 'MechParts Kft.',
    warrantyMonths: 12
  }
]

const mockInventory: PartInventory[] = [
  {
    id: 'INV-101',
    partName: 'Biztonsági szenzor - infrared',
    partNumber: 'SNS-IR-001',
    category: 'safety',
    currentStock: 8,
    minStock: 5,
    maxStock: 20,
    unitPrice: 15000,
    supplier: 'TechSafe Kft.',
    location: 'Raktár A/1',
    lastRestocked: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000),
    monthlyUsage: 3,
    status: 'in-stock'
  },
  {
    id: 'INV-205',
    partName: 'Kapu motor kenőanyag',
    partNumber: 'LUB-MT-205',
    category: 'consumable',
    currentStock: 2,
    minStock: 3,
    maxStock: 12,
    unitPrice: 8500,
    supplier: 'MotoLub Zrt.',
    location: 'Raktár A/2',
    lastRestocked: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
    monthlyUsage: 4,
    status: 'low-stock'
  },
  {
    id: 'INV-150',
    partName: 'LED panel 40W',
    partNumber: 'LED-40W-150',
    category: 'electronic',
    currentStock: 0,
    minStock: 2,
    maxStock: 15,
    unitPrice: 3200,
    supplier: 'LightTech Bt.',
    location: 'Raktár B/1',
    lastRestocked: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000),
    monthlyUsage: 6,
    status: 'out-of-stock'
  },
  {
    id: 'INV-301',
    partName: 'Távvezérlő elem',
    partNumber: 'BAT-CR2032',
    category: 'consumable',
    currentStock: 50,
    minStock: 10,
    maxStock: 30,
    unitPrice: 500,
    supplier: 'BatteryShop Kft.',
    location: 'Raktár A/3',
    lastRestocked: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    monthlyUsage: 8,
    status: 'overstocked'
  },
  {
    id: 'INV-402',
    partName: 'Kapu lánckerék',
    partNumber: 'SPR-CG-402',
    category: 'mechanical',
    currentStock: 3,
    minStock: 2,
    maxStock: 8,
    unitPrice: 25000,
    supplier: 'MechParts Kft.',
    location: 'Raktár B/2',
    lastRestocked: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    monthlyUsage: 1,
    status: 'in-stock'
  }
]

export function PartsUsageTracker() {
  const [partUsages, setPartUsages] = useState<PartUsage[]>(mockPartUsage)
  const [inventory, setInventory] = useState<PartInventory[]>(mockInventory)
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState<string>('all')
  const [timeFilter, setTimeFilter] = useState<string>('all')
  const [selectedUsage, setSelectedUsage] = useState<PartUsage | null>(null)
  const [activeTab, setActiveTab] = useState<'usage' | 'inventory'>('usage')

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'safety':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'electronic':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'mechanical':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'hydraulic':
        return 'bg-cyan-100 text-cyan-800 border-cyan-200'
      case 'consumable':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStockStatusColor = (status: string) => {
    switch (status) {
      case 'in-stock':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'low-stock':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'out-of-stock':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'overstocked':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStockStatusIcon = (status: string) => {
    switch (status) {
      case 'in-stock':
        return <Package className="w-4 h-4" />
      case 'low-stock':
        return <TrendingDown className="w-4 h-4" />
      case 'out-of-stock':
        return <AlertTriangle className="w-4 h-4" />
      case 'overstocked':
        return <TrendingUp className="w-4 h-4" />
      default:
        return <Package className="w-4 h-4" />
    }
  }

  const filteredUsages = partUsages.filter(usage => {
    const matchesSearch = !searchQuery || 
      usage.partName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      usage.partNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      usage.workOrderTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
      usage.technician.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = categoryFilter === 'all' || usage.category === categoryFilter
    
    let matchesTime = true
    if (timeFilter === 'today') {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      matchesTime = usage.usedAt >= today
    } else if (timeFilter === 'week') {
      const weekAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)
      matchesTime = usage.usedAt >= weekAgo
    } else if (timeFilter === 'month') {
      const monthAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
      matchesTime = usage.usedAt >= monthAgo
    }
    
    return matchesSearch && matchesCategory && matchesTime
  })

  const filteredInventory = inventory.filter(item => {
    const matchesSearch = !searchQuery || 
      item.partName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.partNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.supplier.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = categoryFilter === 'all' || item.category === categoryFilter
    
    return matchesSearch && matchesCategory
  })

  const calculateTotalCost = () => {
    return filteredUsages.reduce((sum, usage) => sum + usage.totalCost, 0)
  }

  const getUsageStats = () => {
    const totalUsages = filteredUsages.length
    const totalCost = calculateTotalCost()
    const avgCost = totalUsages > 0 ? totalCost / totalUsages : 0
    
    const categoryStats = filteredUsages.reduce((stats, usage) => {
      stats[usage.category] = (stats[usage.category] || 0) + 1
      return stats
    }, {} as Record<string, number>)
    
    return { totalUsages, totalCost, avgCost, categoryStats }
  }

  const getInventoryStats = () => {
    const totalItems = inventory.length
    const lowStockItems = inventory.filter(item => item.status === 'low-stock' || item.status === 'out-of-stock').length
    const totalValue = inventory.reduce((sum, item) => sum + (item.currentStock * item.unitPrice), 0)
    
    return { totalItems, lowStockItems, totalValue }
  }

  const stats = getUsageStats()
  const inventoryStats = getInventoryStats()

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alkatrész Felhasználás</h1>
          <p className="text-gray-600 mt-2">
            Alkatrész felhasználás követése és készlet kezelés
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex rounded-lg border bg-gray-50 p-1">
            <Button
              variant={activeTab === 'usage' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('usage')}
              className="gap-2"
            >
              <History className="w-4 h-4" />
              Felhasználás
            </Button>
            <Button
              variant={activeTab === 'inventory' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setActiveTab('inventory')}
              className="gap-2"
            >
              <Package className="w-4 h-4" />
              Készlet
            </Button>
          </div>
          
          <Button className="gap-2">
            <Plus className="w-4 h-4" />
            Felhasználás rögzítése
          </Button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid md:grid-cols-4 gap-4">
        {activeTab === 'usage' ? (
          <>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Package className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Összes felhasználás</p>
                    <p className="text-2xl font-bold">{stats.totalUsages}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <BarChart3 className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Összes költség</p>
                    <p className="text-2xl font-bold">{stats.totalCost.toLocaleString()} Ft</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Átlag felhasználás</p>
                    <p className="text-2xl font-bold">{Math.round(stats.avgCost).toLocaleString()} Ft</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <Wrench className="w-5 h-5 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Aktív munkák</p>
                    <p className="text-2xl font-bold">{new Set(partUsages.map(u => u.workOrderId)).size}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <>
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Package className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Összes tétel</p>
                    <p className="text-2xl font-bold">{inventoryStats.totalItems}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-red-100 rounded-lg">
                    <AlertTriangle className="w-5 h-5 text-red-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Alacsony készlet</p>
                    <p className="text-2xl font-bold text-red-600">{inventoryStats.lowStockItems}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <BarChart3 className="w-5 h-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Készlet érték</p>
                    <p className="text-2xl font-bold">{inventoryStats.totalValue.toLocaleString()} Ft</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <Calendar className="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Rendelés szükséges</p>
                    <p className="text-2xl font-bold">{inventory.filter(i => i.status === 'out-of-stock').length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Szűrés és keresés
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Keresés..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Kategória" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Minden kategória</SelectItem>
                <SelectItem value="safety">Biztonsági</SelectItem>
                <SelectItem value="electronic">Elektronikai</SelectItem>
                <SelectItem value="mechanical">Mechanikai</SelectItem>
                <SelectItem value="hydraulic">Hidraulikai</SelectItem>
                <SelectItem value="consumable">Fogyóeszköz</SelectItem>
              </SelectContent>
            </Select>
            
            {activeTab === 'usage' && (
              <Select value={timeFilter} onValueChange={setTimeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Időszak" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Minden idő</SelectItem>
                  <SelectItem value="today">Ma</SelectItem>
                  <SelectItem value="week">Elmúlt hét</SelectItem>
                  <SelectItem value="month">Elmúlt hónap</SelectItem>
                </SelectContent>
              </Select>
            )}
            
            <Button variant="outline" onClick={() => {
              setSearchQuery('')
              setCategoryFilter('all')
              setTimeFilter('all')
            }}>
              Szűrők törlése
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Data Tables */}
      <Card>
        <CardHeader>
          <CardTitle>
            {activeTab === 'usage' 
              ? `Alkatrész felhasználások (${filteredUsages.length})`
              : `Készlet áttekintés (${filteredInventory.length})`
            }
          </CardTitle>
        </CardHeader>
        <CardContent>
          {activeTab === 'usage' ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Alkatrész</TableHead>
                    <TableHead>Kategória</TableHead>
                    <TableHead>Munkalap</TableHead>
                    <TableHead>Mennyiség</TableHead>
                    <TableHead>Egységár</TableHead>
                    <TableHead>Összesen</TableHead>
                    <TableHead>Technikus</TableHead>
                    <TableHead>Dátum</TableHead>
                    <TableHead>Műveletek</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredUsages.map((usage) => (
                    <TableRow key={usage.id} className="hover:bg-gray-50">
                      <TableCell>
                        <div>
                          <p className="font-medium">{usage.partName}</p>
                          <p className="text-sm text-gray-500">{usage.partNumber}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getCategoryColor(usage.category)}>
                          {usage.category === 'safety' && 'Biztonsági'}
                          {usage.category === 'electronic' && 'Elektronikai'}
                          {usage.category === 'mechanical' && 'Mechanikai'}
                          {usage.category === 'hydraulic' && 'Hidraulikai'}
                          {usage.category === 'consumable' && 'Fogyóeszköz'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{usage.workOrderId}</p>
                          <p className="text-sm text-gray-500 line-clamp-1">{usage.workOrderTitle}</p>
                        </div>
                      </TableCell>
                      <TableCell>{usage.quantity} db</TableCell>
                      <TableCell>{usage.unitPrice.toLocaleString()} Ft</TableCell>
                      <TableCell className="font-medium">{usage.totalCost.toLocaleString()} Ft</TableCell>
                      <TableCell>{usage.technician}</TableCell>
                      <TableCell>{usage.usedAt.toLocaleDateString('hu-HU')}</TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedUsage(usage)}
                        >
                          <Eye className="w-4 h-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {filteredUsages.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Nincs találat a megadott szűrési feltételek alapján.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Alkatrész</TableHead>
                    <TableHead>Kategória</TableHead>
                    <TableHead>Készlet</TableHead>
                    <TableHead>Státusz</TableHead>
                    <TableHead>Egységár</TableHead>
                    <TableHead>Érték</TableHead>
                    <TableHead>Beszállító</TableHead>
                    <TableHead>Havi felhasználás</TableHead>
                    <TableHead>Műveletek</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredInventory.map((item) => (
                    <TableRow key={item.id} className="hover:bg-gray-50">
                      <TableCell>
                        <div>
                          <p className="font-medium">{item.partName}</p>
                          <p className="text-sm text-gray-500">{item.partNumber}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={getCategoryColor(item.category)}>
                          {item.category === 'safety' && 'Biztonsági'}
                          {item.category === 'electronic' && 'Elektronikai'}
                          {item.category === 'mechanical' && 'Mechanikai'}
                          {item.category === 'hydraulic' && 'Hidraulikai'}
                          {item.category === 'consumable' && 'Fogyóeszköz'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <span>{item.currentStock}/{item.maxStock}</span>
                          <div className="w-16 bg-gray-200 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${
                                item.currentStock <= item.minStock ? 'bg-red-400' : 
                                item.currentStock > item.maxStock * 0.8 ? 'bg-blue-400' : 
                                'bg-green-400'
                              }`}
                              style={{ width: `${(item.currentStock / item.maxStock) * 100}%` }}
                            />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={`${getStockStatusColor(item.status)} gap-1`}>
                          {getStockStatusIcon(item.status)}
                          {item.status === 'in-stock' && 'Készleten'}
                          {item.status === 'low-stock' && 'Alacsony'}
                          {item.status === 'out-of-stock' && 'Nincs készlet'}
                          {item.status === 'overstocked' && 'Túlkészletezett'}
                        </Badge>
                      </TableCell>
                      <TableCell>{item.unitPrice.toLocaleString()} Ft</TableCell>
                      <TableCell className="font-medium">
                        {(item.currentStock * item.unitPrice).toLocaleString()} Ft
                      </TableCell>
                      <TableCell>{item.supplier}</TableCell>
                      <TableCell>{item.monthlyUsage} db</TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Plus className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <ShoppingCart className="w-4 h-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              
              {filteredInventory.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Package className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Nincs találat a megadott szűrési feltételek alapján.</p>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Usage Details Dialog */}
      {selectedUsage && (
        <Dialog open={!!selectedUsage} onOpenChange={() => setSelectedUsage(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Felhasználás részletei</DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm font-medium text-gray-500">Alkatrész</Label>
                  <p className="font-medium">{selectedUsage.partName}</p>
                  <p className="text-sm text-gray-500">{selectedUsage.partNumber}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Kategória</Label>
                  <Badge className={getCategoryColor(selectedUsage.category)}>
                    {selectedUsage.category}
                  </Badge>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Munkalap</Label>
                  <p className="font-medium">{selectedUsage.workOrderId}</p>
                  <p className="text-sm text-gray-500">{selectedUsage.workOrderTitle}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Objektum</Label>
                  <p>{selectedUsage.objectType}: {selectedUsage.objectId}</p>
                  <p className="text-sm text-gray-500">{selectedUsage.location}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Mennyiség</Label>
                  <p className="font-medium">{selectedUsage.quantity} db</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Költség</Label>
                  <p className="font-medium">{selectedUsage.totalCost.toLocaleString()} Ft</p>
                  <p className="text-sm text-gray-500">({selectedUsage.unitPrice.toLocaleString()} Ft/db)</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Technikus</Label>
                  <p>{selectedUsage.technician}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Felhasználva</Label>
                  <p>{selectedUsage.usedAt.toLocaleString('hu-HU')}</p>
                </div>
                
                <div>
                  <Label className="text-sm font-medium text-gray-500">Beszállító</Label>
                  <p>{selectedUsage.supplier}</p>
                </div>
                
                {selectedUsage.warrantyMonths && (
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Garancia</Label>
                    <p>{selectedUsage.warrantyMonths} hónap</p>
                  </div>
                )}
              </div>
              
              {selectedUsage.notes && (
                <div>
                  <Label className="text-sm font-medium text-gray-500">Megjegyzések</Label>
                  <p className="text-gray-700">{selectedUsage.notes}</p>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}