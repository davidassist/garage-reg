'use client'

import React, { useState, useCallback, useEffect, useRef } from 'react'
import {
  X,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Download,
  Share2,
  Info,
  MapPin,
  Camera,
  Calendar,
  Eye,
  Trash2,
  Edit3
} from 'lucide-react'
import { PhotoUpload, PhotoMetadata } from '@/lib/types/photo-upload'

interface PhotoGalleryProps {
  photos: PhotoUpload[]
  onPhotoDelete?: (photoId: string) => void
  onPhotoEdit?: (photoId: string, metadata: Partial<PhotoMetadata>) => void
  className?: string
}

interface LightboxState {
  isOpen: boolean
  currentIndex: number
  zoom: number
  rotation: number
  showInfo: boolean
}

export function PhotoGallery({
  photos,
  onPhotoDelete,
  onPhotoEdit,
  className = ''
}: PhotoGalleryProps) {
  const [lightbox, setLightbox] = useState<LightboxState>({
    isOpen: false,
    currentIndex: 0,
    zoom: 1,
    rotation: 0,
    showInfo: false
  })

  const [selectedPhotos, setSelectedPhotos] = useState<Set<string>>(new Set())
  const [isSelectionMode, setIsSelectionMode] = useState(false)
  const lightboxRef = useRef<HTMLDivElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)

  // Open lightbox
  const openLightbox = useCallback((index: number) => {
    setLightbox(prev => ({
      ...prev,
      isOpen: true,
      currentIndex: index,
      zoom: 1,
      rotation: 0
    }))
    document.body.style.overflow = 'hidden'
  }, [])

  // Close lightbox
  const closeLightbox = useCallback(() => {
    setLightbox(prev => ({ ...prev, isOpen: false }))
    document.body.style.overflow = 'auto'
  }, [])

  // Navigate photos
  const navigatePhoto = useCallback((direction: 'prev' | 'next') => {
    setLightbox(prev => {
      const newIndex = direction === 'next' 
        ? (prev.currentIndex + 1) % photos.length
        : (prev.currentIndex - 1 + photos.length) % photos.length
      
      return {
        ...prev,
        currentIndex: newIndex,
        zoom: 1,
        rotation: 0
      }
    })
  }, [photos.length])

  // Zoom controls
  const handleZoom = useCallback((delta: number) => {
    setLightbox(prev => ({
      ...prev,
      zoom: Math.max(0.5, Math.min(3, prev.zoom + delta))
    }))
  }, [])

  // Rotation control
  const handleRotate = useCallback(() => {
    setLightbox(prev => ({
      ...prev,
      rotation: (prev.rotation + 90) % 360
    }))
  }, [])

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!lightbox.isOpen) return

      switch (e.key) {
        case 'Escape':
          closeLightbox()
          break
        case 'ArrowLeft':
          navigatePhoto('prev')
          break
        case 'ArrowRight':
          navigatePhoto('next')
          break
        case '=':
        case '+':
          handleZoom(0.2)
          break
        case '-':
          handleZoom(-0.2)
          break
        case 'r':
          handleRotate()
          break
        case 'i':
          setLightbox(prev => ({ ...prev, showInfo: !prev.showInfo }))
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [lightbox.isOpen, closeLightbox, navigatePhoto, handleZoom, handleRotate])

  // Photo selection
  const togglePhotoSelection = useCallback((photoId: string) => {
    setSelectedPhotos(prev => {
      const newSet = new Set(prev)
      if (newSet.has(photoId)) {
        newSet.delete(photoId)
      } else {
        newSet.add(photoId)
      }
      
      // Exit selection mode if no photos selected
      if (newSet.size === 0) {
        setIsSelectionMode(false)
      }
      
      return newSet
    })
  }, [])

  // Enter selection mode
  const enterSelectionMode = useCallback(() => {
    setIsSelectionMode(true)
  }, [])

  // Exit selection mode
  const exitSelectionMode = useCallback(() => {
    setIsSelectionMode(false)
    setSelectedPhotos(new Set())
  }, [])

  // Download photo
  const downloadPhoto = useCallback(async (photo: PhotoUpload) => {
    try {
      const response = await fetch(photo.urls.original)
      const blob = await response.blob()
      
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = photo.fileName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }, [])

  // Share photo
  const sharePhoto = useCallback(async (photo: PhotoUpload) => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: photo.fileName,
          url: photo.urls.original
        })
      } catch (error) {
        console.error('Share failed:', error)
      }
    } else {
      // Fallback: copy URL to clipboard
      navigator.clipboard.writeText(photo.urls.original)
    }
  }, [])

  // Format file size
  const formatFileSize = useCallback((bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }, [])

  // Format date
  const formatDate = useCallback((date: Date) => {
    return new Intl.DateTimeFormat('hu-HU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  }, [])

  const currentPhoto = photos[lightbox.currentIndex]

  return (
    <>
      {/* Gallery Grid */}
      <div className={`photo-gallery ${className}`}>
        {/* Toolbar */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <h3 className="text-lg font-medium text-gray-900">
              Képek ({photos.length})
            </h3>
            
            {selectedPhotos.size > 0 && (
              <span className="text-sm text-blue-600">
                {selectedPhotos.size} kiválasztva
              </span>
            )}
          </div>

          <div className="flex items-center space-x-2">
            {!isSelectionMode ? (
              <button
                onClick={enterSelectionMode}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
              >
                <Edit3 className="w-4 h-4 mr-2" />
                Kiválasztás
              </button>
            ) : (
              <>
                <button
                  onClick={exitSelectionMode}
                  className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
                >
                  Mégse
                </button>
                
                {selectedPhotos.size > 0 && (
                  <button
                    onClick={() => {
                      selectedPhotos.forEach(photoId => onPhotoDelete?.(photoId))
                      exitSelectionMode()
                    }}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Törlés ({selectedPhotos.size})
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        {/* Photo Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {photos.map((photo, index) => (
            <div
              key={photo.id}
              className={`
                relative group cursor-pointer rounded-lg overflow-hidden bg-gray-100 aspect-square
                ${isSelectionMode ? 'ring-2 ring-offset-2' : ''}
                ${selectedPhotos.has(photo.id) ? 'ring-blue-500' : 'ring-transparent'}
              `}
              onClick={() => {
                if (isSelectionMode) {
                  togglePhotoSelection(photo.id)
                } else {
                  openLightbox(index)
                }
              }}
            >
              {/* Photo */}
              <img
                src={photo.urls.thumbnail}
                alt={photo.fileName}
                className="w-full h-full object-cover transition-transform group-hover:scale-105"
                loading="lazy"
              />

              {/* Overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-all duration-200 flex items-center justify-center">
                {!isSelectionMode ? (
                  <Eye className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                ) : (
                  <div className={`
                    w-6 h-6 rounded-full border-2 flex items-center justify-center
                    ${selectedPhotos.has(photo.id) 
                      ? 'bg-blue-500 border-blue-500' 
                      : 'bg-white bg-opacity-80 border-gray-300'
                    }
                  `}>
                    {selectedPhotos.has(photo.id) && (
                      <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                )}
              </div>

              {/* File info */}
              <div className="absolute bottom-0 left-0 right-0 p-2 bg-gradient-to-t from-black to-transparent text-white text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                <div className="truncate">{photo.fileName}</div>
                <div>{formatFileSize(photo.metadata.fileSize)}</div>
              </div>

              {/* GPS indicator */}
              {photo.metadata.location && (
                <div className="absolute top-2 right-2 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center opacity-80">
                  <MapPin className="w-3 h-3 text-white" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Empty state */}
        {photos.length === 0 && (
          <div className="text-center py-12">
            <Camera className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500">Még nincsenek feltöltött képek</p>
          </div>
        )}
      </div>

      {/* Lightbox */}
      {lightbox.isOpen && currentPhoto && (
        <div
          ref={lightboxRef}
          className="fixed inset-0 bg-black bg-opacity-95 z-50 flex items-center justify-center"
          onClick={(e) => e.target === lightboxRef.current && closeLightbox()}
        >
          {/* Header */}
          <div className="absolute top-0 left-0 right-0 z-10 p-4 bg-gradient-to-b from-black to-transparent">
            <div className="flex items-center justify-between text-white">
              <div className="flex items-center space-x-4">
                <span className="text-sm">
                  {lightbox.currentIndex + 1} / {photos.length}
                </span>
                <span className="text-sm font-medium">
                  {currentPhoto.fileName}
                </span>
              </div>

              <div className="flex items-center space-x-2">
                {/* Zoom controls */}
                <button
                  onClick={() => handleZoom(-0.2)}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded"
                  title="Kicsinyítés"
                >
                  <ZoomOut className="w-5 h-5" />
                </button>
                
                <span className="text-sm px-2">
                  {Math.round(lightbox.zoom * 100)}%
                </span>
                
                <button
                  onClick={() => handleZoom(0.2)}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded"
                  title="Nagyítás"
                >
                  <ZoomIn className="w-5 h-5" />
                </button>

                {/* Rotate */}
                <button
                  onClick={handleRotate}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded"
                  title="Forgatás"
                >
                  <RotateCw className="w-5 h-5" />
                </button>

                {/* Info toggle */}
                <button
                  onClick={() => setLightbox(prev => ({ ...prev, showInfo: !prev.showInfo }))}
                  className={`p-2 rounded ${lightbox.showInfo ? 'bg-white bg-opacity-20' : 'text-white hover:bg-white hover:bg-opacity-20'}`}
                  title="Információ"
                >
                  <Info className="w-5 h-5" />
                </button>

                {/* Download */}
                <button
                  onClick={() => downloadPhoto(currentPhoto)}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded"
                  title="Letöltés"
                >
                  <Download className="w-5 h-5" />
                </button>

                {/* Share */}
                <button
                  onClick={() => sharePhoto(currentPhoto)}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded"
                  title="Megosztás"
                >
                  <Share2 className="w-5 h-5" />
                </button>

                {/* Close */}
                <button
                  onClick={closeLightbox}
                  className="p-2 text-white hover:bg-white hover:bg-opacity-20 rounded"
                  title="Bezárás"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Navigation */}
          {photos.length > 1 && (
            <>
              <button
                onClick={() => navigatePhoto('prev')}
                className="absolute left-4 top-1/2 transform -translate-y-1/2 p-3 text-white hover:bg-white hover:bg-opacity-20 rounded-full z-10"
                title="Előző"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
              
              <button
                onClick={() => navigatePhoto('next')}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 p-3 text-white hover:bg-white hover:bg-opacity-20 rounded-full z-10"
                title="Következő"
              >
                <ChevronRight className="w-6 h-6" />
              </button>
            </>
          )}

          {/* Main image */}
          <div className="flex items-center justify-center w-full h-full p-16">
            <img
              ref={imageRef}
              src={currentPhoto.urls.preview}
              alt={currentPhoto.fileName}
              className="max-w-full max-h-full object-contain transition-transform"
              style={{
                transform: `scale(${lightbox.zoom}) rotate(${lightbox.rotation}deg)`
              }}
            />
          </div>

          {/* Info panel */}
          {lightbox.showInfo && (
            <div className="absolute right-0 top-0 bottom-0 w-80 bg-black bg-opacity-80 text-white p-6 overflow-y-auto">
              <h3 className="text-lg font-medium mb-4">Kép információk</h3>
              
              <div className="space-y-4 text-sm">
                {/* Basic info */}
                <div>
                  <h4 className="font-medium mb-2">Alapadatok</h4>
                  <dl className="space-y-1">
                    <div className="flex justify-between">
                      <dt>Fájlnév:</dt>
                      <dd className="text-right">{currentPhoto.fileName}</dd>
                    </div>
                    <div className="flex justify-between">
                      <dt>Méret:</dt>
                      <dd>{formatFileSize(currentPhoto.metadata.fileSize)}</dd>
                    </div>
                    {currentPhoto.metadata.width && currentPhoto.metadata.height && (
                      <div className="flex justify-between">
                        <dt>Felbontás:</dt>
                        <dd>{currentPhoto.metadata.width}×{currentPhoto.metadata.height}</dd>
                      </div>
                    )}
                    <div className="flex justify-between">
                      <dt>Típus:</dt>
                      <dd>{currentPhoto.metadata.mimeType}</dd>
                    </div>
                  </dl>
                </div>

                {/* Date */}
                {currentPhoto.metadata.takenAt && (
                  <div>
                    <h4 className="font-medium mb-2 flex items-center">
                      <Calendar className="w-4 h-4 mr-2" />
                      Készítés ideje
                    </h4>
                    <p>{formatDate(currentPhoto.metadata.takenAt)}</p>
                  </div>
                )}

                {/* Camera info */}
                {currentPhoto.metadata.camera && (
                  <div>
                    <h4 className="font-medium mb-2 flex items-center">
                      <Camera className="w-4 h-4 mr-2" />
                      Fényképezőgép
                    </h4>
                    <dl className="space-y-1">
                      {currentPhoto.metadata.camera.make && (
                        <div className="flex justify-between">
                          <dt>Gyártó:</dt>
                          <dd>{currentPhoto.metadata.camera.make}</dd>
                        </div>
                      )}
                      {currentPhoto.metadata.camera.model && (
                        <div className="flex justify-between">
                          <dt>Modell:</dt>
                          <dd>{currentPhoto.metadata.camera.model}</dd>
                        </div>
                      )}
                      {currentPhoto.metadata.camera.lens && (
                        <div className="flex justify-between">
                          <dt>Objektív:</dt>
                          <dd>{currentPhoto.metadata.camera.lens}</dd>
                        </div>
                      )}
                    </dl>
                  </div>
                )}

                {/* Camera settings */}
                {currentPhoto.metadata.camera?.settings && (
                  <div>
                    <h4 className="font-medium mb-2">Beállítások</h4>
                    <dl className="space-y-1">
                      {currentPhoto.metadata.camera.settings.aperture && (
                        <div className="flex justify-between">
                          <dt>Blende:</dt>
                          <dd>{currentPhoto.metadata.camera.settings.aperture}</dd>
                        </div>
                      )}
                      {currentPhoto.metadata.camera.settings.shutter && (
                        <div className="flex justify-between">
                          <dt>Zársebesség:</dt>
                          <dd>{currentPhoto.metadata.camera.settings.shutter}</dd>
                        </div>
                      )}
                      {currentPhoto.metadata.camera.settings.iso && (
                        <div className="flex justify-between">
                          <dt>ISO:</dt>
                          <dd>{currentPhoto.metadata.camera.settings.iso}</dd>
                        </div>
                      )}
                      {currentPhoto.metadata.camera.settings.focalLength && (
                        <div className="flex justify-between">
                          <dt>Fókusztáv:</dt>
                          <dd>{currentPhoto.metadata.camera.settings.focalLength}</dd>
                        </div>
                      )}
                    </dl>
                  </div>
                )}

                {/* Location */}
                {currentPhoto.metadata.location && (
                  <div>
                    <h4 className="font-medium mb-2 flex items-center">
                      <MapPin className="w-4 h-4 mr-2" />
                      Helyszín
                    </h4>
                    <dl className="space-y-1">
                      <div className="flex justify-between">
                        <dt>Szélesség:</dt>
                        <dd>{currentPhoto.metadata.location.latitude.toFixed(6)}°</dd>
                      </div>
                      <div className="flex justify-between">
                        <dt>Hosszúság:</dt>
                        <dd>{currentPhoto.metadata.location.longitude.toFixed(6)}°</dd>
                      </div>
                      {currentPhoto.metadata.location.altitude && (
                        <div className="flex justify-between">
                          <dt>Magasság:</dt>
                          <dd>{Math.round(currentPhoto.metadata.location.altitude)}m</dd>
                        </div>
                      )}
                    </dl>
                    
                    {/* Map link */}
                    <a
                      href={`https://maps.google.com/?q=${currentPhoto.metadata.location.latitude},${currentPhoto.metadata.location.longitude}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-blue-300 hover:text-blue-200 text-sm mt-2"
                    >
                      Megnyitás térképen →
                    </a>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  )
}