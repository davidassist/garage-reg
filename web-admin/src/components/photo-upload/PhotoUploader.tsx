'use client'

import React, { useCallback, useState, useRef, useEffect } from 'react'
import { 
  Upload, 
  Camera, 
  X, 
  Play, 
  Pause, 
  RotateCcw, 
  AlertCircle, 
  CheckCircle,
  Image as ImageIcon,
  Clock,
  Wifi,
  WifiOff
} from 'lucide-react'
import { uploadService } from '@/lib/services/upload-service'
import { PhotoUpload, UploadProgress, UploadError } from '@/lib/types/photo-upload'

interface PhotoUploaderProps {
  maxFiles?: number
  maxTotalSize?: number // bytes
  onUploadComplete?: (uploads: PhotoUpload[]) => void
  onError?: (error: UploadError) => void
  className?: string
  disabled?: boolean
}

interface UploadingFile {
  id: string
  file: File
  preview: string
  progress: UploadProgress
  error?: UploadError
}

export function PhotoUploader({
  maxFiles = 20,
  maxTotalSize = 100 * 1024 * 1024, // 100MB
  onUploadComplete,
  onError,
  className = '',
  disabled = false
}: PhotoUploaderProps) {
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([])
  const [completedUploads, setCompletedUploads] = useState<PhotoUpload[]>([])
  const [dragOver, setDragOver] = useState(false)
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const cameraInputRef = useRef<HTMLInputElement>(null)
  const dropZoneRef = useRef<HTMLDivElement>(null)

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => setIsOnline(true)
    const handleOffline = () => setIsOnline(false)

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Handle file selection
  const handleFileSelect = useCallback((files: FileList | File[]) => {
    if (disabled || !isOnline) return

    const fileArray = Array.from(files)
    
    // Check limits
    if (uploadingFiles.length + completedUploads.length + fileArray.length > maxFiles) {
      onError?.({
        code: 'QUOTA_EXCEEDED',
        message: `Maximum ${maxFiles} kép tölthető fel`,
        retryable: false
      })
      return
    }

    // Create uploading file entries
    const newUploadingFiles: UploadingFile[] = []
    
    for (const file of fileArray) {
      const id = crypto.randomUUID()
      const preview = URL.createObjectURL(file)
      
      const uploadingFile: UploadingFile = {
        id,
        file,
        preview,
        progress: {
          id,
          fileName: file.name,
          totalBytes: file.size,
          uploadedBytes: 0,
          percentage: 0,
          status: 'pending'
        }
      }
      
      newUploadingFiles.push(uploadingFile)
    }

    setUploadingFiles(prev => [...prev, ...newUploadingFiles])

    // Start upload
    uploadService.uploadFiles(
      fileArray,
      handleUploadProgress,
      handleUploadComplete,
      handleUploadError
    )
  }, [disabled, isOnline, uploadingFiles, completedUploads, maxFiles, onError])

  // Handle upload progress
  const handleUploadProgress = useCallback((fileId: string, progress: UploadProgress) => {
    setUploadingFiles(prev => 
      prev.map(file => 
        file.id === fileId 
          ? { ...file, progress } 
          : file
      )
    )
  }, [])

  // Handle upload completion
  const handleUploadComplete = useCallback((fileId: string, upload: PhotoUpload) => {
    setUploadingFiles(prev => prev.filter(file => file.id !== fileId))
    setCompletedUploads(prev => {
      const newUploads = [...prev, upload]
      onUploadComplete?.(newUploads)
      return newUploads
    })
  }, [onUploadComplete])

  // Handle upload error
  const handleUploadError = useCallback((fileId: string, error: UploadError) => {
    setUploadingFiles(prev => 
      prev.map(file => 
        file.id === fileId 
          ? { ...file, error, progress: { ...file.progress, status: 'failed' } } 
          : file
      )
    )
    onError?.(error)
  }, [onError])

  // Drag and drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    // Only set dragOver to false if leaving the drop zone entirely
    if (dropZoneRef.current && !dropZoneRef.current.contains(e.relatedTarget as Node)) {
      setDragOver(false)
    }
  }, [])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragOver(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      handleFileSelect(files)
    }
  }, [handleFileSelect])

  // File input handlers
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFileSelect(e.target.files)
    }
    e.target.value = '' // Reset input
  }, [handleFileSelect])

  // Action handlers
  const triggerFileInput = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  const triggerCameraInput = useCallback(() => {
    cameraInputRef.current?.click()
  }, [])

  const pauseUpload = useCallback((fileId: string) => {
    uploadService.pauseUpload(fileId)
    setUploadingFiles(prev => 
      prev.map(file => 
        file.id === fileId 
          ? { ...file, progress: { ...file.progress, status: 'paused' } } 
          : file
      )
    )
  }, [])

  const resumeUpload = useCallback((fileId: string) => {
    uploadService.resumeUpload_single(fileId)
    setUploadingFiles(prev => 
      prev.map(file => 
        file.id === fileId 
          ? { ...file, progress: { ...file.progress, status: 'uploading' } } 
          : file
      )
    )
  }, [])

  const cancelUpload = useCallback((fileId: string) => {
    uploadService.cancelUpload(fileId)
    setUploadingFiles(prev => {
      const file = prev.find(f => f.id === fileId)
      if (file) {
        URL.revokeObjectURL(file.preview)
      }
      return prev.filter(f => f.id !== fileId)
    })
  }, [])

  const retryUpload = useCallback((fileId: string) => {
    const file = uploadingFiles.find(f => f.id === fileId)
    if (file) {
      setUploadingFiles(prev => 
        prev.map(f => 
          f.id === fileId 
            ? { ...f, error: undefined, progress: { ...f.progress, status: 'pending' } } 
            : f
        )
      )
      
      uploadService.uploadFiles(
        [file.file],
        handleUploadProgress,
        handleUploadComplete,
        handleUploadError
      )
    }
  }, [uploadingFiles, handleUploadProgress, handleUploadComplete, handleUploadError])

  // Format file size
  const formatFileSize = useCallback((bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }, [])

  // Format time
  const formatTime = useCallback((seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = Math.round(seconds % 60)
    return `${minutes}m ${remainingSeconds}s`
  }, [])

  // Calculate totals
  const totalFiles = uploadingFiles.length + completedUploads.length
  const totalSize = [...uploadingFiles.map(f => f.file.size), ...completedUploads.map(u => u.metadata.fileSize)]
    .reduce((sum, size) => sum + size, 0)

  return (
    <div className={`photo-uploader ${className}`}>
      {/* Connection status */}
      {!isOnline && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <div className="flex items-center">
            <WifiOff className="w-5 h-5 text-yellow-600 mr-2" />
            <span className="text-sm text-yellow-800">
              Nincs internetkapcsolat. A feltöltés folytatódik a kapcsolat helyreállításakor.
            </span>
          </div>
        </div>
      )}

      {/* Upload stats */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Képek:</span>
            <span className="ml-2 font-medium">{totalFiles}/{maxFiles}</span>
          </div>
          <div>
            <span className="text-gray-600">Méret:</span>
            <span className="ml-2 font-medium">{formatFileSize(totalSize)}/{formatFileSize(maxTotalSize)}</span>
          </div>
          <div>
            <span className="text-gray-600">Feltöltés alatt:</span>
            <span className="ml-2 font-medium">{uploadingFiles.length}</span>
          </div>
          <div className="flex items-center">
            {isOnline ? (
              <>
                <Wifi className="w-4 h-4 text-green-500 mr-1" />
                <span className="text-green-600">Online</span>
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4 text-red-500 mr-1" />
                <span className="text-red-600">Offline</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Drop zone */}
      <div
        ref={dropZoneRef}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300'}
          ${disabled || !isOnline ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:border-gray-400'}
        `}
      >
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 text-gray-400">
            <Upload className="w-full h-full" />
          </div>

          <div>
            <p className="text-lg font-medium text-gray-900">
              Húzza ide a képeket vagy kattintson a tallózáshoz
            </p>
            <p className="text-sm text-gray-500 mt-2">
              JPEG, PNG, WebP, HEIC • Max 50MB képenként • Összesen max 100MB
            </p>
          </div>

          <div className="flex justify-center space-x-4">
            <button
              type="button"
              onClick={triggerFileInput}
              disabled={disabled || !isOnline}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ImageIcon className="w-4 h-4 mr-2" />
              Galéria
            </button>

            <button
              type="button"
              onClick={triggerCameraInput}
              disabled={disabled || !isOnline}
              className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Camera className="w-4 h-4 mr-2" />
              Kamera
            </button>
          </div>
        </div>
      </div>

      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        onChange={handleFileInputChange}
        className="hidden"
      />
      
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileInputChange}
        className="hidden"
      />

      {/* Uploading files */}
      {uploadingFiles.length > 0 && (
        <div className="mt-6 space-y-3">
          <h3 className="text-lg font-medium text-gray-900">
            Feltöltés folyamatban ({uploadingFiles.length})
          </h3>
          
          {uploadingFiles.map((file) => (
            <div key={file.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start space-x-4">
                {/* Preview */}
                <div className="flex-shrink-0">
                  <img
                    src={file.preview}
                    alt={file.file.name}
                    className="w-16 h-16 object-cover rounded-md"
                  />
                </div>

                {/* File info and progress */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {file.file.name}
                      </p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(file.file.size)}
                      </p>
                    </div>

                    {/* Status badge */}
                    <div className="flex-shrink-0 ml-2">
                      {file.progress.status === 'uploading' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          <div className="w-2 h-2 bg-blue-600 rounded-full mr-1 animate-pulse" />
                          Feltöltés
                        </span>
                      )}
                      {file.progress.status === 'paused' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          <Pause className="w-3 h-3 mr-1" />
                          Szüneteltetve
                        </span>
                      )}
                      {file.progress.status === 'failed' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          <AlertCircle className="w-3 h-3 mr-1" />
                          Hiba
                        </span>
                      )}
                      {file.progress.status === 'completed' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          Kész
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                    <div 
                      className={`h-2 rounded-full transition-all duration-300 ${
                        file.error ? 'bg-red-500' : 'bg-blue-600'
                      }`}
                      style={{ width: `${file.progress.percentage}%` }}
                    />
                  </div>

                  {/* Progress details */}
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>
                      {Math.round(file.progress.percentage)}% • 
                      {formatFileSize(file.progress.uploadedBytes)}/{formatFileSize(file.progress.totalBytes)}
                    </span>
                    
                    {file.progress.speed && file.progress.estimatedTime && (
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatTime(file.progress.estimatedTime)} • 
                        {formatFileSize(file.progress.speed)}/s
                      </span>
                    )}
                  </div>

                  {/* Error message */}
                  {file.error && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-600">
                      {file.error.message}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex-shrink-0 flex space-x-1">
                  {file.progress.status === 'uploading' && (
                    <button
                      onClick={() => pauseUpload(file.id)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Szüneteltetés"
                    >
                      <Pause className="w-4 h-4" />
                    </button>
                  )}

                  {file.progress.status === 'paused' && (
                    <button
                      onClick={() => resumeUpload(file.id)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Folytatás"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                  )}

                  {file.progress.status === 'failed' && (
                    <button
                      onClick={() => retryUpload(file.id)}
                      className="p-1 text-gray-400 hover:text-gray-600"
                      title="Újra"
                    >
                      <RotateCcw className="w-4 h-4" />
                    </button>
                  )}

                  <button
                    onClick={() => cancelUpload(file.id)}
                    className="p-1 text-gray-400 hover:text-red-600"
                    title="Mégse"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}