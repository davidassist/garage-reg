'use client'

import { useState, useEffect } from 'react'
import { toast } from 'react-hot-toast'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import {
  Plus,
  Edit2,
  Trash2,
  Save,
  X,
  Settings,
  Calendar,
  MapPin,
  AlertTriangle,
  CheckCircle,
  Search,
  Filter
} from 'lucide-react'
import {
  GateComponent,
  GateComponentFormData,
  GateComponentFormSchema,
  GateComponentType,
  GateComponentStatus,
  GateComponentTypeLabels,
  GateComponentStatusLabels
} from '@/lib/types/gate-detail'

interface ComponentsTabProps {
  gateId: string
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

interface ComponentFormProps {
  component?: GateComponent
  onSave: (data: GateComponentFormData) => Promise<void>
  onCancel: () => void
  isInline?: boolean
}

function ComponentForm({ component, onSave, onCancel, isInline = false }: ComponentFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset
  } = useForm<GateComponentFormData>({
    resolver: zodResolver(GateComponentFormSchema),
    defaultValues: component ? {
      name: component.name,
      type: component.type,
      manufacturer: component.manufacturer,
      model: component.model,
      serialNumber: component.serialNumber,
      installationDate: component.installationDate?.toISOString().split('T')[0],
      warrantyExpiry: component.warrantyExpiry?.toISOString().split('T')[0],
      status: component.status,
      location: component.location,
      notes: component.notes
    } : {
      status: 'active' as GateComponentStatus
    }
  })

  const onSubmit = async (data: GateComponentFormData) => {
    try {
      await onSave(data)
      if (!component) {
        reset()
      }
    } catch (error) {
      console.error('Component save error:', error)
    }
  }

  const formClass = isInline 
    ? "bg-blue-50 border border-blue-200 rounded-lg p-4"
    : "bg-white border border-gray-200 rounded-lg p-6"

