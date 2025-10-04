'use client'

import React, { useState, useCallback, useRef, useEffect } from 'react'
import {
  Upload,
  X,
  FileImage,
  AlertCircle,
  CheckCircle2,
  Pause,
  Play,
  RotateCcw,
  Trash2,
  Eye,
  Info,
  Zap,
  Clock,
  HardDrive,
  Wifi,
  Camera,
  MapPin,
  Settings,
  RefreshCw
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import { EnhancedUploadService } from '@/lib/services/enhanced-upload-service'
import { PhotoUpload, PhotoMetadata, UploadProgress, PresignedUrlRequest } from '@/lib/types/photo-upload'
import { extractExifData } from '@/lib/utils/exif'

interface UploadFileState {
  id: string
  file: File
  status: 'pending' | 'uploading' | 'paused' | 'completed' | 'error' | 'cancelled'
  progress: UploadProgress
  metadata?: PhotoMetadata
  preview?: string
  error?: string
  resumable: boolean
  sessionId?: string
}

interface EnhancedPhotoUploaderProps {
  onUploadComplete?: (photos: PhotoUpload[]) => void
  onUploadProgress?: (fileId: string, progress: UploadProgress) => void
  onUploadError?: (fileId: string, error: string) => void
  maxFiles?: number
  maxFileSize?: number
  maxTotalSize?: number
  acceptedTypes?: string[]
  className?: string
  disabled?: boolean
  autoStart?: boolean
  showPreviews?: boolean
  showMetadata?: boolean
  concurrent?: number
}

const DEFAULT_ACCEPTED_TYPES = [
  'image/jpeg',
  'image/jpg', 
  'image/png',
  'image/gif',
  'image/webp',
  'image/bmp',
  'image/tiff'
]

const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${Math.round(seconds)}s`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.round(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const getStatusIcon = (status: UploadFileState['status']) => {
  switch (status) {
    case 'completed':
      return <CheckCircle2 className="w-5 h-5 text-green-500" />
    case 'error':
    case 'cancelled':
      return <AlertCircle className="w-5 h-5 text-red-500" />
    case 'uploading':
      return <Upload className="w-5 h-5 text-blue-500 animate-pulse" />
    case 'paused':
      return <Pause className="w-5 h-5 text-yellow-500" />
    default:
      return <Clock className="w-5 h-5 text-gray-400" />
  }
}

export function EnhancedPhotoUploader({
  onUploadComplete,
  onUploadProgress,
  onUploadError,
  maxFiles = 50,
  maxFileSize = 25 * 1024 * 1024, // 25MB
  maxTotalSize = 100 * 1024 * 1024, // 100MB
  acceptedTypes = DEFAULT_ACCEPTED_TYPES,
  className = '',
  disabled = false,
  autoStart = true,
  showPreviews = true,
  showMetadata = true,
  concurrent = 3
}: EnhancedPhotoUploaderProps) {
  const [files, setFiles] = useState<UploadFileState[]>([])
  const [isDragActive, setIsDragActive] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [totalProgress, setTotalProgress] = useState(0)
  const [uploadStats, setUploadStats] = useState({
    totalBytes: 0,
    uploadedBytes: 0,
    speed: 0,
    eta: 0,
    activeUploads: 0
  })
  const [expandedFile, setExpandedFile] = useState<string | null>(null)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const dropRef = useRef<HTMLDivElement>(null)
  const uploadService = useRef<EnhancedUploadService>()
  const speedCalculatorRef = useRef({
    lastUpdate: Date.now(),
    lastBytes: 0,
    samples: [] as Array<{ time: number; bytes: number }>
  })

  // Initialize upload service
  useEffect(() => {
    uploadService.current = new EnhancedUploadService({
      chunkSize: 1024 * 1024, // 1MB chunks
      maxRetries: 3,
      concurrentUploads: concurrent,
      onProgress: (fileId, progress) => {
        updateFileProgress(fileId, progress)
        onUploadProgress?.(fileId, progress)
      },
      onComplete: (fileId, result) => {
        updateFileStatus(fileId, 'completed')
        // TODO: Handle complete result
      },
      onError: (fileId, error) => {
        updateFileStatus(fileId, 'error', error.message)
        onUploadError?.(fileId, error.message)
      }
    })

    return () => {
      uploadService.current?.cancelAll()
    }
  }, [concurrent, onUploadProgress, onUploadError])

  // Calculate upload speed and ETA
  const updateUploadStats = useCallback(() => {
    const now = Date.now()
    const totalBytes = files.reduce((sum, f) => sum + f.file.size, 0)
    const uploadedBytes = files.reduce((sum, f) => {
      const progress = f.progress.chunksCompleted / f.progress.totalChunks
      return sum + (f.file.size * progress)
    }, 0)
    
    const activeUploads = files.filter(f => f.status === 'uploading').length
    
    // Calculate speed using sliding window
    const calculator = speedCalculatorRef.current
    calculator.samples.push({ time: now, bytes: uploadedBytes })
    calculator.samples = calculator.samples.filter(sample => now - sample.time < 5000) // 5 second window
    
    let speed = 0
    if (calculator.samples.length > 1) {
      const oldest = calculator.samples[0]
      const newest = calculator.samples[calculator.samples.length - 1]
      const timeDiff = (newest.time - oldest.time) / 1000
      const bytesDiff = newest.bytes - oldest.bytes
      speed = timeDiff > 0 ? bytesDiff / timeDiff : 0
    }
    
    const remainingBytes = totalBytes - uploadedBytes
    const eta = speed > 0 ? remainingBytes / speed : 0
    
    setUploadStats({
      totalBytes,
      uploadedBytes,
      speed,
      eta,
      activeUploads
    })
    
    setTotalProgress(totalBytes > 0 ? (uploadedBytes / totalBytes) * 100 : 0)
  }, [files])

  // Update stats regularly during upload
  useEffect(() => {
    if (!isUploading) return
    
    const interval = setInterval(updateUploadStats, 1000)
    return () => clearInterval(interval)
  }, [isUploading, updateUploadStats])

  // Update file progress
  const updateFileProgress = useCallback((fileId: string, progress: UploadProgress) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, progress } : f
    ))
  }, [])

  // Update file status
  const updateFileStatus = useCallback((
    fileId: string, 
    status: UploadFileState['status'], 
    error?: string
  ) => {
    setFiles(prev => prev.map(f => 
      f.id === fileId ? { ...f, status, error } : f
    ))
  }, [])

  // Generate file preview
  const generatePreview = useCallback((file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => resolve(reader.result as string)
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }, [])

  // Process file metadata
  const processFileMetadata = useCallback(async (file: File): Promise<PhotoMetadata> => {
    const exifData = await extractExifData(file)
    
    return {
      fileSize: file.size,
      mimeType: file.type,
      width: exifData.width,
      height: exifData.height,
      takenAt: exifData.dateTime ? new Date(exifData.dateTime) : undefined,
      location: exifData.gps ? {
        latitude: exifData.gps.latitude,
        longitude: exifData.gps.longitude,
        altitude: exifData.gps.altitude
      } : undefined,
      camera: exifData.camera ? {
        make: exifData.camera.make,
        model: exifData.camera.model,
        lens: exifData.camera.lens,
        settings: exifData.camera.settings ? {
          aperture: exifData.camera.settings.aperture,
          shutter: exifData.camera.settings.shutterSpeed,
          iso: exifData.camera.settings.iso,
          focalLength: exifData.camera.settings.focalLength,
          flash: exifData.camera.settings.flash
        } : undefined
      } : undefined,
      checksum: exifData.checksum
    }
  }, [])

  // Validate file
  const validateFile = useCallback((file: File): string | null => {
    if (!acceptedTypes.includes(file.type)) {
      return `Nem támogatott fájltípus: ${file.type}`
    }
    
    if (file.size > maxFileSize) {
      return `A fájl túl nagy: ${formatBytes(file.size)} (max: ${formatBytes(maxFileSize)})`
    }
    
    const currentTotalSize = files.reduce((sum, f) => sum + f.file.size, 0)
    if (currentTotalSize + file.size > maxTotalSize) {
      return `Az összes fájl mérete túllépi a limitet (${formatBytes(maxTotalSize)})`
    }
    
    if (files.length >= maxFiles) {
      return `Túl sok fájl (max: ${maxFiles})`
    }
    
    return null
  }, [acceptedTypes, maxFileSize, maxTotalSize, maxFiles, files])

  // Add files to upload queue
  const addFiles = useCallback(async (fileList: FileList | File[]) => {
    const newFiles: UploadFileState[] = []
    
    for (const file of Array.from(fileList)) {
      const validationError = validateFile(file)
      if (validationError) {
        console.error(`File validation failed: ${validationError}`)
        continue
      }
      
      const fileId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
      
      try {
        const [preview, metadata] = await Promise.all([
          showPreviews ? generatePreview(file) : Promise.resolve(undefined),
          showMetadata ? processFileMetadata(file) : Promise.resolve(undefined)
        ])
        
        const uploadFile: UploadFileState = {
          id: fileId,
          file,
          status: 'pending',
          progress: {
            totalChunks: Math.ceil(file.size / (1024 * 1024)), // 1MB chunks
            chunksCompleted: 0,
            bytesUploaded: 0,
            percentage: 0,
            speed: 0,
            eta: 0
          },
          metadata,
          preview,
          resumable: file.size > 5 * 1024 * 1024 // Files > 5MB are resumable
        }
        
        newFiles.push(uploadFile)
      } catch (error) {
        console.error(`Failed to process file ${file.name}:`, error)
      }
    }
    
    setFiles(prev => [...prev, ...newFiles])
    
    if (autoStart && newFiles.length > 0) {
      startUpload()
    }
  }, [validateFile, showPreviews, showMetadata, generatePreview, processFileMetadata, autoStart])

  // Handle file input change
  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files) {
      addFiles(files)
    }
    // Clear input value to allow re-selecting same files
    e.target.value = ''
  }, [addFiles])

  // Drag and drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    // Only set drag inactive if we're leaving the drop zone entirely
    if (e.currentTarget.contains(e.relatedTarget as Node)) return
    setIsDragActive(false)
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(file => 
      acceptedTypes.includes(file.type)
    )
    
    if (droppedFiles.length > 0) {
      addFiles(droppedFiles)
    }
  }, [acceptedTypes, addFiles])

  // Start upload process
  const startUpload = useCallback(async () => {
    if (!uploadService.current || isUploading) return
    
    const pendingFiles = files.filter(f => f.status === 'pending' || f.status === 'paused')
    if (pendingFiles.length === 0) return
    
    setIsUploading(true)
    
    for (const file of pendingFiles) {
      updateFileStatus(file.id, 'uploading')
      
      try {
        // Request presigned URL
        const presignedRequest: PresignedUrlRequest = {
          fileName: file.file.name,
          fileSize: file.file.size,
          mimeType: file.file.type,
          metadata: file.metadata,
          multipart: file.file.size > 5 * 1024 * 1024 // Use multipart for files > 5MB
        }
        
        // TODO: Make API call to get presigned URL
        // const presignedResponse = await fetch('/api/upload/presigned', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify(presignedRequest)
        // })
        
        // Mock presigned URL response for now
        const mockPresignedResponse = {
          uploadId: `upload-${file.id}`,
          url: `https://example-bucket.s3.amazonaws.com/${file.id}`,
          fields: {},
          multipartUploadId: file.file.size > 5 * 1024 * 1024 ? `multipart-${file.id}` : undefined
        }
        
        // Start upload with presigned URL
        await uploadService.current.uploadFile(file.id, file.file, mockPresignedResponse)
        
      } catch (error) {
        console.error(`Upload failed for ${file.file.name}:`, error)
        updateFileStatus(file.id, 'error', error instanceof Error ? error.message : 'Upload failed')
      }
    }
    
    setIsUploading(false)
  }, [files, isUploading, updateFileStatus])

  // Pause/Resume upload
  const pauseResumeUpload = useCallback((fileId: string) => {
    const file = files.find(f => f.id === fileId)
    if (!file || !uploadService.current) return
    
    if (file.status === 'uploading') {
      uploadService.current.pauseUpload(fileId)
      updateFileStatus(fileId, 'paused')
    } else if (file.status === 'paused' && file.resumable) {
      updateFileStatus(fileId, 'uploading')
      // TODO: Resume upload
    }
  }, [files, updateFileStatus])

  // Cancel upload
  const cancelUpload = useCallback((fileId: string) => {
    if (uploadService.current) {
      uploadService.current.cancelUpload(fileId)
    }
    updateFileStatus(fileId, 'cancelled')
  }, [updateFileStatus])

  // Remove file from queue
  const removeFile = useCallback((fileId: string) => {
    if (uploadService.current) {
      uploadService.current.cancelUpload(fileId)
    }
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }, [])

  // Clear all files
  const clearAll = useCallback(() => {
    if (uploadService.current) {
      uploadService.current.cancelAll()
    }
    setFiles([])
    setIsUploading(false)
  }, [])

  // Retry failed uploads
  const retryFailed = useCallback(() => {
    const failedFiles = files.filter(f => f.status === 'error' || f.status === 'cancelled')
    failedFiles.forEach(f => updateFileStatus(f.id, 'pending'))
    if (failedFiles.length > 0) {
      startUpload()
    }
  }, [files, updateFileStatus, startUpload])

  const completedFiles = files.filter(f => f.status === 'completed')
  const failedFiles = files.filter(f => f.status === 'error' || f.status === 'cancelled')
  const activeFiles = files.filter(f => f.status === 'uploading' || f.status === 'pending')

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Upload Area */}
      <div
        ref={dropRef}
        className={`
          relative border-2 border-dashed rounded-lg transition-all duration-200
          ${isDragActive 
            ? 'border-blue-500 bg-blue-50' 
            : disabled 
              ? 'border-gray-200 bg-gray-50' 
              : 'border-gray-300 hover:border-gray-400 bg-white'
          }
          ${disabled ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
        `}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
        onClick={() => !disabled && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          className="hidden"
          onChange={handleFileInput}
          disabled={disabled}
        />
        
        <div className="p-8 text-center">
          <div className="mx-auto w-16 h-16 mb-4 flex items-center justify-center rounded-full bg-gray-100">
            {isDragActive ? (
              <Upload className="w-8 h-8 text-blue-500" />
            ) : (
              <FileImage className="w-8 h-8 text-gray-400" />
            )}
          </div>
          
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {isDragActive ? 'Engedd el a fájlokat' : 'Fotók feltöltése'}
          </h3>
          
          <p className="text-sm text-gray-500 mb-4">
            Húzd ide a képeket vagy kattints a tallózáshoz
          </p>
          
          <div className="text-xs text-gray-400 space-y-1">
            <p>Támogatott formátumok: JPEG, PNG, GIF, WebP, BMP, TIFF</p>
            <p>Max fájlméret: {formatBytes(maxFileSize)} | Max összesen: {formatBytes(maxTotalSize)}</p>
            <p>Max fájlok száma: {maxFiles}</p>
          </div>
          
          {!disabled && (
            <Button className="mt-4" variant="outline">
              <Upload className="w-4 h-4 mr-2" />
              Fájlok kiválasztása
            </Button>
          )}
        </div>
      </div>

      {/* Upload Stats */}
      {files.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-medium text-gray-900">Feltöltés állapota</h4>
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={clearAll}
                disabled={isUploading}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Összes törlése
              </Button>
              
              {failedFiles.length > 0 && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={retryFailed}
                >
                  <RefreshCw className="w-4 h-4 mr-1" />
                  Újrapróbálás
                </Button>
              )}
              
              {activeFiles.length > 0 && !isUploading && (
                <Button
                  size="sm"
                  onClick={startUpload}
                >
                  <Play className="w-4 h-4 mr-1" />
                  Feltöltés indítása
                </Button>
              )}
            </div>
          </div>
          
          {/* Progress Bar */}
          <div className="mb-3">
            <div className="flex items-center justify-between text-sm mb-1">
              <span>Összesített haladás</span>
              <span>{Math.round(totalProgress)}%</span>
            </div>
            <Progress value={totalProgress} className="h-2" />
          </div>
          
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <HardDrive className="w-4 h-4 text-gray-500" />
              <span>{formatBytes(uploadStats.uploadedBytes)} / {formatBytes(uploadStats.totalBytes)}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Wifi className="w-4 h-4 text-gray-500" />
              <span>{formatBytes(uploadStats.speed)}/s</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <span>{uploadStats.eta > 0 ? formatDuration(uploadStats.eta) : '--'}</span>
            </div>
            
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-gray-500" />
              <span>{uploadStats.activeUploads} aktív</span>
            </div>
          </div>
          
          {/* Status Summary */}
          <div className="mt-3 flex items-center gap-4 text-sm">
            {completedFiles.length > 0 && (
              <Badge variant="default" className="bg-green-100 text-green-800">
                {completedFiles.length} kész
              </Badge>
            )}
            {activeFiles.length > 0 && (
              <Badge variant="default" className="bg-blue-100 text-blue-800">
                {activeFiles.length} folyamatban
              </Badge>
            )}
            {failedFiles.length > 0 && (
              <Badge variant="destructive">
                {failedFiles.length} sikertelen
              </Badge>
            )}
          </div>
        </div>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <h4 className="font-medium text-gray-900">
            Fájlok ({files.length})
          </h4>
          
          <div className="space-y-3">
            {files.map((file) => (
              <div
                key={file.id}
                className="bg-white border rounded-lg p-4 transition-all hover:shadow-sm"
              >
                <div className="flex items-start gap-4">
                  {/* Preview */}
                  {showPreviews && file.preview && (
                    <div className="flex-shrink-0">
                      <img
                        src={file.preview}
                        alt={file.file.name}
                        className="w-16 h-16 object-cover rounded border"
                      />
                    </div>
                  )}
                  
                  {/* File Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(file.status)}
                        <h5 className="font-medium text-gray-900 truncate">
                          {file.file.name}
                        </h5>
                        
                        {file.resumable && (
                          <Badge variant="outline" className="text-xs">
                            Folytatható
                          </Badge>
                        )}
                      </div>
                      
                      {/* Actions */}
                      <div className="flex items-center gap-1">
                        {file.status === 'uploading' && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => pauseResumeUpload(file.id)}
                          >
                            <Pause className="w-4 h-4" />
                          </Button>
                        )}
                        
                        {file.status === 'paused' && file.resumable && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => pauseResumeUpload(file.id)}
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                        )}
                        
                        {(file.status === 'error' || file.status === 'cancelled') && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => updateFileStatus(file.id, 'pending')}
                          >
                            <RotateCcw className="w-4 h-4" />
                          </Button>
                        )}
                        
                        {showMetadata && file.metadata && (
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setExpandedFile(
                              expandedFile === file.id ? null : file.id
                            )}
                          >
                            <Info className="w-4 h-4" />
                          </Button>
                        )}
                        
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => removeFile(file.id)}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                    
                    {/* Progress */}
                    {(file.status === 'uploading' || file.status === 'paused') && (
                      <div className="mb-2">
                        <div className="flex items-center justify-between text-sm mb-1">
                          <span>
                            {Math.round(file.progress.percentage)}% 
                            ({file.progress.chunksCompleted}/{file.progress.totalChunks} chunk)
                          </span>
                          <span>
                            {formatBytes(file.progress.speed)}/s
                          </span>
                        </div>
                        <Progress value={file.progress.percentage} className="h-2" />
                        {file.progress.eta > 0 && (
                          <p className="text-xs text-gray-500 mt-1">
                            Becsült idő: {formatDuration(file.progress.eta)}
                          </p>
                        )}
                      </div>
                    )}
                    
                    {/* Error Message */}
                    {file.status === 'error' && file.error && (
                      <div className="text-sm text-red-600 bg-red-50 p-2 rounded">
                        {file.error}
                      </div>
                    )}
                    
                    {/* Basic File Info */}
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>{formatBytes(file.file.size)}</span>
                      <span>{file.file.type}</span>
                      {file.metadata?.width && file.metadata?.height && (
                        <span>{file.metadata.width} × {file.metadata.height}</span>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Extended Metadata */}
                {expandedFile === file.id && file.metadata && (
                  <div className="mt-4 pt-4 border-t">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      {/* EXIF Data */}
                      {file.metadata.camera && (
                        <div>
                          <h6 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                            <Camera className="w-4 h-4" />
                            Kamera adatok
                          </h6>
                          <div className="space-y-1 text-gray-600">
                            {file.metadata.camera.make && (
                              <p>Gyártó: {file.metadata.camera.make}</p>
                            )}
                            {file.metadata.camera.model && (
                              <p>Modell: {file.metadata.camera.model}</p>
                            )}
                            {file.metadata.camera.lens && (
                              <p>Objektív: {file.metadata.camera.lens}</p>
                            )}
                            {file.metadata.camera.settings && (
                              <div className="mt-2">
                                <p className="font-medium">Beállítások:</p>
                                <div className="ml-2 space-y-1">
                                  {file.metadata.camera.settings.aperture && (
                                    <p>Rekeszérték: f/{file.metadata.camera.settings.aperture}</p>
                                  )}
                                  {file.metadata.camera.settings.shutter && (
                                    <p>Zársebesség: {file.metadata.camera.settings.shutter}s</p>
                                  )}
                                  {file.metadata.camera.settings.iso && (
                                    <p>ISO: {file.metadata.camera.settings.iso}</p>
                                  )}
                                  {file.metadata.camera.settings.focalLength && (
                                    <p>Gyújtótávolság: {file.metadata.camera.settings.focalLength}</p>
                                  )}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                      
                      {/* GPS Data */}
                      {file.metadata.location && (
                        <div>
                          <h6 className="font-medium text-gray-900 mb-2 flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            GPS koordináták
                          </h6>
                          <div className="space-y-1 text-gray-600">
                            <p>Szélesség: {file.metadata.location.latitude.toFixed(6)}°</p>
                            <p>Hosszúság: {file.metadata.location.longitude.toFixed(6)}°</p>
                            {file.metadata.location.altitude && (
                              <p>Magasság: {file.metadata.location.altitude.toFixed(1)}m</p>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}