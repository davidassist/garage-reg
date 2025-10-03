'use client'

import { useState } from 'react'
import { PhotoManager } from '@/components/photo-upload'
import { PhotoUpload } from '@/lib/types/photo-upload'

export default function PhotoUploadDemo() {
  const [photos, setPhotos] = useState<PhotoUpload[]>([])

  const handlePhotosChange = (newPhotos: PhotoUpload[]) => {
    setPhotos(newPhotos)
    console.log('Photos updated:', newPhotos)
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Fotófeltöltő Rendszer Demo
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Drag & drop feltöltő presigned URL-ekkel, többszálú feltöltés, haladásjelző, 
            galéria lightbox és EXIF összefoglaló.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-900 mb-2">🚀 Többszálú Feltöltés</h3>
            <p className="text-sm text-gray-600">
              Akár 3 párhuzamos feltöltés presigned URL-ekkel, 5MB chunks, 
              automatikus újraküldés hibák esetén.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-900 mb-2">📊 Haladásjelző</h3>
            <p className="text-sm text-gray-600">
              Valós idejű feltöltési státusz, sebesség mérés, becsült idő, 
              szüneteltetés/folytatás támogatás.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <h3 className="font-semibold text-gray-900 mb-2">🖼️ Galéria & EXIF</h3>
            <p className="text-sm text-gray-600">
              Lightbox előnézet, EXIF adatok (kamera, GPS, beállítások), 
              nagyítás, forgatás, letöltés.
            </p>
          </div>
        </div>

        {/* Current stats */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Jelenlegi Állapot</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Feltöltött képek:</span>
              <span className="ml-2 font-medium">{photos.length}</span>
            </div>
            <div>
              <span className="text-gray-600">Összes méret:</span>
              <span className="ml-2 font-medium">
                {formatFileSize(photos.reduce((sum, p) => sum + p.metadata.fileSize, 0))}
              </span>
            </div>
            <div>
              <span className="text-gray-600">EXIF adatokkal:</span>
              <span className="ml-2 font-medium">
                {photos.filter(p => p.metadata.camera || p.metadata.location).length}
              </span>
            </div>
            <div>
              <span className="text-gray-600">GPS koordinátákkal:</span>
              <span className="ml-2 font-medium">
                {photos.filter(p => p.metadata.location).length}
              </span>
            </div>
          </div>
        </div>

        {/* Photo Manager */}
        <PhotoManager
          initialPhotos={photos}
          maxFiles={20}
          maxTotalSize={100 * 1024 * 1024} // 100MB
          onPhotosChange={handlePhotosChange}
          className="bg-white rounded-lg shadow-sm border p-6"
        />

        {/* Technical Details */}
        <div className="mt-8 bg-gray-900 text-white rounded-lg p-6">
          <h3 className="text-lg font-medium mb-4">🔧 Technikai Részletek</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Feltöltés:</h4>
              <ul className="space-y-1 text-gray-400">
                <li>• Presigned URL-ek AWS S3 kompatibilis</li>
                <li>• Multipart upload 5MB+ fájlokhoz</li>
                <li>• Maximum 3 párhuzamos feltöltés</li>
                <li>• Automatikus újrapróbálkozás (3x)</li>
                <li>• Resumable uploads session alapon</li>
                <li>• MD5 checksum validáció</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-medium text-gray-300 mb-2">Funkciók:</h4>
              <ul className="space-y-1 text-gray-400">
                <li>• EXIF adatok automatikus kinyerése</li>
                <li>• GPS koordináták támogatás</li>
                <li>• Lightbox galéria zoom/rotate</li>
                <li>• Drag & drop + kamera rögzítés</li>
                <li>• Offline/online állapot kezelés</li>
                <li>• Real-time értesítések</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Debug Info */}
        {photos.length > 0 && (
          <div className="mt-6 bg-gray-100 rounded-lg p-4">
            <details>
              <summary className="font-medium text-gray-900 cursor-pointer">
                Debug Információk ({photos.length} kép)
              </summary>
              <pre className="mt-2 text-xs bg-white p-4 rounded border overflow-auto">
                {JSON.stringify(photos, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>
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