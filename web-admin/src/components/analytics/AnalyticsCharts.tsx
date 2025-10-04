'use client'

import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts'
import * as XLSX from 'xlsx'
import { CSVLink } from 'react-csv'
import {
  Download,
  Filter,
  Calendar,
  Building,
  AlertTriangle,
  CheckCircle2,
  Clock,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart as PieChartIcon,
  FileSpreadsheet,
  FileText,
  RefreshCw,
  Settings,
  Eye,
  Search
} from 'lucide-react'
import { format, subDays, subMonths, startOfMonth, endOfMonth, isWithinInterval } from 'date-fns'

// Types
interface ChartData {
  date: string
  value: number
  label: string
  category?: string
  status?: string
  site?: string
}

interface FilterState {
  dateRange: 'week' | 'month' | 'quarter' | 'year' | 'custom'
  startDate: string
  endDate: string
  site: string
  status: string
  category: string
}

interface ExpiringInspection {
  id: string
  name: string
  site: string
  dueDate: Date
  daysLeft: number
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'pending' | 'scheduled' | 'overdue'
  inspector: string
  type: 'safety' | 'maintenance' | 'compliance' | 'quality'
}

interface SLAData {
  period: string
  target: number
  achieved: number
  total: number
  percentage: number
  site: string
  category: string
}

interface ErrorStatistic {
  category: string
  count: number
  percentage: number
  trend: 'up' | 'down' | 'stable'
  severity: 'low' | 'medium' | 'high' | 'critical'
  site: string
  date: string
}

// Mock data generators
const generateExpiringInspections = (): ExpiringInspection[] => [
  {
    id: 'INS-001',
    name: 'Garázs A biztonsági ellenőrzés',
    site: 'Budapest Garázs A',
    dueDate: new Date(2025, 9, 8),
    daysLeft: 4,
    priority: 'high',
    status: 'scheduled',
    inspector: 'Nagy Péter',
    type: 'safety'
  },
  {
    id: 'INS-002', 
    name: 'Lépcsőházi világítás teszt',
    site: 'Budapest Garázs B',
    dueDate: new Date(2025, 9, 6),
    daysLeft: 2,
    priority: 'medium',
    status: 'pending',
    inspector: 'Szabó Anna',
    type: 'maintenance'
  },
  {
    id: 'INS-003',
    name: 'Tűzvédelmi rendszer auditálás',
    site: 'Debrecen Garázs C',
    dueDate: new Date(2025, 9, 5),
    daysLeft: 1,
    priority: 'critical',
    status: 'overdue',
    inspector: 'Kiss József',
    type: 'compliance'
  },
  {
    id: 'INS-004',
    name: 'Kamera rendszer ellenőrzés',
    site: 'Budapest Garázs A',
    dueDate: new Date(2025, 9, 12),
    daysLeft: 8,
    priority: 'low',
    status: 'scheduled',
    inspector: 'Varga Béla',
    type: 'quality'
  },
  {
    id: 'INS-005',
    name: 'Kapu motor diagnosztika',
    site: 'Szeged Garázs D',
    dueDate: new Date(2025, 9, 3),
    daysLeft: -1,
    priority: 'high',
    status: 'overdue',
    inspector: 'Kovács János',
    type: 'maintenance'
  }
]

const generateSLAData = (): SLAData[] => {
  const sites = ['Budapest Garázs A', 'Budapest Garázs B', 'Debrecen Garázs C', 'Szeged Garázs D']
  const categories = ['safety', 'maintenance', 'compliance', 'quality']
  const data: SLAData[] = []
  
  for (let i = 0; i < 12; i++) {
    const date = subMonths(new Date(), i)
    sites.forEach(site => {
      categories.forEach(category => {
        const target = 95
        const achieved = 80 + Math.random() * 20
        const total = 50 + Math.floor(Math.random() * 100)
        
        data.push({
          period: format(date, 'yyyy-MM'),
          target,
          achieved,
          total,
          percentage: achieved,
          site,
          category
        })
      })
    })
  }
  
  return data.sort((a, b) => a.period.localeCompare(b.period))
}

