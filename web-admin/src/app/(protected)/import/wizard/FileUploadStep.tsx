'use client'

import { useState, useCallback, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Upload, 
  FileText, 
  Download, 
  AlertCircle, 
  CheckCircle,
  X 
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { toast } from '@/components/ui/use-toast'
import { ImportType } from './types'

interface FileUploadStepProps {
  onNext: (importType: ImportType, data: any[]) => void
}

const importTypeConfig = {
  gates: {
    label: 'Kapuk',
    description: 'Kapuk tömeges importálása CSV vagy Excel fájlból',
    templateFields: [
      'name', 'type', 'siteId', 'manufacturer', 'model', 'serialNumber',
      'width', 'height', 'weight', 'motorType', 'motorPower', 'status'
    ]
  },
  sites: {
    label: 'Telephelyek',
    description: 'Telephelyek importálása címekkel és kapcsolattartókkal',
    templateFields: [
      'name', 'address', 'city', 'postalCode', 'country',
      'contactName', 'contactEmail', 'contactPhone', 'status'
    ]
  },
  users: {
    label: 'Felhasználók',
    description: 'Felhasználók és jogosultságaik importálása',
    templateFields: [
      'firstName', 'lastName', 'email', 'role', 'permissions',
      'phone', 'department', 'status'
    ]
  },
  inspections: {
    label: 'Felülvizsgálatok',
    description: 'Tervezett vagy befejezett felülvizsgálatok importálása',
    templateFields: [
      'gateId', 'inspectorName', 'scheduledDate', 'completedDate',
      'status', 'findings', 'recommendations', 'nextInspectionDate'
    ]
  }
}

export function FileUploadStep({ 
  onNext 
}: FileUploadStepProps) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [importType, setImportType] = useState<ImportType>('gates')
  const [parsedData, setParsedData] = useState<any[] | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }, [])

  const handleFileSelect = async (file: File) => {
    if (!file) return

    const validTypes = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ]

    if (!validTypes.includes(file.type) && !file.name.match(/\.(csv|xlsx?)$/i)) {
      toast({
        title: "Érvénytelen fájltípus",
        description: "Csak CSV és Excel fájlok támogatottak (.csv, .xls, .xlsx)",
        variant: "destructive",
      })
      return
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast({
        title: "Fájl túl nagy",
        description: "A fájl mérete nem lehet nagyobb 10MB-nál",
        variant: "destructive",
      })
      return
    }

    setSelectedFile(file)
    setIsProcessing(true)

    try {
      const data = await parseFile(file)
      setParsedData(data)
      toast({
        title: "Fájl sikeresen betöltve",
        description: `${data.length} sor feldolgozva`,
      })
    } catch (error) {
      toast({
        title: "Hiba a fájl feldolgozásában",
        description: error instanceof Error ? error.message : "Ismeretlen hiba",
        variant: "destructive",
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const parseFile = async (file: File): Promise<any[]> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        try {
          const text = e.target?.result as string
          
          if (file.name.endsWith('.csv')) {
            const lines = text.split('\n').filter(line => line.trim())
            if (lines.length === 0) {
              reject(new Error('A CSV fájl üres'))
              return
            }

            const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''))
            const data = lines.slice(1).map((line, index) => {
              const values = line.split(',').map(v => v.trim().replace(/"/g, ''))
              const row: any = { _rowIndex: index + 2 } // +2 because header is row 1
              
              headers.forEach((header, i) => {
                row[header] = values[i] || ''
              })
              
              return row
            })

            resolve(data)
          } else {
            // For Excel files, we'd need a library like xlsx
            // For now, simulate parsing
            reject(new Error('Excel fájlok feldolgozása még nem támogatott ebben a verzióban'))
          }
        } catch (error) {
          reject(new Error('Hiba a fájl tartalmának feldolgozásában'))
        }
      }
      
      reader.onerror = () => {
        reject(new Error('Hiba a fájl olvasásában'))
      }
      
      reader.readAsText(file)
    })
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const downloadTemplate = () => {
    const config = importTypeConfig[importType]
    const csvContent = config.templateFields.join(',') + '\n' +
      config.templateFields.map(() => '').join(',') // Empty row as example
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${importType}_template.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    toast({
      title: "Sablon letöltve",
      description: `A ${config.label} import sablon letöltése elkezdődött`,
    })
  }

  const removeFile = () => {
    setSelectedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const config = importTypeConfig[importType]

  return (
    <div className="space-y-6">
      {/* Import Type Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Import típusa</CardTitle>
          <CardDescription>
            Válassza ki, hogy milyen típusú adatokat szeretne importálni
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="import-type">Adattípus</Label>
            <Select value={importType} onValueChange={(value: ImportType) => setImportType(value)}>
              <SelectTrigger id="import-type">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(importTypeConfig).map(([key, config]) => (
                  <SelectItem key={key} value={key}>
                    {config.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-sm text-muted-foreground">
              {config.description}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Template Download */}
      <Card>
        <CardHeader>
          <CardTitle>Sablon letöltése</CardTitle>
          <CardDescription>
            Töltse le a megfelelő CSV sablont a helyes formátumhoz
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="font-medium">
                {config.label} import sablon
              </p>
              <div className="flex flex-wrap gap-1">
                {config.templateFields.slice(0, 6).map(field => (
                  <Badge key={field} variant="outline" className="text-xs">
                    {field}
                  </Badge>
                ))}
                {config.templateFields.length > 6 && (
                  <Badge variant="outline" className="text-xs">
                    +{config.templateFields.length - 6} további
                  </Badge>
                )}
              </div>
            </div>
            <Button variant="outline" onClick={downloadTemplate}>
              <Download className="mr-2 h-4 w-4" />
              Letöltés
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* File Upload */}
      <Card>
        <CardHeader>
          <CardTitle>Fájl feltöltése</CardTitle>
          <CardDescription>
            Húzza ide a fájlt, vagy kattintson a tallózáshoz
          </CardDescription>
        </CardHeader>
        <CardContent>
          {selectedFile ? (
            <div className="space-y-4">
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Fájl sikeresen betöltve és feldolgozva
                </AlertDescription>
              </Alert>

              <div className="flex items-center justify-between p-3 border rounded-lg bg-muted/50">
                <div className="flex items-center space-x-3">
                  <FileText className="h-8 w-8 text-blue-500" />
                  <div>
                    <p className="font-medium">{selectedFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={removeFile}
                  className="text-muted-foreground hover:text-destructive"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ) : (
            <div
              className={cn(
                "relative border-2 border-dashed rounded-lg p-8 text-center transition-colors",
                dragActive 
                  ? "border-primary bg-primary/5" 
                  : "border-muted-foreground/25 hover:border-muted-foreground/50"
              )}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.xls,.xlsx"
                onChange={handleInputChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={isProcessing}
              />
              
              <div className="space-y-4">
                <div className="mx-auto w-12 h-12 bg-muted rounded-full flex items-center justify-center">
                  <Upload className="h-6 w-6 text-muted-foreground" />
                </div>
                
                {isProcessing ? (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Fájl feldolgozása...</p>
                    <div className="w-16 h-1 bg-muted rounded mx-auto">
                      <div className="h-full bg-primary rounded animate-pulse"></div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">
                      Húzza ide a fájlt, vagy kattintson a tallózáshoz
                    </p>
                    <p className="text-xs text-muted-foreground">
                      CSV, Excel (.xls, .xlsx) - maximum 10MB
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {!selectedFile && (
            <div className="mt-4 space-y-2">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  <strong>Fontos:</strong> A fájlnak tartalmaznia kell a fejlécsort a 
                  mezőnevek megadásával. Használja az előre elkészített sablont 
                  a legjobb eredmény érdekében.
                </AlertDescription>
              </Alert>
            </div>
          )}

          {selectedFile && parsedData && (
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-muted-foreground">
                Fájl készen áll a mezőhozzárendeléshez
              </div>
              <Button 
                onClick={() => onNext(importType, parsedData)}
                className="ml-auto"
              >
                Következő: Mezők hozzárendelése
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}