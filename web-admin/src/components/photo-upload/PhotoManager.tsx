'use client'

import React, { useState, useCallback } from 'react'
import { PhotoUploader } from './PhotoUploader'
import { PhotoGallery } from './PhotoGallery'
import { PhotoUpload, UploadError } from '@/lib/types/photo-upload'
import { AlertCircle, CheckCircle, X } from 'lucide-react'

interface PhotoManagerProps {
  initialPhotos?: PhotoUpload[]
  maxFiles?: number
  maxTotalSize?: number
  onPhotosChange?: (photos: PhotoUpload[]) => void
  className?: string
  disabled?: boolean
}

interface NotificationState {
  id: string
  type: 'success' | 'error' | 'info'
  message: string
  details?: string
}

export function PhotoManager({
  initialPhotos = [],
  maxFiles = 20,
  maxTotalSize = 100 * 1024 * 1024, // 100MB
  onPhotosChange,
  className = '',
  disabled = false
}: PhotoManagerProps) {
  const [photos, setPhotos] = useState<PhotoUpload[]>(initialPhotos)
  const [notifications, setNotifications] = useState<NotificationState[]>([])

  // Add notification
  const addNotification = useCallback((type: 'success' | 'error' | 'info', message: string, details?: string) => {
    const id = crypto.randomUUID()
    const notification: NotificationState = { id, type, message, details }
    
    setNotifications(prev => [...prev, notification])
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id))
    }, 5000)
  }, [])

  // Remove notification
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  // Handle upload completion
  const handleUploadComplete = useCallback((uploads: PhotoUpload[]) => {
    setPhotos(prev => {
      const newPhotos = [...prev, ...uploads]
      onPhotosChange?.(newPhotos)
      return newPhotos
    })
    
    if (uploads.length === 1) {
      addNotification('success', `Kép sikeresen feltöltve: ${uploads[0].fileName}`)
    } else {
      addNotification('success', `${uploads.length} kép sikeresen feltöltve`)
    }
  }, [onPhotosChange, addNotification])

  // Handle upload error
  const handleUploadError = useCallback((error: UploadError) => {
    addNotification('error', 'Feltöltési hiba', error.message)
  }, [addNotification])

  // Handle photo deletion
  const handlePhotoDelete = useCallback((photoId: string) => {
    setPhotos(prev => {
      const photo = prev.find(p => p.id === photoId)
      const newPhotos = prev.filter(p => p.id !== photoId)
      onPhotosChange?.(newPhotos)
      
      if (photo) {
        addNotification('info', `Kép törölve: ${photo.fileName}`)
      }
      
      return newPhotos
    })
  }, [onPhotosChange, addNotification])

  // Handle photo editing
  const handlePhotoEdit = useCallback((photoId: string, updatedMetadata: Partial<any>) => {
    setPhotos(prev => {
      const newPhotos = prev.map(photo => 
        photo.id === photoId 
          ? { ...photo, metadata: { ...photo.metadata, ...updatedMetadata } }
          : photo
      )
      onPhotosChange?.(newPhotos)
      return newPhotos
    })
    
    addNotification('success', 'Kép információk frissítve')
  }, [onPhotosChange, addNotification])

  // Calculate statistics
  const totalSize = photos.reduce((sum, photo) => sum + photo.metadata.fileSize, 0)
  const remainingFiles = maxFiles - photos.length
  const remainingSize = maxTotalSize - totalSize

  return (
    <div className={`photo-manager ${className}`}>
      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
          {notifications.map(notification => (
            <div
              key={notification.id}
              className={`
                p-4 rounded-lg shadow-lg border-l-4 bg-white
                ${notification.type === 'success' ? 'border-green-500' : ''}
                ${notification.type === 'error' ? 'border-red-500' : ''}
                ${notification.type === 'info' ? 'border-blue-500' : ''}
              `}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    {notification.type === 'success' && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                    {notification.type === 'error' && (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    )}
                    {notification.type === 'info' && (
                      <AlertCircle className="w-5 h-5 text-blue-500" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className={`
                      text-sm font-medium
                      ${notification.type === 'success' ? 'text-green-800' : ''}
                      ${notification.type === 'error' ? 'text-red-800' : ''}
                      ${notification.type === 'info' ? 'text-blue-800' : ''}
                    `}>
                      {notification.message}
                    </p>
                    
                    {notification.details && (
                      <p className={`
                        text-xs mt-1
                        ${notification.type === 'success' ? 'text-green-600' : ''}
                        ${notification.type === 'error' ? 'text-red-600' : ''}
                        ${notification.type === 'info' ? 'text-blue-600' : ''}
                      `}>
                        {notification.details}
                      </p>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={() => removeNotification(notification.id)}
                  className="flex-shrink-0 ml-2 p-1 text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Statistics */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Képek:</span>
            <span className="ml-2 font-medium">{photos.length}/{maxFiles}</span>
          </div>
          <div>
            <span className="text-gray-600">Összméret:</span>
            <span className="ml-2 font-medium">
              {formatFileSize(totalSize)}/{formatFileSize(maxTotalSize)}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Maradék helyek:</span>
            <span className="ml-2 font-medium">{remainingFiles}</span>
          </div>
          <div>
            <span className="text-gray-600">Maradék méret:</span>
            <span className="ml-2 font-medium">{formatFileSize(remainingSize)}</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4">
          <div className="flex justify-between text-xs text-gray-600 mb-1">
            <span>Felhasznált tárterület</span>
            <span>{Math.round((totalSize / maxTotalSize) * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                totalSize / maxTotalSize > 0.9 ? 'bg-red-500' :
                totalSize / maxTotalSize > 0.7 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min((totalSize / maxTotalSize) * 100, 100)}%` }}
            />
          </div>
        </div>
      </div>

      {/* Photo Uploader */}
      {(!disabled && remainingFiles > 0 && remainingSize > 0) && (
        <div className="mb-8">
          <PhotoUploader
            maxFiles={remainingFiles}
            maxTotalSize={remainingSize}
            onUploadComplete={handleUploadComplete}
            onError={handleUploadError}
            disabled={disabled}
          />
        </div>
      )}

      {/* Quota reached message */}
      {(remainingFiles <= 0 || remainingSize <= 0) && !disabled && (
        <div className="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <AlertCircle className="w-5 h-5 text-yellow-600 mr-2" />
            <div>
              <p className="text-sm font-medium text-yellow-800">
                {remainingFiles <= 0 
                  ? `Elérte a maximum képek számát (${maxFiles})`
                  : `Elérte a maximum tárterület korlátot (${formatFileSize(maxTotalSize)})`
                }
              </p>
              <p className="text-xs text-yellow-600 mt-1">
                Törölj néhány képet további feltöltéshez.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Photo Gallery */}
      <PhotoGallery
        photos={photos}
        onPhotoDelete={handlePhotoDelete}
        onPhotoEdit={handlePhotoEdit}
      />
    </div>
  )
}

// Helper function
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}