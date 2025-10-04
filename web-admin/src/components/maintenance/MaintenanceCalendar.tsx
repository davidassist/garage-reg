'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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
} from '@/components/ui/dialog'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Calendar as CalendarIcon,
  ChevronLeft,
  ChevronRight,
  Download,
  Filter,
  User,
  Clock,
  AlertTriangle,
  CheckCircle2,
  FileText,
  Wrench,
  Building2,
  Car,
  Eye,
  Plus,
  Grid3x3,
  List,
  MoreVertical
} from 'lucide-react'

interface CalendarEvent {
  id: string
  title: string
  description: string
  type: 'inspection' | 'maintenance' | 'repair' | 'preventive'
  status: 'scheduled' | 'in-progress' | 'completed' | 'cancelled' | 'overdue'
  priority: 'low' | 'medium' | 'high' | 'critical'
  startDate: Date
  endDate: Date
  duration: number // minutes
  technician: string
  location: string
  objectType: 'gate' | 'building' | 'vehicle'
  objectId: string
  notes?: string
  workOrderId?: string
  ticketId?: string
}

interface CalendarDay {
  date: Date
  events: CalendarEvent[]
  isCurrentMonth: boolean
  isToday: boolean
  isWeekend: boolean
}

// Mock data
const mockEvents: CalendarEvent[] = [
  {
    id: 'cal-001',
    title: 'Garázs kapu biztonsági ellenőrzés',
    description: 'Napi biztonsági ellenőrzés szenzor és kapu működésének tesztelése',
    type: 'inspection',
    status: 'scheduled',
    priority: 'high',
    startDate: new Date(2025, 9, 4, 9, 0), // Oct 4, 2025, 9:00 AM
    endDate: new Date(2025, 9, 4, 10, 30),
    duration: 90,
    technician: 'Nagy Péter',
    location: 'Budapest, Garázs A/1',
    objectType: 'gate',
    objectId: 'GATE-123',
    workOrderId: 'WO-001'
  },
  {
    id: 'cal-002',
    title: 'LED világítás karbantartás',
    description: 'Lépcsőházi LED panelek ellenőrzése és szükség esetén cseréje',
    type: 'maintenance',
    status: 'in-progress',
    priority: 'medium',
    startDate: new Date(2025, 9, 4, 14, 0),
    endDate: new Date(2025, 9, 4, 16, 0),
    duration: 120,
    technician: 'Szabó Anna',
    location: 'Budapest, Lépcsőház B',
    objectType: 'building',
    objectId: 'BLDG-002',
    workOrderId: 'WO-002'
  },
  {
    id: 'cal-003',
    title: 'Távvezérlő szinkronizáció',
    description: 'Kritikus távvezérlő párosítás probléma megoldása',
    type: 'repair',
    status: 'overdue',
    priority: 'critical',
    startDate: new Date(2025, 9, 3, 15, 0),
    endDate: new Date(2025, 9, 3, 17, 0),
    duration: 120,
    technician: 'Kiss József',
    location: 'Budapest, Garázs C/4',
    objectType: 'gate',
    objectId: 'GATE-401',
    workOrderId: 'WO-003',
    ticketId: 'MAINT-003'
  },
  {
    id: 'cal-004',
    title: 'Heti megelőző karbantartás',
    description: 'Rutinszerű heti ellenőrzés és kenőanyag feltöltés',
    type: 'preventive',
    status: 'scheduled',
    priority: 'medium',
    startDate: new Date(2025, 9, 5, 8, 0),
    endDate: new Date(2025, 9, 5, 12, 0),
    duration: 240,
    technician: 'Varga Béla',
    location: 'Budapest, Összes garázs',
    objectType: 'building',
    objectId: 'ALL',
    workOrderId: 'WO-004'
  },
  {
    id: 'cal-005',
    title: 'Motor diagnosztika',
    description: 'Kapu motor működésének részletes ellenőrzése',
    type: 'inspection',
    status: 'completed',
    priority: 'low',
    startDate: new Date(2025, 9, 2, 10, 0),
    endDate: new Date(2025, 9, 2, 11, 0),
    duration: 60,
    technician: 'Nagy Péter',
    location: 'Budapest, Garázs D/2',
    objectType: 'gate',
    objectId: 'GATE-250',
    workOrderId: 'WO-005'
  },
  {
    id: 'cal-006',
    title: 'Jármű műszaki vizsgálat',
    description: 'Szolgálati jármű éves műszaki ellenőrzése',
    type: 'inspection',
    status: 'scheduled',
    priority: 'high',
    startDate: new Date(2025, 9, 7, 13, 0),
    endDate: new Date(2025, 9, 7, 15, 30),
    duration: 150,
    technician: 'Kovács János',
    location: 'Műszaki állomás',
    objectType: 'vehicle',
    objectId: 'VEH-001',
    workOrderId: 'WO-006'
  },
  {
    id: 'cal-007',
    title: 'Épület tűzvédelmi ellenőrzés',
    description: 'Tűzjelző rendszer és vészkijáratok ellenőrzése',
    type: 'inspection',
    status: 'scheduled',
    priority: 'high',
    startDate: new Date(2025, 9, 8, 9, 30),
    endDate: new Date(2025, 9, 8, 11, 30),
    duration: 120,
    technician: 'Szabó Anna',
    location: 'Budapest, Főépület',
    objectType: 'building',
    objectId: 'BLDG-001',
    workOrderId: 'WO-007'
  }
]

