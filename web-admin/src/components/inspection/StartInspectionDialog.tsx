'use client'

import React, { useState, useEffect } from 'react'
import { 
  Search, 
  Filter, 
  Clock, 
  User, 
  MapPin, 
  Calendar,
  AlertTriangle,
  CheckCircle,
  X,
  Play,
  FileText,
  Settings
} from 'lucide-react'
import { 
  InspectionTemplate, 
  StartInspectionRequest, 
  INSPECTION_CATEGORIES,
  PRIORITY_CONFIGS 
} from '@/lib/types/inspection'

interface StartInspectionDialogProps {
  isOpen: boolean
  onClose: () => void
  onStart: (request: StartInspectionRequest) => void
  templates: InspectionTemplate[]
  gates?: Array<{ id: string; name: string; location?: string }>
  garages?: Array<{ id: string; name: string; address?: string }>
  users?: Array<{ id: string; name: string; role?: string }>
}

interface TemplateFilters {
  category: string
  search: string
  minDuration: number
  maxDuration: number
  sortBy: 'name' | 'duration' | 'category' | 'recent'
}

export function StartInspectionDialog({
  isOpen,
  onClose,
  onStart,
  templates,
  gates = [],
  garages = [],
  users = []
}: StartInspectionDialogProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<InspectionTemplate | null>(null)
  const [formData, setFormData] = useState<Partial<StartInspectionRequest>>({
    title: '',
    description: '',
    priority: 'normal',
    autoSaveEnabled: true
  })
  const [filters, setFilters] = useState<TemplateFilters>({
    category: 'all',
    search: '',
    minDuration: 0,
    maxDuration: 240,
    sortBy: 'name'
  })
  const [step, setStep] = useState<'template' | 'details'>('template')
  const [errors, setErrors] = useState<Record<string, string>>({})

  // Reset state when dialog opens
  useEffect(() => {
    if (isOpen) {
      setSelectedTemplate(null)
      setFormData({
        title: '',
        description: '',
        priority: 'normal',
        autoSaveEnabled: true
      })
      setStep('template')
      setErrors({})
    }
  }, [isOpen])

  // Update title when template is selected
  useEffect(() => {
    if (selectedTemplate && !formData.title) {
      const now = new Date()
      const dateStr = now.toLocaleDateString('hu-HU')
      const timeStr = now.toLocaleTimeString('hu-HU', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
      
      setFormData(prev => ({
        ...prev,
        templateId: selectedTemplate.id,
        title: `${selectedTemplate.name} - ${dateStr} ${timeStr}`
      }))
    }
  }, [selectedTemplate, formData.title])

  // Filter templates
  const filteredTemplates = templates.filter(template => {
    const matchesCategory = filters.category === 'all' || template.category === filters.category
    const matchesSearch = !filters.search || 
      template.name.toLowerCase().includes(filters.search.toLowerCase()) ||
      template.description?.toLowerCase().includes(filters.search.toLowerCase())
    const matchesDuration = template.estimatedDuration >= filters.minDuration && 
                           template.estimatedDuration <= filters.maxDuration
    
    return matchesCategory && matchesSearch && matchesDuration && template.isActive
  }).sort((a, b) => {
    switch (filters.sortBy) {
      case 'duration':
        return a.estimatedDuration - b.estimatedDuration
      case 'category':
        return a.category.localeCompare(b.category)
      case 'recent':
        return b.updatedAt.getTime() - a.updatedAt.getTime()
      default:
        return a.name.localeCompare(b.name)
    }
  })

  const handleTemplateSelect = (template: InspectionTemplate) => {
    setSelectedTemplate(template)
    setStep('details')
  }

  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {}
    
    if (!formData.title?.trim()) {
      newErrors.title = 'Az ellenőrzés címe kötelező'
    }
    
    if (!selectedTemplate) {
      newErrors.template = 'Válassz egy sablont'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleStart = () => {
    if (validateForm() && selectedTemplate) {
      const request: StartInspectionRequest = {
        templateId: selectedTemplate.id,
        title: formData.title!,
        description: formData.description,
        assignedTo: formData.assignedTo,
        gateId: formData.gateId,
        garageId: formData.garageId,
        dueDate: formData.dueDate,
        priority: formData.priority || 'normal',
        autoSaveEnabled: formData.autoSaveEnabled ?? true
      }
      
      onStart(request)
      onClose()
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <Play className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Új Ellenőrzés Indítása
              </h2>
              <p className="text-sm text-gray-500">
                {step === 'template' ? 'Válassz sablont' : 'Add meg a részleteket'}
              </p>
            </div>
          </div>
          
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Progress Steps */}
        <div className="px-6 py-3 bg-gray-50 border-b">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 ${
              step === 'template' ? 'text-blue-600' : 'text-green-600'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                step === 'template' ? 'bg-blue-100' : 'bg-green-100'
              }`}>
                {step === 'template' ? '1' : '✓'}
              </div>
              <span className="text-sm font-medium">Sablon választás</span>
            </div>
            
            <div className="flex-1 h-0.5 bg-gray-200">
              <div className={`h-full transition-all duration-300 ${
                step === 'details' ? 'bg-blue-600 w-full' : 'bg-gray-200 w-0'
              }`} />
            </div>
            
            <div className={`flex items-center space-x-2 ${
              step === 'details' ? 'text-blue-600' : 'text-gray-400'
            }`}>
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium ${
                step === 'details' ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                2
              </div>
              <span className="text-sm font-medium">Részletek</span>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto" style={{ maxHeight: 'calc(90vh - 200px)' }}>
          {step === 'template' ? (
            <TemplateSelection
              templates={filteredTemplates}
              filters={filters}
              onFiltersChange={setFilters}
              selectedTemplate={selectedTemplate}
              onTemplateSelect={handleTemplateSelect}
            />
          ) : (
            <InspectionDetails
              template={selectedTemplate!}
              formData={formData}
              onFormChange={handleFormChange}
              errors={errors}
              gates={gates}
              garages={garages}
              users={users}
            />
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t bg-gray-50 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {step === 'details' && (
              <button
                onClick={() => setStep('template')}
                className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 
                         transition-colors"
              >
                ← Vissza
              </button>
            )}
            
            {selectedTemplate && (
              <div className="text-sm text-gray-500">
                Kiválasztva: <span className="font-medium">{selectedTemplate.name}</span>
                {' • '}
                <span className="text-gray-400">~{selectedTemplate.estimatedDuration} perc</span>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white 
                       border border-gray-300 rounded-md hover:bg-gray-50 
                       transition-colors"
            >
              Mégsem
            </button>
            
            {step === 'template' ? (
              <button
                onClick={() => selectedTemplate && setStep('details')}
                disabled={!selectedTemplate}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  selectedTemplate
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Tovább →
              </button>
            ) : (
              <button
                onClick={handleStart}
                className="px-6 py-2 text-sm font-medium bg-green-600 text-white 
                         rounded-md hover:bg-green-700 transition-colors
                         flex items-center space-x-2"
              >
                <Play className="w-4 h-4" />
                <span>Ellenőrzés Indítása</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

// Template Selection Component
interface TemplateSelectionProps {
  templates: InspectionTemplate[]
  filters: TemplateFilters
  onFiltersChange: (filters: TemplateFilters) => void
  selectedTemplate: InspectionTemplate | null
  onTemplateSelect: (template: InspectionTemplate) => void
}

function TemplateSelection({
  templates,
  filters,
  onFiltersChange,
  selectedTemplate,
  onTemplateSelect
}: TemplateSelectionProps) {
  return (
    <div className="p-6 space-y-6">
      {/* Filters */}
      <div className="space-y-4">
        <div className="flex items-center space-x-4">
          {/* Search */}
          <div className="flex-1 relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Keresés sablonok között..."
              value={filters.search}
              onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Category Filter */}
          <select
            value={filters.category}
            onChange={(e) => onFiltersChange({ ...filters, category: e.target.value })}
            className="px-3 py-2 border border-gray-300 rounded-md 
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="all">Minden kategória</option>
            {Object.entries(INSPECTION_CATEGORIES).map(([key, category]) => (
              <option key={key} value={key}>
                {category.icon} {category.label}
              </option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={filters.sortBy}
            onChange={(e) => onFiltersChange({ ...filters, sortBy: e.target.value as any })}
            className="px-3 py-2 border border-gray-300 rounded-md 
                     focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="name">Név szerint</option>
            <option value="duration">Időtartam szerint</option>
            <option value="category">Kategória szerint</option>
            <option value="recent">Frissítés szerint</option>
          </select>
        </div>

        {/* Duration Range */}
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-700">Időtartam:</span>
          <div className="flex items-center space-x-2">
            <input
              type="range"
              min="0"
              max="240"
              value={filters.maxDuration}
              onChange={(e) => onFiltersChange({ 
                ...filters, 
                maxDuration: parseInt(e.target.value) 
              })}
              className="w-32"
            />
            <span className="text-sm text-gray-500 min-w-[80px]">
              Max {filters.maxDuration} perc
            </span>
          </div>
        </div>
      </div>

      {/* Templates Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {templates.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Nincsenek a szűrésnek megfelelő sablonok</p>
          </div>
        ) : (
          templates.map(template => (
            <TemplateCard
              key={template.id}
              template={template}
              isSelected={selectedTemplate?.id === template.id}
              onSelect={onTemplateSelect}
            />
          ))
        )}
      </div>
    </div>
  )
}

// Template Card Component
interface TemplateCardProps {
  template: InspectionTemplate
  isSelected: boolean
  onSelect: (template: InspectionTemplate) => void
}

function TemplateCard({ template, isSelected, onSelect }: TemplateCardProps) {
  const category = INSPECTION_CATEGORIES[template.category]
  
  return (
    <div
      onClick={() => onSelect(template)}
      className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
        isSelected 
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-200' 
          : 'border-gray-200 hover:border-gray-300'
      }`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg ${
          isSelected ? 'bg-blue-100' : `bg-${category.color}-100`
        }`}>
          {category.icon}
        </div>
        
        {isSelected && (
          <CheckCircle className="w-5 h-5 text-blue-600" />
        )}
      </div>

      {/* Content */}
      <div className="space-y-2">
        <h3 className="font-medium text-gray-900 text-sm line-clamp-2">
          {template.name}
        </h3>
        
        {template.description && (
          <p className="text-xs text-gray-600 line-clamp-2">
            {template.description}
          </p>
        )}
        
        <div className="flex items-center justify-between text-xs text-gray-500">
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3" />
            <span>~{template.estimatedDuration} perc</span>
          </div>
          
          <div className="flex items-center space-x-1">
            <span>{template.fields.length} mező</span>
          </div>
        </div>
        
        <div className={`text-xs px-2 py-1 rounded-full inline-block bg-${category.color}-100 text-${category.color}-700`}>
          {category.label}
        </div>
      </div>
    </div>
  )
}

// Inspection Details Component
interface InspectionDetailsProps {
  template: InspectionTemplate
  formData: Partial<StartInspectionRequest>
  onFormChange: (field: string, value: any) => void
  errors: Record<string, string>
  gates: Array<{ id: string; name: string; location?: string }>
  garages: Array<{ id: string; name: string; address?: string }>
  users: Array<{ id: string; name: string; role?: string }>
}

function InspectionDetails({
  template,
  formData,
  onFormChange,
  errors,
  gates,
  garages,
  users
}: InspectionDetailsProps) {
  const category = INSPECTION_CATEGORIES[template.category]
  
  return (
    <div className="p-6 space-y-6">
      {/* Template Info */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <div className="flex items-start space-x-3">
          <div className={`w-10 h-10 bg-${category.color}-100 rounded-lg flex items-center justify-center text-lg`}>
            {category.icon}
          </div>
          
          <div className="flex-1">
            <h3 className="font-medium text-gray-900">{template.name}</h3>
            <p className="text-sm text-gray-600 mt-1">{template.description}</p>
            
            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
              <span className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>~{template.estimatedDuration} perc</span>
              </span>
              <span>{template.fields.length} mező</span>
              <span className={`px-2 py-1 rounded-full bg-${category.color}-100 text-${category.color}-700`}>
                {category.label}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Form Fields */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ellenőrzés címe *
            </label>
            <input
              type="text"
              value={formData.title || ''}
              onChange={(e) => onFormChange('title', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Add meg az ellenőrzés címét"
            />
            {errors.title && (
              <p className="text-xs text-red-600 mt-1">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Leírás
            </label>
            <textarea
              value={formData.description || ''}
              onChange={(e) => onFormChange('description', e.target.value)}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Opcionális leírás vagy megjegyzések"
            />
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Prioritás
            </label>
            <select
              value={formData.priority || 'normal'}
              onChange={(e) => onFormChange('priority', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {Object.entries(PRIORITY_CONFIGS).map(([key, priority]) => (
                <option key={key} value={key}>
                  {priority.icon} {priority.label} - {priority.description}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-4">
          {/* Assigned To */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Felelős személy
            </label>
            <select
              value={formData.assignedTo || ''}
              onChange={(e) => onFormChange('assignedTo', e.target.value || undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Nincs hozzárendelve</option>
              {users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.name} {user.role && `(${user.role})`}
                </option>
              ))}
            </select>
          </div>

          {/* Gate */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kapcsolódó kapu
            </label>
            <select
              value={formData.gateId || ''}
              onChange={(e) => onFormChange('gateId', e.target.value || undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Nincs kiválasztva</option>
              {gates.map(gate => (
                <option key={gate.id} value={gate.id}>
                  {gate.name} {gate.location && `- ${gate.location}`}
                </option>
              ))}
            </select>
          </div>

          {/* Garage */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kapcsolódó garázs
            </label>
            <select
              value={formData.garageId || ''}
              onChange={(e) => onFormChange('garageId', e.target.value || undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Nincs kiválasztva</option>
              {garages.map(garage => (
                <option key={garage.id} value={garage.id}>
                  {garage.name} {garage.address && `- ${garage.address}`}
                </option>
              ))}
            </select>
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Határidő
            </label>
            <input
              type="datetime-local"
              value={formData.dueDate ? formData.dueDate.toISOString().slice(0, -1) : ''}
              onChange={(e) => onFormChange('dueDate', e.target.value ? new Date(e.target.value) : undefined)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Auto-save Setting */}
      <div className="border-t pt-4">
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="autoSave"
            checked={formData.autoSaveEnabled ?? true}
            onChange={(e) => onFormChange('autoSaveEnabled', e.target.checked)}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded 
                     focus:ring-blue-500"
          />
          <label htmlFor="autoSave" className="text-sm text-gray-700">
            Automatikus mentés engedélyezése (ajánlott)
          </label>
        </div>
        <p className="text-xs text-gray-500 mt-1 ml-7">
          A rendszer 5 másodpercenként automatikusan menti a változtatásokat
        </p>
      </div>
    </div>
  )
}