const generateErrorStatistics = (): ErrorStatistic[] => {
  const categories = [
    'Kapu meghibásodás', 'Világítási hiba', 'Biztonsági rendszer',
    'Kamera probléma', 'Távvezérlő szinkronizáció', 'Motor túlmelegedés'
  ]
  const sites = ['Budapest Garázs A', 'Budapest Garázs B', 'Debrecen Garázs C', 'Szeged Garázs D']
  const data: ErrorStatistic[] = []
  
  for (let i = 0; i < 30; i++) {
    const date = format(subDays(new Date(), i), 'yyyy-MM-dd')
    categories.forEach(category => {
      sites.forEach(site => {
        const count = Math.floor(Math.random() * 10)
        if (count > 0) {
          data.push({
            category,
            count,
            percentage: Math.random() * 100,
            trend: Math.random() > 0.5 ? 'up' : 'down',
            severity: count > 7 ? 'critical' : count > 5 ? 'high' : count > 2 ? 'medium' : 'low',
            site,
            date
          })
        }
      })
    })
  }
  
  return data
}

export function AnalyticsCharts() {
  const [filters, setFilters] = useState<FilterState>({
    dateRange: 'month',
    startDate: format(subMonths(new Date(), 1), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd'),
    site: 'all',
    status: 'all',
    category: 'all'
  })

  const [expiringInspections] = useState<ExpiringInspection[]>(generateExpiringInspections())
  const [slaData] = useState<SLAData[]>(generateSLAData())
  const [errorStats] = useState<ErrorStatistic[]>(generateErrorStatistics())
  const [refreshing, setRefreshing] = useState(false)

  // Filter data based on current filters
  const filteredData = useMemo(() => {
    const filterByDateRange = (item: any) => {
      if (filters.dateRange === 'custom') {
        const itemDate = new Date(item.date || item.period || item.dueDate)
        return isWithinInterval(itemDate, {
          start: new Date(filters.startDate),
          end: new Date(filters.endDate)
        })
      }
      return true
    }

    const filterBySite = (item: any) => 
      filters.site === 'all' || item.site === filters.site

    const filterByStatus = (item: any) => 
      filters.status === 'all' || item.status === filters.status

    const filterByCategory = (item: any) => 
      filters.category === 'all' || item.category === filters.category || item.type === filters.category

    return {
      inspections: expiringInspections
        .filter(filterByDateRange)
        .filter(filterBySite)
        .filter(filterByStatus)
        .filter(filterByCategory),
      sla: slaData
        .filter(filterByDateRange)
        .filter(filterBySite)
        .filter(filterByCategory),
      errors: errorStats
        .filter(filterByDateRange)
        .filter(filterBySite)
    }
  }, [filters, expiringInspections, slaData, errorStats])

  // Chart data preparation
  const expiringInspectionsChart = useMemo(() => {
    const grouped = filteredData.inspections.reduce((acc, item) => {
      const key = item.daysLeft <= 0 ? 'Lejárt' : 
                  item.daysLeft <= 3 ? '1-3 nap' :
                  item.daysLeft <= 7 ? '4-7 nap' : '1+ hét'
      acc[key] = (acc[key] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return Object.entries(grouped).map(([name, value]) => ({ name, value }))
  }, [filteredData.inspections])

  const slaChart = useMemo(() => {
    return filteredData.sla
      .slice(-12)
      .map(item => ({
        period: format(new Date(item.period), 'MMM yyyy'),
        target: item.target,
        achieved: Math.round(item.achieved),
        total: item.total
      }))
  }, [filteredData.sla])

  const errorChart = useMemo(() => {
    const grouped = filteredData.errors.reduce((acc, item) => {
      const existing = acc.find(x => x.category === item.category)
      if (existing) {
        existing.count += item.count
      } else {
        acc.push({
          category: item.category,
          count: item.count,
          severity: item.severity
        })
      }
      return acc
    }, [] as Array<{category: string, count: number, severity: string}>)

    return grouped.sort((a, b) => b.count - a.count).slice(0, 6)
  }, [filteredData.errors])

  // Export functions
  const exportToCSV = useCallback((data: any[], filename: string) => {
    return {
      data,
      filename: `${filename}-${format(new Date(), 'yyyy-MM-dd')}.csv`,
      headers: Object.keys(data[0] || {}).map(key => ({ label: key, key }))
    }
  }, [])

  const exportToExcel = useCallback((data: any[], filename: string) => {
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Data')
    XLSX.writeFile(wb, `${filename}-${format(new Date(), 'yyyy-MM-dd')}.xlsx`)
  }, [])

  const refreshData = useCallback(async () => {
    setRefreshing(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setRefreshing(false)
  }, [])

  // Color schemes
  const COLORS = {
    primary: ['#3B82F6', '#1D4ED8', '#1E40AF', '#1E3A8A'],
    success: ['#10B981', '#059669', '#047857', '#065F46'],
    warning: ['#F59E0B', '#D97706', '#B45309', '#92400E'],
    danger: ['#EF4444', '#DC2626', '#B91C1C', '#991B1B'],
    mixed: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#F97316']
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analitikai grafikonok és export</h1>
          <p className="text-gray-600 mt-2">
            Recharts alapú vizualizációk szűrőkkel és CSV/XLSX export funkcióval
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            onClick={refreshData}
            disabled={refreshing}
            className="gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            Frissítés
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="w-5 h-5" />
            Szűrők
          </CardTitle>
          <CardDescription>
            Minden grafikonra alkalmazható szűrési opciók
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div>
              <Label className="text-sm font-medium">Időtartam</Label>
              <Select
                value={filters.dateRange}
                onValueChange={(value: any) => 
                  setFilters(prev => ({ ...prev, dateRange: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Elmúlt hét</SelectItem>
                  <SelectItem value="month">Elmúlt hónap</SelectItem>
                  <SelectItem value="quarter">Elmúlt negyedév</SelectItem>
                  <SelectItem value="year">Elmúlt év</SelectItem>
                  <SelectItem value="custom">Egyéni</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {filters.dateRange === 'custom' && (
              <>
                <div>
                  <Label className="text-sm font-medium">Kezdő dátum</Label>
                  <Input
                    type="date"
                    value={filters.startDate}
                    onChange={(e) => 
                      setFilters(prev => ({ ...prev, startDate: e.target.value }))
                    }
                  />
                </div>
                <div>
                  <Label className="text-sm font-medium">Záró dátum</Label>
                  <Input
                    type="date"
                    value={filters.endDate}
                    onChange={(e) => 
                      setFilters(prev => ({ ...prev, endDate: e.target.value }))
                    }
                  />
                </div>
              </>
            )}

            <div>
              <Label className="text-sm font-medium">Telephely</Label>
              <Select
                value={filters.site}
                onValueChange={(value) => 
                  setFilters(prev => ({ ...prev, site: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Minden telephely</SelectItem>
                  <SelectItem value="Budapest Garázs A">Budapest Garázs A</SelectItem>
                  <SelectItem value="Budapest Garázs B">Budapest Garázs B</SelectItem>
                  <SelectItem value="Debrecen Garázs C">Debrecen Garázs C</SelectItem>
                  <SelectItem value="Szeged Garázs D">Szeged Garázs D</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Státusz</Label>
              <Select
                value={filters.status}
                onValueChange={(value) => 
                  setFilters(prev => ({ ...prev, status: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Minden státusz</SelectItem>
                  <SelectItem value="pending">Függőben</SelectItem>
                  <SelectItem value="scheduled">Ütemezett</SelectItem>
                  <SelectItem value="overdue">Lejárt</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Kategória</Label>
              <Select
                value={filters.category}
                onValueChange={(value) => 
                  setFilters(prev => ({ ...prev, category: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Minden kategória</SelectItem>
                  <SelectItem value="safety">Biztonság</SelectItem>
                  <SelectItem value="maintenance">Karbantartás</SelectItem>
                  <SelectItem value="compliance">Megfelelőség</SelectItem>
                  <SelectItem value="quality">Minőség</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Charts Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Expiring Inspections Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-orange-600" />
                  Lejáró ellenőrzések
                </CardTitle>
                <CardDescription>
                  Ellenőrzések lejárat szerinti csoportosítása
                </CardDescription>
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <CSVLink 
                    {...exportToCSV(filteredData.inspections, 'lejaro-ellenorzesek')}
                    className="w-full"
                  >
                    <DropdownMenuItem>
                      <FileText className="w-4 h-4 mr-2" />
                      CSV letöltés
                    </DropdownMenuItem>
                  </CSVLink>
                  <DropdownMenuItem 
                    onClick={() => exportToExcel(filteredData.inspections, 'lejaro-ellenorzesek')}
                  >
                    <FileSpreadsheet className="w-4 h-4 mr-2" />
                    Excel letöltés
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={expiringInspectionsChart}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({name, value}) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {expiringInspectionsChart.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS.mixed[index % COLORS.mixed.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* SLA Performance Chart */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-green-600" />
                  SLA teljesülés
                </CardTitle>
                <CardDescription>
                  Havi SLA teljesítési mutatók cél vs. tényleges
                </CardDescription>
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <CSVLink 
                    {...exportToCSV(filteredData.sla, 'sla-teljesules')}
                    className="w-full"
                  >
                    <DropdownMenuItem>
                      <FileText className="w-4 h-4 mr-2" />
                      CSV letöltés
                    </DropdownMenuItem>
                  </CSVLink>
                  <DropdownMenuItem 
                    onClick={() => exportToExcel(filteredData.sla, 'sla-teljesules')}
                  >
                    <FileSpreadsheet className="w-4 h-4 mr-2" />
                    Excel letöltés
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={slaChart}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="period" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="target" 
                  stroke="#EF4444" 
                  strokeDasharray="5 5"
                  name="Cél (%)"
                />
                <Line 
                  type="monotone" 
                  dataKey="achieved" 
                  stroke="#10B981"
                  strokeWidth={2}
                  name="Teljesített (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Error Statistics Chart */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-600" />
                  Hibastatisztika
                </CardTitle>
                <CardDescription>
                  Hibakategóriák gyakoriság szerint rendezve
                </CardDescription>
              </div>
              
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm">
                    <Download className="w-4 h-4 mr-2" />
                    Export
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <CSVLink 
                    {...exportToCSV(filteredData.errors, 'hibastatisztika')}
                    className="w-full"
                  >
                    <DropdownMenuItem>
                      <FileText className="w-4 h-4 mr-2" />
                      CSV letöltés
                    </DropdownMenuItem>
                  </CSVLink>
                  <DropdownMenuItem 
                    onClick={() => exportToExcel(filteredData.errors, 'hibastatisztika')}
                  >
                    <FileSpreadsheet className="w-4 h-4 mr-2" />
                    Excel letöltés
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={errorChart} layout="horizontal">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="category" type="category" width={150} />
                <Tooltip />
                <Legend />
                <Bar 
                  dataKey="count" 
                  fill="#3B82F6"
                  name="Hibák száma"
                  radius={[0, 4, 4, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Summary Statistics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600">
              {filteredData.inspections.filter(i => i.status === 'overdue').length}
            </div>
            <div className="text-sm text-gray-600">Lejárt ellenőrzések</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">
              {filteredData.inspections.filter(i => i.daysLeft <= 3 && i.daysLeft > 0).length}
            </div>
            <div className="text-sm text-gray-600">3 napon belül lejár</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {Math.round(filteredData.sla.reduce((sum, item) => sum + item.achieved, 0) / Math.max(filteredData.sla.length, 1))}%
            </div>
            <div className="text-sm text-gray-600">Átlag SLA teljesítés</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {filteredData.errors.reduce((sum, item) => sum + item.count, 0)}
            </div>
            <div className="text-sm text-gray-600">Összes hiba</div>
          </CardContent>
        </Card>
      </div>

      {/* Data Tables */}
      <Tabs defaultValue="inspections" className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="inspections">Lejáró ellenőrzések</TabsTrigger>
          <TabsTrigger value="sla">SLA adatok</TabsTrigger>
          <TabsTrigger value="errors">Hibák</TabsTrigger>
        </TabsList>
        
        <TabsContent value="inspections" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Lejáró ellenőrzések részletei</CardTitle>
              <CardDescription>
                Szűrt ellenőrzések listája ({filteredData.inspections.length} elem)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Azonosító</th>
                      <th className="text-left p-2">Név</th>
                      <th className="text-left p-2">Telephely</th>
                      <th className="text-left p-2">Lejárat</th>
                      <th className="text-left p-2">Hátralevő idő</th>
                      <th className="text-left p-2">Prioritás</th>
                      <th className="text-left p-2">Státusz</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.inspections.slice(0, 10).map(item => (
                      <tr key={item.id} className="border-b">
                        <td className="p-2 font-medium">{item.id}</td>
                        <td className="p-2">{item.name}</td>
                        <td className="p-2">{item.site}</td>
                        <td className="p-2">{format(item.dueDate, 'yyyy.MM.dd')}</td>
                        <td className="p-2">
                          <Badge variant={item.daysLeft < 0 ? 'destructive' : item.daysLeft <= 3 ? 'secondary' : 'outline'}>
                            {item.daysLeft < 0 ? `${Math.abs(item.daysLeft)} napja lejárt` : `${item.daysLeft} nap`}
                          </Badge>
                        </td>
                        <td className="p-2">
                          <Badge variant={item.priority === 'critical' ? 'destructive' : item.priority === 'high' ? 'secondary' : 'outline'}>
                            {item.priority === 'critical' && 'Kritikus'}
                            {item.priority === 'high' && 'Magas'}
                            {item.priority === 'medium' && 'Közepes'}
                            {item.priority === 'low' && 'Alacsony'}
                          </Badge>
                        </td>
                        <td className="p-2">
                          <Badge variant={item.status === 'overdue' ? 'destructive' : 'outline'}>
                            {item.status === 'pending' && 'Függőben'}
                            {item.status === 'scheduled' && 'Ütemezett'}
                            {item.status === 'overdue' && 'Lejárt'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="sla" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>SLA teljesítési adatok</CardTitle>
              <CardDescription>
                Havi SLA teljesítési statisztikák ({filteredData.sla.length} rekord)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Időszak</th>
                      <th className="text-left p-2">Telephely</th>
                      <th className="text-left p-2">Kategória</th>
                      <th className="text-left p-2">Cél (%)</th>
                      <th className="text-left p-2">Teljesített (%)</th>
                      <th className="text-left p-2">Összes</th>
                      <th className="text-left p-2">Eltérés</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.sla.slice(0, 10).map((item, index) => (
                      <tr key={index} className="border-b">
                        <td className="p-2 font-medium">{item.period}</td>
                        <td className="p-2">{item.site}</td>
                        <td className="p-2">{item.category}</td>
                        <td className="p-2">{item.target}%</td>
                        <td className="p-2">
                          <Badge variant={item.achieved >= item.target ? 'default' : 'destructive'}>
                            {Math.round(item.achieved)}%
                          </Badge>
                        </td>
                        <td className="p-2">{item.total}</td>
                        <td className="p-2">
                          <span className={item.achieved >= item.target ? 'text-green-600' : 'text-red-600'}>
                            {item.achieved >= item.target ? '+' : ''}{Math.round(item.achieved - item.target)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="errors" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Hibastatisztika részletei</CardTitle>
              <CardDescription>
                Hiba kategóriák és előfordulásaik ({filteredData.errors.length} rekord)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Kategória</th>
                      <th className="text-left p-2">Telephely</th>
                      <th className="text-left p-2">Dátum</th>
                      <th className="text-left p-2">Darabszám</th>
                      <th className="text-left p-2">Súlyosság</th>
                      <th className="text-left p-2">Trend</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.errors.slice(0, 10).map((item, index) => (
                      <tr key={index} className="border-b">
                        <td className="p-2 font-medium">{item.category}</td>
                        <td className="p-2">{item.site}</td>
                        <td className="p-2">{format(new Date(item.date), 'yyyy.MM.dd')}</td>
                        <td className="p-2">{item.count}</td>
                        <td className="p-2">
                          <Badge variant={
                            item.severity === 'critical' ? 'destructive' : 
                            item.severity === 'high' ? 'secondary' : 'outline'
                          }>
                            {item.severity === 'critical' && 'Kritikus'}
                            {item.severity === 'high' && 'Magas'}
                            {item.severity === 'medium' && 'Közepes'}
                            {item.severity === 'low' && 'Alacsony'}
                          </Badge>
                        </td>
                        <td className="p-2">
                          {item.trend === 'up' ? <TrendingUp className="w-4 h-4 text-red-500" /> :
                           item.trend === 'down' ? <TrendingDown className="w-4 h-4 text-green-500" /> :
                           <span className="text-gray-400">→</span>}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}