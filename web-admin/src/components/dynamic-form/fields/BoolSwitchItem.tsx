'use client'

import { useState, useCallback } from 'react'
import { Check, X } from 'lucide-react'
import { BooleanSwitchField } from '@/lib/types/dynamic-form'

interface BoolSwitchItemProps {
  field: BooleanSwitchField
  value?: boolean
  onChange: (value: boolean) => void
  error?: string[]
  disabled?: boolean
  required?: boolean
}

export function BoolSwitchItem({ 
  field, 
  value = false, 
  onChange, 
  error, 
  disabled = false,
  required = false 
}: BoolSwitchItemProps) {
  const [isFocused, setIsFocused] = useState(false)
  
  const config = field.config || {
    trueLabel: 'Igen',
    falseLabel: 'Nem',
    style: 'switch',
    size: 'medium'
  }

  const handleChange = useCallback((newValue: boolean) => {
    if (!disabled) {
      onChange(newValue)
    }
  }, [disabled, onChange])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === ' ' || e.key === 'Enter') {
      e.preventDefault()
      handleChange(!value)
    }
  }, [value, handleChange])

  const renderSwitch = () => {
    const sizeClasses = {
      small: 'w-10 h-6',
      medium: 'w-12 h-7',
      large: 'w-14 h-8'
    }

    const thumbSizeClasses = {
      small: 'w-4 h-4',
      medium: 'w-5 h-5',
      large: 'w-6 h-6'
    }

    const translateClasses = {
      small: value ? 'translate-x-4' : 'translate-x-1',
      medium: value ? 'translate-x-5' : 'translate-x-1',
      large: value ? 'translate-x-6' : 'translate-x-1'
    }

    return (
      <div
        role="switch"
        aria-checked={value}
        tabIndex={disabled ? -1 : 0}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        onClick={() => handleChange(!value)}
        className={`
          relative inline-flex items-center cursor-pointer transition-colors duration-200 ease-in-out rounded-full
          ${sizeClasses[config.size]}
          ${value 
            ? 'bg-blue-600 hover:bg-blue-700' 
            : 'bg-gray-200 hover:bg-gray-300'
          }
          ${disabled 
            ? 'opacity-50 cursor-not-allowed' 
            : 'cursor-pointer'
          }
          ${isFocused ? 'ring-2 ring-blue-500 ring-offset-2' : ''}
          ${error && error.length > 0 ? 'ring-2 ring-red-500' : ''}
        `}
      >
        <span
          className={`
            inline-block transform transition-transform duration-200 ease-in-out bg-white rounded-full shadow-md
            ${thumbSizeClasses[config.size]}
            ${translateClasses[config.size]}
          `}
        >
          {config.size !== 'small' && (
            <span className="flex items-center justify-center h-full">
              {value ? (
                <Check className="w-3 h-3 text-blue-600" />
              ) : (
                <X className="w-3 h-3 text-gray-400" />
              )}
            </span>
          )}
        </span>
      </div>
    )
  }

  const renderCheckbox = () => (
    <label className="flex items-center cursor-pointer">
      <input
        type="checkbox"
        checked={value}
        onChange={(e) => handleChange(e.target.checked)}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        disabled={disabled}
        className={`
          w-5 h-5 text-blue-600 border-2 border-gray-300 rounded focus:ring-blue-500 focus:ring-2
          ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          ${error && error.length > 0 ? 'border-red-500' : ''}
        `}
      />
      <span className="ml-3 text-sm font-medium text-gray-700">
        {value ? config.trueLabel : config.falseLabel}
      </span>
    </label>
  )

  const renderRadio = () => (
    <div className="space-y-3">
      <label className="flex items-center cursor-pointer">
        <input
          type="radio"
          name={field.id}
          checked={value === true}
          onChange={() => handleChange(true)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          className={`
            w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 focus:ring-2
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        />
        <span className="ml-3 text-sm font-medium text-gray-700">
          {config.trueLabel}
        </span>
      </label>
      
      <label className="flex items-center cursor-pointer">
        <input
          type="radio"
          name={field.id}
          checked={value === false}
          onChange={() => handleChange(false)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          className={`
            w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 focus:ring-2
            ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
          `}
        />
        <span className="ml-3 text-sm font-medium text-gray-700">
          {config.falseLabel}
        </span>
      </label>
    </div>
  )

  const renderControl = () => {
    switch (config.style) {
      case 'checkbox':
        return renderCheckbox()
      case 'radio':
        return renderRadio()
      case 'switch':
      default:
        return (
          <div className="flex items-center space-x-3">
            {renderSwitch()}
            <span className="text-sm font-medium text-gray-700">
              {value ? config.trueLabel : config.falseLabel}
            </span>
          </div>
        )
    }
  }

  return (
    <div className={`dynamic-field boolean-switch ${field.cssClasses || ''}`}>
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-medium text-gray-700">
          {field.label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      </div>

      {/* Description */}
      {field.description && (
        <p className="text-xs text-gray-600 mb-3">{field.description}</p>
      )}

      {/* Control */}
      <div className="mb-2">
        {renderControl()}
      </div>

      {/* Error Messages */}
      {error && error.length > 0 && (
        <div className="mt-1">
          {error.map((errorMsg, index) => (
            <p key={index} className="text-xs text-red-600 flex items-center">
              <X className="w-3 h-3 mr-1" />
              {errorMsg}
            </p>
          ))}
        </div>
      )}

      {/* Required Field Visual Constraint */}
      {required && !value && (
        <div className="mt-2 p-2 bg-orange-50 border border-orange-200 rounded-md">
          <p className="text-xs text-orange-700 flex items-center">
            <Check className="w-3 h-3 mr-1" />
            Ez a mező kötelező - válasszon egy opciót a folytatáshoz
          </p>
        </div>
      )}
    </div>
  )
}