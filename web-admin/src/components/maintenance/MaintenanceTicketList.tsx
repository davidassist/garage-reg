'use client'

import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AlertTriangle,
  Clock,
  CheckCircle2,
  XCircle,
  User,
  Calendar,
  FileText,
  Bell,
  AlertCircle,
  Wrench,
  Eye,
  Plus,
  Filter,
  Search,
  Timer,
  Activity
} from 'lucide-react'

interface MaintenanceTicket {
  id: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'open' | 'in-progress' | 'pending' | 'resolved' | 'closed'
  category: 'preventive' | 'corrective' | 'emergency' | 'inspection'
  assignee?: string
  reporter: string
  createdAt: Date
  updatedAt: Date
  dueDate: Date
  slaBreachAt: Date
  estimatedHours: number
  actualHours?: number
  objectType: 'gate' | 'building' | 'vehicle'
  objectId: string
  location: string
  tags: string[]
  attachments: string[]
}

interface SLAConfig {
  critical: number // hours
  high: number
  medium: number
  low: number
}

const slaConfig: SLAConfig = {
  critical: 2,  // 2 hours
  high: 8,      // 8 hours  
  medium: 24,   // 1 day
  low: 72       // 3 days
}

// Mock data
const mockTickets: MaintenanceTicket[] = [
  {
    id: 'MAINT-001',
    title: 'Garázs kapu szenzor meghibásodás',
    description: 'Az alsó biztonsági szenzor nem érzékeli megfelelően az akadályokat. Sürgős javítás szükséges.',
    priority: 'high',
    status: 'open',
    category: 'corrective',
    reporter: 'Kovács János',
    assignee: 'Nagy Péter',
    createdAt: new Date(Date.now() - 3 * 60 * 60 * 1000), // 3 hours ago
    updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 5 * 60 * 60 * 1000), // 5 hours from now
    slaBreachAt: new Date(Date.now() + 5 * 60 * 60 * 1000),
    estimatedHours: 4,
    objectType: 'gate',
    objectId: 'GATE-123',
    location: 'Budapest, Garázs A/1',
    tags: ['sensor', 'safety', 'urgent'],
    attachments: ['sensor-error.jpg']
  },
  {
    id: 'MAINT-002', 
    title: 'Heti karbantartási ellenőrzés',
    description: 'Rutinszerű heti ellenőrzés és kenőanyag feltöltés minden garázs kapunál.',
    priority: 'medium',
    status: 'in-progress',
    category: 'preventive',
    reporter: 'Rendszer',
    assignee: 'Szabó Anna',
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 20 * 60 * 60 * 1000),
    slaBreachAt: new Date(Date.now() + 20 * 60 * 60 * 1000),
    estimatedHours: 6,
    actualHours: 3,
    objectType: 'gate',
    objectId: 'MULTIPLE',
    location: 'Budapest, Összes garázs',
    tags: ['routine', 'preventive', 'lubrication'],
    attachments: []
  },
  {
    id: 'MAINT-003',
    title: 'Távvezérlő szinkronizáció hiba',
    description: 'A 401-es távvezérlő nem párosodik megfelelően a kapu vezérlőjével.',
    priority: 'critical',
    status: 'pending',
    category: 'emergency',
    reporter: 'Lakó Mária', 
    assignee: 'Kiss József',
    createdAt: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
    updatedAt: new Date(Date.now() - 15 * 60 * 1000),
    dueDate: new Date(Date.now() + 90 * 60 * 1000), // 1.5 hours from now
    slaBreachAt: new Date(Date.now() + 90 * 60 * 1000),
    estimatedHours: 2,
    objectType: 'gate',
    objectId: 'GATE-401',
    location: 'Budapest, Garázs B/4',
    tags: ['remote', 'pairing', 'critical'],
    attachments: ['remote-error.pdf']
  },
  {
    id: 'MAINT-004',
    title: 'Épület világítás karbantartás',
    description: 'A lépcsőházban több LED panel cseréje szükséges.',
    priority: 'low',
    status: 'resolved',
    category: 'corrective',
    reporter: 'Takács Gábor',
    assignee: 'Varga Béla',
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000),
    slaBreachAt: new Date(Date.now() + 67 * 60 * 60 * 1000),
    estimatedHours: 3,
    actualHours: 2.5,
    objectType: 'building',
    objectId: 'BLDG-001',
    location: 'Budapest, Lépcsőház C',
    tags: ['lighting', 'led', 'replacement'],
    attachments: []
  }
]

