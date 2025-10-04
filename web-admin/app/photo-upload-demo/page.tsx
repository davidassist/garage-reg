'use client'

import React, { useState, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Camera, 
  Zap, 
  Shield, 
  FileImage, 
  Globe,
  CheckCircle,
  Upload,
  RefreshCw,
  Settings
} from 'lucide-react'
import { EnhancedPhotoUploader } from '@/components/photo-upload/EnhancedPhotoUploader'
import { EnhancedPhotoGallery } from '@/components/photo-upload/EnhancedPhotoGallery'
import { PhotoUpload, PhotoMetadata, UploadProgress } from '@/lib/types/photo-upload'

export default function PhotoUploadDemo() {
  const [uploadedPhotos, setUploadedPhotos] = useState<PhotoUpload[]>([])
  const [uploadStats, setUploadStats] = useState({
    totalFiles: 0,
    successfulUploads: 0,
    failedUploads: 0,
    totalBytes: 0
  })
  const [activeTab, setActiveTab] = useState('uploader')

  // Mock data for gallery demonstration
  const mockPhotos: PhotoUpload[] = [
    {
      id: 'demo-1',
      originalName: 'budapest_parliament.jpg',
      urls: {
        original: 'https://images.unsplash.com/photo-1541963463532-d68292c34d19?w=1200',
        thumbnail: 'https://images.unsplash.com/photo-1541963463532-d68292c34d19?w=200&h=200&fit=crop'
      },
      metadata: {
        fileSize: 2456789,
        mimeType: 'image/jpeg',
        width: 4000,
        height: 3000,
        takenAt: new Date('2024-03-15T14:30:00Z'),
        location: {
          latitude: 47.5017,
          longitude: 19.0458,
          altitude: 102
        },
        camera: {
          make: 'Canon',
          model: 'EOS R5',
          lens: 'RF 24-70mm f/2.8L IS USM',
          settings: {
            aperture: 8,
            shutter: '1/125',
            iso: 200,
            focalLength: '50mm',
            flash: false
          }
        },
        checksum: 'a1b2c3d4e5f6'
      },
      status: 'completed',
      createdAt: new Date('2024-03-15T14:32:00Z').toISOString(),
      updatedAt: new Date('2024-03-15T14:32:00Z').toISOString()
    },
    {
      id: 'demo-2',
      originalName: 'danube_sunset.jpg',
      urls: {
        original: 'https://images.unsplash.com/photo-1565191999001-551c187427bb?w=1200',
        thumbnail: 'https://images.unsplash.com/photo-1565191999001-551c187427bb?w=200&h=200&fit=crop'
      },
      metadata: {
        fileSize: 3789456,
        mimeType: 'image/jpeg',
        width: 5000,
        height: 3333,
        takenAt: new Date('2024-03-10T19:45:00Z'),
        location: {
          latitude: 47.4979,
          longitude: 19.0402
        },
        camera: {
          make: 'Sony',
          model: 'Alpha 7R IV',
          settings: {
            aperture: 11,
            shutter: '1/60',
            iso: 100,
            focalLength: '85mm'
          }
        },
        checksum: 'b2c3d4e5f6g7'
      },
      status: 'completed',
      createdAt: new Date('2024-03-10T19:47:00Z').toISOString(),
      updatedAt: new Date('2024-03-10T19:47:00Z').toISOString()
    },
    {
      id: 'demo-3',
      originalName: 'szechenyi_baths.jpg',
      urls: {
        original: 'https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=1200',
        thumbnail: 'https://images.unsplash.com/photo-1572120360610-d971b9d7767c?w=200&h=200&fit=crop'
      },
      metadata: {
        fileSize: 1987654,
        mimeType: 'image/jpeg',
        width: 3456,
        height: 2304,
        takenAt: new Date('2024-02-28T16:20:00Z'),
        location: {
          latitude: 47.5186,
          longitude: 19.0814
        },
        camera: {
          make: 'Nikon',
          model: 'D850',
          settings: {
            aperture: 5.6,
            shutter: '1/250',
            iso: 400
          }
        },
        checksum: 'c3d4e5f6g7h8'
      },
      status: 'completed',
      createdAt: new Date('2024-02-28T16:22:00Z').toISOString(),
      updatedAt: new Date('2024-02-28T16:22:00Z').toISOString()
    }
  ]

  // Handle upload completion
  const handleUploadComplete = useCallback((photos: PhotoUpload[]) => {
    setUploadedPhotos(prev => [...prev, ...photos])
    setUploadStats(prev => ({
      ...prev,
      totalFiles: prev.totalFiles + photos.length,
      successfulUploads: prev.successfulUploads + photos.length,
      totalBytes: prev.totalBytes + photos.reduce((sum, p) => sum + p.metadata.fileSize, 0)
    }))
    
    // Switch to gallery tab after upload
    setActiveTab('gallery')
  }, [])

  // Handle upload progress
  const handleUploadProgress = useCallback((fileId: string, progress: UploadProgress) => {
    console.log(`Upload progress for ${fileId}:`, progress)
  }, [])

  // Handle upload error
  const handleUploadError = useCallback((fileId: string, error: string) => {
    console.error(`Upload error for ${fileId}:`, error)
    setUploadStats(prev => ({
      ...prev,
      failedUploads: prev.failedUploads + 1
    }))
  }, [])

  // Handle photo deletion from gallery
  const handlePhotoDelete = useCallback((photoId: string) => {
    setUploadedPhotos(prev => prev.filter(p => p.id !== photoId))
  }, [])

  // Handle photo editing
  const handlePhotoEdit = useCallback((photoId: string, metadata: Partial<PhotoMetadata>) => {
    setUploadedPhotos(prev => prev.map(p => 
      p.id === photoId 
        ? { ...p, metadata: { ...p.metadata, ...metadata } }
        : p
    ))
  }, [])

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  const allPhotos = [...mockPhotos, ...uploadedPhotos]

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Fejlett fotó feltöltési rendszer
        </h1>
        <p className="text-lg text-gray-600 mb-6">
          Enterprise szintű fotó kezelés drag&drop feltöltéssel, EXIF feldolgozással és fejlett galéria funkcionalitással.
        </p>

        {/* Feature Highlights */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardContent className="p-4 text-center">
              <Zap className="w-8 h-8 mx-auto mb-2 text-blue-500" />
              <h3 className="font-semibold text-sm">Többszálú feltöltés</h3>
              <p className="text-xs text-gray-500">3 párhuzamos upload</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4 text-center">
              <RefreshCw className="w-8 h-8 mx-auto mb-2 text-green-500" />
              <h3 className="font-semibold text-sm">Folytatható</h3>
              <p className="text-xs text-gray-500">Megszakítás utáni folytatás</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4 text-center">
              <Camera className="w-8 h-8 mx-auto mb-2 text-purple-500" />
              <h3 className="font-semibold text-sm">EXIF feldolgozás</h3>
              <p className="text-xs text-gray-500">GPS + kamera adatok</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4 text-center">
              <Shield className="w-8 h-8 mx-auto mb-2 text-red-500" />
              <h3 className="font-semibold text-sm">100MB kapacitás</h3>
              <p className="text-xs text-gray-500">Magas teljesítmény</p>
            </CardContent>
          </Card>
        </div>

        {/* Upload Statistics */}
        {uploadStats.totalFiles > 0 && (
          <Card className="bg-gray-50">
            <CardContent className="p-4">
              <h3 className="font-semibold mb-2">Feltöltési statisztikák</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-gray-500">Összes fájl:</span>
                  <p className="font-medium">{uploadStats.totalFiles}</p>
                </div>
                <div>
                  <span className="text-gray-500">Sikeres:</span>
                  <p className="font-medium text-green-600">{uploadStats.successfulUploads}</p>
                </div>
                <div>
                  <span className="text-gray-500">Sikertelen:</span>
                  <p className="font-medium text-red-600">{uploadStats.failedUploads}</p>
                </div>
                <div>
                  <span className="text-gray-500">Összméret:</span>
                  <p className="font-medium">{formatBytes(uploadStats.totalBytes)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="uploader" className="flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Feltöltés
          </TabsTrigger>
          <TabsTrigger value="gallery" className="flex items-center gap-2">
            <FileImage className="w-4 h-4" />
            Galéria ({allPhotos.length})
          </TabsTrigger>
          <TabsTrigger value="demo" className="flex items-center gap-2">
            <Settings className="w-4 h-4" />
            Bemutatók
          </TabsTrigger>
        </TabsList>

        {/* Uploader Tab */}
        <TabsContent value="uploader" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Fotó feltöltés</CardTitle>
              <CardDescription>
                Húzd be a képeket vagy tallózz a fájlok között. A rendszer automatikusan feldolgozza az EXIF adatokat és optimalizálja a feltöltést.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <EnhancedPhotoUploader
                onUploadComplete={handleUploadComplete}
                onUploadProgress={handleUploadProgress}
                onUploadError={handleUploadError}
                maxFiles={20}
                maxFileSize={25 * 1024 * 1024} // 25MB
                maxTotalSize={100 * 1024 * 1024} // 100MB
                concurrent={3}
                autoStart={true}
                showPreviews={true}
                showMetadata={true}
                className="w-full"
              />
            </CardContent>
          </Card>

          {/* Upload Features */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="w-5 h-5 text-blue-500" />
                  Teljesítmény funkciók
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Többszálú feltöltés</h4>
                    <p className="text-sm text-gray-600">Akár 3 fájl párhuzamos feltöltése a maximális sebességért</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Chunk-alapú feltöltés</h4>
                    <p className="text-sm text-gray-600">1MB-os darabokra bontás a megbízható átvitelért</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Automatikus újrapróbálkozás</h4>
                    <p className="text-sm text-gray-600">Hálózati hibák esetén intelligens retry logika</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Presigned URL-ek</h4>
                    <p className="text-sm text-gray-600">Biztonságos közvetlen S3 feltöltés server-side aláírással</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Camera className="w-5 h-5 text-purple-500" />
                  Metadata feldolgozás
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">EXIF kinyerés</h4>
                    <p className="text-sm text-gray-600">Kamera beállítások, dátum, technikai paraméterek</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">GPS koordináták</h4>
                    <p className="text-sm text-gray-600">Helymeghatározási adatok és magasság információ</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Automatikus preview</h4>
                    <p className="text-sm text-gray-600">Azonnali thumbnail generálás feltöltés közben</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Fájl validáció</h4>
                    <p className="text-sm text-gray-600">Típus, méret és integritás ellenőrzés</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Gallery Tab */}
        <TabsContent value="gallery" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Fotó galéria</CardTitle>
              <CardDescription>
                Interaktív lightbox galéria EXIF adatok megjelenítésével és fejlett navigációval.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <EnhancedPhotoGallery
                photos={allPhotos}
                onPhotoDelete={handlePhotoDelete}
                onPhotoEdit={handlePhotoEdit}
                maxHeight={800}
                showThumbnails={true}
                enableSelection={false}
                className="w-full"
              />
            </CardContent>
          </Card>

          {/* Gallery Features */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-indigo-500" />
                  Lightbox funkciók
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Zoom és forgatás</h4>
                    <p className="text-sm text-gray-600">5x zoom, 90° forgatás, mouse/touch pan</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Billentyűzet navigáció</h4>
                    <p className="text-sm text-gray-600">Nyíl gombok, ESC, +/- zoom, I info panel</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Teljes EXIF megjelenítés</h4>
                    <p className="text-sm text-gray-600">Kamera adatok, GPS, expozíciós beállítások</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Letöltés és megosztás</h4>
                    <p className="text-sm text-gray-600">Eredeti kép letöltése, link másolása</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileImage className="w-5 h-5 text-orange-500" />
                  Galéria nézetek
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Rács nézet</h4>
                    <p className="text-sm text-gray-600">Rendezett thumbnail rács reszponzív elrendezéssel</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Mozaik nézet</h4>
                    <p className="text-sm text-gray-600">Pinterest-stílusú változó méretű elrendezés</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Lista nézet</h4>
                    <p className="text-sm text-gray-600">Részletes információkkal bővített lista</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                  <div>
                    <h4 className="font-medium">Rendezés és szűrés</h4>
                    <p className="text-sm text-gray-600">Dátum, név, méret szerint rendezés</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Demo Tab */}
        <TabsContent value="demo" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Rendszer bemutatók</CardTitle>
              <CardDescription>
                Interaktív funkció bemutatók és teljesítmény tesztek.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
                  <Upload className="w-6 h-6" />
                  <span className="font-medium">Feltöltés teszt</span>
                  <span className="text-sm text-gray-500">100MB fájl szimulálása</span>
                </Button>
                
                <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
                  <RefreshCw className="w-6 h-6" />
                  <span className="font-medium">Megszakítás teszt</span>
                  <span className="text-sm text-gray-500">Hálózat kiesés szimuláció</span>
                </Button>
                
                <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
                  <Camera className="w-6 h-6" />
                  <span className="font-medium">EXIF feldolgozás</span>
                  <span className="text-sm text-gray-500">Metadata kinyerés demo</span>
                </Button>
                
                <Button variant="outline" className="h-auto p-4 flex flex-col gap-2">
                  <Zap className="w-6 h-6" />
                  <span className="font-medium">Teljesítmény teszt</span>
                  <span className="text-sm text-gray-500">Sebességmérés és optimalizálás</span>
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Technical Specifications */}
          <Card>
            <CardHeader>
              <CardTitle>Műszaki specifikációk</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Feltöltési paraméterek</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Max fájlméret:</span>
                      <Badge variant="outline">25 MB</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Max összméret:</span>
                      <Badge variant="outline">100 MB</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Max fájlok száma:</span>
                      <Badge variant="outline">50</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Párhuzamos feltöltés:</span>
                      <Badge variant="outline">3</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Chunk méret:</span>
                      <Badge variant="outline">1 MB</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>Újrapróbálkozások:</span>
                      <Badge variant="outline">3</Badge>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-3">Támogatott formátumok</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>JPEG/JPG:</span>
                      <Badge variant="default">✓</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>PNG:</span>
                      <Badge variant="default">✓</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>WebP:</span>
                      <Badge variant="default">✓</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>GIF:</span>
                      <Badge variant="default">✓</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>BMP:</span>
                      <Badge variant="default">✓</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span>TIFF:</span>
                      <Badge variant="default">✓</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}