'use client'

import React from 'react'
import { Switch } from '@/components/ui/switch'
import { Checkbox } from '@/components/ui/checkbox'
import { Label } from '@/components/ui/label'
import { AlertCircle, HelpCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { BoolField, FieldComponentProps } from '@/lib/types/dynamic-forms'

interface BoolSwitchItemProps extends FieldComponentProps<boolean> {
  field: BoolField
}

export function BoolSwitchItem({ 
  field, 
  value = false, 
  onChange, 
  onBlur, 
  error = [], 
  warning = [], 
  disabled = false, 
  readonly = false 
}: BoolSwitchItemProps) {
  const hasError = error.length > 0
  const hasWarning = warning.length > 0
  const isRequired = field.required

  const handleChange = (checked: boolean) => {
    if (disabled || readonly) return
    onChange(checked)
    onBlur?.()
  }

  const renderSwitch = () => {
    if (field.switchStyle === 'checkbox') {
      return (
        <div className="flex items-center space-x-2">
          <Checkbox
            id={field.id}
            checked={value}
            onChange={(e) => handleChange(e.target.checked)}
            disabled={disabled || readonly}
            className={cn(
              hasError && 'border-red-500 data-[state=checked]:bg-red-600',
              hasWarning && !hasError && 'border-orange-500 data-[state=checked]:bg-orange-600'
            )}
          />
          <Label
            htmlFor={field.id}
            className={cn(
              'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
              hasError && 'text-red-700',
              hasWarning && !hasError && 'text-orange-700',
              isRequired && "after:content-['*'] after:ml-0.5 after:text-red-500"
            )}
          >
            {field.label}
          </Label>
        </div>
      )
    }

    return (
      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <Label
            htmlFor={field.id}
            className={cn(
              'text-base font-medium',
              hasError && 'text-red-700',
              hasWarning && !hasError && 'text-orange-700',
              isRequired && "after:content-['*'] after:ml-0.5 after:text-red-500"
            )}
          >
            {field.label}
          </Label>
          {field.description && (
            <p className="text-sm text-gray-600">{field.description}</p>
          )}
        </div>
        <Switch
          id={field.id}
          checked={value}
          onChange={(e) => handleChange(e.target.checked)}
          disabled={disabled || readonly}
          className={cn(
            hasError && 'data-[state=checked]:bg-red-600',
            hasWarning && !hasError && 'data-[state=checked]:bg-orange-600'
          )}
        />
      </div>
    )
  }

  return (
    <div className={cn(
      'space-y-2 p-3 rounded-lg border transition-colors',
      hasError && 'border-red-200 bg-red-50',
      hasWarning && !hasError && 'border-orange-200 bg-orange-50',
      !hasError && !hasWarning && 'border-gray-200 bg-white hover:border-gray-300',
      disabled && 'opacity-50 cursor-not-allowed',
      readonly && 'bg-gray-50'
    )}>
      {renderSwitch()}
      
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
      {isRequired && !value && (
        <div className="text-xs text-gray-500 italic">
          Ez a mező kitöltése kötelező
        </div>
      )}
      
      {/* Current Value Display */}
      {readonly && (
        <div className="text-sm text-gray-600 font-mono">
          Érték: {value ? 'Igen' : 'Nem'}
        </div>
      )}
    </div>
  )
}

// Default value provider
BoolSwitchItem.getDefaultValue = (field: BoolField): boolean => {
  return field.defaultValue ?? false
}

// Validation function
BoolSwitchItem.validate = (field: BoolField, value: boolean): string[] => {
  const errors: string[] = []
  
  if (field.required && !value) {
    errors.push(`${field.label} mező kitöltése kötelező`)
  }
  
  return errors
}

// Export for form engine registration
export const BoolSwitchItemConfig = {
  component: BoolSwitchItem,
  type: 'bool' as const,
  getDefaultValue: BoolSwitchItem.getDefaultValue,
  validate: BoolSwitchItem.validate
}