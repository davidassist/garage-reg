'use client'

import React, { useState, useCallback, useEffect, useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  Save, 
  Send,
  Eye,
  EyeOff,
  RotateCcw,
  FileText
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { 
  FormTemplate, 
  DynamicField, 
  FormData, 
  ValidationResult,
  BoolField,
  EnumField, 
  NumberField,
  PhotoField,
  NoteField
} from '@/lib/types/dynamic-forms'

// Import all field components
import { BoolSwitchItem } from './BoolSwitchItem'
import { EnumItem } from './EnumItem'
import { NumberWithRange } from './NumberWithRange'
import { PhotoItem } from './PhotoItem'
import { NoteItem } from './NoteItem'

interface DynamicFormEngineProps {
  template: FormTemplate
  initialData?: FormData
  onSave?: (data: FormData) => void
  onSubmit?: (data: FormData) => void
  onCancel?: () => void
  readOnly?: boolean
  disabled?: boolean
  showProgress?: boolean
  autoSave?: boolean
  autoSaveDelay?: number
  className?: string
}

export function DynamicFormEngine({
  template,
  initialData = {},
  onSave,
  onSubmit,
  onCancel,
  readOnly = false,
  disabled = false,
  showProgress = true,
  autoSave = false,
  autoSaveDelay = 2000,
  className
}: DynamicFormEngineProps) {
  const [formData, setFormData] = useState<FormData>(initialData)
  const [validation, setValidation] = useState<ValidationResult>({})
  const [touchedFields, setTouchedFields] = useState<Set<string>>(new Set())
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [showAllErrors, setShowAllErrors] = useState(false)
  const [autoSaveTimer, setAutoSaveTimer] = useState<NodeJS.Timeout | null>(null)

  // Memoized visible fields based on conditional logic
  const visibleFields = useMemo(() => {
    return template.fields.filter(field => {
      if (!field.conditionalVisibility) return true
      
      const { dependsOn, condition, expectedValue } = field.conditionalVisibility
      const dependentValue = formData[dependsOn]
      
      switch (condition) {
        case 'equals':
          return dependentValue === expectedValue
        case 'not_equals':
          return dependentValue !== expectedValue
        case 'contains':
          return Array.isArray(dependentValue) && dependentValue.includes(expectedValue)
        case 'not_empty':
          return dependentValue != null && dependentValue !== '' && 
                 (!Array.isArray(dependentValue) || dependentValue.length > 0)
        case 'empty':
          return dependentValue == null || dependentValue === '' || 
                 (Array.isArray(dependentValue) && dependentValue.length === 0)
        default:
          return true
      }
    })
  }, [template.fields, formData])

  // Validation logic
  const validateField = useCallback((field: DynamicField, value: any): string[] => {
    switch (field.type) {
      case 'boolean':
        return BoolSwitchItem.validate(field as BoolField, value)
      case 'enum':
        return EnumItem.validate(field as EnumField, value)
      case 'number':
        return NumberWithRange.validate(field as NumberField, value)
      case 'photo':
        return PhotoItem.validate(field as PhotoField, value)
      case 'note':
        return NoteItem.validate(field as NoteField, value)
      default:
        return []
    }
  }, [])

  // Validate entire form
  const validateForm = useCallback((): ValidationResult => {
    const result: ValidationResult = {}
    
    for (const field of visibleFields) {
      const value = formData[field.id]
      const errors = validateField(field, value)
      
      if (errors.length > 0) {
        result[field.id] = { errors, warnings: [] }
      }
    }
    
    return result
  }, [visibleFields, formData, validateField])

  // Update validation when form data changes
  useEffect(() => {
    const validationResult = validateForm()
    setValidation(validationResult)
  }, [validateForm])

  // Auto-save logic
  useEffect(() => {
    if (!autoSave || !onSave || readOnly || disabled) return
    
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer)
    }
    
    const timer = setTimeout(() => {
      onSave(formData)
      setLastSaved(new Date())
    }, autoSaveDelay)
    
    setAutoSaveTimer(timer)
    
    return () => {
      if (timer) clearTimeout(timer)
    }
  }, [formData, autoSave, onSave, readOnly, disabled, autoSaveDelay])

  // Handle field changes
  const handleFieldChange = useCallback((fieldId: string, value: any) => {
    if (readOnly || disabled) return
    
    setFormData(prev => ({
      ...prev,
      [fieldId]: value
    }))
  }, [readOnly, disabled])

  const handleFieldBlur = useCallback((fieldId: string) => {
    setTouchedFields(prev => new Set([...prev, fieldId]))
  }, [])

  // Form actions
  const handleSave = useCallback(() => {
    if (onSave && !readOnly && !disabled) {
      onSave(formData)
      setLastSaved(new Date())
    }
  }, [onSave, formData, readOnly, disabled])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!onSubmit || readOnly || disabled || isSubmitting) return
    
    setShowAllErrors(true)
    const validationResult = validateForm()
    
    // Check if there are any errors
    const hasErrors = Object.values(validationResult).some(v => v.errors.length > 0)
    if (hasErrors) {
      setValidation(validationResult)
      return
    }
    
    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } finally {
      setIsSubmitting(false)
    }
  }, [onSubmit, formData, readOnly, disabled, isSubmitting, validateForm])

  const handleReset = useCallback(() => {
    setFormData(initialData)
    setTouchedFields(new Set())
    setShowAllErrors(false)
    setLastSaved(null)
  }, [initialData])

  // Progress calculation
  const progress = useMemo(() => {
    const requiredFields = visibleFields.filter(f => f.required)
    const completedFields = requiredFields.filter(f => {
      const value = formData[f.id]
      return value != null && value !== '' && 
             (!Array.isArray(value) || value.length > 0)
    })
    
    return {
      completed: completedFields.length,
      total: requiredFields.length,
      percentage: requiredFields.length > 0 ? 
        Math.round((completedFields.length / requiredFields.length) * 100) : 100
    }
  }, [visibleFields, formData])

  // Check if form can be submitted
  const canSubmit = useMemo(() => {
    return !readOnly && !disabled && !isSubmitting &&
           progress.completed === progress.total &&
           Object.keys(validation).length === 0
  }, [readOnly, disabled, isSubmitting, progress, validation])

  // Render field component
  const renderField = useCallback((field: DynamicField) => {
    const value = formData[field.id]
    const fieldValidation = validation[field.id]
    const shouldShowErrors = showAllErrors || touchedFields.has(field.id)
    
    const commonProps = {
      field,
      value,
      onChange: (newValue: any) => handleFieldChange(field.id, newValue),
      onBlur: () => handleFieldBlur(field.id),
      error: shouldShowErrors ? fieldValidation?.errors || [] : [],
      warning: fieldValidation?.warnings || [],
      disabled,
      readonly: readOnly
    }
    
    switch (field.type) {
      case 'boolean':
        return <BoolSwitchItem key={field.id} {...commonProps} field={field as BoolField} />
      case 'enum':
        return <EnumItem key={field.id} {...commonProps} field={field as EnumField} />
      case 'number':
        return <NumberWithRange key={field.id} {...commonProps} field={field as NumberField} />
      case 'photo':
        return <PhotoItem key={field.id} {...commonProps} field={field as PhotoField} />
      case 'note':
        return <NoteItem key={field.id} {...commonProps} field={field as NoteField} />
      default:
        return null
    }
  }, [formData, validation, touchedFields, showAllErrors, disabled, readOnly, handleFieldChange, handleFieldBlur])

  return (
    <Card className={cn('p-6', className)}>
      {/* Form Header */}
      <div className="space-y-4 mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{template.title}</h2>
            {template.description && (
              <p className="text-gray-600 mt-1">{template.description}</p>
            )}
          </div>
          
          {showProgress && (
            <div className="text-right">
              <div className="flex items-center gap-2 mb-2">
                <Badge variant={progress.percentage === 100 ? "default" : "secondary"}>
                  {progress.completed}/{progress.total}
                </Badge>
                <span className="text-sm text-gray-600">
                  {progress.percentage}% kitöltve
                </span>
              </div>
              <div className="w-24 bg-gray-200 rounded-full h-2">
                <div 
                  className={cn(
                    'h-2 rounded-full transition-all duration-300',
                    progress.percentage === 100 ? 'bg-green-500' : 'bg-blue-500'
                  )}
                  style={{ width: `${progress.percentage}%` }}
                />
              </div>
            </div>
          )}
        </div>
        
        {/* Auto-save indicator */}
        {autoSave && lastSaved && (
          <div className="flex items-center gap-1 text-sm text-gray-500">
            <Save className="w-3 h-3" />
            Automatikusan mentve: {lastSaved.toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Form Fields */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {visibleFields.map((field, index) => (
          <div key={field.id}>
            {renderField(field)}
            {index < visibleFields.length - 1 && (
              <Separator className="mt-6" />
            )}
          </div>
        ))}
        
        {visibleFields.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Nincs megjeleníthető mező a jelenlegi beállítások alapján.</p>
          </div>
        )}

        {/* Form Actions */}
        {!readOnly && (
          <div className="flex items-center justify-between pt-6 border-t">
            <div className="flex items-center gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowAllErrors(!showAllErrors)}
                className="text-sm"
              >
                {showAllErrors ? (
                  <>
                    <EyeOff className="w-4 h-4 mr-2" />
                    Hibák elrejtése
                  </>
                ) : (
                  <>
                    <Eye className="w-4 h-4 mr-2" />
                    Összes hiba
                  </>
                )}
              </Button>
              
              <Button
                type="button"
                variant="outline"
                onClick={handleReset}
                disabled={disabled}
                className="text-sm"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                Visszaállítás
              </Button>
            </div>
            
            <div className="flex items-center gap-3">
              {onCancel && (
                <Button
                  type="button"
                  variant="ghost"
                  onClick={onCancel}
                  disabled={disabled}
                >
                  Mégse
                </Button>
              )}
              
              {onSave && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleSave}
                  disabled={disabled}
                >
                  <Save className="w-4 h-4 mr-2" />
                  Mentés
                </Button>
              )}
              
              {onSubmit && (
                <Button
                  type="submit"
                  disabled={!canSubmit}
                  className={cn(
                    'transition-all duration-200',
                    canSubmit && 'bg-green-600 hover:bg-green-700'
                  )}
                >
                  {isSubmitting ? (
                    <>
                      <Clock className="w-4 h-4 mr-2 animate-spin" />
                      Küldés...
                    </>
                  ) : canSubmit ? (
                    <>
                      <CheckCircle className="w-4 h-4 mr-2" />
                      Beküldés
                    </>
                  ) : (
                    <>
                      <AlertCircle className="w-4 h-4 mr-2" />
                      Nem küldhető be
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>
        )}
      </form>
      
      {/* Form Status */}
      {!readOnly && (
        <div className="mt-4 text-xs text-gray-500">
          {progress.total > 0 && (
            <p>
              {progress.completed === progress.total ? (
                <span className="text-green-600 font-medium">
                  ✓ Összes kötelező mező kitöltve
                </span>
              ) : (
                <span>
                  {progress.total - progress.completed} kötelező mező van hátra
                </span>
              )}
            </p>
          )}
          
          {Object.keys(validation).length > 0 && (
            <p className="text-red-600 mt-1">
              {Object.keys(validation).length} mezőben van hiba
            </p>
          )}
        </div>
      )}
    </Card>
  )
}

// Export additional utilities
export const createDefaultFormData = (template: FormTemplate): FormData => {
  const data: FormData = {}
  
  template.fields.forEach(field => {
    switch (field.type) {
      case 'boolean':
        data[field.id] = BoolSwitchItem.getDefaultValue(field as BoolField)
        break
      case 'enum':
        data[field.id] = EnumItem.getDefaultValue(field as EnumField)
        break
      case 'number':
        data[field.id] = NumberWithRange.getDefaultValue(field as NumberField)
        break
      case 'photo':
        data[field.id] = PhotoItem.getDefaultValue(field as PhotoField)
        break
      case 'note':
        data[field.id] = NoteItem.getDefaultValue(field as NoteField)
        break
    }
  })
  
  return data
}

export const validateFormTemplate = (template: FormTemplate): string[] => {
  const errors: string[] = []
  
  if (!template.title) {
    errors.push('Template title is required')
  }
  
  if (!template.fields || template.fields.length === 0) {
    errors.push('Template must have at least one field')
  }
  
  // Check for duplicate field IDs
  const fieldIds = new Set<string>()
  template.fields.forEach(field => {
    if (fieldIds.has(field.id)) {
      errors.push(`Duplicate field ID: ${field.id}`)
    }
    fieldIds.add(field.id)
  })
  
  // Validate conditional visibility dependencies
  template.fields.forEach(field => {
    if (field.conditionalVisibility) {
      const dependentField = template.fields.find(f => f.id === field.conditionalVisibility!.dependsOn)
      if (!dependentField) {
        errors.push(`Field ${field.id} depends on non-existent field: ${field.conditionalVisibility.dependsOn}`)
      }
    }
  })
  
  return errors
}