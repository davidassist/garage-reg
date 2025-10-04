'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { toast } from 'react-hot-toast'
import { 
  ImportSession, 
  ImportEntityType, 
  CsvConfig,
  ImportEntityLabels,
  CsvDelimiterOptions,
  EncodingOptions
} from '@/lib/types/import'
import { FileParser, getFileType, formatFileSize } from '@/lib/import/utils'
import { ExportUtils } from '@/lib/import/utils'
import { getTemplate } from '@/lib/import/templates'
import { 
  Upload, 
  File, 
  FileText, 
  AlertCircle, 
  Download, 
  Settings, 
  Check, 
  X 
} from 'lucide-react'

interface FileUploadStepProps {
  entityType: ImportEntityType
  session?: ImportSession
  onComplete: (session: ImportSession) => void
  isLoading: boolean
  setIsLoading: (loading: boolean) => void
}

export function FileUploadStep({ 
  entityType, 
  session, 
  onComplete, 
  isLoading, 
  setIsLoading 
}: FileUploadStepProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [csvConfig, setCsvConfig] = useState<CsvConfig>({
    delimiter: ',',
    skipEmptyLines: true,
    header: true,
    encoding: 'utf-8',
  })
  const [showCsvConfig, setShowCsvConfig] = useState(false)
  const [parsedData, setParsedData] = useState<{ headers: string[]; data: any[] } | null>(null)

  const template = getTemplate(entityType)

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    const fileType = getFileType(file.name)
    if (!fileType) {
      toast.error('Nem támogatott fájltípus. Csak CSV és Excel fájlokat fogadunk el.')
      return
    }

    setUploadedFile(file)
    setParsedData(null)

    // Show CSV config for CSV files
    if (fileType === 'csv') {
      setShowCsvConfig(true)
    } else {
      // Auto-parse Excel files
      await parseFile(file, fileType)
    }
  }, [])

  const parseFile = async (file: File, fileType: 'csv' | 'xlsx', config?: CsvConfig) => {
    setIsLoading(true)
    try {
      const result = await FileParser.parseFile(
        file,
        fileType,
        fileType === 'csv' ? (config || csvConfig) : undefined
      )

      if (result.errors.length > 0) {
        toast.error(`Fájl beolvasási hibák: ${result.errors.length} db`)
        console.warn('Parse errors:', result.errors)
      }

      setParsedData(result)
      setShowCsvConfig(false)
      toast.success(`Fájl sikeresen beolvasva: ${result.data.length} sor`)
    } catch (error) {
      toast.error(`Fájl beolvasási hiba: ${error}`)
      console.error('File parsing error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCsvConfigApply = () => {
    if (!uploadedFile) return
    parseFile(uploadedFile, 'csv', csvConfig)
  }

  const handleContinue = () => {
    if (!uploadedFile || !parsedData) return

    const newSession: ImportSession = {
      id: Math.random().toString(36).substr(2, 9),
      entityType,
      fileName: uploadedFile.name,
      fileType: getFileType(uploadedFile.name)!,
      fileSize: uploadedFile.size,
      totalRows: parsedData.data.length,
      currentStep: 'mapping',
      csvConfig: getFileType(uploadedFile.name) === 'csv' ? csvConfig : undefined,
      columnMappings: [],
      validatedRows: [],
      validRowsCount: 0,
      invalidRowsCount: 0,
      warningsCount: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    // Store parsed data temporarily (in real app, this would go to session storage or API)
    sessionStorage.setItem(`import-data-${newSession.id}`, JSON.stringify(parsedData))

    onComplete(newSession)
  }

  const downloadSampleFile = (format: 'csv' | 'xlsx') => {
    try {
      if (format === 'csv') {
        const csv = ExportUtils.generateSampleCsv(entityType)
        ExportUtils.downloadFile(csv, `${entityType}_minta.csv`, 'text/csv')
      } else {
        const xlsx = ExportUtils.generateSampleXlsx(entityType)
        ExportUtils.downloadFile(xlsx, `${entityType}_minta.xlsx`, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      }
      toast.success('Minta fájl letöltve')
    } catch (error) {
      toast.error('Hiba a minta fájl generálása során')
      console.error('Sample file generation error:', error)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls'],
    },
    maxFiles: 1,
    disabled: isLoading,
  })

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-semibold text-gray-900">
          {ImportEntityLabels[entityType]} importálása
        </h2>
        <p className="mt-2 text-gray-600">
          Töltse fel a CSV vagy Excel fájlt a(z) {ImportEntityLabels[entityType].toLowerCase()} importálásához
        </p>
      </div>

      {/* Sample Files Section */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Download className="h-5 w-5 text-blue-600 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-sm font-medium text-blue-900">
              Minta fájlok letöltése
            </h3>
            <p className="mt-1 text-sm text-blue-700">
              Töltse le a megfelelő formátumú minta fájlt a helyes struktúra megtekintéséhez
            </p>
            <div className="mt-3 flex space-x-3">
              <button
                onClick={() => downloadSampleFile('csv')}
                disabled={isLoading}
                className="inline-flex items-center px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md disabled:opacity-50"
              >
                <FileText className="h-4 w-4 mr-1" />
                CSV minta
              </button>
              <button
                onClick={() => downloadSampleFile('xlsx')}
                disabled={isLoading}
                className="inline-flex items-center px-3 py-1 text-sm font-medium text-blue-700 bg-blue-100 hover:bg-blue-200 rounded-md disabled:opacity-50"
              >
                <File className="h-4 w-4 mr-1" />
                Excel minta
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* File Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50' 
            : uploadedFile 
              ? 'border-green-300 bg-green-50' 
              : 'border-gray-300 bg-gray-50 hover:border-gray-400'
          }
          ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        {uploadedFile ? (
          <div className="space-y-2">
            <div className="flex items-center justify-center space-x-2">
              <Check className="h-8 w-8 text-green-500" />
              <File className="h-8 w-8 text-gray-600" />
            </div>
            <p className="text-lg font-medium text-gray-900">{uploadedFile.name}</p>
            <p className="text-sm text-gray-600">
              {formatFileSize(uploadedFile.size)} • {getFileType(uploadedFile.name)?.toUpperCase()}
            </p>
            {parsedData && (
              <p className="text-sm text-green-600">
                ✓ Sikeresen beolvasva: {parsedData.data.length} sor, {parsedData.headers.length} oszlop
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <Upload className="h-12 w-12 text-gray-400 mx-auto" />
            <div>
              <p className="text-lg font-medium text-gray-900">
                {isDragActive ? 'Engedje el a fájlt ide' : 'Húzza ide a fájlt vagy kattintson a tallózáshoz'}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                CSV és Excel fájlokat fogadunk el (max. 10MB)
              </p>
            </div>
          </div>
        )}
      </div>

      {/* CSV Configuration */}
      {showCsvConfig && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Settings className="h-5 w-5 text-gray-600" />
              <h3 className="text-lg font-medium text-gray-900">CSV beállítások</h3>
            </div>
            <button
              onClick={() => setShowCsvConfig(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="delimiter" className="block text-sm font-medium text-gray-700 mb-1">
                Elválasztó karakter
              </label>
              <select
                id="delimiter"
                value={csvConfig.delimiter}
                onChange={(e) => setCsvConfig(prev => ({ ...prev, delimiter: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {CsvDelimiterOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="encoding" className="block text-sm font-medium text-gray-700 mb-1">
                Karakterkódolás
              </label>
              <select
                id="encoding"
                value={csvConfig.encoding}
                onChange={(e) => setCsvConfig(prev => ({ ...prev, encoding: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {EncodingOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="space-y-2 mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={csvConfig.header}
                onChange={(e) => setCsvConfig(prev => ({ ...prev, header: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Első sor fejléc</span>
            </label>
            
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={csvConfig.skipEmptyLines}
                onChange={(e) => setCsvConfig(prev => ({ ...prev, skipEmptyLines: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Üres sorok kihagyása</span>
            </label>
          </div>

          <div className="flex justify-end space-x-3">
            <button
              onClick={() => setShowCsvConfig(false)}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
            >
              Mégse
            </button>
            <button
              onClick={handleCsvConfigApply}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              Alkalmaz
            </button>
          </div>
        </div>
      )}

      {/* Required Fields Info */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-yellow-900">
              Kötelező mezők
            </h3>
            <p className="mt-1 text-sm text-yellow-700">
              A következő mezők kötelezőek minden sorban:
            </p>
            <div className="mt-2 flex flex-wrap gap-2">
              {template.fields
                .filter(field => field.required)
                .map(field => (
                  <span
                    key={field.key}
                    className="inline-flex items-center px-2 py-1 text-xs font-medium bg-yellow-100 text-yellow-800 rounded"
                  >
                    {field.name}
                  </span>
                ))
              }
            </div>
          </div>
        </div>
      </div>

      {/* Continue Button */}
      {parsedData && (
        <div className="flex justify-end">
          <button
            onClick={handleContinue}
            disabled={isLoading}
            className="inline-flex items-center px-6 py-3 text-base font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Folytatás: Mezők hozzárendelése
          </button>
        </div>
      )}
    </div>
  )
}