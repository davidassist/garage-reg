'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  CheckCircle, 
  AlertTriangle, 
  X,
  RefreshCw,
  Download,
  ExternalLink,
  Home
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ImportType, ProcessedRow } from './types'
import { useRouter } from 'next/navigation'
import { toast } from '@/components/ui/use-toast'

// ProcessedRow imported from types

interface ImportResult {
  success: boolean
  imported: number
  failed: number
  errors: ImportError[]
  warnings: ImportWarning[]
}

interface ImportError {
  row: number
  message: string
  field?: string
}

interface ImportWarning {
  row: number
  message: string
  field?: string
}

interface ImportStepProps {
  importType: ImportType
  processedData: ProcessedRow[]
  onComplete: () => void
  onBack: () => void
}

export function ImportStep({ 
  importType, 
  processedData, 
  onComplete, 
  onBack 
}: ImportStepProps) {
  const router = useRouter()
  const [isImporting, setIsImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importResult, setImportResult] = useState<ImportResult | null>(null)
  const [importComplete, setImportComplete] = useState(false)

  const validRows = processedData.filter(row => row.validation.isValid)

  const startImport = async () => {
    setIsImporting(true)
    setImportProgress(0)

    try {
      const result = await performImport(validRows)
      setImportResult(result)
      setImportComplete(true)

      if (result.success) {
        toast({
          title: "Import sikeres",
          description: `${result.imported} elem sikeresen importálva`,
        })
      } else {
        toast({
          title: "Import részben sikeres",
          description: `${result.imported} elem importálva, ${result.failed} elem sikertelen`,
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Import hiba",
        description: error instanceof Error ? error.message : "Ismeretlen hiba történt",
        variant: "destructive",
      })
      setImportResult({
        success: false,
        imported: 0,
        failed: validRows.length,
        errors: [{
          row: 0,
          message: error instanceof Error ? error.message : "Ismeretlen hiba történt"
        }],
        warnings: []
      })
      setImportComplete(true)
    } finally {
      setIsImporting(false)
    }
  }

  const performImport = async (rows: ProcessedRow[]): Promise<ImportResult> => {
    const batchSize = 10
    let imported = 0
    let failed = 0
    const errors: ImportError[] = []
    const warnings: ImportWarning[] = []

    for (let i = 0; i < rows.length; i += batchSize) {
      const batch = rows.slice(i, i + batchSize)
      
      try {
        // Simulate API call for each batch
        const batchResults = await Promise.allSettled(
          batch.map(row => importSingleRow(row, importType))
        )

        batchResults.forEach((result, index) => {
          const rowIndex = i + index
          const row = batch[index]

          if (result.status === 'fulfilled') {
            if (result.value.success) {
              imported++
              if (result.value.warnings) {
                warnings.push(...result.value.warnings.map(w => ({
                  ...w,
                  row: row.rowIndex
                })))
              }
            } else {
              failed++
              errors.push({
                row: row.rowIndex,
                message: result.value.error || 'Ismeretlen hiba'
              })
            }
          } else {
            failed++
            errors.push({
              row: row.rowIndex,
              message: result.reason?.message || 'Hálózati hiba'
            })
          }
        })

        setImportProgress(((i + batch.length) / rows.length) * 100)
        
        // Small delay to show progress
        await new Promise(resolve => setTimeout(resolve, 100))

      } catch (error) {
        // Handle batch-level errors
        batch.forEach(row => {
          failed++
          errors.push({
            row: row.rowIndex,
            message: error instanceof Error ? error.message : 'Batch import hiba'
          })
        })
      }
    }

    return {
      success: failed === 0,
      imported,
      failed,
      errors,
      warnings
    }
  }

  const importSingleRow = async (
    row: ProcessedRow, 
    type: ImportType
  ): Promise<{
    success: boolean
    error?: string
    warnings?: ImportWarning[]
  }> => {
    // Simulate API call - replace with actual API integration
    await new Promise(resolve => setTimeout(resolve, 50 + Math.random() * 100))

    // Simulate random failures for demo
    if (Math.random() < 0.05) { // 5% failure rate
      throw new Error('Szimuláltszerverhiba')
    }

    // Simulate business logic validation failures
    if (Math.random() < 0.03) { // 3% business rule failures
      return {
        success: false,
        error: 'Üzleti szabály megszegése: duplikált azonosító'
      }
    }

    // Simulate warnings
    const warnings: ImportWarning[] = []
    if (Math.random() < 0.1) { // 10% chance of warnings
      warnings.push({
        row: row.rowIndex,
        message: 'Hasonló bejegyzés már létezik',
        field: 'name'
      })
    }

    return {
      success: true,
      warnings: warnings.length > 0 ? warnings : undefined
    }
  }

  const exportImportResult = () => {
    if (!importResult) return

    const csvContent = [
      'Sor,Állapot,Üzenet,Mező',
      ...importResult.errors.map(error => 
        `${error.row},Hiba,"${error.message}",${error.field || ''}`
      ),
      ...importResult.warnings.map(warning => 
        `${warning.row},Figyelmeztetés,"${warning.message}",${warning.field || ''}`
      )
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `import_result_${importType}_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  const navigateToList = () => {
    let path = ''
    switch (importType) {
      case 'gates':
        path = '/gates'
        break
      case 'sites':
        path = '/sites'
        break
      case 'users':
        path = '/users'
        break
      case 'inspections':
        path = '/inspections'
        break
      default:
        path = '/dashboard'
    }
    router.push(path)
  }

  const startNewImport = () => {
    window.location.reload()
  }

  return (
    <div className="space-y-6">
      {/* Import Configuration Summary */}
      <Card>
        <CardHeader>
          <CardTitle>Import végrehajtása</CardTitle>
          <CardDescription>
            {validRows.length} érvényes sor importálása ({importType})
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <p className="font-medium">
                {validRows.length} sor lesz importálva
              </p>
              <p className="text-sm text-muted-foreground">
                {processedData.length - validRows.length} hibás sor kihagyva
              </p>
            </div>
            
            {!isImporting && !importComplete && (
              <Button onClick={startImport} size="lg">
                Import indítása
                <RefreshCw className="ml-2 h-4 w-4" />
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Import Progress */}
      {isImporting && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
              Import folyamatban...
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={importProgress} className="w-full" />
            <div className="flex items-center justify-between mt-2">
              <p className="text-sm text-muted-foreground">
                {Math.round(importProgress)}% kész
              </p>
              <p className="text-sm text-muted-foreground">
                {Math.round((importProgress / 100) * validRows.length)} / {validRows.length} sor
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Import Results */}
      {importComplete && importResult && (
        <>
          {/* Summary Alert */}
          {importResult.success ? (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  <p><strong>Import sikeresen befejezve!</strong></p>
                  <p>{importResult.imported} elem importálva.</p>
                  {importResult.warnings.length > 0 && (
                    <p className="text-orange-600">
                      {importResult.warnings.length} figyelmeztetés keletkezett.
                    </p>
                  )}
                </div>
              </AlertDescription>
            </Alert>
          ) : (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-1">
                  <p><strong>Import részben sikeres</strong></p>
                  <p>
                    {importResult.imported} elem sikeresen importálva, 
                    {importResult.failed} elem sikertelen.
                  </p>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {/* Detailed Results */}
          <Card>
            <CardHeader>
              <CardTitle>Import eredmények</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">
                    {importResult.imported}
                  </div>
                  <div className="text-sm text-muted-foreground">Sikeresen importált</div>
                </div>
                
                {importResult.failed > 0 && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-destructive">
                      {importResult.failed}
                    </div>
                    <div className="text-sm text-muted-foreground">Sikertelen</div>
                  </div>
                )}
                
                {importResult.warnings.length > 0 && (
                  <div className="text-center">
                    <div className="text-3xl font-bold text-orange-600">
                      {importResult.warnings.length}
                    </div>
                    <div className="text-sm text-muted-foreground">Figyelmeztetés</div>
                  </div>
                )}
                
                <div className="text-center">
                  <div className="text-3xl font-bold">
                    {importResult.imported + importResult.failed}
                  </div>
                  <div className="text-sm text-muted-foreground">Feldolgozott</div>
                </div>
              </div>

              {/* Error and Warning Details */}
              {(importResult.errors.length > 0 || importResult.warnings.length > 0) && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">Részletes eredmények</h4>
                    <Button variant="outline" size="sm" onClick={exportImportResult}>
                      <Download className="mr-2 h-4 w-4" />
                      Eredmények exportálása
                    </Button>
                  </div>

                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {importResult.errors.map((error, index) => (
                      <div key={`error-${index}`} className="flex items-start space-x-2 p-2 bg-destructive/10 rounded">
                        <X className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
                        <div className="flex-1 text-sm">
                          <span className="font-medium">Sor {error.row}:</span> {error.message}
                          {error.field && (
                            <Badge variant="outline" className="ml-2 text-xs">
                              {error.field}
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    {importResult.warnings.map((warning, index) => (
                      <div key={`warning-${index}`} className="flex items-start space-x-2 p-2 bg-orange-50 rounded">
                        <AlertTriangle className="h-4 w-4 text-orange-600 mt-0.5 flex-shrink-0" />
                        <div className="flex-1 text-sm">
                          <span className="font-medium">Sor {warning.row}:</span> {warning.message}
                          {warning.field && (
                            <Badge variant="outline" className="ml-2 text-xs">
                              {warning.field}
                            </Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Navigation Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Következő lépések</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Button onClick={navigateToList} className="flex-1 md:flex-none">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Importált elemek megtekintése
                </Button>
                
                <Button variant="outline" onClick={startNewImport} className="flex-1 md:flex-none">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Új import indítása
                </Button>
                
                <Button variant="outline" onClick={() => router.push('/dashboard')} className="flex-1 md:flex-none">
                  <Home className="mr-2 h-4 w-4" />
                  Vissza a dashboardra
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}

      {/* Back Navigation */}
      {!isImporting && !importComplete && (
        <div className="flex items-center justify-between">
          <Button variant="outline" onClick={onBack}>
            Vissza a validációhoz
          </Button>
          
          <div className="text-sm text-muted-foreground">
            Készen áll az import indítására
          </div>
        </div>
      )}
    </div>
  )
}