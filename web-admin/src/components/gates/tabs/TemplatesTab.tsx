'use client'

import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import {
  CheckSquare,
  Plus,
  Search,
  Filter,
  Clock,
  Calendar,
  User,
  Edit3,
  Trash2,
  Play,
  Copy,
  FileText,
  AlertCircle,
  CheckCircle2,
  X
} from 'lucide-react'
import {
  InspectionTemplate,
  InspectionStatus,
  InspectionStatusLabels,
  InspectionFrequency,
  InspectionFrequencyLabels
} from '@/lib/types/gate-detail'

interface TemplatesTabProps {
  gateId: string
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function TemplatesTab({ gateId, isLoading, setIsLoading }: TemplatesTabProps) {
  const [templates, setTemplates] = useState<InspectionTemplate[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<InspectionStatus | 'all'>('all')
  const [frequencyFilter, setFrequencyFilter] = useState<InspectionFrequency | 'all'>('all')
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<string | null>(null)
  const [expandedTemplate, setExpandedTemplate] = useState<string | null>(null)

  useEffect(() => {
    loadTemplates()
  }, [gateId])

  const loadTemplates = async () => {
    try {
      setIsLoading(true)
      
      // Mock data - replace with actual API call
      const mockTemplates: InspectionTemplate[] = [
        {
          id: '1',
          gateId,
          name: 'Havi biztonsági ellenőrzés',
          description: 'Teljes körű biztonsági és működési ellenőrzés minden hónap végén',
          frequency: 'monthly',
          estimatedDuration: 45,
          assignedTo: 'Kovács János',
          status: 'active',
          createdAt: new Date('2023-01-10T08:00:00'),
          updatedAt: new Date('2023-12-15T14:30:00'),
          lastInspectionDate: new Date('2023-12-31T16:00:00'),
          nextInspectionDate: new Date('2024-01-31T16:00:00'),
          checklistItems: [
            {
              id: 'item1',
              title: 'Motor működésének ellenőrzése',
              description: 'A motor zajtalanul működik, nincs szokatlan rezgés',
              required: true,
              category: 'mechanical'
            },
            {
              id: 'item2', 
              title: 'Távvezérlő tesztelése',
              description: 'Minden gomb megfelelően működik, hatótáv megfelelő',
              required: true,
              category: 'electrical'
            },
            {
              id: 'item3',
              title: 'Biztonsági érzékelők tesztelése',
              description: 'Fotocelláк és nyomásérzékelők helyes működése',
              required: true,
              category: 'safety'
            },
            {
              id: 'item4',
              title: 'Kenőanyag szintjének ellenőrzése',
              description: 'Mechanikus alkatrészek kenőanyag szintje megfelelő',
              required: false,
              category: 'maintenance'
            },
            {
              id: 'item5',
              title: 'Vezetékek és csatlakozások vizsgálata',
              description: 'Nincs látható sérülés vagy kopás a kábeleken',
              required: true,
              category: 'electrical'
            }
          ]
        },
        {
          id: '2',
          gateId,
          name: 'Éves részletes karbantartás',
          description: 'Teljes körű éves karbantartás és alkatrész csere',
          frequency: 'yearly',
          estimatedDuration: 120,
          assignedTo: 'Dr. Tóth Ferenc',
          status: 'active',
          createdAt: new Date('2023-01-10T08:00:00'),
          updatedAt: new Date('2023-11-20T10:00:00'),
          lastInspectionDate: new Date('2023-01-15T09:00:00'),
          nextInspectionDate: new Date('2024-01-15T09:00:00'),
          checklistItems: [
            {
              id: 'annual1',
              title: 'Motor szerviz',
              description: 'Teljes motor átvizsgálás, olajcsere, szűrőcsere',
              required: true,
              category: 'mechanical'
            },
            {
              id: 'annual2',
              title: 'Elektromos rendszer audit',
              description: 'Minden elektromos komponens részletes tesztelése',
              required: true,
              category: 'electrical'
            },
            {
              id: 'annual3',
              title: 'Szerkezeti elemek cseréje',
              description: 'Kopott alkatrészek cseréje, csavarok meghúzása',
              required: true,
              category: 'mechanical'
            }
          ]
        },
        {
          id: '3',
          gateId,
          name: 'Heti gyors ellenőrzés',
          description: 'Gyors működési teszt minden héten',
          frequency: 'weekly',
          estimatedDuration: 15,
          assignedTo: 'Szabó Anna',
          status: 'paused',
          createdAt: new Date('2023-03-01T10:00:00'),
          updatedAt: new Date('2023-12-01T12:00:00'),
          lastInspectionDate: new Date('2023-11-28T14:00:00'),
          nextInspectionDate: new Date('2024-01-02T14:00:00'),
          checklistItems: [
            {
              id: 'weekly1',
              title: 'Nyitás/zárás teszt',
              description: 'Kapu 3x nyitás és zárás, gördülékeny működés',
              required: true,
              category: 'mechanical'
            },
            {
              id: 'weekly2',
              title: 'Biztonsági funkciók',
              description: 'Vészleállítás és akadályérzékelés tesztelése',
              required: true,
              category: 'safety'
            }
          ]
        }
      ]
      
      // Sort by next inspection date
      mockTemplates.sort((a, b) => {
        if (!a.nextInspectionDate && !b.nextInspectionDate) return 0
        if (!a.nextInspectionDate) return 1
        if (!b.nextInspectionDate) return -1
        return a.nextInspectionDate.getTime() - b.nextInspectionDate.getTime()
      })
      
      setTemplates(mockTemplates)
    } catch (error) {
      toast.error('Hiba a sablonok betöltésekor')
      console.error('Load templates error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: InspectionStatus) => {
    switch (status) {
      case 'active':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />
      case 'paused':
        return <Clock className="h-5 w-5 text-yellow-600" />
      case 'archived':
        return <X className="h-5 w-5 text-gray-600" />
      default:
        return <AlertCircle className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusBadgeColor = (status: InspectionStatus) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800'
      case 'archived':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getUrgencyColor = (nextDate?: Date) => {
    if (!nextDate) return 'text-gray-600'
    
    const now = new Date()
    const diffDays = Math.ceil((nextDate.getTime() - now.getTime()) / (1000 * 60 * 60 * 24))
    
    if (diffDays < 0) return 'text-red-600' // Overdue
    if (diffDays <= 3) return 'text-orange-600' // Due soon
    if (diffDays <= 7) return 'text-yellow-600' // Due this week
    return 'text-green-600' // On schedule
  }

  const handleStartInspection = async (templateId: string, templateName: string) => {
    try {
      setIsLoading(true)
      
      // In a real app, this would create a new inspection record
      toast.success(`Ellenőrzés megkezdve: ${templateName}`)
      
      // Update last inspection date
      setTemplates(prev => prev.map(template => {
        if (template.id === templateId) {
          const now = new Date()
          const nextDate = new Date(now)
          
          // Calculate next inspection date based on frequency
          switch (template.frequency) {
            case 'daily':
              nextDate.setDate(now.getDate() + 1)
              break
            case 'weekly':
              nextDate.setDate(now.getDate() + 7)
              break
            case 'monthly':
              nextDate.setMonth(now.getMonth() + 1)
              break
            case 'quarterly':
              nextDate.setMonth(now.getMonth() + 3)
              break
            case 'yearly':
              nextDate.setFullYear(now.getFullYear() + 1)
              break
            case 'on_demand':
            default:
              // No automatic scheduling for on-demand
              break
          }
          
          return {
            ...template,
            lastInspectionDate: now,
            nextInspectionDate: template.frequency === 'on_demand' ? undefined : nextDate
          }
        }
        return template
      }))
      
    } catch (error) {
      toast.error('Hiba az ellenőrzés indításakor')
      console.error('Start inspection error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteTemplate = async (templateId: string, templateName: string) => {
    if (!confirm(`Biztosan törli a "${templateName}" sablont?`)) return
    
    try {
      setIsLoading(true)
      setTemplates(prev => prev.filter(template => template.id !== templateId))
      toast.success('Sablon törölve')
    } catch (error) {
      toast.error('Hiba a sablon törlésekor')
      console.error('Delete template error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDuplicateTemplate = async (template: InspectionTemplate) => {
    try {
      setIsLoading(true)
      
      const duplicatedTemplate: InspectionTemplate = {
        ...template,
        id: `new-${Date.now()}`,
        name: `${template.name} (másolat)`,
        createdAt: new Date(),
        updatedAt: new Date(),
        lastInspectionDate: undefined,
        nextInspectionDate: undefined
      }
      
      setTemplates(prev => [duplicatedTemplate, ...prev])
      toast.success('Sablon lemásolva')
    } catch (error) {
      toast.error('Hiba a sablon másolásakor')
      console.error('Duplicate template error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.assignedTo?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || template.status === statusFilter
    const matchesFrequency = frequencyFilter === 'all' || template.frequency === frequencyFilter
    
    return matchesSearch && matchesStatus && matchesFrequency
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Ellenőrzési sablonok</h2>
          <p className="text-sm text-gray-600 mt-1">
            {templates.length} sablon, {templates.filter(t => t.status === 'active').length} aktív
          </p>
        </div>
        
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <Plus className="h-4 w-4 mr-2" />
          Új sablon létrehozása
        </button>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col lg:flex-row space-y-4 lg:space-y-0 lg:space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Keresés név, leírás vagy felelős alapján..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="h-4 w-4 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as InspectionStatus | 'all')}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Minden állapot</option>
              {Object.entries(InspectionStatusLabels).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center space-x-2">
            <Clock className="h-4 w-4 text-gray-400" />
            <select
              value={frequencyFilter}
              onChange={(e) => setFrequencyFilter(e.target.value as InspectionFrequency | 'all')}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">Minden gyakoriság</option>
              {Object.entries(InspectionFrequencyLabels).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Új ellenőrzési sablon</h3>
            <button
              onClick={() => setShowCreateForm(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sablon neve
              </label>
              <input
                type="text"
                placeholder="pl. Havi biztonsági ellenőrzés"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Gyakoriság
              </label>
              <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                {Object.entries(InspectionFrequencyLabels).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Becsült időtartam (perc)
              </label>
              <input
                type="number"
                placeholder="30"
                min="5"
                max="480"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Felelős
              </label>
              <input
                type="text"
                placeholder="Válasszon felelőst"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Leírás
              </label>
              <textarea
                rows={3}
                placeholder="Részletes leírás az ellenőrzésről..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={() => setShowCreateForm(false)}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Mégse
            </button>
            <button
              onClick={() => {
                toast.success('Sablon létrehozva')
                setShowCreateForm(false)
              }}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
            >
              Sablon létrehozása
            </button>
          </div>
        </div>
      )}

      {/* Templates List */}
      <div className="space-y-4">
        {filteredTemplates.map((template) => (
          <div key={template.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    {getStatusIcon(template.status)}
                    <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeColor(template.status)}`}>
                      {InspectionStatusLabels[template.status]}
                    </span>
                  </div>
                  
                  {template.description && (
                    <p className="text-gray-600 text-sm mb-3">{template.description}</p>
                  )}
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">
                        {InspectionFrequencyLabels[template.frequency]}
                      </span>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      <span className="text-gray-600">
                        {template.estimatedDuration} perc
                      </span>
                    </div>
                    
                    {template.assignedTo && (
                      <div className="flex items-center space-x-2">
                        <User className="h-4 w-4 text-gray-400" />
                        <span className="text-gray-600">{template.assignedTo}</span>
                      </div>
                    )}
                    
                    {template.nextInspectionDate && (
                      <div className="flex items-center space-x-2">
                        <AlertCircle className="h-4 w-4 text-gray-400" />
                        <span className={getUrgencyColor(template.nextInspectionDate)}>
                          {template.nextInspectionDate.toLocaleDateString('hu-HU')}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  {template.status === 'active' && (
                    <button
                      onClick={() => handleStartInspection(template.id, template.name)}
                      disabled={isLoading}
                      className="p-2 text-green-600 hover:text-green-700 hover:bg-green-50 rounded-md disabled:opacity-50"
                      title="Ellenőrzés indítása"
                    >
                      <Play className="h-4 w-4" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => setExpandedTemplate(expandedTemplate === template.id ? null : template.id)}
                    className="p-2 text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-md"
                    title="Részletek megjelenítése"
                  >
                    <FileText className="h-4 w-4" />
                  </button>
                  
                  <button
                    onClick={() => handleDuplicateTemplate(template)}
                    disabled={isLoading}
                    className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-md disabled:opacity-50"
                    title="Sablon másolása"
                  >
                    <Copy className="h-4 w-4" />
                  </button>
                  
                  <button
                    onClick={() => setEditingTemplate(template.id)}
                    disabled={isLoading}
                    className="p-2 text-gray-600 hover:text-gray-700 hover:bg-gray-50 rounded-md disabled:opacity-50"
                    title="Szerkesztés"
                  >
                    <Edit3 className="h-4 w-4" />
                  </button>
                  
                  <button
                    onClick={() => handleDeleteTemplate(template.id, template.name)}
                    disabled={isLoading}
                    className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-md disabled:opacity-50"
                    title="Törlés"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              {/* Expanded Details */}
              {expandedTemplate === template.id && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h4 className="text-sm font-medium text-gray-900 mb-4">
                    Ellenőrzési pontok ({template.checklistItems.length})
                  </h4>
                  
                  <div className="space-y-3">
                    {template.checklistItems.map((item) => (
                      <div key={item.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-md">
                        <CheckSquare className={`h-4 w-4 mt-1 ${item.required ? 'text-red-600' : 'text-gray-400'}`} />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <h5 className="text-sm font-medium text-gray-900">{item.title}</h5>
                            {item.required && (
                              <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs bg-red-100 text-red-800">
                                Kötelező
                              </span>
                            )}
                          </div>
                          {item.description && (
                            <p className="text-xs text-gray-600">{item.description}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-600">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <span className="font-medium">Létrehozva:</span> {template.createdAt.toLocaleDateString('hu-HU')}
                      </div>
                      <div>
                        <span className="font-medium">Utolsó módosítás:</span> {template.updatedAt.toLocaleDateString('hu-HU')}
                      </div>
                      {template.lastInspectionDate && (
                        <div>
                          <span className="font-medium">Utolsó ellenőrzés:</span> {template.lastInspectionDate.toLocaleDateString('hu-HU')}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {filteredTemplates.length === 0 && (
          <div className="text-center py-12">
            <CheckSquare className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nincsenek sablonok</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || statusFilter !== 'all' || frequencyFilter !== 'all'
                ? 'Nincs a szűrési feltételeknek megfelelő sablon'
                : 'Még nincsenek létrehozva ellenőrzési sablonok ehhez a kapuhoz'
              }
            </p>
            {!searchTerm && statusFilter === 'all' && frequencyFilter === 'all' && (
              <button
                onClick={() => setShowCreateForm(true)}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Első sablon létrehozása
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}