'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  History as HistoryIcon, 
  User, 
  Calendar, 
  Clock, 
  Wrench, 
  AlertTriangle,
  CheckCircle,
  Settings,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'

interface GateHistoryProps {
  gateId: string
}

const mockHistory = [
  {
    id: '1',
    timestamp: '2024-10-04T10:30:00',
    type: 'maintenance',
    title: 'Rendszeres karbantartás',
    description: 'Teljes rendszer ellenőrzés és kenés',
    user: 'Kiss János',
    userRole: 'Karbantartó',
    status: 'completed',
    duration: 120,
    notes: 'Minden rendben, következő karbantartás 3 hónap múlva esedékes'
  },
  {
    id: '2',
    timestamp: '2024-09-28T14:15:00',
    type: 'operation',
    title: 'Kapu működési hiba',
    description: 'A kapu nem zárt be teljesen',
    user: 'Nagy Péter',
    userRole: 'Biztonsági őr',
    status: 'resolved',
    duration: 45,
    notes: 'Fotocella beállítás javítva'
  },
  {
    id: '3',
    timestamp: '2024-09-25T09:20:00',
    type: 'inspection',
    title: 'Biztonsági ellenőrzés',
    description: 'Havi biztonsági audit',
    user: 'Szabó Anna',
    userRole: 'Auditor',
    status: 'completed',
    duration: 30,
    notes: 'Minden biztonsági funkció megfelelően működik'
  },
  {
    id: '4',
    timestamp: '2024-09-20T16:45:00',
    type: 'configuration',
    title: 'Beállítások módosítása',
    description: 'Nyitási/zárási idők beállítása',
    user: 'Kovács Gábor',
    userRole: 'Rendszergazda',
    status: 'completed',
    duration: 15,
    notes: 'Nyitási idő 12s-ról 10s-ra csökkentve'
  },
  {
    id: '5',
    timestamp: '2024-09-15T08:00:00',
    type: 'installation',
    title: 'Komponens csere',
    description: 'Biztonsági fotocella cseréje',
    user: 'Tóth László',
    userRole: 'Technikus',
    status: 'completed',
    duration: 90,
    notes: 'Régi fotocella cserélve, új kalibrálva és tesztelve'
  }
]

const historyTypes = {
  maintenance: { label: 'Karbantartás', color: 'bg-blue-500', icon: Wrench },
  operation: { label: 'Működési esemény', color: 'bg-orange-500', icon: AlertTriangle },
  inspection: { label: 'Ellenőrzés', color: 'bg-green-500', icon: CheckCircle },
  configuration: { label: 'Konfiguráció', color: 'bg-purple-500', icon: Settings },
  installation: { label: 'Telepítés', color: 'bg-gray-500', icon: Settings }
}

const statusConfig = {
  completed: { label: 'Befejezve', color: 'bg-green-500' },
  resolved: { label: 'Megoldva', color: 'bg-blue-500' },
  pending: { label: 'Folyamatban', color: 'bg-yellow-500' },
  cancelled: { label: 'Törölve', color: 'bg-red-500' }
}

export function GateHistory({ gateId }: GateHistoryProps) {
  const [historyOpen, setHistoryOpen] = useState(true)
  const [selectedFilter, setSelectedFilter] = useState<string>('all')

  const filteredHistory = selectedFilter === 'all' 
    ? mockHistory 
    : mockHistory.filter(item => item.type === selectedFilter)

  return (
    <div className="space-y-6">
      <Collapsible open={historyOpen} onOpenChange={setHistoryOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <HistoryIcon className="h-5 w-5 mr-2" />
                  Kapu előzmények ({filteredHistory.length})
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-2">
                    <Button
                      size="sm"
                      variant={selectedFilter === 'all' ? 'default' : 'outline'}
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedFilter('all')
                      }}
                    >
                      Összes
                    </Button>
                    <Button
                      size="sm"
                      variant={selectedFilter === 'maintenance' ? 'default' : 'outline'}
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedFilter('maintenance')
                      }}
                    >
                      Karbantartás
                    </Button>
                    <Button
                      size="sm"
                      variant={selectedFilter === 'operation' ? 'default' : 'outline'}
                      onClick={(e) => {
                        e.stopPropagation()
                        setSelectedFilter('operation')
                      }}
                    >
                      Események
                    </Button>
                  </div>
                  {historyOpen ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </div>
              </div>
              <CardDescription>
                Teljes aktivitási napló és esemény előzmények
              </CardDescription>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent>
              <div className="space-y-4">
                {/* Timeline View */}
                <div className="relative">
                  {filteredHistory.map((item, index) => {
                    const typeConfig = historyTypes[item.type as keyof typeof historyTypes]
                    const statusInfo = statusConfig[item.status as keyof typeof statusConfig]
                    const TypeIcon = typeConfig.icon

                    return (
                      <div key={item.id} className="relative flex items-start space-x-4 pb-8">
                        {/* Timeline line */}
                        {index < filteredHistory.length - 1 && (
                          <div className="absolute left-5 top-12 w-px h-full bg-border"></div>
                        )}
                        
                        {/* Timeline icon */}
                        <div className={`flex items-center justify-center w-10 h-10 rounded-full ${typeConfig.color} text-white z-10`}>
                          <TypeIcon className="h-5 w-5" />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <Card className="shadow-sm">
                            <CardContent className="p-4">
                              <div className="flex items-start justify-between mb-2">
                                <div>
                                  <h4 className="font-semibold text-lg">{item.title}</h4>
                                  <p className="text-muted-foreground">{item.description}</p>
                                </div>
                                <Badge variant="secondary" className={`${statusInfo.color} text-white`}>
                                  {statusInfo.label}
                                </Badge>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                                <div className="flex items-center text-muted-foreground">
                                  <Calendar className="h-4 w-4 mr-2" />
                                  {new Date(item.timestamp).toLocaleDateString('hu-HU')}
                                </div>
                                <div className="flex items-center text-muted-foreground">
                                  <Clock className="h-4 w-4 mr-2" />
                                  {new Date(item.timestamp).toLocaleTimeString('hu-HU', { 
                                    hour: '2-digit', 
                                    minute: '2-digit' 
                                  })}
                                </div>
                                <div className="flex items-center text-muted-foreground">
                                  <User className="h-4 w-4 mr-2" />
                                  {item.user} ({item.userRole})
                                </div>
                                <div className="flex items-center text-muted-foreground">
                                  <Clock className="h-4 w-4 mr-2" />
                                  {item.duration} perc
                                </div>
                              </div>

                              {item.notes && (
                                <div className="mt-3 p-3 bg-muted/50 rounded-lg">
                                  <p className="text-sm">
                                    <strong>Megjegyzések:</strong> {item.notes}
                                  </p>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        </div>
                      </div>
                    )
                  })}
                </div>

                {filteredHistory.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <HistoryIcon className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Nincsenek események a kiválasztott szűrővel</p>
                  </div>
                )}
              </div>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  )
}