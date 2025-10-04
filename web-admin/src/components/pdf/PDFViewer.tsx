'use client'

import React, { useState, useEffect, useRef, useCallback } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  FileText,
  Download,
  Share2,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Maximize2,
  Minimize2,
  ChevronLeft,
  ChevronRight,
  Play,
  Pause,
  MoreVertical,
  Copy,
  ExternalLink,
  Eye,
  User,
  Calendar,
  Hash,
  CheckCircle2,
  AlertTriangle,
  Clock,
  QrCode,
  FileCheck,
  PenTool,
  Shield,
  Info
} from 'lucide-react'

interface PDFDocument {
  id: string
  name: string
  url: string
  size: number
  pages: number
  createdAt: Date
  modifiedAt: Date
  status: 'draft' | 'review' | 'approved' | 'signed' | 'archived'
  version: string
  author: string
  category: 'maintenance' | 'inspection' | 'contract' | 'manual' | 'report'
  metadata: {
    checksum: string
    encrypted: boolean
    hasSignature: boolean
    signingInfo?: {
      signer: string
      signedAt: Date
      certificateValid: boolean
    }
    tags: string[]
    description?: string
  }
  permissions: {
    canDownload: boolean
    canShare: boolean
    canPrint: boolean
    canEdit: boolean
  }
  qrCode?: {
    content: string
    position: { page: number; x: number; y: number }
    size: number
  }
}

interface PDFViewerProps {
  document?: PDFDocument
  onClose?: () => void
  className?: string
}

// Mock PDF document data
const mockPDFDocument: PDFDocument = {
  id: 'DOC-2025-001',
  name: 'Garázs Karbantartási Jelentés - 2025 Q1.pdf',
  url: 'https://mozilla.github.io/pdf.js/web/compressed.tracemonkey-pldi-09.pdf', // Sample PDF
  size: 45 * 1024 * 1024, // 45 MB
  pages: 14,
  createdAt: new Date(2025, 2, 15),
  modifiedAt: new Date(2025, 9, 4),
  status: 'signed',
  version: '2.1',
  author: 'Nagy Péter',
  category: 'maintenance',
  metadata: {
    checksum: 'sha256:a1b2c3d4e5f6...',
    encrypted: true,
    hasSignature: true,
    signingInfo: {
      signer: 'Kovács János (Karbantartási Vezető)',
      signedAt: new Date(2025, 9, 3, 14, 30),
      certificateValid: true
    },
    tags: ['Q1-2025', 'karbantartás', 'garázs-A', 'jóváhagyott'],
    description: 'Negyedéves karbantartási jelentés az A épület garázsainak állapotáról és elvégzett munkákról.'
  },
  permissions: {
    canDownload: true,
    canShare: true,
    canPrint: true,
    canEdit: false
  },
  qrCode: {
    content: 'https://garagereg.hu/documents/DOC-2025-001/verify',
    position: { page: 1, x: 500, y: 50 },
    size: 80
  }
}

