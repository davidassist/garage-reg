'use client'

import { useState, useCallback } from 'react'
import { AlertCircle, Save, RefreshCw } from 'lucide-react'
import { FormTemplate, FormField } from '@/lib/types/dynamic-form'
import { 
  BoolSwitchItem, 
  EnumItem, 
  NumberWithRange, 
  PhotoItem, 
  NoteItem 
} from './fields'

type FormData = Record<string, any>

interface DynamicFormRendererProps {
  template: FormTemplate
  initialData?: FormData
  onSubmit?: (data: FormData) => void | Promise<void>
  onChange?: (data: FormData) => void
  disabled?: boolean
  className?: string
}

export function DynamicFormRenderer({
  template,
  initialData = {},
  onSubmit,
  onChange,
  disabled = false,
  className = ''
}: DynamicFormRendererProps) {
  const [formData, setFormData] = useState<FormData>(initialData)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errors, setErrors] = useState<Record<string, string[]>>({})

  // Handle field value change
  const handleFieldChange = useCallback((fieldId: string, value: any) => {
    const newData = { ...formData, [fieldId]: value }
    setFormData(newData)
    onChange?.(newData)
  }, [formData, onChange])

  // Basic validation
  const validateForm = useCallback(() => {
    const newErrors: Record<string, string[]> = {}
    
    // Get all fields from all sections
    const allFields: FormField[] = []
    template.sections.forEach(section => {
      allFields.push(...section.fields)
    })

    // Validate each field
    allFields.forEach(field => {
      const value = formData[field.id]
      const fieldErrors: string[] = []
      
      // Check required validation
      const requiredRule = field.validation.find(rule => rule.type === 'required')
      if (requiredRule) {
        if (value === undefined || value === null || value === '' || 
            (Array.isArray(value) && value.length === 0)) {
          fieldErrors.push(requiredRule.message || 'Ez a mező kötelező')
        }
      }
      
      if (fieldErrors.length > 0) {
        newErrors[field.id] = fieldErrors
      }
    })
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [formData, template])

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm() || isSubmitting) return

    setIsSubmitting(true)
    try {
      await onSubmit?.(formData)
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }, [validateForm, isSubmitting, formData, onSubmit])

  // Reset form
  const handleReset = useCallback(() => {
    setFormData(initialData)
    setErrors({})
  }, [initialData])

  // Render individual field
  const renderField = useCallback((field: FormField) => {
    const fieldValue = formData[field.id]
    const fieldErrors = errors[field.id] || []
    const isRequired = field.validation?.some(rule => rule.type === 'required') ?? false

    // Common field props
    const commonProps = {
      value: fieldValue,
      onChange: (value: any) => handleFieldChange(field.id, value),
      error: fieldErrors,
      disabled: disabled || field.disabled,
      required: isRequired
    }

    // Render field based on type with explicit typing
    switch (field.type) {
      case 'boolean_switch':
        return <BoolSwitchItem key={field.id} field={field} {...commonProps} />
      
      case 'enum_select':
        return <EnumItem key={field.id} field={field} {...commonProps} />
      
      case 'number_range':
        return <NumberWithRange key={field.id} field={field} {...commonProps} />
      
      case 'photo_upload':
        return <PhotoItem key={field.id} field={field} {...commonProps} />
      
      case 'text_note':
        return <NoteItem key={field.id} field={field} {...commonProps} />
      
      default:
        return (
          <div key={field.id} className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">
              Nem támogatott mező típus: {(field as any).type}
            </p>
          </div>
        )
    }
  }, [formData, errors, disabled, handleFieldChange])

  const isFormValid = Object.keys(errors).length === 0

  return (
    <div className={`dynamic-form-renderer ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Form header */}
        <div className="text-center border-b pb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {template.name}
          </h2>
          {template.description && (
            <p className="text-gray-600 max-w-2xl mx-auto">
              {template.description}
            </p>
          )}
        </div>

        {/* Form sections */}
        {template.sections.map((section, sectionIndex) => (
          <div key={section.id} className="space-y-6">
            {/* Section header */}
            <div className="border-l-4 border-blue-500 pl-4">
              <h3 className="text-lg font-medium text-gray-900">{section.title}</h3>
              {section.description && (
                <p className="text-sm text-gray-600 mt-1">{section.description}</p>
              )}
            </div>

            {/* Section fields */}
            <div className="grid gap-6 grid-cols-1 md:grid-cols-2">
              {section.fields.map(field => (
                <div 
                  key={field.id}
                  className={`${field.gridColumn === 12 ? 'md:col-span-2' : ''}`}
                >
                  {renderField(field)}
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Form validation summary */}
        {!isFormValid && Object.keys(errors).length > 0 && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
              <div>
                <h4 className="text-sm font-medium text-red-800">
                  Javítandó hibák ({Object.keys(errors).length})
                </h4>
                <ul className="mt-2 text-sm text-red-700 list-disc list-inside space-y-1">
                  {Object.entries(errors).map(([fieldId, fieldErrors]) => {
                    const field = template.sections
                      .flatMap(s => s.fields)
                      .find(f => f.id === fieldId)
                    return fieldErrors.map((error, index) => (
                      <li key={`${fieldId}-${index}`}>
                        <strong>{field?.label}:</strong> {error}
                      </li>
                    ))
                  })}
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Form actions */}
        <div className="flex items-center justify-between pt-6 border-t">
          <div>
            {/* Reset button */}
            <button
              type="button"
              onClick={handleReset}
              disabled={disabled}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Visszaállítás
            </button>
          </div>

          {/* Status and submit */}
          <div className="flex items-center space-x-4">
            {/* Form status */}
            <div className="flex items-center text-sm">
              {!isFormValid && (
                <div className="flex items-center text-red-600">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  {Object.keys(errors).length} hiba
                </div>
              )}
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={disabled || !isFormValid || isSubmitting}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                  Mentés...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Mentés
                </>
              )}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}