export function MaintenanceTicketList() {
  const [tickets, setTickets] = useState<MaintenanceTicket[]>(mockTickets)
  const [filteredTickets, setFilteredTickets] = useState<MaintenanceTicket[]>(mockTickets)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [selectedTicket, setSelectedTicket] = useState<MaintenanceTicket | null>(null)
  const [showNewTicketDialog, setShowNewTicketDialog] = useState(false)

  // Filter tickets based on search and filters
  useEffect(() => {
    let filtered = tickets

    if (searchQuery) {
      filtered = filtered.filter(ticket => 
        ticket.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        ticket.objectId.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(ticket => ticket.status === statusFilter)
    }

    if (priorityFilter !== 'all') {
      filtered = filtered.filter(ticket => ticket.priority === priorityFilter)
    }

    setFilteredTickets(filtered)
  }, [tickets, searchQuery, statusFilter, priorityFilter])

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'open':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'in-progress':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'closed':
        return 'bg-gray-100 text-gray-800 border-gray-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'open':
        return <FileText className="w-4 h-4" />
      case 'in-progress':
        return <Activity className="w-4 h-4" />
      case 'pending':
        return <Clock className="w-4 h-4" />
      case 'resolved':
        return <CheckCircle2 className="w-4 h-4" />
      case 'closed':
        return <XCircle className="w-4 h-4" />
      default:
        return <FileText className="w-4 h-4" />
    }
  }

  const getSLAStatus = (ticket: MaintenanceTicket) => {
    const now = new Date()
    const timeToSLA = ticket.slaBreachAt.getTime() - now.getTime()
    const hoursToSLA = timeToSLA / (1000 * 60 * 60)
    
    if (hoursToSLA < 0) {
      return { status: 'breached', color: 'text-red-600', icon: <XCircle className="w-4 h-4" /> }
    } else if (hoursToSLA < 1) {
      return { status: 'critical', color: 'text-red-500', icon: <AlertTriangle className="w-4 h-4" /> }
    } else if (hoursToSLA < 4) {
      return { status: 'warning', color: 'text-orange-500', icon: <Clock className="w-4 h-4" /> }
    } else {
      return { status: 'safe', color: 'text-green-500', icon: <CheckCircle2 className="w-4 h-4" /> }
    }
  }

  const calculateSLAProgress = (ticket: MaintenanceTicket) => {
    const totalSLATime = slaConfig[ticket.priority] * 60 * 60 * 1000 // milliseconds
    const elapsedTime = new Date().getTime() - ticket.createdAt.getTime()
    const progress = Math.min((elapsedTime / totalSLATime) * 100, 100)
    return progress
  }

  const formatTimeRemaining = (ticket: MaintenanceTicket) => {
    const now = new Date()
    const timeToSLA = ticket.slaBreachAt.getTime() - now.getTime()
    const hoursToSLA = Math.floor(timeToSLA / (1000 * 60 * 60))
    const minutesToSLA = Math.floor((timeToSLA % (1000 * 60 * 60)) / (1000 * 60))
    
    if (timeToSLA < 0) {
      const hoursOverdue = Math.abs(hoursToSLA)
      const minutesOverdue = Math.abs(minutesToSLA)
      return `${hoursOverdue}ó ${minutesOverdue}p túllépés`
    } else {
      return `${hoursToSLA}ó ${minutesToSLA}p`
    }
  }

  const getUrgentTicketsCount = () => {
    return tickets.filter(ticket => {
      const slaStatus = getSLAStatus(ticket)
      return slaStatus.status === 'critical' || slaStatus.status === 'breached'
    }).length
  }

  const handleNewTicket = () => {
    setShowNewTicketDialog(true)
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Hibajegy Kezelés</h1>
          <p className="text-gray-600 mt-2">
            Karbantartási hibajegyek és SLA követés
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {getUrgentTicketsCount() > 0 && (
            <Badge variant="destructive" className="gap-1">
              <Bell className="w-3 h-3" />
              {getUrgentTicketsCount()} sürgős
            </Badge>
          )}
          
          <Button onClick={handleNewTicket} className="gap-2">
            <Plus className="w-4 h-4" />
            Új hibajegy
          </Button>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Nyitott jegyek</p>
                <p className="text-2xl font-bold">
                  {tickets.filter(t => t.status === 'open').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Activity className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Folyamatban</p>
                <p className="text-2xl font-bold">
                  {tickets.filter(t => t.status === 'in-progress').length}
                </p>
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
                <p className="text-sm text-gray-600">SLA kritikus</p>
                <p className="text-2xl font-bold text-red-600">
                  {getUrgentTicketsCount()}
                </p>
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
                <p className="text-sm text-gray-600">Megoldott</p>
                <p className="text-2xl font-bold">
                  {tickets.filter(t => t.status === 'resolved').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
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
                placeholder="Keresés jegy címe, leírása vagy ID alapján..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Státusz szűrő" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Minden státusz</SelectItem>
                <SelectItem value="open">Nyitott</SelectItem>
                <SelectItem value="in-progress">Folyamatban</SelectItem>
                <SelectItem value="pending">Várakozás</SelectItem>
                <SelectItem value="resolved">Megoldott</SelectItem>
                <SelectItem value="closed">Lezárt</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Prioritás szűrő" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Minden prioritás</SelectItem>
                <SelectItem value="critical">Kritikus</SelectItem>
                <SelectItem value="high">Magas</SelectItem>
                <SelectItem value="medium">Közepes</SelectItem>
                <SelectItem value="low">Alacsony</SelectItem>
              </SelectContent>
            </Select>
            
            <Button variant="outline" onClick={() => {
              setSearchQuery('')
              setStatusFilter('all')
              setPriorityFilter('all')
            }}>
              Szűrők törlése
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Tickets List */}
      <Card>
        <CardHeader>
          <CardTitle>Hibajegyek ({filteredTickets.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredTickets.map((ticket) => {
              const slaStatus = getSLAStatus(ticket)
              const slaProgress = calculateSLAProgress(ticket)
              
              return (
                <div
                  key={ticket.id}
                  className="p-4 border rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => setSelectedTicket(ticket)}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <Badge className={`${getPriorityColor(ticket.priority)} text-xs`}>
                        {ticket.priority === 'critical' && 'KRITIKUS'}
                        {ticket.priority === 'high' && 'MAGAS'}
                        {ticket.priority === 'medium' && 'KÖZEPES'}
                        {ticket.priority === 'low' && 'ALACSONY'}
                      </Badge>
                      
                      <Badge className={`${getStatusColor(ticket.status)} text-xs gap-1`}>
                        {getStatusIcon(ticket.status)}
                        {ticket.status === 'open' && 'Nyitott'}
                        {ticket.status === 'in-progress' && 'Folyamatban'}
                        {ticket.status === 'pending' && 'Várakozás'}
                        {ticket.status === 'resolved' && 'Megoldott'}
                        {ticket.status === 'closed' && 'Lezárt'}
                      </Badge>
                      
                      <span className="text-sm text-gray-500 font-mono">{ticket.id}</span>
                    </div>
                    
                    <div className={`flex items-center gap-2 ${slaStatus.color}`}>
                      {slaStatus.icon}
                      <span className="text-sm font-medium">
                        {formatTimeRemaining(ticket)}
                      </span>
                    </div>
                  </div>
                  
                  <h3 className="font-semibold text-lg mb-2">{ticket.title}</h3>
                  <p className="text-gray-600 text-sm mb-3 line-clamp-2">{ticket.description}</p>
                  
                  <div className="grid md:grid-cols-3 gap-4 mb-3">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <User className="w-4 h-4" />
                      <span>Felelős: {ticket.assignee || 'Nincs hozzárendelve'}</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Wrench className="w-4 h-4" />
                      <span>{ticket.objectType === 'gate' ? 'Kapu' : ticket.objectType === 'building' ? 'Épület' : 'Jármű'}: {ticket.objectId}</span>
                    </div>
                    
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Calendar className="w-4 h-4" />
                      <span>Létrehozva: {ticket.createdAt.toLocaleDateString('hu-HU')}</span>
                    </div>
                  </div>
                  
                  {/* SLA Progress Bar */}
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">SLA teljesítés</span>
                      <span className={slaStatus.color}>
                        {Math.round(slaProgress)}% - {formatTimeRemaining(ticket)}
                      </span>
                    </div>
                    <Progress 
                      value={slaProgress} 
                      className={`h-2 ${
                        slaProgress > 90 ? 'bg-red-100' : 
                        slaProgress > 70 ? 'bg-orange-100' : 
                        'bg-green-100'
                      }`}
                    />
                  </div>
                  
                  {ticket.tags.length > 0 && (
                    <div className="flex gap-1 mt-3">
                      {ticket.tags.map((tag, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
            
            {filteredTickets.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                <p>Nincs találat a megadott szűrési feltételek alapján.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Ticket Details Dialog */}
      {selectedTicket && (
        <Dialog open={!!selectedTicket} onOpenChange={() => setSelectedTicket(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <span className="font-mono text-sm">{selectedTicket.id}</span>
                <Badge className={getPriorityColor(selectedTicket.priority)}>
                  {selectedTicket.priority === 'critical' && 'KRITIKUS'}
                  {selectedTicket.priority === 'high' && 'MAGAS'}
                  {selectedTicket.priority === 'medium' && 'KÖZEPES'}
                  {selectedTicket.priority === 'low' && 'ALACSONY'}
                </Badge>
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-semibold mb-2">{selectedTicket.title}</h2>
                <p className="text-gray-700">{selectedTicket.description}</p>
              </div>
              
              <div className="grid md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Státusz</Label>
                    <Badge className={`${getStatusColor(selectedTicket.status)} gap-1 mt-1`}>
                      {getStatusIcon(selectedTicket.status)}
                      {selectedTicket.status === 'open' && 'Nyitott'}
                      {selectedTicket.status === 'in-progress' && 'Folyamatban'}
                      {selectedTicket.status === 'pending' && 'Várakozás'}
                      {selectedTicket.status === 'resolved' && 'Megoldott'}
                      {selectedTicket.status === 'closed' && 'Lezárt'}
                    </Badge>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Felelős</Label>
                    <p className="mt-1">{selectedTicket.assignee || 'Nincs hozzárendelve'}</p>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Bejelentő</Label>
                    <p className="mt-1">{selectedTicket.reporter}</p>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Helyszín</Label>
                    <p className="mt-1">{selectedTicket.location}</p>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-500">SLA határidő</Label>
                    <div className={`mt-1 ${getSLAStatus(selectedTicket).color}`}>
                      {selectedTicket.slaBreachAt.toLocaleString('hu-HU')}
                    </div>
                  </div>
                  
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Becsült idő</Label>
                    <p className="mt-1">{selectedTicket.estimatedHours} óra</p>
                  </div>
                  
                  {selectedTicket.actualHours && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Tényleges idő</Label>
                      <p className="mt-1">{selectedTicket.actualHours} óra</p>
                    </div>
                  )}
                  
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Kategória</Label>
                    <p className="mt-1 capitalize">{selectedTicket.category}</p>
                  </div>
                </div>
              </div>
              
              {/* SLA Visual */}
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium">SLA teljesítés</span>
                  <span className={getSLAStatus(selectedTicket).color}>
                    {formatTimeRemaining(selectedTicket)}
                  </span>
                </div>
                <Progress 
                  value={calculateSLAProgress(selectedTicket)} 
                  className="h-3"
                />
              </div>
              
              {selectedTicket.tags.length > 0 && (
                <div>
                  <Label className="text-sm font-medium text-gray-500">Címkék</Label>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {selectedTicket.tags.map((tag, index) => (
                      <Badge key={index} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex gap-3 pt-4 border-t">
                <Button variant="outline">Szerkesztés</Button>
                <Button variant="outline">Komment hozzáadása</Button>
                <Button>Státusz módosítása</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}