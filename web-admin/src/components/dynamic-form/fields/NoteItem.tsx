'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { 
  Type, 
  AlignLeft, 
  Bold, 
  Italic, 
  List, 
  Hash, 
  AtSign, 
  X, 
  AlertCircle,
  Eye,
  EyeOff
} from 'lucide-react'
import { TextNoteField } from '@/lib/types/dynamic-form'

interface NoteItemProps {
  field: TextNoteField
  value?: string
  onChange: (value: string) => void
  error?: string[]
  disabled?: boolean
  required?: boolean
}

export function NoteItem({ 
  field, 
  value = '', 
  onChange, 
  error, 
  disabled = false,
  required = false 
}: NoteItemProps) {
  const [isFocused, setIsFocused] = useState(false)
  const [showPreview, setShowPreview] = useState(false)
  const [textareaHeight, setTextareaHeight] = useState<number>()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const config = field.config || {
    minLength: 0,
    maxLength: 500,
    rows: 3,
    showCounter: true,
    autoResize: true,
    spellCheck: true,
    richText: false,
    mentions: false,
    hashtags: false
  }

  // Auto-resize textarea
  useEffect(() => {
    if (config.autoResize && textareaRef.current) {
      const textarea = textareaRef.current
      textarea.style.height = 'auto'
      const scrollHeight = textarea.scrollHeight
      const newHeight = Math.max(scrollHeight, config.rows * 24) // Assuming ~24px per row
      setTextareaHeight(newHeight)
      textarea.style.height = `${newHeight}px`
    }
  }, [value, config.autoResize, config.rows])

  // Handle input change
  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value
    
    // Apply max length constraint
    if (newValue.length <= config.maxLength) {
      onChange(newValue)
    }
  }, [onChange, config.maxLength])

  // Handle key shortcuts for rich text
  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (!config.richText || disabled) return

    // Bold: Ctrl/Cmd + B
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
      e.preventDefault()
      insertFormatting('**', '**', 'Félkövér szöveg')
    }
    
    // Italic: Ctrl/Cmd + I
    if ((e.ctrlKey || e.metaKey) && e.key === 'i') {
      e.preventDefault()
      insertFormatting('*', '*', 'Dőlt szöveg')
    }

    // List: Ctrl/Cmd + L
    if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
      e.preventDefault()
      insertFormatting('\n- ', '', 'Lista elem')
    }
  }, [config.richText, disabled])

  // Insert formatting around selected text or at cursor position
  const insertFormatting = useCallback((prefix: string, suffix: string, placeholder: string) => {
    if (!textareaRef.current) return

    const textarea = textareaRef.current
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = value.substring(start, end)
    
    const beforeText = value.substring(0, start)
    const afterText = value.substring(end)
    
    const insertText = selectedText || placeholder
    const newValue = beforeText + prefix + insertText + suffix + afterText
    
    if (newValue.length <= config.maxLength) {
      onChange(newValue)
      
      // Set cursor position after formatting
      setTimeout(() => {
        if (selectedText) {
          // If text was selected, position after the formatted text
          textarea.selectionStart = textarea.selectionEnd = start + prefix.length + insertText.length + suffix.length
        } else {
          // If no selection, position between prefix and suffix
          textarea.selectionStart = textarea.selectionEnd = start + prefix.length + insertText.length
        }
        textarea.focus()
      }, 0)
    }
  }, [value, onChange, config.maxLength])

  // Handle mentions and hashtags
  const handleSpecialInput = useCallback((type: 'mention' | 'hashtag') => {
    const symbol = type === 'mention' ? '@' : '#'
    const placeholder = type === 'mention' ? 'felhasználó' : 'címke'
    
    if (!textareaRef.current) return

    const textarea = textareaRef.current
    const start = textarea.selectionStart
    const beforeText = value.substring(0, start)
    const afterText = value.substring(start)
    
    const newValue = beforeText + symbol + placeholder + ' ' + afterText
    
    if (newValue.length <= config.maxLength) {
      onChange(newValue)
      
      // Select the placeholder text
      setTimeout(() => {
        textarea.selectionStart = start + 1
        textarea.selectionEnd = start + 1 + placeholder.length
        textarea.focus()
      }, 0)
    }
  }, [value, onChange, config.maxLength])

  // Process text for preview (basic markdown)
  const processTextForPreview = useCallback((text: string): string => {
    if (!config.richText) return text

    let processed = text
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      // Italic
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Lists
      .replace(/^- (.+)/gm, '• $1')
      // Line breaks
      .replace(/\n/g, '<br>')

    // Hashtags
    if (config.hashtags) {
      processed = processed.replace(/#(\w+)/g, '<span class="text-blue-600 font-medium">#$1</span>')
    }

    // Mentions
    if (config.mentions) {
      processed = processed.replace(/@(\w+)/g, '<span class="text-green-600 font-medium">@$1</span>')
    }

    return processed
  }, [config.richText, config.hashtags, config.mentions])

  // Character count info
  const charCount = value.length
  const charCountColor = charCount > config.maxLength * 0.9 ? 'text-red-600' : 
                        charCount > config.maxLength * 0.7 ? 'text-yellow-600' : 'text-gray-500'

  // Validation status
  const isValid = charCount >= config.minLength && charCount <= config.maxLength
  const isEmpty = charCount === 0

  const renderToolbar = () => {
    if (!config.richText) return null

    return (
      <div className="border-b border-gray-200 p-2 flex items-center space-x-2 bg-gray-50">
        <button
          type="button"
          onClick={() => insertFormatting('**', '**', 'Félkövér szöveg')}
          disabled={disabled}
          className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Félkövér (Ctrl+B)"
        >
          <Bold className="w-4 h-4" />
        </button>
        
        <button
          type="button"
          onClick={() => insertFormatting('*', '*', 'Dőlt szöveg')}
          disabled={disabled}
          className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Dőlt (Ctrl+I)"
        >
          <Italic className="w-4 h-4" />
        </button>
        
        <button
          type="button"
          onClick={() => insertFormatting('\n- ', '', 'Lista elem')}
          disabled={disabled}
          className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
          title="Lista (Ctrl+L)"
        >
          <List className="w-4 h-4" />
        </button>

        <div className="border-l border-gray-300 h-6"></div>

        {config.hashtags && (
          <button
            type="button"
            onClick={() => handleSpecialInput('hashtag')}
            disabled={disabled}
            className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            title="Hashtag beszúrása"
          >
            <Hash className="w-4 h-4" />
          </button>
        )}

        {config.mentions && (
          <button
            type="button"
            onClick={() => handleSpecialInput('mention')}
            disabled={disabled}
            className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-200 rounded disabled:opacity-50 disabled:cursor-not-allowed"
            title="Említés beszúrása"
          >
            <AtSign className="w-4 h-4" />
          </button>
        )}

        <div className="flex-1"></div>

        <button
          type="button"
          onClick={() => setShowPreview(!showPreview)}
          disabled={disabled}
          className={`p-1 rounded disabled:opacity-50 disabled:cursor-not-allowed ${
            showPreview ? 'text-blue-600 bg-blue-100' : 'text-gray-600 hover:text-gray-800 hover:bg-gray-200'
          }`}
          title="Előnézet"
        >
          {showPreview ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
        </button>
      </div>
    )
  }

  const renderTextarea = () => (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      onFocus={() => setIsFocused(true)}
      onBlur={() => setIsFocused(false)}
      disabled={disabled}
      placeholder={field.placeholder}
      rows={config.rows}
      spellCheck={config.spellCheck}
      style={config.autoResize ? { height: textareaHeight } : undefined}
      className={`
        block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm resize-none
        ${disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : 'bg-white'}
        ${error && error.length > 0 ? 'border-red-300 ring-red-500' : ''}
        ${isFocused ? 'ring-1 ring-blue-500 border-blue-500' : ''}
        ${config.richText ? 'rounded-t-none' : ''}
      `}
    />
  )

  const renderPreview = () => (
    <div 
      className="px-3 py-2 border border-gray-300 rounded-md bg-gray-50 min-h-[100px] text-sm text-gray-700"
      dangerouslySetInnerHTML={{ __html: processTextForPreview(value || 'Nincs szöveg az előnézethez...') }}
    />
  )

  return (
    <div className={`dynamic-field text-note ${field.cssClasses || ''}`}>
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-medium text-gray-700">
          {field.label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        {/* Character counter */}
        {config.showCounter && (
          <span className={`text-xs ${charCountColor}`}>
            {charCount}/{config.maxLength}
          </span>
        )}
      </div>

      {/* Description */}
      {field.description && (
        <p className="text-xs text-gray-600 mb-3">{field.description}</p>
      )}

      {/* Rich text toolbar */}
      {config.richText && renderToolbar()}

      {/* Input area */}
      <div className={config.richText ? 'border border-gray-300 rounded-md overflow-hidden' : ''}>
        {showPreview && config.richText ? renderPreview() : renderTextarea()}
      </div>

      {/* Length constraints */}
      {config.minLength > 0 && charCount < config.minLength && (
        <div className="mt-1 text-xs text-gray-500">
          Minimum {config.minLength} karakter szükséges
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
            Ez a mező kötelező - írjon be szöveget a folytatáshoz
          </p>
        </div>
      )}

      {/* Length validation warning */}
      {!isEmpty && !isValid && (
        <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-xs text-yellow-700 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            {charCount < config.minLength 
              ? `Legalább ${config.minLength} karakter szükséges (${config.minLength - charCount} hiányzik)`
              : `Maximum ${config.maxLength} karakter engedélyezett (${charCount - config.maxLength} túllépés)`
            }
          </p>
        </div>
      )}

      {/* Rich text help */}
      {config.richText && !showPreview && (
        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-md">
          <p className="text-xs text-blue-700">
            <strong>Formázás:</strong> **félkövér**, *dőlt*, - lista
            {config.mentions && ', @említés'}
            {config.hashtags && ', #hashtag'}
          </p>
        </div>
      )}
    </div>
  )
}