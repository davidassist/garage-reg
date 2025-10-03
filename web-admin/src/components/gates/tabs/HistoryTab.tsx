'use client'

import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import {
  Calendar,
  User,
  FileText,
  Settings,
  Wrench,
  AlertTriangle,
  Plus,
  Search,
  Filter,
  Clock,
  ChevronDown,
  Eye
} from 'lucide-react'
import {
  GateHistoryEntry,
  GateHistoryType,
  GateHistoryTypeLabels
} from '@/lib/types/gate-detail'

interface HistoryTabProps {
  gateId: string
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function HistoryTab({ gateId, isLoading, setIsLoading }: HistoryTabProps) {
  const [historyEntries, setHistoryEntries] = useState<GateHistoryEntry[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<GateHistoryType | 'all'>('all')
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set())

  useEffect(() => {
    loadHistory()
  }, [gateId])

  const loadHistory = async () => {
    try {
      setIsLoading(true)
      
      // Mock data - replace with actual API call
      const mockHistory: GateHistoryEntry[] = [
        {
          id: '1',
          gateId,
          type: 'installation',
          title: 'Kapu telepítése',
          description: 'A kapu sikeresen telepítve lett a megadott helyszínre. Minden komponens megfelelően működik.',
          performedBy: 'Kovács János',
          performedAt: new Date('2023-01-15T10:30:00'),
          createdAt: new Date('2023-01-15T10:30:00')
        },
        {
          id: '2',
          gateId,
          type: 'maintenance',
          title: 'Rendszeres karbantartás',
          description: 'Félévenkénti karbantartás elvégezve. Motorolajcsere, csapágyak kenése, szenzorok tisztítása.',
          performedBy: 'Nagy Péter',
          performedAt: new Date('2023-07-15T14:15:00'),
          createdAt: new Date('2023-07-15T14:15:00')
        },
        {
          id: '3',
          gateId,
          type: 'component_added',
          title: 'Új szenzor hozzáadása',
          description: 'Biztonsági szenzor telepítése a sín aljára.',
          performedBy: 'Szabó Anna',
          performedAt: new Date('2023-09-10T09:45:00'),
          componentId: '2',
          createdAt: new Date('2023-09-10T09:45:00')
        },
        {
          id: '4',
          gateId,
          type: 'repair',
          title: 'Motor javítás',
          description: 'A főmotor zajossá vált, szénkefe csere szükséges volt.',
          performedBy: 'Kovács János',
          performedAt: new Date('2024-02-20T11:20:00'),
          createdAt: new Date('2024-02-20T11:20:00')
        },
        {
          id: '5',
          gateId,
          type: 'inspection',
          title: 'Biztonsági ellenőrzés',
          description: 'Éves biztonsági ellenőrzés elvégezve. Minden paraméter megfelelő.',
          performedBy: 'Dr. Tóth Ferenc',
          performedAt: new Date('2024-01-15T13:00:00'),
          createdAt: new Date('2024-01-15T13:00:00')
        }
      ]
      
      // Sort by date descending
      mockHistory.sort((a, b) => b.performedAt.getTime() - a.performedAt.getTime())
      setHistoryEntries(mockHistory)
    } catch (error) {
      toast.error('Hiba az előzmények betöltésekor')
      console.error('Load history error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getTypeIcon = (type: GateHistoryType) => {
    switch (type) {
      case 'installation':
        return <Plus className="h-5 w-5 text-green-600" />
      case 'maintenance':
        return <Wrench className="h-5 w-5 text-blue-600" />
      case 'repair':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      case 'inspection':
        return <Eye className="h-5 w-5 text-purple-600" />
      case 'component_added':
        return <Plus className="h-5 w-5 text-green-600" />
      case 'component_removed':
        return <Settings className="h-5 w-5 text-red-600" />
      case 'component_replaced':
        return <Settings className="h-5 w-5 text-yellow-600" />
      default:
        return <FileText className="h-5 w-5 text-gray-600" />
    }
  }

  const getTypeColor = (type: GateHistoryType) => {
    switch (type) {
      case 'installation':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'maintenance':
        return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'repair':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'inspection':
        return 'bg-purple-100 text-purple-800 border-purple-200'
      case 'component_added':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'component_removed':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'component_replaced':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const toggleExpanded = (entryId: string) => {
    const newExpanded = new Set(expandedEntries)
    if (newExpanded.has(entryId)) {
      newExpanded.delete(entryId)
    } else {
      newExpanded.add(entryId)
    }
    setExpandedEntries(newExpanded)
  }

  const formatDateTime = (date: Date) => {
    return date.toLocaleDateString('hu-HU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const filteredEntries = historyEntries.filter(entry => {
    const matchesSearch = entry.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         entry.performedBy.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesType = typeFilter === 'all' || entry.type === typeFilter
    
    return matchesSearch && matchesType
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Előzmények</h2>
          <p className="text-sm text-gray-600 mt-1">
            {historyEntries.length} bejegyzés található
          </p>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Keresés címben, leírásban vagy végrehajtóban..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as GateHistoryType | 'all')}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Minden típus</option>
            {Object.entries(GateHistoryTypeLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* History Timeline */}
      <div className="space-y-4">
        {filteredEntries.map((entry, index) => {
          const isExpanded = expandedEntries.has(entry.id)
          const isLast = index === filteredEntries.length - 1
          
          return (
            <div key={entry.id} className="relative">
              {/* Timeline line */}
              {!isLast && (
                <div className="absolute left-6 top-12 w-0.5 h-full bg-gray-200"></div>
              )}
              
              <div className="flex items-start space-x-4">
                {/* Timeline marker */}
                <div className={`flex-shrink-0 w-12 h-12 rounded-full border-2 flex items-center justify-center bg-white ${getTypeColor(entry.type)}`}>
                  {getTypeIcon(entry.type)}
                </div>
                
                {/* Content */}
                <div className="flex-1 bg-white border border-gray-200 rounded-lg overflow-hidden">
                  <div 
                    className="p-4 cursor-pointer hover:bg-gray-50 transition-colors"
                    onClick={() => toggleExpanded(entry.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3">
                          <h3 className="text-lg font-medium text-gray-900">{entry.title}</h3>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${getTypeColor(entry.type)}`}>
                            {GateHistoryTypeLabels[entry.type]}
                          </span>
                        </div>
                        
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                          <div className="flex items-center space-x-1">
                            <Calendar className="h-4 w-4" />
                            <span>{formatDateTime(entry.performedAt)}</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <User className="h-4 w-4" />
                            <span>{entry.performedBy}</span>
                          </div>
                        </div>
                      </div>
                      
                      <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${
                        isExpanded ? 'rotate-180' : ''
                      }`} />
                    </div>
                  </div>
                  
                  {isExpanded && entry.description && (
                    <div className="border-t border-gray-200 p-4 bg-gray-50">
                      <div className="prose prose-sm max-w-none">
                        <p className="text-gray-700">{entry.description}</p>
                      </div>
                      
                      {entry.componentId && (
                        <div className="mt-3 inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                          <Settings className="h-4 w-4 mr-1" />
                          Komponens ID: {entry.componentId}
                        </div>
                      )}
                      
                      {entry.attachments && entry.attachments.length > 0 && (
                        <div className="mt-3">
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Mellékletek:</h4>
                          <div className="space-y-1">
                            {entry.attachments.map((attachment, idx) => (
                              <a
                                key={idx}
                                href={attachment}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                              >
                                <FileText className="h-4 w-4 mr-1" />
                                Melléklet {idx + 1}
                              </a>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )
        })}
        
        {filteredEntries.length === 0 && (
          <div className="text-center py-12">
            <Clock className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nincsenek előzmények</h3>
            <p className="text-gray-600">
              {searchTerm || typeFilter !== 'all' 
                ? 'Nincs a szűrési feltételeknek megfelelő bejegyzés'
                : 'Még nincsenek rögzített előzmények ehhez a kapuhoz'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  )
}