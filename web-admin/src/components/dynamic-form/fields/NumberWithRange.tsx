'use client'

import { useState, useCallback, useEffect, useMemo } from 'react'
import { Minus, Plus, AlertCircle, X, Calculator } from 'lucide-react'
import { NumberRangeField } from '@/lib/types/dynamic-form'

interface NumberWithRangeProps {
  field: NumberRangeField
  value?: number
  onChange: (value: number | undefined) => void
  error?: string[]
  disabled?: boolean
  required?: boolean
}

export function NumberWithRange({ 
  field, 
  value, 
  onChange, 
  error, 
  disabled = false,
  required = false 
}: NumberWithRangeProps) {
  const [inputValue, setInputValue] = useState<string>('')
  const [isFocused, setIsFocused] = useState(false)


  const config = field.config
  const currentValue = value ?? undefined

  // Initialize input value from prop
  useEffect(() => {
    if (currentValue !== undefined) {
      setInputValue(currentValue.toString())
    } else {
      setInputValue('')
    }
  }, [currentValue])

  // Validation helpers
  const minValue = config.min ?? Number.NEGATIVE_INFINITY
  const maxValue = config.max ?? Number.POSITIVE_INFINITY
  const step = config.step ?? 1

  // Calculate slider parameters
  const sliderMin = config.min ?? 0
  const sliderMax = config.max ?? 100
  const sliderValue = currentValue ?? sliderMin

  // Format number according to config
  const formatNumber = useCallback((num: number): string => {
    if (config.precision === 0) {
      return Math.round(num).toString()
    }
    return num.toFixed(config.precision ?? 2)
  }, [config.precision])

  // Parse and validate input
  const parseInput = useCallback((input: string): number | null => {
    if (!input.trim()) return null
    
    const parsed = parseFloat(input)
    if (isNaN(parsed)) return null
    
    return parsed
  }, [])

  // Handle input change
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newInput = e.target.value
    setInputValue(newInput)

    const parsed = parseInput(newInput)
    if (parsed !== null) {
      // Apply constraints
      const constrained = Math.min(maxValue, Math.max(minValue, parsed))
      onChange(constrained)
    } else if (!newInput.trim()) {
      onChange(undefined)
    }
  }, [parseInput, onChange, minValue, maxValue])

  // Handle slider change
  const handleSliderChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value)
    onChange(newValue)
  }, [onChange])

  // Handle increment/decrement
  const handleIncrement = useCallback((direction: 'up' | 'down') => {
    if (disabled) return

    const current = currentValue ?? (direction === 'up' ? minValue : maxValue)
    const change = direction === 'up' ? step : -step
    const newValue = Math.min(maxValue, Math.max(minValue, current + change))
    
    onChange(newValue)
  }, [disabled, currentValue, minValue, maxValue, step, onChange])

  // Handle preset selection
  const handlePresetSelect = useCallback((preset: number) => {
    onChange(preset)
  }, [onChange])

  // Keyboard shortcuts
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (disabled) return

    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault()
        handleIncrement('up')
        break
      case 'ArrowDown':
        e.preventDefault()
        handleIncrement('down')
        break
      case 'Enter':
        e.preventDefault()
        // Validate and format current input
        const parsed = parseInput(inputValue)
        if (parsed !== null) {
          const constrained = Math.min(maxValue, Math.max(minValue, parsed))
          onChange(constrained)
        }
        break
    }
  }, [disabled, handleIncrement, parseInput, inputValue, minValue, maxValue, onChange])

  // Get percentage for slider visualization
  const getPercentage = useCallback((val: number): number => {
    if (sliderMax === sliderMin) return 0
    return ((val - sliderMin) / (sliderMax - sliderMin)) * 100
  }, [sliderMin, sliderMax])

  const renderNumberInput = () => (
    <div className="relative">
      <input
        type="number"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        disabled={disabled}
        placeholder={field.placeholder}
        min={config.min}
        max={config.max}
        step={config.step}
        className={`
          block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm
          ${disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white'}
          ${error && error.length > 0 ? 'border-red-300 ring-red-500' : 'border-gray-300'}
          pr-3
        `}
      />

      {/* Increment/decrement buttons */}
      {config.style === 'input' && !disabled && (
        <div className="absolute inset-y-0 right-0 flex items-center pr-1">
          <div className="flex flex-col">
            <button
              type="button"
              onClick={() => handleIncrement('up')}
              className="px-2 py-1 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
              tabIndex={-1}
            >
              <Plus className="w-3 h-3" />
            </button>
            <button
              type="button"
              onClick={() => handleIncrement('down')}
              className="px-2 py-1 text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600"
              tabIndex={-1}
            >
              <Minus className="w-3 h-3" />
            </button>
          </div>
        </div>
      )}
    </div>
  )

  const renderSlider = () => (
    <div className="space-y-3">
      {/* Slider */}
      <div className="relative">
        <input
          type="range"
          min={sliderMin}
          max={sliderMax}
          step={step}
          value={sliderValue}
          onChange={handleSliderChange}
          disabled={disabled}
          className={`
            w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
            slider-thumb
          `}
        />
        
        {/* Value indicator */}
        <div 
          className="absolute top-0 transform -translate-x-1/2 -translate-y-8"
          style={{ left: `${getPercentage(sliderValue)}%` }}
        >
          <div className="px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded shadow-lg">
            {formatNumber(sliderValue)}
          </div>
        </div>
      </div>

      {/* Range labels */}
      <div className="flex justify-between text-xs text-gray-500">
        <span>{formatNumber(sliderMin)}</span>
        <span>{formatNumber(sliderMax)}</span>
      </div>

      {/* Input field for precise input */}
      <div className="mt-3">
        {renderNumberInput()}
      </div>
    </div>
  )



  const renderControl = () => {
    switch (config.style) {
      case 'slider':
        return renderSlider()
      case 'both':
        return (
          <div className="space-y-3">
            {renderSlider()}
          </div>
        )
      case 'input':
      default:
        return renderNumberInput()
    }
  }

  // Calculate status
  const isValid = currentValue !== undefined && currentValue >= minValue && currentValue <= maxValue
  const isEmpty = currentValue === undefined

  return (
    <div className={`dynamic-field number-with-range ${field.cssClasses || ''}`}>
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-medium text-gray-700">
          {field.label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        {/* Range info */}
        {(config.min !== undefined || config.max !== undefined) && (
          <span className="text-xs text-gray-500">
            {config.min !== undefined && config.max !== undefined
              ? `${formatNumber(config.min)} - ${formatNumber(config.max)}`
              : config.min !== undefined
              ? `min: ${formatNumber(config.min)}`
              : `max: ${formatNumber(config.max)}`
            }
          </span>
        )}
      </div>

      {/* Description */}
      {field.description && (
        <p className="text-xs text-gray-600 mb-3">{field.description}</p>
      )}

      {/* Control */}
      <div className="mb-2">
        {renderControl()}
      </div>

      {/* Unit indicator */}
      {config.unit && currentValue !== undefined && (
        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-xs text-blue-700">
            Érték: {formatNumber(currentValue)} {config.unit}
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
      {required && isEmpty && (
        <div className="mt-2 p-2 bg-orange-50 border border-orange-200 rounded-md">
          <p className="text-xs text-orange-700 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            Ez a mező kötelező - adjon meg egy érvényes értéket a folytatáshoz
          </p>
        </div>
      )}

      {/* Range constraint warning */}
      {currentValue !== undefined && !isValid && (
        <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-xs text-yellow-700 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            Az érték {minValue} és {maxValue} között kell lennie
          </p>
        </div>
      )}
    </div>
  )
}