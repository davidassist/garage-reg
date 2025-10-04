'use client'

import React, { useState, useRef, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { 
  Upload, 
  X, 
  Eye, 
  Download, 
  Camera, 
  AlertCircle, 
  HelpCircle,
  FileImage,
  Crop
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { PhotoField, FieldComponentProps } from '@/lib/types/dynamic-forms'

interface PhotoFile {
  id: string
  file?: File
  url: string
  name: string
  size: number
  type: string
  preview?: string
}

interface PhotoItemProps extends FieldComponentProps<PhotoFile[]> {
  field: PhotoField
}

export function PhotoItem({ 
  field, 
  value = [], 
  onChange, 
  onBlur, 
  error = [], 
  warning = [], 
  disabled = false, 
  readonly = false 
}: PhotoItemProps) {
  const hasError = error.length > 0
  const hasWarning = warning.length > 0
  const isRequired = field.required
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [dragOver, setDragOver] = useState(false)

  const handleFileSelect = useCallback(async (files: FileList | null) => {
    if (!files || disabled || readonly) return

    const newPhotos: PhotoFile[] = []
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      
      // Validate file type
      if (!field.acceptedFormats.includes(file.type)) {
        continue
      }
      
      // Validate file size
      if (file.size > field.maxSizeKB * 1024) {
        continue
      }
      
      // Check if we're at max files
      if (value.length + newPhotos.length >= field.maxFiles) {
        break
      }

      const photoFile: PhotoFile = {
        id: `photo-${Date.now()}-${i}`,
        file,
        url: URL.createObjectURL(file),
        name: file.name,
        size: file.size,
        type: file.type,
        preview: field.showPreview ? URL.createObjectURL(file) : undefined
      }
      
      newPhotos.push(photoFile)
    }

    if (newPhotos.length > 0) {
      setUploading(true)
      setUploadProgress(0)
      
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval)
            setUploading(false)
            return 100
          }
          return prev + 10
        })
      }, 100)
      
      onChange([...value, ...newPhotos])
      onBlur?.()
    }
  }, [value, onChange, onBlur, field, disabled, readonly])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    handleFileSelect(e.dataTransfer.files)
  }, [handleFileSelect])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    if (!disabled && !readonly) {
      setDragOver(true)
    }
  }, [disabled, readonly])

  const handleDragLeave = useCallback(() => {
    setDragOver(false)
  }, [])

  const handleRemovePhoto = useCallback((photoId: string) => {
    if (disabled || readonly) return
    
    const updatedPhotos = value.filter(photo => photo.id !== photoId)
    
    // Clean up URLs
    const removedPhoto = value.find(photo => photo.id === photoId)
    if (removedPhoto?.url) {
      URL.revokeObjectURL(removedPhoto.url)
    }
    if (removedPhoto?.preview) {
      URL.revokeObjectURL(removedPhoto.preview)
    }
    
    onChange(updatedPhotos)
    onBlur?.()
  }, [value, onChange, onBlur, disabled, readonly])

  const handleViewPhoto = useCallback((photo: PhotoFile) => {
    // Open photo in new window/modal
    window.open(photo.url, '_blank')
  }, [])

  const handleDownloadPhoto = useCallback((photo: PhotoFile) => {
    const link = document.createElement('a')
    link.href = photo.url
    link.download = photo.name
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }, [])

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const canAddMore = value.length < field.maxFiles

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

      {/* Upload Area */}
      {!readonly && canAddMore && (
        <div
          className={cn(
            'border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer',
            dragOver && 'border-primary bg-primary/10',
            !dragOver && 'border-gray-300 hover:border-gray-400',
            hasError && 'border-red-300',
            disabled && 'cursor-not-allowed opacity-50'
          )}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !disabled && fileInputRef.current?.click()}
        >
          <div className="space-y-3">
            <div className="mx-auto w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <Camera className="w-6 h-6 text-gray-400" />
            </div>
            
            <div>
              <p className="text-sm font-medium text-gray-900">
                Kattints a fájl kiválasztásához vagy húzd ide
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {field.acceptedFormats.join(', ')} • Max {formatFileSize(field.maxSizeKB * 1024)}
              </p>
            </div>
            
            <Button 
              type="button" 
              variant="outline" 
              size="sm" 
              disabled={disabled}
              onClick={(e) => {
                e.stopPropagation()
                fileInputRef.current?.click()
              }}
            >
              <Upload className="w-4 h-4 mr-2" />
              Fájl tallózása
            </Button>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple={field.maxFiles > 1}
            accept={field.acceptedFormats.join(',')}
            onChange={(e) => handleFileSelect(e.target.files)}
            className="hidden"
          />
        </div>
      )}

      {/* Upload Progress */}
      {uploading && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Feltöltés...</span>
            <span>{uploadProgress}%</span>
          </div>
          <Progress value={uploadProgress} className="h-2" />
        </div>
      )}

      {/* Photo List */}
      {value.length > 0 && (
        <div className="space-y-3">
          <div className="text-sm font-medium text-gray-700">
            Feltöltött fájlok ({value.length}/{field.maxFiles})
          </div>
          
          <div className={cn(
            'grid gap-3',
            field.showPreview ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3' : 'grid-cols-1'
          )}>
            {value.map((photo) => (
              <div
                key={photo.id}
                className="border rounded-lg p-3 bg-white hover:bg-gray-50 transition-colors"
              >
                {field.showPreview && photo.preview && (
                  <div className="mb-3">
                    <img
                      src={photo.preview}
                      alt={photo.name}
                      className="w-full h-32 object-cover rounded border"
                      loading="lazy"
                    />
                  </div>
                )}
                
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {photo.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(photo.size)} • {photo.type}
                      </p>
                    </div>
                    
                    {!readonly && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => handleRemovePhoto(photo.id)}
                        disabled={disabled}
                        className="h-6 w-6 p-0 text-red-500 hover:text-red-700"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-1">
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleViewPhoto(photo)}
                      className="h-6 px-2 text-xs"
                    >
                      <Eye className="h-3 w-3 mr-1" />
                      Megtekintés
                    </Button>
                    
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDownloadPhoto(photo)}
                      className="h-6 px-2 text-xs"
                    >
                      <Download className="h-3 w-3 mr-1" />
                      Letöltés
                    </Button>
                    
                    {field.allowCrop && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-6 px-2 text-xs"
                        disabled={readonly}
                      >
                        <Crop className="h-3 w-3 mr-1" />
                        Vágás
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* File Constraints Info */}
      <div className="text-xs text-gray-500 space-y-1">
        <div>Max fájlok: {field.maxFiles}</div>
        <div>Max méret: {formatFileSize(field.maxSizeKB * 1024)}</div>
        <div>Formátumok: {field.acceptedFormats.join(', ')}</div>
        {field.minResolution && (
          <div>Min felbontás: {field.minResolution.width}×{field.minResolution.height}px</div>
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
      {isRequired && value.length === 0 && (
        <div className="text-xs text-gray-500 italic">
          Legalább egy fájl feltöltése kötelező
        </div>
      )}
    </div>
  )
}

// Default value provider
PhotoItem.getDefaultValue = (field: PhotoField): PhotoFile[] => {
  return []
}

// Validation function
PhotoItem.validate = (field: PhotoField, value: PhotoFile[]): string[] => {
  const errors: string[] = []
  
  if (field.required && value.length === 0) {
    errors.push(`${field.label} mezőhöz legalább egy fájl feltöltése kötelező`)
  }
  
  if (value.length > field.maxFiles) {
    errors.push(`Maximum ${field.maxFiles} fájl tölthető fel`)
  }
  
  // Validate individual files
  value.forEach((photo, index) => {
    if (photo.size > field.maxSizeKB * 1024) {
      errors.push(`${index + 1}. fájl túl nagy (max ${field.maxSizeKB}KB)`)
    }
    
    if (!field.acceptedFormats.includes(photo.type)) {
      errors.push(`${index + 1}. fájl formátuma nem támogatott`)
    }
  })
  
  return errors
}

// Export for form engine registration
export const PhotoItemConfig = {
  component: PhotoItem,
  type: 'photo' as const,
  getDefaultValue: PhotoItem.getDefaultValue,
  validate: PhotoItem.validate
}