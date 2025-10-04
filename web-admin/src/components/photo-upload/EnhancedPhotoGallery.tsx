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
  Edit3,
  Settings,
  Maximize2,
  MoreVertical,
  Copy,
  ExternalLink
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
// import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { PhotoUpload, PhotoMetadata } from '@/lib/types/photo-upload'

interface EnhancedPhotoGalleryProps {
  photos: PhotoUpload[]
  onPhotoDelete?: (photoId: string) => void
  onPhotoEdit?: (photoId: string, metadata: Partial<PhotoMetadata>) => void
  className?: string
  maxHeight?: number
  showThumbnails?: boolean
  enableSelection?: boolean
  onSelectionChange?: (selectedIds: string[]) => void
}

interface LightboxState {
  isOpen: boolean
  currentIndex: number
  zoom: number
  rotation: number
  showInfo: boolean
  showExif: boolean
  panX: number
  panY: number
}

interface GestureState {
  isDragging: boolean
  startX: number
  startY: number
  lastPanX: number
  lastPanY: number
}

const formatCoordinates = (lat: number, lng: number): string => {
  const latDir = lat >= 0 ? 'N' : 'S'
  const lngDir = lng >= 0 ? 'E' : 'W'
  return `${Math.abs(lat).toFixed(6)}° ${latDir}, ${Math.abs(lng).toFixed(6)}° ${lngDir}`
}

