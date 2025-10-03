'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { 
  Play, 
  Save, 
  CheckCircle, 
  Clock, 
  AlertTriangle,
  FileText,
  Settings,
  Eye
} from 'lucide-react'
import { 
  InspectionInstance, 
  InspectionTemplate, 
  StartInspectionRequest,
  InspectionFormState,
  STATUS_CONFIGS 
} from '@/lib/types/inspection'
import { StartInspectionDialog } from './StartInspectionDialog'
import { InspectionFormRenderer } from './InspectionFormRenderer'
import { InspectionSummary } from './InspectionSummary'
import { UnsavedChangesWarning, useUnsavedChanges } from './UnsavedChangesWarning'

interface InspectionManagerProps {
  // Data props
  templates: InspectionTemplate[]
  inspections?: InspectionInstance[]
  currentInspection?: InspectionInstance | null
  
  // Related data
  gates?: Array<{ id: string; name: string; location?: string }>
  garages?: Array<{ id: string; name: string; address?: string }>
  users?: Array<{ id: string; name: string; role?: string }>
  
  // Event handlers
  onStartInspection?: (request: StartInspectionRequest) => Promise<InspectionInstance>
  onSaveInspection?: (inspection: InspectionInstance) => Promise<void>
  onSubmitInspection?: (inspectionId: string) => Promise<void>
  onFieldChange?: (inspectionId: string, fieldId: string, value: any) => void
  onStatusChange?: (inspectionId: string, status: string) => Promise<void>
  
  // UI props
  className?: string
  autoStart?: boolean
  readOnlyMode?: boolean
}

type ViewMode = 'list' | 'start' | 'form' | 'summary'