export function PDFViewer({ document = mockPDFDocument, onClose, className }: PDFViewerProps) {
  const [currentPage, setCurrentPage] = useState(1)
  const [zoom, setZoom] = useState(100)
  const [rotation, setRotation] = useState(0)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [loadingProgress, setLoadingProgress] = useState(0)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [selectedAction, setSelectedAction] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  
  const viewerRef = useRef<HTMLDivElement>(null)
  const iframeRef = useRef<HTMLIFrameElement>(null)

  // Simulate PDF loading progress for large files
  useEffect(() => {
    setIsLoading(true)
    setLoadingProgress(0)
    
    const loadingInterval = setInterval(() => {
      setLoadingProgress(prev => {
        if (prev >= 100) {
          clearInterval(loadingInterval)
          setTimeout(() => setIsLoading(false), 500)
          return 100
        }
        return prev + Math.random() * 15
      })
    }, 200)
    
    return () => clearInterval(loadingInterval)
  }, [document.url])

  const handleDownload = useCallback(async () => {
    if (!document.permissions.canDownload) {
      alert('Nincs jogosultsága a dokumentum letöltéséhez.')
      return
    }
    
    try {
      setSelectedAction('download')
      
      // Simulate download process
      const response = await fetch(document.url)
      const blob = await response.blob()
      
      const url = window.URL.createObjectURL(blob)
      const link = window.document.createElement('a')
      link.href = url
      link.download = document.name
      window.document.body.appendChild(link)
      link.click()
      window.document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      
      setTimeout(() => setSelectedAction(null), 2000)
    } catch (error) {
      console.error('Download failed:', error)
      setError('Letöltés sikertelen')
      setTimeout(() => setError(null), 3000)
    }
  }, [document])

  const handleShare = useCallback(async () => {
    if (!document.permissions.canShare) {
      alert('Nincs jogosultsága a dokumentum megosztásához.')
      return
    }
    
    setSelectedAction('share')
    
    const shareData = {
      title: document.name,
      text: `GarageReg dokumentum: ${document.name}`,
      url: window.location.href
    }
    
    if (navigator.share) {
      try {
        await navigator.share(shareData)
      } catch (error) {
        console.error('Sharing failed:', error)
      }
    } else {
      // Fallback to clipboard
      await navigator.clipboard.writeText(window.location.href)
      alert('Link vágólapra másolva!')
    }
    
    setTimeout(() => setSelectedAction(null), 2000)
  }, [document])

  const handlePrint = useCallback(() => {
    if (!document.permissions.canPrint) {
      alert('Nincs jogosultsága a dokumentum nyomtatásához.')
      return
    }
    
    setSelectedAction('print')
    window.print()
    setTimeout(() => setSelectedAction(null), 2000)
  }, [document])

  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(prev + 25, 300))
  }, [])

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(prev - 25, 25))
  }, [])

  const handleRotate = useCallback(() => {
    setRotation(prev => (prev + 90) % 360)
  }, [])

  const handlePageChange = useCallback((newPage: number) => {
    setCurrentPage(Math.max(1, Math.min(newPage, document.pages)))
  }, [document.pages])

  const toggleFullscreen = useCallback(() => {
    if (!window.document.fullscreenElement) {
      viewerRef.current?.requestFullscreen()
      setIsFullscreen(true)
    } else {
      window.document.exitFullscreen()
      setIsFullscreen(false)
    }
  }, [])

  const formatFileSize = useCallback((bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }, [])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'draft':
        return <Clock className="w-4 h-4 text-yellow-600" />
      case 'review':
        return <Eye className="w-4 h-4 text-blue-600" />
      case 'approved':
        return <CheckCircle2 className="w-4 h-4 text-green-600" />
      case 'signed':
        return <PenTool className="w-4 h-4 text-purple-600" />
      case 'archived':
        return <FileCheck className="w-4 h-4 text-gray-600" />
      default:
        return <FileText className="w-4 h-4 text-gray-600" />
    }
  }

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'draft': return 'Tervezet'
      case 'review': return 'Ellenőrzés'
      case 'approved': return 'Jóváhagyott'
      case 'signed': return 'Aláírt'
      case 'archived': return 'Archivált'
      default: return status
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'maintenance': return 'Karbantartás'
      case 'inspection': return 'Ellenőrzés'
      case 'contract': return 'Szerződés'
      case 'manual': return 'Kézikönyv'
      case 'report': return 'Jelentés'
      default: return category
    }
  }

  return (
    <div className={`flex h-screen bg-gray-50 ${className}`} ref={viewerRef}>
      {/* Sidebar */}
      {sidebarOpen && (
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          {/* Sidebar Header */}
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900 truncate">
                Dokumentum részletek
              </h3>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSidebarOpen(false)}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
            </div>
            
            <div className="flex items-center gap-2 mb-2">
              {getStatusIcon(document.status)}
              <Badge variant={document.status === 'signed' ? 'default' : 'secondary'}>
                {getStatusLabel(document.status)}
              </Badge>
            </div>
            
            <h4 className="font-medium text-gray-900 mb-1">{document.name}</h4>
            <p className="text-sm text-gray-600">{getCategoryLabel(document.category)}</p>
          </div>

          {/* Sidebar Content */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-6">
              {/* Basic Info */}
              <div>
                <h5 className="text-sm font-medium text-gray-900 mb-3">Alapinformációk</h5>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <Hash className="w-4 h-4 text-gray-400" />
                    <div>
                      <div className="text-xs text-gray-500">Azonosító</div>
                      <div className="text-sm font-medium">{document.id}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-gray-400" />
                    <div>
                      <div className="text-xs text-gray-500">Szerző</div>
                      <div className="text-sm font-medium">{document.author}</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-gray-400" />
                    <div>
                      <div className="text-xs text-gray-500">Verzió / Oldalak</div>
                      <div className="text-sm font-medium">v{document.version} • {document.pages} oldal</div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <div>
                      <div className="text-xs text-gray-500">Módosítva</div>
                      <div className="text-sm font-medium">
                        {document.modifiedAt.toLocaleDateString('hu-HU')}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Security & Signature Info */}
              {document.metadata.hasSignature && document.metadata.signingInfo && (
                <>
                  <div>
                    <h5 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                      <PenTool className="w-4 h-4" />
                      Aláírási információ
                    </h5>
                    <div className="space-y-3">
                      <div className="flex items-start gap-2">
                        <Shield className={`w-4 h-4 mt-0.5 ${
                          document.metadata.signingInfo.certificateValid 
                            ? 'text-green-600' 
                            : 'text-red-600'
                        }`} />
                        <div>
                          <div className="text-xs text-gray-500">Aláíró</div>
                          <div className="text-sm font-medium">{document.metadata.signingInfo.signer}</div>
                          <div className="text-xs text-gray-500 mt-1">
                            {document.metadata.signingInfo.signedAt.toLocaleString('hu-HU')}
                          </div>
                          <div className={`text-xs mt-1 ${
                            document.metadata.signingInfo.certificateValid
                              ? 'text-green-600'
                              : 'text-red-600'
                          }`}>
                            {document.metadata.signingInfo.certificateValid 
                              ? '✓ Érvényes tanúsítvány' 
                              : '⚠ Érvénytelen tanúsítvány'
                            }
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <Separator />
                </>
              )}

              {/* QR Code Preview */}
              {document.qrCode && (
                <>
                  <div>
                    <h5 className="text-sm font-medium text-gray-900 mb-3 flex items-center gap-2">
                      <QrCode className="w-4 h-4" />
                      QR kód előnézet
                    </h5>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className="w-24 h-24 bg-white border rounded-lg mx-auto mb-3 flex items-center justify-center">
                        <div className="w-16 h-16 bg-gray-800 rounded grid grid-cols-8 gap-px">
                          {[...Array(64)].map((_, i) => (
                            <div 
                              key={i} 
                              className={`${Math.random() > 0.5 ? 'bg-white' : 'bg-gray-800'}`}
                            />
                          ))}
                        </div>
                      </div>
                      <div className="text-xs text-gray-600">
                        Oldal {document.qrCode.position.page} • {document.qrCode.size}×{document.qrCode.size}px
                      </div>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="mt-2 text-xs"
                        onClick={() => window.open(document.qrCode?.content, '_blank')}
                      >
                        <ExternalLink className="w-3 h-3 mr-1" />
                        Ellenőrzés
                      </Button>
                    </div>
                  </div>

                  <Separator />
                </>
              )}

              {/* Metadata */}
              <div>
                <h5 className="text-sm font-medium text-gray-900 mb-3">Metaadatok</h5>
                <div className="space-y-3">
                  <div>
                    <div className="text-xs text-gray-500">Fájlméret</div>
                    <div className="text-sm font-medium">{formatFileSize(document.size)}</div>
                  </div>
                  
                  <div>
                    <div className="text-xs text-gray-500">Ellenőrző összeg</div>
                    <div className="text-xs font-mono bg-gray-100 p-1 rounded truncate">
                      {document.metadata.checksum}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    <Shield className={`w-3 h-3 ${document.metadata.encrypted ? 'text-green-600' : 'text-gray-400'}`} />
                    <span className="text-xs">
                      {document.metadata.encrypted ? 'Titkosított' : 'Nem titkosított'}
                    </span>
                  </div>
                  
                  {document.metadata.description && (
                    <div>
                      <div className="text-xs text-gray-500 mb-1">Leírás</div>
                      <div className="text-sm text-gray-700">{document.metadata.description}</div>
                    </div>
                  )}
                  
                  {document.metadata.tags.length > 0 && (
                    <div>
                      <div className="text-xs text-gray-500 mb-2">Címkék</div>
                      <div className="flex flex-wrap gap-1">
                        {document.metadata.tags.map(tag => (
                          <Badge key={tag} variant="outline" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </ScrollArea>

          {/* Sidebar Actions */}
          <div className="p-4 border-t border-gray-200">
            <div className="space-y-2">
              <Button 
                onClick={handleDownload}
                disabled={!document.permissions.canDownload || selectedAction === 'download'}
                className="w-full"
                variant={selectedAction === 'download' ? 'default' : 'outline'}
              >
                <Download className="w-4 h-4 mr-2" />
                {selectedAction === 'download' ? 'Letöltés...' : 'Letöltés'}
              </Button>
              
              <div className="flex gap-2">
                <Button 
                  onClick={handleShare}
                  disabled={!document.permissions.canShare || selectedAction === 'share'}
                  variant="outline"
                  className="flex-1"
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  Megosztás
                </Button>
                
                <Button 
                  onClick={handlePrint}
                  disabled={!document.permissions.canPrint || selectedAction === 'print'}
                  variant="outline"
                  className="flex-1"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Nyomtatás
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main PDF Viewer */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {!sidebarOpen && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setSidebarOpen(true)}
              >
                <Info className="w-4 h-4" />
              </Button>
            )}
            
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage <= 1}
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              <span className="text-sm font-medium">
                {currentPage} / {document.pages}
              </span>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage >= document.pages}
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={handleZoomOut}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            
            <span className="text-sm font-medium min-w-[60px] text-center">
              {zoom}%
            </span>
            
            <Button variant="outline" size="sm" onClick={handleZoomIn}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            
            <Button variant="outline" size="sm" onClick={handleRotate}>
              <RotateCw className="w-4 h-4" />
            </Button>
            
            <Button variant="outline" size="sm" onClick={toggleFullscreen}>
              {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  <MoreVertical className="w-4 h-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleDownload} disabled={!document.permissions.canDownload}>
                  <Download className="w-4 h-4 mr-2" />
                  Letöltés
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handleShare} disabled={!document.permissions.canShare}>
                  <Share2 className="w-4 h-4 mr-2" />
                  Megosztás
                </DropdownMenuItem>
                <DropdownMenuItem onClick={handlePrint} disabled={!document.permissions.canPrint}>
                  <FileText className="w-4 h-4 mr-2" />
                  Nyomtatás
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => navigator.clipboard.writeText(document.url)}>
                  <Copy className="w-4 h-4 mr-2" />
                  URL másolása
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {onClose && (
              <Button variant="outline" size="sm" onClick={onClose}>
                ✕
              </Button>
            )}
          </div>
        </div>

        {/* PDF Content Area */}
        <div className="flex-1 relative bg-gray-100">
          {isLoading && (
            <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10">
              <div className="text-center">
                <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <div className="text-sm font-medium text-gray-700 mb-2">
                  PDF betöltése... ({Math.round(loadingProgress)}%)
                </div>
                <Progress value={loadingProgress} className="w-64" />
                <div className="text-xs text-gray-500 mt-2">
                  Nagy fájlok betöltése eltarthat egy ideig
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center z-10">
              <div className="text-center">
                <AlertTriangle className="w-12 h-12 text-red-600 mx-auto mb-4" />
                <div className="text-lg font-medium text-gray-900 mb-2">Hiba történt</div>
                <div className="text-sm text-gray-600">{error}</div>
                <Button 
                  onClick={() => setError(null)}
                  className="mt-4"
                >
                  Újrapróbálás
                </Button>
              </div>
            </div>
          )}

          {/* PDF Iframe */}
          <iframe
            ref={iframeRef}
            src={`${document.url}#page=${currentPage}&zoom=${zoom}`}
            className="w-full h-full border-0"
            style={{ 
              transform: `rotate(${rotation}deg)`,
              transformOrigin: 'center center'
            }}
            onLoad={() => {
              setIsLoading(false)
              setLoadingProgress(100)
            }}
            onError={() => {
              setIsLoading(false)
              setError('PDF betöltése sikertelen')
            }}
            title={document.name}
          />
        </div>
      </div>
    </div>
  )
}