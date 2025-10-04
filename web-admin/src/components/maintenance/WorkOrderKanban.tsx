'use client'

import React, { useState, useRef } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
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
  MoreVertical,
  Timer,
  Activity,
  GripVertical,
  ArrowRight
} from 'lucide-react'

interface WorkOrder {
  id: string
  title: string
  description: string
  priority: 'low' | 'medium' | 'high' | 'critical'
  status: 'backlog' | 'todo' | 'in-progress' | 'review' | 'done'
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
  comments: Array<{
    id: string
    author: string
    content: string
    timestamp: Date
  }>
}

// Mock data
const mockWorkOrders: WorkOrder[] = [
  {
    id: 'WO-001',
    title: 'Garázs kapu szenzor javítás',
    description: 'Az alsó biztonsági szenzor cseréje és kalibrálása',
    priority: 'high',
    status: 'todo',
    category: 'corrective',
    reporter: 'Kovács János',
    assignee: 'Nagy Péter',
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 6 * 60 * 60 * 1000),
    slaBreachAt: new Date(Date.now() + 6 * 60 * 60 * 1000),
    estimatedHours: 3,
    objectType: 'gate',
    objectId: 'GATE-123',
    location: 'Budapest, Garázs A/1',
    tags: ['sensor', 'safety'],
    attachments: [],
    comments: []
  },
  {
    id: 'WO-002',
    title: 'Távvezérlő szinkronizáció',
    description: 'Távvezérlő újrapárosítása és tesztelés',
    priority: 'critical',
    status: 'in-progress',
    category: 'emergency',
    reporter: 'Lakó Mária',
    assignee: 'Kiss József',
    createdAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 30 * 60 * 1000),
    dueDate: new Date(Date.now() + 1 * 60 * 60 * 1000),
    slaBreachAt: new Date(Date.now() + 1 * 60 * 60 * 1000),
    estimatedHours: 2,
    actualHours: 1,
    objectType: 'gate',
    objectId: 'GATE-401',
    location: 'Budapest, Garázs B/4',
    tags: ['remote', 'pairing', 'critical'],
    attachments: [],
    comments: [
      {
        id: 'c1',
        author: 'Kiss József',
        content: 'Elkezdtem a távvezérlő diagnosztikáját. A frekvencia beállítások hibásak.',
        timestamp: new Date(Date.now() - 30 * 60 * 1000)
      }
    ]
  },
  {
    id: 'WO-003',
    title: 'Heti karbantartás - A épület',
    description: 'Rutinszerű ellenőrzés és kenőanyag feltöltés',
    priority: 'medium',
    status: 'backlog',
    category: 'preventive',
    reporter: 'Rendszer',
    assignee: 'Szabó Anna',
    createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 3 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 20 * 60 * 60 * 1000),
    slaBreachAt: new Date(Date.now() + 20 * 60 * 60 * 1000),
    estimatedHours: 4,
    objectType: 'building',
    objectId: 'BLDG-A',
    location: 'Budapest, A épület',
    tags: ['routine', 'preventive'],
    attachments: [],
    comments: []
  },
  {
    id: 'WO-004',
    title: 'LED panel csere',
    description: 'Lépcsőházi világítás javítása',
    priority: 'low',
    status: 'review',
    category: 'corrective',
    reporter: 'Takács Gábor',
    assignee: 'Varga Béla',
    createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 1 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 48 * 60 * 60 * 1000),
    slaBreachAt: new Date(Date.now() + 48 * 60 * 60 * 1000),
    estimatedHours: 2,
    actualHours: 1.5,
    objectType: 'building',
    objectId: 'BLDG-001',
    location: 'Budapest, Lépcsőház C',
    tags: ['lighting', 'led'],
    attachments: [],
    comments: [
      {
        id: 'c2',
        author: 'Varga Béla',
        content: 'LED panelek kicserélve. Tesztelés folyamatban.',
        timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000)
      }
    ]
  },
  {
    id: 'WO-005',
    title: 'Motor kenési ellenőrzés',
    description: 'Kapu motor kenőanyag szint és működés ellenőrzése',
    priority: 'medium',
    status: 'done',
    category: 'preventive',
    reporter: 'Rendszer',
    assignee: 'Nagy Péter',
    createdAt: new Date(Date.now() - 8 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
    dueDate: new Date(Date.now() + 16 * 60 * 60 * 1000),
    slaBreachAt: new Date(Date.now() + 16 * 60 * 60 * 1000),
    estimatedHours: 1,
    actualHours: 0.5,
    objectType: 'gate',
    objectId: 'GATE-205',
    location: 'Budapest, Garázs C/2',
    tags: ['motor', 'lubrication', 'preventive'],
    attachments: [],
    comments: []
  }
]

