'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { 
  Camera, 
  Upload, 
  X, 
  AlertCircle, 
  RotateCcw, 
  ZoomIn, 
  Download,
  MapPin,
  Image as ImageIcon,
  Trash2
} from 'lucide-react'
import { PhotoUploadField } from '@/lib/types/dynamic-form'

interface PhotoItemProps {
  field: PhotoUploadField
  value?: string[]
  onChange: (value: string[]) => void
  error?: string[]
  disabled?: boolean
  required?: boolean
}

interface PhotoData {
  id: string
  file: File
  dataUrl: string
  fileName: string
  size: number
  timestamp: number
  gpsCoords?: {
    latitude: number
    longitude: number
  }
  dimensions?: {
    width: number
    height: number
  }
}

export function PhotoItem({ 
  field, 
  value = [], 
  onChange, 
  error, 
  disabled = false,
  required = false 
}: PhotoItemProps) {
  const [photos, setPhotos] = useState<PhotoData[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [previewPhoto, setPreviewPhoto] = useState<PhotoData | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)

  const config = field.config || {
    maxFiles: 5,
    maxFileSize: 10485760,
    allowedTypes: ['image/jpeg', 'image/png', 'image/webp'],
    thumbnailSize: 150,
    showPreview: true,
    captureFromCamera: true,
    gpsCapture: false,
    compressionQuality: 0.8
  }

  // Sync photos with value prop
  useEffect(() => {
    // This would typically load photos from URLs in the value array
    // For now, we'll maintain local state
  }, [value])

  // Validate file
  const validateFile = useCallback((file: File): string[] => {
    const errors: string[] = []
    
    // Check file type
    if (!config.allowedTypes?.includes(file.type)) {
      errors.push(`Nem támogatott fájltípus: ${file.type}`)
    }
    
    // Check file size
    if (file.size > (config.maxFileSize || 10485760)) {
      const maxSizeMB = Math.round((config.maxFileSize || 10485760) / 1024 / 1024)
      errors.push(`A fájl túl nagy (max ${maxSizeMB}MB)`)
    }
    
    return errors
  }, [config])

  // Get image dimensions
  const getImageDimensions = useCallback((file: File): Promise<{ width: number; height: number }> => {
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        resolve({ width: img.naturalWidth, height: img.naturalHeight })
      }
      img.src = URL.createObjectURL(file)
    })
  }, [])

  // Get GPS coordinates (if supported)
  const getGpsCoordinates = useCallback((): Promise<{ latitude: number; longitude: number } | null> => {
    if (!config.gpsCapture || !navigator.geolocation) {
      return Promise.resolve(null)
    }

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          })
        },
        () => resolve(null),
        { timeout: 5000 }
      )
    })
  }, [config.gpsCapture])

  // Process uploaded files
  const processFiles = useCallback(async (files: FileList) => {
    if (disabled || uploading) return

    setUploading(true)
    
    const newPhotos: PhotoData[] = []
    const fileArray = Array.from(files)
    
    for (const file of fileArray) {
      // Check if we've reached max files
      if (photos.length + newPhotos.length >= (config.maxFiles || 5)) {
        break
      }

      // Validate file
      const validationErrors = validateFile(file)
      if (validationErrors.length > 0) {
        continue // Skip invalid files
      }

      try {
        // Get file data URL
        const dataUrl = await new Promise<string>((resolve) => {
          const reader = new FileReader()
          reader.onload = (e) => resolve(e.target?.result as string)
          reader.readAsDataURL(file)
        })

        // Get image dimensions
        const dimensions = await getImageDimensions(file)
        
        // Validate dimensions
        if (config.minWidth && dimensions.width < config.minWidth) continue
        if (config.minHeight && dimensions.height < config.minHeight) continue
        if (config.maxWidth && dimensions.width > config.maxWidth) continue
        if (config.maxHeight && dimensions.height > config.maxHeight) continue

        // Get GPS if enabled
        const gpsCoords = await getGpsCoordinates()

        const photoData: PhotoData = {
          id: `photo_${Date.now()}_${Math.random()}`,
          file,
          dataUrl,
          fileName: file.name,
          size: file.size,
          timestamp: Date.now(),
          gpsCoords: gpsCoords || undefined,
          dimensions
        }

        newPhotos.push(photoData)
      } catch (error) {
        console.error('Error processing file:', file.name, error)
      }
    }

    if (newPhotos.length > 0) {
      const updatedPhotos = [...photos, ...newPhotos]
      setPhotos(updatedPhotos)
      
      // Update parent component with file URLs/data
      const photoUrls = updatedPhotos.map(p => p.dataUrl)
      onChange(photoUrls)
    }

    setUploading(false)
  }, [disabled, uploading, photos, config, validateFile, getImageDimensions, getGpsCoordinates, onChange])

  // Handle file input change
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      processFiles(files)
    }
    // Reset input
    e.target.value = ''
  }, [processFiles])

  // Handle drag and drop
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    
    const files = e.dataTransfer.files
    if (files) {
      processFiles(files)
    }
  }, [processFiles])

  // Remove photo
  const handleRemovePhoto = useCallback((photoId: string) => {
    const updatedPhotos = photos.filter(p => p.id !== photoId)
    setPhotos(updatedPhotos)
    
    const photoUrls = updatedPhotos.map(p => p.dataUrl)
    onChange(photoUrls)
  }, [photos, onChange])

  // Trigger file input
  const triggerFileInput = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  // Trigger camera input
  const triggerCameraInput = useCallback(() => {
    cameraInputRef.current?.click()
  }, [])

  // Format file size
  const formatFileSize = useCallback((bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }, [])

  const renderUploadArea = () => (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        relative border-2 border-dashed rounded-lg p-6 text-center transition-colors
        ${dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300'}
        ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-gray-400'}
      `}
    >
      <div className="space-y-4">
        {/* Upload icon */}
        <div className="mx-auto w-12 h-12 text-gray-400">
          <Upload className="w-full h-full" />
        </div>

        {/* Upload text */}
        <div>
          <p className="text-sm text-gray-600">
            Húzza ide a képeket vagy kattintson a tallózáshoz
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {config.allowedTypes?.join(', ') || 'JPEG, PNG, WebP'} 
            {config.maxFileSize && ` • Max ${Math.round(config.maxFileSize / 1024 / 1024)}MB`}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex justify-center space-x-3">
          <button
            type="button"
            onClick={triggerFileInput}
            disabled={disabled}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <ImageIcon className="w-4 h-4 mr-2" />
            Tallózás
          </button>

          {config.captureFromCamera && (
            <button
              type="button"
              onClick={triggerCameraInput}
              disabled={disabled}
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Camera className="w-4 h-4 mr-2" />
              Kamera
            </button>
          )}
        </div>
      </div>

      {/* Loading overlay */}
      {uploading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
          <div className="text-sm text-gray-600">Feltöltés...</div>
        </div>
      )}
    </div>
  )

  const renderPhotoGrid = () => (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      {photos.map((photo) => (
        <div key={photo.id} className="relative group">
          {/* Photo thumbnail */}
          <div 
            className="relative aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer"
            onClick={() => setPreviewPhoto(photo)}
          >
            <img
              src={photo.dataUrl}
              alt={photo.fileName}
              className="w-full h-full object-cover"
            />
            
            {/* Overlay on hover */}
            <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
              <ZoomIn className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </div>

          {/* Photo info */}
          <div className="mt-2 text-xs text-gray-500">
            <div className="truncate" title={photo.fileName}>
              {photo.fileName}
            </div>
            <div className="flex items-center justify-between">
              <span>{formatFileSize(photo.size)}</span>
              {photo.dimensions && (
                <span>{photo.dimensions.width}×{photo.dimensions.height}</span>
              )}
            </div>
          </div>

          {/* Remove button */}
          {!disabled && (
            <button
              type="button"
              onClick={() => handleRemovePhoto(photo.id)}
              className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
            >
              <X className="w-3 h-3" />
            </button>
          )}

          {/* GPS indicator */}
          {photo.gpsCoords && (
            <div className="absolute bottom-1 left-1 w-5 h-5 bg-green-500 text-white rounded-full flex items-center justify-center">
              <MapPin className="w-3 h-3" />
            </div>
          )}
        </div>
      ))}
    </div>
  )

  const renderPhotoPreview = () => {
    if (!previewPhoto) return null

    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
        <div className="relative max-w-4xl max-h-full bg-white rounded-lg overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="text-lg font-medium text-gray-900 truncate pr-4">
              {previewPhoto.fileName}
            </h3>
            <div className="flex items-center space-x-2">
              <button
                type="button"
                onClick={() => setPreviewPhoto(null)}
                className="p-1 text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Image */}
          <div className="p-4">
            <img
              src={previewPhoto.dataUrl}
              alt={previewPhoto.fileName}
              className="max-w-full max-h-96 mx-auto"
            />
          </div>

          {/* Info */}
          <div className="p-4 border-t bg-gray-50 text-sm text-gray-600">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <strong>Méret:</strong> {formatFileSize(previewPhoto.size)}
              </div>
              {previewPhoto.dimensions && (
                <div>
                  <strong>Felbontás:</strong> {previewPhoto.dimensions.width}×{previewPhoto.dimensions.height}
                </div>
              )}
              <div>
                <strong>Időpont:</strong> {new Date(previewPhoto.timestamp).toLocaleString()}
              </div>
              {previewPhoto.gpsCoords && (
                <div>
                  <strong>GPS:</strong> {previewPhoto.gpsCoords.latitude.toFixed(6)}, {previewPhoto.gpsCoords.longitude.toFixed(6)}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const canAddMore = photos.length < (config.maxFiles || 5)

  return (
    <div className={`dynamic-field photo-upload ${field.cssClasses || ''}`}>
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label className="block text-sm font-medium text-gray-700">
          {field.label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        {/* Photo count */}
        <span className="text-xs text-gray-500">
          {photos.length}/{config.maxFiles || 5}
        </span>
      </div>

      {/* Description */}
      {field.description && (
        <p className="text-xs text-gray-600 mb-3">{field.description}</p>
      )}

      {/* Upload area or photo grid */}
      <div className="space-y-4">
        {/* Show upload area if we can add more */}
        {canAddMore && renderUploadArea()}
        
        {/* Show photos if any */}
        {photos.length > 0 && renderPhotoGrid()}
      </div>

      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept={config.allowedTypes.join(',')}
        multiple
        onChange={handleFileChange}
        className="hidden"
      />
      
      {config.captureFromCamera && (
        <input
          ref={cameraInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          onChange={handleFileChange}
          className="hidden"
        />
      )}

      {/* Photo preview modal */}
      {renderPhotoPreview()}

      {/* Error Messages */}
      {error && error.length > 0 && (
        <div className="mt-2">
          {error.map((errorMsg, index) => (
            <p key={index} className="text-xs text-red-600 flex items-center">
              <X className="w-3 h-3 mr-1" />
              {errorMsg}
            </p>
          ))}
        </div>
      )}

      {/* Required Field Visual Constraint */}
      {required && photos.length === 0 && (
        <div className="mt-2 p-2 bg-orange-50 border border-orange-200 rounded-md">
          <p className="text-xs text-orange-700 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            Ez a mező kötelező - töltsön fel legalább egy képet a folytatáshoz
          </p>
        </div>
      )}

      {/* Max files warning */}
      {photos.length >= (config.maxFiles || 5) && (
        <div className="mt-2 p-2 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-xs text-yellow-700 flex items-center">
            <AlertCircle className="w-3 h-3 mr-1" />
            Elérte a maximum képek számát ({config.maxFiles || 5})
          </p>
        </div>
      )}
    </div>
  )
}