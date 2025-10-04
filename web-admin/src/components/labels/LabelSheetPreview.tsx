'use client'

import React, { useState, useEffect, useCallback, useRef } from 'react'
import { toast } from 'react-hot-toast'
import { 
  Eye, 
  Printer, 
  Download, 
  Settings, 
  Plus, 
  Trash2,
  Copy,
  QrCode,
  FileText,
  Grid3x3,
  Maximize2,
  RefreshCw,
  Zap,
  Layout,
  Save,
  Upload
} from 'lucide-react'
import { 
  LabelFormat, 
  LabelFormatConfig, 
  LABEL_FORMATS, 
  GateLabelData, 
  QRConfig, 
  PrintJob 
} from '@/lib/types/labels'
import { LabelService } from '@/lib/services/label-service'
import { QRCodeService } from '@/lib/services/qr-service'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface LabelSheetPreviewProps {
  gates?: Array<{
    id: string
    name: string
    serialNumber?: string
    location?: string
  }>
  onPrint?: (printUrl: string) => void
}

export function LabelSheetPreview({ gates = [], onPrint }: LabelSheetPreviewProps) {
  // Core state
  const [selectedFormat, setSelectedFormat] = useState<LabelFormat>('A4_GRID_25x25')
  const [labelData, setLabelData] = useState<GateLabelData[]>([])
  const [qrConfig, setQRConfig] = useState<QRConfig>({
    size: 80,
    errorCorrectionLevel: 'M',
    margin: 1,
    includeText: true,
    textSize: 8,
    textPosition: 'below'
  })
  
  // Print configuration
  const [copies, setCopies] = useState(1)
  const [startPosition, setStartPosition] = useState(1)
  const [includeGrid, setIncludeGrid] = useState(false)
  const [includeMargins, setIncludeMargins] = useState(false)
  
  // UI state
  const [isGenerating, setIsGenerating] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)
  const [activeTab, setActiveTab] = useState('labels')
  
  // Preview iframe ref
  const previewRef = useRef<HTMLIFrameElement>(null)

  // Initialize label data from gates
  useEffect(() => {
    if (gates.length > 0 && labelData.length === 0) {
      const initialLabels: GateLabelData[] = gates.map(gate => ({
        gateId: gate.id,
        gateName: gate.name,
        serialNumber: gate.serialNumber || '',
        location: gate.location || '',
        qrContent: `${window.location.origin}/gates/${gate.id}`,
        additionalText: gate.location || ''
      }))
      setLabelData(initialLabels)
    }
  }, [gates, labelData.length])

  // Auto-update QR config based on format
  useEffect(() => {
    const format = LABEL_FORMATS[selectedFormat]
    const optimizedConfig = QRCodeService.optimizeQRConfigForSize(
      format.dimensions.width,
      format.dimensions.height,
      qrConfig.includeText
    )
    
    setQRConfig(prev => ({
      ...prev,
      ...optimizedConfig
    }))
  }, [selectedFormat, qrConfig.includeText])

  // Label management
  const handleAddLabel = useCallback(() => {
    const newLabel: GateLabelData = {
      gateId: `gate-${Date.now()}`,
      gateName: 'Új kapu',
      serialNumber: '',
      location: '',
      qrContent: `${window.location.origin}/gates/gate-${Date.now()}`,
      additionalText: ''
    }
    setLabelData(prev => [...prev, newLabel])
  }, [])

  const handleUpdateLabel = useCallback((index: number, updates: Partial<GateLabelData>) => {
    setLabelData(prev => prev.map((label, i) => 
      i === index ? { ...label, ...updates } : label
    ))
  }, [])

  const handleRemoveLabel = useCallback((index: number) => {
    setLabelData(prev => prev.filter((_, i) => i !== index))
  }, [])

  const handleDuplicateLabel = useCallback((index: number) => {
    const original = labelData[index]
    const duplicate = {
      ...original,
      gateId: `${original.gateId}-copy-${Date.now()}`,
      gateName: `${original.gateName} (másolat)`
    }
    setLabelData(prev => [...prev, duplicate])
  }, [labelData])

  // Preview generation
  const generatePreview = useCallback(async () => {
    if (labelData.length === 0) {
      toast.error('Legalább egy címkét hozzá kell adni')
      return
    }

    const validation = LabelService.validateLabelData(labelData)
    if (!validation.valid) {
      toast.error(validation.errors[0])
      return
    }

    setIsGenerating(true)

    try {
      const printJob: PrintJob = {
        format: selectedFormat,
        qrConfig,
        labels: labelData,
        copies,
        startPosition,
        includeGrid,
        includeMargins
      }

      const result = await LabelService.generateLabels(printJob)
      
      if (result.success && result.printUrl) {
        setPreviewUrl(result.printUrl)
        setIsPreviewOpen(true)
        toast.success(`${result.totalLabels} címke generálva (${result.pagesGenerated} oldal)`)
      } else {
        toast.error(result.error || 'Hiba a címke generálásakor')
      }
    } catch (error) {
      toast.error('Hiba a címke generálásakor')
      console.error('Label generation error:', error)
    } finally {
      setIsGenerating(false)
    }
  }, [labelData, selectedFormat, qrConfig, copies, startPosition, includeGrid, includeMargins])

  // Print handling
  const handlePrint = useCallback(async () => {
    if (!previewUrl) {
      await generatePreview()
      return
    }

    try {
      const printJob: PrintJob = {
        format: selectedFormat,
        qrConfig,
        labels: labelData,
        copies,
        startPosition,
        includeGrid,
        includeMargins
      }

      await LabelService.printLabels(printJob)
      onPrint?.(previewUrl)
      toast.success('Nyomtatási ablak megnyitva')
    } catch (error) {
      toast.error('Hiba a nyomtatás indításakor')
      console.error('Print error:', error)
    }
  }, [labelData, selectedFormat, qrConfig, copies, startPosition, includeGrid, includeMargins, previewUrl, onPrint])

  // Open print view in new window
  const handleOpenPrintView = useCallback(() => {
    if (!previewUrl) {
      toast.error('Először generálj előnézetet')
      return
    }
    
    const printWindow = window.open('/print/view', '_blank', 'width=1024,height=768,scrollbars=yes,resizable=yes')
    if (printWindow) {
      // Store print job for the new window
      const printJob: PrintJob = {
        format: selectedFormat,
        qrConfig,
        labels: labelData,
        copies,
        startPosition,
        includeGrid,
        includeMargins
      }
      sessionStorage.setItem('garagereg-print-preview', JSON.stringify(printJob))
    }
  }, [previewUrl, selectedFormat, qrConfig, labelData, copies, startPosition, includeGrid, includeMargins])

  // Download PDF
  const handleDownloadPDF = useCallback(async () => {
    if (!previewUrl) {
      await generatePreview()
      return
    }

    try {
      // Open print view for PDF save
      const printWindow = window.open('/print/view?mode=pdf', '_blank', 'width=1024,height=768')
      if (printWindow) {
        const printJob: PrintJob = {
          format: selectedFormat,
          qrConfig,
          labels: labelData,
          copies,
          startPosition,
          includeGrid,
          includeMargins
        }
        sessionStorage.setItem('garagereg-print-preview', JSON.stringify(printJob))
        
        toast.success('PDF előnézet megnyitva - használd a böngésző Mentés PDF-ként funkcióját')
      }
    } catch (error) {
      toast.error('Hiba a PDF generálásakor')
      console.error('PDF error:', error)
    }
  }, [previewUrl, selectedFormat, qrConfig, labelData, copies, startPosition, includeGrid, includeMargins])

  // Format info calculation
  const formatConfig = LABEL_FORMATS[selectedFormat]
  const labelsPerPage = LabelService.getLabelsPerPage(selectedFormat)
  const totalLabels = labelData.length * copies
  const pagesNeeded = Math.ceil(totalLabels / labelsPerPage)
  const startRow = Math.ceil(startPosition / (formatConfig.grid?.cols || 1))

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Címke generálás</h2>
          <p className="mt-1 text-sm text-gray-600">
            Több QR kód A4 címkelapon, méretezés és nyomtatóbarát PDF
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={generatePreview}
            disabled={isGenerating || labelData.length === 0}
            className="gap-2"
          >
            <Eye className="w-4 h-4" />
            {isGenerating ? 'Generálás...' : 'Előnézet'}
          </Button>
          
          <Button
            variant="outline"
            onClick={handleOpenPrintView}
            disabled={!previewUrl}
            className="gap-2"
          >
            <Layout className="w-4 h-4" />
            Print View
          </Button>
          
          <Button
            onClick={handlePrint}
            disabled={labelData.length === 0}
            className="gap-2"
          >
            <Printer className="w-4 h-4" />
            Nyomtatás
          </Button>
          
          <Button
            variant="outline"
            onClick={handleDownloadPDF}
            disabled={!previewUrl}
            className="gap-2"
          >
            <Download className="w-4 h-4" />
            PDF
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="labels" className="gap-2">
            <FileText className="w-4 h-4" />
            Címkék
          </TabsTrigger>
          <TabsTrigger value="format" className="gap-2">
            <Layout className="w-4 h-4" />
            Formátum
          </TabsTrigger>
          <TabsTrigger value="qr" className="gap-2">
            <QrCode className="w-4 h-4" />
            QR kód
          </TabsTrigger>
        </TabsList>

        <TabsContent value="labels" className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <div className="space-y-1">
                <CardTitle className="text-base">Címkék kezelése</CardTitle>
                <CardDescription>
                  {labelData.length} címke • {totalLabels} összesen (másolatokkal) • {pagesNeeded} oldal
                </CardDescription>
              </div>
              <Button onClick={handleAddLabel} size="sm" className="gap-1">
                <Plus className="w-4 h-4" />
                Hozzáad
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {labelData.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <QrCode className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>Nincsenek címkék</p>
                  <Button 
                    variant="outline" 
                    onClick={handleAddLabel}
                    className="mt-2 gap-2"
                  >
                    <Plus className="w-4 h-4" />
                    Első címke hozzáadása
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {labelData.map((label, index) => (
                    <div 
                      key={`${label.gateId}-${index}`}
                      className="grid grid-cols-1 md:grid-cols-4 gap-3 p-4 border border-gray-200 rounded-lg"
                    >
                      <div className="space-y-2">
                        <Label htmlFor={`gate-id-${index}`} className="text-xs">Kapu ID</Label>
                        <Input
                          id={`gate-id-${index}`}
                          value={label.gateId}
                          onChange={(e) => handleUpdateLabel(index, { gateId: e.target.value })}
                          className="text-sm"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor={`gate-name-${index}`} className="text-xs">Kapu név</Label>
                        <Input
                          id={`gate-name-${index}`}
                          value={label.gateName}
                          onChange={(e) => handleUpdateLabel(index, { gateName: e.target.value })}
                          className="text-sm"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor={`serial-${index}`} className="text-xs">Sorozatszám</Label>
                        <Input
                          id={`serial-${index}`}
                          value={label.serialNumber || ''}
                          onChange={(e) => handleUpdateLabel(index, { serialNumber: e.target.value })}
                          className="text-sm"
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor={`location-${index}`} className="text-xs">Helyszín</Label>
                        <Input
                          id={`location-${index}`}
                          value={label.location || ''}
                          onChange={(e) => handleUpdateLabel(index, { location: e.target.value })}
                          className="text-sm"
                        />
                      </div>
                      
                      <div className="md:col-span-3 space-y-2">
                        <Label htmlFor={`qr-content-${index}`} className="text-xs">QR kód URL</Label>
                        <Input
                          id={`qr-content-${index}`}
                          value={label.qrContent}
                          onChange={(e) => handleUpdateLabel(index, { qrContent: e.target.value })}
                          className="text-sm font-mono"
                        />
                      </div>
                      
                      <div className="flex items-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDuplicateLabel(index)}
                          className="gap-1"
                        >
                          <Copy className="w-3 h-3" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleRemoveLabel(index)}
                          className="gap-1 text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="format" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Címke formátum</CardTitle>
                <CardDescription>
                  Válaszd ki a címkék méretét és elrendezését
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Formátum</Label>
                  <Select 
                    value={selectedFormat} 
                    onValueChange={(value: LabelFormat) => setSelectedFormat(value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(LABEL_FORMATS).map(([key, config]) => (
                        <SelectItem key={key} value={key}>
                          <div>
                            <div className="font-medium">{config.name}</div>
                            <div className="text-xs text-gray-500">{config.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Másolatok száma</Label>
                    <Input
                      type="number"
                      min="1"
                      max="100"
                      value={copies}
                      onChange={(e) => setCopies(parseInt(e.target.value) || 1)}
                    />
                  </div>
                  
                  {formatConfig.grid && (
                    <div className="space-y-2">
                      <Label>Kezdő pozíció</Label>
                      <Input
                        type="number"
                        min="1"
                        max={labelsPerPage}
                        value={startPosition}
                        onChange={(e) => setStartPosition(parseInt(e.target.value) || 1)}
                      />
                      <p className="text-xs text-gray-500">
                        Részben használt lap esetén
                      </p>
                    </div>
                  )}
                </div>

                <div className="space-y-3 pt-2 border-t">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="include-grid">Vágási segédvonalak</Label>
                    <Switch
                      id="include-grid"
                      checked={includeGrid}
                      onChange={(e) => setIncludeGrid(e.target.checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <Label htmlFor="include-margins">Margók jelölése</Label>
                    <Switch
                      id="include-margins"
                      checked={includeMargins}
                      onChange={(e) => setIncludeMargins(e.target.checked)}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Formátum információk</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Címke méret:</span>
                    <span className="font-medium">
                      {formatConfig.dimensions.width}×{formatConfig.dimensions.height} mm
                    </span>
                  </div>
                  
                  {formatConfig.grid && (
                    <>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Rács:</span>
                        <span className="font-medium">
                          {formatConfig.grid.cols}×{formatConfig.grid.rows} 
                          ({labelsPerPage} db/oldal)
                        </span>
                      </div>
                      
                      <div className="flex justify-between">
                        <span className="text-gray-600">Kezdő sor:</span>
                        <span className="font-medium">
                          {startRow}. sor
                        </span>
                      </div>
                    </>
                  )}
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Összesen címke:</span>
                    <span className="font-medium">{totalLabels} db</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Oldalak száma:</span>
                    <span className="font-medium">{pagesNeeded} oldal</span>
                  </div>
                  
                  <div className="flex justify-between">
                    <span className="text-gray-600">Lap méret:</span>
                    <span className="font-medium">A4 (210×297 mm)</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="qr" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">QR kód beállítások</CardTitle>
              <CardDescription>
                A QR kód mérete automatikusan optimalizálva van a címke méretéhez
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>QR kód méret (px)</Label>
                  <Input
                    type="number"
                    min="20"
                    max="200"
                    value={qrConfig.size}
                    onChange={(e) => setQRConfig(prev => ({
                      ...prev,
                      size: parseInt(e.target.value) || 80
                    }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Hibajavítási szint</Label>
                  <Select
                    value={qrConfig.errorCorrectionLevel}
                    onValueChange={(value: 'L' | 'M' | 'Q' | 'H') => 
                      setQRConfig(prev => ({ ...prev, errorCorrectionLevel: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="L">Alacsony (7%)</SelectItem>
                      <SelectItem value="M">Közepes (15%)</SelectItem>
                      <SelectItem value="Q">Magas (25%)</SelectItem>
                      <SelectItem value="H">Nagyon magas (30%)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label>Szöveg méret (pt)</Label>
                  <Input
                    type="number"
                    min="6"
                    max="20"
                    value={qrConfig.textSize}
                    onChange={(e) => setQRConfig(prev => ({
                      ...prev,
                      textSize: parseInt(e.target.value) || 8
                    }))}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label>Szöveg pozíció</Label>
                  <Select
                    value={qrConfig.textPosition}
                    onValueChange={(value: 'below' | 'above' | 'none') =>
                      setQRConfig(prev => ({ ...prev, textPosition: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="below">Alul</SelectItem>
                      <SelectItem value="above">Felül</SelectItem>
                      <SelectItem value="none">Nincs szöveg</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="flex items-center justify-between pt-2 border-t">
                <Label htmlFor="include-text">Kapu név megjelenítése</Label>
                <Switch
                  id="include-text"
                  checked={qrConfig.includeText}
                  onChange={(e) => setQRConfig(prev => ({ 
                    ...prev, 
                    includeText: e.target.checked 
                  }))}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Preview Modal */}
      {isPreviewOpen && previewUrl && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl h-full max-h-[90vh] flex flex-col">
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">Címkelap előnézet</h3>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleOpenPrintView}
                  className="gap-2"
                >
                  <Layout className="w-4 h-4" />
                  Print View
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePrint}
                  className="gap-2"
                >
                  <Printer className="w-4 h-4" />
                  Nyomtatás
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsPreviewOpen(false)}
                >
                  Bezárás
                </Button>
              </div>
            </div>
            
            <div className="flex-1 p-4">
              <iframe
                ref={previewRef}
                src={previewUrl}
                className="w-full h-full border border-gray-200 rounded"
                title="Címkelap előnézet"
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}