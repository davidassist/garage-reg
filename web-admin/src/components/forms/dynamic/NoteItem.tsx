'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { 
  AlertCircle, 
  HelpCircle, 
  Bold, 
  Italic, 
  List,
  Eye,
  Edit,
  Save,
  X
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { NoteField, FieldComponentProps } from '@/lib/types/dynamic-forms'

interface NoteItemProps extends FieldComponentProps<string> {
  field: NoteField
}

export function NoteItem({ 
  field, 
  value = '', 
  onChange, 
  onBlur, 
  error = [], 
  warning = [], 
  disabled = false, 
  readonly = false 
}: NoteItemProps) {
  const hasError = error.length > 0
  const hasWarning = warning.length > 0
  const isRequired = field.required
  
  const [localValue, setLocalValue] = useState(value)
  const [isPreviewMode, setIsPreviewMode] = useState(false)
  const [characterCount, setCharacterCount] = useState(value.length)

  // Sync local value with external value
  useEffect(() => {
    setLocalValue(value)
    setCharacterCount(value.length)
  }, [value])

  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (disabled || readonly) return
    
    const newValue = e.target.value
    
    // Enforce max length
    if (field.maxLength && newValue.length > field.maxLength) {
      return
    }
    
    setLocalValue(newValue)
    setCharacterCount(newValue.length)
    onChange(newValue)
  }, [disabled, readonly, field.maxLength, onChange])

  const handleBlur = useCallback(() => {
    onBlur?.()
  }, [onBlur])

  const handleInsertMarkdown = useCallback((markdown: string) => {
    if (disabled || readonly || !field.allowMarkdown) return
    
    // Get textarea element for cursor position
    const textarea = document.getElementById(field.id) as HTMLTextAreaElement
    if (!textarea) return
    
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = localValue.substring(start, end)
    
    let newText = ''
    switch (markdown) {
      case 'bold':
        newText = `**${selectedText || 'szöveg'}**`
        break
      case 'italic':
        newText = `*${selectedText || 'szöveg'}*`
        break
      case 'list':
        newText = selectedText ? selectedText.split('\n').map(line => `- ${line}`).join('\n') : '- lista elem'
        break
    }
    
    const newValue = localValue.substring(0, start) + newText + localValue.substring(end)
    
    if (!field.maxLength || newValue.length <= field.maxLength) {
      setLocalValue(newValue)
      setCharacterCount(newValue.length)
      onChange(newValue)
      
      // Restore cursor position
      setTimeout(() => {
        textarea.selectionStart = start + newText.length
        textarea.selectionEnd = start + newText.length
        textarea.focus()
      }, 0)
    }
  }, [disabled, readonly, field, localValue, onChange])

  const renderMarkdown = (text: string): string => {
    if (!field.allowMarkdown) return text
    
    let html = text
    
    // Basic markdown rendering
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>')
    html = html.replace(/^- (.*$)/gim, '<li>$1</li>')
    
    // Convert consecutive list items to unordered list
    if (html.includes('<li>')) {
      html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>')
    }
    
    html = html.replace(/\n/g, '<br>')
    
    return html
  }

  const getCharacterCountColor = (): string => {
    const percentage = (characterCount / field.maxLength) * 100
    if (percentage >= 95) return 'text-red-500'
    if (percentage >= 80) return 'text-orange-500'
    return 'text-gray-500'
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
        <div className="flex items-center justify-between">
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
          
          {field.allowMarkdown && !readonly && (
            <div className="flex items-center gap-1">
              {!isPreviewMode && (
                <>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleInsertMarkdown('bold')}
                    disabled={disabled}
                    className="h-6 w-6 p-0"
                    title="Félkövér"
                  >
                    <Bold className="h-3 w-3" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleInsertMarkdown('italic')}
                    disabled={disabled}
                    className="h-6 w-6 p-0"
                    title="Dőlt"
                  >
                    <Italic className="h-3 w-3" />
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleInsertMarkdown('list')}
                    disabled={disabled}
                    className="h-6 w-6 p-0"
                    title="Lista"
                  >
                    <List className="h-3 w-3" />
                  </Button>
                  <div className="w-px h-4 bg-gray-300" />
                </>
              )}
              
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => setIsPreviewMode(!isPreviewMode)}
                disabled={disabled}
                className="h-6 px-2 text-xs"
              >
                {isPreviewMode ? (
                  <>
                    <Edit className="h-3 w-3 mr-1" />
                    Szerkesztés
                  </>
                ) : (
                  <>
                    <Eye className="h-3 w-3 mr-1" />
                    Előnézet
                  </>
                )}
              </Button>
            </div>
          )}
        </div>
        
        {field.description && (
          <p className="text-sm text-gray-600">{field.description}</p>
        )}
      </div>

      {/* Input Area */}
      {!readonly && !isPreviewMode ? (
        <div className="space-y-2">
          <Textarea
            id={field.id}
            value={localValue}
            onChange={handleChange}
            onBlur={handleBlur}
            disabled={disabled}
            placeholder={field.placeholder || 'Írja be a megjegyzését...'}
            rows={field.rows}
            maxLength={field.maxLength}
            className={cn(
              'resize-none',
              hasError && 'border-red-500 focus:ring-red-500',
              hasWarning && !hasError && 'border-orange-500 focus:ring-orange-500'
            )}
          />
          
          {/* Character Counter */}
          {field.showCharCount && (
            <div className="flex justify-between items-center text-xs">
              <span className="text-gray-500">
                {field.minLength > 0 && (
                  <>Min {field.minLength} karakter • </>
                )}
                {field.allowMarkdown && 'Markdown támogatott'}
              </span>
              <span className={getCharacterCountColor()}>
                {characterCount}/{field.maxLength}
              </span>
            </div>
          )}
        </div>
      ) : (
        /* Preview/Readonly Display */
        <div className={cn(
          'min-h-[80px] p-3 border rounded-md bg-gray-50',
          isPreviewMode && 'bg-white border-dashed'
        )}>
          {localValue ? (
            <div 
              className="text-sm text-gray-900 leading-relaxed"
              dangerouslySetInnerHTML={{ 
                __html: field.allowMarkdown ? renderMarkdown(localValue) : localValue.replace(/\n/g, '<br>')
              }}
            />
          ) : (
            <div className="text-sm text-gray-400 italic">
              {isPreviewMode ? 'Nincs tartalom az előnézethez' : 'Nincs megjegyzés'}
            </div>
          )}
        </div>
      )}
      
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
      {isRequired && (!localValue || localValue.length < field.minLength) && (
        <div className="text-xs text-gray-500 italic">
          {field.minLength > 0 
            ? `Legalább ${field.minLength} karakter megadása kötelező`
            : 'Ez a mező kitöltése kötelező'
          }
        </div>
      )}
      
      {/* Readonly Value Display */}
      {readonly && (
        <div className="text-sm text-gray-600 font-mono">
          Hossz: {characterCount} karakter
          {field.allowMarkdown && localValue.includes('*') && ' (Markdown formázva)'}
        </div>
      )}
    </div>
  )
}

// Default value provider
NoteItem.getDefaultValue = (field: NoteField): string => {
  return field.defaultValue ?? ''
}

// Validation function
NoteItem.validate = (field: NoteField, value: string): string[] => {
  const errors: string[] = []
  
  if (field.required && (!value || value.trim().length === 0)) {
    errors.push(`${field.label} mező kitöltése kötelező`)
  }
  
  if (value && value.length < field.minLength) {
    errors.push(`${field.label} legalább ${field.minLength} karakter hosszú kell legyen`)
  }
  
  if (value && value.length > field.maxLength) {
    errors.push(`${field.label} maximum ${field.maxLength} karakter hosszú lehet`)
  }
  
  return errors
}

// Export for form engine registration
export const NoteItemConfig = {
  component: NoteItem,
  type: 'note' as const,
  getDefaultValue: NoteItem.getDefaultValue,
  validate: NoteItem.validate
}