  return (
    <form onSubmit={handleSubmit(onSubmit)} className={formClass}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Komponens neve *
          </label>
          <input
            {...register('name')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="pl. Főmotor"
          />
          {errors.name && (
            <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Típus *
          </label>
          <select
            {...register('type')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Válasszon típust</option>
            {Object.entries(GateComponentTypeLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
          {errors.type && (
            <p className="mt-1 text-sm text-red-600">{errors.type.message}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Gyártó
          </label>
          <input
            {...register('manufacturer')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="pl. CAME"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Modell
          </label>
          <input
            {...register('model')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="pl. BK-1200"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Sorozatszám
          </label>
          <input
            {...register('serialNumber')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="pl. SN123456"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Státusz
          </label>
          <select
            {...register('status')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {Object.entries(GateComponentStatusLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Telepítés dátuma
          </label>
          <input
            {...register('installationDate')}
            type="date"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Garancia lejárata
          </label>
          <input
            {...register('warrantyExpiry')}
            type="date"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Helyszín
          </label>
          <input
            {...register('location')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="pl. Bal oldali motor"
          />
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Megjegyzések
          </label>
          <textarea
            {...register('notes')}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="További megjegyzések..."
          />
        </div>
      </div>

      <div className="flex justify-end space-x-3 mt-4">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
        >
          <X className="h-4 w-4 mr-2 inline" />
          Mégse
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <Save className="h-4 w-4 mr-2 inline" />
          {isSubmitting ? 'Mentés...' : 'Mentés'}
        </button>
      </div>
    </form>
  )
}

export function ComponentsTab({ gateId, isLoading, setIsLoading }: ComponentsTabProps) {
  const [components, setComponents] = useState<GateComponent[]>([])
  const [showAddForm, setShowAddForm] = useState(false)
  const [editingComponent, setEditingComponent] = useState<GateComponent | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<GateComponentStatus | 'all'>('all')

  useEffect(() => {
    loadComponents()
  }, [gateId])

  const loadComponents = async () => {
    try {
      setIsLoading(true)
      
      // Mock data - replace with actual API call
      const mockComponents: GateComponent[] = [
        {
          id: '1',
          gateId,
          name: 'Főmotor',
          type: 'motor',
          manufacturer: 'CAME',
          model: 'BK-1200',
          serialNumber: 'SN123456',
          status: 'active',
          location: 'Bal oldali motor',
          installationDate: new Date('2023-01-15'),
          warrantyExpiry: new Date('2025-01-15'),
          createdAt: new Date(),
          updatedAt: new Date()
        },
        {
          id: '2',
          gateId,
          name: 'Biztonsági szenzor',
          type: 'sensor',
          manufacturer: 'NICE',
          model: 'EPMB',
          serialNumber: 'SN654321',
          status: 'active',
          location: 'Alsó sínek',
          installationDate: new Date('2023-01-15'),
          createdAt: new Date(),
          updatedAt: new Date()
        }
      ]
      
      setComponents(mockComponents)
    } catch (error) {
      toast.error('Hiba a komponensek betöltésekor')
      console.error('Load components error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSaveComponent = async (data: GateComponentFormData) => {
    try {
      setIsLoading(true)
      
      if (editingComponent) {
        // Update existing component
        const updatedComponent: GateComponent = {
          ...editingComponent,
          ...data,
          installationDate: data.installationDate ? new Date(data.installationDate) : undefined,
          warrantyExpiry: data.warrantyExpiry ? new Date(data.warrantyExpiry) : undefined,
          updatedAt: new Date()
        }
        
        setComponents(prev => 
          prev.map(comp => comp.id === editingComponent.id ? updatedComponent : comp)
        )
        setEditingComponent(null)
        toast.success('Komponens sikeresen frissítve')
      } else {
        // Add new component
        const newComponent: GateComponent = {
          id: `new-${Date.now()}`,
          gateId,
          ...data,
          installationDate: data.installationDate ? new Date(data.installationDate) : undefined,
          warrantyExpiry: data.warrantyExpiry ? new Date(data.warrantyExpiry) : undefined,
          createdAt: new Date(),
          updatedAt: new Date()
        }
        
        setComponents(prev => [...prev, newComponent])
        setShowAddForm(false)
        toast.success('Komponens sikeresen hozzáadva')
      }
    } catch (error) {
      toast.error('Hiba a komponens mentésekor')
      console.error('Save component error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteComponent = async (componentId: string) => {
    if (!confirm('Biztosan törli ezt a komponenst?')) return
    
    try {
      setIsLoading(true)
      setComponents(prev => prev.filter(comp => comp.id !== componentId))
      toast.success('Komponens törölve')
    } catch (error) {
      toast.error('Hiba a komponens törlésekor')
      console.error('Delete component error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getStatusIcon = (status: GateComponentStatus) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'maintenance':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      default:
        return <Settings className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = (status: GateComponentStatus) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'inactive':
        return 'bg-gray-100 text-gray-800'
      case 'maintenance':
        return 'bg-yellow-100 text-yellow-800'
      case 'replaced':
        return 'bg-blue-100 text-blue-800'
      case 'removed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const filteredComponents = components.filter(component => {
    const matchesSearch = component.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         component.manufacturer?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         component.model?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = statusFilter === 'all' || component.status === statusFilter
    
    return matchesSearch && matchesStatus
  })

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Komponensek</h2>
          <p className="text-sm text-gray-600 mt-1">
            {components.length} komponens található
          </p>
        </div>
        
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <Plus className="h-4 w-4 mr-2" />
          Komponens hozzáadása
        </button>
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
              placeholder="Keresés komponens név, gyártó vagy modell alapján..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as GateComponentStatus | 'all')}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Minden státusz</option>
            {Object.entries(GateComponentStatusLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Add Component Form */}
      {showAddForm && (
        <ComponentForm
          onSave={handleSaveComponent}
          onCancel={() => setShowAddForm(false)}
          isInline
        />
      )}

      {/* Components List */}
      <div className="space-y-4">
        {filteredComponents.map((component) => (
          <div key={component.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            {editingComponent?.id === component.id ? (
              <ComponentForm
                component={component}
                onSave={handleSaveComponent}
                onCancel={() => setEditingComponent(null)}
              />
            ) : (
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(component.status)}
                      <h3 className="text-lg font-medium text-gray-900">{component.name}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(component.status)}`}>
                        {GateComponentStatusLabels[component.status]}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
                      <div>
                        <label className="text-sm font-medium text-gray-500">Típus</label>
                        <p className="text-gray-900">{GateComponentTypeLabels[component.type]}</p>
                      </div>
                      
                      {component.manufacturer && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Gyártó</label>
                          <p className="text-gray-900">{component.manufacturer}</p>
                        </div>
                      )}
                      
                      {component.model && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Modell</label>
                          <p className="text-gray-900">{component.model}</p>
                        </div>
                      )}
                      
                      {component.serialNumber && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Sorozatszám</label>
                          <p className="text-gray-900">{component.serialNumber}</p>
                        </div>
                      )}
                      
                      {component.location && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Helyszín</label>
                          <div className="flex items-center space-x-1">
                            <MapPin className="h-4 w-4 text-gray-400" />
                            <p className="text-gray-900">{component.location}</p>
                          </div>
                        </div>
                      )}
                      
                      {component.installationDate && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Telepítés</label>
                          <div className="flex items-center space-x-1">
                            <Calendar className="h-4 w-4 text-gray-400" />
                            <p className="text-gray-900">
                              {component.installationDate.toLocaleDateString('hu-HU')}
                            </p>
                          </div>
                        </div>
                      )}
                      
                      {component.warrantyExpiry && (
                        <div>
                          <label className="text-sm font-medium text-gray-500">Garancia lejárat</label>
                          <p className="text-gray-900">
                            {component.warrantyExpiry.toLocaleDateString('hu-HU')}
                          </p>
                        </div>
                      )}
                    </div>
                    
                    {component.notes && (
                      <div className="mt-4">
                        <label className="text-sm font-medium text-gray-500">Megjegyzések</label>
                        <p className="text-gray-700 mt-1">{component.notes}</p>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button
                      onClick={() => setEditingComponent(component)}
                      disabled={isLoading}
                      className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors disabled:opacity-50"
                      title="Szerkesztés"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteComponent(component.id)}
                      disabled={isLoading}
                      className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-md transition-colors disabled:opacity-50"
                      title="Törlés"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
        
        {filteredComponents.length === 0 && (
          <div className="text-center py-12">
            <Settings className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nincsenek komponensek</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || statusFilter !== 'all' 
                ? 'Nincs a szűrési feltételeknek megfelelő komponens'
                : 'Még nincsenek hozzáadott komponensek ehhez a kapuhoz'
              }
            </p>
            {!searchTerm && statusFilter === 'all' && (
              <button
                onClick={() => setShowAddForm(true)}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Első komponens hozzáadása
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}