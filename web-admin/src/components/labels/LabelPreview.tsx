'use client'

import { useState, useEffect, useCallback } from 'react'
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
  Maximize2
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

interface LabelPreviewProps {
  gates?: Array<{
    id: string
    name: string
    serialNumber?: string
    location?: string
  }>
  onPrint?: (printUrl: string) => void
}

export function LabelPreview({ gates = [], onPrint }: LabelPreviewProps) {
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
  const [copies, setCopies] = useState(1)
  const [includeGrid, setIncludeGrid] = useState(false)
  const [includeMargins, setIncludeMargins] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [previewUrl, setPreviewUrl] = useState<string>('')

  // Initialize label data from gates
  useEffect(() => {
    if (gates.length > 0 && labelData.length === 0) {
      const initialLabels: GateLabelData[] = gates.map(gate => ({
        gateId: gate.id,
        gateName: gate.name,
        serialNumber: gate.serialNumber,
        location: gate.location,
        qrContent: `${window.location.origin}/gates/${gate.id}`,
        additionalText: gate.location
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
        includeGrid,
        includeMargins
      }

      const result = await LabelService.generateLabels(printJob)
      
      if (result.success && result.printUrl) {
        setPreviewUrl(result.printUrl)
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
  }, [labelData, selectedFormat, qrConfig, copies, includeGrid, includeMargins])

  const handlePrint = useCallback(async () => {
    if (labelData.length === 0) {
      toast.error('Legalább egy címkét hozzá kell adni')
      return
    }

    const validation = LabelService.validateLabelData(labelData)
    if (!validation.valid) {
      toast.error(validation.errors[0])
      return
    }

    try {
      const printJob: PrintJob = {
        format: selectedFormat,
        qrConfig,
        labels: labelData,
        copies,
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
  }, [labelData, selectedFormat, qrConfig, copies, includeGrid, includeMargins, previewUrl, onPrint])

  const handlePreview = useCallback(() => {
    if (!previewUrl) {
      toast.error('Először generálj előnézetet')
      return
    }
    
    LabelService.openPrintPreview(previewUrl)
  }, [previewUrl])

  const formatConfig = LABEL_FORMATS[selectedFormat]
  const labelsPerPage = LabelService.getLabelsPerPage(selectedFormat)
  const totalLabels = labelData.length * copies
  const pagesNeeded = LabelService.calculatePages(totalLabels, selectedFormat)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center space-y-4 sm:space-y-0">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Címke generálás</h1>
          <p className="text-gray-600 mt-1">
            QR kódos címkék létrehozása nyomtatáshoz
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={generatePreview}
            disabled={isGenerating || labelData.length === 0}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                Generálás...
              </>
            ) : (
              <>
                <Eye className="h-4 w-4 mr-2" />
                Előnézet
              </>
            )}
          </button>
          
          <button
            onClick={handlePreview}
            disabled={!previewUrl}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
          >
            <Maximize2 className="h-4 w-4 mr-2" />
            Megnyitás
          </button>
          
          <button
            onClick={handlePrint}
            disabled={labelData.length === 0}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            <Printer className="h-4 w-4 mr-2" />
            Nyomtatás
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* Format Selection */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Grid3x3 className="h-5 w-5 mr-2" />
              Címke formátum
            </h3>
            
            <div className="space-y-3">
              {Object.entries(LABEL_FORMATS).map(([key, format]) => (
                <label key={key} className="flex items-start space-x-3 cursor-pointer">
                  <input
                    type="radio"
                    name="format"
                    value={key}
                    checked={selectedFormat === key}
                    onChange={(e) => setSelectedFormat(e.target.value as LabelFormat)}
                    className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                  />
                  <div className="flex-1">
                    <div className="text-sm font-medium text-gray-900">
                      {format.name}
                    </div>
                    <div className="text-xs text-gray-600">
                      {format.description}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {format.dimensions.width}×{format.dimensions.height}mm
                      {format.grid && ` • ${format.grid.cols}×${format.grid.rows} = ${format.grid.cols * format.grid.rows} db/oldal`}
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* QR Configuration */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <QrCode className="h-5 w-5 mr-2" />
              QR beállítások
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  QR kód méret
                </label>
                <input
                  type="range"
                  min="20"
                  max="200"
                  step="10"
                  value={qrConfig.size}
                  onChange={(e) => setQRConfig(prev => ({ ...prev, size: parseInt(e.target.value) }))}
                  className="w-full"
                />
                <div className="text-xs text-gray-500 text-center mt-1">
                  {qrConfig.size}px
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Hibajavítás szint
                </label>
                <select
                  value={qrConfig.errorCorrectionLevel}
                  onChange={(e) => setQRConfig(prev => ({ 
                    ...prev, 
                    errorCorrectionLevel: e.target.value as 'L' | 'M' | 'Q' | 'H' 
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                >
                  <option value="L">Alacsony (7%)</option>
                  <option value="M">Közepes (15%)</option>
                  <option value="Q">Jó (25%)</option>
                  <option value="H">Magas (30%)</option>
                </select>
              </div>
              
              <div className="flex items-center space-x-3">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={qrConfig.includeText}
                    onChange={(e) => setQRConfig(prev => ({ ...prev, includeText: e.target.checked }))}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Szöveg megjelenítése</span>
                </label>
              </div>
              
              {qrConfig.includeText && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Szöveg pozíció
                  </label>
                  <select
                    value={qrConfig.textPosition}
                    onChange={(e) => setQRConfig(prev => ({ 
                      ...prev, 
                      textPosition: e.target.value as 'below' | 'above' | 'none' 
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  >
                    <option value="below">QR kód alatt</option>
                    <option value="above">QR kód felett</option>
                    <option value="none">Nincs szöveg</option>
                  </select>
                </div>
              )}
            </div>
          </div>

          {/* Print Options */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              Nyomtatási beállítások
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Másolatok száma
                </label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  value={copies}
                  onChange={(e) => setCopies(parseInt(e.target.value) || 1)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>
              
              <div className="space-y-2">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeGrid}
                    onChange={(e) => setIncludeGrid(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Vágási segédvonalak</span>
                </label>
                
                <label className="flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={includeMargins}
                    onChange={(e) => setIncludeMargins(e.target.checked)}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Margó jelölések (debug)</span>
                </label>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-900 mb-2">Összesítés</h4>
            <div className="text-sm text-blue-700 space-y-1">
              <div>{labelData.length} egyedi címke</div>
              <div>{copies} másolat/címke</div>
              <div className="font-medium">{totalLabels} címke összesen</div>
              <div>{pagesNeeded} oldal szükséges</div>
              <div>{labelsPerPage} címke/oldal</div>
            </div>
          </div>
        </div>

        {/* Label Data Panel */}
        <div className="lg:col-span-2">
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Címke adatok ({labelData.length})
              </h3>
              
              <button
                onClick={handleAddLabel}
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-blue-700 bg-blue-100 border border-blue-200 rounded-md hover:bg-blue-200"
              >
                <Plus className="h-4 w-4 mr-2" />
                Címke hozzáadása
              </button>
            </div>
            
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {labelData.map((label, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="text-sm font-medium text-gray-900">
                      Címke #{index + 1}
                    </div>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleDuplicateLabel(index)}
                        className="p-1 text-gray-400 hover:text-blue-600 rounded"
                        title="Másolás"
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleRemoveLabel(index)}
                        className="p-1 text-gray-400 hover:text-red-600 rounded"
                        title="Törlés"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Kapu név *
                      </label>
                      <input
                        type="text"
                        value={label.gateName}
                        onChange={(e) => handleUpdateLabel(index, { gateName: e.target.value })}
                        className="w-full px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Kapu neve"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Sorozatszám
                      </label>
                      <input
                        type="text"
                        value={label.serialNumber || ''}
                        onChange={(e) => handleUpdateLabel(index, { serialNumber: e.target.value })}
                        className="w-full px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="SN-123456"
                      />
                    </div>
                    
                    <div className="sm:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        QR kód tartalom *
                      </label>
                      <input
                        type="text"
                        value={label.qrContent}
                        onChange={(e) => handleUpdateLabel(index, { qrContent: e.target.value })}
                        className="w-full px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="https://app.garagereg.hu/gates/123"
                      />
                    </div>
                    
                    <div className="sm:col-span-2">
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        További szöveg
                      </label>
                      <input
                        type="text"
                        value={label.additionalText || ''}
                        onChange={(e) => handleUpdateLabel(index, { additionalText: e.target.value })}
                        className="w-full px-3 py-1.5 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Helyszín vagy egyéb info"
                      />
                    </div>
                  </div>
                </div>
              ))}
              
              {labelData.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <QrCode className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                  <p>Nincsenek címkék megadva</p>
                  <p className="text-sm mt-1">Kattints a "Címke hozzáadása" gombra</p>
                </div>
              )}
            </div>
          </div>
          
          {/* Preview iframe */}
          {previewUrl && (
            <div className="mt-6 bg-white border border-gray-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Előnézet</h3>
              <div className="border border-gray-300 rounded-lg overflow-hidden">
                <iframe
                  src={previewUrl}
                  className="w-full h-96 border-none"
                  title="Címke előnézet"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}