'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { 
  Save, 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  Pause, 
  Play,
  Upload,
  MessageSquare,
  Camera,
  Edit3,
  Hash,
  Type,
  ToggleLeft,
  List,
  Eye,
  EyeOff,
  Wifi,
  WifiOff
} from 'lucide-react'
import { 
  InspectionInstance, 
  InspectionTemplate, 
  FieldValue,
  InspectionFormState,
  FIELD_TYPE_CONFIGS 
} from '@/lib/types/inspection'
import { useAutoSave } from '@/lib/services/inspection-autosave'

interface InspectionFormRendererProps {
  inspection: InspectionInstance
  template: InspectionTemplate
  onFieldChange: (fieldId: string, value: any) => void
  onSave: () => Promise<void>
  onSubmit: () => Promise<void>
  onStatusChange: (status: string) => void
  readOnly?: boolean
  className?: string
}

export function InspectionFormRenderer({
  inspection,
  template,
  onFieldChange,
  onSave,
  onSubmit,
  onStatusChange,
  readOnly = false,
  className = ''
}: InspectionFormRendererProps) {
  const [formState, setFormState] = useState<InspectionFormState>({
    values: {},
    errors: {},
    touched: {},
    isSubmitting: false,
    isDirty: false
  })
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [showValidation, setShowValidation] = useState(false)

  // Auto-save hook
  const {
    autoSaveState,
    scheduleAutoSave,
    saveNow,
    saveToLocalStorage,
    loadFromLocalStorage
  } = useAutoSave(inspection.id)

  // Initialize form values from inspection
  useEffect(() => {
    const values: Record<string, any> = {}
    
    inspection.fieldValues.forEach(fieldValue => {
      values[fieldValue.fieldId] = fieldValue.value
    })

    // Try to load from local storage if no values
    if (Object.keys(values).length === 0) {
      const backup = loadFromLocalStorage()
      if (backup) {
        Object.assign(values, backup.values)
      }
    }

    setFormState(prev => ({ ...prev, values }))
  }, [inspection, loadFromLocalStorage])

  // Online/offline detection
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)
    
    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)
    
    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Auto-save on form changes
  useEffect(() => {
    if (formState.isDirty && isOnline && inspection.autoSaveEnabled) {
      scheduleAutoSave(formState, inspection)
      saveToLocalStorage(formState)
    }
  }, [formState, isOnline, inspection, scheduleAutoSave, saveToLocalStorage])

  const handleFieldChange = useCallback((fieldId: string, value: any) => {
    setFormState(prev => ({
      ...prev,
      values: { ...prev.values, [fieldId]: value },
      isDirty: true,
      touched: { ...prev.touched, [fieldId]: true },
      errors: { ...prev.errors, [fieldId]: '' } // Clear error on change
    }))
    
    onFieldChange(fieldId, value)
  }, [onFieldChange])

  const validateField = useCallback((field: any, value: any): string => {
    if (field.required && (!value || value === '')) {
      return 'Ez a mező kötelező'
    }
    
    if (field.validation) {
      const validation = field.validation
      
      if (validation.pattern && typeof value === 'string') {
        const regex = new RegExp(validation.pattern)
        if (!regex.test(value)) {
          return 'A formátum nem megfelelő'
        }
      }
      
      if (validation.min !== undefined && typeof value === 'number' && value < validation.min) {
        return `Minimum érték: ${validation.min}`
      }
      
      if (validation.max !== undefined && typeof value === 'number' && value > validation.max) {
        return `Maximum érték: ${validation.max}`
      }
      
      if (validation.maxLength && typeof value === 'string' && value.length > validation.maxLength) {
        return `Maximum ${validation.maxLength} karakter`
      }
    }
    
    return ''
  }, [])

  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {}
    
    template.fields.forEach(field => {
      const value = formState.values[field.id]
      const error = validateField(field, value)
      if (error) {
        errors[field.id] = error
      }
    })
    
    setFormState(prev => ({ ...prev, errors }))
    return Object.keys(errors).length === 0
  }, [template.fields, formState.values, validateField])

  const handleSaveManually = async () => {
    try {
      setFormState(prev => ({ ...prev, isSubmitting: true }))
      await saveNow(formState, inspection)
      await onSave()
    } catch (error) {
      console.error('Save failed:', error)
    } finally {
      setFormState(prev => ({ ...prev, isSubmitting: false }))
    }
  }

  const handleSubmitForm = async () => {
    setShowValidation(true)
    
    if (validateForm()) {
      try {
        setFormState(prev => ({ ...prev, isSubmitting: true }))
        await onSubmit()
      } catch (error) {
        console.error('Submit failed:', error)
      } finally {
        setFormState(prev => ({ ...prev, isSubmitting: false }))
      }
    }
  }

  const shouldShowField = (field: any): boolean => {
    if (!field.conditionalLogic) return true
    
    const { dependsOn, showWhen, hideWhen } = field.conditionalLogic
    if (!dependsOn) return true
    
    const dependentValue = formState.values[dependsOn]
    
    if (hideWhen !== undefined && dependentValue === hideWhen) {
      return false
    }
    
    if (showWhen !== undefined && dependentValue !== showWhen) {
      return false
    }
    
    return true
  }

  const getFieldError = (fieldId: string): string => {
    if (!showValidation) return ''
    return formState.errors[fieldId] || ''
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Status */}
      <InspectionHeader
        inspection={inspection}
        template={template}
        autoSaveState={autoSaveState}
        isOnline={isOnline}
        formState={formState}
        onSave={handleSaveManually}
        onSubmit={handleSubmitForm}
        onStatusChange={onStatusChange}
        readOnly={readOnly}
      />

      {/* Progress Bar */}
      <div className="bg-white rounded-lg border p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Kitöltöttség</span>
          <span className="text-sm text-gray-500">
            {inspection.completedFields.length} / {inspection.totalFields} mező
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${inspection.progressPercentage}%` }}
          />
        </div>
      </div>

      {/* Form Fields */}
      <div className="space-y-6">
        {template.fields.filter(shouldShowField).map((field, index) => (
          <FieldRenderer
            key={field.id}
            field={field}
            value={formState.values[field.id]}
            error={getFieldError(field.id)}
            touched={formState.touched[field.id]}
            onChange={(value) => handleFieldChange(field.id, value)}
            readOnly={readOnly}
            fieldIndex={index}
          />
        ))}
      </div>

      {/* Validation Summary */}
      {showValidation && Object.keys(formState.errors).length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2 mb-2">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <h3 className="font-medium text-red-800">Hiányos vagy hibás adatok</h3>
          </div>
          <ul className="text-sm text-red-700 space-y-1">
            {Object.entries(formState.errors).map(([fieldId, error]) => {
              const field = template.fields.find(f => f.id === fieldId)
              return (
                <li key={fieldId}>
                  <strong>{field?.label}:</strong> {error}
                </li>
              )
            })}
          </ul>
        </div>
      )}
    </div>
  )
}

// Inspection Header Component
interface InspectionHeaderProps {
  inspection: InspectionInstance
  template: InspectionTemplate
  autoSaveState: any
  isOnline: boolean
  formState: InspectionFormState
  onSave: () => void
  onSubmit: () => void
  onStatusChange: (status: string) => void
  readOnly: boolean
}

function InspectionHeader({
  inspection,
  template,
  autoSaveState,
  isOnline,
  formState,
  onSave,
  onSubmit,
  onStatusChange,
  readOnly
}: InspectionHeaderProps) {
  return (
    <div className="bg-white rounded-lg border p-6">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">{inspection.title}</h1>
          <p className="text-sm text-gray-600 mt-1">
            Sablon: {template.name}
          </p>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center space-x-2">
          {isOnline ? (
            <div className="flex items-center space-x-1 text-green-600">
              <Wifi className="w-4 h-4" />
              <span className="text-xs">Online</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1 text-red-600">
              <WifiOff className="w-4 h-4" />
              <span className="text-xs">Offline</span>
            </div>
          )}
        </div>
      </div>

      {/* Auto-save Status */}
      {autoSaveState.isEnabled && (
        <div className="flex items-center space-x-2 text-sm mb-4">
          {autoSaveState.isSaving ? (
            <div className="flex items-center space-x-2 text-blue-600">
              <div className="w-3 h-3 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <span>Mentés...</span>
            </div>
          ) : autoSaveState.lastSaved ? (
            <div className="flex items-center space-x-2 text-green-600">
              <CheckCircle className="w-4 h-4" />
              <span>Mentve: {autoSaveState.lastSaved.toLocaleTimeString('hu-HU')}</span>
            </div>
          ) : formState.isDirty ? (
            <div className="flex items-center space-x-2 text-orange-600">
              <Clock className="w-4 h-4" />
              <span>Nem mentett változások</span>
            </div>
          ) : null}
          
          {autoSaveState.saveError && (
            <div className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="w-4 h-4" />
              <span>Mentési hiba</span>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      {!readOnly && (
        <div className="flex items-center space-x-3">
          <button
            onClick={onSave}
            disabled={formState.isSubmitting || !formState.isDirty}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors flex items-center space-x-2 ${
              formState.isSubmitting || !formState.isDirty
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            <Save className="w-4 h-4" />
            <span>Mentés</span>
          </button>
          
          {inspection.status === 'in_progress' && (
            <>
              <button
                onClick={() => onStatusChange('completed')}
                disabled={formState.isSubmitting || inspection.progressPercentage < 100}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors flex items-center space-x-2 ${
                  formState.isSubmitting || inspection.progressPercentage < 100
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                <CheckCircle className="w-4 h-4" />
                <span>Befejezés</span>
              </button>
              
              <button
                onClick={() => onStatusChange('draft')}
                disabled={formState.isSubmitting}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 
                         rounded-md hover:bg-gray-50 transition-colors flex items-center space-x-2"
              >
                <Pause className="w-4 h-4" />
                <span>Szüneteltetés</span>
              </button>
            </>
          )}
          
          {inspection.status === 'completed' && (
            <button
              onClick={onSubmit}
              disabled={formState.isSubmitting}
              className="px-4 py-2 text-sm font-medium bg-indigo-600 text-white rounded-md 
                       hover:bg-indigo-700 transition-colors flex items-center space-x-2"
            >
              <Upload className="w-4 h-4" />
              <span>Elküldés</span>
            </button>
          )}
        </div>
      )}
    </div>
  )
}

// Field Renderer Component
interface FieldRendererProps {
  field: any
  value: any
  error: string
  touched: boolean
  onChange: (value: any) => void
  readOnly: boolean
  fieldIndex: number
}

function FieldRenderer({
  field,
  value,
  error,
  touched,
  onChange,
  readOnly,
  fieldIndex
}: FieldRendererProps) {
  const fieldConfig = FIELD_TYPE_CONFIGS[field.type as keyof typeof FIELD_TYPE_CONFIGS]
  const [showAdvanced, setShowAdvanced] = useState(false)

  const getFieldIcon = () => {
    switch (field.type) {
      case 'text': return <Type className="w-4 h-4" />
      case 'number': return <Hash className="w-4 h-4" />
      case 'boolean': return <ToggleLeft className="w-4 h-4" />
      case 'select': 
      case 'multiselect': return <List className="w-4 h-4" />
      case 'photo': return <Camera className="w-4 h-4" />
      case 'signature': return <Edit3 className="w-4 h-4" />
      case 'note': return <MessageSquare className="w-4 h-4" />
      default: return <Type className="w-4 h-4" />
    }
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      {/* Field Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center mt-1">
            {getFieldIcon()}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-900">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            
            {field.description && (
              <p className="text-xs text-gray-600 mt-1">{field.description}</p>
            )}
            
            <div className="flex items-center space-x-2 mt-2">
              <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                {fieldConfig?.label}
              </span>
              <span className="text-xs text-gray-400">#{fieldIndex + 1}</span>
            </div>
          </div>
        </div>
        
        {/* Advanced Options */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
        >
          {showAdvanced ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>

      {/* Field Input */}
      <div className="space-y-3">
        <DynamicFieldInput
          field={field}
          value={value}
          onChange={onChange}
          readOnly={readOnly}
          error={error}
          touched={touched}
        />
        
        {error && (
          <div className="flex items-center space-x-2 text-red-600">
            <AlertCircle className="w-4 h-4" />
            <span className="text-sm">{error}</span>
          </div>
        )}
      </div>

      {/* Advanced Field Info */}
      {showAdvanced && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <div className="grid grid-cols-2 gap-4 text-xs text-gray-500">
            <div>
              <span className="font-medium">Típus:</span> {field.type}
            </div>
            <div>
              <span className="font-medium">Kötelező:</span> {field.required ? 'Igen' : 'Nem'}
            </div>
            {field.validation && (
              <>
                {field.validation.min !== undefined && (
                  <div>
                    <span className="font-medium">Min érték:</span> {field.validation.min}
                  </div>
                )}
                {field.validation.max !== undefined && (
                  <div>
                    <span className="font-medium">Max érték:</span> {field.validation.max}
                  </div>
                )}
                {field.validation.maxLength && (
                  <div>
                    <span className="font-medium">Max hossz:</span> {field.validation.maxLength}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

// Dynamic Field Input Component
interface DynamicFieldInputProps {
  field: any
  value: any
  onChange: (value: any) => void
  readOnly: boolean
  error: string
  touched: boolean
}

function DynamicFieldInput({
  field,
  value,
  onChange,
  readOnly,
  error,
  touched
}: DynamicFieldInputProps) {
  const inputClassName = `w-full px-3 py-2 border rounded-md transition-colors ${
    error && touched 
      ? 'border-red-500 focus:ring-red-500' 
      : 'border-gray-300 focus:ring-blue-500 focus:border-blue-500'
  } ${readOnly ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}`

  switch (field.type) {
    case 'text':
      return (
        <input
          type="text"
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder={field.defaultValue}
          readOnly={readOnly}
          className={inputClassName}
          maxLength={field.validation?.maxLength}
        />
      )

    case 'number':
      return (
        <input
          type="number"
          value={value || ''}
          onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
          placeholder={field.defaultValue?.toString()}
          min={field.validation?.min}
          max={field.validation?.max}
          readOnly={readOnly}
          className={inputClassName}
        />
      )

    case 'boolean':
      return (
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            checked={value || false}
            onChange={(e) => onChange(e.target.checked)}
            disabled={readOnly}
            className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">
            {value ? 'Igen' : 'Nem'}
          </span>
        </div>
      )

    case 'select':
      return (
        <select
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          disabled={readOnly}
          className={inputClassName}
        >
          <option value="">Válassz...</option>
          {field.options?.map((option: string) => (
            <option key={option} value={option}>
              {option}
            </option>
          ))}
        </select>
      )

    case 'multiselect':
      return (
        <div className="space-y-2">
          {field.options?.map((option: string) => (
            <label key={option} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={(value || []).includes(option)}
                onChange={(e) => {
                  const currentValues = value || []
                  if (e.target.checked) {
                    onChange([...currentValues, option])
                  } else {
                    onChange(currentValues.filter((v: string) => v !== option))
                  }
                }}
                disabled={readOnly}
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{option}</span>
            </label>
          ))}
        </div>
      )

    case 'note':
      return (
        <textarea
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Írd ide a megjegyzéseket..."
          rows={4}
          readOnly={readOnly}
          className={inputClassName}
          maxLength={field.validation?.maxLength}
        />
      )

    case 'photo':
      return (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <Camera className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-600">Fotó feltöltés</p>
          <p className="text-xs text-gray-500 mt-1">
            Drag & drop vagy kattints a képek hozzáadásához
          </p>
        </div>
      )

    case 'signature':
      return (
        <div className="border border-gray-300 rounded-lg p-8 bg-gray-50 text-center">
          <Edit3 className="w-8 h-8 text-gray-400 mx-auto mb-2" />
          <p className="text-sm text-gray-600">Aláírás pad</p>
          <p className="text-xs text-gray-500 mt-1">
            Kattints az aláírás megkezdéséhez
          </p>
        </div>
      )

    default:
      return (
        <div className="text-sm text-gray-500 italic">
          Ismeretlen mező típus: {field.type}
        </div>
      )
  }
}