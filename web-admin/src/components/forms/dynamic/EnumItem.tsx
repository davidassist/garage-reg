'use client'

import React from 'react'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group'
import { AlertCircle, HelpCircle, ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { EnumField, FieldComponentProps } from '@/lib/types/dynamic-forms'

interface EnumItemProps extends FieldComponentProps<string | string[]> {
  field: EnumField
}

export function EnumItem({ 
  field, 
  value, 
  onChange, 
  onBlur, 
  error = [], 
  warning = [], 
  disabled = false, 
  readonly = false 
}: EnumItemProps) {
  const hasError = error.length > 0
  const hasWarning = warning.length > 0
  const isRequired = field.required
  const isMultiple = field.allowMultiple

  // Ensure value is in the correct format
  const normalizedValue = isMultiple 
    ? (Array.isArray(value) ? value : (value ? [value] : [])) 
    : (Array.isArray(value) ? value[0] || '' : value || '')

  const handleSingleChange = (newValue: string) => {
    if (disabled || readonly) return
    onChange(newValue)
    onBlur?.()
  }

  const handleMultipleChange = (optionValue: string, checked: boolean) => {
    if (disabled || readonly) return
    
    const currentValues = Array.isArray(normalizedValue) ? normalizedValue : []
    let newValues: string[]
    
    if (checked) {
      newValues = [...currentValues, optionValue]
    } else {
      newValues = currentValues.filter(v => v !== optionValue)
    }
    
    onChange(newValues)
    onBlur?.()
  }

  const renderSelect = () => (
    <div className="space-y-2">
      <Label
        htmlFor={field.id}
        className={cn(
          'text-sm font-medium',
          hasError && 'text-red-700',
          hasWarning && !hasError && 'text-orange-700',
          isRequired && "after:content-['*'] after:ml-0.5 after:text-red-500"
        )}
      >
        {field.label}
      </Label>
      <Select
        value={normalizedValue as string}
        onValueChange={handleSingleChange}
        disabled={disabled || readonly}
      >
        <SelectTrigger
          className={cn(
            hasError && 'border-red-500 focus:ring-red-500',
            hasWarning && !hasError && 'border-orange-500 focus:ring-orange-500'
          )}
        >
          <SelectValue placeholder="Válassz..." />
        </SelectTrigger>
        <SelectContent>
          {field.options.map((option) => (
            <SelectItem
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              <div className="flex flex-col">
                <span>{option.label}</span>
                {option.description && (
                  <span className="text-xs text-gray-500">{option.description}</span>
                )}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )

  const renderRadio = () => (
    <div className="space-y-3">
      <Label
        className={cn(
          'text-sm font-medium',
          hasError && 'text-red-700',
          hasWarning && !hasError && 'text-orange-700',
          isRequired && "after:content-['*'] after:ml-0.5 after:text-red-500"
        )}
      >
        {field.label}
      </Label>
      <RadioGroup
        value={normalizedValue as string}
        onValueChange={handleSingleChange}
        disabled={disabled || readonly}
        className="space-y-2"
      >
        {field.options.map((option) => (
          <div key={option.value} className="flex items-center space-x-2">
            <RadioGroupItem
              value={option.value}
              id={`${field.id}-${option.value}`}
              disabled={option.disabled || disabled || readonly}
              className={cn(
                hasError && 'border-red-500 text-red-600',
                hasWarning && !hasError && 'border-orange-500 text-orange-600'
              )}
            />
            <Label
              htmlFor={`${field.id}-${option.value}`}
              className={cn(
                'text-sm font-normal cursor-pointer',
                option.disabled && 'text-gray-400 cursor-not-allowed'
              )}
            >
              <div>
                <div>{option.label}</div>
                {option.description && (
                  <div className="text-xs text-gray-500 mt-1">{option.description}</div>
                )}
              </div>
            </Label>
          </div>
        ))}
      </RadioGroup>
    </div>
  )

  const renderCheckboxes = () => (
    <div className="space-y-3">
      <Label
        className={cn(
          'text-sm font-medium',
          hasError && 'text-red-700',
          hasWarning && !hasError && 'text-orange-700',
          isRequired && "after:content-['*'] after:ml-0.5 after:text-red-500"
        )}
      >
        {field.label}
      </Label>
      <div className="space-y-2">
        {field.options.map((option) => {
          const isChecked = Array.isArray(normalizedValue) 
            ? normalizedValue.includes(option.value)
            : normalizedValue === option.value
            
          return (
            <div key={option.value} className="flex items-center space-x-2">
              <Checkbox
                id={`${field.id}-${option.value}`}
                checked={isChecked}
                onChange={(e) => handleMultipleChange(option.value, e.target.checked)}
                disabled={option.disabled || disabled || readonly}
                className={cn(
                  hasError && 'border-red-500 data-[state=checked]:bg-red-600',
                  hasWarning && !hasError && 'border-orange-500 data-[state=checked]:bg-orange-600'
                )}
              />
              <Label
                htmlFor={`${field.id}-${option.value}`}
                className={cn(
                  'text-sm font-normal cursor-pointer',
                  option.disabled && 'text-gray-400 cursor-not-allowed'
                )}
              >
                <div>
                  <div>{option.label}</div>
                  {option.description && (
                    <div className="text-xs text-gray-500 mt-1">{option.description}</div>
                  )}
                </div>
              </Label>
            </div>
          )
        })}
      </div>
    </div>
  )

  const renderField = () => {
    if (isMultiple || field.displayStyle === 'checkbox') {
      return renderCheckboxes()
    }
    
    if (field.displayStyle === 'radio') {
      return renderRadio()
    }
    
    return renderSelect()
  }

  return (
    <div className={cn(
      'space-y-3 p-4 rounded-lg border transition-colors',
      hasError && 'border-red-200 bg-red-50',
      hasWarning && !hasError && 'border-orange-200 bg-orange-50',
      !hasError && !hasWarning && 'border-gray-200 bg-white hover:border-gray-300',
      disabled && 'opacity-50 cursor-not-allowed',
      readonly && 'bg-gray-50'
    )}>
      {renderField()}
      
      {field.description && (
        <p className="text-sm text-gray-600">{field.description}</p>
      )}
      
      {/* Validation Messages */}
      {hasError && (
        <div className="flex items-start gap-2 mt-2">
          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            {error.map((msg, index) => (
              <p key={index} className="text-sm text-red-600">{msg}</p>
            ))}
          </div>
        </div>
      )}
      
      {hasWarning && !hasError && (
        <div className="flex items-start gap-2 mt-2">
          <HelpCircle className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            {warning.map((msg, index) => (
              <p key={index} className="text-sm text-orange-600">{msg}</p>
            ))}
          </div>
        </div>
      )}
      
      {/* Required Field Indicator */}
      {isRequired && (!normalizedValue || (Array.isArray(normalizedValue) && normalizedValue.length === 0)) && (
        <div className="text-xs text-gray-500 italic">
          Ez a mező kitöltése kötelező
        </div>
      )}
      
      {/* Current Value Display */}
      {readonly && (
        <div className="text-sm text-gray-600 font-mono">
          Érték: {Array.isArray(normalizedValue) 
            ? normalizedValue.map(v => field.options.find(o => o.value === v)?.label || v).join(', ') 
            : field.options.find(o => o.value === normalizedValue)?.label || normalizedValue}
        </div>
      )}
    </div>
  )
}

// Default value provider
EnumItem.getDefaultValue = (field: EnumField): string | string[] => {
  if (field.allowMultiple) {
    return []
  }
  return field.defaultValue ?? ''
}

// Validation function
EnumItem.validate = (field: EnumField, value: string | string[]): string[] => {
  const errors: string[] = []
  
  if (field.required) {
    if (field.allowMultiple) {
      if (!Array.isArray(value) || value.length === 0) {
        errors.push(`${field.label} mezőben legalább egy opciót ki kell választani`)
      }
    } else {
      if (!value || value === '') {
        errors.push(`${field.label} mező kitöltése kötelező`)
      }
    }
  }
  
  // Validate that selected values exist in options
  const validValues = field.options.map(o => o.value)
  const valuesToCheck = Array.isArray(value) ? value : [value].filter(Boolean)
  
  for (const val of valuesToCheck) {
    if (!validValues.includes(val)) {
      errors.push(`Érvénytelen érték: ${val}`)
    }
  }
  
  return errors
}

// Export for form engine registration
export const EnumItemConfig = {
  component: EnumItem,
  type: 'enum' as const,
  getDefaultValue: EnumItem.getDefaultValue,
  validate: EnumItem.validate
}