'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight, 
  X,
  Download,
  RefreshCw,
  Info
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { ImportType, FieldMapping, ProcessedRow, ValidationResult, ValidationError, ValidationWarning } from './types'

interface ValidationStepProps {
  importType: ImportType
  uploadedData: any[]
  fieldMappings: FieldMapping[]
  onNext: (processedData: ProcessedRow[]) => void
  onBack: () => void
}

export function ValidationStep({ 
  importType, 
  uploadedData, 
  fieldMappings, 
  onNext, 
  onBack 
}: ValidationStepProps) {
  const [processedRows, setProcessedRows] = useState<ProcessedRow[]>([])
  const [isValidating, setIsValidating] = useState(false)
  const [validationProgress, setValidationProgress] = useState(0)
  const [validationComplete, setValidationComplete] = useState(false)
  const [showErrorsOnly, setShowErrorsOnly] = useState(false)

  useEffect(() => {
    validateData()
  }, [uploadedData, fieldMappings])

  const validateData = async () => {
    setIsValidating(true)
    setValidationProgress(0)

    const processed: ProcessedRow[] = []
    const batchSize = 50 // Process in batches to avoid blocking UI

    for (let i = 0; i < uploadedData.length; i += batchSize) {
      const batch = uploadedData.slice(i, i + batchSize)
      
      for (const row of batch) {
        const processedRow = await validateRow(row, row._rowIndex || i + 1)
        processed.push(processedRow)
        
        setValidationProgress(((i + processed.length) / uploadedData.length) * 100)
      }

      // Small delay to allow UI updates
      await new Promise(resolve => setTimeout(resolve, 10))
    }

    setProcessedRows(processed)
    setValidationComplete(true)
    setIsValidating(false)
  }

  const validateRow = async (row: any, rowIndex: number): Promise<ProcessedRow> => {
    const processedData: any = {}
    const errors: ValidationError[] = []
    const warnings: ValidationWarning[] = []

    for (const mapping of fieldMappings) {
      if (!mapping.targetField || !mapping.csvField) continue

      const rawValue = row[mapping.csvField]
      const fieldName = mapping.targetField

      try {
        // Process and validate the value
        const { processedValue, error, warning } = await validateField(
          rawValue, 
          mapping, 
          rowIndex
        )

        processedData[fieldName] = processedValue

        if (error) errors.push(error)
        if (warning) warnings.push(warning)

      } catch (err) {
        errors.push({
          row: rowIndex,
          field: fieldName,
          message: 'Váratlan hiba a feldolgozás során',
          value: rawValue
        })
      }
    }

    return {
      rowIndex,
      originalData: row,
      processedData,
      validation: {
        isValid: errors.length === 0,
        errors,
        warnings
      }
    }
  }

  const validateField = async (
    value: any, 
    mapping: FieldMapping, 
    rowIndex: number
  ): Promise<{
    processedValue: any,
    error?: ValidationError,
    warning?: ValidationWarning
  }> => {
    const fieldName = mapping.targetField!

    // Handle empty values
    if (!value || value === '') {
      if (mapping.isRequired) {
        return {
          processedValue: null,
          error: {
            row: rowIndex,
            field: fieldName,
            message: 'A kötelező mező nem lehet üres',
            value
          }
        }
      }
      return { processedValue: null }
    }

    // Convert and validate based on data type
    switch (mapping.dataType) {
      case 'string':
        const stringValue = String(value).trim()
        if (stringValue.length > 255) {
          return {
            processedValue: stringValue.substring(0, 255),
            warning: {
              row: rowIndex,
              field: fieldName,
              message: 'A szöveg túl hosszú, levágva 255 karakterre',
              value
            }
          }
        }
        return { processedValue: stringValue }

      case 'number':
        const numValue = parseFloat(String(value).replace(',', '.'))
        if (isNaN(numValue)) {
          return {
            processedValue: null,
            error: {
              row: rowIndex,
              field: fieldName,
              message: 'Érvénytelen szám formátum',
              value
            }
          }
        }
        return { processedValue: numValue }

      case 'email':
        const emailValue = String(value).trim().toLowerCase()
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(emailValue)) {
          return {
            processedValue: emailValue,
            error: {
              row: rowIndex,
              field: fieldName,
              message: 'Érvénytelen email formátum',
              value
            }
          }
        }
        return { processedValue: emailValue }

      case 'phone':
        const phoneValue = String(value).replace(/\s/g, '')
        const phoneRegex = /^[+]?[\d\s\-\(\)]{7,15}$/
        if (!phoneRegex.test(phoneValue)) {
          return {
            processedValue: phoneValue,
            warning: {
              row: rowIndex,
              field: fieldName,
              message: 'Esetleg érvénytelen telefonszám formátum',
              value
            }
          }
        }
        return { processedValue: phoneValue }

      case 'date':
        const dateValue = String(value).trim()
        const date = new Date(dateValue)
        if (isNaN(date.getTime())) {
          return {
            processedValue: null,
            error: {
              row: rowIndex,
              field: fieldName,
              message: 'Érvénytelen dátum formátum (használjon YYYY-MM-DD formátumot)',
              value
            }
          }
        }
        return { processedValue: date.toISOString() }

      case 'enum':
        const enumValue = String(value).toLowerCase().trim()
        const validValues = mapping.enumValues || []
        const matchingValue = validValues.find(v => v.toLowerCase() === enumValue)
        
        if (!matchingValue) {
          return {
            processedValue: null,
            error: {
              row: rowIndex,
              field: fieldName,
              message: `Érvénytelen érték. Elfogadott értékek: ${validValues.join(', ')}`,
              value
            }
          }
        }
        return { processedValue: matchingValue }

      default:
        return { processedValue: value }
    }
  }

  const getValidationSummary = () => {
    const validRows = processedRows.filter(row => row.validation.isValid)
    const errorRows = processedRows.filter(row => !row.validation.isValid)
    const warningRows = processedRows.filter(row => 
      row.validation.isValid && row.validation.warnings.length > 0
    )

    const totalErrors = processedRows.reduce((acc, row) => 
      acc + row.validation.errors.length, 0
    )
    const totalWarnings = processedRows.reduce((acc, row) => 
      acc + row.validation.warnings.length, 0
    )

    return {
      totalRows: processedRows.length,
      validRows: validRows.length,
      errorRows: errorRows.length,
      warningRows: warningRows.length,
      totalErrors,
      totalWarnings
    }
  }

  const exportErrors = () => {
    const errorRows = processedRows.filter(row => !row.validation.isValid)
    
    if (errorRows.length === 0) {
      return
    }

    // Create CSV content with original data + error messages
    const csvFields = Object.keys(errorRows[0].originalData).filter(key => key !== '_rowIndex')
    const headers = [...csvFields, 'HIBA_ÜZENETEK']
    
    const csvContent = [
      headers.join(','),
      ...errorRows.map(row => {
        const values = csvFields.map(field => 
          `"${(row.originalData[field] || '').toString().replace(/"/g, '""')}"`
        )
        const errorMessages = row.validation.errors.map(e => 
          `${e.field}: ${e.message}`
        ).join('; ')
        
        return [...values, `"${errorMessages}"`].join(',')
      })
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `import_errors_${importType}_${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  const handleContinue = () => {
    onNext(processedRows)
  }

  const summary = getValidationSummary()
  const displayRows = showErrorsOnly 
    ? processedRows.filter(row => !row.validation.isValid)
    : processedRows

  return (
    <div className="space-y-6">
      {/* Validation Progress */}
      {isValidating && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
              Adatok validálása folyamatban...
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={validationProgress} className="w-full" />
            <p className="text-sm text-muted-foreground mt-2">
              {Math.round(validationProgress)}% kész
            </p>
          </CardContent>
        </Card>
      )}

      {/* Validation Summary */}
      {validationComplete && (
        <Card>
          <CardHeader>
            <CardTitle>Validáció eredménye</CardTitle>
            <CardDescription>
              A adatok ellenőrzésének összefoglalója
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {summary.validRows}
                </div>
                <div className="text-sm text-muted-foreground">Érvényes sor</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-destructive">
                  {summary.errorRows}
                </div>
                <div className="text-sm text-muted-foreground">Hibás sor</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {summary.warningRows}
                </div>
                <div className="text-sm text-muted-foreground">Figyelmeztetéssel</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">
                  {summary.totalRows}
                </div>
                <div className="text-sm text-muted-foreground">Összes sor</div>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex space-x-2">
                <Button
                  variant={showErrorsOnly ? "default" : "outline"}
                  size="sm"
                  onClick={() => setShowErrorsOnly(!showErrorsOnly)}
                >
                  {showErrorsOnly ? 'Minden sor' : 'Csak hibás sorok'}
                </Button>
                
                {summary.errorRows > 0 && (
                  <Button variant="outline" size="sm" onClick={exportErrors}>
                    <Download className="mr-2 h-4 w-4" />
                    Hibás sorok exportálása
                  </Button>
                )}
              </div>

              <div className="flex items-center space-x-2">
                {summary.errorRows > 0 && (
                  <Badge variant="destructive">
                    {summary.totalErrors} hiba
                  </Badge>
                )}
                {summary.totalWarnings > 0 && (
                  <Badge variant="outline" className="text-orange-600 border-orange-600">
                    {summary.totalWarnings} figyelmeztetés
                  </Badge>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Validation Results */}
      {validationComplete && (
        <>
          {summary.errorRows > 0 && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                <div className="space-y-2">
                  <p>
                    <strong>{summary.errorRows} sor tartalmaz hibákat</strong> és nem lesz importálva.
                  </p>
                  <p>
                    Javítsa ki a hibákat a CSV fájlban, vagy exportálja a hibás sorokat 
                    a részletes hibaüzenetekkel együtt.
                  </p>
                </div>
              </AlertDescription>
            </Alert>
          )}

          {summary.warningRows > 0 && summary.errorRows === 0 && (
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>{summary.warningRows} sor figyelmeztetést tartalmaz</strong>, 
                de az import folytatható. Ellenőrizze az érintett sorokat.
              </AlertDescription>
            </Alert>
          )}

          {summary.errorRows === 0 && summary.warningRows === 0 && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>
                <strong>Minden sor érvényes!</strong> Az import folytatható.
              </AlertDescription>
            </Alert>
          )}

          <Card>
            <CardHeader>
              <CardTitle>
                Validációs részletek
                {showErrorsOnly && ` (${displayRows.length} hibás sor)`}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <div className="max-h-96 overflow-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Sor</TableHead>
                      <TableHead>Állapot</TableHead>
                      <TableHead>Hibák / Figyelmeztetések</TableHead>
                      <TableHead>Érintett mezők</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {displayRows.slice(0, 100).map((row) => ( // Limit display for performance
                      <TableRow key={row.rowIndex}>
                        <TableCell>#{row.rowIndex}</TableCell>
                        
                        <TableCell>
                          <div className="flex items-center space-x-1">
                            {row.validation.isValid ? (
                              <CheckCircle className="h-4 w-4 text-green-600" />
                            ) : (
                              <X className="h-4 w-4 text-destructive" />
                            )}
                            <Badge 
                              variant={row.validation.isValid ? "default" : "destructive"}
                              className="text-xs"
                            >
                              {row.validation.isValid ? 'Érvényes' : 'Hibás'}
                            </Badge>
                          </div>
                        </TableCell>
                        
                        <TableCell>
                          <div className="space-y-1 max-w-64">
                            {row.validation.errors.map((error, i) => (
                              <div key={i} className="text-xs text-destructive">
                                <strong>{error.field}:</strong> {error.message}
                              </div>
                            ))}
                            {row.validation.warnings.map((warning, i) => (
                              <div key={i} className="text-xs text-orange-600">
                                <strong>{warning.field}:</strong> {warning.message}
                              </div>
                            ))}
                          </div>
                        </TableCell>
                        
                        <TableCell>
                          <div className="flex flex-wrap gap-1">
                            {[...row.validation.errors, ...row.validation.warnings]
                              .map(issue => issue.field)
                              .filter((field, i, arr) => arr.indexOf(field) === i)
                              .map(field => (
                                <Badge key={field} variant="outline" className="text-xs">
                                  {field}
                                </Badge>
                              ))}
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
              
              {displayRows.length > 100 && (
                <div className="p-4 text-center text-sm text-muted-foreground border-t">
                  Csak az első 100 sor jelenik meg. Használja a szűrőket vagy exportálja az eredményeket.
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* Navigation */}
      {validationComplete && (
        <div className="flex items-center justify-between">
          <Button variant="outline" onClick={onBack}>
            Vissza
          </Button>
          
          <div className="flex items-center space-x-4">
            {summary.errorRows > 0 && (
              <p className="text-sm text-muted-foreground">
                {summary.validRows} sor lesz importálva, {summary.errorRows} sor kihagyva
              </p>
            )}
            
            <Button 
              onClick={handleContinue}
              disabled={summary.validRows === 0}
            >
              {summary.errorRows > 0 
                ? `${summary.validRows} érvényes sor importálása`
                : 'Minden sor importálása'
              }
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}