export function InspectionManager({
  templates,
  inspections = [],
  currentInspection,
  gates = [],
  garages = [],
  users = [],
  onStartInspection,
  onSaveInspection,
  onSubmitInspection,
  onFieldChange,
  onStatusChange,
  className = '',
  autoStart = false,
  readOnlyMode = false
}: InspectionManagerProps) {
  const [viewMode, setViewMode] = useState<ViewMode>(
    currentInspection ? 'form' : autoStart ? 'start' : 'list'
  )
  const [activeInspection, setActiveInspection] = useState<InspectionInstance | null>(
    currentInspection || null
  )
  const [formState, setFormState] = useState<InspectionFormState>({
    values: {},
    errors: {},
    touched: {},
    isSubmitting: false,
    isDirty: false
  })

  // Unsaved changes management
  const {
    hasUnsavedChanges,
    changedFields,
    markAsChanged,
    markAsSaved,
    discardChanges
  } = useUnsavedChanges()

  // Update active inspection when prop changes
  useEffect(() => {
    if (currentInspection) {
      setActiveInspection(currentInspection)
      setViewMode(currentInspection.status === 'completed' ? 'summary' : 'form')
    }
  }, [currentInspection])

  // Initialize form state when active inspection changes
  useEffect(() => {
    if (activeInspection) {
      const values: Record<string, any> = {}
      activeInspection.fieldValues.forEach(fv => {
        values[fv.fieldId] = fv.value
      })
      
      setFormState({
        values,
        errors: {},
        touched: {},
        isSubmitting: false,
        isDirty: false
      })
    }
  }, [activeInspection])

  const getActiveTemplate = (): InspectionTemplate | null => {
    return activeInspection 
      ? templates.find(t => t.id === activeInspection.templateId) || null
      : null
  }

  // Start new inspection
  const handleStartInspection = async (request: StartInspectionRequest) => {
    try {
      if (onStartInspection) {
        const newInspection = await onStartInspection(request)
        setActiveInspection(newInspection)
        setViewMode('form')
        discardChanges() // Reset unsaved changes state
      }
    } catch (error) {
      console.error('Failed to start inspection:', error)
    }
  }

  // Handle field changes
  const handleFieldChange = useCallback((fieldId: string, value: any) => {
    setFormState(prev => ({
      ...prev,
      values: { ...prev.values, [fieldId]: value },
      isDirty: true,
      touched: { ...prev.touched, [fieldId]: true }
    }))
    
    markAsChanged(fieldId)
    
    if (activeInspection && onFieldChange) {
      onFieldChange(activeInspection.id, fieldId, value)
    }
  }, [activeInspection, onFieldChange, markAsChanged])

  // Save inspection
  const handleSaveInspection = async () => {
    if (!activeInspection) return

    try {
      setFormState(prev => ({ ...prev, isSubmitting: true }))
      
      // Update inspection with form values
      const updatedInspection: InspectionInstance = {
        ...activeInspection,
        fieldValues: Object.entries(formState.values).map(([fieldId, value]) => ({
          fieldId,
          value,
          timestamp: new Date()
        })),
        completedFields: Object.keys(formState.values).filter(
          fieldId => formState.values[fieldId] !== undefined && 
                     formState.values[fieldId] !== null && 
                     formState.values[fieldId] !== ''
        ),
        hasUnsavedChanges: false,
        lastSavedAt: new Date(),
        updatedAt: new Date()
      }

      // Recalculate progress
      const template = getActiveTemplate()
      if (template) {
        updatedInspection.progressPercentage = Math.round(
          (updatedInspection.completedFields.length / template.fields.length) * 100
        )
      }

      setActiveInspection(updatedInspection)
      
      if (onSaveInspection) {
        await onSaveInspection(updatedInspection)
      }
      
      setFormState(prev => ({ ...prev, isDirty: false }))
      markAsSaved()
      
    } catch (error) {
      console.error('Save failed:', error)
    } finally {
      setFormState(prev => ({ ...prev, isSubmitting: false }))
    }
  }

  // Submit inspection
  const handleSubmitInspection = async () => {
    if (!activeInspection) return

    try {
      await handleSaveInspection() // Save first
      
      if (onSubmitInspection) {
        await onSubmitInspection(activeInspection.id)
      }
      
      // Update status to submitted
      const updatedInspection: InspectionInstance = {
        ...activeInspection,
        status: 'submitted',
        submittedAt: new Date()
      }
      
      setActiveInspection(updatedInspection)
      setViewMode('summary')
      
    } catch (error) {
      console.error('Submit failed:', error)
    }
  }

  // Handle status changes
  const handleStatusChange = async (status: string) => {
    if (!activeInspection) return

    try {
      if (onStatusChange) {
        await onStatusChange(activeInspection.id, status)
      }

      const now = new Date()
      const updatedInspection: InspectionInstance = {
        ...activeInspection,
        status: status as any,
        ...(status === 'in_progress' && !activeInspection.startedAt && { startedAt: now }),
        ...(status === 'completed' && { completedAt: now }),
        updatedAt: now
      }
      
      setActiveInspection(updatedInspection)
      
      if (status === 'completed') {
        setViewMode('summary')
      }
      
    } catch (error) {
      console.error('Status change failed:', error)
    }
  }

  // Navigation handlers
  const handleBackToList = () => {
    if (hasUnsavedChanges) {
      // Let UnsavedChangesWarning handle this
      return
    }
    setViewMode('list')
    setActiveInspection(null)
    discardChanges()
  }

  const handleEditInspection = () => {
    setViewMode('form')
  }

  const handleViewSummary = () => {
    setViewMode('summary')
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Unsaved Changes Warning */}
      <UnsavedChangesWarning
        hasUnsavedChanges={hasUnsavedChanges}
        onSave={handleSaveInspection}
        onDiscard={discardChanges}
        message={`${changedFields.length > 0 ? changedFields.length : ''} mező módosítása még nincs mentve. Biztosan el szeretnéd hagyni az oldalt?`}
      />

      {/* Navigation Header */}
      {activeInspection && (
        <InspectionNavigationHeader
          inspection={activeInspection}
          template={getActiveTemplate()}
          viewMode={viewMode}
          onBackToList={handleBackToList}
          onViewForm={handleEditInspection}
          onViewSummary={handleViewSummary}
          hasUnsavedChanges={hasUnsavedChanges}
        />
      )}

      {/* Main Content */}
      {viewMode === 'list' && (
        <InspectionListView
          inspections={inspections}
          templates={templates}
          onStartNew={() => setViewMode('start')}
          onSelectInspection={(inspection) => {
            setActiveInspection(inspection)
            setViewMode(inspection.status === 'completed' ? 'summary' : 'form')
          }}
        />
      )}

      {viewMode === 'start' && (
        <StartInspectionDialog
          isOpen={true}
          onClose={() => setViewMode('list')}
          onStart={handleStartInspection}
          templates={templates}
          gates={gates}
          garages={garages}
          users={users}
        />
      )}

      {viewMode === 'form' && activeInspection && getActiveTemplate() && (
        <InspectionFormRenderer
          inspection={activeInspection}
          template={getActiveTemplate()!}
          onFieldChange={handleFieldChange}
          onSave={handleSaveInspection}
          onSubmit={handleSubmitInspection}
          onStatusChange={handleStatusChange}
          readOnly={readOnlyMode}
        />
      )}

      {viewMode === 'summary' && activeInspection && getActiveTemplate() && (
        <InspectionSummary
          inspection={activeInspection}
          template={getActiveTemplate()!}
          onClose={handleBackToList}
          onEdit={readOnlyMode ? undefined : handleEditInspection}
          onSubmit={readOnlyMode ? undefined : handleSubmitInspection}
          onPrint={() => window.print()}
          onExport={() => {/* Export logic */}}
        />
      )}
    </div>
  )
}

// Navigation Header Component
interface InspectionNavigationHeaderProps {
  inspection: InspectionInstance
  template: InspectionTemplate | null
  viewMode: ViewMode
  onBackToList: () => void
  onViewForm: () => void
  onViewSummary: () => void
  hasUnsavedChanges: boolean
}