const technicians = [
  'Nagy Péter',
  'Szabó Anna',
  'Kiss József',
  'Varga Béla',
  'Kovács János'
]

export function MaintenanceCalendar() {
  const [events] = useState<CalendarEvent[]>(mockEvents)
  const [currentDate, setCurrentDate] = useState(new Date(2025, 9, 4)) // Oct 4, 2025
  const [viewMode, setViewMode] = useState<'week' | 'month'>('month')
  const [selectedTechnician, setSelectedTechnician] = useState<string>('all')
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null)
  const [focusedEventIndex, setFocusedEventIndex] = useState<number>(-1)
  const calendarRef = useRef<HTMLDivElement>(null)

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (selectedEvent || !calendarRef.current) return
      
      const eventElements = calendarRef.current.querySelectorAll('[data-event-id]')
      const totalEvents = eventElements.length
      
      if (totalEvents === 0) return
      
      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault()
          setFocusedEventIndex(prev => Math.max(0, prev - 1))
          break
        case 'ArrowDown':
          e.preventDefault()
          setFocusedEventIndex(prev => Math.min(totalEvents - 1, prev + 1))
          break
        case 'Enter':
        case ' ':
          e.preventDefault()
          if (focusedEventIndex >= 0) {
            const eventId = eventElements[focusedEventIndex].getAttribute('data-event-id')
            const event = filteredEvents.find(e => e.id === eventId)
            if (event) setSelectedEvent(event)
          }
          break
        case 'Escape':
          setFocusedEventIndex(-1)
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [focusedEventIndex, selectedEvent])

  // Focus management for keyboard navigation
  useEffect(() => {
    if (focusedEventIndex >= 0 && calendarRef.current) {
      const eventElements = calendarRef.current.querySelectorAll('[data-event-id]')
      const targetElement = eventElements[focusedEventIndex] as HTMLElement
      if (targetElement) {
        targetElement.focus()
        targetElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    }
  }, [focusedEventIndex])

  const filteredEvents = events.filter(event => {
    if (selectedTechnician !== 'all' && event.technician !== selectedTechnician) {
      return false
    }
    
    if (viewMode === 'week') {
      const weekStart = getWeekStart(currentDate)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      return event.startDate >= weekStart && event.startDate <= weekEnd
    } else {
      const monthStart = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
      const monthEnd = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)
      return event.startDate >= monthStart && event.startDate <= monthEnd
    }
  })

  const getWeekStart = (date: Date) => {
    const d = new Date(date)
    const day = d.getDay()
    const diff = d.getDate() - day + (day === 0 ? -6 : 1) // Monday as first day
    return new Date(d.setDate(diff))
  }

  const getCalendarDays = (): CalendarDay[] => {
    const days: CalendarDay[] = []
    
    if (viewMode === 'week') {
      const weekStart = getWeekStart(currentDate)
      for (let i = 0; i < 7; i++) {
        const date = new Date(weekStart)
        date.setDate(date.getDate() + i)
        
        const dayEvents = filteredEvents.filter(event => 
          event.startDate.toDateString() === date.toDateString()
        )
        
        days.push({
          date,
          events: dayEvents,
          isCurrentMonth: true,
          isToday: date.toDateString() === new Date().toDateString(),
          isWeekend: date.getDay() === 0 || date.getDay() === 6
        })
      }
    } else {
      const monthStart = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1)
      const monthEnd = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0)
      
      // Get first day of calendar (might be from previous month)
      const calendarStart = getWeekStart(monthStart)
      
      // Generate 42 days (6 weeks)
      for (let i = 0; i < 42; i++) {
        const date = new Date(calendarStart)
        date.setDate(date.getDate() + i)
        
        const dayEvents = filteredEvents.filter(event => 
          event.startDate.toDateString() === date.toDateString()
        )
        
        days.push({
          date,
          events: dayEvents,
          isCurrentMonth: date.getMonth() === currentDate.getMonth(),
          isToday: date.toDateString() === new Date().toDateString(),
          isWeekend: date.getDay() === 0 || date.getDay() === 6
        })
      }
    }
    
    return days
  }

  const navigateDate = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate)
    
    if (viewMode === 'week') {
      newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7))
    } else {
      newDate.setMonth(newDate.getMonth() + (direction === 'next' ? 1 : -1))
    }
    
    setCurrentDate(newDate)
    setFocusedEventIndex(-1)
  }

  const getEventColor = (event: CalendarEvent) => {
    if (event.status === 'overdue') return 'bg-red-100 border-red-300 text-red-800'
    if (event.status === 'completed') return 'bg-green-100 border-green-300 text-green-800'
    if (event.status === 'in-progress') return 'bg-blue-100 border-blue-300 text-blue-800'
    
    switch (event.priority) {
      case 'critical':
        return 'bg-red-50 border-red-200 text-red-700'
      case 'high':
        return 'bg-orange-50 border-orange-200 text-orange-700'
      case 'medium':
        return 'bg-yellow-50 border-yellow-200 text-yellow-700'
      case 'low':
        return 'bg-green-50 border-green-200 text-green-700'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-3 h-3" />
      case 'in-progress':
        return <Clock className="w-3 h-3" />
      case 'overdue':
        return <AlertTriangle className="w-3 h-3" />
      default:
        return <FileText className="w-3 h-3" />
    }
  }

  const getObjectIcon = (objectType: string) => {
    switch (objectType) {
      case 'gate':
        return <Car className="w-3 h-3" />
      case 'building':
        return <Building2 className="w-3 h-3" />
      case 'vehicle':
        return <Car className="w-3 h-3" />
      default:
        return <Wrench className="w-3 h-3" />
    }
  }

  const exportToICS = () => {
    const icsEvents = filteredEvents.map(event => {
      const formatDate = (date: Date) => {
        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z'
      }
      
      return [
        'BEGIN:VEVENT',
        `UID:${event.id}@garagereg.hu`,
        `DTSTART:${formatDate(event.startDate)}`,
        `DTEND:${formatDate(event.endDate)}`,
        `SUMMARY:${event.title}`,
        `DESCRIPTION:${event.description}\\n\\nTechnikus: ${event.technician}\\nHelyszín: ${event.location}\\nObjektum: ${event.objectId}`,
        `LOCATION:${event.location}`,
        `STATUS:${event.status.toUpperCase()}`,
        `PRIORITY:${event.priority === 'critical' ? '1' : event.priority === 'high' ? '3' : '5'}`,
        'END:VEVENT'
      ].join('\r\n')
    }).join('\r\n')
    
    const icsContent = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//GarageReg//Maintenance Calendar//HU',
      'CALSCALE:GREGORIAN',
      'METHOD:PUBLISH',
      icsEvents,
      'END:VCALENDAR'
    ].join('\r\n')
    
    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `maintenance-calendar-${currentDate.toISOString().split('T')[0]}.ics`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const formatDateHeader = () => {
    if (viewMode === 'week') {
      const weekStart = getWeekStart(currentDate)
      const weekEnd = new Date(weekStart)
      weekEnd.setDate(weekEnd.getDate() + 6)
      
      return `${weekStart.toLocaleDateString('hu-HU', { 
        month: 'long', 
        day: 'numeric' 
      })} - ${weekEnd.toLocaleDateString('hu-HU', { 
        month: 'long', 
        day: 'numeric', 
        year: 'numeric' 
      })}`
    } else {
      return currentDate.toLocaleDateString('hu-HU', { 
        month: 'long', 
        year: 'numeric' 
      })
    }
  }

  const calendarDays = getCalendarDays()
  const weekDays = ['Hétfő', 'Kedd', 'Szerda', 'Csütörtök', 'Péntek', 'Szombat', 'Vasárnap']

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Karbantartási Naptár</h1>
          <p className="text-gray-600 mt-2">
            Ellenőrzések és munkalapok ütemezése - Billentyűzet: ↑↓ navigáció, Enter/Space megnyitás
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={exportToICS}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            ICS Export
          </Button>
          
          <Button className="gap-2">
            <Plus className="w-4 h-4" />
            Új esemény
          </Button>
        </div>
      </div>

      {/* Controls */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigateDate('prev')}
                >
                  <ChevronLeft className="w-4 h-4" />
                </Button>
                
                <h2 className="text-lg font-semibold min-w-[250px] text-center">
                  {formatDateHeader()}
                </h2>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => navigateDate('next')}
                >
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </div>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentDate(new Date())}
              >
                Ma
              </Button>
            </div>
            
            <div className="flex items-center gap-3">
              <Select value={selectedTechnician} onValueChange={setSelectedTechnician}>
                <SelectTrigger className="w-[180px]">
                  <Filter className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Technikus szűrő" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Minden technikus</SelectItem>
                  {technicians.map(tech => (
                    <SelectItem key={tech} value={tech}>
                      {tech}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <div className="flex rounded-lg border bg-gray-50 p-1">
                <Button
                  variant={viewMode === 'week' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => {
                    setViewMode('week')
                    setFocusedEventIndex(-1)
                  }}
                  className="gap-2"
                >
                  <List className="w-4 h-4" />
                  Hét
                </Button>
                <Button
                  variant={viewMode === 'month' ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => {
                    setViewMode('month')
                    setFocusedEventIndex(-1)
                  }}
                  className="gap-2"
                >
                  <Grid3x3 className="w-4 h-4" />
                  Hónap
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {filteredEvents.filter(e => e.status === 'scheduled').length}
            </div>
            <div className="text-sm text-gray-600">Tervezett</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-purple-600">
              {filteredEvents.filter(e => e.status === 'in-progress').length}
            </div>
            <div className="text-sm text-gray-600">Folyamatban</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600">
              {filteredEvents.filter(e => e.status === 'overdue').length}
            </div>
            <div className="text-sm text-gray-600">Késésben</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {filteredEvents.filter(e => e.status === 'completed').length}
            </div>
            <div className="text-sm text-gray-600">Befejezett</div>
          </CardContent>
        </Card>
      </div>

      {/* Calendar Grid */}
      <Card>
        <CardContent className="p-0">
          <div 
            ref={calendarRef}
            className="calendar-grid"
            tabIndex={0}
          >
            {/* Header Row */}
            <div className={`grid ${viewMode === 'week' ? 'grid-cols-7' : 'grid-cols-7'} border-b bg-gray-50`}>
              {weekDays.map(day => (
                <div key={day} className="p-3 text-center font-medium text-gray-700 border-r last:border-r-0">
                  {day}
                </div>
              ))}
            </div>
            
            {/* Calendar Days */}
            <div className={`grid ${viewMode === 'week' ? 'grid-cols-7' : 'grid-cols-7'}`}>
              {calendarDays.map((day, dayIndex) => (
                <div
                  key={dayIndex}
                  className={`min-h-[120px] border-r border-b last:border-r-0 p-2 ${
                    !day.isCurrentMonth ? 'bg-gray-50' : ''
                  } ${day.isWeekend ? 'bg-blue-50/30' : ''} ${
                    day.isToday ? 'bg-blue-100' : ''
                  }`}
                >
                  <div className={`text-sm font-medium mb-2 ${
                    day.isToday ? 'text-blue-700' : 
                    !day.isCurrentMonth ? 'text-gray-400' : 'text-gray-700'
                  }`}>
                    {day.date.getDate()}
                  </div>
                  
                  <div className="space-y-1">
                    {day.events.map((event, eventIndex) => (
                      <div
                        key={event.id}
                        data-event-id={event.id}
                        tabIndex={0}
                        className={`text-xs p-1 rounded border cursor-pointer hover:shadow-sm transition-all ${
                          getEventColor(event)
                        } ${
                          focusedEventIndex === filteredEvents.indexOf(event) 
                            ? 'ring-2 ring-blue-400 ring-offset-1' 
                            : ''
                        }`}
                        onClick={() => setSelectedEvent(event)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault()
                            setSelectedEvent(event)
                          }
                        }}
                      >
                        <div className="flex items-center gap-1 mb-1">
                          {getStatusIcon(event.status)}
                          {getObjectIcon(event.objectType)}
                          <span className="font-medium truncate">
                            {event.startDate.toLocaleTimeString('hu-HU', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </span>
                        </div>
                        <div className="truncate font-medium" title={event.title}>
                          {event.title}
                        </div>
                        <div className="flex items-center gap-1 text-xs opacity-75">
                          <User className="w-2 h-2" />
                          <span className="truncate">{event.technician}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Event Details Dialog */}
      {selectedEvent && (
        <Dialog open={!!selectedEvent} onOpenChange={() => setSelectedEvent(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <div className="flex items-center gap-2">
                  {getStatusIcon(selectedEvent.status)}
                  {getObjectIcon(selectedEvent.objectType)}
                </div>
                <span>{selectedEvent.title}</span>
                <Badge className={getEventColor(selectedEvent)}>
                  {selectedEvent.priority === 'critical' && 'KRITIKUS'}
                  {selectedEvent.priority === 'high' && 'MAGAS'}
                  {selectedEvent.priority === 'medium' && 'KÖZEPES'}
                  {selectedEvent.priority === 'low' && 'ALACSONY'}
                </Badge>
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <p className="text-gray-700">{selectedEvent.description}</p>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Időpont:</span>
                  <p>
                    {selectedEvent.startDate.toLocaleDateString('hu-HU')} {' '}
                    {selectedEvent.startDate.toLocaleTimeString('hu-HU', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })} - {selectedEvent.endDate.toLocaleTimeString('hu-HU', {
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Időtartam:</span>
                  <p>{selectedEvent.duration} perc</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Technikus:</span>
                  <p>{selectedEvent.technician}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Helyszín:</span>
                  <p>{selectedEvent.location}</p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Objektum:</span>
                  <p>
                    {selectedEvent.objectType === 'gate' ? 'Kapu' : 
                     selectedEvent.objectType === 'building' ? 'Épület' : 'Jármű'}: {' '}
                    {selectedEvent.objectId}
                  </p>
                </div>
                
                <div>
                  <span className="text-sm font-medium text-gray-500">Státusz:</span>
                  <Badge className={getEventColor(selectedEvent)}>
                    {selectedEvent.status === 'scheduled' && 'Tervezett'}
                    {selectedEvent.status === 'in-progress' && 'Folyamatban'}
                    {selectedEvent.status === 'completed' && 'Befejezett'}
                    {selectedEvent.status === 'cancelled' && 'Törölve'}
                    {selectedEvent.status === 'overdue' && 'Késésben'}
                  </Badge>
                </div>
              </div>
              
              {selectedEvent.notes && (
                <div>
                  <span className="text-sm font-medium text-gray-500">Megjegyzések:</span>
                  <p className="text-gray-700">{selectedEvent.notes}</p>
                </div>
              )}
              
              <div className="flex gap-3 pt-4 border-t">
                <Button variant="outline" className="gap-2">
                  <Eye className="w-4 h-4" />
                  Részletek
                </Button>
                <Button variant="outline">Szerkesztés</Button>
                <Button>Státusz módosítása</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}