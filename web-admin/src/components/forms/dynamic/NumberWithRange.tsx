'use client'

import React, { useState, useEffect } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { AlertCircle, HelpCircle, Minus, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { NumberField, FieldComponentProps } from '@/lib/types/dynamic-forms'

interface NumberWithRangeProps extends FieldComponentProps<number> {
  field: NumberField
}

export function NumberWithRange({ 
  field, 
  value, 
  onChange, 
  onBlur, 
  error = [], 
  warning = [], 
  disabled = false, 
  readonly = false 
}: NumberWithRangeProps) {
  const hasError = error.length > 0
  const hasWarning = warning.length > 0
  const isRequired = field.required
  
  // Normalize value to ensure it's a number
  const normalizedValue = typeof value === 'number' ? value : (field.defaultValue ?? 0)
  
  // Internal state for input display
  const [inputValue, setInputValue] = useState(normalizedValue.toString())
  
  // Sync input value when external value changes
  useEffect(() => {
    setInputValue(normalizedValue.toString())
  }, [normalizedValue])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled || readonly) return
    
    const newValue = e.target.value
    setInputValue(newValue)
    
    // Parse and validate number
    const parsed = parseFloat(newValue)
    if (!isNaN(parsed)) {
      const bounded = boundValue(parsed)
      if (bounded !== normalizedValue) {
        onChange(bounded)
      }
    }
  }

  const handleInputBlur = () => {
    // Ensure input shows the actual bounded value
    setInputValue(normalizedValue.toString())
    onBlur?.()
  }

  const handleSliderChange = (values: number[]) => {
    if (disabled || readonly) return
    
    const newValue = values[0]
    const bounded = boundValue(newValue)
    onChange(bounded)
  }

  const handleStepChange = (direction: 1 | -1) => {
    if (disabled || readonly) return
    
    const step = field.step || 1
    const newValue = normalizedValue + (direction * step)
    const bounded = boundValue(newValue)
    onChange(bounded)
  }

  const boundValue = (val: number): number => {
    let bounded = val
    
    if (field.min !== undefined) {
      bounded = Math.max(bounded, field.min)
    }
    
    if (field.max !== undefined) {
      bounded = Math.min(bounded, field.max)
    }
    
    // Apply precision rounding
    if (field.precision !== undefined) {
      bounded = parseFloat(bounded.toFixed(field.precision))
    }
    
    return bounded
  }

  const formatValue = (val: number): string => {
    let formatted = val.toString()
    
    if (field.precision !== undefined && field.precision > 0) {
      formatted = val.toFixed(field.precision)
    }
    
    if (field.unit) {
      formatted += ` ${field.unit}`
    }
    
    return formatted
  }

  const getSliderProps = () => {
    const min = field.min ?? 0
    const max = field.max ?? 100
    const step = field.step ?? 1
    
    return { min, max, step }
  }

  return (
    <div className={cn(
      'space-y-4 p-4 rounded-lg border transition-colors',
      hasError && 'border-red-200 bg-red-50',
      hasWarning && !hasError && 'border-orange-200 bg-orange-50',
      !hasError && !hasWarning && 'border-gray-200 bg-white hover:border-gray-300',
      disabled && 'opacity-50 cursor-not-allowed',
      readonly && 'bg-gray-50'
    )}>
      {/* Label and Description */}
      <div className="space-y-1">
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
        {field.description && (
          <p className="text-sm text-gray-600">{field.description}</p>
        )}
      </div>

      {/* Input Section */}
      <div className="space-y-3">
        {/* Number Input with Step Controls */}
        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => handleStepChange(-1)}
            disabled={disabled || readonly || (field.min !== undefined && normalizedValue <= field.min)}
            className="h-9 w-9 p-0"
          >
            <Minus className="h-4 w-4" />
          </Button>
          
          <div className="flex-1 relative">
            <Input
              id={field.id}
              type="number"
              value={inputValue}
              onChange={handleInputChange}
              onBlur={handleInputBlur}
              disabled={disabled || readonly}
              min={field.min}
              max={field.max}
              step={field.step}
              className={cn(
                'text-center',
                hasError && 'border-red-500 focus:ring-red-500',
                hasWarning && !hasError && 'border-orange-500 focus:ring-orange-500'
              )}
              placeholder="0"
            />
            {field.unit && (
              <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">
                {field.unit}
              </span>
            )}
          </div>
          
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => handleStepChange(1)}
            disabled={disabled || readonly || (field.max !== undefined && normalizedValue >= field.max)}
            className="h-9 w-9 p-0"
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>

        {/* Slider (if enabled) */}
        {field.showSlider && field.min !== undefined && field.max !== undefined && (
          <div className="space-y-2">
            <Slider
              value={[normalizedValue]}
              onValueChange={handleSliderChange}
              disabled={disabled || readonly}
              {...getSliderProps()}
              className={cn(
                hasError && '[&_[role=slider]]:border-red-500',
                hasWarning && !hasError && '[&_[role=slider]]:border-orange-500'
              )}
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>{formatValue(field.min)}</span>
              <span className="font-medium">{formatValue(normalizedValue)}</span>
              <span>{formatValue(field.max)}</span>
            </div>
          </div>
        )}

        {/* Range Information */}
        {(field.min !== undefined || field.max !== undefined) && (
          <div className="text-xs text-gray-500">
            Tartomány: 
            {field.min !== undefined && (
              <span className="ml-1">min {formatValue(field.min)}</span>
            )}
            {field.min !== undefined && field.max !== undefined && <span> - </span>}
            {field.max !== undefined && (
              <span>max {formatValue(field.max)}</span>
            )}
          </div>
        )}
      </div>
      
      {/* Validation Messages */}
      {hasError && (
        <div className="flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            {error.map((msg, index) => (
              <p key={index} className="text-sm text-red-600">{msg}</p>
            ))}
          </div>
        </div>
      )}
      
      {hasWarning && !hasError && (
        <div className="flex items-start gap-2">
          <HelpCircle className="w-4 h-4 text-orange-500 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            {warning.map((msg, index) => (
              <p key={index} className="text-sm text-orange-600">{msg}</p>
            ))}
          </div>
        </div>
      )}
      
      {/* Required Field Indicator */}
      {isRequired && (normalizedValue === undefined || normalizedValue === null) && (
        <div className="text-xs text-gray-500 italic">
          Ez a mező kitöltése kötelező
        </div>
      )}
      
      {/* Current Value Display */}
      {readonly && (
        <div className="text-sm text-gray-600 font-mono">
          Érték: {formatValue(normalizedValue)}
        </div>
      )}
    </div>
  )
}

// Default value provider
NumberWithRange.getDefaultValue = (field: NumberField): number => {
  return field.defaultValue ?? (field.min ?? 0)
}

// Validation function
NumberWithRange.validate = (field: NumberField, value: number): string[] => {
  const errors: string[] = []
  
  if (field.required && (value === undefined || value === null || isNaN(value))) {
    errors.push(`${field.label} mező kitöltése kötelező`)
  }
  
  if (typeof value === 'number' && !isNaN(value)) {
    if (field.min !== undefined && value < field.min) {
      errors.push(`${field.label} értéke nem lehet kisebb mint ${field.min}`)
    }
    
    if (field.max !== undefined && value > field.max) {
      errors.push(`${field.label} értéke nem lehet nagyobb mint ${field.max}`)
    }
  }
  
  return errors
}

// Export for form engine registration
export const NumberWithRangeConfig = {
  component: NumberWithRange,
  type: 'number' as const,
  getDefaultValue: NumberWithRange.getDefaultValue,
  validate: NumberWithRange.validate
}