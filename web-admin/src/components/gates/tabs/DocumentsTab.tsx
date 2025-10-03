'use client'

import { useState, useEffect, useRef } from 'react'
import { toast } from 'react-hot-toast'
import {
  Upload,
  FileText,
  Image,
  Film,
  Download,
  Trash2,
  Eye,
  Search,
  Filter,
  Plus,
  X,
  Paperclip
} from 'lucide-react'
import {
  GateDocument,
  GateDocumentType,
  GateDocumentTypeLabels
} from '@/lib/types/gate-detail'

interface DocumentsTabProps {
  gateId: string
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function DocumentsTab({ gateId, isLoading, setIsLoading }: DocumentsTabProps) {
  const [documents, setDocuments] = useState<GateDocument[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [typeFilter, setTypeFilter] = useState<GateDocumentType | 'all'>('all')
  const [showUploadForm, setShowUploadForm] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadDocuments()
  }, [gateId])

  const loadDocuments = async () => {
    try {
      setIsLoading(true)
      
      // Mock data - replace with actual API call
      const mockDocuments: GateDocument[] = [
        {
          id: '1',
          gateId,
          name: 'Használati útmutató',
          type: 'manual',
          filename: 'gate_manual.pdf',
          fileSize: 2048576,
          mimeType: 'application/pdf',
          uploadedBy: 'Kovács János',
          uploadedAt: new Date('2023-01-15T10:30:00'),
          description: 'A kapu használati és karbantartási útmutatója',
          tags: ['útmutató', 'karbantartás'],
          url: '#'
        },
        {
          id: '2',
          gateId,
          name: 'Garancia dokumentum',
          type: 'warranty',
          filename: 'warranty_certificate.pdf',
          fileSize: 1024000,
          mimeType: 'application/pdf',
          uploadedBy: 'Nagy Péter',
          uploadedAt: new Date('2023-01-15T11:00:00'),
          description: '2 éves gyártói garancia',
          tags: ['garancia'],
          url: '#'
        },
        {
          id: '3',
          gateId,
          name: 'Telepítési fotó',
          type: 'photo',
          filename: 'installation_photo.jpg',
          fileSize: 3145728,
          mimeType: 'image/jpeg',
          uploadedBy: 'Szabó Anna',
          uploadedAt: new Date('2023-01-15T15:45:00'),
          description: 'Fotó a telepítés után',
          tags: ['telepítés', 'fotó'],
          url: '#'
        },
        {
          id: '4',
          gateId,
          name: 'Karbantartási jegyzőkönyv',
          type: 'maintenance_log',
          filename: 'maintenance_log_2023.xlsx',
          fileSize: 512000,
          mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          uploadedBy: 'Dr. Tóth Ferenc',
          uploadedAt: new Date('2023-12-31T16:00:00'),
          description: '2023. évi karbantartási dokumentáció',
          tags: ['karbantartás', '2023'],
          url: '#'
        }
      ]
      
      // Sort by upload date descending
      mockDocuments.sort((a, b) => b.uploadedAt.getTime() - a.uploadedAt.getTime())
      setDocuments(mockDocuments)
    } catch (error) {
      toast.error('Hiba a dokumentumok betöltésekor')
      console.error('Load documents error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const getFileIcon = (mimeType: string, type: GateDocumentType) => {
    if (mimeType.startsWith('image/')) {
      return <Image className="h-8 w-8 text-green-600" />
    } else if (mimeType.startsWith('video/')) {
      return <Film className="h-8 w-8 text-purple-600" />
    } else if (mimeType.includes('pdf')) {
      return <FileText className="h-8 w-8 text-red-600" />
    } else if (mimeType.includes('sheet') || mimeType.includes('excel')) {
      return <FileText className="h-8 w-8 text-green-600" />
    } else if (mimeType.includes('document') || mimeType.includes('word')) {
      return <FileText className="h-8 w-8 text-blue-600" />
    } else {
      return <FileText className="h-8 w-8 text-gray-600" />
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
  }

  const handleFileUpload = async (files: FileList) => {
    if (!files.length) return

    try {
      setIsLoading(true)
      
      for (const file of Array.from(files)) {
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
          toast.error(`A fájl "${file.name}" túl nagy (max 10MB)`)
          continue
        }

        // Create new document entry
        const newDocument: GateDocument = {
          id: `new-${Date.now()}-${Math.random()}`,
          gateId,
          name: file.name.replace(/\.[^/.]+$/, ""), // Remove extension
          type: 'other', // Default type
          filename: file.name,
          fileSize: file.size,
          mimeType: file.type || 'application/octet-stream',
          uploadedBy: 'Jelenlegi felhasználó', // Replace with actual user
          uploadedAt: new Date(),
          url: URL.createObjectURL(file) // Temporary URL
        }
        
        setDocuments(prev => [newDocument, ...prev])
        toast.success(`Fájl "${file.name}" sikeresen feltöltve`)
      }
      
      setShowUploadForm(false)
    } catch (error) {
      toast.error('Hiba a fájl feltöltésekor')
      console.error('File upload error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    
    const files = e.dataTransfer.files
    if (files.length) {
      handleFileUpload(files)
    }
  }

  const handleDeleteDocument = async (documentId: string, documentName: string) => {
    if (!confirm(`Biztosan törli a "${documentName}" dokumentumot?`)) return
    
    try {
      setIsLoading(true)
      setDocuments(prev => prev.filter(doc => doc.id !== documentId))
      toast.success('Dokumentum törölve')
    } catch (error) {
      toast.error('Hiba a dokumentum törlésekor')
      console.error('Delete document error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownload = (document: GateDocument) => {
    // In a real app, this would download from the server
    const link = window.document.createElement('a')
    link.href = document.url
    link.download = document.filename
    link.click()
    toast.success('Letöltés megkezdve')
  }

  const filteredDocuments = documents.filter(document => {
    const matchesSearch = document.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         document.filename.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         document.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         document.tags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesType = typeFilter === 'all' || document.type === typeFilter
    
    return matchesSearch && matchesType
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Dokumentumok</h2>
          <p className="text-sm text-gray-600 mt-1">
            {documents.length} dokumentum található
          </p>
        </div>
        
        <button
          onClick={() => setShowUploadForm(!showUploadForm)}
          disabled={isLoading}
          className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          <Plus className="h-4 w-4 mr-2" />
          Dokumentum feltöltése
        </button>
      </div>

      {/* Search and Filter */}
      <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Keresés név, fájlnév, leírás vagy címke alapján..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-gray-400" />
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value as GateDocumentType | 'all')}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Minden típus</option>
            {Object.entries(GateDocumentTypeLabels).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Upload Form */}
      {showUploadForm && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Dokumentum feltöltése</h3>
            <button
              onClick={() => setShowUploadForm(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          {/* Drag and Drop Area */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${dragOver 
                ? 'border-blue-500 bg-blue-100' 
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
              }
            `}
          >
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">
              Húzza ide a fájlokat vagy kattintson a tallózáshoz
            </h4>
            <p className="text-gray-600 text-sm">
              Maximális fájlméret: 10MB. Támogatott formátumok: PDF, Word, Excel, képek, videók
            </p>
            
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={(e) => e.target.files && handleFileUpload(e.target.files)}
              className="hidden"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png,.gif,.mp4,.avi,.mov"
            />
          </div>
        </div>
      )}

      {/* Documents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDocuments.map((document) => (
          <div key={document.id} className="bg-white border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
            <div className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  {getFileIcon(document.mimeType, document.type)}
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {document.name}
                    </h3>
                    <p className="text-xs text-gray-500 truncate">
                      {document.filename}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-1">
                  <button
                    onClick={() => handleDownload(document)}
                    className="p-1 text-gray-400 hover:text-blue-600 rounded"
                    title="Letöltés"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteDocument(document.id, document.name)}
                    disabled={isLoading}
                    className="p-1 text-gray-400 hover:text-red-600 rounded disabled:opacity-50"
                    title="Törlés"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
              
              <div className="space-y-2 text-xs text-gray-600">
                <div className="flex items-center justify-between">
                  <span>Típus:</span>
                  <span className="font-medium">{GateDocumentTypeLabels[document.type]}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span>Méret:</span>
                  <span className="font-medium">{formatFileSize(document.fileSize)}</span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span>Feltöltve:</span>
                  <span className="font-medium">
                    {document.uploadedAt.toLocaleDateString('hu-HU')}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span>Feltöltő:</span>
                  <span className="font-medium">{document.uploadedBy}</span>
                </div>
              </div>
              
              {document.description && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-600">{document.description}</p>
                </div>
              )}
              
              {document.tags && document.tags.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="flex flex-wrap gap-1">
                    {document.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-gray-100 text-gray-800"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            <div className="px-4 py-3 bg-gray-50 border-t border-gray-200">
              <button
                onClick={() => handleDownload(document)}
                className="w-full inline-flex items-center justify-center px-3 py-2 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md transition-colors"
              >
                <Eye className="h-4 w-4 mr-2" />
                Megtekintés
              </button>
            </div>
          </div>
        ))}
        
        {filteredDocuments.length === 0 && (
          <div className="col-span-full text-center py-12">
            <Paperclip className="h-12 w-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Nincsenek dokumentumok</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || typeFilter !== 'all' 
                ? 'Nincs a szűrési feltételeknek megfelelő dokumentum'
                : 'Még nincsenek feltöltött dokumentumok ehhez a kapuhoz'
              }
            </p>
            {!searchTerm && typeFilter === 'all' && (
              <button
                onClick={() => setShowUploadForm(true)}
                className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Első dokumentum feltöltése
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}