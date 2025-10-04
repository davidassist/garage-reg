'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  FileText, 
  Upload, 
  Download, 
  Eye, 
  Trash2, 
  Plus,
  File,
  Image,
  FileImage,
  ChevronDown,
  ChevronUp
} from 'lucide-react'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { toast } from '@/components/ui/use-toast'

interface GateDocumentsProps {
  gateId: string
}

const mockDocuments = [
  {
    id: '1',
    name: 'CAME BX-243 Kezelési utasítás',
    type: 'manual',
    filename: 'came-bx243-manual-hu.pdf',
    size: 2456789,
    uploadDate: '2024-01-15T10:00:00',
    uploadedBy: 'Rendszergazda',
    category: 'manual',
    description: 'Gyári kezelési és karbantartási utasítás'
  },
  {
    id: '2',
    name: 'Telepítési jegyzőkönyv',
    type: 'document',
    filename: 'installation-protocol-2024.pdf',
    size: 1234567,
    uploadDate: '2024-01-20T14:30:00',
    uploadedBy: 'Kiss János',
    category: 'installation',
    description: 'Hivatalos telepítési és átvételi dokumentum'
  },
  {
    id: '3',
    name: 'Áramköri rajz',
    type: 'drawing',
    filename: 'electrical-diagram.pdf',
    size: 3456789,
    uploadDate: '2024-01-15T16:45:00',
    uploadedBy: 'Kovács Gábor',
    category: 'technical',
    description: 'Részletes elektromos kapcsolási rajz'
  },
  {
    id: '4',
    name: 'Karbantartási napló',
    type: 'log',
    filename: 'maintenance-log-2024.xlsx',
    size: 456789,
    uploadDate: '2024-09-01T09:15:00',
    uploadedBy: 'Nagy Péter',
    category: 'maintenance',
    description: 'Havi karbantartási jelentések gyűjteménye'
  },
  {
    id: '5',
    name: 'Kapu fotó - telepítés után',
    type: 'image',
    filename: 'gate-photo-installed.jpg',
    size: 2345678,
    uploadDate: '2024-01-22T11:20:00',
    uploadedBy: 'Szabó Anna',
    category: 'photo',
    description: 'Telepítés utáni állapot dokumentálása'
  }
]

const documentCategories = {
  manual: 'Kezelési utasítás',
  installation: 'Telepítés',
  technical: 'Műszaki rajz',
  maintenance: 'Karbantartás',
  warranty: 'Garancia',
  photo: 'Fotó',
  other: 'Egyéb'
}

