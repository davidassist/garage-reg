'use client'

import { useState, useEffect } from 'react'
import { PhotoUploader, PhotoGallery } from '@/components/photo-upload'
import { PhotoUpload } from '@/lib/types/photo-upload'

export default function SimplePhotoTest() {
  const [photos, setPhotos] = useState<PhotoUpload[]>([])
  const [uploaderKey, setUploaderKey] = useState(0)
  const [stats, setStats] = useState({
    totalSize: 0,
    withExif: 0,
    withGps: 0,
    avgUploadSpeed: 0
  })

  // Update stats when photos change
  useEffect(() => {
    const totalSize = photos.reduce((sum, p) => sum + p.metadata.fileSize, 0)
    const withExif = photos.filter(p => p.metadata.camera || p.metadata.location).length
    const withGps = photos.filter(p => p.metadata.location).length
    // uploadSpeed is part of uploadProgress
    const speeds = photos
      .filter(p => p.uploadProgress?.speed)
      .map(p => p.uploadProgress!.speed!)
    const avgUploadSpeed = speeds.length > 0 ? speeds.reduce((a, b) => a + b, 0) / speeds.length : 0

    setStats({ totalSize, withExif, withGps, avgUploadSpeed })
  }, [photos])

  const handleUploadComplete = (newPhotos: PhotoUpload[]) => {
    setPhotos(prev => [...prev, ...newPhotos])
  }

  const handleDeletePhoto = (photoId: string) => {
    setPhotos(prev => prev.filter(p => p.id !== photoId))
  }

  const resetAll = () => {
    setPhotos([])
    setUploaderKey(prev => prev + 1)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Fotó Teszt Oldal
              </h1>
              <p className="text-gray-600 mt-1">
                Drag & drop, presigned URL, többszálú feltöltés teszt
              </p>
            </div>
            <button
              onClick={resetAll}
              className="px-4 py-2 text-sm font-medium text-red-700 bg-red-50 
                         border border-red-200 rounded-md hover:bg-red-100 
                         transition-colors"
            >
              🗑️ Összes törlése
            </button>
          </div>

          {/* Stats Bar */}
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-sm text-blue-600">Képek száma</div>
              <div className="text-lg font-semibold text-blue-900">
                {photos.length}
              </div>
            </div>
            
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-sm text-green-600">Összes méret</div>
              <div className="text-lg font-semibold text-green-900">
                {formatFileSize(stats.totalSize)}
              </div>
            </div>
            
            <div className="bg-purple-50 p-3 rounded-lg">
              <div className="text-sm text-purple-600">EXIF adattal</div>
              <div className="text-lg font-semibold text-purple-900">
                {stats.withExif}
              </div>
            </div>
            
            <div className="bg-orange-50 p-3 rounded-lg">
              <div className="text-sm text-orange-600">GPS adattal</div>
              <div className="text-lg font-semibold text-orange-900">
                {stats.withGps}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
        {/* Uploader Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            📤 Fotó Feltöltés
          </h2>
          
          <PhotoUploader
            key={uploaderKey}
            maxFiles={10}
            maxTotalSize={50 * 1024 * 1024} // 50MB total
            onUploadComplete={handleUploadComplete}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8"
          />
        </div>

        {/* Gallery Section */}
        {photos.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">
                🖼️ Galéria ({photos.length})
              </h2>
              
              {stats.avgUploadSpeed > 0 && (
                <div className="text-sm text-gray-500">
                  Átlag sebesség: {formatSpeed(stats.avgUploadSpeed)}
                </div>
              )}
            </div>
            
            <PhotoGallery
              photos={photos}
              onPhotoDelete={handleDeletePhoto}
              className="grid-cols-2 md:grid-cols-4 lg:grid-cols-6"
            />
          </div>
        )}

        {/* Empty State */}
        {photos.length === 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-12 text-center">
            <div className="text-4xl mb-4">📷</div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Még nincsenek feltöltött képek
            </h3>
            <p className="text-gray-500 max-w-md mx-auto">
              Húzd be a képeket a fenti területre, vagy kattints a feltöltéshoz. 
              A rendszer automatikusan kinyeri az EXIF adatokat és GPS koordinátákat.
            </p>
          </div>
        )}

        {/* Technical Info */}
        <div className="bg-gray-900 text-white rounded-lg p-6">
          <h3 className="text-lg font-medium mb-3">⚙️ Rendszer Állapot</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Feltöltési Beállítások:</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• Max 10 fájl egyszerre</li>
                <li>• Max 10MB fájlonként</li>
                <li>• Max 50MB összesen</li>
                <li>• 3 párhuzamos feltöltés</li>
                <li>• 5MB chunk méret</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Támogatott Funkciók:</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>• JPEG, PNG, WebP formátumok</li>
                <li>• EXIF metaadat kinyerés</li>
                <li>• GPS koordináták feldolgozás</li>
                <li>• MD5 checksum validáció</li>
                <li>• Resumable uploads</li>
              </ul>
            </div>
          </div>
          
          {/* Connection Status */}
          <div className="mt-4 pt-4 border-t border-gray-700">
            <div className="flex items-center text-sm">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              <span className="text-gray-300">Online - Feltöltés elérhető</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Helper functions
function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

function formatSpeed(bytesPerSecond: number): string {
  if (bytesPerSecond === 0) return '0 B/s'
  const k = 1024
  const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s']
  const i = Math.floor(Math.log(bytesPerSecond) / Math.log(k))
  return `${parseFloat((bytesPerSecond / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}