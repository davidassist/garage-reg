'use client'

import { useState, useCallback, useMemo } from 'react'
import { Check, ChevronDown, Search, X, AlertCircle } from 'lucide-react'
import { EnumSelectField } from '@/lib/types/dynamic-form'

interface EnumItemProps {
  field: EnumSelectField
  value?: string | string[]
  onChange: (value: string | string[]) => void
  error?: string[]
  disabled?: boolean
  required?: boolean
}

export function EnumItem({ 
  field, 
  value, 
  onChange, 
  error, 
  disabled = false,
  required = false 
}: EnumItemProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [isFocused, setIsFocused] = useState(false)

  const config = field.config
  const isMultiple = config.multiple
  const currentValue = value || (isMultiple ? [] : '')

  // Filter options based on search term
  const filteredOptions = useMemo(() => {
    if (!config.searchable || !searchTerm.trim()) {
      return config.options
    }
    
    return config.options.filter(option =>
      option.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      option.description?.toLowerCase().includes(searchTerm.toLowerCase())
    )
  }, [config.options, config.searchable, searchTerm])

  // Check if option is selected
  const isOptionSelected = useCallback((optionValue: string) => {
    if (isMultiple && Array.isArray(currentValue)) {
      return currentValue.includes(optionValue)
    }
    return currentValue === optionValue
  }, [currentValue, isMultiple])

  // Handle option selection
  const handleOptionSelect = useCallback((optionValue: string) => {
    if (disabled) return

    if (isMultiple && Array.isArray(currentValue)) {
      const newValue = [...currentValue]
      const index = newValue.indexOf(optionValue)
      
      if (index > -1) {
        // Remove if already selected
        newValue.splice(index, 1)
      } else {
        // Add if not selected (check maxSelections)
        if (!config.maxSelections || newValue.length < config.maxSelections) {
          newValue.push(optionValue)
        }
      }
      
      onChange(newValue)
    } else {
      onChange(optionValue)
      setIsOpen(false)
    }
  }, [disabled, isMultiple, currentValue, onChange, config.maxSelections])

  // Handle clear selection
  const handleClear = useCallback(() => {
    onChange(isMultiple ? [] : '')
  }, [isMultiple, onChange])

  // Get selected option labels
  const getSelectedLabels = useCallback(() => {
    if (isMultiple && Array.isArray(currentValue)) {
      return currentValue.map(val => 
        config.options.find(opt => opt.value === val)?.label || val
      )
    } else {
      const option = config.options.find(opt => opt.value === currentValue)
      return option ? [option.label] : []
    }
  }, [currentValue, isMultiple, config.options])

  const renderSelectDropdown = () => {
    const selectedLabels = getSelectedLabels()
    
    return (
      <div className="relative">
        {/* Main select button */}
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          className={`
            relative w-full bg-white border rounded-md py-2 pl-3 pr-10 text-left cursor-default focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500
            ${disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'cursor-pointer hover:bg-gray-50'}
            ${error && error.length > 0 ? 'border-red-300 ring-red-500' : 'border-gray-300'}
            ${isFocused ? 'ring-1 ring-blue-500 border-blue-500' : ''}
          `}
        >
          <span className="block truncate">
            {selectedLabels.length > 0 ? (
              isMultiple && selectedLabels.length > 1 ? (
                `${selectedLabels.length} kiválasztva`
              ) : (
                selectedLabels.join(', ')
              )
            ) : (
              <span className="text-gray-500">{field.placeholder || 'Válasszon...'}</span>
            )}
          </span>
          
          <span className="absolute inset-y-0 right-0 flex items-center pr-2 pointer-events-none">
            <ChevronDown className="w-4 h-4 text-gray-400" />
          </span>
        </button>

        {/* Clear button */}
        {config.clearable && selectedLabels.length > 0 && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="absolute inset-y-0 right-8 flex items-center pr-1 hover:bg-gray-100 rounded"
          >
            <X className="w-4 h-4 text-gray-400 hover:text-gray-600" />
          </button>
        )}

        {/* Dropdown */}
        {isOpen && (
          <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
            {/* Search input */}
            {config.searchable && (
              <div className="p-2 border-b border-gray-200">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Keresés..."
                    className="w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
            )}

            {/* Options */}
            <div className="py-1">
              {filteredOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleOptionSelect(option.value)}
                  disabled={option.disabled}
                  className={`
                    w-full text-left px-3 py-2 text-sm hover:bg-gray-100 focus:bg-gray-100 focus:outline-none flex items-center justify-between
                    ${option.disabled ? 'text-gray-400 cursor-not-allowed' : 'text-gray-900 cursor-pointer'}
                    ${isOptionSelected(option.value) ? 'bg-blue-50 text-blue-900' : ''}
                  `}
                >
                  <div className="flex items-center">
                    {option.icon && (
                      <span className="mr-2 text-base">{option.icon}</span>
                    )}
                    <div>
                      <div className="font-medium">{option.label}</div>
                      {option.description && (
                        <div className="text-xs text-gray-500 mt-0.5">
                          {option.description}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {isOptionSelected(option.value) && (
                    <Check className="w-4 h-4 text-blue-600" />
                  )}
                </button>
              ))}
              
              {filteredOptions.length === 0 && (
                <div className="px-3 py-2 text-sm text-gray-500 text-center">
                  Nincs találat
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  const renderRadioButtons = () => (
    <div className="space-y-3">
      {config.options.map((option) => (
        <label key={option.value} className="flex items-start cursor-pointer">
          <input
            type="radio"
            name={field.id}
            value={option.value}
            checked={isOptionSelected(option.value)}
            onChange={() => handleOptionSelect(option.value)}
            disabled={disabled || option.disabled}
            className={`
              w-4 h-4 text-blue-600 border-gray-300 focus:ring-blue-500 focus:ring-2 mt-0.5
              ${(disabled || option.disabled) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          />
          <div className="ml-3">
            <div className="text-sm font-medium text-gray-700 flex items-center">
              {option.icon && <span className="mr-2">{option.icon}</span>}
              {option.label}
            </div>
            {option.description && (
              <div className="text-xs text-gray-500 mt-0.5">
                {option.description}
              </div>
            )}
          </div>
        </label>
      ))}
    </div>
  )

  const renderCheckboxes = () => (
    <div className="space-y-3">
      {config.options.map((option) => (
        <label key={option.value} className="flex items-start cursor-pointer">
          <input
            type="checkbox"
            value={option.value}
            checked={isOptionSelected(option.value)}
            onChange={() => handleOptionSelect(option.value)}
            disabled={disabled || option.disabled}
            className={`
              w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 mt-0.5
              ${(disabled || option.disabled) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          />
          <div className="ml-3">
            <div className="text-sm font-medium text-gray-700 flex items-center">
              {option.icon && <span className="mr-2">{option.icon}</span>}
              {option.label}
            </div>
            {option.description && (
              <div className="text-xs text-gray-500 mt-0.5">
                {option.description}
              </div>
            )}
          </div>
        </label>
      ))}
    </div>
  )

  const renderButtons = () => (
    <div className="space-y-2">
      {isMultiple && (
        <div className="flex flex-wrap gap-2">
          {config.options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleOptionSelect(option.value)}
              disabled={disabled || option.disabled}
              className={`
                px-3 py-2 text-sm font-medium rounded-md border transition-colors
                ${isOptionSelected(option.value)
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }
                ${(disabled || option.disabled) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              {option.icon && <span className="mr-1">{option.icon}</span>}
              {option.label}
            </button>
          ))}
        </div>
      )}
      
      {!isMultiple && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {config.options.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => handleOptionSelect(option.value)}
              disabled={disabled || option.disabled}
              className={`
                px-3 py-2 text-sm font-medium rounded-md border transition-colors text-left
                ${isOptionSelected(option.value)
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
                }
                ${(disabled || option.disabled) ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
              `}
            >
              <div className="flex items-center">
                {option.icon && <span className="mr-2">{option.icon}</span>}
                <div>
                  <div>{option.label}</div>
                  {option.description && (
                    <div className="text-xs opacity-75 mt-0.5">
                      {option.description}
                    </div>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )

  const renderControl = () => {
    switch (config.style) {
      case 'radio':
        return renderRadioButtons()
      case 'checkbox':
        return renderCheckboxes()
      case 'buttons':
        return renderButtons()
      case 'select':
      default:
        return renderSelectDropdown()
    }
  }

  const selectedLabels = getSelectedLabels()
  const hasMaxSelections = isMultiple && config.maxSelections && 
    Array.isArray(currentValue) && currentValue.length >= config.maxSelections

  return (
    <div className={`dynamic-field enum-select ${field.cssClasses || ''}`}>
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-medium text-gray-700">
          {field.label}
          {required && <span className="text-red-500 ml-1">*</span>}
          {isMultiple && config.maxSelections && (
            <span className="text-xs text-gray-500 ml-2">
              (max {config.maxSelections})
            </span>
          )}
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

      {/* Selection limit warning */}
      {hasMaxSelections && (
        <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-xs text-yellow-700 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            Maximum {config.maxSelections} opció kiválasztható
          </p>
        </div>
      )}

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
      {required && selectedLabels.length === 0 && (
        <div className="mt-2 p-2 bg-orange-50 border border-orange-200 rounded-md">
          <p className="text-xs text-orange-700 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            Ez a mező kötelező - válasszon legalább egy opciót a folytatáshoz
          </p>
        </div>
      )}
    </div>
  )
}