const getFileIcon = (type: string, filename: string) => {
  if (type === 'image' || filename.match(/\.(jpg|jpeg|png|gif|bmp)$/i)) {
    return <FileImage className="h-5 w-5 text-green-600" />
  }
  if (filename.match(/\.pdf$/i)) {
    return <FileText className="h-5 w-5 text-red-600" />
  }
  if (filename.match(/\.(doc|docx)$/i)) {
    return <FileText className="h-5 w-5 text-blue-600" />
  }
  if (filename.match(/\.(xls|xlsx)$/i)) {
    return <File className="h-5 w-5 text-green-600" />
  }
  return <File className="h-5 w-5 text-gray-600" />
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

export function GateDocuments({ gateId }: GateDocumentsProps) {
  const [documents, setDocuments] = useState(mockDocuments)
  const [documentsOpen, setDocumentsOpen] = useState(true)
  const [selectedCategory, setSelectedCategory] = useState<string>('all')

  const filteredDocuments = selectedCategory === 'all' 
    ? documents 
    : documents.filter(doc => doc.category === selectedCategory)

  const handleUpload = () => {
    // Simulate file upload
    toast({
      title: "Fájl feltöltése",
      description: "A fájl feltöltési funkció hamarosan elérhető lesz.",
    })
  }

  const handleDownload = (document: any) => {
    // Simulate file download
    toast({
      title: "Fájl letöltése",
      description: `${document.name} letöltése megkezdődött.`,
    })
  }

  const handlePreview = (document: any) => {
    // Simulate file preview
    toast({
      title: "Fájl előnézet",
      description: `${document.name} megnyitása új ablakban.`,
    })
  }

  const handleDelete = (id: string) => {
    setDocuments(prev => prev.filter(doc => doc.id !== id))
    toast({
      title: "Dokumentum törölve",
      description: "A dokumentum sikeresen eltávolításra került.",
    })
  }

  return (
    <div className="space-y-6">
      <Collapsible open={documentsOpen} onOpenChange={setDocumentsOpen}>
        <Card>
          <CollapsibleTrigger asChild>
            <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2" />
                  Dokumentumok ({filteredDocuments.length})
                </CardTitle>
                <div className="flex items-center space-x-2">
                  <Button
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      handleUpload()
                    }}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Feltöltés
                  </Button>
                  {documentsOpen ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </div>
              </div>
              <CardDescription>
                Kapu dokumentumok, kézikönyvek, rajzok és egyéb fájlok
              </CardDescription>
            </CardHeader>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <CardContent>
              <div className="space-y-4">
                {/* Category Filter */}
                <div className="flex flex-wrap gap-2">
                  <Button
                    size="sm"
                    variant={selectedCategory === 'all' ? 'default' : 'outline'}
                    onClick={() => setSelectedCategory('all')}
                  >
                    Összes
                  </Button>
                  {Object.entries(documentCategories).map(([key, label]) => (
                    <Button
                      key={key}
                      size="sm"
                      variant={selectedCategory === key ? 'default' : 'outline'}
                      onClick={() => setSelectedCategory(key)}
                    >
                      {label}
                    </Button>
                  ))}
                </div>

                {/* Documents Grid/Table */}
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Dokumentum</TableHead>
                        <TableHead>Kategória</TableHead>
                        <TableHead>Méret</TableHead>
                        <TableHead>Feltöltés dátuma</TableHead>
                        <TableHead>Feltöltő</TableHead>
                        <TableHead className="text-right">Műveletek</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredDocuments.map((document) => (
                        <TableRow key={document.id}>
                          <TableCell>
                            <div className="flex items-start space-x-3">
                              {getFileIcon(document.type, document.filename)}
                              <div className="flex-1">
                                <p className="font-medium">{document.name}</p>
                                <p className="text-sm text-muted-foreground">{document.description}</p>
                                <p className="text-xs text-muted-foreground font-mono">{document.filename}</p>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">
                              {documentCategories[document.category as keyof typeof documentCategories]}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-sm">
                            {formatFileSize(document.size)}
                          </TableCell>
                          <TableCell className="text-sm">
                            <div>
                              <p>{new Date(document.uploadDate).toLocaleDateString('hu-HU')}</p>
                              <p className="text-xs text-muted-foreground">
                                {new Date(document.uploadDate).toLocaleTimeString('hu-HU', { 
                                  hour: '2-digit', 
                                  minute: '2-digit' 
                                })}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell className="text-sm">
                            {document.uploadedBy}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end space-x-1">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handlePreview(document)}
                                title="Előnézet"
                              >
                                <Eye className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDownload(document)}
                                title="Letöltés"
                              >
                                <Download className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDelete(document.id)}
                                className="text-destructive hover:text-destructive"
                                title="Törlés"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                      {filteredDocuments.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                            <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                            <p>Nincsenek dokumentumok a kiválasztott kategóriában</p>
                            <Button 
                              className="mt-2" 
                              variant="outline" 
                              size="sm"
                              onClick={handleUpload}
                            >
                              <Plus className="h-4 w-4 mr-2" />
                              Első dokumentum hozzáadása
                            </Button>
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>

                {/* Upload Instructions */}
                {filteredDocuments.length > 0 && (
                  <Card className="bg-muted/20">
                    <CardContent className="p-4">
                      <div className="flex items-center space-x-3">
                        <Upload className="h-5 w-5 text-muted-foreground" />
                        <div>
                          <p className="font-medium">Dokumentum feltöltés</p>
                          <p className="text-sm text-muted-foreground">
                            Támogatott formátumok: PDF, DOC, DOCX, XLS, XLSX, JPG, PNG. Maximum fájlméret: 10MB
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </CardContent>
          </CollapsibleContent>
        </Card>
      </Collapsible>
    </div>
  )
}