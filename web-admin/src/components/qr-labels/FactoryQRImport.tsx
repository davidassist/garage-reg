'use client'

import { useState, useRef } from 'react'
import { 
  Upload, 
  FileText, 
  CheckCircle2, 
  AlertTriangle, 
  X, 
  Download,
  FileSpreadsheet
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { QRLabelsAPI, FactoryQRImportResult as APIFactoryQRImportResult, QRMappingRequest } from '@/lib/services/qr-labels-api'

// Temporary toast implementation
const toast = ({ title, description, variant }: { title: string, description?: string, variant?: 'default' | 'destructive' }) => {
  console.log(`${variant === 'destructive' ? 'ERROR' : 'INFO'}: ${title}${description ? ` - ${description}` : ''}`)
  alert(`${title}${description ? `: ${description}` : ''}`)
}

interface FactoryQRImportProps {
  onImportComplete?: (result: APIFactoryQRImportResult) => void
  onClose?: () => void
}

export function FactoryQRImport({ onImportComplete, onClose }: FactoryQRImportProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [batchName, setBatchName] = useState('')
  const [importResult, setImportResult] = useState<APIFactoryQRImportResult | null>(null)
  const [previewData, setPreviewData] = useState<string[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Generate factory QR mapping
  const [gateCount, setGateCount] = useState(10)
  const [generatedBatch, setGeneratedBatch] = useState('')

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.csv')) {
      toast({
        title: 'Hibás fájl típus',
        description: 'Csak CSV fájlok támogatottak',
        variant: 'destructive'
      })
      return
    }

    setUploadedFile(file)
    
    // Generate batch name from filename
    const baseName = file.name.replace('.csv', '')
    setBatchName(`import_${baseName}_${Date.now()}`)

    // Preview file content
    const reader = new FileReader()
    reader.onload = (e) => {
      const content = e.target?.result as string
      const lines = content.split('\n').slice(0, 6) // Show first 5 lines + header
      setPreviewData(lines)
    }
    reader.readAsText(file)
  }

  const handleImport = async () => {
    if (!uploadedFile) return

    setIsUploading(true)
    setImportResult(null)

    try {
      // Use real API
      const result = await QRLabelsAPI.importFactoryQR(uploadedFile, batchName)
      setImportResult(result)
      onImportComplete?.(result)

      toast({
        title: 'Import befejezve',
        description: `${result.successCount} kapu sikeresen frissítve`,
        variant: result.errorCount > 0 ? 'destructive' : 'default'
      })

    } catch (error) {
      console.error('Import failed:', error)
      toast({
        title: 'Import hiba',
        description: 'A fájl importálása sikertelen volt',
        variant: 'destructive'
      })
    } finally {
      setIsUploading(false)
    }
  }

  const handleGenerateMapping = async () => {
    setIsGenerating(true)

    try {
      const request: QRMappingRequest = {
        gateCount: gateCount,
        batchName: generatedBatch || undefined
      }

      // Use real API
      await QRLabelsAPI.downloadFactoryQRMapping(request)

      toast({
        title: 'Mapping generálva',
        description: `${gateCount} kapu mapping CSV letöltve`
      })

    } catch (error) {
      console.error('Mapping generation failed:', error)
      toast({
        title: 'Generálás hiba',
        description: 'A mapping generálása sikertelen volt',
        variant: 'destructive'
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const resetForm = () => {
    setUploadedFile(null)
    setBatchName('')
    setImportResult(null)
    setPreviewData([])
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleClose = () => {
    setIsOpen(false)
    resetForm()
    onClose?.()
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline" size="sm">
          <Upload className="h-4 w-4 mr-2" />
          Gyári QR
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileSpreadsheet className="h-5 w-5" />
            Gyári QR kezelés
          </DialogTitle>
          <DialogDescription>
            Gyári QR mapping generálása és CSV import
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Mapping generálás */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Download className="h-4 w-4" />
                Gyári QR mapping generálás
              </CardTitle>
              <CardDescription>
                CSV fájl létrehozása előre gyártott QR tokenekkel
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="gateCount">Kapuk száma</Label>
                  <Input
                    id="gateCount"
                    type="number"
                    min="1"
                    max="10000"
                    value={gateCount}
                    onChange={(e) => setGateCount(parseInt(e.target.value) || 10)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="batchName">Batch név (opcionális)</Label>
                  <Input
                    id="batchName"
                    placeholder="pl. factory_batch_2024"
                    value={generatedBatch}
                    onChange={(e) => setGeneratedBatch(e.target.value)}
                  />
                </div>
              </div>

              <div className="bg-gray-50 p-3 rounded-md text-sm">
                <p className="font-medium mb-2">Generált CSV formátum:</p>
                <code className="text-xs bg-white p-2 rounded block">
                  gate_code,factory_qr,batch,generated_at<br/>
                  GATE-0001,FQR-batch-abc123def,factory_batch_2024,2024-10-03T12:00:00<br/>
                  GATE-0002,FQR-batch-def456ghi,factory_batch_2024,2024-10-03T12:00:01
                </code>
              </div>

              <Button 
                onClick={handleGenerateMapping} 
                disabled={isGenerating}
                className="w-full"
              >
                {isGenerating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generálás...
                  </>
                ) : (
                  <>
                    <Download className="h-4 w-4 mr-2" />
                    CSV letöltés ({gateCount} kapu)
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          <Separator />

          {/* CSV Import */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <Upload className="h-4 w-4" />
                Gyári QR CSV import
              </CardTitle>
              <CardDescription>
                Gyári QR tokenek hozzárendelése kapukhoz CSV fájlból
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="csvFile">CSV fájl kiválasztása</Label>
                <div className="flex gap-2">
                  <Input
                    id="csvFile"
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    className="flex-1"
                  />
                  {uploadedFile && (
                    <Button variant="outline" size="icon" onClick={resetForm}>
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>

              {uploadedFile && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="batchNameInput">Batch név</Label>
                    <Input
                      id="batchNameInput"
                      value={batchName}
                      onChange={(e) => setBatchName(e.target.value)}
                      placeholder="Import batch neve"
                    />
                  </div>

                  {previewData.length > 0 && (
                    <div className="space-y-2">
                      <Label>Fájl előnézet</Label>
                      <div className="bg-gray-50 p-3 rounded-md">
                        <p className="text-sm text-gray-600 mb-2">
                          {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
                        </p>
                        <pre className="text-xs bg-white p-2 rounded overflow-x-auto">
                          {previewData.join('\n')}
                          {previewData.length >= 6 && '\n...'}
                        </pre>
                      </div>
                    </div>
                  )}

                  <div className="bg-blue-50 p-3 rounded-md text-sm">
                    <p className="font-medium mb-2">Támogatott CSV formátumok:</p>
                    <ul className="text-xs space-y-1">
                      <li>• <code>gate_id,factory_qr</code> - Kapu ID és QR token</li>
                      <li>• <code>gate_code,factory_qr</code> - Kapu kód és QR token</li>
                      <li>• <code>kapu_id,qr_token</code> - Magyar fejlécek</li>
                    </ul>
                  </div>

                  <Button 
                    onClick={handleImport} 
                    disabled={isUploading || !batchName.trim()}
                    className="w-full"
                  >
                    {isUploading ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Importálás...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        CSV importálása
                      </>
                    )}
                  </Button>
                </div>
              )}

              {/* Import eredmény */}
              {importResult && (
                <div className="space-y-3 pt-4 border-t">
                  <div className="flex items-center gap-2">
                    {importResult.errorCount === 0 ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-5 w-5 text-yellow-600" />
                    )}
                    <span className="font-medium">Import eredmény</span>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {importResult.successCount}
                      </div>
                      <div className="text-sm text-gray-600">Sikeres</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">
                        {importResult.errorCount}
                      </div>
                      <div className="text-sm text-gray-600">Hiba</div>
                    </div>
                    <div className="text-center">
                      <Badge variant="outline" className="text-xs">
                        {importResult.batchName}
                      </Badge>
                      <div className="text-sm text-gray-600">Batch</div>
                    </div>
                  </div>

                  {importResult.errors.length > 0 && (
                    <div className="space-y-2">
                      <Label>Hibák részletei</Label>
                      <Textarea
                        value={importResult.errors.join('\n')}
                        readOnly
                        className="h-24 text-sm"
                      />
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Bezárás */}
          <div className="flex justify-end">
            <Button variant="outline" onClick={handleClose}>
              Bezárás
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}