function InspectionNavigationHeader({
  inspection,
  template,
  viewMode,
  onBackToList,
  onViewForm,
  onViewSummary,
  hasUnsavedChanges
}: InspectionNavigationHeaderProps) {
  const statusConfig = STATUS_CONFIGS[inspection.status]

  return (
    <div className="bg-white rounded-lg border p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onBackToList}
            className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
          >
            ← Vissza a listához
          </button>
          
          <div className="text-sm text-gray-500">
            {template?.name} • {inspection.title}
          </div>
          
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
            statusConfig.color === 'gray' ? 'bg-gray-100 text-gray-700' :
            statusConfig.color === 'blue' ? 'bg-blue-100 text-blue-700' :
            statusConfig.color === 'green' ? 'bg-green-100 text-green-700' :
            'bg-red-100 text-red-700'
          }`}>
            <span>{statusConfig.icon}</span>
            <span>{statusConfig.label}</span>
          </div>
          
          {hasUnsavedChanges && (
            <div className="flex items-center space-x-1 text-orange-600">
              <AlertTriangle className="w-4 h-4" />
              <span className="text-xs font-medium">Nem mentett változások</span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={onViewForm}
            disabled={viewMode === 'form'}
            className={`px-3 py-1 text-sm font-medium rounded transition-colors ${
              viewMode === 'form'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <FileText className="w-4 h-4 inline mr-1" />
            Űrlap
          </button>
          
          <button
            onClick={onViewSummary}
            disabled={viewMode === 'summary'}
            className={`px-3 py-1 text-sm font-medium rounded transition-colors ${
              viewMode === 'summary'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-1" />
            Összegzés
          </button>
        </div>
      </div>
    </div>
  )
}

// List View Component
interface InspectionListViewProps {
  inspections: InspectionInstance[]
  templates: InspectionTemplate[]
  onStartNew: () => void
  onSelectInspection: (inspection: InspectionInstance) => void
}

function InspectionListView({
  inspections,
  templates,
  onStartNew,
  onSelectInspection
}: InspectionListViewProps) {
  const [filter, setFilter] = useState<string>('all')

  const filteredInspections = inspections.filter(inspection => {
    if (filter === 'all') return true
    return inspection.status === filter
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ellenőrzések</h1>
          <p className="text-gray-600 mt-1">Kezelje az ellenőrzési folyamatokat</p>
        </div>
        
        <button
          onClick={onStartNew}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 
                   transition-colors flex items-center space-x-2"
        >
          <Play className="w-4 h-4" />
          <span>Új Ellenőrzés</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 
                   focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="all">Minden állapot</option>
          <option value="draft">Vázlat</option>
          <option value="in_progress">Folyamatban</option>
          <option value="completed">Befejezett</option>
          <option value="submitted">Elküldött</option>
          <option value="approved">Jóváhagyott</option>
        </select>
      </div>

      {/* Inspections Grid */}
      <div className="grid gap-4">
        {filteredInspections.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg border">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Nincsenek ellenőrzések</p>
            <button
              onClick={onStartNew}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 
                       transition-colors"
            >
              Kezdje el az első ellenőrzést
            </button>
          </div>
        ) : (
          filteredInspections.map(inspection => (
            <InspectionListItem
              key={inspection.id}
              inspection={inspection}
              template={templates.find(t => t.id === inspection.templateId)}
              onSelect={() => onSelectInspection(inspection)}
            />
          ))
        )}
      </div>
    </div>
  )
}

// List Item Component
interface InspectionListItemProps {
  inspection: InspectionInstance
  template?: InspectionTemplate
  onSelect: () => void
}

function InspectionListItem({ inspection, template, onSelect }: InspectionListItemProps) {
  const statusConfig = STATUS_CONFIGS[inspection.status]

  return (
    <div
      onClick={onSelect}
      className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-medium text-gray-900">{inspection.title}</h3>
          {template && (
            <p className="text-sm text-gray-600 mt-1">{template.name}</p>
          )}
          
          <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
            <span>Létrehozva: {inspection.createdAt.toLocaleDateString('hu-HU')}</span>
            <span>Kitöltöttség: {inspection.progressPercentage}%</span>
            {inspection.assignedTo && (
              <span>Felelős: {inspection.assignedTo}</span>
            )}
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          {inspection.progressPercentage > 0 && (
            <div className="w-16 bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${inspection.progressPercentage}%` }}
              />
            </div>
          )}
          
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${
            statusConfig.color === 'gray' ? 'bg-gray-100 text-gray-700' :
            statusConfig.color === 'blue' ? 'bg-blue-100 text-blue-700' :
            statusConfig.color === 'green' ? 'bg-green-100 text-green-700' :
            'bg-red-100 text-red-700'
          }`}>
            <span>{statusConfig.icon}</span>
            <span>{statusConfig.label}</span>
          </div>
        </div>
      </div>
    </div>
  )
}