const formatDateTime = (date: Date): string => {
  return new Intl.DateTimeFormat('hu-HU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

export function EnhancedPhotoGallery({
  photos,
  onPhotoDelete,
  onPhotoEdit,
  className = '',
  maxHeight = 600,
  showThumbnails = true,
  enableSelection = false,
  onSelectionChange
}: EnhancedPhotoGalleryProps) {
  const [lightbox, setLightbox] = useState<LightboxState>({
    isOpen: false,
    currentIndex: 0,
    zoom: 1,
    rotation: 0,
    showInfo: false,
    showExif: false,
    panX: 0,
    panY: 0
  })

  const [selectedPhotos, setSelectedPhotos] = useState<Set<string>>(new Set())
  const [gesture, setGesture] = useState<GestureState>({
    isDragging: false,
    startX: 0,
    startY: 0,
    lastPanX: 0,
    lastPanY: 0
  })
  const [viewMode, setViewMode] = useState<'grid' | 'masonry' | 'list'>('grid')
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'size'>('date')
  
  const lightboxRef = useRef<HTMLDivElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Open lightbox
  const openLightbox = useCallback((index: number) => {
    setLightbox(prev => ({
      ...prev,
      isOpen: true,
      currentIndex: index,
      zoom: 1,
      rotation: 0,
      panX: 0,
      panY: 0
    }))
    document.body.style.overflow = 'hidden'
  }, [])

  // Close lightbox
  const closeLightbox = useCallback(() => {
    setLightbox(prev => ({ ...prev, isOpen: false }))
    document.body.style.overflow = 'auto'
  }, [])

  // Navigate lightbox
  const navigateLightbox = useCallback((direction: 'prev' | 'next') => {
    setLightbox(prev => {
      const newIndex = direction === 'next' 
        ? (prev.currentIndex + 1) % photos.length
        : prev.currentIndex === 0 ? photos.length - 1 : prev.currentIndex - 1
      
      return {
        ...prev,
        currentIndex: newIndex,
        zoom: 1,
        rotation: 0,
        panX: 0,
        panY: 0
      }
    })
  }, [photos.length])

  // Zoom functions
  const zoomIn = useCallback(() => {
    setLightbox(prev => ({ 
      ...prev, 
      zoom: Math.min(prev.zoom * 1.5, 5),
      panX: 0,
      panY: 0
    }))
  }, [])

  const zoomOut = useCallback(() => {
    setLightbox(prev => ({ 
      ...prev, 
      zoom: Math.max(prev.zoom / 1.5, 0.1),
      panX: 0,
      panY: 0
    }))
  }, [])

  const rotate = useCallback(() => {
    setLightbox(prev => ({ 
      ...prev, 
      rotation: (prev.rotation + 90) % 360
    }))
  }, [])

  // Mouse/touch pan handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (lightbox.zoom <= 1) return
    
    e.preventDefault()
    setGesture({
      isDragging: true,
      startX: e.clientX,
      startY: e.clientY,
      lastPanX: lightbox.panX,
      lastPanY: lightbox.panY
    })
  }, [lightbox.zoom, lightbox.panX, lightbox.panY])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!gesture.isDragging || lightbox.zoom <= 1) return
    
    const deltaX = e.clientX - gesture.startX
    const deltaY = e.clientY - gesture.startY
    
    setLightbox(prev => ({
      ...prev,
      panX: gesture.lastPanX + deltaX,
      panY: gesture.lastPanY + deltaY
    }))
  }, [gesture])

  const handleMouseUp = useCallback(() => {
    setGesture(prev => ({ ...prev, isDragging: false }))
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
          navigateLightbox('prev')
          break
        case 'ArrowRight':
          navigateLightbox('next')
          break
        case '+':
        case '=':
          zoomIn()
          break
        case '-':
          zoomOut()
          break
        case 'r':
        case 'R':
          rotate()
          break
        case 'i':
        case 'I':
          setLightbox(prev => ({ ...prev, showInfo: !prev.showInfo }))
          break
        case 'e':
        case 'E':
          setLightbox(prev => ({ ...prev, showExif: !prev.showExif }))
          break
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [lightbox.isOpen, closeLightbox, navigateLightbox, zoomIn, zoomOut, rotate])

  // Photo selection
  const toggleSelection = useCallback((photoId: string) => {
    if (!enableSelection) return
    
    setSelectedPhotos(prev => {
      const newSet = new Set(prev)
      if (newSet.has(photoId)) {
        newSet.delete(photoId)
      } else {
        newSet.add(photoId)
      }
      
      onSelectionChange?.(Array.from(newSet))
      return newSet
    })
  }, [enableSelection, onSelectionChange])

  // Download photo
  const downloadPhoto = useCallback(async (photo: PhotoUpload) => {
    try {
      const response = await fetch(photo.urls.original)
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      
      const a = document.createElement('a')
      a.href = url
      a.download = photo.originalName
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }, [])

  // Copy to clipboard
  const copyToClipboard = useCallback(async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
    } catch (error) {
      console.error('Copy failed:', error)
    }
  }, [])

  // Sort photos
  const sortedPhotos = React.useMemo(() => {
    return [...photos].sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        case 'name':
          return a.originalName.localeCompare(b.originalName)
        case 'size':
          return b.metadata.fileSize - a.metadata.fileSize
        default:
          return 0
      }
    })
  }, [photos, sortBy])

  const currentPhoto = photos[lightbox.currentIndex]

  if (photos.length === 0) {
    return (
      <div className={`flex items-center justify-center p-8 text-gray-500 ${className}`}>
        <div className="text-center">
          <Eye className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Nincsenek feltöltött fotók</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`space-y-4 ${className}`} ref={containerRef}>
      {/* Gallery Controls */}
      <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-600">
            {photos.length} fotó
          </span>
          
          {selectedPhotos.size > 0 && (
            <Badge variant="secondary">
              {selectedPhotos.size} kijelölve
            </Badge>
          )}
        </div>
        
        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <Button
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            Rács
          </Button>
          <Button
            variant={viewMode === 'masonry' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('masonry')}
          >
            Mozaik
          </Button>
          <Button
            variant={viewMode === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('list')}
          >
            Lista
          </Button>
          
          <Separator orientation="vertical" className="h-6" />
          
          {/* Sort Options */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'name' | 'size')}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="date">Dátum</option>
            <option value="name">Név</option>
            <option value="size">Méret</option>
          </select>
        </div>
      </div>

      {/* Photo Grid */}
      <div 
        className={`
          ${viewMode === 'grid' 
            ? 'grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 gap-4'
            : viewMode === 'masonry'
            ? 'columns-2 md:columns-3 lg:columns-4 xl:columns-6 gap-4 space-y-4'
            : 'space-y-4'
          }
        `}
        style={{ maxHeight: maxHeight ? `${maxHeight}px` : undefined }}
      >
        {sortedPhotos.map((photo, index) => (
          <div
            key={photo.id}
            className={`
              relative group cursor-pointer 
              ${viewMode === 'list' ? 'flex items-center gap-4 p-4 bg-white rounded-lg border' : 'bg-white rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition-all'}
              ${selectedPhotos.has(photo.id) ? 'ring-2 ring-blue-500' : ''}
            `}
            onClick={() => enableSelection ? toggleSelection(photo.id) : openLightbox(index)}
          >
            {viewMode === 'list' ? (
              <>
                <img
                  src={photo.urls.thumbnail}
                  alt={photo.originalName}
                  className="w-16 h-16 object-cover rounded"
                />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-900 truncate">
                    {photo.originalName}
                  </p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(photo.metadata.fileSize)}
                  </p>
                  <p className="text-xs text-gray-400">
                    {formatDateTime(new Date(photo.createdAt))}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {photo.metadata.location && (
                    <div title="GPS adatok">
                      <MapPin className="w-4 h-4 text-green-500" />
                    </div>
                  )}
                  {photo.metadata.camera && (
                    <div title="EXIF adatok">
                      <Camera className="w-4 h-4 text-blue-500" />
                    </div>
                  )}
                </div>
              </>
            ) : (
              <>
                <div className="aspect-square bg-gray-100 overflow-hidden">
                  <img
                    src={photo.urls.thumbnail}
                    alt={photo.originalName}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                  />
                </div>
                
                {/* Overlay */}
                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-colors">
                  <div className="absolute top-2 right-2 flex gap-1">
                    {photo.metadata.location && (
                      <Badge variant="secondary" className="bg-white/90 text-xs">
                        <MapPin className="w-3 h-3 mr-1" />
                        GPS
                      </Badge>
                    )}
                    {photo.metadata.camera && (
                      <Badge variant="secondary" className="bg-white/90 text-xs">
                        <Camera className="w-3 h-3 mr-1" />
                        EXIF
                      </Badge>
                    )}
                  </div>
                  
                  {/* Quick Actions */}
                  <div className="absolute bottom-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="flex gap-1">
                      <Button
                        size="sm"
                        variant="secondary"
                        className="h-8 w-8 p-0"
                        onClick={(e) => {
                          e.stopPropagation()
                          downloadPhoto(photo)
                        }}
                      >
                        <Download className="w-3 h-3" />
                      </Button>
                      {onPhotoDelete && (
                        <Button
                          size="sm"
                          variant="destructive"
                          className="h-8 w-8 p-0"
                          onClick={(e) => {
                            e.stopPropagation()
                            onPhotoDelete(photo.id)
                          }}
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
                
                {viewMode === 'grid' && (
                  <div className="p-2">
                    <p className="text-xs text-gray-600 truncate">
                      {photo.originalName}
                    </p>
                    <p className="text-xs text-gray-400">
                      {formatFileSize(photo.metadata.fileSize)}
                    </p>
                  </div>
                )}
              </>
            )}
          </div>
        ))}
      </div>

      {/* Lightbox */}
      {lightbox.isOpen && currentPhoto && (
        <div className="fixed inset-0 z-50 bg-black">
          {/* Lightbox Header */}
          <div className="absolute top-0 left-0 right-0 z-10 bg-gradient-to-b from-black/80 to-transparent p-4">
            <div className="flex items-center justify-between text-white">
              <div>
                <h3 className="font-medium">{currentPhoto.originalName}</h3>
                <p className="text-sm text-gray-300">
                  {lightbox.currentIndex + 1} / {photos.length}
                </p>
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-white hover:bg-white/20"
                  onClick={() => setLightbox(prev => ({ ...prev, showInfo: !prev.showInfo }))}
                >
                  <Info className="w-4 h-4" />
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-white hover:bg-white/20"
                  onClick={() => downloadPhoto(currentPhoto)}
                >
                  <Download className="w-4 h-4" />
                </Button>
                
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-white hover:bg-white/20"
                  onClick={closeLightbox}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* Main Image Area */}
          <div 
            ref={lightboxRef}
            className="absolute inset-0 flex items-center justify-center p-16"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          >
            <img
              ref={imageRef}
              src={currentPhoto.urls.original}
              alt={currentPhoto.originalName}
              className={`
                max-w-full max-h-full object-contain transition-transform duration-200
                ${gesture.isDragging ? 'cursor-grabbing' : lightbox.zoom > 1 ? 'cursor-grab' : 'cursor-default'}
              `}
              style={{
                transform: `
                  scale(${lightbox.zoom}) 
                  rotate(${lightbox.rotation}deg) 
                  translate(${lightbox.panX}px, ${lightbox.panY}px)
                `,
                transformOrigin: 'center center'
              }}
              draggable={false}
            />
          </div>

          {/* Navigation Arrows */}
          {photos.length > 1 && (
            <>
              <Button
                className="absolute left-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white border-0"
                onClick={() => navigateLightbox('prev')}
              >
                <ChevronLeft className="w-6 h-6" />
              </Button>
              
              <Button
                className="absolute right-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white border-0"
                onClick={() => navigateLightbox('next')}
              >
                <ChevronRight className="w-6 h-6" />
              </Button>
            </>
          )}

          {/* Lightbox Controls */}
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-black/80 rounded-lg p-2">
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                onClick={zoomOut}
              >
                <ZoomOut className="w-4 h-4" />
              </Button>
              
              <span className="text-white text-sm px-2">
                {Math.round(lightbox.zoom * 100)}%
              </span>
              
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                onClick={zoomIn}
              >
                <ZoomIn className="w-4 h-4" />
              </Button>
              
              <Separator orientation="vertical" className="h-6 bg-white/30" />
              
              <Button
                variant="ghost"
                size="sm"
                className="text-white hover:bg-white/20"
                onClick={rotate}
              >
                <RotateCw className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Info Panel */}
          {lightbox.showInfo && (
            <div className="absolute top-0 right-0 h-full w-80 bg-white shadow-xl overflow-hidden">
              <div className="p-4 border-b">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">Fotó információ</h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setLightbox(prev => ({ ...prev, showExif: !prev.showExif }))}
                  >
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>
              </div>
              
              <div className="h-full pb-16 overflow-y-auto">
                <div className="p-4 space-y-4">
                  {/* Basic Info */}
                  <div className="space-y-2">
                    <h4 className="font-medium text-sm">Alapadatok</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-gray-500">Fájlnév:</span>
                        <p className="font-mono text-xs break-all">
                          {currentPhoto.originalName}
                        </p>
                      </div>
                      <div>
                        <span className="text-gray-500">Méret:</span>
                        <p>{formatFileSize(currentPhoto.metadata.fileSize)}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Típus:</span>
                        <p>{currentPhoto.metadata.mimeType}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Feltöltve:</span>
                        <p>{formatDateTime(new Date(currentPhoto.createdAt))}</p>
                      </div>
                      {currentPhoto.metadata.width && currentPhoto.metadata.height && (
                        <>
                          <div>
                            <span className="text-gray-500">Felbontás:</span>
                            <p>{currentPhoto.metadata.width} × {currentPhoto.metadata.height}</p>
                          </div>
                          <div>
                            <span className="text-gray-500">Arány:</span>
                            <p>{(currentPhoto.metadata.width / currentPhoto.metadata.height).toFixed(2)}:1</p>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                  {/* GPS Location */}
                  {currentPhoto.metadata.location && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-green-500" />
                        GPS koordináták
                      </h4>
                      <div className="text-sm space-y-1">
                        <p className="font-mono text-xs">
                          {formatCoordinates(
                            currentPhoto.metadata.location.latitude,
                            currentPhoto.metadata.location.longitude
                          )}
                        </p>
                        {currentPhoto.metadata.location.altitude && (
                          <p className="text-gray-500">
                            Magasság: {currentPhoto.metadata.location.altitude.toFixed(1)}m
                          </p>
                        )}
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-xs"
                            onClick={() => {
                              const coords = `${currentPhoto.metadata.location!.latitude},${currentPhoto.metadata.location!.longitude}`
                              copyToClipboard(coords)
                            }}
                          >
                            <Copy className="w-3 h-3 mr-1" />
                            Másolás
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-xs"
                            onClick={() => {
                              const url = `https://maps.google.com/maps?q=${currentPhoto.metadata.location!.latitude},${currentPhoto.metadata.location!.longitude}`
                              window.open(url, '_blank')
                            }}
                          >
                            <ExternalLink className="w-3 h-3 mr-1" />
                            Térkép
                          </Button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Camera EXIF */}
                  {currentPhoto.metadata.camera && lightbox.showExif && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm flex items-center gap-2">
                        <Camera className="w-4 h-4 text-blue-500" />
                        Kamera adatok
                      </h4>
                      <div className="space-y-2 text-sm">
                        {currentPhoto.metadata.camera.make && (
                          <div>
                            <span className="text-gray-500">Gyártó:</span>
                            <p>{currentPhoto.metadata.camera.make}</p>
                          </div>
                        )}
                        {currentPhoto.metadata.camera.model && (
                          <div>
                            <span className="text-gray-500">Modell:</span>
                            <p>{currentPhoto.metadata.camera.model}</p>
                          </div>
                        )}
                        {currentPhoto.metadata.camera.lens && (
                          <div>
                            <span className="text-gray-500">Objektív:</span>
                            <p>{currentPhoto.metadata.camera.lens}</p>
                          </div>
                        )}
                        
                        {currentPhoto.metadata.camera.settings && (
                          <div className="space-y-1">
                            <span className="text-gray-500 font-medium">Expozíciós beállítások:</span>
                            <div className="grid grid-cols-2 gap-1 text-xs">
                              {currentPhoto.metadata.camera.settings.aperture && (
                                <div>f/{currentPhoto.metadata.camera.settings.aperture}</div>
                              )}
                              {currentPhoto.metadata.camera.settings.shutter && (
                                <div>{currentPhoto.metadata.camera.settings.shutter}s</div>
                              )}
                              {currentPhoto.metadata.camera.settings.iso && (
                                <div>ISO {currentPhoto.metadata.camera.settings.iso}</div>
                              )}
                              {currentPhoto.metadata.camera.settings.focalLength && (
                                <div>{currentPhoto.metadata.camera.settings.focalLength}</div>
                              )}
                            </div>
                            {currentPhoto.metadata.camera.settings.flash && (
                              <p className="text-xs text-gray-500">Vaku használva</p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Date Taken */}
                  {currentPhoto.metadata.takenAt && (
                    <div className="space-y-2">
                      <h4 className="font-medium text-sm flex items-center gap-2">
                        <Calendar className="w-4 h-4 text-purple-500" />
                        Felvétel időpontja
                      </h4>
                      <p className="text-sm">
                        {formatDateTime(new Date(currentPhoto.metadata.takenAt))}
                      </p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="space-y-2 pt-4 border-t">
                    <h4 className="font-medium text-sm">Műveletek</h4>
                    <div className="flex flex-col gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="justify-start"
                        onClick={() => downloadPhoto(currentPhoto)}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Letöltés
                      </Button>
                      
                      <Button
                        size="sm"
                        variant="outline"
                        className="justify-start"
                        onClick={() => copyToClipboard(currentPhoto.urls.original)}
                      >
                        <Copy className="w-4 h-4 mr-2" />
                        Link másolása
                      </Button>
                      
                      {onPhotoEdit && (
                        <Button
                          size="sm"
                          variant="outline"
                          className="justify-start"
                          onClick={() => {
                            // TODO: Open edit modal
                          }}
                        >
                          <Edit3 className="w-4 h-4 mr-2" />
                          Szerkesztés
                        </Button>
                      )}
                      
                      {onPhotoDelete && (
                        <Button
                          size="sm"
                          variant="destructive"
                          className="justify-start"
                          onClick={() => {
                            onPhotoDelete(currentPhoto.id)
                            closeLightbox()
                          }}
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Törlés
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}