const columns = [
  { id: 'backlog', title: 'Várakozó', color: 'bg-gray-100' },
  { id: 'todo', title: 'Tervezetten', color: 'bg-blue-100' },
  { id: 'in-progress', title: 'Folyamatban', color: 'bg-yellow-100' },
  { id: 'review', title: 'Ellenőrzés', color: 'bg-purple-100' },
  { id: 'done', title: 'Kész', color: 'bg-green-100' }
]

export function WorkOrderKanban() {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>(mockWorkOrders)
  const [selectedWorkOrder, setSelectedWorkOrder] = useState<WorkOrder | null>(null)
  const [draggedItem, setDraggedItem] = useState<string | null>(null)
  const [draggedOverColumn, setDraggedOverColumn] = useState<string | null>(null)
  const dragCounterRef = useRef(0)

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

  const getSLAStatus = (workOrder: WorkOrder) => {
    const now = new Date()
    const timeToSLA = workOrder.slaBreachAt.getTime() - now.getTime()
    const hoursToSLA = timeToSLA / (1000 * 60 * 60)
    
    if (hoursToSLA < 0) {
      return { status: 'breached', color: 'text-red-600', bgColor: 'bg-red-50 border-red-200' }
    } else if (hoursToSLA < 1) {
      return { status: 'critical', color: 'text-red-500', bgColor: 'bg-red-50 border-red-200' }
    } else if (hoursToSLA < 4) {
      return { status: 'warning', color: 'text-orange-500', bgColor: 'bg-orange-50 border-orange-200' }
    } else {
      return { status: 'safe', color: 'text-green-500', bgColor: 'bg-white border-gray-200' }
    }
  }

  const formatTimeRemaining = (workOrder: WorkOrder) => {
    const now = new Date()
    const timeToSLA = workOrder.slaBreachAt.getTime() - now.getTime()
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

  const handleDragStart = (e: React.DragEvent, workOrderId: string) => {
    setDraggedItem(workOrderId)
    e.dataTransfer.setData('text/plain', workOrderId)
    e.dataTransfer.effectAllowed = 'move'
    
    // Add audit log entry
    console.log(`Drag started: Work Order ${workOrderId}`, {
      timestamp: new Date().toISOString(),
      user: 'Current User', // In real app, get from auth
      action: 'drag_start',
      workOrderId
    })
  }

  const handleDragEnd = () => {
    setDraggedItem(null)
    setDraggedOverColumn(null)
    dragCounterRef.current = 0
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDragEnter = (e: React.DragEvent, columnId: string) => {
    e.preventDefault()
    dragCounterRef.current++
    setDraggedOverColumn(columnId)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    dragCounterRef.current--
    if (dragCounterRef.current === 0) {
      setDraggedOverColumn(null)
    }
  }

  const handleDrop = (e: React.DragEvent, newStatus: string) => {
    e.preventDefault()
    const workOrderId = e.dataTransfer.getData('text/plain')
    
    if (workOrderId && workOrderId !== newStatus) {
      const workOrder = workOrders.find(wo => wo.id === workOrderId)
      const oldStatus = workOrder?.status
      
      setWorkOrders(prev => 
        prev.map(wo => 
          wo.id === workOrderId 
            ? { 
                ...wo, 
                status: newStatus as WorkOrder['status'],
                updatedAt: new Date()
              }
            : wo
        )
      )
      
      // Audit log entry
      console.log(`Work Order status changed: ${workOrderId}`, {
        timestamp: new Date().toISOString(),
        user: 'Current User', // In real app, get from auth
        action: 'status_change',
        workOrderId,
        oldStatus,
        newStatus,
        method: 'drag_and_drop'
      })
      
      // Show notification for critical status changes
      if (newStatus === 'done' && workOrder) {
        console.log(`Work Order completed: ${workOrder.title}`)
      }
    }
    
    setDraggedOverColumn(null)
    dragCounterRef.current = 0
  }

  const getWorkOrdersByStatus = (status: string) => {
    return workOrders.filter(wo => wo.status === status)
  }

  const getColumnStats = (status: string) => {
    const orders = getWorkOrdersByStatus(status)
    const criticalCount = orders.filter(wo => {
      const slaStatus = getSLAStatus(wo)
      return slaStatus.status === 'critical' || slaStatus.status === 'breached'
    }).length
    
    return { total: orders.length, critical: criticalCount }
  }

  return (
    <div className="max-w-full mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Munkalap Kanban</h1>
          <p className="text-gray-600 mt-2">
            Drag & drop munkálatok státusz kezelése és auditálás
          </p>
        </div>
        
        <Button className="gap-2">
          <Plus className="w-4 h-4" />
          Új munkalap
        </Button>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-5 gap-4 min-h-[600px]">
        {columns.map((column) => {
          const stats = getColumnStats(column.id)
          const isDropTarget = draggedOverColumn === column.id
          
          return (
            <div key={column.id} className="space-y-3">
              {/* Column Header */}
              <Card className={`${column.color} border-2 ${isDropTarget ? 'border-blue-400 shadow-lg' : ''}`}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">
                      {column.title}
                    </CardTitle>
                    <div className="flex items-center gap-1">
                      <Badge variant="outline" className="text-xs">
                        {stats.total}
                      </Badge>
                      {stats.critical > 0 && (
                        <Badge variant="destructive" className="text-xs">
                          <Bell className="w-3 h-3 mr-1" />
                          {stats.critical}
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* Dropzone */}
              <div
                className={`min-h-[500px] p-2 rounded-lg border-2 border-dashed transition-all ${
                  isDropTarget 
                    ? 'border-blue-400 bg-blue-50' 
                    : 'border-gray-200 bg-gray-50/50'
                }`}
                onDragOver={handleDragOver}
                onDragEnter={(e) => handleDragEnter(e, column.id)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, column.id)}
              >
                <div className="space-y-3">
                  {getWorkOrdersByStatus(column.id).map((workOrder) => {
                    const slaStatus = getSLAStatus(workOrder)
                    const isDragging = draggedItem === workOrder.id
                    
                    return (
                      <Card
                        key={workOrder.id}
                        className={`cursor-grab active:cursor-grabbing transition-all hover:shadow-md ${
                          isDragging ? 'opacity-50 rotate-2 scale-105' : ''
                        } ${slaStatus.bgColor}`}
                        draggable
                        onDragStart={(e) => handleDragStart(e, workOrder.id)}
                        onDragEnd={handleDragEnd}
                        onClick={() => setSelectedWorkOrder(workOrder)}
                      >
                        <CardContent className="p-3">
                          {/* Header */}
                          <div className="flex items-start justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <GripVertical className="w-4 h-4 text-gray-400" />
                              <Badge className={`${getPriorityColor(workOrder.priority)} text-xs`}>
                                {workOrder.priority === 'critical' && 'KRITIKUS'}
                                {workOrder.priority === 'high' && 'MAGAS'}
                                {workOrder.priority === 'medium' && 'KÖZEPES'}
                                {workOrder.priority === 'low' && 'ALACSONY'}
                              </Badge>
                            </div>
                            
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm" className="p-1 h-auto">
                                  <MoreVertical className="w-4 h-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent>
                                <DropdownMenuItem>
                                  <Eye className="w-4 h-4 mr-2" />
                                  Részletek
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <User className="w-4 h-4 mr-2" />
                                  Hozzárendelés
                                </DropdownMenuItem>
                                <DropdownMenuItem>
                                  <ArrowRight className="w-4 h-4 mr-2" />
                                  Státusz változtatás
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </div>
                          
                          {/* Content */}
                          <div className="space-y-2">
                            <span className="text-xs text-gray-500 font-mono">{workOrder.id}</span>
                            <h3 className="font-medium text-sm line-clamp-2">{workOrder.title}</h3>
                            <p className="text-xs text-gray-600 line-clamp-2">{workOrder.description}</p>
                          </div>
                          
                          {/* Meta Info */}
                          <div className="mt-3 space-y-2">
                            <div className="flex items-center justify-between text-xs text-gray-500">
                              <div className="flex items-center gap-1">
                                <User className="w-3 h-3" />
                                <span>{workOrder.assignee || 'Nincs'}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <Wrench className="w-3 h-3" />
                                <span>{workOrder.objectId}</span>
                              </div>
                            </div>
                            
                            <div className="flex items-center justify-between text-xs">
                              <div className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                <span>{workOrder.estimatedHours}ó becsült</span>
                              </div>
                              {workOrder.actualHours && (
                                <div className="flex items-center gap-1 text-blue-600">
                                  <Timer className="w-3 h-3" />
                                  <span>{workOrder.actualHours}ó tényleges</span>
                                </div>
                              )}
                            </div>
                            
                            {/* SLA Warning */}
                            <div className={`flex items-center justify-between text-xs ${slaStatus.color}`}>
                              <div className="flex items-center gap-1">
                                {slaStatus.status === 'breached' && <XCircle className="w-3 h-3" />}
                                {slaStatus.status === 'critical' && <AlertTriangle className="w-3 h-3" />}
                                {slaStatus.status === 'warning' && <Clock className="w-3 h-3" />}
                                {slaStatus.status === 'safe' && <CheckCircle2 className="w-3 h-3" />}
                                <span>SLA: {formatTimeRemaining(workOrder)}</span>
                              </div>
                            </div>
                          </div>
                          
                          {/* Comments indicator */}
                          {workOrder.comments.length > 0 && (
                            <div className="mt-2 flex items-center gap-1 text-xs text-gray-500">
                              <FileText className="w-3 h-3" />
                              <span>{workOrder.comments.length} komment</span>
                            </div>
                          )}
                          
                          {/* Tags */}
                          {workOrder.tags.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-2">
                              {workOrder.tags.slice(0, 2).map((tag, index) => (
                                <Badge key={index} variant="outline" className="text-xs">
                                  {tag}
                                </Badge>
                              ))}
                              {workOrder.tags.length > 2 && (
                                <Badge variant="outline" className="text-xs">
                                  +{workOrder.tags.length - 2}
                                </Badge>
                              )}
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )
                  })}
                  
                  {getWorkOrdersByStatus(column.id).length === 0 && (
                    <div className="text-center py-8 text-gray-400">
                      <FileText className="w-8 h-8 mx-auto mb-2" />
                      <p className="text-sm">Nincs munkalap</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Work Order Details Dialog */}
      {selectedWorkOrder && (
        <Dialog open={!!selectedWorkOrder} onOpenChange={() => setSelectedWorkOrder(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <span className="font-mono text-sm">{selectedWorkOrder.id}</span>
                <Badge className={getPriorityColor(selectedWorkOrder.priority)}>
                  {selectedWorkOrder.priority.toUpperCase()}
                </Badge>
              </DialogTitle>
            </DialogHeader>
            
            <div className="space-y-4">
              <div>
                <h2 className="text-lg font-semibold mb-2">{selectedWorkOrder.title}</h2>
                <p className="text-gray-700">{selectedWorkOrder.description}</p>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="text-sm font-medium text-gray-500">Felelős:</span>
                  <p>{selectedWorkOrder.assignee || 'Nincs hozzárendelve'}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Helyszín:</span>
                  <p>{selectedWorkOrder.location}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">Becsült idő:</span>
                  <p>{selectedWorkOrder.estimatedHours} óra</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-500">SLA határidő:</span>
                  <p className={getSLAStatus(selectedWorkOrder).color}>
                    {selectedWorkOrder.slaBreachAt.toLocaleString('hu-HU')}
                  </p>
                </div>
              </div>
              
              {selectedWorkOrder.comments.length > 0 && (
                <div>
                  <h3 className="font-medium mb-2">Kommentek</h3>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {selectedWorkOrder.comments.map(comment => (
                      <div key={comment.id} className="p-2 bg-gray-50 rounded text-sm">
                        <div className="flex justify-between items-start mb-1">
                          <span className="font-medium">{comment.author}</span>
                          <span className="text-xs text-gray-500">
                            {comment.timestamp.toLocaleString('hu-HU')}
                          </span>
                        </div>
                        <p>{comment.content}</p>
                      </div>
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